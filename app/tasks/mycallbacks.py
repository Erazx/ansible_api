#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division
from ansible import callbacks
from datetime import datetime
from redis import Redis
import logging
from copy import deepcopy
from flask import current_app
__metaclass__ = type

try:
    import simplejson as json
except ImportError:
    import json

logger = logging.getLogger('myapp')


def log_redis(content):
    r = Redis(host=current_app.config['ELK_REDIS_BROKER_HOST'], port=current_app.config['ELK_REDIS_BROKER_PORT'])
    msg = {
        "timestamp": datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"),
        "server_addr": current_app.config['ANSIBLE_CONTROL_HOST'],
        "type": current_app.config['ELK_MESSAGE_TYPE'],
        "level": 4,
        "celery_task_id": content.pop('celery_task_id'),
    }
    for host, value in content.iteritems():
        tmp = deepcopy(msg)
        tmp['server_name'] = host
        tmp.update(value)
        try:
            r.rpush(current_app.config['ELK_LOGSTASH_KEY'], json.dumps(tmp))
        except Exception as e:
            logger.error('Log Redis Failed: %s' % e.message)
            logger.error('Data: %s' % json.dumps(tmp))
        finally:
            tmp = {}


class MyAggregateStats(callbacks.AggregateStats):
    """
    Holds stats about per-host activity during playbook runs.
    """
    def __init__(self):
        super(MyAggregateStats, self).__init__()
        self.result = {}

    def _increment(self, what, host, value=None):
        self.processed[host] = 1
        if what == 'result':
            prev = (getattr(self, what)).get(host, [])
            prev.append(value)
            getattr(self, what)[host] = prev
        else:
            prev = (getattr(self, what)).get(host, 0)
            getattr(self, what)[host] = prev+1

    def compute(self, runner_results, setup=False, poll=False, ignore_errors=False):
        """
        Walk through all results and increment stats.
        """
        super(MyAggregateStats, self).compute(runner_results, setup, poll, ignore_errors)

        for (host, value) in runner_results.get('contacted', {}).iteritems():
            if value.get('invocation', {}).get('module_name', '') != 'setup':
                self._increment('result', host, value)
        for (host, value) in runner_results.get('dark', {}).iteritems():
            value['outcome'] = 'dark'
            self._increment('result', host, value)

    def summarize(self, host):
        """
        Return information about a particular host
        """
        summarized_info = super(MyAggregateStats, self).summarize(host)

        # Adding the info I need
        summarized_info['result'] = self.result.get(host, {})

        return summarized_info
