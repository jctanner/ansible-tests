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


# MAKE SURE hacking/env-setup IS SOURCED BEFORE RUNNING TESTS
def test_ansible_playbook_in_path():
    path = None
    try:
        path = subprocess.check_output(shlex.split('which ansible-playbook'))
    except:
        pass

    assert path is not None

# MAKE SURE ANSIBLE_SSH_USER OVERRIDES ALL OTHER remote_user DEFS
def test_inventory_ssh_user():
    output = None
    cmdargs = "ansible-playbook -c ssh -vvvv -i inventory_with_ssh_user site.yml"
    cmdargs = shlex.split(cmdargs)
    try:
        output = subprocess.check_output(cmdargs)
    except:
        pass

    remote_users = []
    lines = output.split("\n")
    for line in lines:
        if "ESTABLISH CONNECTION FOR USER" in line:
            username = shlex.split(line)[-1]
            remote_users.append(username)

    #f = open("/tmp/test.out", "a"); f.write(output) ; f.close()
    #f = open("/tmp/test.out", "a"); f.write(str(remote_users)) ; f.close()

    assert 'invuser' in remote_users
    assert len([x for x in remote_users if x != "invuser"]) == 0

# MAKE SURE remote_user PREFERENCE IS: TASK > PLAY > PLAYBOOK
def test_playbook_remote_user():
    output = None
    cmdargs = "ansible-playbook -c ssh -vvvv -i inventory site.yml"
    cmdargs = shlex.split(cmdargs)
    try:
        output = subprocess.check_output(cmdargs)
    except:
        pass

    remote_users = []
    lines = output.split("\n")
    for line in lines:
        if "ESTABLISH CONNECTION FOR USER" in line:
            username = shlex.split(line)[-1]
            remote_users.append(username)

    assert 'invuser' not in remote_users
    assert remote_users == ['playuser', 'taskuser', 'playuser']


# LOCAL CONNECTIONS SHOULD NOT HAVE A REMOTE USER
def test_playbook_local_play():
    output = None
    cmdargs = "ansible-playbook -c ssh -vvvv -i inventory site-local-play.yml"
    cmdargs = shlex.split(cmdargs)
    try:
        output = subprocess.check_output(cmdargs)
    except:
        pass

    remote_users = []
    lines = output.split("\n")
    for line in lines:
        if "ESTABLISH CONNECTION FOR USER" in line:
            username = shlex.split(line)[-1]
            remote_users.append(username)

    assert len(remote_users) == 0


# LOCAL TASKS SHOULD NOT HAVE A REMOTE USER
def test_playbook_local_task():
    output = None
    cmdargs = "ansible-playbook -c ssh -vvvv -i inventory site-local-task.yml"
    cmdargs = shlex.split(cmdargs)
    try:
        output = subprocess.check_output(cmdargs)
    except:
        pass

    remote_users = []
    lines = output.split("\n")
    for line in lines:
        if "ESTABLISH CONNECTION FOR USER" in line:
            username = shlex.split(line)[-1]
            remote_users.append(username)

    assert remote_users == ['taskuser', 'playuser']


# TASK remote_user SHOULD OVERRIDE -u ARG
def test_playbook_cli_userarg():
    output = None
    cmdargs = "ansible-playbook -c ssh -vvvv -i inventory site-no_users.yml -u cliuser"
    cmdargs = shlex.split(cmdargs)
    try:
        output = subprocess.check_output(cmdargs)
    except:
        pass

    remote_users = []
    lines = output.split("\n")
    for line in lines:
        if "ESTABLISH CONNECTION FOR USER" in line:
            username = shlex.split(line)[-1]
            remote_users.append(username)

    assert remote_users == ['cliuser', 'taskuser', 'cliuser']


# PLAYBOOK AND TASK remote_user SHOULD OVERRIDE -u ARG
def test_cli_userarg_vs_playbook_user():
    output = None
    cmdargs = "ansible-playbook -c ssh -vvvv -i inventory site.yml -u cliuser"
    cmdargs = shlex.split(cmdargs)
    try:
        output = subprocess.check_output(cmdargs)
    except:
        pass

    remote_users = []
    lines = output.split("\n")
    for line in lines:
        if "ESTABLISH CONNECTION FOR USER" in line:
            username = shlex.split(line)[-1]
            remote_users.append(username)

    assert remote_users == ['playuser', 'taskuser', 'playuser']


# PLAYBOOK AND TASK remote_user SHOULD OVERRIDE -u ARG
def test_cli_userarg_vs_role_task_user():
    output = None
    cmdargs = "ansible-playbook -c ssh -vvvv -i inventory site-roles.yml -u cliuser"
    cmdargs = shlex.split(cmdargs)
    try:
        output = subprocess.check_output(cmdargs)
    except:
        pass

    remote_users = []
    lines = output.split("\n")
    for line in lines:
        if "ESTABLISH CONNECTION FOR USER" in line:
            username = shlex.split(line)[-1]
            remote_users.append(username)

    assert remote_users == ['roletaskuser', 'cliuser', 'cliuser', 'roletaskuser']


