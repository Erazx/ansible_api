#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import
from ansible.inventory import Inventory
from ansible.inventory.group import Group
from ansible.inventory.host import Host
from ansible.runner import Runner
from ansible.playbook import PlayBook
from ansible import callbacks, utils
from flask import current_app
from .mycallbacks import MyAggregateStats, log_redis
import os
import ansible.constants as ANS_CONS


# ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# PLAYBOOK_DIR = os.path.join(ROOT_DIR, 'ansible_playbooks')


class ResourceBase(object):
    """
    generate inventory

    :param resource: inventory resource, format:
        {
            "hosts" : {
                "host1": {"port": "22", "username": "test", "password": "xxxx"},
                "host2": {"port": "22", "username": "test", "password": "xxxx"},
            },
            "groups": {
                "group1": {"hosts": ["host1", "host2",...], "vars": {'var1':'xxxx', 'var2':'yyy',...} },
                "group2": {"hosts": ["host1", "host2",...], "child": ["group1"], "vars": {'var1':'xxxx', 'var2':'yyy',...} },
            }
        }
    """
    def __init__(self, resource=None):
        host_list = not resource and ANS_CONS.DEFAULT_HOST_LIST or []
        self.inventory = Inventory(host_list=host_list)
        self.resource = resource
        resource and self.gen_inventory()

    @staticmethod
    def gen_host(host_name=None, host_vars={}):
        """
        Generate ansible Host object
        :param host_name: <string> ansible inventory hostname
        :param host_vars: <dict> host variables
        :return: Host object
        """
        ssh_host = host_vars.get('ip', host_name)
        ssh_port = host_vars.get('port', ANS_CONS.DEFAULT_REMOTE_PORT)
        ssh_user = host_vars.get('username')
        ssh_pass = host_vars.get('password')
        ssh_fkey = host_vars.get('ssh_key')
        # init Host
        host = Host(name=host_name, port=ssh_port)
        host.set_variable('ansible_ssh_host', ssh_host)
        # shortcut variables
        ssh_user and host.set_variable('ansible_ssh_user', ssh_user)
        ssh_pass and host.set_variable('ansible_ssh_pass', ssh_pass)
        ssh_fkey and host.set_variable('ansible_private_key_file', ssh_fkey)
        # extra variables
        for key, value in host_vars.iteritems():
            if key not in ['ip', 'port', 'username', 'password', 'ssh_key']:
                host.set_variable(key, value)
        # return Host object
        return host

    @staticmethod
    def gen_group(group_name=None, group_vars={}):
        """
        Generate ansible Group object
        :param group_name: <string> Group Name
        :param group_vars: <dict> Group Variables
        :return: ansible Group object
        """
        group = Group(name=group_name)
        for key, value in group_vars.iteritems():
            group.set_variable(key, value)
        return group

    def gen_inventory(self):
        """
        :return: None
        """
        # set hosts
        if 'hosts' in self.resource.keys():
            for host, info in self.resource['hosts'].iteritems():
                obj_host = self.gen_host(host, info)
                self.inventory.get_group('all').add_host(obj_host)
        # add group
        if 'groups' in self.resource.keys():
            for group, detail in self.resource['groups'].iteritems():
                obj_group = self.gen_group(group, detail.get('vars', {}))
                for host in detail.get('hosts', []):
                    obj_group.add_host(self.inventory.get_host(host))
                for child in detail.get('child', []):
                    obj_group.add_child_group(self.inventory.get_group(child))
                self.inventory.add_group(obj_group)

    def get_lists(self):
        print("Host: ")
        print("=================")
        for host in self.inventory.list_hosts():
            print(host)
        print("Group: ")
        print("=================")
        for group in self.inventory.list_groups():
            print(group)


class AdHoc(ResourceBase):
    """
    execute ansible ad-hoc mode
    """
    def __init__(self, resource=None):
        super(AdHoc, self).__init__(resource)
        self.result_raw = {}

    def run(self, task, module_args, module_name="shell", timeout=10, forks=10, pattern='*', su_user=None):

        runner = Runner(
            module_name=module_name,
            module_args=module_args,
            inventory=self.inventory,
            pattern=pattern,
            forks=forks,
            timeout=timeout,
            su=su_user and True or False,
            su_user=su_user,
        )
        self.result_raw['celery_task_id'] = task
        tmp = runner.run()

        for (host, value) in tmp.get('contacted', {}).iteritems():
            if value.get('invocation', {}).get('module_name', '') != 'setup':
                if not self.result_raw.get(host):
                    self.result_raw[host] = {}
                self.result_raw[host]['result'] = value
        for (host, value) in tmp.get('dark', {}).iteritems():
            if not self.result_raw.get(host):
                    self.result_raw[host] = {}
            value['outcome'] = 'dark'
            self.result_raw[host]['result'] = value

        log_redis(self.result_raw)
        return self.result_raw


class MyPlayBook(ResourceBase):
    """
    execute ansible playbook
    """
    def __init__(self, resource=None):
        super(MyPlayBook, self).__init__(resource)
        self.result_raw = None

    def run(self, task, playbook, extra_vars=None, check=False):
        stats = MyAggregateStats()
        playbook_callback = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
        runner_callback = callbacks.PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)
        abs_playbook_path = os.path.join(current_app.config['ANSIBLE_PLAYBOOKS_DIR'], playbook)

        pb = PlayBook(
            playbook=abs_playbook_path,
            stats=stats,
            callbacks=playbook_callback,
            runner_callbacks=runner_callback,
            inventory=self.inventory,
            extra_vars=extra_vars,
            check=check,
        )
        self.result_raw = pb.run()
        self.result_raw['celery_task_id'] = task
        log_redis(self.result_raw)
        return self.result_raw

if __name__ == "__main__":
    res = {
            "hosts" : {
                "192.168.1.1": {"port": "22", "username": "root", "password": "xxxx"},
                "192.168.1.2": {"port": "22", "username": "root", "password": "yyyy"},
                "192.168.1.3": {"port": "22", "username": "root", "password": "zzz"},
            },
            "groups": {
                "group1": { "hosts": ["192.168.1.1", "192.168.1.2"], vars: {'var1':'xxxx', 'var2':'yyy'} },
                "group2": { "hosts": ["192.168.1.3"], "child": ["group1"], vars: {'var3':'z', 'var4':'o'} },
            }
        }
    inv = ResourceBase(res)
    inv.get_lists()