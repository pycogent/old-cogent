#!/usr/bin/env python
#file cogent_tests/parse/test_microarray.py

"""Tests for the Microarray output parser

Owner: Jeremy Widmann Jeremy.Widmann@colorado.edu

Revision History

Written 10/11/04 by Jeremy Widmann.
"""
from __future__ import division
from old_cogent.util.unit_test import TestCase, main
from old_cogent.parse.agilent_microarray import *


class MicroarrayParserTests(TestCase):
    """Tests for MicroarrayParser.
    """

    def setUp(self):
        """Setup function for MicroarrayParser tests.
        """
        self.sample_file = ['first line in file',
                            'second line, useless data',
                            'FEATURES\tFirst\tL\tProbeName\tGeneName\tLogRatio',
                            'DATA\tFirst\tData\tProbe1\tGene1\t0.02',
                            'DATA\tSecond\tData\tProbe2\tGene2\t-0.34']
    def test_MicroarrayParser_empty_list(self):
        #Empty list should return tuple of empty lists
        self.assertEqual(MicroarrayParser([]),([],[],[]))
    def test_MicroarrayParser(self):
        #Given correct file format, return correct results
        self.assertEqual(MicroarrayParser(self.sample_file),
                            (['PROBE1','PROBE2'],
                            ['GENE1','GENE2'],[float(0.02),float(-0.34)]))
        

#run if called from command-line
if __name__ == "__main__":
    main()
