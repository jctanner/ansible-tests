#!/usr/bin/python

"""
import unittest
calhost | success >> {
    "ansible_facts": {
        "ansible_kernel": "3.2.0-29-generic"
    },
    "changed": false
}
"""

import os 
import sys
import subprocess 
import shlex
import tempfile


def parse_playbook_output(rawdata):
    # localhost : ok=3    changed=3    unreachable=0    failed=0
    results = {}
    results['sudocalls'] = 0
    results['msg'] = None

    lines = rawdata.split("\n")
    for line in lines:
        if line.strip().startswith('localhost'):
            parts = shlex.split(line)
            for word in parts:
                if '=' in word:
                    k,v = word.split('=')
                    results[k] = int(v)

        if 'sudo -k && sudo -H -S -p' in line:
            results['sudocalls'] += 1

    return results

def parse_ansible_output(rawdata):
    results = {}
    results['msg'] = None
    lines = rawdata.split("\n")
    for line in lines:
        parts = shlex.split(line)
        if len(parts) > 0:
            #print parts
            if parts[0] == 'msg:':
                results['msg'] = line.split(':', 1)[1].strip().replace('"', '').replace(',', '')
    return results    


# MAKE SURE hacking/env-setup IS SOURCED BEFORE RUNNING TESTS
def test_ansible_playbook_in_path():
    path = None
    try:
        path = subprocess.check_output(shlex.split('which ansible-playbook'))
    except:
        pass

    assert path is not None

# TEST SUDO
def test_checkmode_setup():

    # https://github.com/ansible/ansible/pull/5151
    
    # ansible -i inventory localhost -m setup -C
    # localhost | success >> {
    #         "msg": "cannot yet run check mode against old-style modules", 
    #           "skippped": true
    # }

    cmdargs = "ansible -i inventory localhost -m setup -C"
    cmdargs = shlex.split(cmdargs)

    p = subprocess.Popen(cmdargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()

    assert stdout is not None, "no output from ansible: %s" % stderr
    results = parse_ansible_output(stdout)

    #assert False, "%s" % results
    assert 'msg' in results, "no message: %s" % results
    assert results['msg'] != 'cannot yet run check mode against old-style modules' \
                            "wrong error: %s" % results['msg'] 




