#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from pydantic import BaseModel


# token url相应模型
class Token(BaseModel):
    access_token: str
    token_type: str


# 令牌数据模型
class TokenData(BaseModel):
    username: str = None


# 用户基础模型
class User(BaseModel):
    username: str
    email: str = None
    full_name: str = None
    disabled: bool = None


# 用户输入数据模型
class UserInDB(User):
    hashed_password: str


# AD用户模型
class ADUser(BaseModel):
    username: str
    dn: str
    email: str = None
    name: str = None
    disabled: bool = None
