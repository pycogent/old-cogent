#!/usr/bin/env python

"""remove_temp.py: deletes temporary files, recursively.

Walks through a specified directory and all its subdirectories, deleting
all files that look like temp files (defined by suffixes).

Written 1/22/04 by Rob Knight

9/24/09 Rob Knight: now deletes .DS_Store files on MacOSX as well.
"""

from os import walk, remove
from os.path import join

start_dir = '.'

bad_names = dict.fromkeys(['.DS_Store'])

bad_ends = dict.fromkeys(['pyc', 'pyo', 'o', 'swp', 'bak', 'class'])

def delete(name):
    print "Removing file %s" % name
    remove(name)

for root, dirs, files in walk(start_dir):
    for name in files:
        if name in bad_names:
            delete(join(root, name))
        elif name.endswith('~'):
            delete(join(root, name))
        else:
            suffix = name.split('.')[-1]
            if suffix in bad_ends:
                delete(join(root, name))
