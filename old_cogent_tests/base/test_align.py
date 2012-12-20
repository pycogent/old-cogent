#!/usr/bin/env python
#file evo/alignments/test_align.py

"""Test code for sequence and structure alignments in evo.alignment.util

Revision History

Written week of 3/29/04 for PyEvolve by Rob Knight.

4/9/04 Rob Knight: Check that Alignment preserves order on init from list.

5/4/04 Rob Knight: added tests for negation. Updated method names.

6/4/04 Jeremy Widmann: added tests for IUPACConsensus, isRagged, and
scoreMatrix.  Added additional Alignments in setup for tests. Added
test_columnFrequencies, test_columnProbs, test_majorityConsensus,
and test_uncertainties from test_bayes_util.py.

2/7/05 Rob Knight: renamed file and moved to correct place.

1/30/06: Cathy Lozuopone: added tests for omitGapCols, make_gap_filter, and
to_fasta and updated tests for omitGapCols

1/30/06 Jeremy Widmann: added tests for getIntMap
"""

from old_cogent.util.unit_test import TestCase, main
from old_cogent.base.align import Alignment, make_gap_filter
from old_cogent.base.sequence import Rna, RnaSequence, frac_same
from old_cogent.base.stats import Freqs, Numbers
from old_cogent.base.alphabet import *
from old_cogent.struct.rna2d import ViennaStructure

