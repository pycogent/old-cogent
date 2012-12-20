#!/usr/bin/env python
#file cogent_tests.motif.test_motif_formatters.py
from __future__ import division
from old_cogent.util.unit_test import TestCase, main
import string
import re
from copy import copy
import old_cogent.parse.meme
import old_cogent.motif.util
import old_cogent.motif.motif_formatters
import old_cogent.base.align
from old_cogent.parse.meme import *
from old_cogent.motif.util import *
from old_cogent.motif.motif_formatters import *
from old_cogent.base.align import Alignment

"""Tests of the motif_formatters module.

Owner: Jeremy Widmann jeremy.widmann@colorado.edu

Revision History:

Written 7/16/04 by Jeremy Widmann.

9/26/05 Jeremy Widmann: Changed tests for MotifStatsBySequence, MotifLocationsBySequence, and HighlightOnAlignment objects to reflect change:
each have optional sequence order parameter to be passed to __call__ method.

4/9/06 Jeremy Widmann: Commented out tests since MotifFormatters have all changed and haven't had time to rewrite tests before code merge.
"""

class MotifStatsBySequenceTests(TestCase):
    """Tests for MotifStatsBySequence class.
    """
    def setUp(self):
        """Setup for MotifStatsBySequence tests."""
        
        self.meme_results = copy(MEME_RESULTS)
        self.meme_results.Alignment['test']='acgu'
        
        self.sequences = [
                        'accucua',
                        'caucguu',
                        'cguacgu',
                        'cgacucg',
                        'cgaucag',
                        'cuguacc',
                        'cgcauca',
                        ]
        self.locations = [
                        Location('seq0',1,3),
                        Location('seq1',1,3),
                        Location('seq1',1,5),
                        Location('seq1',5,3),
                        Location('seq2',3,54),
                        Location('seq2',54,2),
                        Location('seq3',4,0),
                        ]
        self.Pvalues = [
                        .1,
                        .002,
                        .0000000003,
                        .6,
                        .0094,
                        .6,
                        .00201,
                        ]
        self.Evalues = [
                        .006,
                        .02,
                        .9,
                        .0200000001,
                        .09,
                        .0000003,
                        .900001,
                        ]
        self.modules_no_e = []
        for i in xrange(7):
            self.modules_no_e.append(ModuleInstance(self.sequences[i],
                                                    self.locations[i],
                                                    self.Pvalues[i]))
        
        self.module_no_template = Module(
            {
                (self.modules_no_e[0].Location.SeqId,
                 self.modules_no_e[0].Location.Start):self.modules_no_e[0],
                (self.modules_no_e[1].Location.SeqId,
                 self.modules_no_e[1].Location.Start):self.modules_no_e[1],
                (self.modules_no_e[2].Location.SeqId,
                 self.modules_no_e[2].Location.Start):self.modules_no_e[2],
                (self.modules_no_e[3].Location.SeqId,
                 self.modules_no_e[3].Location.Start):self.modules_no_e[3],
                (self.modules_no_e[4].Location.SeqId,
                 self.modules_no_e[4].Location.Start):self.modules_no_e[4],
                (self.modules_no_e[5].Location.SeqId,
                 self.modules_no_e[5].Location.Start):self.modules_no_e[5],
                (self.modules_no_e[6].Location.SeqId,
                 self.modules_no_e[6].Location.Start):self.modules_no_e[6],
                }
            )

        #Create a MotifResults object for testing
        self.minimal_motif_results = MotifResults()
        self.minimal_motif_results.Motifs=[Motif(self.module_no_template)]
        self.minimal_motif_results.Alignment=Alignment({
            'seq0':'aaaaa',
            'seq1':'ccccc',
            'seq2':'ggggg',
            'seq3':'uuuuu',
            })
        self.minimal_combined_p = {'CombinedP':
                                   {'seq0':'0.00001',
                                    'seq1':'0.0345',
                                    'seq2':'0.00003',
                                    'seq3':'0.00000003',}
                                   }
        
        self.motif_html_minimal = [\
            '<html><head><title>Motif Finder Results</title></head><body>',
            '<table><tr><td>Sequence</td><td></td><td>Motif_ID</td>',
            '<td>Motif_P_Value</td><td>Motif_Sequence</td></tr>',
            '<tr><td>seq0</td><td></td></tr>',
            '<tr><td></td><td></td><td>None</td><td>0.1</td>',
            '<td>accucua</td></tr>',
            '<tr><td>seq1</td><td></td></tr>',
            '<tr><td></td><td></td><td>None</td><td>3e-10</td>',
            '<td>cguacgu</td></tr>',
            '<tr><td></td><td></td><td>None</td><td>0.6</td>',
            '<td>cgacucg</td></tr>',
            '<tr><td>seq2</td><td></td></tr>',
            '<tr><td></td><td></td><td>None</td><td>0.6</td>',
            '<td>cuguacc</td></tr>',
            '<tr><td></td><td></td><td>None</td><td>0.0094</td>',
            '<td>cgaucag</td></tr>',
            '<tr><td>seq3</td><td></td></tr>',
            '<tr><td></td><td></td><td>None</td><td>0.00201</td>',
            '<td>cgcauca</td></tr>',
            '</table></body></html>']

        self.motif_html_complete = [\
            '<html><head><title>Motif Finder Results</title></head><body>',
            '<table><tr><td>Sequence</td><td>Combined_P_Value</td>',
            '<td>Motif_ID</td><td>Motif_P_Value</td><td>Motif_Sequence</td></tr>',
            '<tr><td>seq0</td><td>1e-05</td></tr>',
            '<tr><td></td><td></td><td>None</td><td>0.1</td>',
            '<td>accucua</td></tr>',
            '<tr><td>seq1</td><td>0.0345</td></tr>',
            '<tr><td></td><td></td><td>None</td><td>3e-10</td>',
            '<td>cguacgu</td></tr>',
            '<tr><td></td><td></td><td>None</td><td>0.6</td>',
            '<td>cgacucg</td></tr>',
            '<tr><td>seq2</td><td>3e-05</td></tr>',
            '<tr><td></td><td></td><td>None</td><td>0.6</td>',
            '<td>cuguacc</td></tr>',
            '<tr><td></td><td></td><td>None</td><td>0.0094</td>',
            '<td>cgaucag</td></tr>',
            '<tr><td>seq3</td><td>3e-08</td></tr>',
            '<tr><td></td><td></td><td>None</td><td>0.00201</td>',
            '<td>cgcauca</td></tr>',
            '</table></body></html>']

    def test_init(self):
        """__init__ function should initialize MotifStatsBySequence object."""
        
        #self.assertEqual(MotifStatsBySequence().MotifResults,None)
        #self.assertEqual(MotifStatsBySequence('MotifResults').MotifResults,
        #                 'MotifResults')
    def test_sequenceLines(self):
        """sequenceLines should return correct string given seqID."""
        """
        motif_stats = MotifStatsBySequence(self.meme_results)
        motif_stats.combinedP=True
        #Test for sequence in alignment with no motifs
        self.assertEqual(motif_stats.sequenceLines('test'),'')
        seq_line_1 = ['<tr><td>1</td><td>0.0348</td></tr>',
            '<tr><td></td><td></td><td>3</td><td>0.000106</td><td>CTATTGG</td></tr>']
        #Test for sequence in alignment with motif
        self.assertEqual(motif_stats.sequenceLines('1'),''.join(seq_line_1))
        """

    def test_Locations(self):
        """Calling Locations property should return dict from _get_location_dict
        """
        """
        #Create empty MotifStatsBySequence object
        motif_stats_empty = MotifStatsBySequence()
        self.assertEqual(motif_stats_empty.Locations,{})
        #Create MotifStatsBySequence object with minimal MotifResults object
        motif_stats = MotifStatsBySequence(self.minimal_motif_results)
        expected_locations = {Module(
            {('seq0', 1): 'accucua',
             ('seq1', 1): 'cguacgu',
             ('seq1', 3): 'cgacucg',
             ('seq2', 2): 'cuguacc',
             ('seq2', 3): 'cgaucag',
             ('seq3', 0): 'cgcauca'}):
            {'seq0': [1],
             'seq1': [1, 3],
             'seq2': [2,3],
             'seq3': [0],
             }
            }
        self.assertEqual(str(motif_stats.Locations),str(expected_locations))
        """
    def test_call(self):
        """Calling MotifStatsBySequence object should return correct HTML string
        """
        """
        #Test empty MotifResults
        motif_stats_empty = MotifStatsBySequence()
        self.assertEqual(motif_stats_empty(),'')
        #Test no combinedP
        motif_stats_minimal = MotifStatsBySequence(self.minimal_motif_results)
        self.assertEqual(motif_stats_minimal(),''.join(self.motif_html_minimal))
        #Test combinedP
        motif_stats_complete = MotifStatsBySequence(self.minimal_motif_results)
        motif_stats_complete.MotifResults.Results = self.minimal_combined_p
        self.assertEqual(motif_stats_complete(),
                         ''.join(self.motif_html_complete))
        """

