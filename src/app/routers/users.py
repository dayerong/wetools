#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from api.ActiveDirectory import OperationAD
from config.conf import users_config
from api import exmail, sap_middle, sap

router = APIRouter()
templates = Jinja2Templates(directory="app/templates/")


# 修改AD用户密码
@router.get("/users/ad", response_class=HTMLResponse)
async def users(request: Request, ):
    content = {"request": request, "msg": "users"}
    return templates.TemplateResponse("users.html", content)


@router.post("/users/ad")
async def reset_password(request: Request,
                         name: str = Form(...)):
    password = users_config["ad_user_default_password"]
    op = OperationAD()
    rs = op.modify_password(name, password)["result"]
    if rs == 1:
        content = {"request": request, "name": name, "msg": "no_users"}
        return templates.TemplateResponse("failed_msg.html", content)
    else:
        content = {"request": request, "name": name, "msg": "users"}
        return templates.TemplateResponse("sucess_msg.html", content)


# 修改企业邮箱用户密码
@router.get("/users/exmail", response_class=HTMLResponse)
async def users(request: Request):
    content = {"request": request, "msg": "extmail"}
    return templates.TemplateResponse("users.html", content)


@router.post("/users/exmail")
async def reset_password(request: Request,
                         email: str = Form(...)):
    rs = exmail.update_exmail_password(email)
    if rs == 0:
        content = {"request": request, "email": email, "msg": "extmail"}
        return templates.TemplateResponse("sucess_msg.html", content)
    else:
        content = {"request": request, "email": email, "msg": "no_extmails"}
        return templates.TemplateResponse("failed_msg.html", content)


# 禁用邮箱及AD用户
@router.get("/users/disable", response_class=HTMLResponse)
async def users(request: Request, ):
    content = {"request": request, "msg": "disable"}
    return templates.TemplateResponse("users.html", content)


@router.post("/users/disable")
async def disable_users(request: Request,
                        email: str = Form(...)):
    rs = exmail.disable_exmail_user(email)
    if rs == 0:
        # 从中间库查询工号
        # account = sap_middle.getZcodeFromDB(email)
        # 从SAP查询工号
        account = sap.getZcodeFromSap(email)
        if account:
            op = OperationAD()
            rs = op.modify_user_status(account, 'disable')
            if rs["result"] != 1:
                content = {"request": request, "email": email, "account": account, "msg": "disable"}
                return templates.TemplateResponse("sucess_msg.html", content)
            else:
                content = {"request": request, "email": email, "account": account, "msg": "not_in_ad"}
                return templates.TemplateResponse("failed_msg.html", content)
        else:
            content = {"request": request, "email": email, "msg": "not_in_sap"}
            return templates.TemplateResponse("failed_msg.html", content)
    else:
        content = {"request": request, "email": email, "msg": "no_extmails_disable"}
        return templates.TemplateResponse("failed_msg.html", content)
