#!/usr/bin/env python
#file evo/models/util.py

"""Provides utility methods for randomization.

Owner: Rob Knight rob@spot.colorado.edu

Status: Development

Revision History

11/28/03 Rob Knight: Created for PyEvolve, adapted from script to randomize
peptide database.

12/28/03 Rob Knight: Changed package and imports.
"""
from random import shuffle
from old_cogent.util.misc import find_many

def shuffle_range(items, start, end):
    """Randomizes region of items between start and end indices, in-place.
    
    Shuffle affects items[start] but not items[end], as ususal for
    slice operations.

    Items slices must be assignable.
    
    No return value, as per standard for in-place operations.
    """
    length = len(items)
    #handle negative indices
    if start < 0:
        start = length - start
    if end < 0:
        end = length - end
    #skip if 0 or 1 items
    if end - start > 1: #shuffle has no effect on 0 or 1 item
        curr = items[start:end]
        shuffle(curr)
        items[start:end] = curr[:]

def shuffle_between(items, constructor=None):
    """Returns function that shuffles a sequence between specified items.

    If constructor is not passed, uses ''.join() for subclasses of strings,
    and seq.__class__ for everything else.

    Note that each interval between items is shuffled independently: use
    shuffle_except to keep a particular item in place while shuffling
    everything else.

    The resulting function takes only the sequence as an argument, so can be 
    passed e.g. to map().
    """
    c = constructor
    def result(seq):
        """Returns copy of seq shuffled between specified items."""
        #figure out the appropriate constructor, if not supplied
        if c is None:
            if isinstance(seq, str):
                constructor = lambda x: seq.__class__(''.join(x))
            else:
                constructor = seq.__class__
        else:
            constructor = c
        #figure out where to cut the sequence
        cut_sites = find_many(seq, items)
        #want to shuffle sequence before first and after last match as well
        if (not cut_sites) or cut_sites[0] != 0:
            cut_sites.insert(0, 0)
        seq_length = len(seq)
        if cut_sites[-1] != seq_length:
            cut_sites.append(seq_length)
        #shuffle each pair of (i, i+1) matches, excluding position of match
        curr_seq = list(seq)
        for start, end in zip(cut_sites, cut_sites[1:]):
            shuffle_range(curr_seq, start+1, end) #remember to exclude start
        #return the shuffled copy
        return constructor(curr_seq)
    #return the resulting function
    return result

#example of shuffle_between
shuffle_peptides = shuffle_between('KR', ''.join)

def shuffle_except_indices(items, indices):
    """Shuffles all items in list in place, except at specified indices.
    
    items must be slice-assignable.
    WARNING: Uses quadratic algorithm. Don't use for long lists!
    """
    length = len(items)
    if not length:
        return []
    orig = items[:]
    sorted_indices = indices[:]
    #make indices positive
    for i, s in enumerate(sorted_indices):
        if s < 0:
            sorted_indices[i] = length + s 
    sorted_indices.sort()
    sorted_indices.reverse()
    last = None
    for i in sorted_indices:
        if i != last:   #skip repeated indices in list
            del items[i]
        last = i
    shuffle(items)
    sorted_indices.reverse()
    last = None
    for i in sorted_indices:
        if i != last:
            items.insert(i, orig[i])
        last = i



def shuffle_except_indices_linear(items, indices):
    """Shuffles all items in list in place, except at specified indices.
    
    items must be slice-assignable.
    Uses linear algorithm, so suitable for long lists.
    """
    length = len(items)
    if not length:
        return []
    orig = items[:]
    sorted_indices = indices[:]
    #make indices positive
    for i, s in enumerate(sorted_indices):
        if s < 0:
            sorted_indices[i] = length + s 
    sorted_indices.sort()
    sorted_indices.reverse()
    last = None
    for i in sorted_indices:
        if i != last:   #skip repeated indices in list
            del items[i]
        last = i
    shuffle(items)
    sorted_indices.reverse()
    last = None
    for i in sorted_indices:
        if i != last:
            items.insert(i, orig[i])
        last = i
     

def shuffle_except(items, constructor=None):
    """Returns function that shuffles a sequence except specified items.

    If constructor is not passed, uses ''.join() for subclasses of strings,
    and seq.__class__ for everything else.

    Note that each interval between items is shuffled independently: use
    shuffle_except to keep a particular item in place while shuffling
    everything else.

    The resulting function takes only the sequence as an argument, so can be 
    passed e.g. to map().
    """
    c = constructor
    def result(seq):
        """Returns copy of seq shuffled between specified items."""
        #figure out the appropriate constructor, if not supplied
        if c is None:
            if isinstance(seq, str):
                constructor = lambda x: seq.__class__(''.join(x))
            else:
                constructor = seq.__class__
        else:
            constructor = c
        #figure out where to cut the sequence
        cut_sites = find_many(seq, items)
        #want to shuffle sequence before first and after last match as well
        if (not cut_sites) or cut_sites[0] != 0:
            cut_sites.insert(0, 0)
        seq_length = len(seq)
        if cut_sites[-1] != seq_length:
            cut_sites.append(seq_length)
        #shuffle each pair of (i, i+1) matches, excluding position of match
        curr_seq = list(seq)
        for start, end in zip(cut_sites, cut_sites[1:]):
            shuffle_range(curr_seq, start+1, end) #remember to exclude start
        #return the shuffled copy
        return constructor(curr_seq)
    #return the resulting function
    return result

#example of shuffle_between
shuffle_peptides = shuffle_between('KR', ''.join)
