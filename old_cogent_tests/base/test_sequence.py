#!/usr/bin/env python
#file evo/test_sequence.py

"""Unit tests for Sequence class and its subclasses.

Owner: Rob Knight rob@spot.colorado.edu

Status: Development: feedback requested

Revision History

11/6/03 Rob Knight: initially written for PyEvolve.

4/7/04 Rob Knight: added tests for gapVector, gapMaps, and isGap.

4/8/04 Rob Knight: added tests for matrixDistance, fracSame, fracDiff,
fracSameGaps, fracDiffGaps, fracSameNonGaps, fracDiffNonGaps, fracSimilar.
"""

from old_cogent.base.sequence import SequenceI, Sequence, RnaSequence, DnaSequence, \
    ProteinSequence, MutableSequence, SequenceCleaner, \
    Rna, Dna, Protein, \
    RnaUngapped, DnaUngapped, ProteinUngapped, \
    MutableRna, MutableDna, MutableProtein, \
    MutableRnaUngapped, MutableDnaUngapped, MutableProteinUngapped
from old_cogent.util.misc import ConstraintError, Delegator, ConstrainedList, \
    ConstrainedString, FunctionWrapper
from old_cogent.base.alphabet import RnaAlphabet, DnaAlphabet, ProteinAlphabet
from old_cogent.util.unit_test import TestCase, main
from old_cogent.base.info import Info as InfoClass

class SequenceITests(TestCase):
    """Tests of the SequenceI class.
    
    Currently, does not do individual tests of the methods that are delegated
    to Alphabet (basically no code to test).
    """
    def test_find_info(self):
        """Tests of the find_info method."""
        class obj_info(object):
            #use 'xyz' as a special case so we can set info to None as well as
            #having it absent
            def __init__(self, Info='xyz'):
                if Info != 'xyz':
                    self.Info = Info

        class cls_info_bad(obj_info):
            Info = 3

        class cls_info_good(obj_info):
            Info = InfoClass({'Species':'Homo sapiens', 'GO':123})

        empty_o = obj_info('xyz')
        none_o = obj_info(None)
        dict_o = obj_info({'a':'b'})
        bad_o = obj_info('abc')
        
        empty_c = cls_info_good('xyz')
        none_c = cls_info_good(None)
        dict_c = cls_info_good({'a':'b'})
        bad_c = cls_info_good('abc')

        empty_c_bad = cls_info_bad('xyz')
        none_c_bad = cls_info_bad(None)
        dict_c_bad = cls_info_bad({'a':'b'})
        bad_c_bad = cls_info_bad('abc')

        empty_info = InfoClass()
        ab_info = InfoClass({'a':'b'})
        sp_info = InfoClass({'Species':'Homo sapiens', 'GO':123})

        seq = SequenceI(None)
        fi = seq._find_info

        self.assertEqual(fi(), empty_info)
        self.assertEqual(fi(empty_o), empty_info)
        self.assertEqual(fi(none_o), empty_info)
        self.assertEqual(fi(dict_o), ab_info)
        self.assertEqual(fi(bad_o), 'abc')
        self.assertEqual(fi(empty_c), sp_info)
        self.assertEqual(fi(none_c), sp_info)
        self.assertEqual(fi(dict_c), ab_info)
        self.assertEqual(fi(bad_c), 'abc')
        self.assertEqual(fi(empty_c_bad), 3)
        self.assertEqual(fi(none_c_bad), 3)
        self.assertEqual(fi(dict_c_bad), ab_info)
        self.assertEqual(fi(bad_c_bad), 'abc')

        #should always use info if it was supplied
        self.assertEqual(fi(empty_o, 1), 1)
        self.assertEqual(fi(none_o, 1), 1)
        self.assertEqual(fi(dict_o, 1), 1)
        self.assertEqual(fi(bad_o, 1), 1)
        self.assertEqual(fi(empty_c, 1), 1)
        self.assertEqual(fi(none_c, 1), 1)
        self.assertEqual(fi(dict_c, 1), 1)
        self.assertEqual(fi(bad_c, 1), 1)
        self.assertEqual(fi(empty_c_bad, 1), 1)
        self.assertEqual(fi(none_c_bad, 1), 1)
        self.assertEqual(fi(dict_c_bad, 1), 1)
        self.assertEqual(fi(bad_c_bad, 1), 1)

