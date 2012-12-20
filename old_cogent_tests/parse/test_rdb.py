#!/usr/bin/env python
#file evo/parsers/test_rdb.py
"""Unit test for RDB Parser

Revision History

11/20/03 Written by Sandra Smit (used Rob's test_fasta.py as example/template
"""


from old_cogent.parse.rdb import RdbParser, MinimalRdbParser,is_seq_label,\
    InfoMaker
from old_cogent.base.sequence import Sequence, Dna
from old_cogent.base.info import Info
from old_cogent.parse.record import RecordError
from old_cogent.util.unit_test import TestCase, main

class RdbTests(TestCase):
    """Tests for top-level functions in Rdb.py"""

    def test_is_seq_label(self):
        """is_seq_label should return True if a line starts with 'seq:'"""
        seq = 'seq:this is a sequence line'
        not_seq = 'this is not a sequence line'
        still_not_seq = 'this seq: is still not a sequence line'
        self.assertEqual(is_seq_label(seq),True)
        self.assertEqual(is_seq_label(not_seq),False)
        self.assertEqual(is_seq_label(still_not_seq),False)
        
class InfoMakerTests(TestCase):
    """Tests for the Constructor InfoMaker. Should return an Info object"""
    
    def test_empty(self):
        """InfoMaker should return an empty Info obj when initiated with an empty header"""
        empty_header = []
        obs = InfoMaker(empty_header)
        exp = Info()
        self.assertEqual(obs,exp)
    
    def test_full(self):
        """InfoMaker should return Info object with name, value pairs"""
        test_header = ['acc: X3402','abc:1','mty: ssu','seq: Mit. X3402',\
                        '','nonsense',':no_name']
        obs = InfoMaker(test_header)
        exp = Info()
        exp.rRNA = 'X3402'
        exp.abc = '1'
        exp.Species = 'Mit. X3402'
        exp.Gene = 'ssu'
        self.assertEqual(obs,exp)

class GenericRdbTest(TestCase):
    "SetUp data for all Rdb parsers"""
    
    def setUp(self):
        self.empty = []
        self.labels = 'mty:ssu\nseq:bac\n//\nttl:joe\nseq:mit\n//'.split('\n')
        self.nolabels = 'ACGUAGCUAGCUAC\nGCUGCAUCG\nAUCG\n//'.split('\n')
        self.oneseq = 'seq:H.Sapiens\nAGUCAUCUAGAUHCAUHC\n//'.split('\n')
        self.multiline = 'seq:H.Sapiens\nAGUCAUUAG\nAUHCAUHC\n//'.split('\n')
        self.threeseq = 'seq:bac\nAGU\n//\nseq:mit\nACU\n//\nseq:pla\nAAA\n//'.split('\n')
        self.twogood = 'seq:bac\n//\nseq:mit\nACU\n//\nseq:pla\nAAA\n//'.split('\n')
        self.oneX = 'seq:bac\nX\n//\nseq:mit\nACT\n//\nseq:pla\nAAA\n//'.split('\n')
        self.strange = 'seq:bac\nACGUXxAaKkoo---*\n//'.split('\n')


class MinimalRdbParserTests(GenericRdbTest):
    """Tests of MinimalRdbParser: returns (headerLines,sequence) tuples"""
    
    def test_empty(self):
        """MinimalRdbParser should return empty list from file w/o seqs"""
        self.assertEqual(list(MinimalRdbParser(self.empty)),[])
        self.assertEqual(list(MinimalRdbParser(self.nolabels, strict=False)),
                [])
        self.assertRaises(RecordError, list, MinimalRdbParser(self.nolabels))

    def test_only_labels(self):
        """MinimalRdbParser should return empty list from file w/o seqs"""
        #should fail if strict (the default)
        self.assertRaises(RecordError, list, 
            MinimalRdbParser(self.labels,strict=True))
        #if not strict, should skip the records
        self.assertEqual(list(MinimalRdbParser(self.labels, strict=False)), 
            [])

    def test_only_sequences(self):
        """MinimalRdbParser should return empty list form file w/o lables"""
        #should fail if strict (the default)
        self.assertRaises(RecordError, list,
            MinimalRdbParser(self.nolabels,strict=True))
        #if not strict, should skip the records
        self.assertEqual(list(MinimalRdbParser(self.nolabels, strict=False)), 
            [])

    def test_single(self):
        """MinimalRdbParser should read single record as (header,seq) tuple"""
        res = list(MinimalRdbParser(self.oneseq))
        self.assertEqual(len(res),1)
        first = res[0]
        self.assertEqual(first, (['seq:H.Sapiens'], 'AGUCAUCUAGAUHCAUHC'))
       
        res = list(MinimalRdbParser(self.multiline))
        self.assertEqual(len(res),1)
        first = res[0]
        self.assertEqual(first, (['seq:H.Sapiens'], 'AGUCAUUAGAUHCAUHC'))

    def test_multiple(self):
        """MinimalRdbParser should read multiple record correctly"""
        res = list(MinimalRdbParser(self.threeseq))
        self.assertEqual(len(res), 3)
        a, b, c = res
        self.assertEqual(a, (['seq:bac'], 'AGU'))
        self.assertEqual(b, (['seq:mit'], 'ACU'))
        self.assertEqual(c, (['seq:pla'], 'AAA'))

    def test_multiple_bad(self):
        """MinimalRdbParser should complain or skip bad records"""
        self.assertRaises(RecordError, list, MinimalRdbParser(self.twogood))
        f = list(MinimalRdbParser(self.twogood, strict=False))
        self.assertEqual(len(f), 2)
        a, b = f
        self.assertEqual(a, (['seq:mit'], 'ACU'))
        self.assertEqual(b, (['seq:pla'], 'AAA'))
        
    def test_strange(self):
        """MRP should handle strange char. according to constr. and strip off '*'"""
        f = list(MinimalRdbParser(self.strange))
        obs = f[0]
        exp = (['seq:bac'],'ACGUXxAaKkoo---')
        self.assertEqual(obs,exp)

