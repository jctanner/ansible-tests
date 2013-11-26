#!/usr/bin/python

import os
import sys
import tempfile
import string
import random


rrange = 1000   # number of hosts/groups
rlen = 10       # host/group name length
chars = string.ascii_letters.lower()

hfh, hpath = tempfile.mkstemp()
gfh, gpath = tempfile.mkstemp()
hf = open(hpath, "a")
gf = open(gpath, "a")
open("/tmp/awx.log", "a").write("%s\n" % hpath)
open("/tmp/awx.log", "a").write("%s\n" % gpath)

hf.write("hostnames:\n")
gf.write("groupnames:\n")

for i in range(0, rrange):
    h = "".join([random.choice(chars).lower() for n in xrange(rlen)])
    g = "".join([random.choice(chars).lower() for n in xrange(rlen)])
    hf.write("  - %s\n" % h)
    gf.write("  - %s\n" % g)
hf.close()
gf.close()

print "hosts: %s" % hpath
print "groups: %s" % gpath

