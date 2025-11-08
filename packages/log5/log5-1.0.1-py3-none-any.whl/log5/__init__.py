#!/usr/bin/env python
# -*- coding: utf-8 -*-
#===============================================================================
#
# Copyright (c) 2017 <> All Rights Reserved
#
#
# File: /Users/hain/chat-log-burnish/purelog/common/log.py
# Author: Hai Liang Wang
# Date: 2017-10-25:16:58:57
#
#===============================================================================

"""
   
"""
from __future__ import print_function
from __future__ import division

__copyright__ = "Copyright (c) 2017 . All Rights Reserved"
__author__    = "Hai Liang Wang"
__date__      = "2017-10-25:16:58:57"


import os
import sys
import logging
import json
import atexit

curdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(curdir)

if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding("utf-8")
    # raise "Must be using Python 3"

ENV = os.environ.copy()

'''
日志输出
'''
OUTPUT_STDOUT = 1
OUTPUT_FILE = 2
OUTPUT_BOTH = 3

'''
日志级别
'''
CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0

'''
日志格式
'''
LOG_FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

LOG_LEVEL= ENV.get("LOG_LEVEL", "INFO")
LOG_FILE= ENV.get("LOG_FILE", None)

if isinstance(LOG_LEVEL, str):
    LOG_LEVEL = LOG_LEVEL.upper()
    if LOG_LEVEL.lower() == "WARN":
        LOG_LEVEL = "WARNING"

print("[log5] logger settings LOG_FILE %s, LOG_LEVEL %s >> usage checkout https://github.com/hailiang-wang/python-log5" % (LOG_FILE, LOG_LEVEL))

# log would print twice with logging.basicConfig
# logging.basicConfig(level=LOG_LEVEL)

'''
Handlers
'''
fh = None
ch = logging.StreamHandler()
ch.setFormatter(LOG_FORMATTER)
ch.setLevel(LOG_LEVEL)

# handle exit
def exit_handler():
    global fh
    if fh and LOG_FILE:
        print("\n[log5] LOG FILE path %s" % LOG_FILE)
        print("[log5] exit gracefully ...")

atexit.register(exit_handler)


def init_fh_global():
    global fh
    if LOG_FILE is None:
        print("[log5] WARN: Environment varibale LOG_FILE is empty, can not init log5 normally for file logger")
        return
    
    if fh == None:
        fh = logging.FileHandler(LOG_FILE)
        fh.setFormatter(LOG_FORMATTER)
        fh.setLevel(LOG_LEVEL)

def set_log_level(level = "DEBUG"):
    fh.setLevel(level)
    ch.setLevel(level)

def get_logger(logger_name, output_mode = OUTPUT_STDOUT):
    logger = logging.getLogger(logger_name)
    
    # https://medium.com/neural-engineer/python-logging-propagation-and-disabling-noisy-logs-6560b2119865
    # Remove all default handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # # Reset logger hierarchy - this clears the internal dict of loggers
    # logging.Logger.manager.loggerDict.clear()

    global fh
    global ch

    if output_mode == OUTPUT_STDOUT:
        logger.addHandler(ch)

    if output_mode == OUTPUT_FILE:
        init_fh_global()
        if fh: logger.addHandler(fh)

    if output_mode == OUTPUT_BOTH:
        logger.addHandler(ch)

        init_fh_global()
        if fh: logger.addHandler(fh)

    logger.setLevel(DEBUG)
    logger.propagate=False # https://signoz.io/guides/log-messages-appearing-twice-with-python-logging/

    return logger


def pretty(j, indent=4, sort_keys=True):
    """
    get dict object/json as pretty string
    :param j:
    :return:
    """
    return json.dumps(j, indent=indent, sort_keys=sort_keys, ensure_ascii=False, default=str)


def LN(x):
    """
    log name 获得模块名字，输出日志短名称
    LN(__name__)
    """
    return x.split(".")[-1]

if __name__ == "__main__":
    logger = get_logger(LN(__name__), output_mode=OUTPUT_BOTH)
    logger.debug('bar')
    logger.info('foo')