class SequenceTests(TestCase):
    """Tests of the Sequence class."""
    SEQ = Sequence
    RNA = RnaSequence
    DNA = DnaSequence
    PROT = ProteinSequence
    def test_init_empty(self):
        """Sequence and subclasses should init correctly."""
        s = self.SEQ()
        assert hasattr(s, 'Info')
        assert hasattr(s, 'Refs')
        self.assertEqual(s, '')
        assert s.Alphabet is None

        r = self.RNA()
        assert hasattr(r, 'Info')
        assert hasattr(r, 'Refs')
        assert r.Alphabet is RnaAlphabet

    def test_init_data(self):
        """Sequence init with data should set data in correct location"""
        r = self.RNA('ucagg', Info={'x':3, 'GO':5})
        self.assertEqual(r, 'ucagg')
        self.assertEqual(r.x, 3)
        self.assertEqual(r.GO, [5])
        assert 'x' in r.Info
        assert 'GO' in r.Info
        assert 'GO' in r.Refs
        assert 'x' not in r.Refs
        r.GO = (2,3,4)
        self.assertEqual(r.GO, [2,3,4])
        r.x = '7'
        self.assertEqual(r.x, '7')
        assert 'x' not in r.Refs
        assert 'x' in r.Info
        assert 'x' not in r.__dict__
        r.x = 3
        self.assertEqual(r.x, 3)
        assert 'x' not in r.Refs
        assert 'x' in r.Info
        assert 'x' not in r.__dict__
        new_alphabet = 'ucagx'
        r.Alphabet = new_alphabet
        assert 'Alphabet' not in r.Info
        assert r.Alphabet is not RnaAlphabet
        assert r.Alphabet is new_alphabet
        assert getattr(r, 'Alphabet') is new_alphabet
        self.assertEqual(r+'xxx', 'ucaggxxx')

    def test_stripDegenerate(self):
        """Sequence stripDegenerate should remove any degenerate bases"""
        self.assertEqual(self.RNA('UCAG-').stripDegenerate(), 'UCAG-')
        self.assertEqual(self.RNA('NRYSW').stripDegenerate(), '')
        self.assertEqual(self.RNA('USNG').stripDegenerate(), 'UG')

    def test_stripBad(self):
        """Sequence stripBad should remove any non-base, non-gap chars"""
        self.assertEqual(self.RNA('UCxxxAGwsnyrHBNzzzD-D').stripBad(), 
            'UCAGwsnyrHBND-D')
        self.assertEqual(self.RNA('@#^*($@!#&()!@QZX').stripBad(), '')
        self.assertEqual(self.RNA('aaaxggg---!ccc').stripBad(), 
            'aaaggg---ccc')

    def test_stripBadAndGaps(self):
        """Sequence stripBadAndGaps should remove gaps and bad chars"""
        self.assertEqual(self.RNA('UxxCAGwsnyrHBNz#!D-D').stripBadAndGaps(), 
            'UCAGwsnyrHBNDD')
        self.assertEqual(self.RNA('@#^*($@!#&()!@QZX').stripBadAndGaps(), '')
        self.assertEqual(self.RNA('aaa ggg ---!ccc').stripBadAndGaps(), 
            'aaagggccc')

    def test_shuffle(self):
        """Sequence shuffle should return new random sequence w/ same monomers"""
        r = self.RNA('UUUUCCCCAAAAGGGG')
        s = r.shuffle()
        assert r.Info is s.Info
        self.assertEqual(r.Info, s.Info)
        self.assertNotEqual(r, s)
        self.assertEqualItems(r, s)

    def test_complement(self):
        """Sequence complement should correctly complement sequence"""
        self.assertEqual(self.RNA('UauCG-NR').complement(), 'AuaGC-NY')
        self.assertEqual(self.DNA('TatCG-NR').complement(), 'AtaGC-NY')
        self.assertEqual(self.DNA('').complement(), '')
        self.assertRaises(TypeError, self.PROT('ACD').complement)

    def test_rc(self):
        """Sequence rc should correctly reverse-complement sequence"""
        self.assertEqual(self.RNA('UauCG-NR').rc(), 'YN-CGauA')
        self.assertEqual(self.DNA('TatCG-NR').rc(), 'YN-CGatA')
        self.assertEqual(self.RNA('').rc(), '')
        self.assertEqual(self.RNA('A').rc(), 'U')
        self.assertRaises(TypeError, self.PROT('ACD').rc)

    def test_contains(self):
        """Sequence contains should return correct result"""
        r = self.RNA('UCA')
        assert 'U' in r
        assert 'CA' in r
        assert 'X' not in r
        assert 'G' not in r

    def test_iter(self):
       """Sequence iter should iterate over sequence"""
       p = self.PROT('QWE')
       self.assertEqual(list(p), ['Q','W','E'])

    def test_isGapped(self):
        """Sequence isGapped should return True if gaps in seq"""
        assert not self.RNA('').isGapped()
        assert not self.RNA('ACGUCAGUACGUCAGNRCGAUcaguaguacYRNRYRN').isGapped()
        assert self.RNA('-').isGapped()
        assert self.PROT('--').isGapped()
        assert self.RNA('CAGUCGUACGUCAGUACGUacucauacgac-caguACUG').isGapped()
        assert self.RNA('CA--CGUAUGCA-----g').isGapped()
        assert self.RNA('CAGU-').isGapped()

    def test_isGap(self):
        """Sequence isGap should return True if char is a valid gap char"""
        r = self.RNA('ACGUCAGUACGUCAGNRCGAUcaguaguacYRNRYRN')
        for char in 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOASDFGHJKLZXCVBNM':
            assert not r.isGap(char)
        assert r.isGap('-')
        #only works on a single literal that's a gap, not on a sequence.
        #possibly, this behavior should change?
        assert not r.isGap('---')
        #check behaviour on self
        assert not self.RNA('CGAUACGUACGACU').isGap()
        assert not self.RNA('---CGAUA----CGUACG---ACU---').isGap()
        assert self.RNA('').isGap()
        assert self.RNA('----------').isGap()


    def test_isDegenerate(self):
        """Sequence isDegenerate should return True if degen symbol in seq"""
        assert not self.RNA('').isDegenerate()
        assert not self.RNA('UACGCUACAUGuacgucaguGCUAGCUA---ACGUCAG').isDegenerate()
        assert self.RNA('N').isDegenerate()
        assert self.RNA('R').isDegenerate()
        assert self.RNA('y').isDegenerate()
        assert self.RNA('GCAUguagcucgUCAGUCAGUACgUgcasCUAG').isDegenerate()
        assert self.RNA('ACGYAUGCUGYWWNMNuwbycwuybcwbwub').isDegenerate()

    def test_isStrict(self):
        """Sequence isStrict should return True if all symbols in Monomers"""
        assert self.RNA('').isStrict()
        assert self.PROT('A').isStrict()
        assert self.RNA('UAGCACUgcaugcauGCAUGACuacguACAUG').isStrict()
        assert not self.RNA('CAGUCGAUCA-cgaucagUCGAUGAC').isStrict()

    def test_firstGap(self):
        """Sequence firstGap should return index of first gap symbol, or None"""
        self.assertEqual(self.RNA('').firstGap(), None)
        self.assertEqual(self.RNA('a').firstGap(), None)
        self.assertEqual(self.RNA('uhacucHuhacUUhacan').firstGap(), None)
        self.assertEqual(self.RNA('-abc').firstGap(), 0)
        self.assertEqual(self.RNA('b-ac').firstGap(), 1)
        self.assertEqual(self.RNA('abcd-').firstGap(), 4)

    def test_firstDegenerate(self):
        """Sequence firstDegenerate should return index of first degen symbol"""
        self.assertEqual(self.RNA('').firstDegenerate(), None)
        self.assertEqual(self.RNA('a').firstDegenerate(), None)
        self.assertEqual(self.RNA('UCGACA--CU-gacucaguacgua'
            ).firstDegenerate(), None)
        self.assertEqual(self.RNA('nCAGU').firstDegenerate(), 0)
        self.assertEqual(self.RNA('CUGguagvAUG').firstDegenerate(), 7)
        self.assertEqual(self.RNA('ACUGCUAacgud').firstDegenerate(), 11)

    def test_firstNonStrict(self):
        """Sequence firstNonStrict should return index of first non-strict symbol"""
        self.assertEqual(self.RNA('').firstNonStrict(), None)
        self.assertEqual(self.RNA('A').firstNonStrict(), None)
        self.assertEqual(self.RNA('ACGUACGUcgaucagu').firstNonStrict(), None)
        self.assertEqual(self.RNA('N').firstNonStrict(), 0)
        self.assertEqual(self.RNA('-').firstNonStrict(), 0)
        self.assertEqual(self.RNA('ACGUcgAUGUGCAUcagu-').firstNonStrict(),18)

    def test_disambiguate(self):
        """Sequence disambiguate should remove degenerate bases"""
        self.assertEqual(self.RNA('').disambiguate(), '')
        self.assertEqual(self.RNA('AGCUGAUGUA--CAGU').disambiguate(),
            'AGCUGAUGUA--CAGU')
        self.assertEqual(self.RNA('AUn-yrs-wkmCGwmrNMWRKY').disambiguate(
            'strip'), 'AU--CG')
        s = self.RNA('AUn-yrs-wkmCGwmrNMWRKY')
        t = s.disambiguate('random')
        u = s.disambiguate('random')
        for i, j in zip(s, t):
            if i in s.Alphabet.Degenerates:
                assert j in s.Alphabet.Degenerates[i]
            else:
                assert i == j
        self.assertNotEqual(t, u)
        self.assertEqual(len(s), len(t))

    def test_degap(self):
        """Sequence degap should remove all gaps from sequence"""
        self.assertEqual(self.RNA('').degap(), '')
        self.assertEqual(self.RNA('GUCAGUCgcaugcnvuncdks').degap(), 
            'GUCAGUCgcaugcnvuncdks')
        self.assertEqual(self.RNA('----------------').degap(), '')
        self.assertEqual(self.RNA('gcuauacg-').degap(), 'gcuauacg')
        self.assertEqual(self.RNA('-CUAGUCA').degap(), 'CUAGUCA')
        self.assertEqual(self.RNA('---a---c---u----g---').degap(), 'acug')
        
    def test_gapList(self):
        """Sequence gapList should return correct gap positions"""
        self.assertEqual(self.RNA('').gapList(), [])
        self.assertEqual(self.RNA('ACUGUCAGUACGHSDKCUCDNNS').gapList(),[])
        self.assertEqual(self.RNA('GUACGUACAKDC-SDHDSK').gapList(),[12])
        self.assertEqual(self.RNA('-DSHUHDS').gapList(), [0])
        self.assertEqual(self.RNA('UACHASADS-').gapList(), [9])
        self.assertEqual(self.RNA('---CGAUgCAU---ACGHc---ACGUCAGU---'
            ).gapList(), [0,1,2,11,12,13,19,20,21,30,31,32])

    def test_gapVector(self):
        """Sequence gapVector should return correct gap positions"""
        g = lambda x: self.RNA(x).gapVector()
        self.assertEqual(g(''), [])
        self.assertEqual(g('ACUGUCAGUACGHCSDKCCUCCDNCNS'), [False]*27)
        self.assertEqual(g('GUACGUAACAKADC-SDAHADSAK'), 
         map(bool, map(int,'000000000000001000000000')))
        self.assertEqual(g('-DSHSUHDSS'), 
         map(bool, map(int,'1000000000')))
        self.assertEqual(g('UACHASCAGDS-'), 
         map(bool, map(int,'000000000001')))
        self.assertEqual(g('---CGAUgCAU---ACGHc---ACGUCAGU---'), \
         map(bool, map(int,'111000000001110000011100000000111')))

    def test_gapMaps(self):
        """Sequence gapMaps should return dicts mapping gapped/ungapped pos"""
        empty = ''
        no_gaps = 'aaa'
        all_gaps = '---'
        start_gaps = '--abc'
        end_gaps = 'ab---'
        mid_gaps = '--a--b-cd---'
        gm = lambda x: self.RNA(x).gapMaps()
        self.assertEqual(gm(empty), ({},{}))
        self.assertEqual(gm(no_gaps), ({0:0,1:1,2:2}, {0:0,1:1,2:2}))
        self.assertEqual(gm(all_gaps), ({},{}))
        self.assertEqual(gm(start_gaps), ({0:2,1:3,2:4},{2:0,3:1,4:2}))
        self.assertEqual(gm(end_gaps), ({0:0,1:1},{0:0,1:1}))
        self.assertEqual(gm(mid_gaps), ({0:2,1:5,2:7,3:8},{2:0,5:1,7:2,8:3}))
     
    def test_countGaps(self):
        """Sequence countGaps should return correct gap count"""
        self.assertEqual(self.RNA('').countGaps(), 0)
        self.assertEqual(self.RNA('ACUGUCAGUACGHSDKCUCDNNS').countGaps(),
            0)
        self.assertEqual(self.RNA('GUACGUACAKDC-SDHDSK').countGaps(), 1)
        self.assertEqual(self.RNA('-DSHUHDS').countGaps(), 1)
        self.assertEqual(self.RNA('UACHASADS-').countGaps(), 1)
        self.assertEqual(self.RNA('---CGAUgCAU---ACGHc---ACGUCAGU---'
            ).countGaps(), 12)

    def test_countDegenerate(self):
        """Sequence countDegenerate should return correct degen base count"""
        self.assertEqual(self.RNA('').countDegenerate(), 0)
        self.assertEqual(self.RNA('GACUGCAUGCAUCGUACGUCAGUACCGA'
            ).countDegenerate(), 0)
        self.assertEqual(self.RNA('N').countDegenerate(), 1)
        self.assertEqual(self.PROT('N').countDegenerate(), 0)
        self.assertEqual(self.RNA('NRY').countDegenerate(), 3)
        self.assertEqual(self.RNA('ACGUAVCUAGCAUNUCAGUCAGyUACGUCAGS'
            ).countDegenerate(), 4)

    def test_possibilites(self):
        """Sequence possibilities should return correct # possible sequences"""
        self.assertEqual(self.RNA('').possibilities(), 1)
        self.assertEqual(self.RNA('ACGUgcaucagUCGuGCAU').possibilities(), 1)
        self.assertEqual(self.RNA('N').possibilities(), 4)
        self.assertEqual(self.RNA('R').possibilities(), 2)
        self.assertEqual(self.RNA('H').possibilities(), 3)
        self.assertEqual(self.RNA('nRh').possibilities(), 24)
        self.assertEqual(self.RNA('AUGCnGUCAg-aurGauc--gauhcgauacgws'
            ).possibilities(), 96)
       
    def test_MW(self):
        """Sequence MW should return correct molecular weight"""
        self.assertEqual(self.PROT('').MW(), 0)
        self.assertEqual(self.RNA('').MW(), 0)
        self.assertFloatEqual(self.PROT('A').MW(), 107.09)
        self.assertFloatEqual(self.RNA('A').MW(), 375.17)
        self.assertFloatEqual(self.PROT('AAA').MW(), 285.27)
        self.assertFloatEqual(self.RNA('AAA').MW(), 1001.59)
        self.assertFloatEqual(self.RNA('AAACCCA').MW(), 2182.37)

    def test_canMatch(self):
        """Sequence canMatch should return True if all positions can match"""
        assert self.RNA('').canMatch('')
        assert self.RNA('UCAG').canMatch('UCAG')
        assert not self.RNA('UCAG').canMatch('ucag')
        assert self.RNA('UCAG').canMatch('NNNN')
        assert self.RNA('NNNN').canMatch('UCAG')
        assert self.RNA('NNNN').canMatch('NNNN')
        assert not self.RNA('N').canMatch('x')
        assert not self.RNA('N').canMatch('-')
        assert self.RNA('UCAG').canMatch('YYRR')
        assert self.RNA('UCAG').canMatch('KMWS')

    def test_canMismatch(self):
        """Sequence canMismatch should return True on any possible mismatch"""
        assert not self.RNA('').canMismatch('')
        assert self.RNA('N').canMismatch('N')
        assert self.RNA('R').canMismatch('R')
        assert self.RNA('N').canMismatch('r')
        assert self.RNA('CGUACGCAN').canMismatch('CGUACGCAN')
        assert self.RNA('U').canMismatch('C')
        assert self.RNA('UUU').canMismatch('UUC')
        assert self.RNA('UUU').canMismatch('UUY')
        assert not self.RNA('UUU').canMismatch('UUU')
        assert not self.RNA('UCAG').canMismatch('UCAG')
        assert not self.RNA('U--').canMismatch('U--')

    def test_mustMatch(self):
        """Sequence mustMatch should return True when no possible mismatches"""
        assert self.RNA('').mustMatch('')
        assert not self.RNA('N').mustMatch('N')
        assert not self.RNA('R').mustMatch('R')
        assert not self.RNA('N').mustMatch('r')
        assert not self.RNA('CGUACGCAN').mustMatch('CGUACGCAN')
        assert not self.RNA('U').mustMatch('C')
        assert not self.RNA('UUU').mustMatch('UUC')
        assert not self.RNA('UUU').mustMatch('UUY')
        assert self.RNA('UU-').mustMatch('UU-')
        assert self.RNA('UCAG').mustMatch('UCAG')

    def test_canPair(self):
        """Sequence canPair should return True if all positions can pair"""
        assert self.RNA('').canPair('')
        assert not self.RNA('UCAG').canPair('UCAG')
        assert self.RNA('UCAG').canPair('CUGA')
        assert not self.RNA('UCAG').canPair('cuga')
        assert self.RNA('UCAG').canPair('NNNN')
        assert self.RNA('NNNN').canPair('UCAG')
        assert self.RNA('NNNN').canPair('NNNN')
        assert not self.RNA('N').canPair('x')
        assert not self.RNA('N').canPair('-')
        assert self.RNA('-').canPair('-')
        assert self.RNA('UCAGU').canPair('KYYRR')
        assert self.RNA('UCAG').canPair('KKRS')
        assert self.RNA('U').canPair('G')

        assert not self.DNA('T').canPair('G')

    def test_canMispair(self):
        """Sequence canMispair should return True on any possible mispair"""
        assert not self.RNA('').canMispair('')
        assert self.RNA('N').canMispair('N')
        assert self.RNA('R').canMispair('Y')
        assert self.RNA('N').canMispair('r')
        assert self.RNA('CGUACGCAN').canMispair('NUHCHUACH')
        assert self.RNA('U').canMispair('C')
        assert self.RNA('U').canMispair('R')
        assert self.RNA('UUU').canMispair('AAR')
        assert self.RNA('UUU').canMispair('GAG')
        assert not self.RNA('UUU').canMispair('AAA')
        assert not self.RNA('UCAG').canMispair('CUGA')
        assert self.RNA('U--').canMispair('--U')

        assert self.DNA('TCCAAAGRYY').canMispair('RRYCTTTGGA')

    def test_mustPair(self):
        """Sequence mustPair should return True when no possible mispairs"""
        assert self.RNA('').mustPair('')
        assert not self.RNA('N').mustPair('N')
        assert not self.RNA('R').mustPair('Y')
        assert not self.RNA('A').mustPair('A')
        assert not self.RNA('CGUACGCAN').mustPair('NUGCGUACG')
        assert not self.RNA('U').mustPair('C')
        assert not self.RNA('UUU').mustPair('AAR')
        assert not self.RNA('UUU').mustPair('RAA')
        assert not self.RNA('UU-').mustPair('-AA')
        assert self.RNA('UCAG').mustPair('CUGA')

        assert self.DNA('TCCAGGG').mustPair('CCCTGGA')
        assert self.DNA('tccaggg').mustPair('ccctgga')
        assert not self.DNA('TCCAGGG').mustPair('NCCTGGA')

    def test_diff(self):
        """Sequence diff should count 1 for each difference between sequences"""
        self.assertEqual(self.RNA('UGCUGCUC').diff(''), 0)
        self.assertEqual(self.RNA('UGCUGCUC').diff('U'), 0)
        self.assertEqual(self.RNA('UGCUGCUC').diff('UCCCCCUC'), 3)
        #case-sensitive!
        self.assertEqual(self.RNA('AAAAA').diff('aaaaa'), 5)
        #raises TypeError if other not iterable
        self.assertRaises(TypeError, self.RNA('AAAAA').diff, 5)
        
    def test_distance(self):
        """Sequence distance should calculate correctly based on function"""
        def f(a, b):
            if a == b:
                return 0
            if (a in 'UC' and b in 'UC') or (a in 'AG' and b in 'AG'):
                return 1
            else:
                return 10
        #uses identity function by default
        self.assertEqual(self.RNA('UGCUGCUC').distance(''), 0)
        self.assertEqual(self.RNA('UGCUGCUC').distance('U'), 0)
        self.assertEqual(self.RNA('UGCUGCUC').distance('UCCCCCUC'), 3)
        #case-sensitive!
        self.assertEqual(self.RNA('AAAAA').distance('aaaaa'), 5)
        #should use function if supplied
        self.assertEqual(self.RNA('UGCUGCUC').distance('', f), 0)
        self.assertEqual(self.RNA('UGCUGCUC').distance('U', f), 0)
        self.assertEqual(self.RNA('UGCUGCUC').distance('C', f), 1)
        self.assertEqual(self.RNA('UGCUGCUC').distance('G', f), 10)
        self.assertEqual(self.RNA('UGCUGCUC').distance('UCCCCCUC', f), 21)
        #case-sensitive!
        self.assertEqual(self.RNA('AAAAA').distance('aaaaa', f), 50)

    def test_matrixDistance(self):
        """Sequence matrixDistance should look up distances from a matrix"""
        #note that the score matrix must contain 'diagonal' elements m[i][i] 
        #to avoid failure when the sequences match.
        m = {'U':{'U':0, 'C':1, 'A':5}, 'C':{'C':0, 'A':2,'G':4}}
        self.assertEqual(self.RNA('UUUCCC').matrixDistance('UCACGG', m), 14)
        self.assertEqual(self.RNA('UUUCCC').matrixDistance('', m), 0)
        self.assertEqual(self.RNA('UUU').matrixDistance('CAC', m), 7)
        self.assertRaises(KeyError, self.RNA('UUU').matrixDistance, 'CAG', m)

    def test_fracSame(self):
        """Sequence fracSame should return similarity between sequences"""
        s1 = self.RNA('ACGU')
        s2 = self.RNA('AACG')
        s3 = self.RNA('GG')
        s4 = self.RNA('A')
        e = self.RNA('')
        self.assertEqual(s1.fracSame(e), 0)
        self.assertEqual(s1.fracSame(s2), 0.25)
        self.assertEqual(s1.fracSame(s3), 0)
        self.assertEqual(s1.fracSame(s4), 1.0)  #note truncation

    def test_fracDiff(self):
        """Sequence fracDiff should return difference between sequences"""
        s1 = self.RNA('ACGU')
        s2 = self.RNA('AACG')
        s3 = self.RNA('GG')
        s4 = self.RNA('A')
        e = self.RNA('')
        self.assertEqual(s1.fracDiff(e), 0)
        self.assertEqual(s1.fracDiff(s2), 0.75)
        self.assertEqual(s1.fracDiff(s3), 1)
        self.assertEqual(s1.fracDiff(s4), 0)  #note truncation

    def test_fracSameGaps(self):
        """Sequence fracSameGaps should return similarity in gap positions"""
        s1 = self.RNA('AAAA')
        s2 = self.RNA('GGGG')
        s3 = self.RNA('----')
        s4 = self.RNA('A-A-')
        s5 = self.RNA('-G-G')
        s6 = self.RNA('UU--')
        s7 = self.RNA('-')
        s8 = self.RNA('GGG')
        e =  self.RNA('')
        self.assertEqual(s1.fracSameGaps(s1), 1)
        self.assertEqual(s1.fracSameGaps(s2), 1)
        self.assertEqual(s1.fracSameGaps(s3), 0)
        self.assertEqual(s1.fracSameGaps(s4), 0.5)
        self.assertEqual(s1.fracSameGaps(s5), 0.5)
        self.assertEqual(s1.fracSameGaps(s6), 0.5)
        self.assertEqual(s1.fracSameGaps(s7), 0)
        self.assertEqual(s1.fracSameGaps(e), 0)
        self.assertEqual(s3.fracSameGaps(s3), 1)
        self.assertEqual(s3.fracSameGaps(s4), 0.5)
        self.assertEqual(s3.fracSameGaps(s7), 1.0)
        self.assertEqual(e.fracSameGaps(e), 0.0)
        self.assertEqual(s4.fracSameGaps(s5), 0.0)
        self.assertEqual(s4.fracSameGaps(s6), 0.5)
        self.assertFloatEqual(s6.fracSameGaps(s8), 2/3.0)
        
    def test_fracDiffGaps(self):
        """Sequence fracDiffGaps should return difference in gap positions"""
        s1 = self.RNA('AAAA')
        s2 = self.RNA('GGGG')
        s3 = self.RNA('----')
        s4 = self.RNA('A-A-')
        s5 = self.RNA('-G-G')
        s6 = self.RNA('UU--')
        s7 = self.RNA('-')
        s8 = self.RNA('GGG')
        e =  self.RNA('')
        self.assertEqual(s1.fracDiffGaps(s1), 0)
        self.assertEqual(s1.fracDiffGaps(s2), 0)
        self.assertEqual(s1.fracDiffGaps(s3), 1)
        self.assertEqual(s1.fracDiffGaps(s4), 0.5)
        self.assertEqual(s1.fracDiffGaps(s5), 0.5)
        self.assertEqual(s1.fracDiffGaps(s6), 0.5)
        self.assertEqual(s1.fracDiffGaps(s7), 1)
        self.assertEqual(s1.fracDiffGaps(e), 0)
        self.assertEqual(s3.fracDiffGaps(s3), 0)
        self.assertEqual(s3.fracDiffGaps(s4), 0.5)
        self.assertEqual(s3.fracDiffGaps(s7), 0.0)
        self.assertEqual(e.fracDiffGaps(e), 0.0)
        self.assertEqual(s4.fracDiffGaps(s5), 1.0)
        self.assertEqual(s4.fracDiffGaps(s6), 0.5)
        self.assertFloatEqual(s6.fracDiffGaps(s8), 1/3.0)

    def test_fracSameNonGaps(self):
        """Sequence fracSameNonGaps should return similarities at non-gaps"""
        s1 = self.RNA('AAAA')
        s2 = self.RNA('AGGG')
        s3 = self.RNA('GGGG')
        s4 = self.RNA('AG--GA-G')
        s5 = self.RNA('CU--CU-C')
        s6 = self.RNA('AC--GC-G')
        s7 = self.RNA('--------')
        s8 = self.RNA('AAAA----')
        s9 = self.RNA('A-GG-A-C')
        e =  self.RNA('')

        test = lambda x, y, z: self.assertFloatEqual(x.fracSameNonGaps(y), z)
        test(s1, s2, 0.25)
        test(s1, s3, 0)
        test(s2, s3, 0.75)
        test(s1, s4, 0.5)
        test(s4, s5, 0)
        test(s4, s6, 0.6)
        test(s4, s7, 0)
        test(s4, s8, 0.5)
        test(s4, s9, 2/3.0)
        test(e, s4, 0)

    def test_fracDiffNonGaps(self):
        """Sequence fracDiffNonGaps should return differences at non-gaps"""
        s1 = self.RNA('AAAA')
        s2 = self.RNA('AGGG')
        s3 = self.RNA('GGGG')
        s4 = self.RNA('AG--GA-G')
        s5 = self.RNA('CU--CU-C')
        s6 = self.RNA('AC--GC-G')
        s7 = self.RNA('--------')
        s8 = self.RNA('AAAA----')
        s9 = self.RNA('A-GG-A-C')
        e =  self.RNA('')

        test = lambda x, y, z: self.assertFloatEqual(x.fracDiffNonGaps(y), z)
        test(s1, s2, 0.75)
        test(s1, s3, 1)
        test(s2, s3, 0.25)
        test(s1, s4, 0.5)
        test(s4, s5, 1)
        test(s4, s6, 0.4)
        test(s4, s7, 0)
        test(s4, s8, 0.5)
        test(s4, s9, 1/3.0)
        test(e, s4, 0)

    def test_fracSimilar(self):
        """Sequence fracSimilar should return the fraction similarity"""
        transitions = dict.fromkeys([ \
            ('A','A'), ('A','G'), ('G','A'), ('G','G'),
            ('U','U'), ('U','C'), ('C','U'), ('C','C')])
        
        s1 = self.RNA('UCAGGCAA')
        s2 = self.RNA('CCAAAUGC')
        s3 = self.RNA('GGGGGGGG')
        e =  self.RNA('')

        test = lambda x, y, z: self.assertFloatEqual( \
            x.fracSimilar(y, transitions), z)

        test(e, e, 0)
        test(s1, e, 0)
        test(s1, s1, 1)
        test(s1, s2, 7.0/8)
        test(s1, s3, 5.0/8)
        test(s2,s3, 4.0/8)

