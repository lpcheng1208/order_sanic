#!/usr/bin/env python
# coding=UTF-8
import os
import pickle
import re
import bcrypt
import requests
import logging
import logging.handlers
import jwt
import datetime

from bson import ObjectId

import config
import json
import random
import time
import urllib
import calendar



def is_mobile(phone):
    if re.match("^1[3456789][0-9]{9}$", phone):
        return True
    return False

def create_encrypt_pwd(passwd):
    '''生成加密的密码'''
    return bcrypt.hashpw(passwd, bcrypt.gensalt())

def check_pwd(oldpwd, newpwd):
    '''校验密码'''
    return bcrypt.checkpw(str(oldpwd), str(newpwd))

def create_vcode():
    if config.test_mode:
        return '111111'
    return str(random.randint(100000,999999))

def id_card_check(name, id_card):
    url = "https://idcert.market.alicloudapi.com/idcard"
    appCode = "3d0dac0f4a6644b98fae55ac3b620858"
    headers = {"Authorization":"APPCODE %s" % appCode}
    try:
        r = requests.get(url, {"idCard":id_card, "name":name}, headers=headers, verify=False)
        return r.json()
    except:
        logging.error("id cert error:", exc_info=True)
        return {}
    
def create_jwt_token(data):
    secret = "my-secret-token-to-change-in-production"
    claim = "auth"
    encoded = jwt.encode(data, claim, algorithm='HS512', headers={"verify_signature":secret})
    return encoded

def java_login(username, pwd, code=''):
    try:
        return {}
        logging.info("%s,%s,%s" % (username, pwd, code))
        if not config.java_server:
            return {}
        if pwd:
            data = {"code":"","openId":"","password":pwd,"phoneType":2,"thirdPartId":0,"thirdPartType":"","username":username}
            r = requests.post("%s/store/apis/authenticate" % config.java_server, json=data)
        else:
            data = {"code":code,"openId":"","password":"123456","phoneType":2,"thirdPartId":'0',"thirdPartType":"","username":username}
            r = requests.post("%s/store/apis/authCodeLogin" % config.java_server, json=data)
        res = r.text
        logging.info(res)
        res = json.loads(res)
        return res
    except:
        logging.info("java login error:", exc_info=True)
        return {}

def search_wuliu(express_company, express_no):
    url = config.WULIUURL
    headers = {'Authorization': 'APPCODE ' + config.APPCODEYUFU}
    url += "?%s" % urllib.urlencode({"com":express_company, "nu":express_no})
    r = requests.get(url, headers=headers) 
    res = r.text
    logging.info(res)
    res = json.loads(res)
    if not res:
        return {}
    return res['showapi_res_body']

def create_order_no():
    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    randstr = str(random.randint(1000, 9999))
    return now + randstr

def create_order_id():
    nowtime = time.strftime("%Y%m%d%H%M%S")
    randstr = str(random.randint(1000, 9999))
    return config.appKey+nowtime+randstr


