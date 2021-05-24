#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from ldap3 import *
from config.conf import dc_config_prd
from common.logs import Log
from config.conf import userauth_config
from common.usercrypto import aes_decode


class AdOperation(object):
    def __init__(self, domain, ip, admin, pwd=None):
        self.domain = domain
        self.DC = ','.join(['DC=' + dc for dc in domain.split('.')])  # cuanon.com -> DC=cuanon,DC=com
        self.pre = domain.split('.')[0].upper()
        self.ip = ip
        self.admin = admin
        self.pwd = pwd
        self.server = Server(self.ip, get_info=ALL, use_ssl=True)
        # self.server = Server(self.ip, get_info=ALL)
        self.conn = Connection(self.server, user=self.pre + '\\' + self.admin, password=self.pwd, auto_bind=True,
                               authentication=NTLM)

    # 查找指定OU下的用户
    def search_user_whole(self, user):
        try:
            att_list = ['displayName', 'sAMAccountname', 'title', 'mail', 'mobile']
            self.conn.search(search_base=user,
                             search_filter='(objectclass=user)',  # 查询数据的类型
                             attributes=att_list)  # 查询数据的哪些属性
            dn = self.conn.response[0]['dn']
            cn = {}.fromkeys(('cn',), dn)
            attr = self.conn.response[0]['attributes']
            rs = {}
            rs.update(cn)
            rs.update(dict(attr))
            return rs
        except:
            return False

    # 查找AD中所有用户
    def search_user(self, user):
        att_list = ['displayName', 'sAMAccountname', 'title', 'mail', 'mobile', 'telephoneNumber']
        self.conn.search(search_base=self.DC,
                         search_filter='(|(displayName={})(sAMAccountname={}))'.format(user, user),  # 查询数据的类型
                         attributes=att_list)  # 查询数据的哪些属性
        # 注意：查询不到返回也是True
        user_rs = []
        for i in range(len(self.conn.response[:-3])):
            rs = {}
            dn = self.conn.response[:-3][i]['dn']
            # 创建字典
            cn = {}.fromkeys(('cn',), dn)
            attr = self.conn.response[:-3][i]['attributes']
            rs.update(cn)
            rs.update(dict(attr))
            user_rs.append(rs)
        if user_rs:
            rs = {"result": user_rs}
            return rs
        else:
            return False

    # 根据登录名查找用户的DN
    def search_user_dn(self, user):
        att_list = 'distinguishedName'
        self.conn.search(search_base=self.DC,
                         search_filter='(sAMAccountname={})'.format(user),  # 查询数据的类型
                         attributes=att_list)  # 查询数据的哪些属性
        # 注意：查询不到返回也是True
        logger = Log()
        if len(self.conn.response) != 3:
            user_dn = self.conn.response[:-3][0]['dn']
            return user_dn
        else:
            logger.info('search_user_dn', '用户【 {0} 】不存在'.format(user))
            return False

    # 创建用户
    def add_user(self, info=None):
        [name, account, dn, title, mp, email] = info['姓名'], info['工号'], info['部门'], info['职务'], info['手机'], info['邮箱']
        user_attr = {'userPrincipalName': account + '@' + self.domain,  # 登录名
                     'sAMAccountname': account,  # 以前版本登录名
                     'userAccountControl': 544,  # 启用账户
                     'title': title,  # 职务
                     'givenName': name[1:],  # 名
                     'sn': name[0:1],  # 姓
                     'displayname': name,  # 姓名
                     'mail': email,  # 邮箱
                     'mobile': mp  # 手机号
                     }

        cn_name = account + "-" + name
        dn_base = 'CN=' + cn_name + ',' + ','.join(['OU=' + ou for ou in dn.split('/')[::-1]]) + ',' + self.DC
        res = self.search_user_whole(dn_base)

        if res:
            return {"error": "user already exists"}
        else:
            self.conn.add(dn=dn_base, object_class='user', attributes=user_attr)
            return {"staus": self.conn.result}

    # 删除用户
    def remove_user(self, account, department):
        att_list = ['displayName', 'sAMAccountname']
        self.conn.search(search_base=self.DC,
                         search_filter='(sAMAccountname={})'.format(account),
                         attributes=att_list)
        res = self.conn.response[:-3]
        if res:
            cn = self.conn.response[:-3][0]['dn']
            user_dep = ','.join(cn.split(',')[1:])
            input_dep = ','.join(['OU=' + ou for ou in department.split('/')[::-1]]) + ',' + self.DC
            if user_dep == input_dep:
                try:
                    self.conn.delete(dn=cn)
                    return {"staus": self.conn.result}
                except:
                    return {"staus": self.conn.result}
            else:
                return {"error": "department mismatch"}
        else:
            return {"error": "user does not exists"}

    # 用户修改密码
    def modify_user_password(self, user_dn, password):
        cryptokey = userauth_config['encodingAESKey']
        decode_passwd = aes_decode(password, cryptokey)
        if decode_passwd:
            res = self.conn.extend.microsoft.modify_password(user_dn, decode_passwd)
            logger = Log()
            if res:
                logger.info('modify_user_password', '用户【 {0} 】成功密码修改为:  {1}'.format(user_dn, password))
                return self.conn.result
            elif self.conn.result['result'] == 53:
                logger.info('modify_user_password', '用户【 {0} 】密码修改失败，不符合密码策略: {1}'.format(user_dn, password))
                rs = {"result": 1, "description": "password policy mismatch"}
                return rs
            else:
                logger.info('modify_user_password', '用户【 {0} 】密码修改失败，其它错误: '.format(user_dn))
                logger.info('modify_user_password', self.conn.result)
                rs = {"result": 1, "description": "unknown error"}
                return rs
        else:
            return {"result": 1, "description": "decrypt failed"}

    # 禁用用户
    def disable_user(self, user_dn):
        res = self.conn.modify(user_dn, {'userAccountControl': [('MODIFY_REPLACE', 514)]})
        logger = Log()
        logger.info('disable_user', '用户【 {0} 】已禁用: '.format(user_dn))
        return self.conn.result

    # 启用用户
    def enable_user(self, user_dn):
        res = self.conn.modify(user_dn, {'userAccountControl': [('MODIFY_REPLACE', 512)]})
        logger = Log()
        logger.info('disable_user', '用户【 {0} 】已启用: '.format(user_dn))
        return self.conn.result

    def closeconn(self):
        self.conn.unbind()


