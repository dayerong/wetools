#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from datetime import timedelta, datetime
from fastapi import HTTPException, Depends, Header
from jwt import PyJWTError
from starlette import status
from api.ActiveDirectory import OperationAD
from config.conf import token_config, userauth_config
from common.userauth import OAuth2PasswordBearerWithCookie
from common.google_authenticator import get_totp
import jwt
from api.wxauth import get_authenticated_user

from model.tokenmodels import ADUser, TokenData

SECRET_KEY = token_config['SECRET_KEY']
ALGORITHM = token_config['ALGORITHM']

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/auth")


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_ad_user(account: str,
                         password: str):
    op = OperationAD()
    rs = op.login_auth(account, password)
    if rs['result'] == 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "ActiveDirectory"},
        )
    return account


def authenticate_google_code(code: str):
    totp = get_totp()
    if code != totp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google authenticator code is incorrect",
            headers={"WWW-Authenticate": "Google Authenticator"},
        )
    return True


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "ActiveDirectory"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except PyJWTError:
        raise credentials_exception
    account = token_data.username
    return account


async def get_current_active_user(current_user: ADUser = Depends(get_current_user)):
    username = get_authenticated_user(current_user)
    if not username:
        op = OperationAD()
        userdn = op.get_authenticated_user(current_user)
        if userdn != userauth_config['auth_dn']:
            raise HTTPException(status_code=400, detail="{} is an unauthenticated user.".format(current_user))
        return current_user
    else:
        return username


async def authcheck(secretkey: str = Header(..., )):
    """只做简单的安全控制"""
    if secretkey != token_config['SECRET_KEY']:
        raise HTTPException(
            status_code=401,
            detail="Token校验失败",
            headers={"X-Error": "Secretkey failed validation"},
        )
