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
def test_ansible_doc_in_path():
    path = None
    try:
        path = subprocess.check_output(shlex.split('which ansible-doc'))
    except:
        pass

    assert path is not None

# CHECK FOR ERRORS OR TRACEBACKS IN LIST OUTPUT
def test_module_doc_list_errors():

    fh, fpath = tempfile.mkstemp()

    output = None
    cmdargs = "ansible-doc -l"
    cmdargs = shlex.split(cmdargs)
    try:
        output = subprocess.check_output(cmdargs, stderr=fh)
    except:
        pass

    assert output is not None

    output = output.strip()
    stderr = open(fpath).read()
    output += stderr
    os.remove(fpath)

    lines = output.split("\n")

    for line in lines:
        assert not line.startswith("Traceback")
        assert not line.startswith("ERROR")

