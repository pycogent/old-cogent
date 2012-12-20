#!/usr/bin/env python
#file evo/test_alphabet.py

"""Unit tests for Alphabet and Monomer classes: amino acids, bases, etc.

Owner: Rob Knight rob@spot.colorado.edu

Status: Development: feedback requested

Revision History

9/1/03 Rob Knight: initially written.

10/14/03 Rob Knight: changed import statements, added tests.

11/3/03 Rob Knight: added tests for MatchMaker and PairMaker, and for the
various pairing methods of Alphabet.

4/7/04 Rob Knight: added tests for isGap, gapVector, and gapMaps.

6/3/04 Rob Knight: added some specific tests for the RNA alphabet, including
tests for degenerateFromSequence.
"""

from old_cogent.base.alphabet import AminoAcids, Monomer, MatchMaker, PairMaker, \
    Alphabet, DnaAlphabet, RnaAlphabet, ProteinAlphabet
from old_cogent.util.unit_test import TestCase, main
from sets import ImmutableSet

class MonomerTests(TestCase):
    """Tests of the Monomer class, holding data for individual amino acids"""
    def setUp(self):
        self.Ala = Monomer("A", "Ala", "Alanine", 89.09)
        self.Cys = Monomer("C", "Cys", "Cysteine",  121.16)
        self.Glu = Monomer("E", "Glu", "Glutamate",  147.13)

    def test_init_bad(self):
        """Monomer requires all four fields for init"""
        self.assertRaises(TypeError, Monomer,"Ala", "Alanine", 89.09)
        self.assertRaises(TypeError, Monomer,"A", "Alanine", 89.09)
        self.assertRaises(TypeError, Monomer,"A", "Ala", 89.09)
        self.assertRaises(TypeError, Monomer,"A", "Ala", "Alanine")
        self.assertRaises(TypeError, Monomer,"A", "Alanine")

    def test_cmp(self):
        """Monomer cmp should proceed by 1-letter code"""
        self.assertEqual(self.Ala == self.Ala, 1)
        self.assertEqual(self.Ala == self.Cys, 0)
        self.assertEqual(self.Ala < self.Cys, 1)
        self.assertEqual(self.Ala > self.Cys, 0)

    def test_sort(self):
        """Monomer cmp should support sort()"""
        aa = [self.Cys, self.Ala, self.Glu, self.Ala]
        aa.sort()
        self.assertEqual(aa, [self.Ala, self.Ala, self.Cys, self.Glu])

class AminoAcidsTests(TestCase):
    """Tests of the AminoAcids object, containing IUPAC amino acid data."""
    def test_lowercase_matches(self):
        """AminoAcids uppercase and lowercase symbol should return same object"""
        for symbol in "ACDEFGHIKLMNPQRSTVWY*U":
            self.assertEqual(AminoAcids[symbol], AminoAcids[symbol.lower()])

    def test_symbols(self):
        """AminoAcids symbol returned should match 1-letter code"""
        for symbol in "ACDEFGHIKLMNPQRSTVWY*U":
            self.assertEqual(str(AminoAcids[symbol]), symbol)

    def test_names(self):
        """AminoAcids symbol names should be correct"""
        self.assertEqual(AminoAcids['A'].Name, "Alanine")
        self.assertEqual(AminoAcids['U'].Name, "Selenocysteine")

    def test_three_letter(self):
        """AminoAcids three-letter codes should be correct"""
        self.assertEqual(AminoAcids['A'].ThreeLetter, "Ala")

    def test_one_letter(self):
        """AminoAcids one-letter codes should be correct"""
        self.assertEqual(AminoAcids['A'].OneLetter, 'A')

    def test_molecular_weights(self):
        """AminoAcids molecular weights should be correct"""
        self.assertEqual(AminoAcids['C'].MW, 121.16)