class SequenceSubclassTests(TestCase):
    """Only one general set of tests, since the subclasses are very thin."""
    def test_DnaSequence(self):
        """DnaSequence should behave as expected"""
        x = DnaSequence('tcag', {'Species':'x'})
        assert isinstance(x, Sequence)
        assert isinstance(x, Delegator)
        assert isinstance(x, ConstrainedString)
        self.assertEqual(x, 'tcag')
        self.assertEqual(x.Species, 'x')
        x.Species = 'qwe'
        self.assertEqual(x.Species, 'qwe')
        self.assertEqual(x.Info.Species, 'qwe')
        
        x = DnaSequence('aaa') + DnaSequence('ccc')
        self.assertEqual(x, 'aaaccc')
        self.assertEqual(x.Species, None)
        assert x.Alphabet is DnaAlphabet
        self.assertRaises(ConstraintError, x.__add__, 'z')
        self.assertEqual(DnaSequence('TTTAc').rc(), 'gTAAA')
        x.Species = 'qaz'
        x_f = x.freeze()
        assert x_f.Alphabet is DnaAlphabet
        assert x_f is x
        x_t = x.thaw()
        assert isinstance(x_t, SequenceI)
        assert isinstance(x_t, MutableSequence)
        assert isinstance(x_t, Delegator)
        assert isinstance(x_t, ConstrainedList)
        assert x_t.Alphabet is DnaAlphabet
        self.assertEqual(x_t, list('aaaccc'))
        self.assertEqual(x_t.Species, 'qaz')
        x_t[2:4] = 'tt'
        new_x = x_t.freeze()
        self.assertNotEqual(new_x, x)
        self.assertEqual(new_x, 'aattcc')
        self.assertEqual(new_x.Info, x.Info)

