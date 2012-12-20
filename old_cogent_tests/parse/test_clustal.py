#!/usr/bin/env python
#file evo/parsers/test_clustal.py
"""Unit tests for the clustal parsers.

Revision History

Written 12/27/03 by Rob Knight

5/18/04 Rob Knight: added tests for ClustalParser that returns Alignment
object.
11/10/05 Sandra Smit: added line in test_is_clustal_seq_line to test for 
lines starting with 'MUSCLE'.
"""
from old_cogent.parse.clustal import LabelLineParser, is_clustal_seq_line, \
    last_space, delete_trailing_number, MinimalClustalParser, ClustalParser, \
    OldClustalParser
from old_cogent.base.sequence import Dna, Sequence, Protein
from old_cogent.parse.record import RecordError
from old_cogent.util.unit_test import TestCase, main
from old_cogent.base.align import Alignment

#Note: the data are all strings and hence immutable, so it's OK to define
#them here instead of in setUp and then subclassing everything from that
#base class. If the data were mutable, we'd need to take more precautions
#to avoid crossover between tests.

minimal = 'abc\tucag'
two = 'abc\tuuu\ndef\tccc\n\n    ***\n\ndef ggg\nabc\taaa\n'.split('\n')

real = """CLUSTAL W (1.82) multiple sequence alignment


abc             GCAUGCAUGCAUGAUCGUACGUCAGCAUGCUAGACUGCAUACGUACGUACGCAUGCAUCA 60
def             ------------------------------------------------------------
xyz             ------------------------------------------------------------


abc             GUCGAUACGUACGUCAGUCAGUACGUCAGCAUGCAUACGUACGUCGUACGUACGU-CGAC 119
def             -----------------------------------------CGCGAUGCAUGCAU-CGAU 18
xyz             -------------------------------------CAUGCAUCGUACGUACGCAUGAC 23
                                                         *    * * * *    **

abc             UGACUAGUCAGCUAGCAUCGAUCAGU 145
def             CGAUCAGUCAGUCGAU---------- 34
xyz             UGCUGCAUCA---------------- 33
                *     ***""".split('\n')

bad = ['dshfjsdfhdfsj','hfsdjksdfhjsdf']

space_labels = ['abc uca','def ggg ccc']

class clustalTests(TestCase):
    """Tests of top-level functions."""
    def test_is_clustal_seq_line(self):
        """is_clustal_seq_line should reject blanks and 'CLUSTAL'"""
        ic = is_clustal_seq_line
        assert ic('abc')
        assert ic('abc  def')
        assert not ic('CLUSTAL')
        assert not ic('CLUSTAL W fsdhicjkjsdk')
        assert not ic('  *   *')
        assert not ic(' abc def')
        assert not ic('MUSCLE (3.41) multiple sequence alignment')

    def test_last_space(self):
        """last_space should split on last whitespace"""
        self.assertEqual(last_space('a\t\t\t  b    c'), ['a b', 'c'])
        self.assertEqual(last_space('xyz'), ['xyz'])
        self.assertEqual(last_space('  a b'), ['a','b'])

    def test_delete_trailing_number(self):
        """delete_trailing_number should delete the trailing number if present"""
        dtn = delete_trailing_number
        self.assertEqual(dtn('abc'), 'abc')
        self.assertEqual(dtn('a b c'), 'a b c')
        self.assertEqual(dtn('a \t  b  \t  c'), 'a \t  b  \t  c')
        self.assertEqual(dtn('a b 3'), 'a b')
        self.assertEqual(dtn('a b c \t 345'), 'a b c')

class MinimalClustalParserTests(TestCase):
    """Tests of the MinimalClustalParser class"""
    def test_null(self):
        """MinimalClustalParser should return empty dict and list on null input"""
        result = MinimalClustalParser([])
        self.assertEqual(result, ({},[]))
        
    def test_minimal(self):
        """MinimalClustalParser should handle single-line input correctly"""
        result = MinimalClustalParser([minimal]) #expects seq of lines
        self.assertEqual(result, ({'abc':['ucag']}, ['abc']))

    def test_two(self):
        """MinimalClustalParser should handle two-sequence input correctly"""
        result = MinimalClustalParser(two)
        self.assertEqual(result, ({'abc':['uuu','aaa'],'def':['ccc','ggg']}, \
            ['abc', 'def']))

    def test_real(self):
        """MinimalClustalParser should handle real Clustal output"""
        data, labels = MinimalClustalParser(real)
        self.assertEqual(labels, ['abc', 'def', 'xyz'])
        self.assertEqual(data, {
            'abc':
            [   'GCAUGCAUGCAUGAUCGUACGUCAGCAUGCUAGACUGCAUACGUACGUACGCAUGCAUCA', 
                'GUCGAUACGUACGUCAGUCAGUACGUCAGCAUGCAUACGUACGUCGUACGUACGU-CGAC',
                'UGACUAGUCAGCUAGCAUCGAUCAGU'
            ],
            'def':
            [   '------------------------------------------------------------',
                '-----------------------------------------CGCGAUGCAUGCAU-CGAU',
                'CGAUCAGUCAGUCGAU----------'
            ],
            'xyz':
            [   '------------------------------------------------------------',
                '-------------------------------------CAUGCAUCGUACGUACGCAUGAC',
                'UGCUGCAUCA----------------'
            ]
            })

    def test_bad(self):
        """MinimalClustalParser should reject bad data if strict"""
        result = MinimalClustalParser(bad, strict=False)
        self.assertEqual(result, ({},[]))
        #should fail unless we turned strict processing off
        self.assertRaises(RecordError, MinimalClustalParser, bad)

    def test_space_labels(self):
        """MinimalClustalParser should tolerate spaces in labels"""
        result = MinimalClustalParser(space_labels)
        self.assertEqual(result, ({'abc':['uca'],'def ggg':['ccc']},\
            ['abc', 'def ggg']))

