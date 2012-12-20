#!/usr/bin/env python
#file evo/parsers/rdb.py
"""Provides a parser for Rdb format files.

Data in from the European rRNA database in distribution format.

Owner: Sandra Smit ssmit@mac.com

Status: Development

Revision History

Written 11/18/03 by Sandra Smit
12/2/03 Sandra Smit: changed default SeqConstructor in RnaSequence to make stripping
possible, but keep all characters not in the RnaAlphabet. Changed MinimalRdbParser
to remove '*' from the end of a sequence.
"""
from string import strip
from old_cogent.parse.record_finder import DelimitedRecordFinder
from old_cogent.parse.record import RecordError
from old_cogent.base.sequence import Sequence,RnaSequence
from old_cogent.base.info import Info

RdbFinder = DelimitedRecordFinder('//')

_field_names = {'acc':'rRNA',\
                'src':'Source',\
                'str':'Strain',\
                'ta1':'Taxonomy1',\
                'ta2':'Taxonomy2',\
                'ta3':'Taxonomy3',\
                'ta4':'Taxonomy4',\
                'chg':'Changes',\
                'rem':'Remarks',\
                'aut':'Authors',\
                'ttl':'Title',\
                'jou':'Journal',\
                'dat':'JournalYear',\
                'vol':'JournalVolume',\
                'pgs':'JournalPages',\
                'mty':'Gene',\
                'del':'Deletions',\
                'seq':'Species'}


def InfoMaker(header_lines):
    """Returns an Info object constructed from the headerLines."""
    info = Info()
    for line in header_lines:
        all = line.strip().split(':',1)
        #strip out empty lines, lines without name, lines without colon
        if not all[0] or len(all) != 2: 
            continue
        try:
            name = _field_names[all[0]]
        except KeyError:
            name = all[0]
            
        value = all[1].strip()
        info[name] = value
    return info

def is_seq_label(x):
    "Check if x looks like a sequence label line."""
    return x.startswith('seq:')

def MinimalRdbParser(infile,strict=True):
    """Yield successive sequences as (headerLines, sequence) tuples.
    
    If strict is True (default) raises RecordError when 'seq' label is missing
    and if the record doesn't contain any sequences.
    """
    for rec in RdbFinder(infile):
        index = None
        for line in rec:
            if is_seq_label(line):
                index = rec.index(line) + 1 #index of first sequence line
        
        # if there is no line that starts with 'seq:' throw error or skip
        if not index:
            if strict:
                raise RecordError, "Found Rdb record without seq label "\
                    + "line: %s"%rec[0]
            else:
                continue
            
        headerLines = rec[:index]
        sequence = ''.join(rec[index:-1]) #strip off the delimiter
        if sequence.endswith('*'):
            sequence = sequence[:-1] #strip off '*'

        #if there are no sequences throw error or skip
        if not sequence:
            if strict:
                raise RecordError, "Found Rdb record without sequences: %s"\
                    %rec[0]
            else:
                continue

        yield headerLines, sequence

def RdbParser(lines, SeqConstructor=RnaSequence, LabelConstructor=InfoMaker\
                ,strict=True):
    """Treats lines as stream of Rdb records."""
    for header,sequence in MinimalRdbParser(lines,strict=strict):
        if strict:
            #need to do error checking while constructing info and sequence
            info = LabelConstructor(header)
            try:
                yield SeqConstructor(sequence,Info = info)
            except:
                raise RecordError, "Sequence construction failed on " + \
                "record with reference %s"%info.Refs
        else:
            #not strict: just skip any record that raises an exception
            try:
                yield SeqConstructor(sequence, Info=LabelConstructor(header))
            except:
                continue

if __name__ == '__main__':
    from sys import argv
    filename = argv[1]
    for sequence in RdbParser(open(filename)):
        print sequence.Species
        print sequence

