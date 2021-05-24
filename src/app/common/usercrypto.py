#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import base64
from Crypto.Cipher import AES


# 解密
def aes_decode(text, key):
    try:
        aes = AES.new(str.encode(key), AES.MODE_ECB)  # 初始化加密器
        decrypted_text = aes.decrypt(base64.decodebytes(bytes(text, encoding='utf8'))).decode("utf8")  # 解密
        decrypted_text = decrypted_text[:-ord(decrypted_text[-1])]  # 去除多余补位
        return decrypted_text
    except Exception as e:
        return False


# 加密
def aes_encode(text, key):
    while len(text) % 16 != 0:  # 补足字符串长度为16的倍数
        text += (16 - len(text) % 16) * chr(16 - len(text) % 16)
    data = str.encode(text)
    aes = AES.new(str.encode(key), AES.MODE_ECB)  # 初始化加密器
    encrypted_text = str(base64.encodebytes(aes.encrypt(data)), encoding='utf8').replace('\n', '')  # 加密
    return encrypted_text
