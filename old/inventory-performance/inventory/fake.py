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

def load(filename):
    f = open(filename, "rb")
    inventory = cPickle.load(f)    
    f.close()
    return inventory

def write(inventory, filename):
    f = open(filename, "wb")
    cPickle.dump(inventory, f)    
    f.close()

def build(gc, hc, vc):
    inventory = {}
    inventory['all'] = {}
    inventory['all']['hosts'] = []
    inventory['all']['vars'] = {}
    #inventory['all']['vars']['ansible_ssh_user'] = "root"
    #inventory['all']['vars']['ansible_ssh_host'] = "192.168.1.148"

    inventory['_meta'] = {}
    inventory['_meta']['hostvars'] = {}



    # make a bunch of groups
    for x in range(0, gc):
        this_group = "g" + str(x)
        inventory[this_group] = {}
        inventory[this_group]['hosts'] = []
        inventory[this_group]['vars'] = {}

    # make a bunch of hosts
    for z in range(0, hc):
        this_host = "h" + str(x) + str(z)
        #inventory[this_group]['hosts'].append(this_host)       
        inventory['all']['hosts'].append(this_host)       
        inventory['_meta']['hostvars'][this_host] = {}

        # add host to two random groups
        if ( "g" + str(z) ) in inventory:
            inventory["g" + str(z)]['hosts'].append(this_host)
        if ( "g" + str(z + 1) ) in inventory:
            inventory["g" + str(z + 1)]['hosts'].append(this_host)

    # make a bunch of vars for each host
    for y in range(0, vc):
        if len(inventory['all']['vars'].keys()) < (vc + 1):
            this_var = "v" + str(y)
            inventory['all']['vars'][this_var] = this_var + "-value"
            #inventory['_meta']['hostvars'][this_host][this_var] = this_var + "-value"
            #inventory[this_group]['vars'][this_host + this_var] = this_host + this_var + "-value"

    return inventory

def profile(inventory):
    hosts = 0
    groups = 0
    vars_ = 0
    
    hosts += len(inventory['all']['hosts'])

    vars_ += len(inventory['all']['vars'].keys())

    groupnames = [ x for x in inventory.keys() if x not in ['all', '_meta'] ]
    groups += len(groupnames)

    for g in groupnames:
        vars_ += len(inventory[g]['vars'].keys())

    f = open("/tmp/awx.log", "a").write("###########\n")        
    f = open("/tmp/awx.log", "a").write("groups: %s\n" % groups)        
    f = open("/tmp/awx.log", "a").write("hosts: %s\n" % hosts)        
    f = open("/tmp/awx.log", "a").write("vars: %s\n" % vars_)        

groupcount = int(os.environ.get('ANSIBLE_INVENTORY_GROUP_COUNT', 1))
hostcount = int(os.environ.get('ANSIBLE_INVENTORY_HOST_COUNT', 1))
varcount = int(os.environ.get('ANSIBLE_INVENTORY_VAR_COUNT', 1))

filename = "inventory-" + str(groupcount) + "-" + str(hostcount) + "-" + str(varcount)
filename = os.path.join("/tmp", filename)

if os.path.isfile(filename):
    inventory = load(filename)
else:
    inventory = build(groupcount, hostcount, varcount)
    write(inventory, filename)

profile(inventory)

if check_host is None:
    print json.dumps(inventory)
else:
    print json.dumps(inventory['_meta']['hostvars'][check_host])

