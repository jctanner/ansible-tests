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

import string
import random
import time


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


def test_add_host_to_existing_group():

    fh, fpath = tempfile.mkstemp()
    output = None
    cmdargs = "ansible-playbook -vvvv -i inventory existing.yml"
    cmdargs = shlex.split(cmdargs)

    p = subprocess.Popen(cmdargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()

    assert stdout is not None, \
        "no output from ansible-playbook: %s" % stdout + stderr
    results = parse_playbook_output(stdout)

    assert results != {}, "parsing results failed" 
    assert results['failed'] == 0, "results: %s" % results
    os.remove(fpath)

def test_add_host_to_nonexisting_group():

    fh, fpath = tempfile.mkstemp()
    output = None
    cmdargs = "ansible-playbook -vvvv -i inventory nonexisting.yml"
    cmdargs = shlex.split(cmdargs)

    p = subprocess.Popen(cmdargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()

    assert stdout is not None, \
        "no output from ansible-playbook: %s" % stdout + stderr
    results = parse_playbook_output(stdout)

    assert results != {}, "parsing results failed" 
    assert results['failed'] == 0, "results: %s" % results
    os.remove(fpath)

def test_add_hosts_and_groups():

    fh, fpath = tempfile.mkstemp()
    output = None
    cmdargs = "ansible-playbook -vvvv -i inventory multiadd.yml"
    cmdargs = shlex.split(cmdargs)

    try:
        output = subprocess.check_output(cmdargs, stderr=fh)
    except:
        #import epdb; epdb.serve()
        pass

    assert output is not None, "no output from ansible-playbook: %s" % fh.read()
    #assert output is not None, "no output from ansible-playbook: %s" % fpath.read()
    results = parse_playbook_output(output)

    assert results != {}, "parsing results failed" 
    assert results['failed'] == 0, "results: %s" % results
    assert results['unreachable'] == 0, "results: %s" % results
    os.remove(fpath)

def test_add_host_performance():

    fh, fpath = tempfile.mkstemp()
    output = None
    cmdargs = "ansible-playbook -vvvv -i inventory performance.yml"
    cmdargs = shlex.split(cmdargs)

    start_time = time.time()
    try:
        output = subprocess.check_output(cmdargs, stderr=fh)
    except:
        #import epdb; epdb.serve()
        pass
    elapsed_time = time.time() - start_time

    assert output is not None, "no output from ansible-playbook: %s" % fh.read()
    results = parse_playbook_output(output)

    assert results != {}, "parsing results failed" 
    assert results['failed'] == 0, "results: %s" % results
    os.remove(fpath)

    assert elapsed_time < 5, "performance regression: %s > 5.5" % elapsed_time