class AlignmentTests(TestCase):
    """Tests of the Alignment object."""
    def setUp(self):
        """Define some standard Alignment objects."""
        self.empty = Alignment({})
        self.one_seq = Alignment({'a':'aaaaa'})
        self.ragged = Alignment({'a':'aaaaaa', 'b':'aaa', 'c':'aaaa'})
        self.identical = Alignment({'a':'aaaa','b':'aaaa'})
        self.gaps = Alignment({'a':'aaaaaaa','b':'a--a-aa', 'c':'aa-----'})
        self.gaps_rna = Alignment({'a':Rna('aaaaaaa'), 'b':Rna('a--a-aa'), \
            'c':Rna('aa-----')})
        self.unordered = Alignment({'a':'aaaaa','b':'bbbbb'})
        self.ordered1 = Alignment({'a':'aaaaa','b':'bbbbb'}, RowOrder=['a','b'])
        self.ordered2 = Alignment({'a':'aaaaa','b':'bbbbb'}, RowOrder=['b','a'])
        self.mixed = Alignment({'a':'abcde', 'b':'lmnop'})
        self.end_gaps = Alignment({'a':'--a-bc-', 'b':'-cb-a--', 'c':'--d-ef-'})
        self.many = Alignment({
            'a': Rna('ucagucaguu'),
            'b': Rna('uccgucaauu'),
            'c': Rna('accaucaguc'),
            'd': Rna('ucaaucgguu'),
            'e': Rna('uugguugggu'),
            'f': Rna('ccgggcggcc'),
            'g': Rna('ucaaccggaa'),
            })
        #Additional Alignments for tests added 6/4/04 by Jeremy Widmann
        self.integers = Alignment([[1,2,3,4,5],[1,1,1,1,1],[5,4,3,2,1]])
        self.sequences = Alignment(map(RnaSequence, ['UCAG', 'UCAG', 'UCAG']))
        self.structures = Alignment(map(ViennaStructure, 
                                ['(())..', '......', '(....)']), None, str)
        self.labeled = Alignment(['abc', 'def'], ['1st', '2nd'])
        #Additional Alignment for tests added 1/30/06 by Cathy Lozupone
        self.omitRowsTemplate_aln = Alignment({
            's1':Rna('UC-----CU---C'),
            's2':Rna('UC------U---C'),
            's3':Rna('UUCCUUCUU-UUC'),
            's4':Rna('UU-UUUU-UUUUC'),
            's5':Rna('-------------')
            })
    
    def test_init_dict(self):
        """Alignment init from dict should work as expected"""
        d = {'a':'aaaaa', 'b':'bbbbb'}
        a = Alignment(d)
        self.assertEqual(a, d)
        self.assertEqual(a.items(), d.items())

    def test_init_seq(self):
        """Alignment init from list of sequences should use indices as keys"""
        seqs = ['aaaaa', 'bbbbb', 'ccccc']
        a = Alignment(seqs)
        self.assertEqual(len(a), 3)
        self.assertEqual(a[0], 'aaaaa')
        self.assertEqual(a[1], 'bbbbb')
        self.assertEqual(a[2], 'ccccc')
        self.assertEqual(a.RowOrder, [0,1,2])
        self.assertEqual(list(a.Rows), ['aaaaa','bbbbb','ccccc'])

    def test_init_pairs(self):
        """Alignment init from list of (key,val) pairs should work correctly"""
        seqs = [['x', 'xxx'], ['b','bbb'], ['c','ccc']]
        a = Alignment(seqs)
        self.assertEqual(len(a), 3)
        self.assertEqual(a['x'], 'xxx')
        self.assertEqual(a['b'], 'bbb')
        self.assertEqual(a['c'], 'ccc')
        self.assertEqual(a.RowOrder, ['x','b','c'])
        self.assertEqual(list(a.Rows), ['xxx','bbb','ccc'])

    def test_init_ordered(self):
        """Alignment should iterate over rows correctly even if ordered"""
        first = self.ordered1
        sec = self.ordered2
        un = self.unordered

        self.assertEqual(first.RowOrder, ['a','b'])
        self.assertEqual(sec.RowOrder, ['b', 'a'])
        self.assertEqual(un.RowOrder, un.keys())

        first_list = list(first.Rows)
        sec_list = list(sec.Rows)
        un_list = list(un.Rows)

        self.assertEqual(first_list, ['aaaaa','bbbbb'])
        self.assertEqual(sec_list, ['bbbbb','aaaaa'])
    
        #check that the unordered seq matches one of the lists
        assert (un_list == first_list) or (un_list == sec_list)
        self.assertNotEqual(first_list, sec_list)

    def test_SeqLen_get(self):
        """Alignment SeqLen should return length of longest seq"""
        self.assertEqual(self.empty.SeqLen, 0)
        self.assertEqual(self.one_seq.SeqLen, 5)
        self.assertEqual(self.ragged.SeqLen, 6)
        self.assertEqual(self.identical.SeqLen, 4)
        self.assertEqual(self.gaps.SeqLen, 7)

    def test_SeqLen_set(self):
        """Alignment SeqLen assignment should pad or truncate sequences"""
        #if there are no sequences, SeqLen will always be 0
        a = self.empty
        a.SeqLen = 5
        self.assertEqual(a.SeqLen, 0)

        a = self.one_seq
        a.SeqLen = 10
        self.assertEqual(a['a'], 'aaaaa-----')
        a.SeqLen = 2
        self.assertEqual(a['a'], 'aa')

        a = self.ragged
        a.SeqLen = None
        self.assertEqual(a, {'a':'aaaaaa', 'b':'aaa---', 'c':'aaaa--'})
        a.SeqLen = 8
        self.assertEqual(a, {'a':'aaaaaa--','b':'aaa-----','c':'aaaa----'})
        a.SeqLen = 2
        self.assertEqual(a, {'a':'aa','b':'aa','c':'aa'})

        a.DefaultGap = '~'
        a.SeqLen = 4
        self.assertEqual(a, {'a':'aa~~','b':'aa~~','c':'aa~~'})

    def test_Rows(self):
        """Alignment Rows property should return rows in correct order."""
        first = self.ordered1
        sec = self.ordered2
        un = self.unordered

        first_list = list(first.Rows)
        sec_list = list(sec.Rows)
        un_list = list(un.Rows)

        self.assertEqual(first_list, ['aaaaa','bbbbb'])
        self.assertEqual(sec_list, ['bbbbb','aaaaa'])
    
        #check that the unordered seq matches one of the lists
        assert (un_list == first_list) or (un_list == sec_list)
        self.assertNotEqual(first_list, sec_list)

        #should work on empty alignment
        self.assertEqual(list(self.empty.Rows), [])

        #should work on ragged alignment
        self.ragged.RowOrder = 'bac'
        self.assertEqual(list(self.ragged.Rows), ['aaa', 'aaaaaa', 'aaaa'])
        
    def test_iterRows(self):
        """Alignment iterRows() method should support reordering of rows"""
        self.assertEqual(list(self.empty.iterRows()), [])

        self.ragged.RowOrder = ['a','b','c']
        rows = list(self.ragged.iterRows())
        self.assertEqual(rows, ['aaaaaa', 'aaa', 'aaaa'])
        rows = list(self.ragged.iterRows(row_order=['b','a','a']))
        self.assertEqual(rows, ['aaa', 'aaaaaa', 'aaaaaa'])
        assert rows[1] is rows[2]
        assert rows[0] is self.ragged['b']
        
    def test_Cols(self):
        """Alignment Cols property should iterate over columns, using self.RowOrder"""
        r = self.ragged
        self.assertRaises(IndexError, list, r.Cols)
        r.SeqLen = None
        r.RowOrder = ['a','b','c']
        self.assertEqual(list(r.Cols), map(list, \
            ['aaa','aaa','aaa', 'a-a', 'a--', 'a--']))
        #should work on empty alignment
        self.assertEqual(list(self.empty.Cols), [])
        
    def test_iterCols(self):
        """Alignment iterCols() method should support reordering of cols"""
        r = self.ragged
        self.assertRaises(IndexError, list, r.iterCols(col_order=[5,1,3]))
        r.RowOrder = 'cb'
        r.SeqLen = None
        self.assertEqual(list(r.iterCols(col_order=[5,1,3])),\
            map(list,['--','aa','a-']))

        r.RowOrder = ['a','b','c']
        cols = list(self.ragged.iterCols())
        self.assertEqual(cols, map(list, ['aaa','aaa','aaa','a-a','a--','a--']))
        
    def test_Items(self):
        """Alignment Items should iterate over items in specified order."""
        #should work on empty alignment
        self.assertEqual(list(self.empty.Items), [])
        #should work if one row
        self.assertEqual(list(self.one_seq.Items), ['a']*5)
        #should work on ragged alignment
        self.assertEqual(list(self.ragged.Items), ['a']*13)
        #should take order into account
        self.assertEqual(list(self.ordered1.Items), ['a']*5 + ['b']*5)
        self.assertEqual(list(self.ordered2.Items), ['b']*5 + ['a']*5)
        
    def test_iterItems(self):
        """Alignment iterItems() should iterate over items in correct order"""
        #should work on empty alignment
        self.assertEqual(list(self.empty.iterItems()), [])
        #should work if one row
        self.assertEqual(list(self.one_seq.iterItems()), ['a']*5)
        #should work on ragged alignment
        self.assertEqual(list(self.ragged.iterItems()), ['a']*13)
        #should take order into account
        self.assertEqual(list(self.ordered1.iterItems()), ['a']*5 + ['b']*5)
        self.assertEqual(list(self.ordered2.iterItems()), ['b']*5 + ['a']*5)
        #should allow row and/or col specification
        self.assertRaises(IndexError, list, self.ragged.iterItems(\
            row_order=['c','b'], col_order=[5,1,3]))
        self.ragged.SeqLen = None
        self.assertEqual(list(self.ragged.iterItems(row_order=['c','b'], \
            col_order=[5,1,3])), list('-aa-a-'))
        #should not interfere with superclass iteritems()
        i = list(self.ragged.iteritems()) #remember, we padded self.ragged above
        i.sort()
        self.assertEqual(i, [('a','aaaaaa'),('b','aaa---'),('c','aaaa--')])
    
    def test_getRows(self):
        """Alignment getRows should return new Alignment with selected rows."""
        self.assertRaises(KeyError, self.empty.getRows, ['a'])
        a = self.ragged.getRows('bc')
        assert isinstance(a, Alignment)
        self.assertEqual(a, {'b':'aaa','c':'aaaa'})
        #should be able to negate
        a = self.ragged.getRows('bc', negate=True)
        self.assertEqual(a, {'a':'aaaaaa'})

    def test_getRowIndices(self):
        """Alignment getRowIndices should return names of rows where f(row) is True"""
        is_long = lambda x: len(x) > 10
        is_med = lambda x: len(x) > 3
        is_any = lambda x: len(x) > 0
        self.assertEqual(self.ragged.getRowIndices(is_long), [])
        self.ragged.RowOrder = 'cba'
        self.assertEqual(self.ragged.getRowIndices(is_med), ['c','a'])
        self.ragged.RowOrder = 'abc'
        self.assertEqual(self.ragged.getRowIndices(is_med), ['a','c'])
        self.assertEqual(self.ragged.getRowIndices(is_any), ['a','b','c'])
        #should be able to negate
        self.assertEqual(self.ragged.getRowIndices(is_med, negate=True), ['b'])
        self.assertEqual(self.ragged.getRowIndices(is_any, negate=True), [])

    def test_getRowsIf(self):
        """Alignment getRowsIf should return rows where f(row) is True"""
        is_long = lambda x: len(x) > 10
        is_med = lambda x: len(x) > 3
        is_any = lambda x: len(x) > 0
        self.assertEqual(self.ragged.getRowsIf(is_long), {})
        self.ragged.RowOrder = 'cba'
        self.assertEqual(self.ragged.getRowsIf(is_med), \
            {'c':'aaaa','a':'aaaaaa'})
        self.ragged.RowOrder = None
        self.assertEqual(self.ragged.getRowsIf(is_med), \
            {'c':'aaaa','a':'aaaaaa'})
        self.assertEqual(self.ragged.getRowsIf(is_any), self.ragged)
        assert isinstance(self.ragged.getRowsIf(is_med), Alignment)
        #should be able to negate
        self.assertEqual(self.ragged.getRowsIf(is_med, negate=True), \
            {'b':'aaa'})

    def test_getCols(self):
        """Alignment getCols should return new alignment w/ specified columns"""
        self.assertEqual(self.empty.getCols([0]), {})
        
        self.assertEqual(self.gaps.getCols([5,4,0], row_constructor=''.join), \
            {'a':'aaa','b':'a-a','c':'--a'})
        assert isinstance(self.gaps.getCols([0]), Alignment)
        #should be able to negate
        self.assertEqual(self.gaps.getCols([5,4,0], negate=True, \
            row_constructor=''.join),
            {'a':'aaaa','b':'--aa','c':'a---'})

    def test_getColIndices(self):
        """Alignment getColIndices should return names of cols where f(col) is True"""
        gap_1st = lambda x: x[0] == '-'
        gap_2nd = lambda x: x[1] == '-'
        gap_3rd = lambda x: x[2] == '-'
        is_list =  lambda x: isinstance(x, list)
        self.gaps.RowOrder = 'abc'

        self.assertEqual(self.gaps.getColIndices(gap_1st), [])
        self.assertEqual(self.gaps.getColIndices(gap_2nd), [1,2,4])
        self.assertEqual(self.gaps.getColIndices(gap_3rd), [2,3,4,5,6])
        self.assertEqual(self.gaps.getColIndices(is_list), [0,1,2,3,4,5,6])
        #should be able to negate
        self.assertEqual(self.gaps.getColIndices(gap_2nd, negate=True), \
            [0,3,5,6])
        self.assertEqual(self.gaps.getColIndices(gap_1st, negate=True), \
            [0,1,2,3,4,5,6])
        self.assertEqual(self.gaps.getColIndices(is_list, negate=True), [])

    def test_getColsIf(self):
        """Alignment getColsIf should return cols where f(col) is True"""
        gap_1st = lambda x: x[0] == '-'
        gap_2nd = lambda x: x[1] == '-'
        gap_3rd = lambda x: x[2] == '-'
        is_list =  lambda x: isinstance(x, list)
        self.gaps.RowOrder = 'abc'

        self.assertEqual(self.gaps.getColsIf(gap_1st,row_constructor=''.join),\
            {'a':'', 'b':'', 'c':''})
        self.assertEqual(self.gaps.getColsIf(gap_2nd,row_constructor=''.join),\
            {'a':'aaa', 'b':'---', 'c':'a--'})
        self.assertEqual(self.gaps.getColsIf(gap_3rd,row_constructor=''.join),\
            {'a':'aaaaa', 'b':'-a-aa', 'c':'-----'})
        self.assertEqual(self.gaps.getColsIf(is_list,row_constructor=''.join),\
            self.gaps)

        assert isinstance(self.gaps.getColsIf(gap_1st), Alignment)
        #should be able to negate
        self.assertEqual(self.gaps.getColsIf(gap_1st, row_constructor=''.join,\
            negate=True), self.gaps)
        self.assertEqual(self.gaps.getColsIf(gap_2nd, row_constructor=''.join,\
            negate=True), {'a':'aaaa','b':'aaaa','c':'a---'})
        self.assertEqual(self.gaps.getColsIf(gap_3rd, row_constructor=''.join,\
            negate=True), {'a':'aa','b':'a-','c':'aa'})

    def test_getItems(self):
        """Alignment getItems should return list of items from k,v pairs"""
        self.assertEqual(self.mixed.getItems([('a',3),('b',4),('a',0)]), \
            ['d','p','a'])
        self.assertRaises(KeyError, self.mixed.getItems, [('x','y')])
        self.assertRaises(IndexError, self.mixed.getItems, [('a',1000)])
        #should be able to negate -- note that results will have rows in
        #arbitrary order
        self.assertEqualItems(self.mixed.getItems([('a',3),('b',4),('a',0)], \
            negate=True), ['b','c','e','l','m','n','o'])

    def test_getItemIndices(self):
        """Alignment getItemIndices should return coordinates of matching items"""
        is_vowel = lambda x: x in 'aeiou'
        self.mixed.RowOrder = 'ba'     #specify reverse order
        self.assertEqual(self.mixed.getItemIndices(is_vowel), \
            [('b',3),('a',0),('a',4)])
        not_vowel = lambda x: not is_vowel(x)
        self.assertEqual(self.ragged.getItemIndices(not_vowel), [])
        #should be able to negate
        self.assertEqualItems(self.mixed.getItemIndices(is_vowel, negate=True),\
            [('a',1),('a',2),('a',3),('b',0),('b',1),('b',2),('b',4)])

    def test_getItemsIf(self):
        """Alignment getItemsIf should return matching items"""
        is_vowel = lambda x: x in 'aeiou'
        self.mixed.RowOrder = 'ba'
        self.assertEqual(self.mixed.getItemsIf(is_vowel), ['o','a','e'])
        self.assertEqual(self.empty.getItemsIf(is_vowel), [])
        self.assertEqual(self.one_seq.getItemsIf(is_vowel), list('aaaaa'))
        #should be able to negate
        self.assertEqualItems(self.mixed.getItemsIf(is_vowel, negate=True), \
            list('bcdlmnp'))

    def test_getSimilar(self):
        """Alignment getSimilar should get all sequences close to target seq"""
        aln = self.many
        x = Rna('gggggggggg')
        y = Rna('----------')
        #test min and max similarity ranges
        result = aln.getSimilar(aln['a'],min_similarity=0.4,max_similarity=0.7)
        for seq in 'cefg':
            assert seq in result
            assert result[seq] == aln[seq]
        self.assertEqual(len(result), 4)
        
        result = aln.getSimilar(aln['a'],min_similarity=0.95,max_similarity=1)
        for seq in 'a':
            assert seq in result
            assert result[seq] == aln[seq]
        self.assertEqual(len(result), 1)

        result = aln.getSimilar(aln['a'], min_similarity=0.75, \
            max_similarity=0.85)
        for seq in 'bd':
            assert seq in result
            assert result[seq] == aln[seq]
        self.assertEqual(len(result), 2)

        result = aln.getSimilar(aln['a'],min_similarity=0,max_similarity=0.2)
        self.assertEqual(len(result), 0)

        #test some sequence transformations
        transform = lambda s: s[1:4]
        result = aln.getSimilar(aln['a'], min_similarity=0.5, \
            transform=transform)
        for seq in 'abdfg':
            assert seq in result
            assert result[seq] == aln[seq]
        self.assertEqual(len(result), 5)

        transform = lambda s: s[-3:]
        result = aln.getSimilar(aln['a'], min_similarity=0.5, \
            transform=transform)
        for seq in 'abcde':
            assert seq in result
            assert result[seq] == aln[seq]
        self.assertEqual(len(result), 5)

        #test a different distance metric
        metric = lambda x, y: x.count('g') + y.count('g')
        result = aln.getSimilar(aln['a'], min_similarity=5, max_similarity=10, \
            metric=metric)
        for seq in 'ef':
            assert seq in result
            assert result[seq] == aln[seq]
        self.assertEqual(len(result), 2)

        #test the combination of a transform and a distance metric
        aln = Alignment(dict(enumerate(map(Rna, ['aA-ac','A-aAC','aa-aa']))))
        transform = lambda s: Rna(s.upper())
        metric = RnaSequence.fracSameNonGaps
        #first, do it without the transformation
        result = aln.getSimilar(aln[0], min_similarity=0.5, metric=metric)
        for seq in [0,2]:
            assert seq in result
            assert result[seq] == aln[seq]
        self.assertEqual(len(result), 2)
        
        result = aln.getSimilar(aln[0], min_similarity=0.8, metric=metric)
        for seq in [0]:
            assert seq in result
            assert result[seq] == aln[seq]
        self.assertEqual(len(result), 1)
        #then, verify that the transform changes the results         
        result = aln.getSimilar(aln[0], min_similarity=0.5, metric=metric, \
            transform=transform)
        for seq in [0,1,2]:
            assert seq in result
            assert result[seq] == aln[seq]
        self.assertEqual(len(result), 3)
        
        result = aln.getSimilar(aln[0], min_similarity=0.8, metric=metric, \
            transform=transform)
        for seq in [0,1]:
            assert seq in result
            assert result[seq] == aln[seq]
        self.assertEqual(len(result), 2)
         
    def test_omitGapCols(self):
        """Alignment omitGapCols should return alignment w/o columns of gaps"""
        aln = self.end_gaps
        
        #first, check behavior when we're just acting on the cols (and not
        #trying to delete the naughty rows).
        
        #default should strip out cols that are 100% gaps
        self.assertEqual(aln.omitGapCols(row_constructor=''.join), \
            {'a':'-abc', 'b':'cba-', 'c':'-def'})
        #if allowed_gap_frac is 1, shouldn't delete anything
        self.assertEqual(aln.omitGapCols(1, row_constructor=''.join), \
            {'a':'--a-bc-', 'b':'-cb-a--', 'c':'--d-ef-'})
        #if allowed_gap_frac is 0, should strip out any cols containing gaps
        self.assertEqual(aln.omitGapCols(0, row_constructor=''.join), \
            {'a':'ab', 'b':'ba', 'c':'de'})
        #intermediate numbers should work as expected
        self.assertEqual(aln.omitGapCols(0.4, row_constructor=''.join), \
            {'a':'abc', 'b':'ba-', 'c':'def'})
        self.assertEqual(aln.omitGapCols(0.7, row_constructor=''.join), \
            {'a':'-abc', 'b':'cba-', 'c':'-def'})
        #check that it doesn't fail on an empty alignment
        self.assertEqual(self.empty.omitGapCols(), {})

        #second, need to check behavior when the naughty rows should be
        #deleted as well.

        #default should strip out cols that are 100% gaps
        self.assertEqual(aln.omitGapCols(row_constructor=''.join, \
            del_rows=True), {'a':'-abc', 'b':'cba-', 'c':'-def'})
        #if allowed_gap_frac is 1, shouldn't delete anything
        self.assertEqual(aln.omitGapCols(1, row_constructor=''.join, \
            del_rows=True), {'a':'--a-bc-', 'b':'-cb-a--', 'c':'--d-ef-'})
        #if allowed_gap_frac is 0, should strip out any cols containing gaps
        self.assertEqual(aln.omitGapCols(0, row_constructor=''.join, \
            del_rows=True), {}) #everything has at least one naughty non-gap
        #intermediate numbers should work as expected
        self.assertEqual(aln.omitGapCols(0.4, row_constructor=''.join,
            del_rows=True), {'a':'abc', 'c':'def'}) #b has a naughty non-gap
        #check that does not delete b if allowed_frac_bad_calls higher than 0.14
        self.assertEqual(aln.omitGapCols(0.4, row_constructor=''.join,
            del_rows=True, allowed_frac_bad_cols=0.2), \
                    {'a':'abc', 'b':'ba-','c':'def'})
        self.assertEqual(aln.omitGapCols(0.4, row_constructor=''.join,
            del_rows=True), {'a':'abc', 'c':'def'}) #b has a naughty non-gap
        
        self.assertEqual(aln.omitGapCols(0.7, row_constructor=''.join,
            del_rows=True), {'a':'-abc', 'b':'cba-', 'c':'-def'}) #all ok
        #check that it doesn't fail on an empty alignment
        self.assertEqual(self.empty.omitGapCols(del_rows=True), {})

        #when we increase the number of sequences to 6, more differences
        #start to appear.
        aln['d'] = '-------'
        aln['e'] = 'xyzxyzx'
        aln['f'] = 'ab-cdef'
        #if no gaps are allowed, everything is deleted...
        self.assertEqual(aln.omitGapCols(0, del_rows=False), \
            {'a':[], 'b':[], 'c':[], 'd':[], 'e':[], 'f':[]})
        #...though not a sequence that's all gaps, since it has no positions
        #that are not gaps. This 'feature' should possibly be considered a bug.
        self.assertEqual(aln.omitGapCols(0, del_rows=True), {'d':[]})
        #if we're deleting only full columns of gaps, del_rows does nothing.
        self.assertEqual(aln.omitGapCols(del_rows=True, \
            row_constructor=''.join), aln)
        #at 50%, should delete a bunch of minority sequences
        self.assertEqual(aln.omitGapCols(0.5, del_rows=True, \
            row_constructor=''.join), \
            {'a':'-abc','b':'cba-','c':'-def','d':'----'})
        #shouldn't depend on order of rows
        aln.RowOrder = 'fadbec'
        self.assertEqual(aln.omitGapCols(0.5, del_rows=True, \
            row_constructor=''.join), \
            {'a':'-abc','b':'cba-','c':'-def','d':'----'})
        

    def test_omitGapRows(self):
        """Alignment omitGapRows should return alignment w/o rows with gaps"""
        #check default params
        self.assertEqual(self.gaps.omitGapRows(), self.gaps.omitGapRows(0))
        #check for boundary effects
        self.assertEqual(self.gaps.omitGapRows(-1), {})
        self.assertEqual(self.gaps.omitGapRows(0), {'a':'aaaaaaa'})
        self.assertEqual(self.gaps.omitGapRows(0.1), {'a':'aaaaaaa'})
        self.assertEqual(self.gaps.omitGapRows(3.0/7 - 0.01), {'a':'aaaaaaa'})
        self.assertEqual(self.gaps.omitGapRows(3.0/7), \
            {'a':'aaaaaaa','b':'a--a-aa'})
        self.assertEqual(self.gaps.omitGapRows(3.0/7 + 0.01), \
            {'a':'aaaaaaa','b':'a--a-aa'})
        self.assertEqual(self.gaps.omitGapRows(5.0/7 - 0.01), \
            {'a':'aaaaaaa','b':'a--a-aa'})
        self.assertEqual(self.gaps.omitGapRows(5.0/7 + 0.01), self.gaps)
        self.assertEqual(self.gaps.omitGapRows(0.99), self.gaps)
        #check new object creation
        assert self.gaps.omitGapRows(0.99) is not self.gaps
        assert isinstance(self.gaps.omitGapRows(3.0/7), Alignment)
        #repeat tests for object that supplies its own gaps
        self.assertEqual(self.gaps_rna.omitGapRows(-1), {})
        self.assertEqual(self.gaps_rna.omitGapRows(0), {'a':'aaaaaaa'})
        self.assertEqual(self.gaps_rna.omitGapRows(0.1), {'a':'aaaaaaa'})
        self.assertEqual(self.gaps_rna.omitGapRows(3.0/7 - 0.01), \
            {'a':'aaaaaaa'})
        self.assertEqual(self.gaps_rna.omitGapRows(3.0/7), \
            {'a':'aaaaaaa','b':'a--a-aa'})
        self.assertEqual(self.gaps_rna.omitGapRows(3.0/7 + 0.01), \
            {'a':'aaaaaaa','b':'a--a-aa'})
        self.assertEqual(self.gaps_rna.omitGapRows(5.0/7 - 0.01), \
            {'a':'aaaaaaa','b':'a--a-aa'})
        self.assertEqual(self.gaps_rna.omitGapRows(5.0/7 + 0.01), self.gaps_rna)
        self.assertEqual(self.gaps_rna.omitGapRows(0.99), self.gaps_rna)
        assert self.gaps_rna.omitGapRows(0.99) is not self.gaps_rna
        assert isinstance(self.gaps_rna.omitGapRows(3.0/7), Alignment)

    def test_omitGapRuns(self):
        """Alignment omitGapRuns should return alignment w/o runs of gaps"""
        #negative value will still let through ungapped sequences
        self.assertEqual(self.gaps.omitGapRuns(-5), {'a':'aaaaaaa'})
        #test edge effects
        self.assertEqual(self.gaps.omitGapRuns(0), {'a':'aaaaaaa'})
        self.assertEqual(self.gaps.omitGapRuns(1), {'a':'aaaaaaa'})
        self.assertEqual(self.gaps.omitGapRuns(2),{'a':'aaaaaaa','b':'a--a-aa'})
        self.assertEqual(self.gaps.omitGapRuns(3),{'a':'aaaaaaa','b':'a--a-aa'})
        self.assertEqual(self.gaps.omitGapRuns(4),{'a':'aaaaaaa','b':'a--a-aa'})
        self.assertEqual(self.gaps.omitGapRuns(5), self.gaps)
        self.assertEqual(self.gaps.omitGapRuns(6), self.gaps)
        self.assertEqual(self.gaps.omitGapRuns(1000), self.gaps)
        #test new object creation
        assert self.gaps.omitGapRuns(6) is not self.gaps
        assert isinstance(self.gaps.omitGapRuns(6), Alignment)

    def test_distanceMatrix(self):
        """Alignment distanceMatrix should produce correct scores"""
        self.assertEqual(self.empty.distanceMatrix(frac_same), {})
        self.assertEqual(self.one_seq.distanceMatrix(frac_same), {'a':{'a':1}})
        self.assertEqual(self.gaps.distanceMatrix(frac_same), 
            {   'a':{'a':7/7.0,'b':4/7.0,'c':2/7.0},
                'b':{'a':4/7.0,'b':7/7.0,'c':3/7.0},
                'c':{'a':2/7.0,'b':3/7.0,'c':7/7.0},
            })

    def test_IUPACConsensus_RNA(self):
        """Alignment IUPACConsensus should use RNA IUPAC symbols correctly"""
        alignmentUpper = Alignment( ['UCAGN-UCAGN-UCAGN-UCAGAGCAUN-',
                                     'UUCCAAGGNN--UUCCAAGGNNAGCAG--',
                                     'UUCCAAGGNN--UUCCAAGGNNAGCUA--',
                                     'UUUUCCCCAAAAGGGGNNNN--AGCUA--',
                                     'UUUUCCCCAAAAGGGGNNNN--AGCUA--',
                                     ])
        alignmentLower = Alignment( ['ucagn-ucagn-ucagn-ucagagcaun-',
                                     'uuccaaggnn--uuccaaggnnagcag--',
                                     'uuccaaggnn--uuccaaggnnagcua--',
                                     'uuuuccccaaaaggggnnnn--agcua--',
                                     'uuuuccccaaaaggggnnnn--agcua--',
                                     ])
        alignmentMixed = Alignment( ['ucagn-ucagn-ucagn-ucagagcaun-',
                                     'UUCCAAGGNN--UUCCAAGGNNAGCAG--',
                                     'uuccaaggnn--uuccaaggnnagcua--',
                                     'UUUUCCCCAAAAGGGGNNNN--AGCUA--',
                                     'uuuuccccaaaaggggnnnn--agcua--',
                                     ])
                                    
        #following IUPAC consensus calculated by hand
        #Test all uppper
        self.assertEqual(alignmentUpper.IUPACConsensus(),
                         'UYHBN?BSNN??KBVSN?NN??AGCWD?-')
        #Test all lower
        self.assertEqual(alignmentLower.IUPACConsensus(),
                         'uyhbn?bsnn??kbvsn?nn??agcwd?-')
        #Test mixed case
        self.assertEqual(alignmentMixed.IUPACConsensus(),
                         'UYHBN?BSNN??KBVSN?NN??AGCWD?-')
        
    def test_IUPACConsensus_DNA(self):
        """Alignment IUPACConsensus should use DNA IUPAC symbols correctly"""
        alignmentUpper = Alignment( ['TCAGN-TCAGN-TCAGN-TCAGAGCATN-',
                                     'TTCCAAGGNN--TTCCAAGGNNAGCAG--',
                                     'TTCCAAGGNN--TTCCAAGGNNAGCTA--',
                                     'TTTTCCCCAAAAGGGGNNNN--AGCTA--',
                                     'TTTTCCCCAAAAGGGGNNNN--AGCTA--',
                                     ])
        alignmentLower = Alignment( ['tcagn-tcagn-tcagn-tcagagcatn-',
                                     'ttccaaggnn--ttccaaggnnagcag--',
                                     'ttccaaggnn--ttccaaggnnagcta--',
                                     'ttttccccaaaaggggnnnn--agcta--',
                                     'ttttccccaaaaggggnnnn--agcta--',
                                     ])
        alignmentMixed = Alignment( ['tcagn-tcagn-tcagn-tcagagcatn-',
                                     'TTCCAAGGNN--TTCCAAGGNNAGCAG--',
                                     'ttccaaggnn--ttccaaggnnagcta--',
                                     'TTTTCCCCAAAAGGGGNNNN--AGCTA--',
                                     'ttttccccaaaaggggnnnn--agcta--',
                                     ])
                                    
        #following IUPAC consensus calculated by hand
        #Test all uppper
        self.assertEqual(alignmentUpper.IUPACConsensus(DnaAlphabet),
                         'TYHBN?BSNN??KBVSN?NN??AGCWD?-')
        #Test all lower
        self.assertEqual(alignmentLower.IUPACConsensus(DnaAlphabet),
                         'tyhbn?bsnn??kbvsn?nn??agcwd?-')
        #Test mixed case
        self.assertEqual(alignmentMixed.IUPACConsensus(DnaAlphabet),
                         'TYHBN?BSNN??KBVSN?NN??AGCWD?-')

    def test_IUPACConsensus_Protein(self):
        """Alignment IUPACConsensus should use protein IUPAC symbols correctly"""
        alignmentUpper = Alignment( ['ACDEFGHIKLMNPQRSTUVWY-',
                                     'ACDEFGHIKLMNPQRSUUVWF-',
                                     'ACDEFGHIKLMNPERSKUVWC-',
                                     'ACNEFGHIKLMNPQRS-UVWP-',                                     
                                     ])
        alignmentLower = Alignment( ['acdefghiklmnpqrstuvwy-',
                                     'acdefghiklmnpqrsuuvwf-',
                                     'acdefghiklmnperskuvwc-',
                                     'acnefghiklmnpqrs-uvwp-',
                                     ])
        alignmentMixed = Alignment( ['acdefghiklmnpqrstuvwy-',
                                     'ACDEFGHIKLMNPQRSUUVWF-',
                                     'acdefghiklmnperskuvwc-',
                                     'ACNEFGHIKLMNPQRS-UVWP-',
                                     ])
                                    
        #following IUPAC consensus calculated by hand
        #Test all uppper
        self.assertEqual(alignmentUpper.IUPACConsensus(ProteinAlphabet),
                         'ACBEFGHIKLMNPZRS?UVWx-')
        #Test all lower
        self.assertEqual(alignmentLower.IUPACConsensus(ProteinAlphabet),
                         'acbefghiklmnpzrs?uvwx-')
        #Test mixed case
        self.assertEqual(alignmentMixed.IUPACConsensus(ProteinAlphabet),
                         'ACBEFGHIKLMNPZRS?UVWx-')

    def test_toPhylip(self):
        """Alignment should return PHYLIP string format correctly"""
        align_norm = Alignment( ['ACDEFGHIKLMNPQRSTUVWY-',
                                     'ACDEFGHIKLMNPQRSUUVWF-',
                                     'ACDEFGHIKLMNPERSKUVWC-',
                                     'ACNEFGHIKLMNPQRS-UVWP-',                                     
                                     ])

        phylip_str, id_map =  align_norm.toPhylip()

        self.assertEqual(phylip_str, """4 22\nseq0000001 ACDEFGHIKLMNPQRSTUVWY-\nseq0000002 ACDEFGHIKLMNPQRSUUVWF-\nseq0000003 ACDEFGHIKLMNPERSKUVWC-\nseq0000004 ACNEFGHIKLMNPQRS-UVWP-""")
        self.assertEqual(id_map, {'seq0000004': 3, 'seq0000001': 0, 'seq0000003': 2, 'seq0000002': 1})

        align_rag = Alignment( ['ACDEFGHIKLMNPQRSTUVWY-',
                                     'ACDEFGHIKLMNPQRSUUVWF-',
                                     'ACDEFGHIKLMNPERSKUVWC-',
                                     'ACNEFGHIKLMNUVWP-',                                     
                                     ])


        self.assertRaises(ValueError,  align_rag.toPhylip)

    def test_isRagged(self):
        """Alignment isRagged should return true if ragged alignment"""
        assert(self.ragged.isRagged())
        assert(not self.identical.isRagged())
        assert(not self.gaps.isRagged())

    def test_scoreMatrix(self):
        """Alignment scoreMatrix should produce position specific score matrix."""
        scoreMatrix = {
            0:{'a':1.0,'c':1.0,'u':5.0},
            1:{'c':6.0,'u':1.0},
            2:{'a':3.0,'c':2.0,'g':2.0},
            3:{'a':3.0,'g':4.0},
            4:{'c':1.0,'g':1.0,'u':5.0},
            5:{'c':6.0,'u':1.0},
            6:{'a':3.0,'g':4.0},
            7:{'a':1.0,'g':6.0},
            8:{'a':1.0,'c':1.0,'g':1.0,'u':4.0},
            9:{'a':1.0,'c':2.0,'u':4.0},
            }
        self.assertEqual(self.many.scoreMatrix(), scoreMatrix)

    def test_columnFrequencies(self):
        """Alignment.columnFrequencies should count symbols in each column"""
        #calculate by hand what the first and last columns should look like in
        #each case
        firstvalues = [ [self.integers, Freqs([1,1,5])],
                        [self.sequences, Freqs('UUU')],
                        [self.structures, Freqs('(.(')],
                    ]
        
        lastvalues = [ [self.integers, Freqs([5,1,1])],
                        [self.sequences, Freqs('GGG')],
                        [self.structures, Freqs('..)')],
                    ]
        #check that the first columns are what we expected
        for obj, result in firstvalues:
            freqs = obj.columnFrequencies()
            self.assertEqual(str(freqs[0]), str(result))
        #check that the last columns are what we expected
        for obj, result in lastvalues:
            freqs = obj.columnFrequencies()
            self.assertEqual(str(freqs[-1]), str(result))
        #check that it works for the empty alignment
        freqs = self.empty.columnFrequencies()
        self.assertEqual(str(freqs), str([]))

    def test_columnProbs(self):
        """Alignment.columnProbs should find Pr(symbol) in each column"""
        #make an alignment with 4 rows (easy to calculate probabilities)
        align = Alignment(["AAA", "ACA", "GGG", "GUC"])
        cp = align.columnProbs()
        #check that the column probs match the counts we expect
        self.assertEqual(cp, map(Freqs, [   
            {'A':0.5, 'G':0.5},
            {'A':0.25, 'C':0.25, 'G':0.25, 'U':0.25},
            {'A':0.5, 'G':0.25, 'C':0.25},
            ]))

    def test_majorityConsensus(self):
        """Alignment.majorityConsensus should return commonest symbol per column"""
        #Check the majority consensus in detail for the integer alignment
        obs = self.integers.majorityConsensus()
        self.assertEqual(obs[0], 1)
        assert(obs[1] in [2, 1, 4])
        self.assertEqual(obs[2], 3)
        assert(obs[3] in [2, 1, 4])
        self.assertEqual(obs[4], 1)
        #Check the exact strings expected from string transform
        self.assertEqual(self.sequences.majorityConsensus(str), 'UCAG')
        self.assertEqual(self.structures.majorityConsensus(str), '(.....')
        self.assertEqual(str(self.empty.majorityConsensus()), str([]))

    
    def test_uncertainties(self):
        """Alignment.uncertainties should match hand-calculated values"""
        aln = Alignment(['abc', 'axc'])
        obs = aln.uncertainties()
        self.assertFloatEqual(obs, [0, 1, 0])
        #check what happens with only one input sequence
        aln = Alignment(['abc'])
        obs = aln.uncertainties()
        self.assertFloatEqual(obs, [0, 0, 0])
        #check that we can screen out bad items OK
        aln = Alignment(['abc', 'def', 'ghi', 'jkl', 'GHI'])
        obs = aln.uncertainties('abcdefghijklmnop')
        self.assertFloatEqual(obs, [2.0] * 3)

    def test_omitRowsTemplate(self):
        """Alignment.omitRowsTemplate returns new aln with well-aln to temp"""
        aln = self.omitRowsTemplate_aln
        result = aln.omitRowsTemplate('s3', 0.9, 5)
        self.assertEqual(result, {'s3': 'UUCCUUCUU-UUC', \
                's4': 'UU-UUUU-UUUUC'})
        result2 = aln.omitRowsTemplate('s4', 0.9, 4)
        self.assertEqual(result2, {'s3': 'UUCCUUCUU-UUC', \
                's4': 'UU-UUUU-UUUUC'})
        result3 = aln.omitRowsTemplate('s1', 0.9, 4)
        self.assertEqual(result3, {'s2': 'UC------U---C', \
                's1': 'UC-----CU---C', 's5': '-------------'})
        result4 = aln.omitRowsTemplate('s3', 0.5, 13)
        self.assertEqual(result4, {'s3': 'UUCCUUCUU-UUC', \
                's4': 'UU-UUUU-UUUUC'})
        
    def test_toFasta(self):
        """toFasta returns a fasta string"""

        aln = self.end_gaps 
        result = aln.toFasta()
        self.assertEqual(result, """>a
--a-bc-
>c
--d-ef-
>b
-cb-a--""")

    def test_make_gap_filter(self):
        """make_gap_filter returns f(seq) -> True if aligned ok w/ query"""
        s1 = Rna('UC-----CU---C')
        s3 = Rna('UUCCUUCUU-UUC')
        s4 = Rna('UU-UUUU-UUUUC')
        #check that the behavior is ok for gap runs
        f1 = make_gap_filter(s1, 0.9, 5)
        f3 = make_gap_filter(s3, 0.9, 5)
        #Should return False since s1 has gap run >= 5 with respect to s3
        self.assertEqual(f3(s1), False)
        #Should return False since s3 has an insertion run >= 5 to s1
        self.assertEqual(f1(s3), False)
        #Should retun True since s4 does not have a long enough gap or ins run
        self.assertEqual(f3(s4), True)
        f3 = make_gap_filter(s3, 0.9, 6)
        self.assertEqual(f3(s1), True)
        
        #Check that behavior is ok for gap_fractions
        f1 = make_gap_filter(s1, 0.5, 6)
        f3 = make_gap_filter(s3, 0.5, 6)
        #Should return False since 0.53% of positions are diff for gaps
        self.assertEqual(f3(s1), False)
        self.assertEqual(f1(s3), False)
        self.assertEqual(f3(s4), True)

    def test_getIntMap(self):
        """Alignment.getIntMap should return correct mapping."""
        aln = Alignment({'seq1':'ACGU','seq2':'CGUA','seq3':'CCGU'})
        int_keys = {'seq_0':'seq1','seq_1':'seq2','seq_2':'seq3'}
        int_map = {'seq_0':'ACGU','seq_1':'CGUA','seq_2':'CCGU'}
        im,ik = aln.getIntMap()
        self.assertEqual(ik,int_keys)
        self.assertEqual(im,int_map)

#run tests if invoked from command line
if __name__ == '__main__':
    main()
