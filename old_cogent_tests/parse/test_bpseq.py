#!/usr/bin/env python
#test_bpseq.py
"""Provides Tests for BpseqParser and related functions.

Owner: Sandra Smit (Sandra.Smit@colorado.edu)

Status: Stable

Revision History:
3/29/06 Sandra Smit: implemented tests.
"""

from old_cogent.util.unit_test import TestCase, main
from old_cogent.base.info import Info
from old_cogent.parse.bpseq import BpseqParseError, _construct_sequence,\
    _parse_header, _parse_residues, BpseqParser

class BpseqParserTests(TestCase):
    """Provides tests for BpseqParser and related functions"""

    def test_construct_sequence(self):
        """_construct_sequence: should return correct sequence or raise error
        """
        d = {0:'A',1:'C',2:'G',3:'U'}
        self.assertEqual(_construct_sequence(d),'ACGU')
        d = {0:'A',1:'C',2:'G',5:'U'}
        self.assertRaises(BpseqParseError, _construct_sequence, d)

    def test_parse_header(self):
        """_parse_header: should work on standard header"""
        h1 = ['Filename: d.16.b.E.coli.bpseq','Organism: Escherichia coli',\
            'Accession Number: J01695', 'Citation and related information'+\
            ' available at http://www.rna.icmb.utexas.edu']
        self.assertEqual(_parse_header(h1),{'Filename':'d.16.b.E.coli.bpseq',\
            'Accession_Number': 'J01695', 'Organism': 'Escherichia coli',\
            'Refs': {}})
        assert isinstance(_parse_header(h1), Info)
        
        #if the Citation line is missing, some other line is skipped!
        h2 = ['Filename: d.16.b.E.coli.bpseq','Organism: Escherichia coli',\
            'Accession Number: J01695']
        self.assertEqual(_parse_header(h2),{'Filename':'d.16.b.E.coli.bpseq',\
            'Organism': 'Escherichia coli', 'Refs': {}})

        #if it fails to split on ':' (Accession) line is skipped
        h3 = ['Filename: d.16.b.E.coli.bpseq','Organism: Escherichia coli',\
            'Accession Number J01695', 'Citation and related information'+\
            ' available at http://www.rna.icmb.utexas.edu']
        self.assertEqual(_parse_header(h3),{'Filename':'d.16.b.E.coli.bpseq',\
            'Organism': 'Escherichia coli', 'Refs': {}})

    def test_parse_residues(self):
        """_parse_residues: should work on valid data, returning Vienna or Pairs
        """
        lines = RES_LINES.split('\n')
        exp_seq = 'UGGUAAUACGUUGCGAAGCC'
        exp_pairs_w_pseudo = [(2,8),(3,7),(4,11),(5,10),(6,9),(12,18),(13,17)]
        exp_pairs_wo_pseudo_m = [(4,11),(5,10),(6,9),(12,18),(13,17)]
        exp_pairs_wo_pseudo_f = [(2,8),(3,7),(12,18),(13,17)]
        exp_vienna_m = '....(((..)))((...)).'
        exp_vienna_f = '..((...))...((...)).'
        self.assertEqual(_parse_residues(lines),(exp_seq, exp_vienna_m))
        self.assertEqual(_parse_residues(lines, pseudoknot_rule='first'),\
            (exp_seq, exp_vienna_f))
        self.assertEqual(_parse_residues(lines, remove_pseudoknots=True,\
            pseudoknot_rule='first'), (exp_seq, exp_vienna_f))
        self.assertEqual(_parse_residues(lines, return_pairs=True,\
            remove_pseudoknots=False), (exp_seq, exp_pairs_w_pseudo))
        self.assertEqual(_parse_residues(lines, return_pairs=True,\
            remove_pseudoknots=True), (exp_seq, exp_pairs_wo_pseudo_m))
        self.assertEqual(_parse_residues(lines, return_pairs=True,\
            remove_pseudoknots=True, pseudoknot_rule='first'),\
            (exp_seq, exp_pairs_wo_pseudo_f))

    def test_parse_residues_errors(self):
        """_parse_residues: should raise BpseqParseErrors in several cases
        """
        not_all_lines = RES_LINES_NOT_ALL.split('\n')
        wrong_lines = RES_LINES_WRONG.split('\n')
        conflict_lines = RES_LINES_CONFLICT.split('\n')
        self.assertRaises(BpseqParseError, _parse_residues, not_all_lines)
        self.assertRaises(BpseqParseError, _parse_residues, wrong_lines)
        self.assertRaises(BpseqParseError, _parse_residues, conflict_lines)

    def test_BpseqParser(self):
        """BpseqParser: should work on valid data, returning Vienna or Pairs
        """
        lines = RES_LINES_W_HEADER.split('\n')
        exp_seq = 'UGGUAAUACGUUGCGAAGCC'
        exp_pairs_w_pseudo = [(2,8),(3,7),(4,11),(5,10),(6,9),(12,18),(13,17)]
        exp_pairs_wo_pseudo_m = [(4,11),(5,10),(6,9),(12,18),(13,17)]
        exp_pairs_wo_pseudo_f = [(2,8),(3,7),(12,18),(13,17)]
        exp_vienna_m = '....(((..)))((...)).'
        exp_vienna_f = '..((...))...((...)).'
        self.assertEqual(BpseqParser(lines),(exp_seq, exp_vienna_m))
        self.assertEqual(BpseqParser(lines)[0].Info,\
            {'Filename':'d.16.b.E.coli.bpseq',\
            'Accession_Number': 'J01695', 'Organism': 'Escherichia coli',\
            'Refs': {}})
        self.assertEqual(BpseqParser(lines, pseudoknot_rule='first'),\
            (exp_seq, exp_vienna_f))
        self.assertEqual(BpseqParser(lines, remove_pseudoknots=True,\
            pseudoknot_rule='first'), (exp_seq, exp_vienna_f))
        self.assertEqual(BpseqParser(lines, return_pairs=True,\
            remove_pseudoknots=False), (exp_seq, exp_pairs_w_pseudo))
        self.assertEqual(BpseqParser(lines, return_pairs=True,\
            remove_pseudoknots=True), (exp_seq, exp_pairs_wo_pseudo_m))
        self.assertEqual(BpseqParser(lines, return_pairs=True,\
            remove_pseudoknots=True, pseudoknot_rule='first'),\
            (exp_seq, exp_pairs_wo_pseudo_f))

    def test_BpseqParser_errors(self):
        """BpseqParser: should handle errors correctly"""
        exp_seq = 'UGGUAAUACGUUGCGAAGCC'
        exp_vienna_m = '....(((..)))((...)).'
        
        #raises error when header is missing
        lines = RES_LINES.split('\n')
        self.assertRaises(BpseqParseError, BpseqParser, lines)

        #skips lines in unknown format
        lines = RES_LINES_UNKNOWN.split('\n')
        self.assertEqual(BpseqParser(lines),(exp_seq, exp_vienna_m))
        self.assertEqual(BpseqParser(lines)[0].Info,\
            {'Filename':'d.16.b.E.coli.bpseq',\
            'Accession_Number': 'J01695', 'Organism': 'Escherichia coli',\
            'Refs': {}})

