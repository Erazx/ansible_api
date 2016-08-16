#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import current_app
import hashlib
import socket
import json

# sign_key='secret_sign_key'


def getmd5(str_to_md5):
    """
    md5sum string
    :param str_to_md5: <string>
    :return: <string>
    """
    hash_handler = hashlib.md5()
    hash_handler.update(str_to_md5)
    return hash_handler.hexdigest()


def check_sign(dict_to_check, sign):
    """
    simple method to check sign
    :param dict_to_check: <dict>
    :param sign: <string>
    :return: <bool>
    """
    # global sign_key
    sorted_list = sorted(dict_to_check.iteritems(), key=lambda d: d[0], reverse=True)
    s = ''
    for key, value in sorted_list:
        try:
            s += value
        except TypeError:
            s += json.dumps(value)
    if getmd5(s+current_app.config['API_SIGN_KEY']) == sign:
        return True
    else:
        return False


def is_safe_ip(ip):
    """
    check ip in whitelist or not
    :param ip: <string> ip address
    :return: <bool>
    """
    # should define global
    # white_ip_list = ('127.0.0.1', '192.168.1.1')
    try:
        socket.inet_pton(socket.AF_INET, ip)
    except AttributeError:
        try:
            socket.inet_aton(ip)
        except socket.error:
            return False
    except socket.error:
        return False

    if ip.count('.') == 3 and ip in current_app.config['API_WHITE_IP_LIST']:
        return True
    else:
        return False
