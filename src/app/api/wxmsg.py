#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from common.WXBizMsgCrypt import WXBizMsgCrypt
from config.conf import infra_wxauth_config
from typing import Type, TypeVar, Generic
from xml.etree.ElementTree import fromstring
from pydantic import BaseModel
from starlette.requests import Request

# 以下为接受XML格式数据部分
T = TypeVar("T", bound=BaseModel)


def wxmsgcpt():
    sCorpID = infra_wxauth_config["Corpid"]
    sEncodingAESKey = infra_wxauth_config["EncodingAESKey"]
    sToken = infra_wxauth_config["Token"]
    wxcpt = WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID)
    return wxcpt


class XmlBody(Generic[T]):
    def __init__(self, model_class: Type[T]):
        self.model_class = model_class

    async def __call__(self, request: Request) -> T:
        # the following check is unnecessary if always using xml,
        # but enables the use of json too
        if '/xml' in request.headers.get("Content-Type", ""):
            body = await request.body()
            doc = fromstring(body)
            dict_data = {}
            for node in doc.getchildren():
                dict_data[node.tag] = node.text
        else:
            dict_data = await request.json()
        return self.model_class.parse_obj(dict_data)
