#!/usr/bin/python

"""
The remote_user for a connection has an order of preference based on various sources ...

inventory ansible_ssh_user > task remote_user > play remote_user > playbook remote_user > cli --user
"""

import unittest
import os 
import sys
import subprocess 
import shlex
import tempfile


# MAKE SURE hacking/env-setup IS SOURCED BEFORE RUNNING TESTS
def test_ansible_playbook_in_path():
    path = None
    try:
        path = subprocess.check_output(shlex.split('which ansible-playbook'))
    except:
        pass

    assert path is not None

# MAKE SURE ANSIBLE_SSH_USER OVERRIDES ALL OTHER remote_user DEFS
"""
def test_inventory_ssh_user():

    #"msg": "/home/jtanner"
    #"msg": "/home/jtanner"
    #"msg": "/home/jtanner/.ssh/"
    #"msg": "19000"

    fh, fpath = tempfile.mkstemp()
    output = None
    cmdargs = "ansible-playbook -c ssh -vvvv -i inventory site.yml"
    cmdargs = shlex.split(cmdargs)
    try:
        output = subprocess.check_output(cmdargs, stderr=fh)
    except:
        pass

    messages = []
    lines = output.split("\n")
    for line in lines:
        if line.strip().startswith('"msg"'):
            data = line.split(':', 1)[1].strip()
            messages.append(data)

    assert len(messages) == 4, "%s" % messages
    assert messages[0] == '"/home/jtanner"', "%s" % messages
    assert messages[1] == '"/home/jtanner"', "%s" % messages
    os.remove(fpath)
"""
