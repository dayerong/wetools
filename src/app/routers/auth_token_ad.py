#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from datetime import timedelta
from fastapi import Depends, APIRouter, Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from api.token import create_access_token, authenticate_ad_user, get_current_active_user, authenticate_google_code
from api.wxauth import gettoken, getuserinfo, getappinfo, authorize_url
from config.conf import token_config, infra_wxauth_config
from model.tokenmodels import *

templates = Jinja2Templates(directory="app/templates/")

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = token_config['ACCESS_TOKEN_EXPIRE_MINUTES']


@router.post("/auth", response_class=RedirectResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 code: str = Form(...)) -> RedirectResponse:
    user = authenticate_ad_user(form_data.username, form_data.password)
    authenticate_google_code(code)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user}, expires_delta=access_token_expires).decode("utf-8")
    response = RedirectResponse(url="/index", status_code=302)
    response.set_cookie(key="Authorization", value=access_token, httponly=True, path='/', max_age=3600)
    return response


@router.get("/login")
def login(request: Request):
    Corpid = infra_wxauth_config["Corpid"]
    Secret = infra_wxauth_config["Secret"]
    Agentid = infra_wxauth_config["Agentid"]
    token = gettoken(Corpid, Secret)
    code = request.query_params.get('code')

    # 企业微信授权免登陆
    if code:
        userinfo = getuserinfo(token, code)
        userid = userinfo["UserId"]
        users_in_app = getappinfo(token, Agentid)
        users = [item[key] for item in users_in_app['allow_userinfos']['user'] for key in item]

        if userid in users:
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(data={"sub": userid}, expires_delta=access_token_expires).decode("utf-8")
            response = RedirectResponse(url="/index", status_code=302)
            response.set_cookie(key="Authorization", value=access_token, httponly=True, path='/', max_age=3600)
            return response
        else:
            return templates.TemplateResponse("login.html", {"request": request})
    else:
        return templates.TemplateResponse("login.html", {"request": request})


@router.get("/index", response_model=ADUser)
def index(request: Request,
          current_user: ADUser = Depends(get_current_active_user)):
    if current_user:
        return templates.TemplateResponse("index.html", {"request": request, "username": current_user})


@router.get("/", response_class=RedirectResponse)
def root() -> RedirectResponse:
    response = RedirectResponse(url="/login")
    return response


@router.get("/logout")
def logout() -> RedirectResponse:
    response = RedirectResponse(url="/")
    response.delete_cookie(key="Authorization")
    return response


@router.get("/auth/code", response_class=RedirectResponse)
def root() -> RedirectResponse:
    corpid = infra_wxauth_config["Corpid"]
    url = "http://x.x.com/login"
    state = 'infra'
    redirect_url = authorize_url(corpid, url, state)
    response = RedirectResponse(url=redirect_url)
    return response
