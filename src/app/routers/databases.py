#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from api.dbmanager import backupBMP

router = APIRouter()
templates = Jinja2Templates(directory="app/templates/")


# 备份业中BMP数据库表
@router.get("/databases/bmp", response_class=HTMLResponse)
async def bmp(request: Request):
    content = {"request": request, "msg": "bmp"}
    return templates.TemplateResponse("databases.html", content)


@router.post("/databases/bmp")
async def backup_bmp(request: Request,
                     name: str = Form(...)):
    rs = backupBMP(name)
    status = rs[0]

    if status == 10:
        content = {"request": request, "tablename": name, "msg": "bmp", "status": "notable"}
        return templates.TemplateResponse("failed_msg.html", content)
    elif status == 11:
        filename = rs[1]
        content = {"request": request, "filename": filename, "msg": "bmp", "status": "nofile"}
        return templates.TemplateResponse("failed_msg.html", content)
    elif status == 0:
        filename = rs[1]
        content = {"request": request, "filename": filename, "msg": "bmp"}
        return templates.TemplateResponse("sucess_msg.html", content)