class MotifLocationsBySequenceTests(TestCase):
    """Tests for MotifLocationsBySequence class.
    """
    def setUp(self):
        """Setup for MotifLocationsBySequence tests."""
        
        self.meme_results = copy(MEME_RESULTS)
        self.meme_results.Alignment['test']='acgu'
        
        self.sequences = [
                        'accucua',
                        'caucguu',
                        'cguacgu',
                        'cgacucg',
                        'cgaucag',
                        'cuguacc',
                        'cgcauca',
                        ]
        self.locations = [
                        Location('seq0',1,3),
                        Location('seq1',1,3),
                        Location('seq1',1,5),
                        Location('seq1',5,3),
                        Location('seq2',3,54),
                        Location('seq2',54,2),
                        Location('seq3',4,0),
                        ]
        self.Pvalues = [
                        .1,
                        .002,
                        .0000000003,
                        .6,
                        .0094,
                        .6,
                        .00201,
                        ]
        self.Evalues = [
                        .006,
                        .02,
                        .9,
                        .0200000001,
                        .09,
                        .0000003,
                        .900001,
                        ]
        self.modules_no_e = []
        for i in xrange(7):
            self.modules_no_e.append(ModuleInstance(self.sequences[i],
                                                    self.locations[i],
                                                    self.Pvalues[i]))
        
        self.module_no_template = Module(
            {
                (self.modules_no_e[0].Location.SeqId,
                 self.modules_no_e[0].Location.Start):self.modules_no_e[0],
                (self.modules_no_e[1].Location.SeqId,
                 self.modules_no_e[1].Location.Start):self.modules_no_e[1],
                (self.modules_no_e[2].Location.SeqId,
                 self.modules_no_e[2].Location.Start):self.modules_no_e[2],
                (self.modules_no_e[3].Location.SeqId,
                 self.modules_no_e[3].Location.Start):self.modules_no_e[3],
                (self.modules_no_e[4].Location.SeqId,
                 self.modules_no_e[4].Location.Start):self.modules_no_e[4],
                (self.modules_no_e[5].Location.SeqId,
                 self.modules_no_e[5].Location.Start):self.modules_no_e[5],
                (self.modules_no_e[6].Location.SeqId,
                 self.modules_no_e[6].Location.Start):self.modules_no_e[6],
                }
            )

        #Create a MotifResults object for testing
        self.minimal_motif_results = MotifResults()
        self.minimal_motif_results.Motifs=[Motif(self.module_no_template)]
        self.minimal_motif_results.Alignment=Alignment({
            'seq0':'aaaaa',
            'seq1':'ccccc',
            'seq2':'ggggg',
            'seq3':'uuuuu',
            })

        self.motif_html_complete = [\
            '<html><head><title>Motif Finder Results</title></head><body>',
            '<table>',
            '<tr><td>1:</td><td>18-CTATTGG-1</td></tr>',
            '<tr><td>105:</td><td>CTATTGGGGC-11</td></tr>',
            '<tr><td>11:</td><td>15-CTAGTGGGCC</td></tr>',
            '<tr><td>159:</td><td>14-CTATTGG</td></tr>',
            '<tr><td>17:</td><td>CGTTACG-9-CTATTGGGGC</td></tr>',
            '<tr><td>28:</td><td>3-CTATTGGGGC-13</td></tr>',
            '<tr><td>402-C01:</td><td>1-CGGTACG-16-CTATTGGGCC</td></tr>',
            '<tr><td>407-A07:</td><td>5-CTATTGGGGC-11-CGTTACG-1</td></tr>',
            '<tr><td>410-A10:</td><td>7-CGTTACG-13-CTATTGG</td></tr>',
            '<tr><td>505-D01:</td><td>3-TGTTACG-16-CTATTGGGGC-13</td></tr>',
            '<tr><td>507-B04-1:</td>',
            '<td>8-CGTTACG-13-CTAATGG-7-CTATTGG</td></tr>',
            '<tr><td>518-D12:</td><td>CTATTGGGGT-20-CATTACG-12</td></tr>',
            '<tr><td>621-H01:</td><td>30-CGTTACG-8-CTATTGGGGC-19</td></tr>',
            '<tr><td>625-H05:</td><td>2-CTAGTGGGGC-20-TGTTACG-26</td></tr>',
            '<tr><td>629-C08:</td>',
            '<td>5-TGTTCCG-6-CTATTGGGGC-9-CGTTACG-13-CTATTGG</td></tr>',
            '</table></body></html>']

    def test_init(self):
        """Tests for __init__ function."""
        
        """
        self.assertEqual(MotifLocationsBySequence().MotifResults,None)
        self.assertEqual(MotifLocationsBySequence('MotifResults').MotifResults,
                         'MotifResults')
        """

    def test_locations(self):
        """Calling Locations property should return dict from _get_location_dict
        """
        """
        #Create empty MotifStatsBySequence object
        motif_locations_empty = MotifLocationsBySequence()
        self.assertEqual(motif_locations_empty.Locations,{})
        #Create MotifStatsBySequence object with minimal MotifResults object
        motif_locations = MotifLocationsBySequence(self.minimal_motif_results)
        expected_module = Module(
            {('seq0', 1): 'accucua',
             ('seq1', 1): 'cguacgu',
             ('seq1', 3): 'cgacucg',
             ('seq2', 2): 'cuguacc',
             ('seq2', 3): 'cgaucag',
             ('seq3', 0): 'cgcauca'})
            
        expected_locations = {'seq0':
                              {1:expected_module},
                              'seq1':
                              {1:expected_module,
                               3:expected_module},
                              'seq2':
                              {2:expected_module,
                               3:expected_module},
                              'seq3':
                              {0:expected_module}
                              }
        self.assertEqual(str(motif_locations.Locations),str(expected_locations))
        """

    def test_sequenceLines(self):
        """sequenceLines should return correct string given seqID."""
        """
        motif_locations = MotifLocationsBySequence(self.meme_results)
        #Test for sequence in alignment with no motifs
        self.assertEqual(motif_locations.sequenceLines('test'),'')
        
        seq_lines = ['<tr><td>1:</td><td>18-CTATTGG-1</td></tr>', \
                     '<tr><td>629-C08:</td><td>5-TGTTCCG-6-CTATTGGGGC' +\
                     '-9-CGTTACG-13-CTATTGG</td></tr>']
        
        #Test for sequence in alignment with motifs
        self.assertEqual(motif_locations.sequenceLines('1'),seq_lines[0])
        self.assertEqual(motif_locations.sequenceLines('629-C08'),seq_lines[1])
        """
                         
    def test_call(self):
        """Calling MotifLocationsBySequence should return correct HTML string.
        """
        """
        #Test empty MotifResults
        motif_locations_empty = MotifLocationsBySequence()
        self.assertEqual(motif_locations_empty(),'')
        #Test combinedP
        motif_locations_complete =\
            MotifLocationsBySequence(self.meme_results)
        self.assertEqual(motif_locations_complete(),
                         ''.join(self.motif_html_complete))
        """

