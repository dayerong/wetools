#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import paramiko
import socket
from config.conf import log_config
from common.logs import Log


def ssh_exec_command(ip, port, username, password, cmd):
    log = Log()
    try:
        path = log_config['ssh_log_file'][0:log_config['ssh_log_file'].rfind("/")]
        if not os.path.isdir(path):
            os.makedirs(path)

        if not os.path.isfile(log_config['ssh_log_file']):
            f = open(log_config['ssh_log_file'], 'w')
            f.close()

        paramiko.util.log_to_file(log_config['ssh_log_file'])
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=ip, port=port, username=username, password=password, timeout=60, allow_agent=False,
                    look_for_keys=False)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        exit_status = stdout.channel.recv_exit_status()
        return exit_status, stdout.read(), stderr.read()
    except paramiko.ssh_exception.AuthenticationException:
        log.error('ssh_connect', '用户名与密码验证失败')
        return 'AuthenticationException'
    except socket.timeout:
        log.error('ssh_connect', '连接失败')
        return 'timeout'
