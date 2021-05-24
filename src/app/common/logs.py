#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from config.conf import log_config
import logging
import os


class Log(object):
    def __init__(self):
        self.logformat = log_config['logformat']
        self.filename = log_config['file']
        self.datefmt = log_config['datefmt']

        path = self.filename[0:self.filename.rfind("/")]
        if not os.path.isdir(path):
            os.makedirs(path)

        if not os.path.isfile(self.filename):
            f = open(self.filename, 'w')
            f.close()

    def info(self, loggername, logcontent):
        logging.basicConfig(filename=self.filename, format=self.logformat, datefmt=self.datefmt)
        logger = logging.getLogger(loggername)
        logger.setLevel(20)
        logger.info(logcontent)

    def error(self, loggername, logcontent):
        logging.basicConfig(filename=self.filename, format=self.logformat, datefmt=self.datefmt)
        logger = logging.getLogger(loggername)
        logger.setLevel(40)
        logger.error(logcontent)