class SequenceByMotifTests(TestCase):
    """Tests for SequenceByMotif class.
    """
    def setUp(self):
        """Setup for SequenceByMotif tests."""
        
        self.meme_results = copy(MEME_RESULTS)
        
        self.sequences = [
                        'accucua',
                        'caucguu',
                        'cguacgu',
                        'cgacucg',
                        'cgaucag',
                        'cuguacc',
                        'cgcauca',
                        ]
        self.locations = [
                        Location('seq0',1,3),
                        Location('seq1',1,3),
                        Location('seq1',1,5),
                        Location('seq1',5,3),
                        Location('seq2',3,54),
                        Location('seq2',54,2),
                        Location('seq3',4,0),
                        ]
        self.Pvalues = [
                        .1,
                        .002,
                        .0000000003,
                        .6,
                        .0094,
                        .6,
                        .00201,
                        ]
        self.Evalues = [
                        .006,
                        .02,
                        .9,
                        .0200000001,
                        .09,
                        .0000003,
                        .900001,
                        ]
        self.modules_no_e = []
        for i in xrange(7):
            self.modules_no_e.append(ModuleInstance(self.sequences[i],
                                                    self.locations[i],
                                                    self.Pvalues[i]))
        
        self.module_no_template = Module(
            {
                (self.modules_no_e[0].Location.SeqId,
                 self.modules_no_e[0].Location.Start):self.modules_no_e[0],
                (self.modules_no_e[1].Location.SeqId,
                 self.modules_no_e[1].Location.Start):self.modules_no_e[1],
                (self.modules_no_e[2].Location.SeqId,
                 self.modules_no_e[2].Location.Start):self.modules_no_e[2],
                (self.modules_no_e[3].Location.SeqId,
                 self.modules_no_e[3].Location.Start):self.modules_no_e[3],
                (self.modules_no_e[4].Location.SeqId,
                 self.modules_no_e[4].Location.Start):self.modules_no_e[4],
                (self.modules_no_e[5].Location.SeqId,
                 self.modules_no_e[5].Location.Start):self.modules_no_e[5],
                (self.modules_no_e[6].Location.SeqId,
                 self.modules_no_e[6].Location.Start):self.modules_no_e[6],
                }
            )

        #Create a MotifResults object for testing
        self.minimal_motif_results = MotifResults()
        self.minimal_motif_results.Motifs=[Motif(self.module_no_template)]
        self.minimal_motif_results.Alignment=Alignment({
            'seq0':'aaaaa',
            'seq1':'ccccc',
            'seq2':'ggggg',
            'seq3':'uuuuu',
            })
        self.module_1_line = [\
            '<tr><td>1</td><td>2.18e-22</td></tr>',
            '<tr><td></td><td></td><td>105</td><td>1.95e-06</td>',
            '<td>CTATTGGGGCCGAAATGGTTA</td></tr>',
            '<tr><td></td><td></td><td>11</td><td>6.37e-06</td>',
            '<td>TACGTTGTTAGACAGCTAGTGGGCC</td></tr>',
            '<tr><td></td><td></td><td>17</td><td>1.95e-06</td>',
            '<td>CGTTACGCTACTTGTGCTATTGGGGC</td></tr>',
            '<tr><td></td><td></td><td>28</td><td>1.95e-06</td>',
            '<td>TCCCTATTGGGGCCAAGGGCTACGGG</td></tr>',
            '<tr><td></td><td></td><td>402-C01</td><td>3.3e-06</td>',
            '<td>CCGGTACGGTTTGTCTTAACATTCCTATTGGGCC</td></tr>',
            '<tr><td></td><td></td><td>407-A07</td><td>1.95e-06</td>',
            '<td>CGTTACTATTGGGGCGGGTATTTTCCCGTTACGT</td></tr>',
            '<tr><td></td><td></td><td>505-D01</td><td>1.95e-06</td>',
            '<td>GCATGTTACGTGACTTTTGATTGTTGCTATTGGGGCATTGCCGTACACG</td></tr>',
            '<tr><td></td><td></td><td>518-D12</td><td>9.4e-06</td>',
            '<td>CTATTGGGGTGTTGTATTGAGTTATTGCGACATTACGCGTTCTGGTTCG</td></tr>',
            '<tr><td></td><td></td><td>621-H01</td><td>1.95e-06</td>',
            '<td>CACAAAATGCCGCAGGTAGTCGAGGGAGTACGTTACGCATGCGTGCTATTGGGGCGTC',
            'ATTTGTCTACACTGGC</td></tr>',
            '<tr><td></td><td></td><td>625-H05</td><td>5.11e-06</td>',
            '<td>GCCTAGTGGGGCAGCTGACAGAATAGGTCGACTGTTACGGTTAGCGTTCCTTCAGGTATC',
            'ACANC</td></tr>',
            '<tr><td></td><td></td><td>629-C08</td><td>1.95e-06</td>',
            '<td>TTACGTGTTCCGTGAACACTATTGGGGCGTGTAAGAGCGTTACGTGTTCCGTGAACACTA',
            'TTGG</td></tr>']
        self.seq_by_motif_html_complete = [\
            '<html><head><title>Motif Finder Results</title></head><body>',
            '<table><tr><td>Motif</td><td>Combined_P_Value</td>',
            '<td>SequenceID</td><td>Sequence_P_Value</td><td>Sequence</td></tr>',
            '<tr><td>1</td><td>2.18e-22</td></tr>',
            '<tr><td></td><td></td><td>105</td><td>1.95e-06</td>',
            '<td>CTATTGGGGCCGAAATGGTTA</td></tr>',
            '<tr><td></td><td></td><td>11</td><td>6.37e-06</td>',
            '<td>TACGTTGTTAGACAGCTAGTGGGCC</td></tr>',
            '<tr><td></td><td></td><td>17</td><td>1.95e-06</td>',
            '<td>CGTTACGCTACTTGTGCTATTGGGGC</td></tr>',
            '<tr><td></td><td></td><td>28</td><td>1.95e-06</td>',
            '<td>TCCCTATTGGGGCCAAGGGCTACGGG</td></tr>',
            '<tr><td></td><td></td><td>402-C01</td><td>3.3e-06</td>',
            '<td>CCGGTACGGTTTGTCTTAACATTCCTATTGGGCC</td></tr>',
            '<tr><td></td><td></td><td>407-A07</td><td>1.95e-06</td>',
            '<td>CGTTACTATTGGGGCGGGTATTTTCCCGTTACGT</td></tr>',
            '<tr><td></td><td></td><td>505-D01</td><td>1.95e-06</td>',
            '<td>GCATGTTACGTGACTTTTGATTGTTGCTATTGGGGCATTGCCGTACACG</td></tr>',
            '<tr><td></td><td></td><td>518-D12</td><td>9.4e-06</td>',
            '<td>CTATTGGGGTGTTGTATTGAGTTATTGCGACATTACGCGTTCTGGTTCG</td></tr>',
            '<tr><td></td><td></td><td>621-H01</td><td>1.95e-06</td>',
            '<td>CACAAAATGCCGCAGGTAGTCGAGGGAGTACGTTACGCATGCGTGCTATTGGGGCGTCATTT',
            'GTCTACACTGGC</td></tr>',
            '<tr><td></td><td></td><td>625-H05</td><td>5.11e-06</td>',
            '<td>GCCTAGTGGGGCAGCTGACAGAATAGGTCGACTGTTACGGTTAGCGTTCCTTCAGGTATCAC',
            'ANC</td></tr>',
            '<tr><td></td><td></td><td>629-C08</td><td>1.95e-06</td>',
            '<td>TTACGTGTTCCGTGAACACTATTGGGGCGTGTAAGAGCGTTACGTGTTCCGTGAACA',
            'CTATTGG</td></tr>',
            '<tr><td>2</td><td>4.19e-09</td></tr>',
            '<tr><td></td><td></td><td>17</td><td>6.82e-05</td>',
            '<td>CGTTACGCTACTTGTGCTATTGGGGC</td></tr>',
            '<tr><td></td><td></td><td>402-C01</td><td>0.000277</td>',
            '<td>CCGGTACGGTTTGTCTTAACATTCCTATTGGGCC</td></tr>',
            '<tr><td></td><td></td><td>407-A07</td><td>6.82e-05</td>',
            '<td>CGTTACTATTGGGGCGGGTATTTTCCCGTTACGT</td></tr>',
            '<tr><td></td><td></td><td>410-A10</td><td>6.82e-05</td>',
            '<td>CTTTGCTCGTTACGTGGTTGTATGCCGCTATTGG</td></tr>',
            '<tr><td></td><td></td><td>505-D01</td><td>0.000174</td>',
            '<td>GCATGTTACGTGACTTTTGATTGTTGCTATTGGGGCATTGCCGTACACG</td></tr>',
            '<tr><td></td><td></td><td>507-B04-1</td><td>6.82e-05</td>',
            '<td>CTTGCACACGTTACGTGTGAGCCATTCTCTAATGGTGTTGCGCTATTGG</td></tr>',
            '<tr><td></td><td></td><td>518-D12</td><td>0.000214</td>',
            '<td>CTATTGGGGTGTTGTATTGAGTTATTGCGACATTACGCGTTCTGGTTCG</td></tr>',
            '<tr><td></td><td></td><td>621-H01</td><td>6.82e-05</td>',
            '<td>CACAAAATGCCGCAGGTAGTCGAGGGAGTACGTTACGCATGCGTGCTATTGGGGCGTCATTT',
            'GTCTACACTGGC</td></tr>',
            '<tr><td></td><td></td><td>625-H05</td><td>0.000174</td>',
            '<td>GCCTAGTGGGGCAGCTGACAGAATAGGTCGACTGTTACGGTTAGCGTTCCTTCAGGTATCA',
            'CANC</td></tr>',
            '<tr><td></td><td></td><td>629-C08</td><td>0.000645</td>',
            '<td>TTACGTGTTCCGTGAACACTATTGGGGCGTGTAAGAGCGTTACGTGTTCCGTGAACACTATT',
            'GG</td></tr><tr><td>3</td><td>0.000921</td></tr>',
            '<tr><td></td><td></td><td>1</td><td>0.000106</td>',
            '<td>TTACGCACTTGGATAGTGCTATTGGG</td></tr>',
            '<tr><td></td><td></td><td>159</td><td>0.000106</td>',
            '<td>TTACGACCGTTGGTCTATTGG</td></tr>',
            '<tr><td></td><td></td><td>410-A10</td><td>0.000106</td>',
            '<td>CTTTGCTCGTTACGTGGTTGTATGCCGCTATTGG</td></tr>',
            '<tr><td></td><td></td><td>507-B04-1</td><td>0.000106</td>',
            '<td>CTTGCACACGTTACGTGTGAGCCATTCTCTAATGGTGTTGCGCTATTGG</td></tr>',
            '<tr><td></td><td></td><td>629-C08</td><td>0.000106</td>',
            '<td>TTACGTGTTCCGTGAACACTATTGGGGCGTGTAAGAGCGTTACGTGTTCCGTGAACACTATT',
            'GG</td></tr></table></body></html>']

    def test_init(self):
        """Tests for __init__ function."""
        """
        self.assertEqual(SequenceByMotif().MotifResults,None)
        self.assertEqual(SequenceByMotif('MotifResults').MotifResults,
                         'MotifResults')
        """

    def test_locations(self):
        """Calling Locations property should return dict from _get_location_dict
        """
        """
        #Create empty SequenceByMotif object
        seq_by_motif_empty = SequenceByMotif()
        self.assertEqual(seq_by_motif_empty.Locations,{})
        #Create SequenceByMotif object with minimal MotifResults object
        seq_by_motif = SequenceByMotif(self.minimal_motif_results)
        expected_module = Module(
            {('seq0', 1): 'accucua',
             ('seq1', 1): 'cguacgu',
             ('seq1', 3): 'cgacucg',
             ('seq2', 2): 'cuguacc',
             ('seq2', 3): 'cgaucag',
             ('seq3', 0): 'cgcauca'})
            
        expected_locations = {expected_module:
                              {'seq0':[1],
                               'seq1':[1,3],
                               'seq2':[2,3],
                               'seq3':[0]
                               }
                              }
        self.assertEqual(str(seq_by_motif.Locations),str(expected_locations))
        """

    def test_moduleLines(self):
        """moduleLines should return correct string given module."""
        """
        seq_by_motif = SequenceByMotif(self.meme_results)
        #Test for sequence in alignment with motif
        self.assertEqual(seq_by_motif.moduleLines(\
            seq_by_motif.MotifResults.Motifs[0].Modules[0]),
                         ''.join(self.module_1_line))
        """

    def test_call(self):
        """Calling SequenceByMotif should return correct HTML string."""
        """
        #Test empty MotifResults
        seq_by_motif_empty = SequenceByMotif()
        self.assertEqual(seq_by_motif_empty(),'')
        #Test combinedP
        seq_by_motif_complete =\
            SequenceByMotif(self.meme_results)
        self.assertEqual(seq_by_motif_complete(),
                         ''.join(self.seq_by_motif_html_complete))
        """

