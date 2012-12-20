#/bin/env python
#file cogent/parse/phylip.py

"""Parsers for PHYLIP Format 

Owner: Micah Hamady hamady@colorado.edu

Status: Prototype - M. Robeson will be refining this, don't use yet

Revision History

Written 10/4/05 by Micah Hamady - Quick Hack to work w/app controllers 

"""
from old_cogent.parse.record import RecordError
from old_cogent.base.align import Alignment

def is_blank(x):
    """Checks if x is blank or a FASTA comment line."""
    return not x.strip()


def _get_header_info(line):
    """
    Get number of sequences and length of sequence
    """
    header_parts = map(int, line.split())
    
    if len(header_parts) != 2:
        raise RecordError, "Invalid header format"
    
    return header_parts

def _split_line(line, id_offset):
    """
    First 10 chars must be blank or contain id info
    """
    if not line or not line.strip():
        return None, None
  
    # extract id and sequence
    cur_id = line[0:id_offset].strip()
    cur_seq = line[id_offset:].strip().replace(" ", "")

    return cur_id, cur_seq

def MinimalPhylipParser(data, id_map=None):
    """Yields successive sequences from data as (label, seq) tuples.

    **Need to implement id map.

    **NOTE if using phylip interleaved format, will cache entire file in
        memory before returning sequences. If phylip file not interleaved
        then will yield each successive sequence.

    data: sequence of lines in phylip format (an open file, list, etc)
    id_map: optional id mapping from external ids to phylip labels - not sure
        if we're going to implement this


    returns (id, sequence) tuples
    """
    
    seq_cache = {}
    interleaved_id_map = {}
    id_offset = 10
    cur_ct = -1 
    is_interleaved = True

    for line in data:
        if cur_ct == -1:
            # get header info
            num_seqs, seq_len = _get_header_info(line)
          
            if not num_seqs or not seq_len:
                return 
            cur_ct += 1
            continue

        cur_id, cur_seq = _split_line(line, id_offset)

        # skip blank lines
        if not cur_id and not cur_seq:
            continue

        if cur_ct == 0:
            # check if interleaved or not
            if len(cur_seq) == seq_len:
                is_interleaved = False

        if not is_interleaved:
            yield cur_id, cur_seq
        else:
            cur_id_ix = cur_ct % num_seqs

            if (cur_ct + 1) % num_seqs == 0:
                id_offset = 0

            if cur_id_ix not in interleaved_id_map:
                interleaved_id_map[cur_id_ix] = cur_id
                seq_cache[cur_id_ix] = []

            seq_cache[cur_id_ix].append(cur_seq)
        cur_ct += 1


    # return joined seuqencess if interleaved
    if is_interleaved:
        for cur_id_ix, seq_parts in seq_cache.items():
            join_seq = ''.join(seq_parts)
            #print interleaved_id_map[cur_id_ix], join_seq

            if len(join_seq) != seq_len:
                raise RecordError, "Sequence length is not the same as header specification. Found %d, Expected %d" % (len(join_seq), seq_len)

            yield interleaved_id_map[cur_id_ix], join_seq

def get_align_for_phylip(data, id_map=None):
    """
    Convenience function to return aligment object from phylip data

    data: sequence of lines in phylip format (an open file, list, etc)
    id_map: optional id mapping from external ids to phylip labels - not sure
        if we're going to implement this

    returns Alignment object
    """

    mpp = MinimalPhylipParser(data, id_map)

    tuples = []
    for tup in mpp:
        tuples.append(tup)
    return Alignment(tuples)

