#!/usr/bin/env python
#file evo/parsers/test_fasta.py
"""Unit tests for the parsers.

Revision History

Written 11/12/03 by Rob Knight
"""
from old_cogent.parse.fasta import FastaParser, MinimalFastaParser, \
    NcbiFastaLabelParser, NcbiFastaParser
from old_cogent.base.sequence import Dna, Sequence, Protein
from old_cogent.parse.record import RecordError
from old_cogent.util.unit_test import TestCase, main

class GenericFastaTest(TestCase):
    """Setup data for all the various FASTA parsers."""
    def setUp(self):
        """standard files"""
        self.labels = '>abc\n>def\n>ghi\n'.split('\n')
        self.oneseq = '>abc\nUCAG\n'.split('\n')
        self.multiline = '>xyz\nUUUU\nCC\nAAAAA\nG'.split('\n')
        self.threeseq='>123\na\n> \t abc  \t \ncag\ngac\n>456\nc\ng'.split('\n')
        self.twogood='>123\n\n> \t abc  \t \ncag\ngac\n>456\nc\ng'.split('\n')
        self.oneX='>123\nX\n> \t abc  \t \ncag\ngac\n>456\nc\ng'.split('\n')
        self.nolabels = 'GJ>DSJGSJDF\nSFHKLDFS>jkfs\n'.split('\n')
        self.empty = []
 
class MinimalFastaParserTests(GenericFastaTest):
    """Tests of MinimalFastaParser: returns (label, seq) tuples."""
       
    def test_empty(self):
        """MinimalFastaParser should return empty list from 'file' w/o labels"""
        self.assertEqual(list(MinimalFastaParser(self.empty)), [])
        self.assertEqual(list(MinimalFastaParser(self.nolabels, strict=False)),
            [])
        self.assertRaises(RecordError, list, MinimalFastaParser(self.nolabels))

    def test_no_labels(self):
        """MinimalFastaParser should return empty list from file w/o seqs"""
        #should fail if strict (the default)
        self.assertRaises(RecordError, list, 
            MinimalFastaParser(self.labels,strict=True))
        #if not strict, should skip the records
        self.assertEqual(list(MinimalFastaParser(self.labels, strict=False)), 
            [])
        
    def test_single(self):
        """MinimalFastaParser should read single record as (label, seq) tuple"""
        f = list(MinimalFastaParser(self.oneseq))
        self.assertEqual(len(f), 1)
        a = f[0]
        self.assertEqual(a, ('abc', 'UCAG'))

        f = list(MinimalFastaParser(self.multiline))
        self.assertEqual(len(f), 1)
        a = f[0]
        self.assertEqual(a, ('xyz', 'UUUUCCAAAAAG'))

    def test_multiple(self):
        """MinimalFastaParser should read multiline records correctly"""
        f = list(MinimalFastaParser(self.threeseq))
        self.assertEqual(len(f), 3)
        a, b, c = f
        self.assertEqual(a, ('123', 'a'))
        self.assertEqual(b, ('abc', 'caggac'))
        self.assertEqual(c, ('456', 'cg'))

    def test_multiple_bad(self):
        """MinimalFastaParser should complain or skip bad records"""
        self.assertRaises(RecordError, list, MinimalFastaParser(self.twogood))
        f = list(MinimalFastaParser(self.twogood, strict=False))
        self.assertEqual(len(f), 2)
        a, b = f
        self.assertEqual(a, ('abc', 'caggac'))
        self.assertEqual(b, ('456', 'cg'))

