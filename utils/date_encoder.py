#!/usr/bin/env python
# coding=UTF-8
import json
import datetime
import calendar
import decimal
import logging
import sys


class ApiResult(dict):

    def error(self, code=6001, msg="", data={}):
        self["code"] = code
        self["msg"] = msg
        self["data"] = data
        return json_encoder(self)

    def success(self, code=0, data={}, msg="success"):
        self["code"] = code
        self["msg"] = msg
        self["data"] = data
        return json_encoder(self)

    @classmethod
    def get_inst(cls):
        return ApiResult(code=0, msg="", data={})

def json_encoder(data):
    data = json.dumps(data, cls=DecimalEncoder, ensure_ascii=False)
    logging.info("data %s" % data)
    return data


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):  # decimal类型转换，使其可以转换为json格式数据
            return float(obj)
        elif isinstance(obj, datetime.datetime):  # datetime类型转换，使其可以转换为json格式数据
            return obj.__str__()
        elif isinstance(obj, datetime.date):  # date类型转换，使其可以转换为json格式数据
            return obj.__str__()
        return super(DecimalEncoder, self).default(obj)



_MONTH = ((0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
          (0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31))


def get_date(d=0, m=0, y=0, start_date=None, format="",S=0,M=0, H=0):
    if not start_date:
        start_date = datetime.datetime.now()
    if d != 0 or H != 0 or S !=0 or M!= 0:
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

if __name__ == '__main__':
    t = datetime.datetime.strptime("2019-07-12", "%Y-%m-%d")
    print(get_date(H=5, M=30, start_date=datetime.datetime.strptime("2019-07-30 00:00:00", "%Y-%m-%d %H:%M:%S")))