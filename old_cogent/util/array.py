#!/usr/bin/env python
# file util/array.py: small array utility functions

"""Provides small utility functions for Numeric arrays.

Owner: ?

Status: Development

Revision History:
File started by Rob and Jeremy: functions gapped_to_ungapped, 
    ungapped_to_gapped, masked_to_unmasked, unmasked_to_masked, pairs_to_array  
    
9/15/05 Sandra Smit: added ln_2, log2, safe_p_log_p, safe_log, 
    row_uncertainty, column_uncertainty, row_degeneracy, column_degeneracy,
    hamming_distance, norm, euclidean_distance
2/8/06 Sandra Smit: changed safe_log and safe_p_log_p to return floats always.
"""

from Numeric import array, arange, logical_not, cumsum, where, compress, ravel,\
    zeros, put, Float64, Int32, take, sort, searchsorted, log, nonzero, sum,\
    sqrt, clip

def gapped_to_ungapped(orig, gap_state, remove_mask=False):
    """Return array converting gapped to ungapped indices based on gap state.

    Will use == to test whether items equal the gapped state. Assumes character
    arrays.

    If remove_mask is True (default is False), will assign positions that are
    only in the gapped but not the ungapped version to -1 for easy detection.
    """
    return masked_to_unmasked(orig == gap_state, remove_mask)

def ungapped_to_gapped(orig, gap_state):
    """Returns array mapping indices in ungapped sequence to indices in orig.

    See documentation for unmasked_to_masked for more detail.
    """
    return unmasked_to_masked(orig == gap_state)

def masked_to_unmasked(mask, remove_mask=False):
    """Returns array mapping indices in orig to indices in ungapped.

    Specifically, for each position in orig, returns the index of the position
    in the unmasked sequence of the last non-masked character at or before
    that index (i.e. if the index corresponds to a masked position, will return
    the index of the previous non-masked position since the masked positions
    aren't in the unmasked sequence by definition).

    If remove_mask is True (the default is False), sets the masked positions
    to -1 for easy detection.
    """
    result = cumsum(logical_not(mask)) -1
    if remove_mask:
        result = where(mask, -1, result)
    return result

def unmasked_to_masked(mask):
    """Returns array mapping indices in ungapped to indices in original.

    Any position where the mask is True will be omitted from the final result.
    """
    return compress(logical_not(mask), arange(len(mask)))

def pairs_to_array(pairs, num_items=None, transform=None):
    """Returns array with same data as pairs (list of tuples).

    pairs can contain (first, second, weight) or (first, second) tuples.
    If 2 items in the tuple, weight will be assumed to be 1.

    num_items should contain the number of items that the pairs are chosen
    from. If None, will calculate based on the largest item in the actual
    list.

    transform contains a array that maps indices in the pairs coordinates
    to other indices, i.e. transform[old_index] = new_index. It is
    anticipated that transform will be the result of calling ungapped_to_gapped
    on the original, gapped sequence before the sequence is passed into
    something that strips out the gaps (e.g. for motif finding or RNA folding).

    WARNING: all tuples must be the same length! (i.e. if weight is supplied
    for any, it must be supplied for all.

    WARNING: if num_items is actually smaller than the biggest index in the
    list (+ 1, because the indices start with 0), you'll get an exception
    when trying to place the object. Don't do it.
    """
    #handle easy case
    if not pairs:
        return array([])
    data = array(pairs)
    #figure out if we're mapping the indices to gapped coordinates
    if transform:
        #pairs of indices
        idx_pairs = take(transform, data[:,0:2].astype(Int32))    
    else:
        idx_pairs = data[:,0:2].astype(Int32)
    #figure out biggest item if not supplied
    if num_items is None:
        num_items = int(max(ravel(idx_pairs))) + 1
    #make result array
    result = zeros((num_items,num_items), Float64)
    if len(data[0]) == 2:
        values = 1
    else:
        values = data[:,2]
    put(ravel(result), idx_pairs[:,0]*num_items+idx_pairs[:,1], values)
    return result

ln_2 = log(2)

def log2(x):
    """Returns the log (base 2) of x"
    
    WARNING: log2(0) will give -inf on one platform, but it might raise
    an error (Overflow or ZeroDivision on another platform. So don't rely
    on getting -inf in your downstream code.
    """
    return log(x)/ln_2

def safe_p_log_p(a):
    """Returns -(p*log2(p)) for every nonzero p in a.

    a: Numeric array

    WARNING: log2 is only defined on positive numbers, so make sure
    there are no negative numbers in the array.

    Always returns an array with floats in there to avoid unexpected
    results when applying it to an array with just integers.
    """
    c = array(a.copy(),Float64)
    flat = ravel(c)
    nz_i = nonzero(flat)
    nz_e = take(flat,nz_i)
    log_nz = log2(nz_e)
    put(flat,nz_i,nz_e*-log_nz)
    return c

