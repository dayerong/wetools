#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import requests
import json
import urllib3
from config.conf import exmail_config
from common.logs import Log

urllib3.disable_warnings()


def GetToken(Corpid, Secret):
    Url = "https://api.exmail.qq.com/cgi-bin/gettoken"
    Data = {
        "corpid": Corpid,
        "corpsecret": Secret
    }
    r = requests.get(url=Url, params=Data, verify=False)
    Token = r.json()['access_token']
    return Token


def getuserinfo(Token, User):
    Url = "https://api.exmail.qq.com/cgi-bin/user/get"
    Data = {
        "access_token": Token,
        "userid": User,
    }
    r = requests.get(url=Url, params=Data, verify=False)
    rs = r.json()["errcode"]
    return rs


def update_user_password(Token, User, Password):
    Url = "https://api.exmail.qq.com/cgi-bin/user/update?access_token=%s" % Token
    Data = {
        "userid": User,
        "password": Password
    }
    data = json.dumps(Data, ensure_ascii=False)
    r = requests.post(url=Url, data=data.encode('utf-8'))
    return r.json()


def disable_user(Token, User):
    Url = "https://api.exmail.qq.com/cgi-bin/user/update?access_token=%s" % Token
    Data = {
        "userid": User,
        "enable": 0
    }
    data = json.dumps(Data, ensure_ascii=False)
    r = requests.post(url=Url, data=data.encode('utf-8'))
    return r.json()


def update_exmail_password(UserMail):
    Corpid = exmail_config["Corpid"]
    Secret = exmail_config["Secret"]
    Password = exmail_config["Defaultpassword"]
    Token = GetToken(Corpid, Secret)
    rs = getuserinfo(Token, UserMail)
    if rs == 0:
        update_user_password(Token, UserMail, Password)
        logger = Log()
        logger.info('update_exmail_password', '用户【 {0} 】成功密码修改为:  {1}'.format(UserMail, Password))
        return 0
    else:
        return rs


def disable_exmail_user(UserMail):
    Corpid = exmail_config["Corpid"]
    Secret = exmail_config["Secret"]
    Token = GetToken(Corpid, Secret)
    rs = getuserinfo(Token, UserMail)
    if rs == 0:
        disable_user(Token, UserMail)
        logger = Log()
        logger.info('disable_exmail_user', '用户【 {0} 】已禁用'.format(UserMail))
        return 0
    else:
        return rs
