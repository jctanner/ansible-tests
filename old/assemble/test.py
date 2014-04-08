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

# TEST LOCAL ASSEMBLE
def test_assemble_local():

    # https://github.com/ansible/ansible/pull/5091
    fh, fpath = tempfile.mkstemp()
    output = None
    cmdargs = "ansible-playbook -i inventory site.yml"
    cmdargs = shlex.split(cmdargs)
    p = subprocess.Popen(cmdargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()

    assert stdout is not None, "no output from ansible-playbook: %s" % stderr
    results = parse_playbook_output(stdout)

    assert results != {}, "parsing results failed" 
    assert results['failed'] == 0, "results: %s" % results
