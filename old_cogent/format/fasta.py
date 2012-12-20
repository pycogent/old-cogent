#!/usr/bin/env python
# cogent.format.fasta.py

"""Writer for FASTA sequence format

Owner: Jeremy Widmann (jeremy.widmann@colorado.edu)

Status: Development

Revision History:

Written July 2005 by Jeremy Widmann

8/26/05 Jeremy Widmann:  fasta_from_alignment now casts label to a string.
"""

def fasta_from_sequences(seqs):
    """Returns a FASTA string given a list of sequences.
    
        - seqs can be a list of sequence objects or strings.
    """
    #List of fasta sequence lines
    fasta_list = []
    #For each sequence
    for i,seq in enumerate(seqs):
        #Check if it has a label
        label = str(i)
        try:
            if seq.Label:
                label = seq.Label
        except:
            pass
        try:
            if seq.Name:
                label = seq.Name
        except:
            pass
        #Add label line
        fasta_list.append('>'+label)
        #Add sequence line
        fasta_list.append(seq)
    #join on newline and return
    return '\n'.join(fasta_list)
    
def fasta_from_alignment(aln):
    """Returns a FASTA string given an alignment.
    
        - aln can be an Alignment object or dict.
    """
    #Get alignment order
    try:
        order = aln.RowOrder
    except:
        order = aln.keys()
        order.sort()
    #List of fasta sequence lines
    fasta_list = []
    #For each sequence
    for label in order:
        #append the label line
        fasta_list.append('>'+str(label))
        #append the sequence line
        fasta_list.append(aln[label])
    #join on newline and return
    return '\n'.join(fasta_list)
