import json
import logging
import traceback

import sanicdb, aiomysql
from pymysql import IntegrityError
from sanic import request
from aioredis.commands import Redis
from sanic import Blueprint
from sanic.response import json as json_response

from apis.order.filter import *
from extends.aio_redis import rds
from models.User import User
from models.model_mongo import UserMon, Gift_list
from bson import ObjectId

from utils.date_encoder import get_date

view = Blueprint('view', url_prefix='')
logger = logging.getLogger("user")


def logined(func):
    async def wraper(request: request.Request, *args, **kwargs):
        res = {'state_code': -1, 'error_msg': 'login first'}
        api_key = request.headers.get('apis-key','unknown')
        print(api_key,type(api_key))
        sql = 'SELECT eatery_id from eatery WHERE api_key = %s'
        async with request.app.db.acquire() as conn:  # type: aiomysql.connection.Connection
            async with conn.cursor() as cur:  # type: aiomysql.cursors.Cursor
                await cur.execute(sql,api_key)
                ret = await cur.fetchall()
                if ret:
                    rel = await func(request, *args, **kwargs)
                else:
                    return response.json(res)
        return rel
    return wraper

@view.route('/get', methods=['GET'], name='order_get', strict_slashes=False)
# @logined
# @params(order_get_filter)
async def handler(request: request.Request):
    page_num = request.args.get("page_num")
    logger.info("data %s" % page_num)
    a = {
    "_id" : 41,
    "gift_name" : "heart_of_the_sea",
    "gift_icon" : "http://download.dual-whatsapp.com/gift/heart_of_the_sea.png",
    "url" : "http://download.dual-whatsapp.com/gifts/heart_of_the_sea.gift",
    "md5" : "b7dfa05562c89047006c1713b2dd4e4a",
    "price" : 677,
    "valid" : True,
    "gift_order" : 11,
    "gift_type" : "gift",
    "name" : "OceanHeart",
    "length" : 1250
    }
    # m = await Gift_list.insert_one(a)
    # if m:
    #     logger.info(22222222)
    # i = await UserMon.insert_one({"username": "lllllll", "passwd": "1221244"})
    # if i:
    #     logger.info(1111111111)

    a_list = []
    # for row in llll.objects:
    #     miii = row.get("_id")
    #     miiii = row.get("username")
    #     passwd = row.get("passwd")
    #     a_list.append({"a": str(miii), "b": miiii, "c": passwd})
    #     logger.info("miii %s miiii %s" % (miii, miiii))
    m = User(request=request)
    now_time = get_date()

    rows = await m.query_user_money(userid='5c36a7a8ddf27b0043d62f90')
    # logger.info("aaaaa  %s" % rows)
    rds_db = request.app.rds
    rds_db_1 = request.app.rds_1
    b = await rds_db.get_hash_data("aaaa")
    await rds_db_1.save_update_usual_data("abbb", 1, 600)
    c = await rds_db.redis_db.ttl("bbb")
    d = await rds_db.get_keys("*")
    # d = await rds_db.save_session(m)
    res = {'code': 0, 'msg': 'success', "data": {"1": b, "now_time": now_time,"money_detail": rows, "c": c, "d": d}}
    # logger.info(res)
    return json_response(res)

