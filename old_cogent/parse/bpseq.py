#!/usr/bin/env python
#bpseq.py
"""Provides parser for bpseq files downloaded from Gutell's comparative 
RNA website.

Owner: Sandra Smit (Sandra.Smit@colorado.edu)

Status: Stable

Revision History:
2005? Sandra Smit: written parser
3/29/06 Sandra Smit: added parameters to BpseqParser to return either
    ViennaStructure or Pairs object. Implemented tests.

The file format is:

Filename: d.16.b.E.coli.bpseq
Organism: Escherichia coli
Accession Number: J01695
Citation and related information available at http://www.rna.icmb.utexas.edu
1 A 0
2 A 0
3 A 0
4 U 0
5 U 0
6 G 0
7 A 0
8 A 0
9 G 25
10 A 24
11 G 23
12 U 22
13 U 21
14 U 0

So, header of four lines (Filename, Organism, Accession Number, Citation)
Sequence, structure information in tuples of residue position, residue name,
residue partner. The residue partner is 0 if the base is unpaired.

Numbering is 1-based!
"""
from string import strip
from __future__ import division
from old_cogent.struct.rna2d import Vienna, Pairs
from old_cogent.base.info import Info
from old_cogent.base.sequence import Rna

class BpseqParseError(Exception):
    """Exception raised when an error occurs during parsing a bpseq file"""
    pass

def _construct_sequence(seq_dict):
    """Constructs Rna Sequence from dict of pos:residue.

    NOTE: Adjusts numbering from starting-at-one to starting-at-zero

    seq_dict: dictionary of position: residue
    """
    
    max_pos = max(seq_dict.keys())
    #initiate sequence with gaps
    seq = ['-']*(max_pos+1) #max_pos is highest index, seq should be that +1
    #assign residues to positions
    for k,v in seq_dict.items():
        seq[k] = v
    #raise Error if there are still gaps in the sequence
    if '-' in seq:
        raise BpseqParseError,\
            "Not all positions in the sequence have a specified residue: %s"\
            %(''.join(seq))
    
    return ''.join(seq)

def _parse_header(header_lines):
    """Returns Info object from header information.
    
    Parses only the first three header lines with Filename, Organism, and
        Accession number.
    There's no error checking in here. If it fails to split on ':', the 
        information is simply not added to the dictionary. If the last line
        is not the Citation line, some other last line will be skipped.
    
    header_lines: list of lines containing header information
    """
    info = {}
    #iterate over all lines except the last (which tells you where to 
    #find related information (always the same website))
    for line in header_lines[:-1]:
        line = line.strip()
        try:
            field, value = map(strip,line.split(':',1))
            field = field.replace(' ','_')
            info[field] = value
        except:
            #no interesting header line
            pass
    return Info(info)

def _parse_residues(residue_lines, return_pairs=False,\
    remove_pseudoknots=False, pseudoknot_rule='majority'):
    """Returns Rna sequence and Vienna structure built from the residue list
    
    Checks for double entries both in the sequence and the structure, and
    checks that the structre is valid in the sense that if (up,down) in there,
    that (down,up) is the same. 
    """
    #create dictionary/list for sequence and structure
    seq_dict = {}
    pairs = Pairs()
    
    for line in residue_lines:
        try:
            pos, res, partner = line.strip().split()
            
            #convert to int AND ADJUST NUMBERING
            pos = int(pos)-1
            partner = int(partner)-1
            
            #fill seq_dict
            if pos in seq_dict:
                raise BpseqParseError,\
                    "Double entry for residue %s (%s in bpseq file)"\
                    %(str(pos), str(pos+1))
            else:
                seq_dict[pos] = res
            
            #fill Pairs object
            if partner == -1: #because of number adjustment
                partner = None
            pairs.append((pos,partner))
        except ValueError:
            raise BpseqParseError, "Failed to parse line: %s"%(line)
    
    #check for conflicts, remove unpaired ones, remove pseudoknots
    if pairs.hasConflicts():
        raise BpseqParseError, "Conflicts in the list of basepairs"
    
    pairs = pairs.directed()
    pairs.sort()
    seq = Rna(_construct_sequence(seq_dict))
    
    if remove_pseudoknots is True or return_pairs is False:
        #either pseudoknots are removed on request or a Vienna structure is
        #requested for which the pseudoknots also need to be removed
        if pairs.hasPseudoknots():
            pairs = pairs.nested(rule=pseudoknot_rule)

    if return_pairs:
        return seq, pairs
    else: #Vienna structure requested
        #make the actual seq and struct strings
        struct = pairs.toVienna(max(seq_dict.keys())+1)
        assert len(seq) == len(struct)
        return seq, struct

def BpseqParser(lines, return_pairs=False, remove_pseudoknots=False,\
    pseudoknot_rule='majority'):
    """Returns sequence and structure specified in file.

    infile: filestream of bpseq file.
    return_pairs: if True, Pairs object is returned, if False (default), a
        ViennaStructure object is returned. In this case the pseudoknots are
        automatically removed!
    remove_pseudoknots: if True, pseudoknots are removed from the Pairs object
        with the specified rule. If False, the plain Pairs object is returned.
    pseudoknot_rule: Rule with which the pseudoknots are removed. "majority"
        removes pairs such that the majority of pairs survives, "first" keeps
        the first base pair found as the real one and the next as the pseudo-
        knotted pair. For more documentation see the PseudoknotRemover in
        cogent.struct.rna2d

    Bpseq file looks like this:
    
    Filename: d.16.b.E.coli.bpseq
    Organism: Escherichia coli
    Accession Number: J01695
    Citation and related information available at http://www....
    1 A 0
    2 A 0
    3 A 0
    4 U 0
    5 U 0
    6 G 0
    7 A 0
    8 A 0
    9 G 25
    10 A 24
    11 G 23
    12 U 22
    13 U 21
        
    So, 4 header lines, followed by a list of residues.
    Position (indexed to 1), residue, partner position
    """
    #split header and residue lines
    header = []
    residues = []
    
    for line in lines:
        if line.startswith('Filename') or line.startswith('Organism') or\
            line.startswith('Accession') or line.startswith('Citation'):
            header.append(line.strip())
        elif len(line.split()) == 3:
            residues.append(line.strip())
        else:
            #unknown
            continue
    if not header:
        raise BpseqParseError,\
            "No header information in input lines"

    #parse header and seq/struct separately
    header_info = _parse_header(header)
    seq, struct = _parse_residues(residues, return_pairs=return_pairs,\
        remove_pseudoknots=remove_pseudoknots,\
        pseudoknot_rule=pseudoknot_rule)
    
    #add header info to the sequence as Info object
    seq.Info = header_info
    
    return seq, struct

if __name__ == "__main__":
    from sys import argv
    seq, struct = BpseqParser(open(argv[1]))
    print seq
    print seq.Info
    print struct
