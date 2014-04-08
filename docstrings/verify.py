#!/usr/bin/env python

# http://stackoverflow.com/questions/1714027/version-number-comparison

import os 
import sys
import ast
import subprocess
import shlex
from distutils.version import LooseVersion
from pkg_resources import parse_version
import cPickle as pickle

docscript = """#!/usr/bin/env python
import os
import sys
from ansible import utils
from ansible.utils import module_docs

module_name = sys.argv[1]
try:
    module_path = utils.plugins.module_finder.find_plugin(module_name)
except:
    print None
    sys.exit(1)

doc = None
try:
    doc, plainexamples = module_docs.get_docstring(module_path)
except AssertionError, e:
    pass
except SyntaxError, e:
    pass
except Exception, e:
    pass


if not doc:
    sys.exit(1)
else:
    print doc
"""

class Checkout(object):
    def __init__(self, repo_url, branch='devel', tmp_path='/tmp'):
        self.repo_url = repo_url
        self.tmp_path = tmp_path
        self.branch = branch

        self.git = subprocess.check_output(['which', 'git'])
        self.git = self.git.strip()

        parts = repo_url.split('/')        
        self.repo_user = parts[-2]
        self.repo_name = parts[-1]
        self.repo_dir = self.repo_user + "_" + self.repo_name + "_" + branch
        self.repo_path = os.path.join(self.tmp_path, self.repo_dir)

    def makecheckout(self):
        if not os.path.isdir(self.repo_path):
            cmd = "git clone %s -b %s %s" % (self.repo_url, self.branch, self.repo_path)
            print "# %s" % cmd
            rc, out, err = run_command(cmd, cwd=self.tmp_path, shell=False)
            if rc != 0:
                import epdb; epdb.st()

    def exec_command(self, cmd):
        this_path = os.path.join(self.tmp_path, self.repo_dir, "hacking") + "/env-setup"
        cmd = "source %s 2>&1 > /dev/null && %s" % (this_path, cmd)
        rc, out, err = run_command(cmd, shell=True, executable="/bin/bash", split=False)
        return rc, out, err

def run_command(cmd, cwd=None, shell=True, executable=None, split=True):

    if type(cmd) is not list and split:
        cmd = shlex.split(cmd)

    if not cwd:
         p = subprocess.Popen(cmd, 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                executable=executable,
                shell=shell)
    else:
         p = subprocess.Popen(cmd, 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd,
                executable=executable,
                shell=shell)

    out, err = p.communicate() 
    return p.returncode, out, err

def get_versions():
    aversions = {}
    cmd = "git branch --all"
    rc, out, err = run_command(cmd, cwd="/home/jtanner/ansible", shell=False)
    if rc != 0:
        print 'ERROR: unable to run git branch --all in /home/jtanner/ansible'
        sys.exit(1)

    for bversion in out.split('\n'):
        bversion = bversion.strip()

        # skip head
        if '->' in bversion:
            continue

        # skip non remotes
        if not bversion.startswith('remotes'):
            continue

        bnormal = bversion.split('/')[-1]

        aversions[bnormal] = bversion

    return aversions

def make_test_plan(aversions, mdict):

    plan = {}

    for mkey in sorted(mdict.keys()):
        for pkey in mdict[mkey]['params'].keys():
            m_name = mdict[mkey]['module']
            p_version = mdict[mkey]['params'][pkey]['version_added']
            p_version = str(p_version)
            m_name = mdict[mkey]['module']

            if p_version not in plan:
                plan[p_version] = {}

            if m_name not in plan[p_version]:
                plan[p_version][m_name] = []
    
            plan[p_version][m_name].append(pkey)

    plan.pop("historical", None)
    return plan                        

def locate_parameter(aversions, module, param):

    found = []

    for akey in aversions.keys():
        """
        if akey == 'devel':
            this_version = "1.6"
        else:
            this_version = akey.replace('release', '')
            this_version = this_version.replace('-', '')
            this_version = str(this_version)
        """

        #import epdb; epdb.st()        
        this_checkout = Checkout("https://github.com/ansible/ansible", branch=akey)
        this_checkout.makecheckout()       

        # verify module_docs works on this version
        cmd = "python /tmp/docscript.py %s" % 'file'
        rc, out, err = this_checkout.exec_command(cmd)
        if rc != 0:
            #print '# %s unable to import module_docs' % akey          
            continue

        # get all docs for this module at this version 
        cmd = "python /tmp/docscript.py %s" % module
        rc, out, err = this_checkout.exec_command(cmd)
        if rc == 0:
            data = ast.literal_eval(out)
        else:
            data = None

        if data:
            if param in data['options']:
                found.append(akey)

    return found

def run_test_plan(plan, aversions, mdict):
    keymap = {}
    results = []
    for akey in aversions.keys():
        if akey == 'devel':
            this_version = "1.6"
        else:
            this_version = akey.replace('release', '')
            this_version = this_version.replace('-', '')
            this_version = str(this_version)

        keymap[this_version] = akey

    for plan_version in sorted(plan.keys()):

        if not plan_version in keymap:
            continue            

        this_branch = aversions[keymap[plan_version]]
        this_branch = this_branch.split('/')[-1]
        print "#",plan_version,":",this_branch
        this_checkout = Checkout("https://github.com/ansible/ansible", branch=this_branch)
        this_checkout.makecheckout()

        # verify module_docs works on this version
        cmd = "python /tmp/docscript.py %s" % 'file'
        rc, out, err = this_checkout.exec_command(cmd)
        if rc != 0:
            print '# %s unable to import module_docs: %s' % (this_branch, out)        
            continue

        #import epdb; epdb.st()
        for mkey in sorted(plan[plan_version].keys()):
            # get all docs for this module at this version 
            cmd = "python /tmp/docscript.py %s" % mdict[mkey]['module']
            rc, out, err = this_checkout.exec_command(cmd)
            if rc == 0:
                data = ast.literal_eval(out)
            else:
                data = None

            if data:
                for pkey in plan[plan_version][mkey]:
                    if pkey in data['options']:
                        print "VERIFIED: %s in %s with %s" % (pkey, mkey, this_branch)
                    else:
                        found = locate_parameter(aversions, mkey, pkey)
                        found = ",".join(sorted(found))
                        print "BAD: %s in %s with %s: found in %s" % \
                                (pkey, mkey, this_branch, found)
                        this_result = "%s;%s;%s;%s" % (mkey, pkey, plan_version, found)
                        results.append(this_result)

    for line in results:
        open("/tmp/results.csv", "a").write("%s\n" % line)

#####################
#       MAIN        #
#####################

if __name__ == "__main__":

    mdict = pickle.load(open("/tmp/module-params.pickle", "rb"))
    # mdict
    #   module_name:
    #       version_added: 1.6
    #       module: the name
    #       params:
    #           one:
    #               key:
    #                   version_added: 1.6

    open("/tmp/docscript.py", "wb").write(docscript)
    aversions = get_versions()
    plan = make_test_plan(aversions, mdict)
    run_test_plan(plan, aversions, mdict)

#import epdb; epdb.st()
