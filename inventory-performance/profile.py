#!/usr/bin/env python

import os
import shlex
import time
import subprocess
import itertools

"""
groupcount = int(os.environ.get('ANSIBLE_INVENTORY_GROUP_COUNT', 1))
hostcount = int(os.environ.get('ANSIBLE_INVENTORY_HOST_COUNT', 1))
varcount = int(os.environ.get('ANSIBLE_INVENTORY_VAR_COUNT', 1))
"""

def profile_playbook(playbook_file, environment=None):
    this_cmd = 'python -m cProfile $(which ansible-playbook) -i inventory %s' % (playbook_file)
    elapsed_time, rc, stdout, stderr = _run(this_cmd, environment=environment)
    return (elapsed_time, rc, stdout, stderr)

def cache_inventory(script_path, environment=None):
    this_cmd = "python %s" % script_path
    elapsed_time, rc, stdout, stderr = _run(this_cmd, environment=environment)
    return (elapsed_time, rc, stdout, stderr)


def _run(this_cmd, environment=None):
    kwargs = dict(
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if environment:
        kwargs['env'] = environment

    start_time = time.time()
    p = subprocess.Popen(this_cmd, **kwargs)
    stdout, stderr = p.communicate()
    elapsed_time = time.time() - start_time
    rc = p.returncode
    return (elapsed_time, rc, stdout, stderr)

def get_test_params(limit=100):
    plist = []
    plist = sorted( [x for x in itertools.permutations(range(1, limit, 5), 2) ] )
    return plist

def parse_cprofile_stdout(data):

    result = {}
    lines = data.split('\n')

    # find the line cprofile starts on
    startline = None
    for idx, val in enumerate(lines):
        if 'ncalls  tottime  percall  cumtime  percall' in val:
            startline = idx + 1

    if not startline:
        return None    

    cplines = lines[startline:]        
    for cl in cplines:
        parts = shlex.split(cl)
        if len(parts) == 6:
            result[str(parts[5])] = dict(ncalls=parts[0],
                                        tottime=parts[1],
                                        percall=parts[2],
                                        cumtime=parts[3],
                                        percall2=parts[4])

    return result
    
def main():

    limit = 100

    for x in range(1, limit, 5):
        hosts = x
        for groups, vars_ in get_test_params(limit=limit):

            environment = dict(ANSIBLE_INVENTORY_HOST_COUNT = str(x),
                               ANSIBLE_INVENTORY_GROUP_COUNT = str(groups),
                               ANSIBLE_INVENTORY_VAR_COUNT = str(vars_),
                               PYTHONPATH="/home/jtanner/ansible/lib:",
                               ANSIBLE_LIBRARY="/home/jtanner/ansible/library:/usr/share/ansible/",
                               PATH="/home/jtanner/ansible/bin:/home/jtanner/bin:/home/jtanner/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin")

            # cache the inventory build
            __, __, __, __ = cache_inventory("inventory/fake.py", environment=environment)

            # run the playbook and measure
            elapsed_time, rc, stdout, stderr = profile_playbook("site-one.yml", environment=environment)      

            stats = None
            if rc == 0:
                stats = parse_cprofile_stdout(stdout)

            get_host_count = None
            if stats:
                get_host_count = stats['__init__.py:327(_get_host)']['ncalls']

            #print "%s,%s,%s,%s,%s" % (elapsed_time, hosts, groups, vars_, get_host_count)
            pl = "%s,%s,%s,%s,%s" % (hosts, groups, vars_, get_host_count, elapsed_time)
            open("/tmp/performance.csv", "a").write(pl + "\n")
            print pl
            #import epdb; epdb.st()



if __name__ == "__main__":
    main()    