class MatchMakerTests(TestCase):
    """Tests of the MatchMaker factory function."""
    def test_init_empty(self):
        """MatchMaker should init ok with no parameters"""
        self.assertEqual(MatchMaker(), {})

    def test_init_monomers(self):
        """MatchMaker with only monomers should produce {(i,i):True}"""
        m = MatchMaker('')
        self.assertEqual(m, {})
        m = MatchMaker('qaz')
        self.assertEqual(m, {('q','q'):True,('a','a'):True,('z','z'):True})
    
    def test_init_gaps(self):
        """MatchMaker with only gaps should match all gaps to each other"""
        m = MatchMaker('', '~!')
        self.assertEqual(m, {('~','~'):True,('!','!'):True,('!','~'):True,
            ('~','!'):True})

    def test_init_degen(self):
        """MatchMaker with only degen should work as expected"""
        m = MatchMaker(None, None, {'x':'ab','y':'bc','z':'cd', 'n':'bcd'})
        self.assertEqual(m, {('x','x'):False, ('x','y'):False, ('x','n'):False,
            ('y','x'):False, ('y','y'):False, ('y','z'):False, ('y','n'):False,
            ('z','y'):False, ('z','z'):False, ('z','n'):False, ('n','x'):False,
            ('n','y'):False, ('n','z'):False, ('n','n'):False})
        assert ('x','z') not in m

    def test_init_all(self):
        """MatchMaker with everything should produce correct dict"""
        m = MatchMaker('ABC',('-','~'),{'X':'AB','Y':('B','C'),'N':list('ABC')})
        exp = {
            ('-','-'):True,
            ('~','~'):True,
            ('-','~'):True,
            ('~','-'):True,
            ('A','A'):True,
            ('B','B'):True,
            ('C','C'):True,
            ('A','X'):False,
            ('X','A'):False,
            ('B','X'):False,
            ('X','B'):False,
            ('B','Y'):False,
            ('Y','B'):False,
            ('C','Y'):False,
            ('Y','C'):False,
            ('A','N'):False,
            ('N','A'):False,
            ('B','N'):False,
            ('N','B'):False,
            ('C','N'):False,
            ('N','C'):False,
            ('X','X'):False,
            ('Y','Y'):False,
            ('N','N'):False,
            ('X','Y'):False,
            ('Y','X'):False,
            ('X','N'):False,
            ('N','X'):False,
            ('Y','N'):False,
            ('N','Y'):False,
            }
        self.assertEqual(m, exp)

class PairMakerTests(TestCase):
    """Tests of the PairMaker factory function."""
    def setUp(self):
        """Define some standard pairs and other data"""
        self.pairs = {('U','A'):True, ('A','U'):True, ('G','U'):False}
    
    def test_init_empty(self):
        """PairMaker should init ok with no parameters"""
        self.assertEqual(PairMaker(), {})

    def test_init_pairs(self):
        """PairMaker with just pairs should equal the original"""
        self.assertEqual(PairMaker(self.pairs), self.pairs)
        assert PairMaker(self.pairs) is not self.pairs
    
    def test_init_monomers(self):
        """PairMaker with pairs and monomers should equal just the pairs"""
        self.assertEqual(PairMaker(self.pairs, 'ABCDEFG'), self.pairs)
        assert PairMaker(self.pairs, 'ABCDEFG') is not self.pairs

    def test_init_gaps(self):
        """PairMaker should add all combinations of gaps as weak pairs"""
        p = PairMaker(self.pairs, None, '-~')
        self.assertNotEqual(p, self.pairs)
        self.pairs.update({('~','~'):False,('-','~'):False,('-','-'):False,
            ('~','-'):False})
        self.assertEqual(p, self.pairs)

    def test_init_degen(self):
        """PairMaker should add in degenerate combinations as weak pairs"""
        p = PairMaker(self.pairs, 'AUG','-', {'R':'AG','Y':'CU','W':'AU'})
        self.assertNotEqual(p, self.pairs)
        self.pairs.update({
        ('-','-'):False,
        ('A','Y'):False,
        ('Y','A'):False,
        ('A','W'):False,
        ('W','A'):False,
        ('U','R'):False,
        ('R','U'):False,
        ('U','W'):False,
        ('W','U'):False,
        ('G','Y'):False,
        ('G','W'):False,
        ('R','Y'):False,
        ('R','W'):False,
        ('Y','R'):False,
        ('Y','W'):False,
        ('W','R'):False,
        ('W','Y'):False,
        ('W','W'):False,
        })
        self.assertEqual(p, self.pairs)
        

