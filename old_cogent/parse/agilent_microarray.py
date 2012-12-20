#!/usr/bin/env python
#file cogent/parse/agilent_microarray.py

"""Parses Microarray output file.

Owner: Jeremy Widmann Jeremy.Widmann@colorado.edu

Status: Development

Revision History

Written 10/11/04 by Jeremy Widmann.
"""
from old_cogent.parse.record_finder import LabeledRecordFinder

def MicroarrayParser(lines):
    """Returns tuple: ([ProbeNames],[GeneNames],[LogRatios]) for all dots in
    microarray file.
    """
    probe_names = []
    gene_names = []
    log_ratios = []
    #Make sure lines is not empty
    if lines:
        #Get the block of lines that starts with FEATURES
        features_record = LabeledRecordFinder(\
            lambda x: x.startswith('FEATURES'))
        features_block = list(features_record(lines))
        #Discard first block
        features_block = features_block[1]
        #Get the indices of GeneName and LogRatio from the block
        features_list = features_block[0].split('\t')
        probe_index = features_list.index('ProbeName')
        gene_index = features_list.index('GeneName')
        log_index = features_list.index('LogRatio')
        #Get the lists for GeneName and LogRatio
        for line in features_block[1:]:
            temp = line.split('\t')
            probe_names.append(temp[probe_index].upper())
            gene_names.append(temp[gene_index].upper())
            log_ratios.append(float(temp[log_index]))
    return (probe_names, gene_names, log_ratios)
    