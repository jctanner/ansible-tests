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


# basic.yml  mixedvarsescape.yml

# TEST BASIC VARIABLE CREATION
def test_vars_basic():

    fh, fpath = tempfile.mkstemp()
    output = None
    cmdargs = "ansible-playbook -vvvv -i inventory -t basic vartest.yml"
    cmdargs = shlex.split(cmdargs)
    try:
        output = subprocess.check_output(cmdargs, stderr=fh)
    except:
        import epdb; epdb.serve()

    # localhost : ok=3    changed=3    unreachable=0    failed=0
    results = {}
    assert output is not None, "No output from ansible-playbook"
    lines = output.split("\n")
    for line in lines:
        if line.strip().startswith('localhost'):
            parts = shlex.split(line)
            for word in parts:
                if '=' in word:
                    k,v = word.split('=')
                    open("/tmp/awx.log", "a").write("%s\n" % word)
                    results[k] = int(v)

    assert results != {}, "parsing results failed" 
    assert results['failed'] == 0, "results: %s" % results
    os.remove(fpath)
