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
def test_lineinfile_multimatching():

    fh, outpath = tempfile.mkstemp()
    if os.path.exists(outpath):
        os.remove(outpath)

    output = None
    cmdargs = "ansible-playbook -v -i inventory -e 'tempfile=%s' multiline.yml" % outpath
    cmdargs = shlex.split(cmdargs)
    try:
        output = subprocess.check_output(cmdargs)
    except:
        pass

    assert output is not None, "Null output from: %s" % cmdargs
    assert os.path.exists(outpath), "%s was not created" % outpath
    contents = open(outpath).read().strip()
    assert contents == "b\nb\nb\nb\nb", "%s != 'b\nb\nb\nb\nb'" % contents
    os.remove(outpath)