class RdbParserTests(GenericRdbTest):
    """Tests for the RdbParser. Should return Sequence objects"""
    
    def test_empty(self):
        """RdbParser should return empty list from 'file' w/o labels"""
        self.assertEqual(list(RdbParser(self.empty)), [])
        self.assertEqual(list(RdbParser(self.nolabels, strict=False)),
            [])
        self.assertRaises(RecordError, list, RdbParser(self.nolabels))

    def test_only_labels(self):
        """RdbParser should return empty list from file w/o seqs"""
        #should fail if strict (the default)
        self.assertRaises(RecordError, list, 
            RdbParser(self.labels,strict=True))
        #if not strict, should skip the records
        self.assertEqual(list(RdbParser(self.labels, strict=False)), [])
        
    def test_only_sequences(self):
        """RdbParser should return empty list form file w/o lables"""
        #should fail if strict (the default)
        self.assertRaises(RecordError, list,
            RdbParser(self.nolabels,strict=True))
        #if not strict, should skip the records
        self.assertEqual(list(RdbParser(self.nolabels, strict=False)), 
            [])
    
    def test_single(self):
        """RdbParser should read single record as (header,seq) tuple"""
        res = list(RdbParser(self.oneseq))
        self.assertEqual(len(res),1)
        first = res[0]
        self.assertEqual(first, Sequence('AGUCAUCUAGAUHCAUHC'))
        self.assertEqual(first.Info, Info({'Species':'H.Sapiens'}))
       
        res = list(RdbParser(self.multiline))
        self.assertEqual(len(res),1)
        first = res[0]
        self.assertEqual(first, Sequence('AGUCAUUAGAUHCAUHC'))
        self.assertEqual(first.Info, Info({'Species':'H.Sapiens'}))

    def test_single_constructor(self):
        """RdbParser should use constructors if supplied"""
        f = list(RdbParser(self.oneseq, Dna))
        self.assertEqual(len(f), 1)
        a = f[0]
        self.assertEqual(a, 'AGTCATCTAGATHCATHC')
        self.assertEqual(a.Info, Info({'Species':'H.Sapiens'}))

        def alternativeConstr(header_lines):
            info = Info()
            for line in header_lines:
                all = line.strip().split(':',1)
                #strip out empty lines, lines without name, lines without colon
                if not all[0] or len(all) != 2: 
                    continue
                name = all[0].upper()
                value = all[1].strip().upper()
                info[name] = value
            return info
        
        f = list(RdbParser(self.oneseq, Dna, alternativeConstr))
        self.assertEqual(len(f), 1)
        a = f[0]
        self.assertEqual(a, 'AGTCATCTAGATHCATHC')
        self.assertEqual(a.Info, Info({'SEQ':'H.SAPIENS'}))

    def test_multiple_constructor_bad(self):
        """RdbParser should complain or skip bad records w/ constructor"""

        def dnastrict(x, **kwargs):
            try:
                return Dna(x, strict=True, **kwargs)
            except:
                raise RecordError, "Could not convert sequence"
       
        self.assertRaises(RecordError, list, RdbParser(self.oneX,dnastrict))
        f = list(RdbParser(self.oneX, dnastrict, strict=False))
        self.assertEqual(len(f), 2)
        a, b = f

        self.assertEqual(a, 'ACT')
        self.assertEqual(a.Info,Info({'Species':'mit'}))
        self.assertEqual(b, 'AAA')
        self.assertEqual(b.Info,Info({'Species':'pla'}))


if __name__ == '__main__':
    main()

