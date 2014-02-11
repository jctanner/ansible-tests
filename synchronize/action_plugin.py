#!/usr/bin/env python

from ansible.runner.action_plugins.synchronize import ActionModule as Synchronize

class FakeRunner(object):
    def __init__(self):
        self.connection = None
        self.transport = None
        self.basedir = None
        self.sudo = None
        self.remote_user = None
        self.private_key_file = None

    def _execute_module(self, conn, tmp, module_name, args, inject=None):
        self.executed_conn = conn
        self.executed_tmp = tmp
        self.executed_module_name = module_name
        self.executed_args = args
        self.executed_inject = inject

class FakeConn(object):
    def __init__(self):
        self.host = None
        self.delegate = None

"""
class FakeInject(object):
    def __init__(self):
        self.x = None
"""

############################################
#   Basic Test
############################################

runner = FakeRunner()
conn = FakeConn()
inject = {
            'inventory_hostname': "localhost",
            'delegate_to': None,
         }

# def setup(self, module_name, inject)
# def run(self, conn, tmp, module_name, module_args, inject, complex_args=None, **kwargs):
#   return self.runner._execute_module(conn, tmp, 'synchronize', module_items, inject=inject)
x = Synchronize(runner)
x.setup("synchronize", inject)
x.run(conn, "/tmp", "synchronize", "src=/tmp/foo dest=/tmp/bar", inject)

print "#======================================#"
print "conn:",runner.executed_conn
print "tmp:",runner.executed_tmp
print "module_name:",runner.executed_module_name
print "args:",runner.executed_args
print "inject:",runner.executed_inject


############################################
#   Simple Remote Host
############################################

"""
#BEFORE
runner.remote_user: jtanner
runner.transport: ssh
inject['ansible_connection']: None
inject['ansible_ssh_user']: root
inject['delegate_to']: None

# AFTER
options['dest_port']: None
inject['ansible_connection']: local
inject['ansible_ssh_port']: None
inject['ansible_ssh_user']: jtanner
inject['delegate_to']: 127.0.0.1
module_items: dest=jtanner@el6.lab.net:/tmp/foobar src=/tmp/foobaz
"""

runner = FakeRunner()
runner.remote_user = "root"
runner.transport = "ssh"
conn = FakeConn()
inject = {
            'inventory_hostname': "el6.lab.net",
            'inventory_hostname_short': "el6",
            'ansible_connection': None,
            'ansible_ssh_user': 'root',
            'delegate_to': None,
            'playbook_dir': '.',
         }

x = Synchronize(runner)
x.setup("synchronize", inject)
x.run(conn, "/tmp", "synchronize", "src=/tmp/foo dest=/tmp/bar", inject)

print "#============ BASIC ============#"
print "module_name:",runner.executed_module_name
print "args:",runner.executed_args
print "inject:",runner.executed_inject

assert runner.executed_inject['delegate_to'] == "127.0.0.1", "was not delegated to 127.0.0.1"
assert runner.executed_args == "dest=root@el6.lab.net:/tmp/bar src=/tmp/foo", "wrong args used"
assert runner.sudo == False, "sudo not set to false"

############################################
#   Simple Vagrant Host
############################################

runner = FakeRunner()
runner.remote_user = "jtanner"
runner.transport = "ssh"
conn = FakeConn()
conn.host = "127.0.0.1"
conn.delegate = "thishost"
inject = {
            'inventory_hostname': "thishost",
            'ansible_ssh_user': 'vagrant',
            'ansible_ssh_host': '127.0.0.1',
            'ansible_ssh_port': '2222',
            'delegate_to': None,
            'playbook_dir': '.',
            'hostvars': {
                'thishost': {
                    'inventory_hostname': 'thishost',
                    'ansible_ssh_port': '2222',
                    'ansible_ssh_host': '127.0.0.1',
                    'ansible_ssh_user': 'vagrant'
                }
            }
         }

x = Synchronize(runner)
x.setup("synchronize", inject)
x.run(conn, "/tmp", "synchronize", "src=/tmp/foo dest=/tmp/bar", inject)

print "#=========== VAGRANT ===========#"
print "module_name:",runner.executed_module_name
print "args:",runner.executed_args
print "inject:",runner.executed_inject

#import epdb; epdb.st()
assert runner.transport == "ssh", "runner transport was changed"
assert runner.remote_user == "jtanner", "runner remote_user was changed"
assert runner.executed_inject['delegate_to'] == "127.0.0.1", "was not delegated to 127.0.0.1"
assert runner.executed_inject['ansible_ssh_user'] == "vagrant", "runner user was changed"
assert "dest_port=2222" in runner.executed_args, "remote port was not set to 2222"
assert "src=/tmp/foo" in runner.executed_args, "source was set incorrectly"
assert "dest=vagrant@127.0.0.1:/tmp/bar" in runner.executed_args, "dest was set incorrectly"

"""
######### START
inject['ansible_connection']: MISSING
runner.transport: ssh
######### RUN
before loop
127.0.0.1 is 127.0.0.1: True
original_transport: ssh
conn.delegate: thishost
delegate vars: {'inventory_hostname': 'thishost', 'inventory_hostname_short': 'thishost', 'who': {u'changed': True, u'end': u'2014-02-10 17:54:07.931071', u'stdout': u'vagrant', u'cmd': u'whoami ', u'rc': 0, u'start': u'2014-02-10 17:54:07.928069', u'stderr': u'', u'delta': u'0:00:00.003002', 'invocation': {'module_name': 'shell', 'module_args': 'whoami'}, 'stdout_lines': [u'vagrant']}, 'ansible_ssh_host': '127.0.0.1', 'ansible_ssh_user': 'vagrant', 'group_names': ['ungrouped'], 'ansible_ssh_port': 2222}
in loop
inject_user: root
runner_user: jtanner
this_user: vagrant
"""
