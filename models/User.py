# from sanic import request
import logging

logger = logging.getLogger("user_db")

class User():
    def __init__(self, request):
        self.db = request.app.db

    def __del__(self):
        self.db = None

    def query_user_money(self, userid=None):
        db = self.db
        sql = "select * from  t_money_detail where userid='%s' limit 10" % userid
        return db.query(sql)

    def insert_user(self):
        sql = "insert into users (username, password) values ('lpc', '123456')"
        return self.db.insert_one(sql)

    def query_user_s(self, page_num, page_size):
        sql = "select * from t_money_detail where ctime>='2019-01-03 00:00:00' and action=1"
        if page_num:
            sql += " LIMIT %s,%s"
        return self.db.query(sql, ((page_num - 1) * page_size, page_size))