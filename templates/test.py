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

# MAKE A SIMPLE TEMPLATE foo == bar
def test_basic_file_template():

    # ok: [localhost] => {"changed": false, "gid": 1000, "group": "jtanner", 
    #   "mode": "0600", "owner": "jtanner", "path": "/tmp/foo_only.txt", 
    #   "size": 4, "state": "file", "uid": 1000}

    outpath = "/tmp/foo_only.txt"
    if os.path.exists(outpath):
        os.remove(outpath)

    output = None
    cmdargs = "ansible-playbook -vvv -i inventory -t foo_only site.yml"
    cmdargs = shlex.split(cmdargs)
    try:
        output = subprocess.check_output(cmdargs)
    except:
        pass

    assert output is not None, "Null output from ansible-playbook"
    assert os.path.exists(outpath), "%s was not created" % outpath
    contents = open(outpath).read().strip()
    assert contents == "bar", "%s != bar" % contents
    os.remove(outpath)

# MAKE A SIMPLE TEMPLATE WITH UPPER FILTER foo == BAR
def test_basic_file_template_with_filter():

    outpath = "/tmp/foo_plus_filter.txt"
    if os.path.exists(outpath):
        os.remove(outpath)

    output = None
    cmdargs = "ansible-playbook -vvv -i inventory -t foo_plus_filter site.yml"
    cmdargs = shlex.split(cmdargs)
    try:
        output = subprocess.check_output(cmdargs)
    except:
        pass

    assert output is not None, "Null output from ansible-playbook"
    assert os.path.exists(outpath), "%s was not created" % outpath
    contents = open(outpath).read().strip()
    assert contents == "BAR", "%s != BAR " % (contents)
    os.remove(outpath)


#ansible-playbook -i inventory -t yaml_list lists.yml 
#ansible-playbook -i inventory -t jinja_list lists.yml 

# YAML LIST FROM ... alist: ['abc', 'def']
def test_yaml_list_var():

    outpath = "/tmp/test_list.txt"
    if os.path.exists(outpath):
        os.remove(outpath)

    output = None
    cmdargs = "ansible-playbook -vvv -i inventory -t yaml_list lists.yml"
    cmdargs = shlex.split(cmdargs)
    try:
        output = subprocess.check_output(cmdargs)
    except:
        pass

    assert output is not None, "Null output from ansible-playbook"
    assert os.path.exists(outpath), "%s was not created" % outpath
    contents = open(outpath).read().strip()
    assert contents == "abc", "%s != abc" % (contents)
    os.remove(outpath)


# JINJA LIST FROM ... blist: "{{ alist }}"
def test_jinja_list_var():

    outpath = "/tmp/test_list.txt"
    if os.path.exists(outpath):
        os.remove(outpath)

    output = None
    cmdargs = "ansible-playbook -vvv -i inventory -t jinja_list lists.yml"
    cmdargs = shlex.split(cmdargs)
    try:
        output = subprocess.check_output(cmdargs)
    except:
        pass

    assert output is not None, "Null output from ansible-playbook"
    assert os.path.exists(outpath), "%s was not created" % outpath
    contents = open(outpath).read().strip()
    assert contents == "abc", "%s != abc" % (contents)
    os.remove(outpath)


