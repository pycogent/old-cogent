#/usr/bin/env python
#file cogent/parse/clustal.py

"""Parsers for Clustal and related formats.

Owner: Rob Knight rob@spot.colorado.edu

Status: Development  -- WARNING: ClustalParser will soon be replaced
with what is currently NewClustalParser! This will happen before 5/20/04!

Implementation Notes:

Currently, does not check whether sequences are the same length and are in
order. Skips any line that starts with a blank.

ClustalParser preserves the order of the sequences from the original file.
However, it does use a dict as an intermediate, so two sequences can't have
the same label. This is probably OK since Clustal will refuse to run on a
FASTA file in which two sequences have the same label, but could potentially
cause trouble with manually edited files (all the segments of the conflicting
sequences would be interleaved, possibly in an unpredictable way).

If the lines have trailing numbers (i.e. Clustal was run with -LINENOS=ON),
silently deletes them. Does not check that the numbers actually correspond to
the number of chars in the sequence printed so far.

Revision History

Written 12/27/03 by Rob Knight.

5/18/04 Rob Knight: added NewClustalParser, which returns an Alignment
object. Note that this will become ClustalParser in the near future:
existing code will break!
11/10/05 Sandra Smit: adjusted is_clustal_seq_line so it now works for 
MUSCLE alignments (in clustal format) as well. 
"""
from old_cogent.parse.record import RecordError, DelimitedSplitter
from old_cogent.base.sequence import Sequence
from old_cogent.base.align import Alignment
from old_cogent.base.info import Info, DbRef
from string import strip

def LabelLineParser(record, splitter, strict=True):
    """Returns dict mapping list of data to labels, plus list with field order.

    Field order contains labels in order encountered in file.

    NOTE: doesn't care if lines are out of order in different blocks. This 
    should never happen anyway, but it's possible that this behavior should
    be changed to tighten up validation.
    """
    labels = []
    result = {}
    for line in record:
        try:
            key, val = splitter(line.rstrip())
        except:
            if strict:
                raise RecordError, \
                    "Failed to extract key and value from line %s" % line
            else:
                continue    #just skip the line if not strict
            
        if key in result:
            result[key].append(val)
        else:
            result[key] = [val]
            labels.append(key)
    return result, labels

def is_clustal_seq_line(line):
    """Returns True if line starts with a non-blank character but not 'CLUSTAL'.

    Useful for filtering other lines out of the file.
    """
    return line and (not line[0].isspace()) and\
        (not line.startswith('CLUSTAL')) and (not line.startswith('MUSCLE'))

last_space = DelimitedSplitter(None, -1)

def delete_trailing_number(line):
    """Deletes trailing number from a line.

    WARNING: does not preserve internal whitespace when a number is removed! 
    (converts each whitespace run to a single space). Returns the original
    line if it didn't end in a number.
    """
    pieces = line.split()
    try:
        int(pieces[-1])
        return ' '.join(pieces[:-1])
    except ValueError:  #no trailing numbers
        return line

def MinimalClustalParser(record, strict=True):
    """Returns (data, label_order) tuple.

    Data is dict of label -> sequence (pieces not joined).
    """
    return LabelLineParser(map(delete_trailing_number, \
        filter(is_clustal_seq_line, record)), last_space, strict)

def OldClustalParser(record, seq_constructor=Sequence, aln_constructor=list, 
    strict=True):
    """Returns contents of record as an ordered list."""
    seqs, label_order = MinimalClustalParser(record, strict)
    result = []
    for label in label_order:
        result.append(seq_constructor(''.join(map(strip, seqs[label])), \
            Info={'Label':label}))
    return aln_constructor(result)

def ClustalParser(record, seq_constructor=Sequence, strict=True):
    """Returns contents of record as Alignment object."""
    seqs, label_order = MinimalClustalParser(record, strict)
    result = Alignment()
    for label, seq in seqs.items():
        new_seq = seq_constructor(''.join(map(strip, seq)))
        try:
            new_seq.Label = label
        except AttributeError:
            pass
        result[label] = new_seq
    result.RowOrder = label_order
    return result
