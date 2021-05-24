#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from pydantic import BaseModel


class Item(BaseModel):
    ToUserName: str
    AgentID: str
    Encrypt: str