class SequenceCleanerInterfaceTests(SequenceTests):
    """Products of SequenceCleaner should behave the same as the Sequences."""
    SEQ = FunctionWrapper(SequenceCleaner())
    RNA = FunctionWrapper(Rna)
    DNA = FunctionWrapper(Dna)
    PROT = FunctionWrapper(Protein)

class MutableSequenceCleanerInterfaceTests(SequenceTests):
    """Products of SequenceCleaner should behave the same as the Sequences."""
    SEQ = FunctionWrapper(SequenceCleaner())
    RNA = FunctionWrapper(MutableRna)
    DNA = FunctionWrapper(MutableDna)
    PROT = FunctionWrapper(MutableProtein)

class MutableSequenceInterfaceTests(SequenceTests):
    """MutableSequences should behave the same as the Sequences."""
    SEQ = FunctionWrapper(MutableSequence)
    RNA = FunctionWrapper(MutableRna)
    DNA = FunctionWrapper(MutableDna)
    PROT = FunctionWrapper(MutableProtein)

class MutableSequenceTests(TestCase):
    """Mutable sequences should really be mutable."""
    def test_mutable(self):
        """Mutable sequences should really be mutable"""
        r = Rna('ucag-t')
        m = MutableRna(r)
        self.assertEqual(r, 'ucag-u')
        self.assertEqual(m, 'ucag-u')
        self.assertEqual(r, list('ucag-u'))
        self.assertEqual(m, list('ucag-u'))
        self.assertEqual(m, r)
        self.assertEqual(r, m)  #needed to override _both_ cmp methods...
        m[2:5] = 'a'
        self.assertEqual(m, 'ucau')
        try:
            m[-1] = 'x'
        except ConstraintError:
            pass
        else:
            self.fail('Failed to prevent addition of bad item')