#Global Test Data
ALIGN = Alignment({'1':'TTACGCACTTGGATAGTGCTATTGGG',
    '11':'TACGTTGTTAGACAGCTAGTGGGCC',
    '17':'CGTTACGCTACTTGTGCTATTGGGGC',
    '28':'TCCCTATTGGGGCCAAGGGCTACGGG',
    '105':'CTATTGGGGCCGAAATGGTTA',
    '159':'TTACGACCGTTGGTCTATTGG',
    '402-C01':'CCGGTACGGTTTGTCTTAACATTCCTATTGGGCC',
    '407-A07':'CGTTACTATTGGGGCGGGTATTTTCCCGTTACGT',
    '410-A10':'CTTTGCTCGTTACGTGGTTGTATGCCGCTATTGG',
    '505-D01':'GCATGTTACGTGACTTTTGATTGTTGCTATTGGGGCATTGCCGTACACG',
    '507-B04-1':'CTTGCACACGTTACGTGTGAGCCATTCTCTAATGGTGTTGCGCTATTGG',
    '518-D12':'CTATTGGGGTGTTGTATTGAGTTATTGCGACATTACGCGTTCTGGTTCG',
    '621-H01':'CACAAAATGCCGCAGGTAGTCGAGGGAGTACGTTACGCATGCGTGCTATTGGGGCGTCATTTGTCTACACTGGC',
    '625-H05':'GCCTAGTGGGGCAGCTGACAGAATAGGTCGACTGTTACGGTTAGCGTTCCTTCAGGTATCACANC',
    '629-C08':'TTACGTGTTCCGTGAACACTATTGGGGCGTGTAAGAGCGTTACGTGTTCCGTGAACACTATTGG'})

meme_file = open('MemeJob16346.txt')
lines = meme_file.readlines()
MEME_RESULTS = MemeParser(lines)
for module in MEME_RESULTS.Modules:
    MEME_RESULTS.Motifs.append(Motif(module))
MEME_RESULTS.Alignment = ALIGN
#Get total length of alignment
ALIGN_LEN = 0
for seq in MEME_RESULTS.Alignment.values():
    ALIGN_LEN += len(seq)
for motif in MEME_RESULTS.Motifs:
    for module in motif.Modules:
        module.Pvalue = module.Evalue/ALIGN_LEN
#End Global Test Data

#run if called from command-line
if __name__ == "__main__":
    main()
