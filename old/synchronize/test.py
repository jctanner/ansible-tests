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
    """
    PLAY RECAP ********************************************************************
    ahost                      : ok=11   changed=5    unreachable=0    failed=0
    bhost                      : ok=3    changed=2    unreachable=0    failed=0
    chost                      : ok=3    changed=2    unreachable=0    failed=0
    localhost                  : ok=5    changed=5    unreachable=0    failed=0
    """
    recap_index = None
    results = {}
    lines = rawdata.split("\n")
    #for line in lines:
    for idx, val in enumerate(lines):
        #import epdb; epdb.serve()
        """"
        if line.strip().startswith('localhost'):
            parts = shlex.split(line)
            for word in parts:
                if '=' in word:
                    k,v = word.split('=')
                    results[k] = int(v)
        """
        if val.startswith("PLAY RECAP"):
            recap_index = idx                    
            continue
        if recap_index is not None:
            results[str(idx)] = val
            parts = shlex.split(val)
            #if parts[0] not in results:
            #    results[parts[0]] = val
            for word in parts:
                if '=' in word:
                    k,v = word.split('=')
                    if k not in results:
                        results[k] = int(v)
                    else:
                        results[k] += int(v)

    #print results
    return results


# MAKE SURE hacking/env-setup IS SOURCED BEFORE RUNNING TESTS
def test_ansible_playbook_in_path():
    path = None
    try:
        path = subprocess.check_output(shlex.split('which ansible-playbook'))
    except:
        pass

    assert path is not None

def test_synchronize():

    # https://github.com/ansible/ansible/pull/5091
    fh, fpath = tempfile.mkstemp()
    output = None
    cmdargs = "ansible-playbook -vvvv -i inventory site.yml"
    cmdargs = shlex.split(cmdargs)
    p = subprocess.Popen(cmdargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()

    assert stdout is not None, "no output from ansible-playbook: %s" % stderr
    results = parse_playbook_output(stdout)

    assert results != {}, "parsing results failed" 
    assert results['failed'] == 0, "results: %s \n %s" % (results, stdout)

def test_synchronize_vagrant():

    # https://github.com/ansible/ansible/pull/5091
    fh, fpath = tempfile.mkstemp()
    output = None
    cmdargs = "ansible-playbook -vvvv -i inventory.vagrant site-vagrant.yml"
    cmdargs = shlex.split(cmdargs)
    p = subprocess.Popen(cmdargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()

    assert stdout is not None, "no output from ansible-playbook: %s" % stderr
    results = parse_playbook_output(stdout)

    assert results != {}, "parsing results failed" 
    assert results['failed'] == 0, "results: %s" % results
