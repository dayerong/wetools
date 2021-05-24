#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html

from common.userauth import get_current_username

router = APIRouter()


# swagger安全配置
@router.get("/Swagger", include_in_schema=False)
async def get_swagger(credentials: HTTPBasicCredentials = Depends(get_current_username)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Infrastructure Tools Project")
