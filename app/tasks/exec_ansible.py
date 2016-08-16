#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from flask import current_app
from app import celery
# from celery.util.log import get_task_logger
from .ansible_api import AdHoc, MyPlayBook


# @celery.task(name='app.exec_ad_hoc', bind=True)
@celery.task(bind=True)
def exec_ad_hoc(self, data):
    try:
        res = data.pop('resource')
    except KeyError:
        res = None
    r = AdHoc(res)
    return r.run(self.request.id, **data)


# @celery.task(name='app.exec_playbook', bind=True)
@celery.task(bind=True)
def exec_playbook(self, data):
    try:
        res = data.pop('resource')
    except KeyError:
        res = None
    pb = MyPlayBook(res)
    return pb.run(self.request.id, **data)
