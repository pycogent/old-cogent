#!/usr/bin/env python
"""
Run all tests comment here

NOTE: Need to modify this file so that it redirects the output to a file, then
reads in that file and summarizes the test. Otherwise, individual files that
use os.popen3 won't work, which is the current behavior.

"""
from os import walk, popen3, environ
from os.path import join
import re

good_pattern = re.compile('OK\s*$') 
start_dir = 'old_cogent_tests'
python_name = 'python'

bad_tests = []
filenames = []

for root, dirs, files in walk(start_dir):
    for name in files:
        if name.startswith('test_') and name.endswith('.py'):
            filenames.append(join(root,name))
filenames.sort()

for filename in filenames:
    #old_cogent_tests/app/test_util.py
    if ("old_cogent_tests/app/test_util.py" == filename):
        print 'SKIPPING APP UTIL!!'
        continue
    print "Testing %s:\n" % filename
    result = popen3('%s %s -v' % (python_name, filename))[2].read()
    print result
    if not good_pattern.search(result):
        bad_tests.append(filename)

if bad_tests:
    print "Failed the following tests:\n%s" % '\n'.join(bad_tests)
else:
    print "All tests passed successfully."
