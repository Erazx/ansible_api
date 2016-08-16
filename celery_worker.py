#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from app import celery, create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app.app_context().push()
