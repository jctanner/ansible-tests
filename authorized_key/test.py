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


def parse_playbook_output(rawdata):
    # localhost : ok=3    changed=3    unreachable=0    failed=0
    results = {}
    lines = rawdata.split("\n")
    for line in lines:
        if line.strip().startswith('localhost'):
            parts = shlex.split(line)
            for word in parts:
                if '=' in word:
                    k,v = word.split('=')
                    results[k] = int(v)

    return results


# MAKE SURE hacking/env-setup IS SOURCED BEFORE RUNNING TESTS
def test_ansible_playbook_in_path():
    path = None
    try:
        path = subprocess.check_output(shlex.split('which ansible-playbook'))
    except:
        pass

    assert path is not None


# TEST BASIC VARIABLE CREATION
def test_simple_authorized_keys():

    fh, fpath = tempfile.mkstemp()
    output = None
    cmdargs = "ansible-playbook -vvvv -i inventory simple.yml"
    cmdargs = shlex.split(cmdargs)
    try:
        output = subprocess.check_output(cmdargs, stderr=fh)
    except:
        #import epdb; epdb.serve()
        pass

    assert output is not None, "no output from ansible-playbook: %s" % fh.read()
    results = parse_playbook_output(output)

    assert results != {}, "parsing results failed" 
    assert results['failed'] == 0, "results: %s" % results
    os.remove(fpath)
