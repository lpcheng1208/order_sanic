#!/usr/bin/env python3
# coding=utf-8

"""
@author: guoyanfeng
@software: PyCharm
@time: 18-12-25 下午4:58
"""
import asyncio
import atexit

import aelog
from aiomysql.sa import create_engine
from aiomysql.sa.exc import Error
from pymysql.err import IntegrityError, MySQLError


from .err_msg import mysql_msg
from .exceptions import FuncArgsError, HttpError, MysqlDuplicateKeyError, MysqlError, QueryArgsError
from .utils import verify_message

__all__ = ("AIOMysqlClient",)


class AIOMysqlClient(object):
    """
    MySQL异步操作指南
    """

    def __init__(self, app=None, *, username="root", passwd=None, host="127.0.0.1", port=3306, dbname=None,
                 pool_size=50, **kwargs):
        """
        mongo 非阻塞工具类
        Args:
            app: app应用
            host:mysql host
            port:mysql port
            dbname: database name
            username: mysql user
            passwd: mysql password
            pool_size: mysql pool size
        """

        self.aio_engine = None
        self.username = username
        self.passwd = passwd
        self.host = host
        self.port = port
        self.dbname = dbname
        self.pool_size = pool_size
        self.message = kwargs.get("message", {})
        self.use_zh = kwargs.get("use_zh", True)
        self.msg_zh = None

        if app is not None:
            self.init_app(app, username=self.username, passwd=self.passwd, host=self.host, port=self.port,
                          dbname=self.dbname, pool_size=self.pool_size, **kwargs)

    def init_app(self, app, *, username=None, passwd=None, host=None, port=None, dbname=None,
                 pool_size=None, **kwargs):
        """
        mysql 实例初始化
        Args:
            app: app应用
            host:mysql host
            port:mysql port
            dbname: database name
            username: mysql user
            passwd: mysql password
            pool_size: mysql pool size
        Returns:
        """
        username = username or app.config.get("ACLIENTS_MYSQL_USERNAME", None) or self.username
        passwd = passwd or app.config.get("ACLIENTS_MYSQL_PASSWD", None) or self.passwd
        host = host or app.config.get("ACLIENTS_MYSQL_HOST", None) or self.host
        port = port or app.config.get("ACLIENTS_MYSQL_PORT", None) or self.port
        dbname = dbname or app.config.get("ACLIENTS_MYSQL_DBNAME", None) or self.dbname
        pool_size = pool_size or app.config.get("ACLIENTS_MYSQL_POOL_SIZE", None) or self.pool_size
        message = kwargs.get("message") or app.config.get("ACLIENTS_MYSQL_MESSAGE", None) or self.message
        use_zh = kwargs.get("use_zh") or app.config.get("ACLIENTS_MYSQL_MSGZH", None) or self.use_zh

        passwd = passwd if passwd is None else str(passwd)
        self.message = verify_message(mysql_msg, message)
        self.msg_zh = "msg_zh" if use_zh else "msg_en"

        @app.listener('before_server_start')
        async def open_connection(app_, loop):
            """
            Args:
            Returns:
            """
            # engine
            # 增加autocommit = True可以解决个别情况下，提交了数据但是查询还是老的数据的问题
            self.aio_engine = await create_engine(user=username, db=dbname, host=host, port=port,
                                                  password=passwd, maxsize=pool_size, charset="utf8")

        @app.listener('after_server_stop')
        async def close_connection(app_, loop):
            """
            Args:
            Returns:
            """
            if self.aio_engine:
                self.aio_engine.close()
                await self.aio_engine.wait_closed()

    def init_engine(self, *, username="root", passwd=None, host="127.0.0.1", port=3306, dbname=None,
                    pool_size=50, **kwargs):
        """
        mysql 实例初始化
        Args:
            host:mysql host
            port:mysql port
            dbname: database name
            username: mysql user
            passwd: mysql password
            pool_size: mysql pool size
        Returns:
        """
        username = username or self.username
        passwd = passwd or self.passwd
        host = host or self.host
        port = port or self.port
        dbname = dbname or self.dbname
        pool_size = pool_size or self.pool_size
        message = kwargs.get("message") or self.message
        use_zh = kwargs.get("use_zh") or self.use_zh

        passwd = passwd if passwd is None else str(passwd)
        self.message = verify_message(mysql_msg, message)
        self.msg_zh = "msg_zh" if use_zh else "msg_en"
        loop = asyncio.get_event_loop()

        async def open_connection():
            """
            Args:
            Returns:
            """
            # engine
            # 增加autocommit = True可以解决个别情况下，提交了数据但是查询还是老的数据的问题
            self.aio_engine = await create_engine(user=username, db=dbname, host=host, port=port,
                                                  password=passwd, maxsize=pool_size, charset="utf8")

        async def close_connection():
            """
            Args:
            Returns:
            """
            if self.aio_engine:
                self.aio_engine.close()
                await self.aio_engine.wait_closed()

        loop.run_until_complete(open_connection())
        atexit.register(lambda: loop.run_until_complete(close_connection()))

    async def _insert_one(self, sql, param=None):
        """
        插入数据
        Args:
            model: model
            insert_data: 值类型
        Returns:
            返回插入的条数
        """
        # try:
        #     query = insert(model).values(insert_data)
        #     new_values = self._get_model_default_value(model)
        #     new_values.update(insert_data)
        # except SQLAlchemyError as e:
        #     aelog.exception(e)
        #     raise QueryArgsError(message="Cloumn args error: {}".format(str(e)))
        # else:
        async with self.aio_engine.acquire() as conn:
            async with conn.begin() as trans:
                try:
                    cursor = await self.execute(sql, param)
                except IntegrityError as e:
                    await trans.rollback()
                    aelog.exception(e)
                    if "Duplicate" in str(e):
                        raise MysqlDuplicateKeyError(e)
                    else:
                        raise MysqlError(e)
                except (MySQLError, Error) as e:
                    await trans.rollback()
                    aelog.exception(e)
                    raise MysqlError(e)
                except Exception as e:
                    await trans.rollback()
                    aelog.exception(e)
                    raise HttpError(500, message=self.message[1][self.msg_zh], error=e)
                else:
                    # 理论也是不应该加的，但是出现过一个连接提交后另一个连接拿不到数据的情况，而开启autocommit后就可以了，因此这里
                    # 加一条
                    await conn.execute('commit')
        return cursor.rowcount, cursor.lastrowid

    async def _update_data(self, sql, param=None):
        """
        更新数据
        Args:
            model: model
            query_key: 更新的查询条件
            update_data: 值类型
            or_query_key: 或查询model的过滤条件
        Returns:
            返回更新的条数
        """
        async with self.aio_engine.acquire() as conn:
            async with conn.begin() as trans:
                try:
                    cursor = await self.execute(sql, param)
                except IntegrityError as e:
                    await trans.rollback()
                    aelog.exception(e)
                    if "Duplicate" in str(e):
                        raise MysqlDuplicateKeyError(e)
                    else:
                        raise MysqlError(e)
                except (MySQLError, Error) as e:
                    await trans.rollback()
                    aelog.exception(e)
                    raise MysqlError(e)
                except Exception as e:
                    await trans.rollback()
                    aelog.exception(e)
                    raise HttpError(500, message=self.message[2][self.msg_zh], error=e)
                else:
                    await conn.execute('commit')
        return cursor.rowcount

    async def _delete_data(self, sql, param=None):
        """
        更新数据
        Args:
            model: model
            query_key: 删除的查询条件
            or_query_key: 或查询model的过滤条件
        Returns:
            返回删除的条数
        """
        async with self.aio_engine.acquire() as conn:
            async with conn.begin() as trans:
                try:
                    cursor = await self.execute(sql, param)
                except (MySQLError, Error) as e:
                    await trans.rollback()
                    aelog.exception(e)
                    raise MysqlError(e)
                except Exception as e:
                    await trans.rollback()
                    aelog.exception(e)
                    raise HttpError(500, message=self.message[3][self.msg_zh], error=e)
                else:
                    await conn.execute('commit')
        return cursor.rowcount

    async def _find_one(self, sql, param=None):
        """
        查询单条数据
        Args:
            model: 查询的model名称
            query_key: 查询model的过滤条件
            or_query_key: 或查询model的过滤条件
        Returns:
            返回匹配的数据或者None
        """
        # cursor = await self.execute(sql, param)
        # resp = await cursor.fetchone()
        # return dict(resp) if resp else None

        try:
            async with self.aio_engine.acquire() as conn:
                cursor = await self.execute(sql, param)
                resp = await cursor.fetchone()
                await conn.execute('commit')  # 理论上不应该加这个的，但是这里默认就会启动一个事务，很奇怪
        except (MySQLError, Error) as err:
            aelog.exception("Find one data failed, {}".format(err))
            raise HttpError(400, message=self.message[4][self.msg_zh], error=err)
        else:
            return dict(resp) if resp else None


    async def execute(self, sql, param=None):
        """
        插入数据，更新或者删除数据
        Args:
            query: SQL的查询字符串或者sqlalchemy表达式
        Returns:
            不确定执行的是什么查询，直接返回ResultProxy实例
        """
        async with self.aio_engine.acquire() as conn:
            async with conn.begin() as trans:
                try:
                    aelog.info("sql: %s" % sql)
                    if not param:
                        cursor = await conn.execute(sql)
                    else:
                        cursor = await conn.execute(sql, param)
                except IntegrityError as e:
                    await trans.rollback()
                    aelog.exception(e)
                    if "Duplicate" in str(e):
                        raise MysqlDuplicateKeyError(e)
                    else:
                        raise MysqlError(e)
                except (MySQLError, Error) as e:
                    await trans.rollback()
                    aelog.exception(e)
                    raise MysqlError(e)
                except Exception as e:
                    await trans.rollback()
                    aelog.exception(e)
                    raise HttpError(500, message=self.message[6][self.msg_zh], error=e)
                else:
                    await conn.execute('commit')
        return cursor

    async def query(self, sql, param=None):
        """
        查询数据，用于复杂的查询
        Args:
            query: SQL的查询字符串或者sqlalchemy表达式
        Returns:
            不确定执行的是什么查询，直接返回ResultProxy实例
        """
        try:
            cursor = await self.execute(sql, param)
            resp = await cursor.fetchall()
        except (MySQLError, Error) as err:
            aelog.exception("Find data failed, {}".format(err))
            raise HttpError(400, message=self.message[5][self.msg_zh], error=err)
        else:
            return [dict(val) for val in resp] if resp else None

    async def insert_one(self, sql, param=None):
        """
        插入数据
        Args:
            model: model
            insert_data: 值类型
        Returns:
            返回插入的条数
        """
        return await self._insert_one(sql, param)

    async def find_one(self, sql, param=None):
        """
        查询单条数据
        Args:
            model: 查询的model名称
            query_key: 查询model的过滤条件
            or_query_key: 或查询model的过滤条件
        Returns:
            返回匹配的数据或者None
        """
        return await self._find_one(sql, param)


    async def update_data(self, sql, param=None):
        """
        更新数据
        Args:
            model: model
            query_key: 更新的查询条件
            or_query_key: 或查询model的过滤条件
            update_data: 值类型
        Returns:
            返回更新的条数
        """
        return await self._update_data(sql, param)

    async def delete_data(self, sql, param=None):
        """
        更新数据
        Args:
            model: model
            query_key: 删除的查询条件, 必须有query_key，不允许删除整张表
            or_query_key: 或查询model的过滤条件
        Returns:
            返回删除的条数
        """
        if not sql:
            raise FuncArgsError("query_key must be provide!")
        return await self._delete_data(sql, param)


db_sql = AIOMysqlClient()