def safe_log(a):
    """Returns the log (base 2) of each nonzero item in a.

    a: Numeric array

    WARNING: log2 is only defined on positive numbers, so make sure
    there are no negative numbers in the array.

    Always returns an array with floats in there to avoid unexpected
    results when applying it to an array with just integers.
    """
    c = array(a.copy(),Float64)
    flat = ravel(c)
    nz_i = nonzero(flat)
    nz_e = take(flat,nz_i)
    log_nz = log2(nz_e)
    put(flat,nz_i,log_nz)
    return c

def row_uncertainty(a):
    """Returns uncertainty (Shannon's entropy) for each row in a IN BITS
    
    a: Numeric array (has to be 2-dimensional!)

    The uncertainty is calculated in BITS not NATS!!!

    Will return 0 for every empty row, but an empty array for every empty column,
    thanks to this sum behavior:
    >>> sum(array([[]]),1)
    array([0])
    >>> sum(array([[]]))
    zeros((0,), 'l')
    """
    try:
        return sum(safe_p_log_p(a),1)
    except ValueError:
        raise ValueError, "Array has to be two-dimensional"

def column_uncertainty(a):
    """Returns uncertainty (Shannon's entropy) for each column in a in BITS

    a: Numeric array (has to be 2-dimensional)

    The uncertainty is calculated in BITS not NATS!!!

    Will return 0 for every empty row, but an empty array for every empty column,
    thanks to this sum behavior:
    >>> sum(array([[]]),1)
    array([0])
    >>> sum(array([[]]))
    zeros((0,), 'l')

    """
    if len(a.shape) < 2:
        raise ValueError, "Array has to be two-dimensional"
    return sum(safe_p_log_p(a))


def row_degeneracy(a,cutoff=.5):
    """Returns the number of characters that's needed to cover >= cutoff

    a: Numeric array
    cutoff: number that should be covered in the array

    Example:
    [   [.1 .3  .4  .2],
        [.5 .3  0   .2],
        [.8 0   .1  .1]]
    if cutoff = .75: row_degeneracy -> [3,2,1]
    if cutoff = .95: row_degeneracy -> [4,3,3]

    WARNING: watch out with floating point numbers. 
    if the cutoff= 0.9 and in the array is also 0.9, it might not be found
    >>> searchsorted(cumsum(array([.6,.3,.1])),.9)
    2
    >>> searchsorted(cumsum(array([.5,.4,.1])),.9)
    1

    If the cutoff value is not found, the result is clipped to the
    number of columns in the array.
    """
    if not a:
        return []
    try:
        b = cumsum(sort(a)[:,::-1],1)
    except IndexError:
        raise ValueError, "Array has to be two dimensional"
    degen = [searchsorted(aln_pos,cutoff) for aln_pos in b]
    #degen contains now the indices at which the cutoff was hit
    #to change to the number of characters, add 1
    return clip(array(degen)+1,0,a.shape[1])


def column_degeneracy(a,cutoff=.5):
    """Returns the number of characters that's needed to cover >= cutoff

    a: Numeric array
    cutoff: number that should be covered in the array

    Example:
    [   [.1 .8  .3],
        [.3 .2  .3],
        [.6 0   .4]]
    if cutoff = .75: column_degeneracy -> [2,1,3]
    if cutoff = .45: column_degeneracy -> [1,1,2]

    WARNING: watch out with floating point numbers. 
    if the cutoff= 0.9 and in the array is also 0.9, it might not be found
    >>> searchsorted(cumsum(array([.6,.3,.1])),.9)
    2
    >>> searchsorted(cumsum(array([.5,.4,.1])),.9)
    1

    If the cutoff value is not found, the result is clipped to the
    number of rows in the array. 
    """
    if not a:
        return []
    b = cumsum(sort(a,0)[::-1])
    try:
        degen = [searchsorted(b[:,idx],cutoff) for idx in range(len(b[0]))]
    except TypeError:
        raise ValueError, "Array has to be two dimensional"
    #degen contains now the indices at which the cutoff was hit
    #to change to the number of characters, add 1
    return clip(array(degen)+1,0,a.shape[0])

def hamming_distance(x,y):
    """Returns the Hamming distance between two arrays.

    The Hamming distance is the number of characters which differ between
    two sequences (arrays).
    
    WARNING: This function truncates the longest array to the length of 
    the shortest one.
    
    Example:
    ABC, ABB -> 1
    ABCDEFG, ABCEFGH -> 4
    """
    shortest = min(map(len,[x,y]))
    return sum(x[:shortest] != y[:shortest])

def norm(a):
    """Returns the norm of a matrix or vector

    Calculates the Euclidean norm of a vector.
    Applies the Frobenius norm function to a matrix 
    (a.k.a. Euclidian matrix norm)

    a = Numeric array
    """
    return sqrt(sum((a*a).flat))

def euclidean_distance(a,b):
    """Returns the Euclidean distance between two vectors/arrays
    a,b: Numeric vectors or arrays

    WARNING: this method is NOT intended for use on arrays of different
    sizes, but no check for this has been built in. 
    """
    return norm(a-b)