class LoginAuth(object):
    def __init__(self, domain, ip, username=None, pwd=None):
        self.domain = domain
        self.DC = ','.join(['DC=' + dc for dc in domain.split('.')])  # cuanon.com -> DC=cuanon,DC=com
        self.pre = domain.split('.')[0].upper()
        self.ip = ip
        self.username = username
        self.pwd = pwd

    # 验证用户密码
    def userauth(self, account, password):
        try:
            self.username = account
            self.pwd = password
            # self.server = Server(self.ip, get_info=ALL, use_ssl=True)
            self.server = Server(self.ip, get_info=ALL)
            self.conn = Connection(self.server, user=self.pre + '\\' + self.username, password=self.pwd, auto_bind=True,
                                   authentication=NTLM)
            return {'result': 0, 'description': 'success'}
        except:
            return {'result': 1, 'description': 'auth failed'}

    def closeconn(self):
        self.conn.unbind()


class OperationAD(object):
    def __init__(self):
        self.domain = dc_config_prd['dc']
        self.ip = dc_config_prd['ip']
        self.admin = dc_config_prd['admin']
        self.pwd = dc_config_prd['pwd']

    def query_user(self, user):
        op = AdOperation(self.domain, self.ip, self.admin, self.pwd)
        rs = op.search_user(user)
        op.closeconn()
        return rs

    def create_user(self, userinfo):
        op = AdOperation(self.domain, self.ip, self.admin, self.pwd)
        rs = op.add_user(userinfo)
        op.closeconn()
        return rs

    def delete_user(self, account, department):
        op = AdOperation(self.domain, self.ip, self.admin, self.pwd)
        rs = op.remove_user(account, department)
        op.closeconn()
        return rs

    def modify_password(self, account, password):
        op = AdOperation(self.domain, self.ip, self.admin, self.pwd)
        user_dn = op.search_user_dn(account)
        if user_dn:
            rs = op.modify_user_password(user_dn, password)
            op.closeconn()
            return rs
        else:
            rs = {"result": 1, "description": "user does not exists"}
            op.closeconn()
            return rs

    def modify_user_status(self, account, flag):
        op = AdOperation(self.domain, self.ip, self.admin, self.pwd)
        user_dn = op.search_user_dn(account)
        if user_dn:
            if flag == 'enable':
                rs = op.enable_user(user_dn)
                op.closeconn()
                return rs
            elif flag == 'disable':
                rs = op.disable_user(user_dn)
                op.closeconn()
                return rs
        else:
            rs = {"result": 1, "description": "user does not exists"}
            op.closeconn()
            return rs

    def login_auth(self, account, password):
        op = LoginAuth(self.domain, self.ip)
        rs = op.userauth(account, password)
        return rs

    def get_authenticated_user(self, account):
        op = AdOperation(self.domain, self.ip, self.admin, self.pwd)
        user_dn = op.search_user_dn(account)
        auth_dn = ','.join(user_dn.split(',')[-5:])
        return auth_dn
