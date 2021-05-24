#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import requests
import json
import urllib3
from config.conf import itsvc_config

urllib3.disable_warnings()


def GetToken(Corpid, Secret):
    Url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
    Data = {
        "corpid": Corpid,
        "corpsecret": Secret
    }
    r = requests.get(url=Url, params=Data, verify=False)
    Token = r.json()['access_token']
    return Token


def SendMessage(Token, Userid, Agentid, Subject, Content):
    Url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s" % Token
    Data = {
        "touser": Userid,
        "msgtype": "markdown",
        "agentid": Agentid,
        "markdown": {
            "content": Subject + '\n' + Content
        },
        "safe": "0"
    }
    data = json.dumps(Data, ensure_ascii=False)
    r = requests.post(url=Url, data=data.encode('utf-8'))
    return r.json()


def SendToUser(info=None):
    Corpid = itsvc_config['CorpID']
    Secret = itsvc_config['Corpsecret']
    Agentid = itsvc_config['Agentid']
    Token = GetToken(Corpid, Secret)
    Status = SendMessage(Token, info['userid'], Agentid, info['subject'], info['content'])
    return Status


def sendPushMsg(userid, push_info=None):
    project, branch, commit_id, commit_title, commit_timestamp, author_name, author_email = push_info['project'], \
                                                                                            push_info['branch'], \
                                                                                            push_info['commit_id'], \
                                                                                            push_info[
                                                                                                'commit_title'], \
                                                                                            push_info[
                                                                                                'commit_timestamp'], \
                                                                                            push_info[
                                                                                                'author_name'], \
                                                                                            push_info[
                                                                                                'author_email']

    push_msg = {
        "userid": userid,
        "subject": "项目**{0}**收到一次Push提交\n".format(project),
        "content": ">**提交详情**\n  \
                   分   支：<font color=\"info\">{branch}</font>\n \
                   提交者：<font color=\"info\">{author_name}</font>\n \
                   邮   箱：<font color=\"info\">{author_email}</font>\n> \
                   时   间：<font color=\"info\">{commit_timestamp}</font>\n \
                   提交描述：<font color=\"info\">{commit_title}</font>\n  \
                   提交ID：<font color=\"info\">{commit_id}</font>\n".format(
            branch=branch,
            author_name=author_name,
            author_email=author_email,
            commit_timestamp=commit_timestamp,
            commit_title=commit_title,
            commit_id=commit_id)
    }
    SendToUser(push_msg)


def sendMergeMsg(userid, merge_info=None):
    project, source_branch, target_branch, merge_commit_sha, commit_title, commit_timestamp, author_name, author_email, assignees = \
        merge_info['project'], merge_info['source_branch'], merge_info['target_branch'], merge_info['merge_commit_sha'], \
        merge_info['commit_title'], merge_info['commit_timestamp'], merge_info['author_name'], merge_info[
            'author_email'], \
        merge_info['assignees']

    merge_msg = {
        "userid": userid,
        "subject": "项目**{0}**收到一次Merge提交\n".format(project),
        "content": ">**提交详情**\n  \
                   源分支：<font color=\"info\">{source_branch}</font>\n \
                   目标分支：<font color=\"info\">{target_branch}</font>\n \
                   提交者：<font color=\"info\">{author_name}</font>\n \
                   分配者：<font color=\"info\">{assignees}</font>\n \
                   邮   箱：<font color=\"info\">{author_email}</font>\n> \
                   时   间：<font color=\"info\">{commit_timestamp}</font>\n \
                   提交描述：<font color=\"info\">{commit_title}</font>\n  \
                   提交ID：<font color=\"info\">{merge_commit_sha}</font>\n".format(
            source_branch=source_branch,
            target_branch=target_branch,
            author_email=author_email,
            commit_timestamp=commit_timestamp,
            commit_title=commit_title,
            merge_commit_sha=merge_commit_sha,
            assignees=assignees,
            author_name=author_name
        )
    }
    SendToUser(merge_msg)
