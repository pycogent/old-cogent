#!/usr/bin/env python
# cogent_tests.format.test_fasta.py

"""Tests for FASTA sequence format writer.

Owner: Jeremy Widmann (jeremy.widmann@colorado.edu)

Status: Development

Revision History:

Written July 2005 by Jeremy Widmann
"""
from old_cogent.util.unit_test import TestCase, main
from old_cogent.format.fasta import fasta_from_sequences, fasta_from_alignment
from old_cogent.base.align import Alignment
from old_cogent.base.sequence import Sequence
from copy import copy

class FastaTests(TestCase):
    """Tests for Fasta writer.
    """
    def setUp(self):
        """Setup for Fasta tests."""
        self.strings = ['AAAA','CCCC','gggg','uuuu']
        self.labels = ['1st','2nd','3rd','4th']
        self.sequences_with_labels = map(Sequence,copy(self.strings))
        self.sequences_with_names = map(Sequence,copy(self.strings))
        for l,sl,sn in zip(self.labels,self.sequences_with_labels,\
            self.sequences_with_names):
            sl.Label = l
            sn.Name = l
        self.fasta_no_label='>0\nAAAA\n>1\nCCCC\n>2\ngggg\n>3\nuuuu'
        self.fasta_with_label=\
            '>1st\nAAAA\n>2nd\nCCCC\n>3rd\ngggg\n>4th\nuuuu'
        self.alignment_dict = {'1st':'AAAA','2nd':'CCCC','3rd':'gggg',
            '4th':'uuuu'}
        self.alignment_object = Alignment(copy(self.alignment_dict))
        self.alignment_object.RowOrder = ['1st','2nd','3rd','4th']
        
    
    def test_fastaFromSequence(self):
        """should return correct fasta string."""
        self.assertEqual(fasta_from_sequences(''),'')
        self.assertEqual(fasta_from_sequences(self.strings),\
            self.fasta_no_label)
        self.assertEqual(fasta_from_sequences(self.sequences_with_labels),\
            self.fasta_with_label)
        self.assertEqual(fasta_from_sequences(self.sequences_with_names),\
            self.fasta_with_label)
    
    def test_fasta_from_alignment(self):
        """should return correct fasta string."""
        self.assertEqual(fasta_from_alignment({}),'')
        self.assertEqual(fasta_from_alignment(self.alignment_dict),\
            self.fasta_with_label)
        self.assertEqual(fasta_from_alignment(self.alignment_object),\
            self.fasta_with_label)

if __name__ == "__main__":
    main()
            
            