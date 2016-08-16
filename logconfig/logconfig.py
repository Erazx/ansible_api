#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
try:
    # for python 2.6
    from logutils.dictconfig import dictConfig
except ImportError:
    from logging.config import dictConfig

# logging.NullHandler New in python 2.7
try:
    # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
    # logging.getLogger(__name__).addHandler(NullHandler())
    # use namespace
    logging.NullHandler = NullHandler

import os.path


def init_logging(log_dir):
    """
    initial logging
    """
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(filename)s:%(lineno)d(%(module)s:%(funcName)s) - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'simple': {
                'format': '%(asctime)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
        },
        'filters': {
        },
        'handlers': {
            'null': {
                'level': 'DEBUG',
                'class': 'logging.NullHandler',
            },
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'standard',
                'stream': 'ext://sys.stderr',
            },
            'syslog': {
                'level': 'DEBUG',
                'class': 'logging.handlers.SysLogHandler',
                'facility': 'logging.handlers.SysLogHandler.LOG_LOCAL7',
                'formatter': 'standard',
            },
            'syslog2': {
                'level': 'DEBUG',
                'class': 'logging.handlers.SysLogHandler',
                'facility': 'logging.handlers.SysLogHandler.LOG_LOCAL7',
                'formatter': 'standard',
            },
            'access': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename':  os.path.join(log_dir, 'access.log'),
                'maxBytes': 1024*1024*2,
                'backupCount': 5,
                'formatter': 'standard',
            },
            'application': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename':  os.path.join(log_dir, 'app.log'),
                'maxBytes': 1024*1024*2,
                'backupCount': 5,
                'formatter': 'standard',
            },
        },
        'loggers': {
            'werkzeug': {
                'handlers': ['access', 'console'],
                'level': 'DEBUG',
                'propagate': False,
            },
            'myapp': {
                'handlers': ['application'],
                'level': 'DEBUG',
                'propagate': True,
            },
        },
    }

    dictConfig(LOGGING)