class FastaParserTests(GenericFastaTest):
    """Tests of FastaParser: returns sequence objects."""
       
    def test_empty(self):
        """FastaParser should return empty list from 'file' w/o labels"""
        self.assertEqual(list(FastaParser(self.empty)), [])
        self.assertEqual(list(FastaParser(self.nolabels, strict=False)),
            [])
        self.assertRaises(RecordError, list, FastaParser(self.nolabels))

    def test_no_labels(self):
        """FastaParser should return empty list from file w/o seqs"""
        #should fail if strict (the default)
        self.assertRaises(RecordError, list, 
            FastaParser(self.labels,strict=True))
        #if not strict, should skip the records
        self.assertEqual(list(FastaParser(self.labels, strict=False)), [])
        
    def test_single(self):
        """FastaParser should read single record as seq object"""
        f = list(FastaParser(self.oneseq))
        self.assertEqual(len(f), 1)
        a = f[0]
        self.assertEqual(a, 'UCAG')
        self.assertEqual(a.Label, 'abc')

        f = list(FastaParser(self.multiline))
        self.assertEqual(len(f), 1)
        a = f[0]
        self.assertEqual(a, 'UUUUCCAAAAAG')
        self.assertEqual(a.Label, 'xyz')

    def test_single_constructor(self):
        """FastaParser should use constructors if supplied"""
        f = list(FastaParser(self.oneseq, Dna))
        self.assertEqual(len(f), 1)
        a = f[0]
        self.assertEqual(a, 'TCAG')
        self.assertEqual(a.Label, 'abc')

        def upper_abc(x):
            return {'ABC': x.upper()}

        f = list(FastaParser(self.multiline, Dna, upper_abc))
        self.assertEqual(len(f), 1)
        a = f[0]
        self.assertEqual(a, 'TTTTCCAAAAAG')
        self.assertEqual(a.Label, None)
        self.assertEqual(a.ABC, 'XYZ')

    def test_multiple(self):
        """FastaParser should read multiline records correctly"""
        f = list(FastaParser(self.threeseq))
        self.assertEqual(len(f), 3)
        for i in f:
            assert isinstance(i, Sequence)
        a, b, c = f
        self.assertEqual((a.Label, a), ('123', 'a'))
        self.assertEqual((b.Label, b), ('abc', 'caggac'))
        self.assertEqual((c.Label, c), ('456', 'cg'))

    def test_multiple_bad(self):
        """Parser should complain or skip bad records"""
        self.assertRaises(RecordError, list, FastaParser(self.twogood))
        f = list(FastaParser(self.twogood, strict=False))
        self.assertEqual(len(f), 2)
        a, b = f
        self.assertEqual((a.Label, a), ('abc', 'caggac'))
        self.assertEqual((b.Label, b), ('456', 'cg'))

    def test_multiple_constructor_bad(self):
        """Parser should complain or skip bad records w/ constructor"""

        def dnastrict(x, **kwargs):
            try:
                return Dna(x, strict=True, **kwargs)
            except:
                raise RecordError, "Could not convert sequence"
        
        self.assertRaises(RecordError, list, FastaParser(self.oneX, dnastrict))
        f = list(FastaParser(self.oneX, dnastrict, strict=False))
        self.assertEqual(len(f), 2)
        a, b = f
        self.assertEqual((a.Label, a), ('abc', 'caggac'))
        self.assertEqual((b.Label, b), ('456', 'cg'))

class NcbiFastaLabelParserTests(TestCase):
    """Tests of the label line parser for NCBI's FASTA identifiers."""
    def test_init(self):
        """Labels from genpept.fsa should work as expected"""
        i = NcbiFastaLabelParser(
            '>gi|37549575|ref|XP_352503.1| similar to EST gb|ATTS1136')
        self.assertEqual(i.GI, ['37549575'])
        self.assertEqual(i.RefSeq, ['XP_352503.1'])
        self.assertEqual(i.Description, 'similar to EST gb|ATTS1136')

        i = NcbiFastaLabelParser(
            '>gi|32398734|emb|CAD98694.1| (BX538350) dbj|baa86974.1, possible')
        self.assertEqual(i.GI, ['32398734'])
        self.assertEqual(i.RefSeq, [])
        self.assertEqual(i.EMBL, ['CAD98694.1'])
        self.assertEqual(i.Description, '(BX538350) dbj|baa86974.1, possible')

        i = NcbiFastaLabelParser(
            '>gi|10177064|dbj|BAB10506.1| (AB005238)   ')
        self.assertEqual(i.GI, ['10177064'])
        self.assertEqual(i.DDBJ, ['BAB10506.1'])
        self.assertEqual(i.Description, '(AB005238)')

