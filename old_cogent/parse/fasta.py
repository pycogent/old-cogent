#/usr/bin/env python
#file evo/parsers/fasta.py

"""Parsers for FASTA and related formats.

Owner: Rob Knight rob@spot.colorado.edu

Status: Development

Revision History

Written 11/8/03 by Rob Knight.

11/12/03 Rob Knight: modified to take account of comment lines. Now able to 
read NCBI FASTA sequences and interpret database identifiers correctly.
Successfully ran on entire genpept.fsa file without errors.
"""
from old_cogent.parse.record_finder import LabeledRecordFinder
from old_cogent.parse.record import RecordError
from old_cogent.base.sequence import Sequence
from old_cogent.base.info import Info, DbRef
from string import strip

def is_fasta_label(x):
    """Checks if x looks like a FASTA label line."""
    return x.startswith('>')

def is_blank_or_comment(x):
    """Checks if x is blank or a FASTA comment line."""
    return (not x) or x.startswith('#') or x.isspace()

FastaFinder = LabeledRecordFinder(is_fasta_label, ignore=is_blank_or_comment)

def MinimalFastaParser(infile, strict=True):
    """Yields successive sequences from infile as (label, seq) tuples.

    If strict is True (default), raises RecordError when label or seq missing.
    """
    for rec in FastaFinder(infile):
        #first line must be a label line
        if not is_fasta_label(rec[0]):
            if strict:
                raise RecordError, "Found Fasta record without label line: %s"%\
                    rec
            else:
                continue
        #record must have at least one sequence
        if len(rec) < 2:
            if strict:
                raise RecordError, "Found label line without sequences: %s" % \
                    rec
            else:
                continue
            
        label = rec[0][1:].strip()
        seq = ''.join(rec[1:])

        yield label, seq

def MinimalInfo(label):
    """Minimal info data maker: returns {'Label':label}."""
    return {'Label':label}

def FastaParser(infile,seq_maker=Sequence,info_maker=MinimalInfo,strict=True):
    """Yields successive sequences from infile as sequence objects.

    Constructs the sequence using seq_maker(seq, info=Info(info_maker(label))).

    If strict is True (default), raises RecordError when label or seq missing.
    Also raises RecordError if seq_maker fails.

    It is info_maker's responsibility to raise the appropriate RecordError or
    FieldError on failure.

    Result of info_maker need not actually be an info object, but can just be
    a dict or other data that Info can use in its constructor.
    """
    for label, seq in MinimalFastaParser(infile, strict=strict):
        if strict:
            #need to do error checking when constructing info and sequence
            info = info_maker(label) #will raise exception if bad
            try:
                yield seq_maker(seq, Info=info)
            except:
                raise RecordError, \
                "Sequence construction failed on record with label %s" % label
        else:
            #not strict: just skip any record that raises an exception
            try:
                yield(seq_maker(seq, Info=info_maker(label)))
            except:
                continue

#labeled fields in the NCBI FASTA records
NcbiLabels = {
'dbj':'DDBJ',
'emb':'EMBL',
'gb':'GenBank',
'ref':'RefSeq',
}

def NcbiFastaLabelParser(line):
    """Creates an Info object and populates it with the line contents.
    
    As of 11/12/03, all records in genpept.fsa and the human RefSeq fasta
    files were consistent with this format.
    """
    info = Info()
    try:
        ignore, gi, db, db_ref, description = map(strip, line.split('|', 4))
    except ValueError:  #probably got wrong value
        raise RecordError, "Unable to parse label line %s" % line
    info.GI = gi
    info[NcbiLabels[db]] = db_ref
    info.Description = description
    return info

def NcbiFastaParser(infile, seq_maker=Sequence, strict=True):
    return FastaParser(infile, seq_maker=seq_maker, 
        info_maker=NcbiFastaLabelParser, strict=strict)
