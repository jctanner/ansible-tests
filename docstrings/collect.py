#!/usr/bin/env python

import os
import sys
import subprocess
from ansible import utils
from ansible.utils import module_docs
import cPickle as pickle
from exceptions import Exception

module_list = []
paths = utils.plugins.module_finder._get_paths()
for path in paths:
    if os.path.isdir(path):
        for module in os.listdir(path):
            fullpath = os.path.join(path, module)
            if os.path.isfile(fullpath):
                module_list.append(fullpath)


# Use module_docs lib to get all parameter info
mdict = {}
for module in sorted(module_list):
    doc = None
    plainexamples = None

    mname = os.path.basename(module)
    if mname in module_docs.BLACKLIST_MODULES:
        continue

    try:
        doc, plainexamples = module_docs.get_docstring(module)
    except AssertionError, e:
        pass
    except SyntaxError, e:
        pass
    except Exception, e:
        pass

    if doc:
        module_name = os.path.basename(module)
        mdict[module_name] = {}
        mdict[module_name]['params'] = {}
        mdict[module_name]['version_added'] = doc['version_added']
        mdict[module_name]['module'] = doc['module'] 
        
        for optkey in doc['options'].keys():

            # If not version_added, assume it was added
            # when the module was added
            mdict[module_name]['params'][optkey] = {}
            if not 'version_added' in doc['options'][optkey]:
                mdict[module_name]['params'][optkey]['version_added'] = \
                    doc['version_added']
            else:
                mdict[module_name]['params'][optkey]['version_added'] = \
                    doc['options'][optkey]['version_added']                

        #import epdb; epdb.st()

pickle.dump(mdict, open("/tmp/module-params.pickle", "wb"))