RES_LINES=\
"""1 U 0
2 G 0
3 G 9
4 U 8
5 A 12
6 A 11
7 U 10
8 A 4
9 C 3
10 G 7
11 U 6
12 U 5
13 G 19
14 C 18
15 G 0
16 A 0
17 A 0
18 G 14
19 C 13
20 C 0"""


RES_LINES_NOT_ALL=\
"""1 U 0
2 G 0
3 G 0
6 A 0"""

RES_LINES_WRONG=\
"""1 U0
2 G 0
3 G 0
6 A 0"""

RES_LINES_CONFLICT=\
"""1 U 4
2 G 3
3 G 2
4 A 1
4 A 0"""

RES_LINES_W_HEADER=\
"""Filename: d.16.b.E.coli.bpseq
Organism: Escherichia coli
Accession Number: J01695
Citation and related information available at http://www.rna.icmb.utexas.edu
1 U 0
2 G 0
3 G 9
4 U 8
5 A 12
6 A 11
7 U 10
8 A 4
9 C 3
10 G 7
11 U 6
12 U 5
13 G 19
14 C 18
15 G 0
16 A 0
17 A 0
18 G 14
19 C 13
20 C 0"""

RES_LINES_UNKNOWN=\
"""Filename: d.16.b.E.coli.bpseq
Organism: Escherichia coli
Accession Number: J01695
Citation and related information available at http://www.rna.icmb.utexas.edu
1 U 0
2 G 0
3 G 9
UNKNOWN LINE
4 U 8
5 A 12
6 A 11
7 U 10
8 A 4
9 C 3
10 G 7
11 U 6
12 U 5
13 G 19
14 C 18
15 G 0
16 A 0
17 A 0
18 G 14
19 C 13
20 C 0"""

#run if called from command-line
if __name__ == "__main__":
    main()
