#!/usr/bin/env python
#file cogent/parse/rfam.py
"""Provides a parser for Rfam format files.

Owners: Sandra Smit (Sandra.Smit@colorado.edu)
        Greg Caporaso (caporaso@colorado.edu)

Status: Development. According to future requirements behavior will be changed

Revision History

12/31/03 Written by Sandra Smit and Greg Caporaso

1/8/04 Greg Caporaso: in is_seq_line changed (line and ...) to (len(line)>0
and ...) to avoid a bug where the empty string was returned

1/15/04 Sandra Smit: MinimalRfamParser: changed sequence construction part,
so it raises appropriate errors. is_seq_line changed back to the original \
'return line etc'.

1/20/04 Sandra Smit: made changes according to Rob's comments. Most important 
changes to structure construction in MinimalRfamParser,header construction
in HeaderToInfo, and label splitting in RfamSequence.

11/29/04 Sandra Smit: changed the output of MinimalRfamParser and RfamParser.
They now return the sequences as an Alignment object. The sequences are keyed
by their original label in the database. Changed RfamSequence to LabelToInfo,
which handles the parsing of the sequence label. Replacing dots with dashes in
the sequence has moved to the MinimalRfamParser (uses ChangedSequence). All tests working.

2/24/06 Sandra Smit: adjusted MinimalRfamParser, so it doesn't raise an error
when the header is missing. It now works for a file containing a single family
in stockholm format (where the header information is missing).
"""
from string import strip
from old_cogent.parse.record import RecordError
from old_cogent.parse.record_finder import DelimitedRecordFinder
from old_cogent.parse.clustal import OldClustalParser, ClustalParser
from old_cogent.base.sequence import Sequence,Rna
from old_cogent.base.info import Info
from old_cogent.struct.rna2d import WussStructure
from old_cogent.util.transform import trans_all,keep_chars

RfamFinder = DelimitedRecordFinder('//')

#all fields concerning the references are translated to None, except for 
# the MedLine ID, so that we can lookup the information if needed.
#RC = Reference comment
#RN = Reference Number
#RT = Reference Title
#RA = Reference Author
#RL = Reference Location
# The None fields are filtered out later
_field_names = {'AC':'Rfam',\
                'ID':'Identification',\
                'DE':'Description',\
                'AU':'Author',\
                'SE':'AlignmentSource',\
                'SS':'StructureSource',\
                'BM':'BuildCommands',\
                'GA':'GatheringThreshold',\
                'TC':'TrustedCutoff',\
                'NC':'NoiseCutoff',\
                'TP':'FamilyType',\
                'SQ':'Sequences',\
                'PI': 'PreviousIdentifications',\
                'DC': 'DatabaseComment',\
                'DR': 'DatabaseReference',\
                'RC': None,\
                'RN': None,\
                'RM': 'MedlineRef',\
                'RT': None,\
                'RA': None,\
                'RL': None,\
                'CC': 'Comment'}
                

def HeaderToInfo(header,strict=True):
    """Returns an Info object constructed from the header lines.

    Header is a list of lines that contain header information.
    Fields that can occur multiple times in a header are stored in a list.
    Fields that (should) occur only once are stored as a single value
    Comments are joined by ' ' to one field.
    Fields concerning the references are ignored, except for MedLine ID.
    """
    # construct temporary dictionary containing all original information
    initial_info = {}
    for line in header:
        line = line.strip()
        if not line:
            continue
        try:
            init,label,content = line.split(' ',2)
            if not init == '#=GF' or len(label) != 2:
                raise RecordError
        except:
            if strict:
                raise RecordError, "Failed to extract label and content " +\
                    "information from line %s"%(line)
            else:
                continue
        if label in ['BM','DR','RM','CC']:
            if label in initial_info:
                initial_info[label].append(content.strip())
            else:
                initial_info[label] = [content.strip()]
        else:
            initial_info[label] = content.strip()
            
    # transform initial dict into final one
    # throw away useless information; group information
    final_info={}
    for key in initial_info.keys():
        name = _field_names.get(key,key)
        if name == 'Comment':
            value = ' '.join(initial_info[key])
        else:
            value = initial_info[key]
        final_info[name] = value
    
    return Info(final_info)

