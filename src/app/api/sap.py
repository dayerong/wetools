#!/usr/bin/env python
# -*- encoding: utf-8 -*-


import datetime
import json
from suds.client import Client
from suds.transport.https import HttpAuthenticated
from suds.sudsobject import asdict

from config.conf import sap_employee_config, sap_emp_email_config


def recursive_asdict(d):
    """Convert Suds object into serializable format."""
    out = {}
    for k, v in asdict(d).items():
        if hasattr(v, '__keylist__'):
            out[k] = recursive_asdict(v)
        elif isinstance(v, list):
            out[k] = []
            for item in v:
                if hasattr(item, '__keylist__'):
                    out[k].append(recursive_asdict(item))
                else:
                    out[k].append(item)
        else:
            out[k] = v
    return out


def suds_to_json(data):
    return json.dumps(recursive_asdict(data))


def getZcodeFromSap(mail):
    url = sap_emp_email_config["url"]
    username = sap_emp_email_config["username"]
    password = sap_emp_email_config["password"]
    today = datetime.date.today()

    t = HttpAuthenticated(username=username, password=password)
    client = Client(url, transport=t)
    rs = client.service.ZHR_GET_EMP_MAIL(I_BEGDA=today, I_EMAIL=mail.upper())
    data = recursive_asdict(rs)
    zcode = data["O_ZCODE"]
    return zcode
