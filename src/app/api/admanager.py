#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from config.conf import infratools_config
import requests


def get_user_info(name):
    url = infratools_config["search_users_api_url"]

    param = {
        'name': name
    }
    response = requests.get(url, params=param)
    rs = response.json()
    if rs:
        return rs["result"][0]
    else:
        return name


def reset_password(name):
    url = infratools_config["reset_password_api_url"]
    password = infratools_config["default_password"]

    param = {
        'account': name,
        'password': password
    }
    response = requests.put(url, params=param)
    rs = response.json()
    return rs["result"]
