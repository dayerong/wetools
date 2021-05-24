#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import time
from common.ssh import ssh_exec_command
from config.conf import db_backup_config, bmp_config
from common.logs import Log


class backupDB(object):
    def __init__(self):
        self.ip = db_backup_config['ip']
        self.user = db_backup_config['user']
        self.password = db_backup_config['password']
        self.path = db_backup_config['path']
        self.port = 22
        self.log = Log()

    def backupTable(self, host, user, password, database, table):
        # 创建备份目录
        dir_name = time.strftime('%Y%m%d')
        mkdir_cmd = 'mkdir -p {path}/{dir}'.format(path=self.path, dir=dir_name)
        ssh_exec_command(self.ip, self.port, self.user, self.password, mkdir_cmd)
        self.log.info('backupDB', '创建备份目录:{}'.format(dir_name))

        # 备份表
        ctime = time.strftime('%m%d%H%M')
        backup_table_name = '{table}_{ctime}.sql'.format(table=table, ctime=ctime)
        sqlcmd = 'mysqldump -h {host} -u {user} -p{password} --databases {database} --tables {table} > {path}/{dir}/{backup_name}'.format(
            host=host, user=user, password=password, database=database, table=table, path=self.path,
            backup_name=backup_table_name, dir=dir_name)
        status, stdout, stderr = ssh_exec_command(self.ip, self.port, self.user, self.password, sqlcmd)
        self.log.info('backupDB', '备份表:{}'.format(table))

        if status == 6 and 'Couldn\'t find table' in stderr.decode():
            # 表不存在，会生成一个空的sql文件，需要删除
            rm_cmd = 'rm -rf {path}/{dir}/{backup_name}'.format(path=self.path, dir=dir_name,
                                                                backup_name=backup_table_name)
            ssh_exec_command(self.ip, self.port, self.user, self.password, rm_cmd)
            self.log.error('backupDB', '删除无效备份文件:{}'.format(backup_table_name))
            return 10, table
        elif status == 0:
            checkcmd = 'ls {path}/{dir}/{backup_name}'.format(path=self.path, backup_name=backup_table_name,
                                                              dir=dir_name)
            status, stdout, stderr = ssh_exec_command(self.ip, self.port, self.user, self.password, checkcmd)
            self.log.info('backupDB', '成功备份:{path}/{dir}/{backup_name}'.format(path=self.path,
                                                                               backup_name=backup_table_name,
                                                                               dir=dir_name))
            file = stdout.decode().split('\n')[0]
            return status, file
        else:
            self.log.error('backupDB', 'stderr: {}'.format(stderr.decode()))


def backupBMP(table):
    host = bmp_config['host']
    user = bmp_config['user']
    passwd = bmp_config['passwd']
    db = bmp_config['db']
    ssh = backupDB()
    status, file = ssh.backupTable(host, user, passwd, db, table)
    if status == 0:
        return status, file
    elif status == 10:
        return status,
    elif status != 0:
        return 11, file