class OldClustalParserTests(TestCase):
    """Tests of the OldClustalParser class"""
    def test_null(self):
        """OldClustalParser should return empty alignment on null input"""
        result = OldClustalParser([])
        self.assertEqual(result, [])
        
    def test_minimal(self):
        """OldClustalParser should handle single-line input correctly"""
        result = OldClustalParser([minimal]) #expects seq of lines
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], 'ucag')
        self.assertEqual(result[0].Label, 'abc')

    def test_two(self):
        """OldClustalParser should handle two-sequence input correctly"""
        result = OldClustalParser(two)
        self.assertEqual(len(result), 2)    #make sure we got two sequences
        first, second = result
        self.assertEqual(first, 'uuuaaa')
        self.assertEqual(first.Label, 'abc')
        self.assertEqual(second, 'cccggg')
        self.assertEqual(second.Label, 'def')
        
    def test_real(self):
        """OldClustalParser should handle real Clustal output"""
        result = OldClustalParser(real)
        self.assertEqual(len(result), 3)    #make sure we got three sequences
        self.assertEqual([r.Label for r in result], ['abc', 'def', 'xyz'])
        self.assertEqual(result, [
            'GCAUGCAUGCAUGAUCGUACGUCAGCAUGCUAGACUGCAUACGUACGUACGCAUGCAUCA' + \
            'GUCGAUACGUACGUCAGUCAGUACGUCAGCAUGCAUACGUACGUCGUACGUACGU-CGAC' + \
            'UGACUAGUCAGCUAGCAUCGAUCAGU'
            ,
            '------------------------------------------------------------' + \
            '-----------------------------------------CGCGAUGCAUGCAU-CGAU' + \
            'CGAUCAGUCAGUCGAU----------'
            ,
            '------------------------------------------------------------' + \
            '-------------------------------------CAUGCAUCGUACGUACGCAUGAC' + \
            'UGCUGCAUCA----------------'
            ])

    def test_bad(self):
        """OldClustalParser should reject bad data if strict"""
        result = OldClustalParser(bad, strict=False)
        self.assertEqual(result, [])
        #should fail unless we turned strict processing off
        self.assertRaises(RecordError, OldClustalParser, bad)

    def test_space_labels(self):
        """OldClustalParser should tolerate spaces in labels"""
        result = OldClustalParser(space_labels)
        self.assertEqual(result, ['uca', 'ccc'])
        self.assertEqual([r.Label for r in result], ['abc', 'def ggg'])

class ClustalParserTests(TestCase):
    """Tests of the ClustalParser class"""
    def test_null(self):
        """ClustalParser should return empty alignment on null input"""
        result = ClustalParser([])
        self.assertEqual(result, Alignment())
        
    def test_minimal(self):
        """ClustalParser should handle single-line input correctly"""
        result = ClustalParser([minimal]) #expects seq of lines
        self.assertEqual(len(result), 1)
        self.assertEqual(result, {'abc':'ucag'})
        self.assertEqual(result['abc'].Label, 'abc')
        self.assertEqual(result.RowOrder, ['abc'])

    def test_two(self):
        """ClustalParser should handle two-sequence input correctly"""
        result = ClustalParser(two)
        self.assertEqual(len(result), 2)    #make sure we got two sequences
        self.assertEqual(result, {'abc':'uuuaaa','def':'cccggg'})
        self.assertEqual(result.RowOrder, ['abc','def'])
        self.assertEqual(result['abc'].Label, 'abc')
        
    def test_real(self):
        """ClustalParser should handle real Clustal output"""
        result = ClustalParser(real)
        self.assertEqual(len(result), 3)    #make sure we got three sequences
        self.assertEqual(result, {
        'abc':  \
            'GCAUGCAUGCAUGAUCGUACGUCAGCAUGCUAGACUGCAUACGUACGUACGCAUGCAUCA' + \
            'GUCGAUACGUACGUCAGUCAGUACGUCAGCAUGCAUACGUACGUCGUACGUACGU-CGAC' + \
            'UGACUAGUCAGCUAGCAUCGAUCAGU'    \
            ,
        'def':  \
            '------------------------------------------------------------' + \
            '-----------------------------------------CGCGAUGCAUGCAU-CGAU' + \
            'CGAUCAGUCAGUCGAU----------'    \
            ,
        'xyz':  \
            '------------------------------------------------------------' + \
            '-------------------------------------CAUGCAUCGUACGUACGCAUGAC' + \
            'UGCUGCAUCA----------------'    \
            })
        self.assertEqual(result.RowOrder, ['abc', 'def', 'xyz'])

    def test_bad(self):
        """ClustalParser should reject bad data if strict"""
        result = ClustalParser(bad, strict=False)
        self.assertEqual(result, {})
        #should fail unless we turned strict processing off
        self.assertRaises(RecordError, ClustalParser, bad)

    def test_space_labels(self):
        """ClustalParser should tolerate spaces in labels"""
        result = ClustalParser(space_labels)
        self.assertEqual(result, {'abc':'uca', 'def ggg':'ccc'})


if __name__ == '__main__':
    main()
