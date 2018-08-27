#!/usr/bin/python
# -*- coding:utf-8 -*-

import logging
import os
import time
from logging import handlers
from Adeployment.conf.conf import *
from Adeployment.core.environments import get_logpath

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def now_dates():
    new_date = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time()))
    return new_date



def logger(LOG_INFO,LOG_LEVEL,log_type='ADAdmin_Log'):
    # 写入log文件，保存log名称到DB
    logs_name = get_logpath()
    logger = logging.getLogger(log_type)
    logger.setLevel(LOG_LEVEL)
    ch = logging.StreamHandler()
    ch.setLevel(LOG_LEVEL)
    fh = handlers.RotatingFileHandler(logs_name)
    fh.setLevel(LOG_LEVEL)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(ch)
    logger.addHandler(fh)
    logger.info(LOG_INFO)
    logger.removeHandler(ch)
    logger.removeHandler(fh)
    return logger

log_name = LOGS + "-" + now_dates() + '.log'

def logger_run(LOG_INFO,LOG_LEVEL,log_type='ADAdmin_Log'):
    # 写入log文件，保存log名称到DB
    logger = logging.getLogger(log_type)
    logger.setLevel(LOG_LEVEL)
    ch = logging.StreamHandler()
    ch.setLevel(LOG_LEVEL)
    fh = handlers.RotatingFileHandler(log_name)
    fh.setLevel(LOG_LEVEL)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(ch)
    logger.addHandler(fh)
    logger.info(LOG_INFO)
    logger.removeHandler(ch)
    logger.removeHandler(fh)
    return logger

def check_logpath():
    if  os.path.isfile(LOGS):
        os.remove(LOGS)