_MONTH = ((0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
          (0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31))


def get_date(d=0, m=0, y=0, start_date=None, format="",S=0,M=0, H=0):
    if not start_date:
        start_date = datetime.datetime.now()
    if d != 0 or H != 0 or S != 0 or M != 0:
        start_date += datetime.timedelta(days=d, hours=H, minutes=M, seconds=S)
    if not (y or m):
        if format == "date":
            return start_date.strftime("%Y-%m-%d")
        elif format == "date_time":
            return start_date.strftime("%m月%d日")
        return start_date.strftime("%Y-%m-%d %H:%M:%S")

    n = int(start_date.year) * 12 + int(start_date.month) - 1
    n = n + m
    ryear = n / 12
    rmonth = n % 12 + 1
    rday = start_date.day
    if calendar.isleap(ryear):
        if rday > _MONTH[1][rmonth]:
            rday = _MONTH[1][rmonth]
    else:
        if rday > _MONTH[0][rmonth]:
            rday = _MONTH[0][rmonth]

    y += int((m + int(start_date.month) - 1) / 12)
    result = start_date.replace(year=start_date.year + y, month=rmonth, day=rday)
    if format == "date":
        return result.strftime("%Y-%m-%d")
    elif format == "date_time":
        return start_date.strftime("%m月%d日")
    return result.strftime("%Y-%m-%d %H:%M:%S")

def CalculateAge(Date):
    '''Calculates the age and days until next birthday from the given birth date'''
    try:
        Date = Date.split('-')
        BirthDate = datetime.date(int(Date[0]), int(Date[1]), int(Date[2]))
        Today = datetime.date.today()
        if (Today.month > BirthDate.month):
            NextYear = datetime.date(Today.year + 1, BirthDate.month, BirthDate.day)
        elif (Today.month < BirthDate.month):
            NextYear = datetime.date(Today.year, Today.month + (BirthDate.month - Today.month), BirthDate.day)
        elif (Today.month == BirthDate.month):
            if (Today.day > BirthDate.day):
                NextYear = datetime.date(Today.year + 1, BirthDate.month, BirthDate.day)
            elif (Today.day < BirthDate.day):
                NextYear = datetime.date(Today.year, BirthDate.month, Today.day + (BirthDate.day - Today.day))
            elif (Today.day == BirthDate.day):
                NextYear = 0
        Age = Today.year - BirthDate.year
        if NextYear == 0:  # if today is the birthday
            return '%d' % (Age)
        else:
            DaysLeft = NextYear - Today
            return '%d' % (Age)
    except:
        return 'Wrong date format'

def get_user_info(uid):
    value = redis_info.get(uid)
    if value is None:
        actor = Actor.objects(id=uid).first()
        if actor is None:
            info = None
        else:
            info_json = actor.to_json()
            info = json.loads(info_json)
            redis_info.set(uid, info_json, ex=60 * 60 * 24 * 2)
    else:
        try:
            info = json.loads(value.decode('utf-8'))
        except Exception as e:
            logging.exception(e)
            info = pickle.loads(value)
    return info

def get_user_info_by_rid(rid):
    key = 'info_{}'.format(str(rid))
    value = redis_info.get(key)
    if value is None:
        actor = Actor.objects(rid=rid).first()
        if actor is None:
            info = None
        else:
            info = json.loads(actor.to_json())
            redis_info.set(key, pickle.dumps(info), ex=60 * 60 * 24 * 2)
    else:
        info = pickle.loads(value)
    return info



def str_to_timestamp(time_str):
    timeArray = time.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    timestamp = int(time.mktime(timeArray))
    return timestamp


def timestamp_to_str(timestamp):
    timeArray = time.localtime(timestamp)
    time_str = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return time_str


def get_my_rank(db, start_time, end_time, start_date, search_type):
    rds_key = "income_100_rank_%s_%s" % (search_type, start_date)
    data_rank = {}
    if redis_room.exists(rds_key):
        data_rank = json.loads(redis_room.get(rds_key))
    else:
        all_actor = Actor.objects(gender=2, valid=1).all()
        actor_uids = []
        for actor in all_actor:
            actor_uids.append(str(actor.id))
        rows = db.query_income_rank(start_time, end_time, actor_uids)
        rank = 1
        for row in rows:
            uid = row.get("userid", "")
            coins = row.get("coins", 0)
            data_rank[uid] = "%s-%s" % (str(coins), str(rank))
            rank += 1
        redis_room.set(rds_key, json.dumps(data_rank))
        if start_date >= get_date(format="date"):
            redis_room.expire(rds_key, 60 * 60)

    return data_rank

def timestamp_from_objectid(objectid):
    result = 0
    try:
        result = time.mktime(objectid.generation_time.timetuple())
    except:
        pass
    return result

def time2ObjectId(timestamp):
    return "{0:x}".format(timestamp) + '0000000000000000'

def get_mysql_datetime(start_time, end_time):
    start_time = get_date(H=5, M=30, start_date=datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S"))
    end_time = get_date(H=5, M=30, start_date=datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S"))
    return start_time, end_time

def cache_user_info(actor):
    redis_info.set(str(actor.id), actor.to_json(), ex=60 * 60 * 24 * 2)

    return True

if __name__ == "__main__":
    #print java_login("13430789767", "", "111111")
    # newpwd = create_encrypt_pwd('111111')
    # old_pwd= '$2b$12$xUmIPSFMcmT/MXADwtysHebvv9du2yflN5HpARC.0anLgCEgfqCrm'
    #print check_pwd(newpwd, old_pwd)
    # print search_wuliu('shunfeng', '765903026318')
    print(timestamp_from_objectid(ObjectId("5d3e9181e3633400ac8a1371")))