class AlphabetTests(TestCase):
    """Tests of the Alphabet class."""
    
    def test_init_minimal(self):
        """Alphabet should init OK with just monomers"""
        a = Alphabet(dict.fromkeys('Abc'))
        assert 'A' in a
        assert 'a' in a
        assert 'b' in a
        assert 'B' not in a
        assert 'x' not in a
    
    def test_init_everything(self):
        """Alphabet should init OK with all parameters set"""
        class has_mw(object):
            """Object with an MW property for testing MW"""
            def __init__(self, mw):
                self.MW = mw
                
        k = dict.fromkeys
        a = Alphabet(k('Abc'), {'d':'bc'}, k('~'), {'b':'c','c':'b'}, 'cab', \
            {}, 3, False)
        a.Monomers['A'] = has_mw(6)
        for i in 'Abcd~':
            assert i in a
        self.assertEqual(a.complement('b'), 'c')
        self.assertEqual(a.complement('AbcAA'), 'AcbAA')
        self.assertEqual(a.firstDegenerate('AbcdA'), 3)
        self.assertEqual(a.firstGap('a~c'), 1)
        self.assertEqual(a.firstInvalid('Abcx'), 3)
        self.assertEqual(a.MW(''), 0)
        self.assertEqual(a.MW('AA~A'), 21)

    def test_stripDegenerate(self):
        """Alphabet stripDegenerate should remove any degenerate bases"""
        s = RnaAlphabet.stripDegenerate
        self.assertEqual(s('UCAG-'), 'UCAG-')
        self.assertEqual(s('NRYSW'), '')
        self.assertEqual(s('USNG'), 'UG')

    def test_stripBad(self):
        """Alphabet stripBad should remove any non-base, non-gap chars"""
        s = RnaAlphabet.stripBad
        self.assertEqual(s('UCAGwsnyrHBND-D'), 'UCAGwsnyrHBND-D')
        self.assertEqual(s('@#^*($@!#&()!@QZX'), '')
        self.assertEqual(s('aaa ggg ---!ccc'), 'aaaggg---ccc')

    def test_stripBadAndGaps(self):
        """Alphabet stripBadAndGaps should remove gaps and bad chars"""
        s = RnaAlphabet.stripBadAndGaps
        self.assertEqual(s('UCAGwsnyrHBND-D'), 'UCAGwsnyrHBNDD')
        self.assertEqual(s('@#^*($@!#&()!@QZX'), '')
        self.assertEqual(s('aaa ggg ---!ccc'), 'aaagggccc')

    def test_complement(self):
        """Alphabet complement should correctly complement sequence"""
        self.assertEqual(RnaAlphabet.complement('UauCG-NR'), 'AuaGC-NY')
        self.assertEqual(DnaAlphabet.complement('TatCG-NR'), 'AtaGC-NY')
        self.assertEqual(RnaAlphabet.complement(''), '')
        self.assertRaises(TypeError, ProteinAlphabet.complement, 'ACD')
        #if it wasn't a string, result should be a list
        self.assertEqual(RnaAlphabet.complement(list('UauCG-NR')), 
            list('AuaGC-NY'))
        self.assertEqual(RnaAlphabet.complement(('a','c')), ('u','g')) 
        #constructor should fail for a dict
        self.assertRaises(ValueError, RnaAlphabet.complement, {'a':'c'})

    def test_rc(self):
        """Alphabet rc should correctly reverse-complement sequence"""
        self.assertEqual(RnaAlphabet.rc('UauCG-NR'), 'YN-CGauA')
        self.assertEqual(DnaAlphabet.rc('TatCG-NR'), 'YN-CGatA')
        self.assertEqual(RnaAlphabet.rc(''), '')
        self.assertEqual(RnaAlphabet.rc('A'), 'U')
        self.assertRaises(TypeError, ProteinAlphabet.rc, 'ACD')
        #if it wasn't a string, result should be a list
        self.assertEqual(RnaAlphabet.rc(list('UauCG-NR')), 
            list('YN-CGauA'))
        self.assertEqual(RnaAlphabet.rc(('a','c')), ('g','u')) 
        #constructor should fail for a dict
        self.assertRaises(ValueError, RnaAlphabet.rc, {'a':'c'})

    def test_contains(self):
        """Alphabet contains should return correct result"""
        for i in 'UCAGWSMKRYBDHVN-' + 'UCAGWSMKRYBDHVN-'.lower():
            assert i in RnaAlphabet
        for i in 'x!@#$%^&ZzQq':
            assert i not in RnaAlphabet
        assert 'Q' in ProteinAlphabet

        a = Alphabet(dict.fromkeys('ABC'), add_lower=True)
        for i in 'abcABC':
            assert i in a
        assert 'x' not in a
        b = Alphabet(dict.fromkeys('ABC'), add_lower=False)
        for i in 'ABC':
            assert i in b
        for i in 'abc':
            assert i not in b

    def test_iter(self):
       """Alphabet iter should iterate over monomer order or sorted keys"""
       self.assertEqual(list(RnaAlphabet), ['U','C','A','G'])
       self.assertEqual(list(DnaAlphabet), ['T','C','A','G'])
       a = Alphabet(dict.fromkeys('ZXCV'))
       self.assertEqual(list(a), ['C','V','X','Z'])

    def test_isGapped(self):
        """Alphabet isGapped should return True if gaps in seq"""
        g = RnaAlphabet.isGapped
        assert not g('')
        assert not g('ACGUCAGUACGUCAGNRCGAUcaguaguacYRNRYRN')
        assert g('-')
        assert g('--')
        assert g('CAGUCGUACGUCAGUACGUacucauacgac-caguACUG')
        assert g('CA--CGUAUGCA-----g')
        assert g('CAGU-')

    def test_isGap(self):
        """Alphabet isGap should return True if char is a gap"""
        g = RnaAlphabet.isGap
        #True for the empty string
        assert not g('')
        #True for all the standard and degenerate symbols
        s = 'ACGUCAGUACGUCAGNRCGAUcaguaguacYRNRYRN'
        assert not g(s)
        for i in s:
            assert not g(i)
        #should be true for a single gap
        assert g('-')
        #note that it _shouldn't_ be true for a run of gaps: use a.isGapped()
        assert not g('--')

    def test_isDegenerate(self):
        """Alphabet isDegenerate should return True if degen symbol in seq"""
        d = RnaAlphabet.isDegenerate
        assert not d('')
        assert not d('UACGCUACAUGuacgucaguGCUAGCUA---ACGUCAG')
        assert d('N')
        assert d('R')
        assert d('y')
        assert d('GCAUguagcucgUCAGUCAGUACgUgcasCUAG')
        assert d('ACGYAUGCUGYEWEWNFMNfuwbybcwuybcjwbeiwfub')

    def test_isValid(self):
        """Alphabet isValid should return True if any unknown symbol in seq"""
        v = RnaAlphabet.isValid
        assert not v(3)
        assert not v(None)
        assert v('ACGUGCAUGUCAYCAYGUACGcaugacyugc----RYNCYRNC')
        assert v('')
        assert v('a')
        assert not v('ACIUBHFWUIXZKLNJUCIHBICNSOWMOINJ')
        assert not v('CAGUCAGUCACA---GACCAUG-_--cgau')

    def test_isStrict(self):
        """Alphabet isStrict should return True if all symbols in Monomers"""
        s = RnaAlphabet.isStrict
        assert not s(3)
        assert not s(None)
        assert s('')
        assert s('A')
        assert s('UAGCACUgcaugcauGCAUGACuacguACAUG')
        assert not s('CAGUCGAUCA-cgaucagUCGAUGAC')
        assert not s('ACGUGCAUXCAGUCAG')

    def test_firstGap(self):
        """Alphabet firstGap should return index of first gap symbol, or None"""
        g = RnaAlphabet.firstGap
        self.assertEqual(g(''), None)
        self.assertEqual(g('a'), None)
        self.assertEqual(g('uhacucHuhacUIUIhacan'), None)
        self.assertEqual(g('-abc'), 0)
        self.assertEqual(g('b-ac'), 1)
        self.assertEqual(g('abcd-'), 4)

    def test_firstDegenerate(self):
        """Alphabet firstDegenerate should return index of first degen symbol"""
        d = RnaAlphabet.firstDegenerate
        self.assertEqual(d(''), None)
        self.assertEqual(d('a'), None)
        self.assertEqual(d('UCGACA--CU-gacucaguacgua'), None)
        self.assertEqual(d('nCAGU'), 0)
        self.assertEqual(d('CUGguagvAUG'), 7)
        self.assertEqual(d('ACUGCUAacgud'), 11)

    def test_firstInvalid(self):
        """Alphabet firstInvalid should return index of first invalid symbol"""
        i = RnaAlphabet.firstInvalid
        self.assertEqual(i(''), None)
        self.assertEqual(i('A'), None)
        self.assertEqual(i('ACGUNVBuacg-wskmWSMKYRryNnN--'), None)
        self.assertEqual(i('x'), 0)
        self.assertEqual(i('rx'), 1)
        self.assertEqual(i('CAGUNacgunRYWSwx'), 15)

    def test_firstNonStrict(self):
        """Alphabet firstNonStrict should return index of first non-strict symbol"""
        s = RnaAlphabet.firstNonStrict
        self.assertEqual(s(''), None)
        self.assertEqual(s('A'), None)
        self.assertEqual(s('ACGUACGUcgaucagu'), None)
        self.assertEqual(s('N'), 0)
        self.assertEqual(s('-'), 0)
        self.assertEqual(s('x'), 0)
        self.assertEqual(s('ACGUcgAUGUGCAUcaguX'), 18)
        self.assertEqual(s('ACGUcgAUGUGCAUcaguX-38243829'), 18)

    def test_disambiguate(self):
        """Alphabet disambiguate should remove degenerate bases"""
        d = RnaAlphabet.disambiguate
        self.assertEqual(d(''), '')
        self.assertEqual(d('AGCUGAUGUA--CAGU'),'AGCUGAUGUA--CAGU')
        self.assertEqual(d('AUn-yrs-wkmCGwmrNMWRKY', 'strip'), 'AU--CG')
        self.assertEqual(d(tuple('AUn-yrs-wkmCGwmrNMWRKY'), 'strip'), \
            tuple('AU--CG'))
        s = 'AUn-yrs-wkmCGwmrNMWRKY'
        t = d(s, 'random')
        u = d(s, 'random')
        for i, j in zip(s, t):
            if i in RnaAlphabet.Degenerates:
                assert j in RnaAlphabet.Degenerates[i]
            else:
                assert i == j
        self.assertNotEqual(t, u)
        self.assertEqual(d(tuple('UCAG'), 'random'), tuple('UCAG'))
        self.assertEqual(len(s), len(t))
        assert RnaAlphabet.firstDegenerate(t) is None
        #should raise exception on unknown disambiguation method
        self.assertRaises(NotImplementedError, d, s, 'xyz')

    def test_degap(self):
        """Alphabet degap should remove all gaps from sequence"""
        g = RnaAlphabet.degap
        self.assertEqual(g(''), '')
        self.assertEqual(g('GUCAGUCgcaugcnvuincdks'), 'GUCAGUCgcaugcnvuincdks')
        self.assertEqual(g('----------------'), '')
        self.assertEqual(g('gcuauacg-'), 'gcuauacg')
        self.assertEqual(g('-CUAGUCA'), 'CUAGUCA')
        self.assertEqual(g('---a---c---u----g---'), 'acug')
        self.assertEqual(g(tuple('---a---c---u----g---')), tuple('acug'))
        
    def test_gapList(self):
        """Alphabet gapList should return correct gap positions"""
        g = RnaAlphabet.gapList
        self.assertEqual(g(''), [])
        self.assertEqual(g('ACUGUCAGUACGHFSDKJCUICDNINS'), [])
        self.assertEqual(g('GUACGUIACAKJDC-SDFHJDSFK'), [14])
        self.assertEqual(g('-DSHFUHDSF'), [0])
        self.assertEqual(g('UACHASJAIDS-'), [11])
        self.assertEqual(g('---CGAUgCAU---ACGHc---ACGUCAGU---'), \
            [0,1,2,11,12,13,19,20,21,30,31,32])
        a = Alphabet(Monomers={'A':1}, Gaps=dict.fromkeys('!@#$%'))
        g = a.gapList
        self.assertEqual(g(''), [])
        self.assertEqual(g('!!!'), [0,1,2])
        self.assertEqual(g('!@#$!@#$!@#$'), range(12))
        self.assertEqual(g('cguua!cgcuagua@cguasguadc#'), [5,14,25])

    def test_gapVector(self):
        """Alphabet gapVector should return correct gap positions"""
        g = RnaAlphabet.gapVector
        self.assertEqual(g(''), [])
        self.assertEqual(g('ACUGUCAGUACGHFSDKJCUICDNINS'), [False]*27)
        self.assertEqual(g('GUACGUIACAKJDC-SDFHJDSFK'), 
         map(bool, map(int,'000000000000001000000000')))
        self.assertEqual(g('-DSHFUHDSF'), 
         map(bool, map(int,'1000000000')))
        self.assertEqual(g('UACHASJAIDS-'), 
         map(bool, map(int,'000000000001')))
        self.assertEqual(g('---CGAUgCAU---ACGHc---ACGUCAGU---'), \
         map(bool, map(int,'111000000001110000011100000000111')))
        a = Alphabet(Monomers={'A':1}, Gaps=dict.fromkeys('!@#$%'))
        g = a.gapVector
        self.assertEqual(g(''), [])
        self.assertEqual(g('!!!'), map(bool, [1,1,1]))
        self.assertEqual(g('!@#$!@#$!@#$'), [True] * 12)
        self.assertEqual(g('cguua!cgcuagua@cguasguadc#'), 
         map(bool, map(int,'00000100000000100000000001')))

    def test_gapMaps(self):
        """Alphabet gapMaps should return dicts mapping gapped/ungapped pos"""
        empty = ''
        no_gaps = 'aaa'
        all_gaps = '---'
        start_gaps = '--abc'
        end_gaps = 'ab---'
        mid_gaps = '--a--b-cd---'
        gm = RnaAlphabet.gapMaps
        self.assertEqual(gm(empty), ({},{}))
        self.assertEqual(gm(no_gaps), ({0:0,1:1,2:2}, {0:0,1:1,2:2}))
        self.assertEqual(gm(all_gaps), ({},{}))
        self.assertEqual(gm(start_gaps), ({0:2,1:3,2:4},{2:0,3:1,4:2}))
        self.assertEqual(gm(end_gaps), ({0:0,1:1},{0:0,1:1}))
        self.assertEqual(gm(mid_gaps), ({0:2,1:5,2:7,3:8},{2:0,5:1,7:2,8:3}))
        
    def test_countGaps(self):
        """Alphabet countGaps should return correct gap count"""
        c = RnaAlphabet.countGaps
        self.assertEqual(c(''), 0)
        self.assertEqual(c('ACUGUCAGUACGHFSDKJCUICDNINS'), 0)
        self.assertEqual(c('GUACGUIACAKJDC-SDFHJDSFK'), 1)
        self.assertEqual(c('-DSHFUHDSF'), 1)
        self.assertEqual(c('UACHASJAIDS-'), 1)
        self.assertEqual(c('---CGAUgCAU---ACGHc---ACGUCAGU---'), 12)
        a = Alphabet(Monomers={'A':1}, Gaps=dict.fromkeys('!@#$%'))
        c = a.countGaps
        self.assertEqual(c(''), 0)
        self.assertEqual(c('!!!'), 3)
        self.assertEqual(c('!@#$!@#$!@#$'), 12)
        self.assertEqual(c('cguua!cgcuagua@cguasguadc#'), 3)

    def test_countDegenerate(self):
        """Alphabet countDegenerate should return correct degen base count"""
        d = RnaAlphabet.countDegenerate
        self.assertEqual(d(''), 0)
        self.assertEqual(d('GACUGCAUGCAUCGUACGUCAGUACCGA'), 0)
        self.assertEqual(d('N'), 1)
        self.assertEqual(d('NRY'), 3)
        self.assertEqual(d('ACGUAVCUAGCAUNUCAGUCAGyUACGUCAGS'), 4)

    def test_possibilites(self):
        """Alphabet possibilities should return correct # possible sequences"""
        p = RnaAlphabet.possibilities
        self.assertEqual(p(''), 1)
        self.assertEqual(p('ACGUgcaucagUCGuGCAU'), 1)
        self.assertEqual(p('N'), 4)
        self.assertEqual(p('R'), 2)
        self.assertEqual(p('H'), 3)
        self.assertEqual(p('nRh'), 24)
        self.assertEqual(p('AUGCnGUCAg-aurGauc--gauhcgauacgws'), 96)
       
    def test_MW(self):
        """Alphabet MW should return correct molecular weight"""
        r = RnaAlphabet.MW
        p = ProteinAlphabet.MW
        self.assertEqual(p(''), 0)
        self.assertEqual(r(''), 0)
        self.assertFloatEqual(p('A'), 107.09)
        self.assertFloatEqual(r('A'), 375.17)
        self.assertFloatEqual(p('AAA'), 285.27)
        self.assertFloatEqual(r('AAA'), 1001.59)
        self.assertFloatEqual(r('AAACCCA'), 2182.37)

    def test_canMatch(self):
        """Alphabet canMatch should return True if all positions can match"""
        m = RnaAlphabet.canMatch
        assert m('', '')
        assert m('UCAG', 'UCAG')
        assert not m('UCAG', 'ucag')
        assert m('UCAG', 'NNNN')
        assert m('NNNN', 'UCAG')
        assert m('NNNN', 'NNNN')
        assert not m('N', 'x')
        assert not m('N', '-')
        assert m('UCAG', 'YYRR')
        assert m('UCAG', 'KMWS')

    def test_canMismatch(self):
        """Alphabet canMismatch should return True on any possible mismatch"""
        m = RnaAlphabet.canMismatch
        assert not m('','')
        assert m('N', 'N')
        assert m('R', 'R')
        assert m('N', 'r')
        assert m('CGUACGCAN', 'CGUACGCAN')
        assert m('U', 'C')
        assert m('UUU', 'UUC')
        assert m('UUU', 'UUY')
        assert not m('UUU', 'UUU')
        assert not m('UCAG', 'UCAG')
        assert not m('U--', 'U--')

    def test_mustMatch(self):
        """Alphabet mustMatch should return True when no possible mismatches"""
        m = RnaAlphabet.mustMatch
        assert m('','')
        assert not m('N', 'N')
        assert not m('R', 'R')
        assert not m('N', 'r')
        assert not m('CGUACGCAN', 'CGUACGCAN')
        assert not m('U', 'C')
        assert not m('UUU', 'UUC')
        assert not m('UUU', 'UUY')
        assert m('UU-', 'UU-')
        assert m('UCAG', 'UCAG')

    def test_canPair(self):
        """Alphabet canPair should return True if all positions can pair"""
        p = RnaAlphabet.canPair
        assert p('', '')
        assert not p('UCAG', 'UCAG')
        assert p('UCAG', 'CUGA')
        assert not p('UCAG', 'cuga')
        assert p('UCAG', 'NNNN')
        assert p('NNNN', 'UCAG')
        assert p('NNNN', 'NNNN')
        assert not p('N', 'x')
        assert not p('N', '-')
        assert p('-', '-')
        assert p('UCAGU', 'KYYRR')
        assert p('UCAG', 'KKRS')
        assert p('U', 'G')

        d = DnaAlphabet.canPair
        assert not d('T', 'G')

    def test_canMispair(self):
        """Alphabet canMispair should return True on any possible mispair"""
        m = RnaAlphabet.canMispair
        assert not m('','')
        assert m('N', 'N')
        assert m('R', 'Y')
        assert m('N', 'r')
        assert m('CGUACGCAN', 'NUHCHUACH')
        assert m('U', 'C')
        assert m('U', 'R')
        assert m('UUU', 'AAR')
        assert m('UUU', 'GAG')
        assert not m('UUU', 'AAA')
        assert not m('UCAG', 'CUGA')
        assert m('U--', '--U')

        d = DnaAlphabet.canPair
        assert d('TCCAAAGRYY', 'RRYCTTTGGA')

    def test_mustPair(self):
        """Alphabet mustPair should return True when no possible mispairs"""
        m = RnaAlphabet.mustPair
        assert m('','')
        assert not m('N', 'N')
        assert not m('R', 'Y')
        assert not m('A', 'A')
        assert not m('CGUACGCAN', 'NUGCGUACG')
        assert not m('U', 'C')
        assert not m('UUU', 'AAR')
        assert not m('UUU', 'RAA')
        assert not m('UU-', '-AA')
        assert m('UCAG', 'CUGA')

        d = DnaAlphabet.mustPair
        assert d('TCCAGGG', 'CCCTGGA')
        assert d('tccaggg', 'ccctgga')
        assert not d('TCCAGGG', 'NCCTGGA')

