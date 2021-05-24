#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# 域控信息
dc_config_prd = {
    'dc': '',
    'admin': '',
    'pwd': '',
    'ip': ''
}

# Token
token_config = {
    'SECRET_KEY': '',  # 密钥
    'ALGORITHM': 'HS256',  # 算法
    'ACCESS_TOKEN_EXPIRE_MINUTES': 30  # 访问令牌过期分钟
}

# log设置
log_config = {
    'logformat': '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    'loglevel': 20,  # 0 NOSET, 10 DEBUG, 20 INFO, 30 WARNING, 40 ERROR, 50 CRITICAL
    'file': './app/logs/app.log',
    'datefmt': '%Y/%m/%d %H:%M:%S',
    'ssh_log_file': './app/logs/ssh.log'
}

# 用户认证
userauth_config = {
    'encodingAESKey': '',
    'auth_dn': 'OU=系统运维组,OU=集团信息技术部,OU=公司,DC=commany,DC=com'
}

# swagger用户认证
swagger_auth_config = {
    'username': '',
    'password': '',
    'encodingAESKey': ''
}

# 谷歌密码认证
google_authenticator_config = {
    'issuer_name': '',
    'secret': ''
}

# 用户默认配置
users_config = {
    'ad_user_default_password': '',
    'exmail_default_password': '',
}

# 企业邮箱信息
exmail_config = {
    'Corpid': '',
    'Secret': '',
    'Defaultpassword': ''
}

# 企业微信应用网页授权、接收消息API信息
infra_wxauth_config = {
    'Corpid': '',
    'Secret': '',
    'Agentid': '',
    'Token': '',
    'EncodingAESKey': ''
}

# infra-tools API
infratools_config = {
    'search_users_api_url': 'http://10.0.1.13:8100/ad/v2/users',
    'reset_password_api_url': 'http://10.0.1.13:8100/ad/v1/users',
    'default_password': '',
}

# SAP接口：人员信息全量查询接口
sap_employee_config = {
    'url': '',
    'username': '',
    'password': ''
}

# SAP接口： 查询邮箱接口
sap_emp_email_config = {
    'url': '',
    'username': '',
    'password': ''
}

# 中间数据库连接参数
mid_db_config = {
    'host': '',
    'port': 3306,
    'user': '',
    'passwd': '',
    'db': '',
    'charset': 'utf8'
}

# Gitlab Webhooks配置
git_hooks_config = {
    'secret_token': '',
    'userid': ''  # 企业微信通知人
}

# 企业微信代码发布服务应用
itsvc_config = {
    'CorpID': '',
    'Corpsecret': '',
    'Agentid': ''
}

# Jenkins信息
jenkins_config = {
    'jenkins_url': '',
    'user': '',
    'password': ''
}

# 数据库备份服务器信息
db_backup_config = {
    'ip': '',
    'user': '',
    'password': '',
    'path': ''
}

# RDS 数据库
bmp_config = {
    'host': '',
    'user': '',
    'passwd': '',
    'db': ''
}
