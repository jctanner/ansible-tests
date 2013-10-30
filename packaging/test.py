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

# MAKE SURE A SINGLE PACKAGE CAN BE INSTALLED
def test_basic_package_install():

    #<el6.lab.net> REMOTE_MODULE yum name=dos2unix state=installed
    #ok: [el6.lab.net] => {"changed": false, "msg": "", "rc": 0, "results": 
    #    ["dos2unix-3.1-37.el6.x86_64 providing dos2unix is already installed"]}

    output = None
    cmdargs = "ansible-playbook -c ssh -vvvv -i inventory -t one yum.yml"
    cmdargs = shlex.split(cmdargs)
    try:
        #output = subprocess.check_output(cmdargs, stderr=fh, stdout=fh2)
        output = subprocess.check_output(cmdargs)
    except:
        pass

    assert output is not None
    #output = output.strip()
    lines = output.split("\n")


    installed = []

    for line in lines:
        # grep out package names sent to the yum command
        if 'REMOTE_MODULE yum' in line:
            words = shlex.split(line)
            for word in words:
                if word.startswith("name="):
                    packages = shlex.split(word, "=")
                    packages = packages[0].replace('name=', '').split(',')
                    for p in packages:
                        installed.append(p)
        # get the result
        if '"results":' in line:
            pass

    assert len(installed) == 1, "%s should have one package" % installed


# MAKE SURE A LIST OF PACKAGES IS SENT TO YUM AND NOT ONE PKG AT A TIME
def test_package_list_install():

    output = None
    cmdargs = "ansible-playbook -c ssh -vvvv -i inventory -t list yum.yml"
    cmdargs = shlex.split(cmdargs)
    try:
        #output = subprocess.check_output(cmdargs, stderr=fh, stdout=fh2)
        output = subprocess.check_output(cmdargs)
    except:
        pass

    assert output is not None
    lines = output.split("\n")

    for line in lines:
        # grep out package names sent to the yum command
        if 'REMOTE_MODULE yum' in line:
            words = shlex.split(line)
            for word in words:
                if word.startswith("name="):
                    packages = shlex.split(word, "=")
                    packages = packages[0].replace('name=', '').split(',')
                    #open("/tmp/awx.log", "a").write("%s\n" % packages)
                    assert len(packages) > 1, "%s should have been more than one package name" % packages


# MAKE SURE ONE PACKAGE IS SENT IF TASK IS CONDITIONAL
def test_conditional_package_list_install():

    output = None
    cmdargs = "ansible-playbook -c ssh -vvvv -i inventory -t conditional_list yum.yml"
    cmdargs = shlex.split(cmdargs)
    try:
        #output = subprocess.check_output(cmdargs, stderr=fh, stdout=fh2)
        output = subprocess.check_output(cmdargs)
    except:
        pass

    assert output is not None
    lines = output.split("\n")

    for line in lines:
        # grep out package names sent to the yum command
        if 'REMOTE_MODULE yum' in line:
            words = shlex.split(line)
            for word in words:
                if word.startswith("name="):
                    packages = shlex.split(word, "=")
                    packages = packages[0].replace('name=', '').split(',')
                    #open("/tmp/awx.log", "a").write("%s\n" % packages)
                    assert len(packages) == 1, "%s should only contain one packagename" % packages
                    assert packages[0] == "strace", "%s should be 'strace'"  % packages
                    assert packages[0] != "dos2unix", "should have skipped dos2unix: %s"  % packages