def LabelToInfo(sequence, strict=True):
    """Returns an Info object constructed from the sequence Label

    sequence: Sequence object with an 'Label' attribute

    The label will be split on Genbank acc. no. and sequence coordinates.
    The coordinates will be shifted one position, since in Python the first
        position is 0.
    """
    #adjust label
    label = sequence.Label
    try:
        gb, pos = label.split('/',1) #split genbank label and pos
        if not gb:
            gb = None
        if not pos:
            pos = None
    except: #unable to split, so string doesn't contain '/'
        if strict:
            raise RecordError, "Failed to extract genbank id and positions" +\
            " from label %s"%label
        else:
            gb = None
            pos =None
    if pos:
        try:
            start, end = pos.split('-',1) #split start and end pos
        except:
            if strict:
                raise RecordError, "Failed to extract genbank id and positions" +\
            " from label %s"%label
            else:
                start = None
                end = None
    else:
        start = None
        end = None
    if start:
        # adjust start position to do the correct thing in python
        # see comment in docstring
        start = int(start)-1
    if end:
        end = int(end)
    info = Info({'GenBank':gb,'Start':start,'End':end})
    return info

def is_header_line(line):
    """Returns True if line is a header line"""
    return line.startswith('#=GF')

def is_seq_line(line):
    """Returns True if line is a sequence line"""
    return bool(line) and (not line[0].isspace()) and \
    (not line.startswith('#')) and (not line.startswith('//'))

def is_structure_line(line):
    """Returns True if line is a structure line"""
    return line.startswith('#=GC SS_cons')

def ChangedSequence(data, seq_constructor=Rna):
    """Returns new RNA Sequence object, replaces dots with dashes in sequence.
    """
    return seq_constructor(str(data).replace('.','-'))

def MinimalRfamParser(infile,strict=True):
    """Yield successive sequences as (header, sequences, structure) tuples.
    
    header is a list of header lines
    sequences is an Alignment object. Sequences are Rna objects keyed by the
        original labels in the database.
    structure is a WussStructure
    """
    for record in RfamFinder(infile):
        header = []
        sequences = []
        structure = []
        for line in record:
            if is_header_line(line):
                header.append(line.strip())
            elif is_seq_line(line):
                sequences.append(line)
            elif is_structure_line(line):
                structure.append(line)
            else:
                continue
        #sequence and structure are required. An empty header is possible,
        #for example when looking at the stockholm format of just one family
        if not sequences or not structure:
            if strict:
                error = 'Found record with missing element(s): '
                if not sequences:
                    error += 'sequences '
                if not structure:
                    error += 'structure '
                raise RecordError, error
            else:
                continue
        #join all sequence parts together, construct label
        try:
            sequences = ClustalParser(sequences,strict=strict,
                seq_constructor=ChangedSequence)
        except RecordError, e:
            if strict:
                raise RecordError, str(e)
            else:
                continue
        
        #construct the structure
        try:
            res = ClustalParser(structure, strict=strict)
            assert len(res) == 1 #otherwise multiple keys
            structure = res['#=GC SS_cons']
        except (RecordError, KeyError, AssertionError):
            if strict:
                raise RecordError,\
                    "Can't parse structure of family: %s"%(str(header))
            else:
                structure = None
                            
        yield header, sequences, structure
                
def RfamParser(lines, seq_constructor=Rna, label_constructor=\
    HeaderToInfo,struct_constructor=WussStructure,strict=True):
    """Yields (family_info, sequences, structure).

    Treats lines as a stream of Rfam records.
    Family_info is the general information about the alignment.
    Sequences is an Alignment object. Each sequence has its own Info
        object with Genbank ID etc. Sequences are keyed by the original 
        label in the database.
    Structure is the consensus structure of the alignment, in Wuss format
    """
    for header, alignment, structure in MinimalRfamParser\
        (lines,strict=strict):
        if strict:
            try:
                family_info = label_constructor(header,strict=strict)
            except:
                raise RecordError,"Info construction failed on " +\
                    "record with header %s"%header
            try:
                for seq in alignment.iterRows():
                    seq.Info = LabelToInfo(seq, strict=strict)
                structure = struct_constructor(structure)
                yield family_info, alignment, structure
            except:
                raise RecordError,"Sequence construction failed on " +\
                    "record with reference %s"%(family_info.Refs)
        else:
            try:
                family_info = label_constructor(header,strict=strict)
                for seq in alignment.iterRows():
                    seq.Info = LabelToInfo(seq, strict=strict)
                structure = struct_constructor(structure)
                yield family_info, alignment, structure
            except:
                continue

