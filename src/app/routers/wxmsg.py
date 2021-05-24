#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys
import time
import xml.etree.cElementTree as ET
from fastapi import APIRouter, Depends

from api import admanager, exmail
from api.wxmsg import wxmsgcpt, XmlBody
from common.logs import Log
from config import TextMenu
from config.TextMenu import DesktopMenu
from model.wxmodels import Item

router = APIRouter()
wxcpt = wxmsgcpt()


# 回调验证部分
@router.get("/wxmsgcpt")
async def Verify(msg_signature: str,
                 timestamp: str,
                 nonce: str,
                 echostr: str
                 ):
    sVerifyMsgSig = msg_signature
    sVerifyTimeStamp = timestamp
    sVerifyNonce = nonce
    sVerifyEchoStr = echostr
    ret, sReplyEchoStr = wxcpt.VerifyURL(sVerifyMsgSig, sVerifyTimeStamp, sVerifyNonce, sVerifyEchoStr)
    if (ret != 0):
        print("ERR: DecryptMsg ret: " + str(ret))
        sys.exit(1)
    return int(sReplyEchoStr)


# 接受消息模版
Recived_Temp = """
<xml> 
   <ToUserName><![CDATA[%(ToUserName)s]]></ToUserName>
   <AgentID><![CDATA[%(AgentID)s]]></AgentID>
   <Encrypt><![CDATA[%(Encrypt)s]]></Encrypt>
</xml>
"""

# 发送消息模版
Send_Temp = """
<xml>
   <ToUserName>%(ToUserName)s</ToUserName>
   <FromUserName>%(FromUserName)s</FromUserName> 
   <CreateTime>%(timestamp)s</CreateTime>
   <MsgType>text</MsgType>
   <Content>%(content)s</Content>
</xml>
"""


# 消息接收部分
@router.post("/wxmsgcpt")
async def sendMsg(msg_signature: str,
                  timestamp: str,
                  nonce: str,
                  item: Item = Depends(XmlBody(Item))
                  ):
    Recived_dict = {
        'ToUserName': item.ToUserName,
        'AgentID': item.AgentID,
        'Encrypt': item.Encrypt,
    }

    ReqData = Recived_Temp % Recived_dict
    ret, sMsg = wxcpt.DecryptMsg(sPostData=ReqData, sMsgSignature=msg_signature, sTimeStamp=timestamp, sNonce=nonce)
    if (ret != 0):
        print("ERR: DecryptMsg ret: " + str(ret))
        sys.exit(1)

    xml_tree = ET.fromstring(sMsg)
    FromUserName = xml_tree.find("FromUserName").text
    ToUserName = xml_tree.find("ToUserName").text
    msgType = xml_tree.find("MsgType").text

    def SendTextMsg(ToUserName, FromUserName, content):
        timestamp = str(time.time())
        Send_dict = {
            "ToUserName": ToUserName,
            "FromUserName": FromUserName,
            "timestamp": timestamp,
            "content": content,
        }
        # 消息发送部分
        sRespData = Send_Temp % Send_dict
        ret, sEncryptMsg = wxcpt.EncryptMsg(sReplyMsg=sRespData, sNonce=nonce, timestamp=timestamp)
        if (ret != 0):
            print("ERR: EncryptMsg ret: " + str(ret))
            sys.exit(1)
        return sEncryptMsg

    if msgType == 'text':
        logger = Log()
        content_recived = xml_tree.find("Content").text
        if content_recived.lower() == 'help':
            contentlog = "WeComAPI Desktop Service : [%s to %s][%s]" % (FromUserName, ToUserName, content_recived)
            logger.info('help', contentlog)
            sEncryptMsg = SendTextMsg(ToUserName, FromUserName, DesktopMenu())
            return sEncryptMsg

        # 查询AD用户
        elif content_recived.lower()[0:1] == 'q' and content_recived.lower()[1] == ' ' and len(
                content_recived.split()) == 2:
            name = content_recived.lower()[1:].strip().upper()
            info = admanager.get_user_info(name)
            rs = TextMenu.search_ad_user(info)
            contentlog = "WeComAPI Desktop Service : [%s to %s][%s]" % (FromUserName, ToUserName, rs)
            logger.info('search_ad_user', contentlog)  # 记录日志文件
            sEncryptMsg = SendTextMsg(ToUserName, FromUserName, rs)
            return sEncryptMsg

        # 重置AD用户密码
        elif content_recived.lower()[0:8] == 'password' and content_recived.lower()[8] == ' ' and len(
                content_recived.split()) == 2:
            name = content_recived.lower()[8:].strip().upper()
            rs = admanager.reset_password(name)
            if rs == 0:
                rs = TextMenu.reset_password(name)
            else:
                rs = TextMenu.reset_password_error(name)
            contentlog = "WeComAPI Desktop Service : [%s to %s][%s]" % (FromUserName, ToUserName, rs)
            logger.info('reset_ad_password', contentlog)  # 记录日志文件
            sEncryptMsg = SendTextMsg(ToUserName, FromUserName, rs)
            return sEncryptMsg

        # 重置企业邮箱密码
        elif content_recived.lower()[0:4] == 'mail' and content_recived.lower()[4] == ' ' and len(
                content_recived.split()) == 2:
            name = content_recived.lower()[4:].strip().lower()
            rs = exmail.update_exmail_password(name)
            if rs == 0:
                rs = TextMenu.reset_email(name)
            elif rs == 60111:
                rs = TextMenu.reset_email_noid(name)
            else:
                rs = TextMenu.reset_email_error(name)
            contentlog = "WeComAPI Desktop Service : [%s to %s][%s]" % (FromUserName, ToUserName, rs)
            logger.info('reset_email', contentlog)  # 记录日志文件
            sEncryptMsg = SendTextMsg(ToUserName, FromUserName, rs)
            return sEncryptMsg

        else:
            rs = content_recived
            contentlog = "WeComAPI Desktop Service : [%s to %s][%s]" % (FromUserName, ToUserName, rs)
            logger.info('help', contentlog)  # 记录日志文件
            resp_content = '输入help查看帮助'
            sEncryptMsg = SendTextMsg(ToUserName, FromUserName, resp_content)
            return sEncryptMsg

    elif msgType == 'event':
        event = xml_tree.find("Event").text
        eventKey = xml_tree.find("EventKey").text
        if event == 'click' and eventKey == 'help':
            sEncryptMsg = SendTextMsg(ToUserName, FromUserName, DesktopMenu())
            return sEncryptMsg