class SequenceCleanerTests(TestCase):
    """Tests of some of the products of the SequenceCleaner factory function."""
    def setUp(self):
        """Define some standard sequences"""
        self.na = 'UCAGucagTCAGtcag---NRYWS'            #some nucleic acid chars
        self.na_bad = 'UCAGuc1a!g#TC^&AZGtcag-.~NRYWS'  #...plus some bad chars
        self.seq = 'ACGN TU WS-~.'
        self.seq_bad = self.seq + '@'
    def test_Rna_empty(self):
        """Rna should produce empty RNA string with empty Info"""
        r = Rna()
        self.assertEqual(r, '')
        assert r.Alphabet is RnaAlphabet
        self.assertEqual(r.Info, InfoClass())

    def test_Rna_conversion(self):
        """Rna should silently convert DNA to RNA"""
        na = self.na
        bad = self.na_bad
        self.assertEqual(Rna(na), 'UCAGucagUCAGucag---NRYWS')
        self.assertEqual(Rna(na, strict=True), 'UCAGucagUCAGucag---NRYWS')
        self.assertEqual(Rna(na), 'UCAGucagUCAGucag---NRYWS')
        self.assertEqual(Rna(bad), 'UCAGucagUCAGucag---NRYWS')
        self.assertRaises(ConstraintError, Rna, bad, True)

    def test_Rna_polymorphism(self):
        """Rna should work on any sequence"""
        self.assertEqual(Rna(['U','C','A']), 'UCA')
        self.assertEqual(Rna(('U','C','A')), 'UCA')
        #note that we only use the keys in a dict, and the order can be permuted
        self.assertEqualItems(Rna({'U':3,'C':2,'A':2}), 'UCA')

    def test_standard_instances(self):
        """Rna, Dna, Protein and their friends should do correct conversions"""
        seq = self.seq
        bad = self.seq_bad
        
        self.assertEqual(Rna(seq), 'ACGN-UU-WS---')
        assert Rna(seq).isDegenerate()
        assert Rna(seq).isGapped()
        self.assertEqual(Rna(seq, True), 'ACGN-UU-WS---')
        self.assertEqual(Rna(bad), 'ACGN-UU-WS---')
        self.assertRaises(ConstraintError, Rna, bad, True)

        self.assertEqual(Dna(seq), 'ACGN-TT-WS---')
        assert Dna(seq).isDegenerate()
        assert Dna(seq).isGapped()
        self.assertEqual(Dna(seq, True), 'ACGN-TT-WS---')
        self.assertEqual(Dna(bad), 'ACGN-TT-WS---')
        self.assertRaises(ConstraintError, Dna, bad, True)

        self.assertEqual(Protein(seq), 'ACGN-TU-WS---')
        assert not Protein(seq).isDegenerate()
        assert Protein(seq).isGapped()
        self.assertEqual(Protein(seq, True), 'ACGN-TU-WS---')
        self.assertEqual(Protein(bad), 'ACGN-TU-WS---')
        self.assertRaises(ConstraintError, Protein, bad, True)

        self.assertEqual(RnaUngapped(seq), 'ACGNUUWS')
        assert RnaUngapped(seq).isDegenerate()
        assert not RnaUngapped(seq).isGapped()
        self.assertEqual(RnaUngapped(seq, True), 'ACGNUUWS')
        self.assertEqual(RnaUngapped(bad), 'ACGNUUWS')
        self.assertRaises(ConstraintError, RnaUngapped, bad, True)

        self.assertEqual(DnaUngapped(seq), 'ACGNTTWS')
        assert DnaUngapped(seq).isDegenerate()
        assert not DnaUngapped(seq).isGapped()
        self.assertEqual(DnaUngapped(seq, True), 'ACGNTTWS')
        self.assertEqual(DnaUngapped(bad), 'ACGNTTWS')
        self.assertRaises(ConstraintError, DnaUngapped, bad, True)

        self.assertEqual(ProteinUngapped(seq), 'ACGNTUWS')
        assert not ProteinUngapped(seq).isDegenerate()
        assert not ProteinUngapped(seq).isGapped()
        self.assertEqual(ProteinUngapped(seq, True), 'ACGNTUWS')
        self.assertEqual(ProteinUngapped(bad), 'ACGNTUWS')
        self.assertRaises(ConstraintError, ProteinUngapped, bad, True)

        
        
#run if called from command-line
if __name__ == "__main__":
    main()
