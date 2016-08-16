#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from app import create_app
from flask_script import Manager, Shell


app = create_app(os.getenv('FLACK_CONFIG') or 'default')
manager = Manager(app)


if __name__ == '__main__':
    manager.run()
