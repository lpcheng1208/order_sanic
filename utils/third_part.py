#!/usr/bin/env python
# coding=UTF-8
import sys
import logging
import requests

def check_wx_token(access_token, openid):
    try:
        url = "http://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=zh_CN" % (access_token, openid)
        h = requests.get(url)
        res = h.text
        logging.info(res)
        return 'ok' in res
    except:
        logging.error("wx apis error", exc_info=True)
        return None
    
def check_qq_token(access_token, openid):
    try:
        
        url = "https://graph.qq.com/oauth2.0/me?access_token=%s" % access_token
        h = requests.get(url, verify=False)
        res = h.text
        logging.info(res)
        return openid in res
    except:
        logging.error("qq apis error", exc_info=True)
        return None
    