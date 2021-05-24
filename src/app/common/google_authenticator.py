#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import hmac
import base64
import struct
import hashlib
import time
import pyotp
from qrcode import QRCode
from qrcode import constants
from config.conf import google_authenticator_config


def get_hotp_token(secret, intervals_no):
    """This is where the magic happens."""
    key = base64.b32decode(normalize(secret), True)  # True is to fold lower into uppercase
    # key = base64.b32decode(secret, True)
    msg = struct.pack(">Q", intervals_no)
    h = bytearray(hmac.new(key, msg, hashlib.sha1).digest())
    o = h[19] & 15
    h = str((struct.unpack(">I", h[o:o + 4])[0] & 0x7fffffff) % 1000000)
    return prefix0(h)


def get_totp_token(secret):
    """The TOTP token is just a HOTP token seeded with every 30 seconds."""
    return get_hotp_token(secret, intervals_no=int(time.time()) // 30)


def normalize(key):
    """Normalizes secret by removing spaces and padding with = to a multiple of 8"""
    k2 = key.strip().replace(' ', '')
    # k2 = k2.upper()	# skipped b/c b32decode has a foldcase argument
    if len(k2) % 8 != 0:
        k2 += '=' * (8 - len(k2) % 8)
    return k2


def prefix0(h):
    """Prefixes code with leading zeros if missing."""
    if len(h) < 6:
        h = '0' * (6 - len(h)) + h
    return h


def get_qr_image(secret, zcode, issuer_name):
    key = base64.b32decode(normalize(secret), True)  # True is to fold lower into uppercase
    content = pyotp.totp.TOTP(secret).provisioning_uri(name=zcode, issuer_name=issuer_name)
    qr = QRCode(version=1,
                error_correction=constants.ERROR_CORRECT_L,
                box_size=6,
                border=4, )

    qr.add_data(content)
    qr.make(fit=True)
    img = qr.make_image()
    img.save('../public/resource/qr/{name}.png'.format(name=zcode))


def get_totp():
    secret = google_authenticator_config['secret']
    totp = get_totp_token(secret)
    return totp


def create_qr(zcode):
    issuer_name = google_authenticator_config['issuer_name']
    secret = google_authenticator_config['secret']
    get_qr_image(secret, zcode, issuer_name)
