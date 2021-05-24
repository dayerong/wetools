#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from api.token import get_current_active_user
from routers import users, auth_token_ad, swagger, wxmsg, common, databases
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

tags_metadata = [
    {
        "name": "Users",
        "description": "Manage **users**."
    },
    {
        "name": "SAP",
        "description": "Manage **SAP**.",
    },
]

app = FastAPI(
    openapi_url="/openapi.json",
    docs_url=None,
    redoc_url=None,
    title="Infrastructure Tools",
    description="Windows Active Directory API",
    version="1.0.0"
)

origins = [
    "http://192.168.1.46:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(swagger.router)
app.include_router(users.router, dependencies=[Depends(get_current_active_user)])
app.include_router(databases.router, dependencies=[Depends(get_current_active_user)])
app.include_router(auth_token_ad.router)
app.include_router(wxmsg.router)
app.include_router(common.router)

if __name__ == '__main__':
    uvicorn.run(app='main:app', host="0.0.0.0", port=8000, reload=True, debug=True)