class NcbiFastaParserTests(TestCase):
    """Tests of the NcbiFastaParser."""
    def setUp(self):
        """Define a few standard files"""
        self.peptide = [
'>gi|10047090|ref|NP_055147.1| small muscle protein, X-linked [Homo sapiens]',
'MNMSKQPVSNVRAIQANINIPMGAFRPGAGQPPRRKECTPEVEEGVPPTSDEEKKPIPGAKKLPGPAVNL',
'SEIQNIKSELKYVPKAEQ',
'>gi|10047092|ref|NP_037391.1| neuronal protein [Homo sapiens]',
'MANRGPSYGLSREVQEKIEQKYDADLENKLVDWIILQCAEDIEHPPPGRAHFQKWLMDGTVLCKLINSLY',
'PPGQEPIPKISESKMAFKQMEQISQFLKAAETYGVRTTDIFQTVDLWEGKDMAAVQRTLMALGSVAVTKD'
]
        self.nasty = [
'  ',                               #0  ignore leading blank line
'>gi|abc|ref|def|',                 #1  no description -- ok
'UCAG',                             #2  single line of sequence
'#comment',                         #3  comment -- skip
'  \t   ',                          #4  ignore blank line between records
'>gi|xyz|gb|qwe|  \tdescr   \t\t',  #5  desciption has whitespace
'UUUU',                             #6  two lines of sequence
'CCCC',                             #7  
'>gi|bad|ref|nonsense',             #8  missing last pipe -- error
'ACU',                              #9  
'>gi|bad|description',              #10 not enough fields -- error       
'AAA',                              #11
'>gi|bad|ref|stuff|label',          #12
'XYZ',                              #13 bad sequence -- error
'>gi|bad|gb|ignore| description',   #14 label without sequence -- error
'>  gi  |  123  | dbj  | 456 | desc|with|pipes| ',#15 label w/ whitespace -- OK
'ucag',                             #16
'  \t  ',                           #17 ignore blank line inside record
'UCAG',                             #18
'tgac',                             #19 lowercase should be OK
'# comment',                        #20 comment -- skip
'NNNN',                             #21 degenerates should be OK
'   ',                              #22 ignore trailing blank line
]
        self.empty = []
        self.no_label = ['ucag']

    def test_empty(self):
        """NcbiFastaParser should accept empty input"""
        self.assertEqual(list(NcbiFastaParser(self.empty)), [])
        self.assertEqual(list(NcbiFastaParser(self.empty, Protein)), [])

    def test_normal(self):
        """NcbiFastaParser should accept normal record if loose or strict"""
        f = list(NcbiFastaParser(self.peptide, Protein))
        self.assertEqual(len(f), 2)
        a, b = f
        self.assertEqual(a, 'MNMSKQPVSNVRAIQANINIPMGAFRPGAGQPPRRKECTPEVEEGVPPTSDEEKKPIPGAKKLPGPAVNLSEIQNIKSELKYVPKAEQ')
        self.assertEqual(a.GI, ['10047090'])
        self.assertEqual(a.RefSeq, ['NP_055147.1'])
        self.assertEqual(a.DDBJ, [])
        self.assertEqual(a.Description, 
            'small muscle protein, X-linked [Homo sapiens]')

        self.assertEqual(b, 'MANRGPSYGLSREVQEKIEQKYDADLENKLVDWIILQCAEDIEHPPPGRAHFQKWLMDGTVLCKLINSLYPPGQEPIPKISESKMAFKQMEQISQFLKAAETYGVRTTDIFQTVDLWEGKDMAAVQRTLMALGSVAVTKD')
        self.assertEqual(b.GI, ['10047092'])
        self.assertEqual(b.RefSeq, ['NP_037391.1'])
        self.assertEqual(b.Description, 'neuronal protein [Homo sapiens]')

    def test_dodgy(self):
        """NcbiFastaParser should raise error on bad records if strict"""
        #if strict, starting anywhere in the first 15 lines should cause errors
        for i in range(15):
            self.assertRaises(RecordError,list,NcbiFastaParser(self.nasty[i:]))
        #...but the 16th is OK.
        r = list(NcbiFastaParser(self.nasty[15:]))[0]
        self.assertEqual(r, 'ucagUCAGtgacNNNN')
        #test that we get what we expect if not strict
        r = list(NcbiFastaParser(self.nasty, Sequence, strict=False))
        self.assertEqual(len(r), 4)
        a, b, c, d = r
        self.assertEqual((a, a.GI, a.RefSeq, a.Description), 
            ('UCAG', ['abc'], ['def'], ''))
        self.assertEqual((b, b.GI, b.GenBank, b.Description),
            ('UUUUCCCC', ['xyz'], ['qwe'], 'descr'))
        self.assertEqual((c, c.GI, c.RefSeq, c.Description),
            ('XYZ', ['bad'], ['stuff'], 'label'))
        self.assertEqual((d, d.GI, d.DDBJ, d.Description),
            ('ucagUCAGtgacNNNN', ['123'], ['456'], 'desc|with|pipes|'))
        #...and when we explicitly supply a constructor
        r = list(NcbiFastaParser(self.nasty, Dna, strict=False))
        self.assertEqual(len(r), 4)
        a, b, c, d = r     
        self.assertEqual((a, a.GI, a.RefSeq, a.Description), 
            ('TCAG', ['abc'], ['def'], ''))
        self.assertEqual((b, b.GI, b.GenBank, b.Description),
            ('TTTTCCCC', ['xyz'], ['qwe'], 'descr'))
        self.assertEqual((c, c.GI, c.RefSeq, c.Description),
            ('Y', ['bad'], ['stuff'], 'label')) #bad chars stripped
        self.assertEqual((d, d.GI, d.DDBJ, d.Description),
            ('tcagTCAGtgacNNNN', ['123'], ['456'], 'desc|with|pipes|'))
        #...including one that will raise an exception on bad sequences
        def dnastrict(x, **kwargs):
            try:
                return Dna(x, strict=True, **kwargs)
            except:
                raise RecordError, "Could not convert sequence"
        r = list(NcbiFastaParser(self.nasty, dnastrict, strict=False))
        self.assertEqual(len(r), 3)
        a, b, d = r     #c from above is excluded since can't make seq
        self.assertEqual((a, a.GI, a.RefSeq, a.Description), 
            ('TCAG', ['abc'], ['def'], ''))
        self.assertEqual((b, b.GI, b.GenBank, b.Description),
            ('TTTTCCCC', ['xyz'], ['qwe'], 'descr'))
        self.assertEqual((d, d.GI, d.DDBJ, d.Description),
            ('tcagTCAGtgacNNNN', ['123'], ['456'], 'desc|with|pipes|'))
        
if __name__ == '__main__':
    main()