class RnaAlphabetTests(TestCase):
    """Spot-checks of alphabet functionality applied to RNA alphabet."""
    
    def test_contains(self):
        """RnaAlphabet should __contain__ the expected symbols."""
        keys = 'ucagrymkwsbhvdn?-'
        for k in keys:
            assert k in RnaAlphabet
        for k in keys.upper():
            assert k in RnaAlphabet
        assert 'X' not in RnaAlphabet

    def test_InverseDegens(self):
        """RnaAlphabet should have correct inverse degenerates"""
        degens = [
            ['ucag', 'n'],
            ['ucag-', '?'],
            ['ucg', 'b'],
            ['uag', 'd'],
            ['uca', 'h'],
            ['ug', 'k'],
            ['ca', 'm'],
            ['ag', 'r'],
            ['cg', 's'],
            ['cag', 'v'],
            ['ua', 'w'],
            ['uc', 'y'],
            ['a', 'a'],
            ['c', 'c'],
            ['g', 'g'],
            ['u','u'],
            ['-','-'],
        ]
        
        result = {}
        for key, val in degens:
            result[ImmutableSet(key)] = val
            result[ImmutableSet(key.upper())] = val.upper()

        new_vals = result.values()
        new_vals.sort()

        rna_vals = RnaAlphabet.InverseDegenerates.values()
        rna_vals.sort()
        
        self.assertEqual(''.join(new_vals), ''.join(rna_vals))
        

        self.assertEqual(len(result), len(RnaAlphabet.InverseDegenerates))
            
        self.assertEqual(result, RnaAlphabet.InverseDegenerates)

    def test_degenerateFromSequence(self):
        """RnaAlphabet degenerateFromSequence should give correct results"""
        d = RnaAlphabet.degenerateFromSequence
        #check monomers
        self.assertEqual(d('a'), 'a')
        self.assertEqual(d('C'), 'C')
        #check seq of monomers
        self.assertEqual(d('aaaaa'), 'a')
        #check some 2- to 4-way cases
        self.assertEqual(d('aaaaag'), 'r')
        self.assertEqual(d('ccgcgcgcggcc'), 's')
        self.assertEqual(d('accgcgcgcggcc'), 'v')
        self.assertEqual(d('aaaaagcuuu'), 'n')
        #check some cases with gaps
        self.assertEqual(d('aa---aaagcuuu'), '?')
        self.assertEqual(d('aaaaaaaaaaaaaaa-'), '?')
        self.assertEqual(d('----------------'), '-')
        #check mixed case example
        self.assertEqual(d('AaAAaa'), 'A')

#run if called from command-line
if __name__ == "__main__":
    main()
