#!/usr/bin/env python
#file cogent.format.nexus.py

def to_nexus_blocks(self, alignment=None, trees=None):
    """Writes out a Nexus-format block using the alignment and/or trees.

    No names may be in the trees but not in the alignment.

    If the alignment is supplied, uses the names of the sequences in the
    alignment as a master list. Otherwise, must gather the name from each
    node in each of the trees to make a master list.

    Each name will be assigned a 1-based id, and these ids will be substituted
    throughout the alignment and set of trees.

    Will not modify the input objects in place (will make copies if necessary).

    Returns string containing the nexus blocks for taxa, optionally data,
    optionally trees.
    """
