#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import requests
import urllib3
from urllib.parse import quote

from config.conf import infra_wxauth_config

urllib3.disable_warnings()


def gettoken(Corpid, Secret):
    Url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
    Data = {
        "corpid": Corpid,
        "corpsecret": Secret
    }
    r = requests.get(url=Url, params=Data, verify=False)
    Token = r.json()['access_token']
    return Token


def getuserinfo(Token, Code):
    Url = "https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo"
    Data = {
        "access_token": Token,
        "code": Code,
    }
    r = requests.get(url=Url, params=Data, verify=False)
    rs = r.json()
    return rs


def getuserdetail(Token, UserID):
    url = 'https://qyapi.weixin.qq.com/cgi-bin/user/get?'
    para = {
        'access_token': Token,
        'userid': UserID
    }
    r = requests.get(url=url, params=para, verify=False)
    info = r.json()
    return info


def getappinfo(Token, Agentid):
    Url = "https://qyapi.weixin.qq.com/cgi-bin/agent/get"
    Data = {
        "access_token": Token,
        "agentid": Agentid,
    }
    r = requests.get(url=Url, params=Data, verify=False)
    rs = r.json()
    return rs


def authorize_url(Corpid, url, state):
    redirect_uri = quote(url, safe='')
    OAUTH_CODE_URL = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=code&scope=snsapi_base&state=%s#wechat_redirect" % (
        Corpid, redirect_uri, state)
    return OAUTH_CODE_URL


def get_authenticated_user(userid):
    Corpid = infra_wxauth_config["Corpid"]
    Secret = infra_wxauth_config["Secret"]
    Agentid = infra_wxauth_config["Agentid"]
    token = gettoken(Corpid, Secret)
    users_in_app = getappinfo(token, Agentid)
    users = [item[key] for item in users_in_app['allow_userinfos']['user'] for key in item]
    if userid in users:
        username = getuserdetail(token, userid)['name']
        return username
    else:
        return False
