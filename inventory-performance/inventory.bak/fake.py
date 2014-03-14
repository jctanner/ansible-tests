#!/usr/bin/python

import os
import sys
import string
import epdb
import json
import cPickle

extra_data = " ansible_ssh_user=root ansible_ssh_host=192.168.1.148"

check_host = None
if len(sys.argv) > 1:
    if sys.argv[1] == "--host":
        check_host = sys.argv[2]

def load():
    f = open("/tmp/inventory", "rb")
    inventory = cPickle.load(f)    
    f.close()
    return inventory

def write(inventory):
    f = open("/tmp/inventory", "wb")
    cPickle.dump(inventory, f)    
    f.close()

def build():
    inventory = {}
    inventory['all'] = {}
    inventory['all']['hosts'] = []
    inventory['all']['vars'] = {}
    inventory['all']['vars']['ansible_ssh_user'] = "root"
    inventory['all']['vars']['ansible_ssh_host'] = "192.168.1.148"

    inventory['_meta'] = {}
    inventory['_meta']['hostvars'] = {}


    # make a bunch of groups
    for x in range(0, 100):
        this_group = "g" + str(x)
        inventory[this_group] = {}
        inventory[this_group]['hosts'] = []
        inventory[this_group]['vars'] = {}

        # make a bunch of hosts
        for z in range(0, 10):
            this_host = "h" + str(x) + str(z)
            inventory[this_group]['hosts'].append(this_host)       
            inventory['all']['hosts'].append(this_host)       
            inventory['_meta']['hostvars'][this_host] = {}

            # make a bunch of vars
            for y in range(0, 10):
                this_var = "v" + str(y)
                inventory['all']['vars'][this_var] = this_var + "-value"
                inventory['_meta']['hostvars'][this_host][this_var] = this_var + "-value"
                inventory[this_group]['vars'][this_host + this_var] = this_host + this_var + "-value"

    return inventory

if os.path.isfile("/tmp/inventory"):
    inventory = load()
else:
    inventory = build()
    write(inventory)

if check_host is None:
    print json.dumps(inventory)
else:
    print json.dumps(inventory['_meta']['hostvars'][check_host])

