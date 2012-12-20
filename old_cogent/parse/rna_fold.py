#!/usr/bin/env python
#file cogent/parse/rna_fold.py

"""Parses RNAfold dot plot output file.

Owner: Jeremy Widmann Jeremy.Widmann@colorado.edu

Status: Development

Revision History

Written 10/6/04 by Jeremy Widmann.

10/19/04 Jeremy Widmann: Changed getSequence function to explicitly remove the
    trailing backslash from each sequence line rather than remove all non-alpha
    characters.

7/12/06 Jeremy Widmann: 
"""
from string import strip
from old_cogent.parse.record_finder import LabeledRecordFinder

def get_min_free_energy(stdout_string):
    """Returns minimum free energy from RNAfold or RNAeval Standard Out string.
    """
    lines = stdout_string.splitlines()
    return float(lines[1].split(' ',1)[-1][1:-1].strip())

def RnaFoldParser(lines):
    """Returns a tuple containing sequence and dot plot indices.
    
        (sequence, (index1, index2, pair probability))
    """
    sequence = ''
    indices = []
    #Make sure lines is not empty
    if lines:
        #Get the block of lines that starts with /sequence
        sequence_block = LabeledRecordFinder(\
            lambda x: x.startswith('/sequence'))
        #only care about the second element in the result
        seq_block = list(sequence_block(lines))[1]
        #Get the sequence from the block
        sequence = getSequence(seq_block)
        #Get the indices and pair probabilites from the block
        indices = getIndices(seq_block)
    return (sequence, indices)


def getSequence(lines):
    """Returns sequence that RNAfold dot plot represents, given lines.
    """
    sequence_pieces = []
    #For each line after the first, containing /sequence
    for line in map(strip, lines[1:]):
        #If the line which denotes the end of a sequence is not reached
        if line.startswith(')'):
            break
        else:
            #Strip of whitespace and add to list
            sequence_pieces.append(line.replace('\\',''))
    return ''.join(sequence_pieces)
    
def getIndices(lines):
    """Returns list of tuples: (index1,index2,pair probability).
    """
    index_list = []
    #For each line that ends with 'ubox' (which denotes lines with indices)
    for line in filter(lambda x: x.endswith('ubox'), lines):
            #split on whitespace
            up_index,down_index,probability,ubox = line.split()
            #Build tuple with indices and pair probability
            index_list.append((int(up_index), int(down_index), \
                float(probability)))
    return index_list
