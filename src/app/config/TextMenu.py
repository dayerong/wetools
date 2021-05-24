#!/usr/bin/env python
# -*- coding: utf-8 -*-


def DesktopMenu():
    return """请选择（输入忽略大小写）：
■  查询AD用户
    输入：【q+空格+工号】

■  重置AD用户密码
    输入：【password+空格+工号】
    
■  重置企业邮箱密码
    输入：【mail+空格+Email】
"""


def search_ad_user(info):
    if isinstance(info, dict):
        name, account, title, dep, tel, mail = info["displayName"], info["sAMAccountName"], info["title"], '/'.join(
            info["cn"].split(",")[::-1][2:][:-1]).replace("OU=", ""), info["telephoneNumber"], ''.join(info["mail"])
        return """
姓名：%s
工号：%s
部门：%s
职位：%s
联系电话：%s
邮箱：%s
    """ % (name, account, dep, title, tel, mail)
    else:
        return "工号【%s】不存在" % info.upper()


def reset_password(name):
    return """【%s】已修改为初始密码：Cuanon@2021
！！！请提醒用户立即修改密码！！！""" % name


def reset_password_error(name):
    return "【%s】用户密码修改失败，请联系管理员！" % name


def reset_email(name):
    return """【%s】已修改为初始密码：Asia2021
！！！请提醒用户立即修改密码！！！""" % name


def reset_email_error(name):
    return "【%s】用户密码修改失败，请联系管理员！" % name


def reset_email_noid(name):
    return "【%s】邮箱不存在，请确认！" % name
