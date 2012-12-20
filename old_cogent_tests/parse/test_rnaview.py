#!/usr/bin/env python
# test_rnaview.py

"""
Revision History:
5/18-19/04 Greg Caporaso: file creation, tests for objects to store data
5/20/04 Greg Caporaso: added tests of new WobblePair selectivity, added 
tests of toPairsFromWC and toPairsFromWobble, these need to be expanded once
we're sure that these will stay; tests for some parser methods written
5/21/04 Greg Caporaso: more parser tests written, all written parser 
functionality fully tested
5/24/04 Greg Caporaso: call() tests completed; added tests for functionality 
of translating modified bases in all sequences based on pdb translation table
5/25/04 Greg Caporaso: updated and added some tests after optimization of 
code; added test of BasePairsFromFile
5/26/04 Greg Caporaso: updated tests of toPairs* methods to test reflect that
it now raises a NotImplementedError rather than a BasePairsError
"""

from unittest import TestCase, main 
from old_cogent.parse.rnaview import RnaViewPairsParser, Base, BasePair,\
        BasePairs, BaseInitError, BasePairsInitError, RnaViewParseError,\
        BasePairsError, BasePairsFromFile
from old_cogent.base.sequence import Rna
from old_cogent.base.dict2d import Dict2D

class test_Base(TestCase):
    """ Tests the Base class """
    def setUp(self):
        """ Setup some necessary data for the tests """
        self.sequence = Rna('GCAU')
        self.identity = 'G'
        self.position = 0

    def test_init(self):
        """Base: init functions as expected """
        b = Base(Position=self.position, Identity=self.identity,\
                Sequence=self.sequence)

    def test_invalid_init_position(self):
        """Base: improper initialization position handled """
        
        self.assertRaises(BaseInitError,Base,Position='P',\
                Identity=self.identity, Sequence=self.sequence)
        
    def test_invalid_init_identity(self):
        """Base: improper initialization identity handled """
        #self.assertRaises(BaseInitError,Base,Position=self.position,\
         #       Identity=Base(0,'a',self.sequence), Sequence=self.sequence)
        #Is there anything that can't be converted to a string???
        pass

    def test_invalid_init_sequence(self):
        """Base: improper initialization sequence handled """
        self.assertRaises(BaseInitError,Base,Position=self.position,\
                Identity=self.identity,Sequence='UAC')

    def test_eq(self):
        """Base: == functions as expected """
        # Define a standard to compare others
        b = Base(Position=0,Identity='A',Sequence=Rna('AAUUCCUU'))
        # Identical to b
        b_a = Base(Position=0,Identity='A',Sequence=Rna('AAUUCCUU'))
        # Differ in Position from b
        b_b = Base(Position=1,Identity='A',Sequence=Rna('AAUUCCUU'))
        # Differ in Identity from b
        b_c = Base(Position=0,Identity='C',Sequence=Rna('AAUUCCUU'))
        # Differ in Sequence from b
        b_d = Base(Position=0,Identity='A',Sequence=Rna('AAUUGCUU'))
        # Differ in everything from b
        b_e = Base(Position=4,Identity='G',Sequence=Rna('AAUUCGUU'))
        
        self.assertEqual(b == b, True)
        self.assertEqual(b_a == b, True)
        self.assertEqual(b_b == b, False)
        self.assertEqual(b_c == b, False)
        self.assertEqual(b_d == b, False)
        self.assertEqual(b_e == b, False)

    def test_ne(self):
        """Base: != functions as expected"""
        # Define a standard to compare others
        b = Base(Position=0,Identity='A',Sequence=Rna('AAUUCCUU'))
        # Identical to b
        b_a = Base(Position=0,Identity='A',Sequence=Rna('AAUUCCUU'))
        # Differ in Position from b
        b_b = Base(Position=1,Identity='A',Sequence=Rna('AAUUCCUU'))
        # Differ in Identity from b
        b_c = Base(Position=0,Identity='C',Sequence=Rna('AAUUCCUU'))
        # Differ in Sequence from b
        b_d = Base(Position=0,Identity='A',Sequence=Rna('AAUUGCUU'))
        # Differ in everything from b
        b_e = Base(Position=4,Identity='G',Sequence=Rna('AAUUCGUU'))
        
        self.assertEqual(b != b, False)
        self.assertEqual(b_a != b, False)
        self.assertEqual(b_b != b, True)
        self.assertEqual(b_c != b, True)
        self.assertEqual(b_d != b, True)
        self.assertEqual(b_e != b, True)

class test_BasePair(TestCase):
    """ Tests the BasePair class """
    def setUp(self):
        """ Setup some necessary data for the tests """
        self.upstream = Base(Position=0,Identity='G',\
                Sequence=Rna('GAAAAAC'))
        self.downstream = Base(Position=6, Identity='C',\
                Sequence=Rna('GAAAAAC'))
        self.bpclass = '+/+ cis'

    def test_init(self):
        """BasePair: init functions as expected """
        bp = BasePair(Upstream=self.upstream, Downstream=self.downstream,\
                BpClass=self.bpclass)
    
    def test_eq(self):
        """BasePair: == functions as expected """
        b_a = Base(Position=0,Identity='C',Sequence=Rna('CGUA'))
        b_a1 = Base(Position=0,Identity='C',Sequence=Rna('CGUA'))
        b_b = Base(Position=1,Identity='G',Sequence=Rna('CGUA'))
        b_b1 = Base(Position=1,Identity='G',Sequence=Rna('CGUA'))
        b_c = Base(Position=3,Identity='A',Sequence=Rna('CGUA'))

        # a standard to use for comparisons
        bp = BasePair(Upstream=b_a,Downstream=b_b,BpClass='-/- cis')
        # identical to standard
        bp_a = BasePair(Upstream=b_a1,Downstream=b_b1,BpClass='-/- cis')
        # differing upstream
        bp_b = BasePair(Upstream=b_c,Downstream=b_b,BpClass='-/- cis')
        # differing downstream
        bp_c = BasePair(Upstream=b_a,Downstream=b_c,BpClass='-/- cis')
        # differing BpClass
        bp_d = BasePair(Upstream=b_a,Downstream=b_b,BpClass='+/+ cis')
        # differing everything
        bp_e = BasePair(Upstream=b_c,Downstream=b_a,BpClass='+/+ cis')


        self.assertEqual(bp == bp, True)
        self.assertEqual(bp_a == bp, True)
        self.assertEqual(bp_b == bp, False)
        self.assertEqual(bp_c == bp, False)
        self.assertEqual(bp_d == bp, False)
        self.assertEqual(bp_e == bp, False)

    def test_ne(self):
        """BasePair: != functions as expected """
        b_a = Base(Position=0,Identity='C',Sequence=Rna('CGUA'))
        b_a1 = Base(Position=0,Identity='C',Sequence=Rna('CGUA'))
        b_b = Base(Position=1,Identity='G',Sequence=Rna('CGUA'))
        b_b1 = Base(Position=1,Identity='G',Sequence=Rna('CGUA'))
        b_c = Base(Position=3,Identity='A',Sequence=Rna('CGUA'))

        # a standard to use for comparisons
        bp = BasePair(Upstream=b_a,Downstream=b_b,BpClass='-/- cis')
        # identical to standard
        bp_a = BasePair(Upstream=b_a1,Downstream=b_b1,BpClass='-/- cis')
        # differing upstream
        bp_b = BasePair(Upstream=b_c,Downstream=b_b,BpClass='-/- cis')
        # differing downstream
        bp_c = BasePair(Upstream=b_a,Downstream=b_c,BpClass='-/- cis')
        # differing BpClass
        bp_d = BasePair(Upstream=b_a,Downstream=b_b,BpClass='+/+ cis')
        # differing everything
        bp_e = BasePair(Upstream=b_c,Downstream=b_a,BpClass='+/+ cis')


        self.assertEqual(bp != bp, False)
        self.assertEqual(bp_a != bp, False)
        self.assertEqual(bp_b != bp, True)
        self.assertEqual(bp_c != bp, True)
        self.assertEqual(bp_d != bp, True)
        self.assertEqual(bp_e != bp, True)

    def test_isWC(self):
        """BasePair: isWC() functions as expected """
        A = Base(Position=0,Identity='A',Sequence=Rna('A'))
        G = Base(Position=0,Identity='G',Sequence=Rna('A'))
        C = Base(Position=0,Identity='C',Sequence=Rna('A'))
        U = Base(Position=0,Identity='U',Sequence=Rna('A'))
        a = Base(Position=0,Identity='a',Sequence=Rna('A'))
        g = Base(Position=0,Identity='g',Sequence=Rna('A'))
        c = Base(Position=0,Identity='c',Sequence=Rna('A'))
        u = Base(Position=0,Identity='u',Sequence=Rna('A'))

        self.assertEqual(\
             BasePair(Upstream=A,Downstream=A,BpClass='').isWC(),False)
        self.assertEqual(\
             BasePair(Upstream=A,Downstream=G,BpClass='').isWC(),False)
        self.assertEqual(\
             BasePair(Upstream=A,Downstream=C,BpClass='').isWC(),False)
        self.assertEqual(\
             BasePair(Upstream=A,Downstream=U,BpClass='').isWC(),True)
        self.assertEqual(\
             BasePair(Upstream=A,Downstream=a,BpClass='').isWC(),False)
        self.assertEqual(\
             BasePair(Upstream=A,Downstream=g,BpClass='').isWC(),False)
        self.assertEqual(\
             BasePair(Upstream=A,Downstream=c,BpClass='').isWC(),False)
        self.assertEqual(\
             BasePair(Upstream=A,Downstream=u,BpClass='').isWC(),True)
        self.assertEqual(\
             BasePair(Upstream=G,Downstream=C,BpClass='').isWC(),True)
        self.assertEqual(\
             BasePair(Upstream=g,Downstream=c,BpClass='').isWC(),True)
        self.assertEqual(\
             BasePair(Upstream=C,Downstream=G,BpClass='').isWC(),True)
        self.assertEqual(\
             BasePair(Upstream=G,Downstream=c,BpClass='').isWC(),True)

    def test_isWobble(self):
        """BasePair: isWobble() functions as expected """
        A = Base(Position=0,Identity='A',Sequence=Rna('A'))
        G = Base(Position=0,Identity='G',Sequence=Rna('A'))
        C = Base(Position=0,Identity='C',Sequence=Rna('A'))
        U = Base(Position=0,Identity='U',Sequence=Rna('A'))
        a = Base(Position=0,Identity='a',Sequence=Rna('A'))
        g = Base(Position=0,Identity='g',Sequence=Rna('A'))
        c = Base(Position=0,Identity='c',Sequence=Rna('A'))
        u = Base(Position=0,Identity='u',Sequence=Rna('A'))
        
        self.assertEqual(\
             BasePair(Upstream=G,Downstream=U,BpClass='').isWobble(),True)
        self.assertEqual(\
             BasePair(Upstream=G,Downstream=u,BpClass='').isWobble(),True)
        self.assertEqual(\
             BasePair(Upstream=g,Downstream=U,BpClass='').isWobble(),True)
        self.assertEqual(\
             BasePair(Upstream=g,Downstream=u,BpClass='').isWobble(),True)
        self.assertEqual(\
             BasePair(Upstream=U,Downstream=G,BpClass='').isWobble(),True)
        self.assertEqual(\
             BasePair(Upstream=u,Downstream=g,BpClass='').isWobble(),True)
        self.assertEqual(\
             BasePair(Upstream=A,Downstream=G,BpClass='').isWobble(),False)
        self.assertEqual(\
             BasePair(Upstream=A,Downstream=U,BpClass='').isWobble(),False)
        self.assertEqual(\
             BasePair(Upstream=U,Downstream=A,BpClass='').isWobble(),False)
        self.assertEqual(\
             BasePair(Upstream=G,Downstream=a,BpClass='').isWobble(),False)

class test_BasePairs(TestCase):
    """ Tests the BasePairs class """

    
    def setUp(self):
        """ Setup some necessary data for the tests """
        self.a = Rna('AU') 
        self.b0_a = Base(Position=0,Identity='A',Sequence=self.a)
        self.b1_a = Base(Position=1,Identity='U',Sequence=self.a)

        self.b = Rna('AUCGGUG')
        self.b0_b = Base(Position=0,Identity='A',Sequence=self.b)
        self.b1_b = Base(Position=1,Identity='U',Sequence=self.b)
        self.b2_b = Base(Position=2,Identity='C',Sequence=self.b)
        self.b3_b = Base(Position=3,Identity='G',Sequence=self.b)
        self.b4_b = Base(Position=4,Identity='G',Sequence=self.b)
        self.b5_b = Base(Position=5,Identity='U',Sequence=self.b)
        self.b6_b = Base(Position=6,Identity='G',Sequence=self.b)

        self.c = Rna('ACCGUA')
        self.b0_c = Base(Position=0,Identity='A',Sequence=self.c)
        self.b1_c = Base(Position=1,Identity='C',Sequence=self.c)
        self.b2_c = Base(Position=2,Identity='C',Sequence=self.c)
        self.b3_c = Base(Position=3,Identity='G',Sequence=self.c)
        self.b4_c = Base(Position=4,Identity='U',Sequence=self.c)

        self.wc = [\
         BasePair(Upstream=self.b0_a,Downstream=self.b1_b,BpClass='+/+ cis'),\
         BasePair(Upstream=self.b1_a,Downstream=self.b0_b,BpClass='+/+ cis'),\
         BasePair(Upstream=self.b3_b,Downstream=self.b1_c,BpClass='+/+ cis'),\
         BasePair(Upstream=self.b4_b,Downstream=self.b2_c,BpClass='+/+ cis')]
        self.wc.sort()

        self.wobble = [\
         BasePair(Upstream=self.b5_b,Downstream=self.b3_c,BpClass='+/+ cis'),\
         BasePair(Upstream=self.b6_b,Downstream=self.b4_c,BpClass='+/+ cis')]
        self.wobble.sort()

        self.noncannonical = [\
         BasePair(Upstream=self.b2_b,Downstream=self.b0_c,BpClass='-/- cis')]
        self.noncannonical.sort()

        self.all_bps = [\
         BasePair(Upstream=self.b0_a,Downstream=self.b1_b,BpClass='+/+ cis'),\
         BasePair(Upstream=self.b1_a,Downstream=self.b0_b,BpClass='+/+ cis'),\
         BasePair(Upstream=self.b2_b,Downstream=self.b0_c,BpClass='-/- cis'),\
         BasePair(Upstream=self.b3_b,Downstream=self.b1_c,BpClass='+/+ cis'),\
         BasePair(Upstream=self.b4_b,Downstream=self.b2_c,BpClass='+/+ cis'),\
         BasePair(Upstream=self.b5_b,Downstream=self.b3_c,BpClass='+/+ cis'),\
         BasePair(Upstream=self.b6_b,Downstream=self.b4_c,BpClass='+/+ cis')]
        self.all_bps.sort()

        self.unimol_bps = [\
         BasePair(Upstream=self.b0_b,Downstream=self.b5_b,BpClass='+/+ cis'),\
         BasePair(Upstream=self.b1_b,Downstream=self.b4_b,BpClass='+/+ cis'),\
         BasePair(Upstream=self.b2_b,Downstream=self.b3_b,BpClass='+/+ cis')]
        self.unimol_bps.sort()
        
        self.sequences = [self.a, self.b, self.c]
        self.sequences.sort()

        self.unimol_sequences = [self.b]
        self.unimol_sequences.sort()

    def test_init(self):
        """BasePairs: init returns without error """
        bpl = BasePairs(base_pairs=self.all_bps)

    def test_init_default(self):
        """BasePairs: functions as expected with default parameter"""
        bpl = BasePairs()
        
        # attributes
        self.assertEqual(bpl,[])
        self.assertEqual(bpl._sequences,[])
        
        # properties
        self.assertEqual(list(bpl.Sequences),[])
        self.assertEqual(list(bpl.WCPairs),[])
        self.assertEqual(list(bpl.WobblePairs),[])
        self.assertEqual(list(bpl.NonCannonicalPairs),[])

    def test_invalid_init(self):
        """BasePairs: init correctly detects invalid data """
        # base_pairs not 'list-able'
        self.assertRaises(BasePairsInitError,BasePairs,1)
        # base_pairs 'list-able' but not list of BasePair objects
        self.assertRaises(BasePairsInitError,BasePairs,[5])

    def test_init_sequences(self):
        """BasePairs: init of sequences property functions as expected """
        # _sequences should have all three sequences
        bpl = BasePairs(base_pairs=self.all_bps)
        s = bpl._sequences
        s.sort()
        self.assertEqual(s, self.sequences)

        # _sequences should have sequences b & c
        bpl = BasePairs(base_pairs=self.noncannonical)
        s = bpl._sequences
        s.sort()
        expected = [self.b, self.c]
        expected.sort()
        self.assertEqual(s, expected)

    def test_Sequences(self):
        """BasePairs: iterator of sequences functions as expected """
        bpl = BasePairs(base_pairs=self.all_bps)
        seqs = list(bpl.Sequences)
        seqs.sort()
        self.assertEqual(seqs,self.sequences)

    def test_WCPairs(self):
        """BasePairs: iterator over WC base pairs functions as expected """
        bpl = BasePairs(base_pairs=self.all_bps)
        cpb = list(bpl.WCPairs)
        cpb.sort()
        self.assertEqual(cpb,self.wc)

    def test_WobblePairs(self):
        """BasePairs: iterator over Wobble base pairs functions as expected """
        bpl = BasePairs(base_pairs=self.all_bps)
        wcp = list(bpl.WobblePairs)
        wcp.sort()
        self.assertEqual(wcp,self.wobble)
        
    def test_NonCannonicalPairs(self):
        """BasePairs: iterator over non-cannonical base pairs functions as expected
        """
        bpl = BasePairs(base_pairs=self.all_bps)
        ncpb = list(bpl.NonCannonicalPairs)
        ncpb.sort()
        self.assertEqual(ncpb,self.noncannonical)

    def test_creation_from_iterator(self):
        """BasePairs: can create a new BasePairs from selective iterator """
        bpl = BasePairs(base_pairs=self.all_bps)
        new_bpl = BasePairs(bpl.WCPairs)
        new_seqs = list(new_bpl.Sequences)
        new_seqs.sort()
        self.assertEqual(new_seqs,self.sequences)
        new_bps = list(new_bpl)
        new_bps.sort()
        self.assertEqual(new_bps,self.wc)

    def test_list_iteration(self):
        """BasePairs: iteration over self functions as expected """
        bpl = BasePairs(base_pairs=self.all_bps)
        actual = []
        for bp in bpl:
            actual += [bp]
        actual.sort()
        self.assertEqual(actual,self.all_bps)

        actual = list(bpl)
        actual.sort()
        self.assertEqual(actual,self.all_bps)

    """Need to expand tests for toPairs when creating the InterMolPairs
        object, etc. """

    def test_toPairsFromWC(self):
        """BasePairs: single sequence WC pairs converted to Pairs object """
        bpl = BasePairs(base_pairs=self.unimol_bps)
        p = bpl.toPairsFromWC()
        p_lookup = dict.fromkeys(p)
        for bp in bpl.WCPairs:
            self.assertEqual((bp.Upstream.Position, bp.Downstream.Position)\
                    in p_lookup, True)

    def test_toPairsFromWC_invalid(self):
        """BasePairs: invalid pairs object creation detected (W-C) """
        bpl = BasePairs(base_pairs=self.all_bps)
        self.assertRaises(NotImplementedError,bpl.toPairsFromWC)
        
    def test_toPairsFromWobble(self):
        """BasePairs: single sequence Wobble pairs converted to Pairs object\
        """
        bpl = BasePairs(base_pairs=self.unimol_bps)
        p = bpl.toPairsFromWobble()
        p_lookup = dict.fromkeys(p)
        for bp in bpl.WobblePairs:
            self.assertEqual((bp.Upstream.Position, bp.Downstream.Position)\
                    in p_lookup, True)
    
    def test_toPairsFromWobble_invalid(self):
        """BasePairs: invalid pairs object creation detected (Wobble) """
        bpl = BasePairs(base_pairs=self.all_bps)
        self.assertRaises(NotImplementedError,bpl.toPairsFromWobble)
    
    """ Tests for toInterMolPairs* methods, not yet written
    def test_toInterMolPairsFromWC(self):    
        ""BasePairs: InterMolPairs correctly created from W-C pairs ""
        bpl = BasePairs(base_pairs=self.all_bps)
        p = bpl.toInterMolPairsFromWC()
        p_lookup = dict.fromkeys(p)
        for bp in bpl.WCPairs:
            self.assertEqual((bp.Upstream.Position, bp.Downstream.Position)\
                    in p_lookup, True)
        
    def test_toInterMolPairsFromWobble(self):    
        ""BasePairs: InterMolPairs correctly created from Wobble pairs ""
        bpl = BasePairs(base_pairs=self.all_bps)
        p = bpl.toInterMolPairsFromWobble()
        p_lookup = dict.fromkeys(p)
        for bp in bpl.WobblePairs:
            self.assertEqual((bp.Upstream.Position, bp.Downstream.Position)\
                    in p_lookup, True)
    """

class test_RnaViewPairsParser(TestCase):
    """ Tests for the RNAview base pairs parser """
    def setUp(self):
        """ Setup some data necessary for the tests """
        self.mol1_rnaview = list(single_strand_rnaview.split('\n'))
        self.mol1_pdb = list(single_strand_pdb.split('\n'))
        self.mol1_seqs = {'A':list('GCGACCGAGCCAGCGAAAGUUGGGAGUCGC')}
        
        self.mol2_rnaview = list(double_strand_rnaview.split('\n'))
        self.mol2_pdb = list(double_strand_pdb.split('\n'))
        self.mol2_seqs = {'A':list('CGGACCGAGCCAG'),'B':list('GCUGGGAGUCC'),\
                'C':list('CGGACCGAGCCAG'),'D':list('GCUGGGAGUCC')}

        self.mol3_pdb = list(mixed_strand_pdb.split('\n'))
        self.mol3_seqs = {'A': ['ALA','LYS','MSE','ALA'],\
                'B':list('GGCCGG')}

        self.mol4_pdb = list(modified_bases_single_pdb.split('\n'))
        self.mol4_seqs = {'A':list('GCGGAUUUAgCUCAGuaGGGAGAGCg')}

        self.mol5_pdb = list(modified_bases_double_pdb.split('\n'))
        self.mol5_seqs = {'A':list('Gg'),'B':list('Au')}
   
        self.short_single_rnaview = list(short_single_rnaview.split('\n'))
        self.short_single_seqs = {'A':'GCUC'}
        
        self.short_double_rnaview = list(short_double_rnaview.split('\n'))
        self.short_double_seqs = {'A':'GUU', 'B':'CAC', 'C':'UUU'}
   
        self.short_invalid_rnaview = list(short_invalid_rnaview.split('\n'))
    
    def test_init(self):
        """RnaViewPairsParser: init returns w/o error """
        p = RnaViewPairsParser()

    def test_parse_positions(self):
        """RnaViewPairsParser: positions for bases correctly determined """
        p = RnaViewPairsParser()
        # single strand
        self.assertEqual(p._parse_positions('1_30,'),[0,29])
        # multiple strands
        self.assertEqual(p._parse_positions('2_24,'),[1,23])
        self.assertEqual(p._parse_positions('24_2,'),[23,1])
   
    def test_parse_positions_invalid(self):
        """RnaViewPairsParser: invalid position data handled as expected """
        p = RnaViewPairsParser()
        self.assertRaises(RnaViewParseError,p._parse_bases,'')
        self.assertRaises(RnaViewParseError,p._parse_bases,'_24')
        self.assertRaises(RnaViewParseError,p._parse_bases,'224')
        self.assertRaises(RnaViewParseError,p._parse_bases,'2_')
    
    def test_parse_bases(self):
        """RnaViewPairsParser: identites for bases corectly determined """
        p = RnaViewPairsParser()
        self.assertEqual(p._parse_bases('G-C'),['G','C'])
        self.assertEqual(p._parse_bases('g-c'),['g','c'])
        self.assertEqual(p._parse_bases('A-C'),['A','C'])
        self.assertEqual(p._parse_bases('G-u'),['G','u'])

    def test_parse_bases_invalid(self):
        """RnaViewPairsParser: invalid base identity data handled as expected """
        p = RnaViewPairsParser()
        self.assertRaises(RnaViewParseError,p._parse_bases,'-C')
        self.assertRaises(RnaViewParseError,p._parse_bases,'GC')
        self.assertRaises(RnaViewParseError,p._parse_bases,'G-')
        self.assertRaises(RnaViewParseError,p._parse_bases,'F-C')
        self.assertRaises(RnaViewParseError,p._parse_bases,'C-F')
    
    def test_parse_bpclass(self):
        """RnaViewPairsParser: bpclass parsed correctly"""
        p = RnaViewPairsParser()
        self.assertEqual(p._parse_bpclass('stacked',None),'stacked')
        self.assertEqual(p._parse_bpclass('stacked'),'stacked')
        self.assertEqual(p._parse_bpclass('S/H','tran'),'S/H tran')
        self.assertEqual(p._parse_bpclass('+/+','cis'),'+/+ cis')
        self.assertEqual(p._parse_bpclass('syn','stacked'),'syn stacked')
        self.assertEqual(p._parse_bpclass('syn','XIX'),'syn')
    
    def test_parse_bpclass_invalid(self):
        """RnaViewPairsParser: invalid bpclass data handled as expected """
        p = RnaViewPairsParser()
        # Is anything invalid?
        #self.assertRaises(RnaViewParseError,p._parse_bpclass,45)
  
    def test_parse_pair_seqs(self):
        """RnaViewPairsParser: base -> sequence data parsed correct
        """
        p = RnaViewPairsParser()
        all_seqs = {'A':None,'B':None,'C':None,'D':None}
        # Single sequence
        self.assertEqual(p._parse_pair_seqs(':',':',all_seqs),['A','A']) 
        # Multiple sequences
        self.assertEqual(p._parse_pair_seqs('B:','C:',all_seqs),['B','C']) 
        self.assertEqual(p._parse_pair_seqs('A:','D:',all_seqs),['A','D']) 
        self.assertEqual(p._parse_pair_seqs('C:','B:',all_seqs),['C','B']) 
    
    def test_parse_pair_seqs_invalid(self):
        """RnaViewPairsParser: invalid base -> sequence data handled as expected
        """
        p = RnaViewPairsParser()
        all_seqs = {'A':None,'B':None}
        # missing or invalid sequence
        self.assertRaises(RnaViewParseError,p._parse_pair_seqs,'','B:',all_seqs)
        self.assertRaises(RnaViewParseError,p._parse_pair_seqs,'A:','',all_seqs)
        self.assertRaises(RnaViewParseError,p._parse_pair_seqs,'4:','B:',all_seqs)
        self.assertRaises(RnaViewParseError,p._parse_pair_seqs,'E:','B:',all_seqs)

    def test_adjust_positions(self):
        """RnaViewPairsParser: _adjust_positions() functions as expected """
        p = RnaViewPairsParser()
        all_seqs = {'A':list('uuu'),'B':('cc'),'C':('aaaa')}
        # no adjustment
        pos = [0,1]
        p._adjust_positions(pos,['A','A'],all_seqs)
        self.assertEqual(pos,[0,1])
        # adjust second only
        pos = [0,3]
        p._adjust_positions(pos,['A','B'],all_seqs)
        self.assertEqual(pos,[0,0])
        # adjust first only
        pos = [3,1]
        p._adjust_positions(pos,['B','A'],all_seqs)
        self.assertEqual(pos,[0,1])
        # adjust both
        pos = [4,7]
        p._adjust_positions(pos,['B','C'],all_seqs)
        self.assertEqual(pos,[1,2])

    def test_adjust_stream_order(self):
        """RnaViewPairsParser: stream order determined correctly"""
        p = RnaViewPairsParser()
        all_seqs = {'A':list('uuu'),'B':('cc'),'C':('aaaa')}
        # no adjustment
        self.assertEqual(p._adjust_stream_order([0,1],['A','A'],all_seqs),(0,1))
        self.assertEqual(p._adjust_stream_order([0,1],['A','B'],all_seqs),(0,1))
        self.assertEqual(p._adjust_stream_order([99,1],['A','B'],all_seqs),(0,1))
        self.assertEqual(p._adjust_stream_order([0,1],['A','C'],all_seqs),(0,1))
        self.assertEqual(p._adjust_stream_order([0,1],['B','C'],all_seqs),(0,1))
        self.assertEqual(p._adjust_stream_order([0,1],['B','B'],all_seqs),(0,1))
        # reverse order
        self.assertEqual(p._adjust_stream_order([10,1],['A','A'],all_seqs),(1,0))
        self.assertEqual(p._adjust_stream_order([1,10],['B','A'],all_seqs),(1,0))
        self.assertEqual(p._adjust_stream_order([11,10],['B','A'],all_seqs),(1,0))
        self.assertEqual(p._adjust_stream_order([1,10],['C','A'],all_seqs),(1,0))
        self.assertEqual(p._adjust_stream_order([1,10],['C','B'],all_seqs),(1,0))
    
    def test_parse_base_pair_single_full(self):
        """RnaViewPairsParser: single strand bp line converted to BasePair"""
        p = RnaViewPairsParser()
        # test on a single strand
        l = '1_30,  :     1 G-C    30  : W/W cis         n/a'
        bp_actual = p._parse_base_pair(l, self.mol1_seqs)
        b1 = Base(Position=0,Identity='G',Sequence=Rna(self.mol1_seqs['A']))
        b2 = Base(Position=29,Identity='C',Sequence=Rna(self.mol1_seqs['A']))
        bp_expected =\
            BasePair(Upstream=b1,Downstream=b2,BpClass='W/W cis')
        self.assertEqual(bp_actual,bp_expected)

    def test_parse_base_pair_double_full(self):
        """RnaViewPairsParser: double strand bp line converted to BasePair"""
        # test on a double strand
        p = RnaViewPairsParser()
        l = '2_24, A:    19 G-C    49 B: +/+ cis         XIX'
        bp_actual = p._parse_base_pair(l, self.mol2_seqs)
        b1 = Base(Position=1,Identity='G',Sequence=Rna(self.mol2_seqs['A']))
        b2 = Base(Position=10,Identity='C',Sequence=Rna(self.mol2_seqs['B']))
        bp_expected =\
            BasePair(Upstream=b1,Downstream=b2,BpClass='+/+ cis')
        self.assertEqual(bp_actual,bp_expected)
  
    def test_parse_base_pair_invalid_fields(self):
        """RnaViewPairsParser: invalid fields handled as expected """
        p = RnaViewPairsParser()
        # inserted/deleted fields
        self.assertRaises(RnaViewParseError,p._parse_base_pair,\
                '2_24, A:  hello  19 G-C    49 B: +/+ cis         XIX',\
                self.mol2_seqs)
        self.assertRaises(RnaViewParseError,p._parse_base_pair,\
                '2_24, A:    G-C    49 B: +/+ cis         XIX',\
                self.mol2_seqs)
        self.assertRaises(RnaViewParseError,p._parse_base_pair,\
                '2_24, A:    19 G-C    49 hello B: +/+ cis         XIX',\
                self.mol2_seqs)
        self.assertRaises(RnaViewParseError,p._parse_base_pair,\
                '2_2 cis         XIX',\
                self.mol2_seqs)
        self.assertRaises(RnaViewParseError,p._parse_base_pair,\
                '',\
                self.mol2_seqs)

    def test_get_sequences(self):
        """RnaViewPairsParser: Sequences correctly determined"""
        p = RnaViewPairsParser()
        # single strand test
        s = p._get_sequences(self.mol1_pdb)
        self.assertEqual(s, self.mol1_seqs)
        
        # double strand test
        s = p._get_sequences(self.mol2_pdb)
        self.assertEqual(s, self.mol2_seqs)

        # mixed strand test (ie. protein and RNA, should get both)
        s = p._get_sequences(self.mol3_pdb)
        self.assertEqual(s,self.mol3_seqs)

        # missing sequence data
        s = p._get_sequences([])
        self.assertEqual(s,{})

    def test_build_translation_table(self):
        """RnaViewPairsParser: Translation table for modified bases constructed
        """
        p = RnaViewPairsParser()
        # no data
        self.assertEqual(p._build_translation_table({'A':list('a')},[]),{})
        
        # single strand
        expected = {'A':{'2MG':{9:'g'},\
                'H2U':{15:'u',16:'a'},\
                'M2G':{25:'g'},\
                'OMC':{31:'c'}}}
        self.assertEqual(p._build_translation_table(self.mol4_seqs,\
                self.mol4_pdb),expected)
        
        # double strand
        expected = {'A':{'2MG':{1:'g'}},\
                    'B':{'2MG':{1:'u'}}}
        self.assertEqual(p._build_translation_table(self.mol5_seqs,\
                self.mol5_pdb),expected)

    def test_build_translation_table_invalid(self):
        """RnaViewPairsParser: Invalid translation table data detected """
        p = RnaViewPairsParser()
        all_seqs = {'A':list('a')}
        # Missing fields
        self.assertRaises(RnaViewParseError,p._build_translation_table,\
                all_seqs,\
                ['SEQADV 1EHZ 2MGA   10  GB   M10263      G    10 TRNA'])
        self.assertRaises(RnaViewParseError,p._build_translation_table,\
                all_seqs,\
                ['SEQADV 1EHZ2MG A   10  GB   M10263      G    10 TRNA'])
        self.assertRaises(RnaViewParseError,p._build_translation_table,\
                all_seqs,\
                ['SEQADV 1EHZ 2MG A10  GB   M10263      G    10 TRNA'])
        self.assertRaises(RnaViewParseError,p._build_translation_table,\
                all_seqs,\
                ['SEQADV 1EHZ 2MG A 10GB   M10263      G    10 TRNA'])

    def test_translate_single(self):
        """RnaViewPairsParser: Modified bases translated in single strand """
        p = RnaViewPairsParser()

        # various tests
        # single change
        trans_table = {'A':{'2MG':{1:'g'}}}
        test_seq = {'A':['A','2MG','U']}
        expected = {'A':list('AgU')}
        p._translate(test_seq,trans_table)
        self.assertEqual(test_seq,expected)
       
        # two changes, different modification
        trans_table = {'A':{'2MG':{1:'g'},'H2U':{3:'a'}}}
        test_seq = {'A':['A','2MG','U','H2U']}
        expected = {'A':list('AgUa')}
        p._translate(test_seq,trans_table)
        self.assertEqual(test_seq,expected)
      
        # two changes, same modification
        trans_table = {'A':{'H2U':{1:'g', 3:'a'}}}
        test_seq = {'A':['A','H2U','U','H2U']}
        expected = {'A':list('AgUa')}
        p._translate(test_seq,trans_table)
        self.assertEqual(test_seq,expected)
     

        # single change, one definition not used in translation
        trans_table = {'A':{'2MG':{1:'g'},'H2U':{5:'c'}}}
        test_seq = {'A':['A','2MG','U']}
        expected = {'A':list('AgU')}
        p._translate(test_seq,trans_table)
        self.assertEqual(test_seq,expected)
    
        # combination of all above possibilities
        trans_table = {'A':{'2MG':{1:'g'},\
                'H2U':{2:'u',4:'a'},\
                'M2G':{5:'g'},\
                'OMC':{29:'c'}}}
        test_seq = {'A':['A','2MG','H2U','C','H2U','M2G'] + list('ACGUUUG')}
        expected = {'A':list('AguCagACGUUUG')}
        p._translate(test_seq,trans_table)
        self.assertEqual(test_seq,expected)

    def test_translate_double(self):
        """RnaViewPairsParser: Modified bases translated in double strand """
        p = RnaViewPairsParser()
        
        # two modifications, one in each seq
        trans_table = {'A':{'2MG':{1:'g'}},\
                    'B':{'2MG':{1:'u'}}}
        test_seq = {'A':['A','2MG'], 'B':['C','2MG']}
        expected = {'A':list('Ag'),'B':list('Cu')}
        p._translate(test_seq,trans_table)
        self.assertEqual(test_seq,expected)
        
        # two modifications, both in first seq
        trans_table = {'A':{'2MG':{1:'g'},'GMA':{0:'u'}}}
        test_seq = {'A':['GMA','2MG'], 'B':['C','A']}
        expected = {'A':list('ug'),'B':list('CA')}
        p._translate(test_seq,trans_table)
        self.assertEqual(test_seq,expected)
        
    def test_translate_invalid(self):
        """RnaViewPairsParser: Modified base translation errors handled """
        p = RnaViewPairsParser()
        
        # invalid position -> Identity pairing
        trans_table = {'A':{'2MG':{2:'g'}}}
        test_seq = {'A':['A','2MG','U']}
        self.assertRaises(RnaViewParseError,p._translate,\
                test_seq,trans_table)
        
        # base in sequence doesn't match a base in translation table
        trans_table = {'A':{'2MG':{2:'g'}}}
        test_seq = {'A':['A','2mG','U']}
        self.assertRaises(RnaViewParseError,p._translate,\
                test_seq,trans_table)
        
    def test_get_sequences_modified_bases(self):
        """RnaViewPairsParser: Sequences w/ modifed bases correctly determined
        """
        p = RnaViewPairsParser()

        # single sequence
        self.assertEqual(p._get_sequences(self.mol4_pdb), self.mol4_seqs)
        # two sequences 
        self.assertEqual(p._get_sequences(self.mol5_pdb), self.mol5_seqs)


    def test_parse_base_pairs_correct_number(self):
        """RnaViewPairsParser: parse base pairs return correct size BasePairs
        """
        p = RnaViewPairsParser()
        
        bps = p._parse_base_pairs(self.short_single_rnaview,\
                self.short_single_seqs)
        self.assertEqual(len(bps),2)
        
        bps = p._parse_base_pairs(self.short_double_rnaview,\
                self.short_double_seqs)
        self.assertEqual(len(bps),2)
       
    def test_parse_base_pairs_sequences(self):
        """RnaViewPairsParser: parse base pairs correctly inits _sequences
        """
        p = RnaViewPairsParser()

        bps = p._parse_base_pairs(self.short_single_rnaview,\
                self.short_single_seqs)
        expected_seqs = [Rna(self.short_single_seqs['A'])]
        self.assertEqual(bps._sequences,expected_seqs)

        bps = p._parse_base_pairs(self.short_double_rnaview,\
                self.short_double_seqs)
        expected_seqs = [Rna(self.short_double_seqs['A']),\
            Rna(self.short_double_seqs['B'])]
        expected_seqs.sort()
        actual_seqs = bps._sequences
        actual_seqs.sort()
        self.assertEqual(actual_seqs, expected_seqs)
        
    def test_parse_base_pairs_single_full(self):
        """RnaViewPairsParser: parse base pairs correctly handles single RNA
        """
        p = RnaViewPairsParser()

        b0 = Base(Position=0,Identity='G',Sequence=\
                Rna(self.short_single_seqs['A']))
        b1 = Base(Position=1,Identity='C',Sequence=\
                Rna(self.short_single_seqs['A']))
        b2 = Base(Position=2,Identity='U',Sequence=\
                Rna(self.short_single_seqs['A']))
        b3 = Base(Position=3,Identity='C',Sequence=\
                Rna(self.short_single_seqs['A']))

        bp0 = BasePair(Upstream=b0,Downstream=b3,BpClass='W/W cis')
        bp1 = BasePair(Upstream=b1,Downstream=b3,BpClass='stacked')
        bp_list_expected = BasePairs([bp0,bp1])

        bp_list_actual = p._parse_base_pairs(self.short_single_rnaview,\
                self.short_single_seqs)
        self.assertEqual(bp_list_actual, bp_list_expected)

    def test_parse_base_pairs_double_full(self):
        """RnaViewPairsParser: parse base pairs correctly handles double RNA
        """
        p = RnaViewPairsParser()

        b0 = Base(Position=0,Identity='G',Sequence=\
                Rna(self.short_double_seqs['A']))
        b1 = Base(Position=1,Identity='U',Sequence=\
                Rna(self.short_double_seqs['A']))
        b4 = Base(Position=1,Identity='A',Sequence=\
                Rna(self.short_double_seqs['B']))
        b5 = Base(Position=2,Identity='C',Sequence=\
                Rna(self.short_double_seqs['B']))

        bp0 = BasePair(Upstream=b0,Downstream=b5,BpClass='W/W cis')
        bp1 = BasePair(Upstream=b1,Downstream=b4,BpClass='stacked')
        bp_list_expected = BasePairs([bp0,bp1])

        bp_list_actual = p._parse_base_pairs(self.short_double_rnaview,\
                self.short_double_seqs)
        self.assertEqual(bp_list_actual, bp_list_expected)

    def test_base_pairs_parser_invalid_data(self):
        """RnaViewPairsParser: invalid data correctly handled """
        p = RnaViewPairsParser()
        self.assertRaises(RnaViewParseError,p._parse_base_pairs,\
                self.short_invalid_rnaview, self.short_double_seqs)


    def test_call_single(self):
        """RnaViewPairsParser: call() functions on single sequence"""
        p = RnaViewPairsParser()
        bps = p(self.mol1_rnaview,self.mol1_pdb)
        seq = self.mol1_seqs['A']
        # select tests
        # 1_30
        b0 = Base(Position=0,Identity='G',Sequence=Rna(seq))
        b29 = Base(Position=29,Identity='C',Sequence=Rna(seq))
        bp0 = BasePair(Upstream=b0,Downstream=b29,BpClass='W/W cis')
        self.assertEqual(bps[0],bp0)
        
        # 6_7
        b5 = Base(Position=5,Identity='C',Sequence=Rna(seq))
        b6 = Base(Position=6,Identity='G',Sequence=Rna(seq))
        bp8 = BasePair(Upstream=b5,Downstream=b6,BpClass='syn stacked')
        self.assertEqual(bps[8],bp8)
        
        # 15_17
        b14 = Base(Position=14,Identity='G',Sequence=Rna(seq))
        b16 = Base(Position=16,Identity='A',Sequence=Rna(seq))
        bp24 = BasePair(Upstream=b14,Downstream=b16,BpClass='S/S tran')
        self.assertEqual(bps[24],bp24)
        
    def test_call_double(self):
        """RnaViewPairsParser: call() functions on double sequence """
        p = RnaViewPairsParser()
        bps = p(self.mol2_rnaview,self.mol2_pdb)
        A = self.mol2_seqs['A'] 
        B = self.mol2_seqs['B'] 

        # select tests
        # 2_24
        b1 = Base(Position=1,Identity='G',Sequence=Rna(A))
        b23 = Base(Position=10,Identity='C',Sequence=Rna(B))
        bp0 = BasePair(Upstream=b1,Downstream=b23,BpClass='+/+ cis')
        self.assertEqual(bp0,bps[0])

        # 14_15 (both on B strand)
        b13 = Base(Position=0,Identity='G',Sequence=Rna(B))
        b14 = Base(Position=1,Identity='C',Sequence=Rna(B))
        bp8 = BasePair(Upstream=b13,Downstream=b14,BpClass='stacked')
        self.assertEqual(bp8,bps[8])

        # 6_20
        b5 = Base(Position=5,Identity='C',Sequence=Rna(A))
        b19 = Base(Position=6,Identity='A',Sequence=Rna(B))
        bp9 = BasePair(Upstream=b5,Downstream=b19,BpClass='S/W cis')
        self.assertEqual(bp9,bps[9])

class test_BasePairsFromFile(TestCase):

    def setUp(self):
        self.mol1_rnaview = list(single_strand_rnaview.split('\n'))
        self.mol1_pdb = list(single_strand_pdb.split('\n'))
        self.mol1_seqs = {'A':list('GCGACCGAGCCAGCGAAAGUUGGGAGUCGC')}
        
        self.mol2_rnaview = list(double_strand_rnaview.split('\n'))
        self.mol2_pdb = list(double_strand_pdb.split('\n'))
        self.mol2_seqs = {'A':list('CGGACCGAGCCAG'),'B':list('GCUGGGAGUCC'),\
                'C':list('CGGACCGAGCCAG'),'D':list('GCUGGGAGUCC')}

    def test_single(self):
        """BasePairsFromFile: functions on single strand of RNA"""
        bps = BasePairsFromFile(self.mol1_rnaview,self.mol1_pdb)
        seq = self.mol1_seqs['A']
        # select tests
        # 1_30
        b0 = Base(Position=0,Identity='G',Sequence=Rna(seq))
        b29 = Base(Position=29,Identity='C',Sequence=Rna(seq))
        bp0 = BasePair(Upstream=b0,Downstream=b29,BpClass='W/W cis')
        self.assertEqual(bps[0],bp0)
        
        # 6_7
        b5 = Base(Position=5,Identity='C',Sequence=Rna(seq))
        b6 = Base(Position=6,Identity='G',Sequence=Rna(seq))
        bp8 = BasePair(Upstream=b5,Downstream=b6,BpClass='syn stacked')
        self.assertEqual(bps[8],bp8)
        
        # 15_17
        b14 = Base(Position=14,Identity='G',Sequence=Rna(seq))
        b16 = Base(Position=16,Identity='A',Sequence=Rna(seq))
        bp24 = BasePair(Upstream=b14,Downstream=b16,BpClass='S/S tran')
        self.assertEqual(bps[24],bp24)

    def test_double(self):
        """BasePairsFromFile: functions of double strand of RNA """
        bps = BasePairsFromFile(self.mol2_rnaview,self.mol2_pdb)
        A = self.mol2_seqs['A'] 
        B = self.mol2_seqs['B'] 

        # select tests
        # 2_24
        b1 = Base(Position=1,Identity='G',Sequence=Rna(A))
        b23 = Base(Position=10,Identity='C',Sequence=Rna(B))
        bp0 = BasePair(Upstream=b1,Downstream=b23,BpClass='+/+ cis')
        self.assertEqual(bps[0],bp0)

        # 14_15 (both on B strand)
        b13 = Base(Position=0,Identity='G',Sequence=Rna(B))
        b14 = Base(Position=1,Identity='C',Sequence=Rna(B))
        bp8 = BasePair(Upstream=b13,Downstream=b14,BpClass='stacked')
        self.assertEqual(bps[8],bp8)

        # 6_20
        b5 = Base(Position=5,Identity='C',Sequence=Rna(A))
        b19 = Base(Position=6,Identity='A',Sequence=Rna(B))
        bp9 = BasePair(Upstream=b5,Downstream=b19,BpClass='S/W cis')
        self.assertEqual(bps[9],bp9)

######Data########

single_strand_rnaview =\
"""
PDB data file name: 2LDZ.pdb_nmr.pdb
BEGIN_base-pair
     1_30,  :     1 G-C    30  : W/W cis         n/a
      2_3,  :     2 C-G     3  :      stacked
     2_29,  :     2 C-G    29  : +/+ cis         XIX
     2_30,  :     2 C-C    30  : W/W cis         n/a
     3_28,  :     3 G-C    28  : W/W cis         n/a
     4_27,  :     4 A-U    27  : -/- cis         XX
      5_6,  :     5 C-C     6  :      stacked
     5_26,  :     5 C-G    26  : +/+ cis         XIX
      6_7,  :     6 C-G     7  :   syn  stacked
     6_25,  :     6 C-A    25  : W/W cis         n/a
    10_23,  :    10 C-G    23  : +/+ cis         XIX
    11_22,  :    11 C-G    22  : +/+ cis         XIX
    12_13,  :    12 A-G    13  :      stacked
    12_21,  :    12 A-U    21  : -/- cis         XX
    13_14,  :    13 G-C    14  :      stacked
    13_20,  :    13 G-U    20  : W/W cis         XXVIII
    14_19,  :    14 C-G    19  : +/+ cis         XIX
    17_18,  :    17 A-A    18  :      stacked
    18_19,  :    18 A-G    19  :      stacked
    21_22,  :    21 U-G    22  :      stacked
    26_27,  :    26 G-U    27  :      stacked
    28_29,  :    28 C-G    29  :      stacked
    29_30,  :    29 G-C    30  :      stacked
    15_18,  :    15 G-A    18  : S/H tran        !1H(b_b).
    15_17,  :    15 G-A    17  : S/S tran        !(s_s)
END_base-pair
  The total base pairs =  12 (from   30 bases)
------------------------------------------------
 Standard  WW--cis  WW-tran  HH--cis  HH-tran  SS--cis  SS-tran
        7        5        0        0        0        0        0
  WH--cis  WH-tran  WS--cis  WS-tran  HS--cis  HS-tran
        0        0        0        0        0        0
------------------------------------------------
"""

# pdb file is truncated to save space: most ATOM and REMARK lines removed
single_strand_pdb=\
"""
HEADER    CATALYTIC RNA                           18-AUG-98   2LDZ              
TITLE     SOLUTION STRUCTURE OF THE LEAD-DEPENDENT RIBOZYME, NMR,               
TITLE    2 MINIMIZED AVERAGE STRUCTURE                                          
COMPND    MOL_ID: 1;                                                            
COMPND   2 MOLECULE: LEAD-DEPENDENT RIBOZYME;                                   
COMPND   3 CHAIN: NULL;                                                         
COMPND   4 SYNONYM: LEADZYME;                                                   
COMPND   5 ENGINEERED: YES;                                                     
COMPND   6 BIOLOGICAL_UNIT: MONOMER;                                            
COMPND   7 OTHER_DETAILS: MOLECULE IS RNA                                       
SOURCE    MOL_ID: 1;                                                            
SOURCE   2 SYNTHETIC: NON-BIOLOGICAL SEQUENCE;                                  
SOURCE   3 OTHER_DETAILS: PREPARED BY IN VITRO TRANSCRIPTION FROM               
SOURCE   4 SYNTHETIC DNA TEMPLATE                                               
KEYWDS    CATALYTIC RNA, INTERNAL LOOPS, LEADZYME, NMR SPECTROSCOPY,            
KEYWDS   2 RNA STRUCTURE                                                        
EXPDTA    NMR, MINIMIZED AVERAGE STRUCTURE                                      
AUTHOR    C.G.HOOGSTRATEN,P.LEGAULT,A.PARDI                                     
REVDAT   1   23-FEB-99 2LDZ    0                                                
JRNL        AUTH   C.G.HOOGSTRATEN,P.LEGAULT,A.PARDI                            
JRNL        TITL   NMR SOLUTION STRUCTURE OF THE LEAD-DEPENDENT                 
JRNL        TITL 2 RIBOZYME: EVIDENCE FOR DYNAMICS IN RNA CATALYSIS             
JRNL        REF    J.MOL.BIOL.                   V. 284   337 1998              
JRNL        REFN   ASTM JMOBAK  UK ISSN 0022-2836                 0070          
REMARK   1                                                                      
REMARK   1 REFERENCE 1                                                          
REMARK   1  AUTH   P.LEGAULT,C.G.HOOGSTRATEN,E.METLITZKY,A.PARDI                
REMARK   1  TITL   ORDER, DYNAMICS AND METAL-BINDING IN THE                     
REMARK   1  TITL 2 LEAD-DEPENDENT RIBOZYME                                      
REMARK   1  REF    J.MOL.BIOL.                   V. 284   325 1998              
REMARK   1  REFN   ASTM JMOBAK  UK ISSN 0022-2836                 0070          
REMARK   1 REFERENCE 2                                                          
REMARK   1  AUTH   T.PAN,B.DICHTL,O.C.UHLENBECK                                 
REMARK   1  TITL   PROPERTIES OF AN IN VITRO SELECTED PB2+ CLEAVAGE             
REMARK   1  TITL 2 MOTIF                                                        
REMARK   1  REF    BIOCHEMISTRY                  V.  33  9561 1994              
REMARK 900                                                                      
REMARK 900 RELATED ENTRIES                                                      
REMARK 900 PDB ENTRY 1LDZ IS THE SET OF 25 MODELS.                              
DBREF  2LDZ      1    30  PDB    2LDZ     2LDZ             1     30             
SEQRES   1     30    G   C   G   A   C   C   G   A   G   C   C   A   G          
SEQRES   2     30    C   G   A   A   A   G   U   U   G   G   G   A   G          
SEQRES   3     30    U   C   G   C                                              
SITE     1 SCS  2   C     6    G     7                                          
CRYST1    1.000    1.000    1.000  90.00  90.00  90.00 P 1           1          
ORIGX1      1.000000  0.000000  0.000000        0.00000                         
ORIGX2      0.000000  1.000000  0.000000        0.00000                         
ORIGX3      0.000000  0.000000  1.000000        0.00000                         
SCALE1      1.000000  0.000000  0.000000        0.00000                         
SCALE2      0.000000  1.000000  0.000000        0.00000                         
SCALE3      0.000000  0.000000  1.000000        0.00000                         
ATOM      1  O5*   G     1     -32.512  -6.647   2.341  1.00  4.64           O  
ATOM      2  C5*   G     1     -31.953  -7.420   3.407  1.00  4.73           C  
ATOM      3  C4*   G     1     -31.559  -6.542   4.592  1.00  4.97           C  
ATOM      4  O4*   G     1     -30.801  -7.278   5.554  1.00  5.08           O  
"""

double_strand_rnaview=\
"""
PDB data file name: 429d.pdb1
BEGIN_base-pair
     2_24, A:    19 G-C    49 B: +/+ cis         XIX
     3_23, A:    20 G-C    48 B: +/+ cis         XIX
     4_22, A:    21 A-U    47 B: -/- cis         XX
     5_21, A:    22 C-G    46 B: +/+ cis         XIX
    10_18, A:    27 C-G    43 B: +/+ cis         XIX
    11_17, A:    28 C-G    42 B: +/+ cis         XIX
    12_16, A:    29 A-U    41 B: -/- cis         XX
    13_15, A:    30 G-C    40 B: +/+ cis         XIX
    14_15, B:    39 G-C    40 B:      stacked
     6_20, A:    23 C-A    45 B: S/W cis         !1H(b_b)
END_base-pair
  The total base pairs =   8 (from   24 bases)
------------------------------------------------
 Standard  WW--cis  WW-tran  HH--cis  HH-tran  SS--cis  SS-tran
        8        0        0        0        0        0        0
  WH--cis  WH-tran  WS--cis  WS-tran  HS--cis  HS-tran
        0        0        0        0        0        0
------------------------------------------------
"""

# pdb files are truncated to save space, most ATOM fields removed
double_strand_pdb=\
"""
HEADER    RNA                                     29-SEP-98   XXXX              
TITLE     CRYSTAL STRUCTURE OF A LEADZYME; METAL BINDING AND                    
TITLE    2 IMPLICATIONS FOR CATALYSIS                                           
COMPND    5'-R(*CP*GP*GP*AP*CP*CP*GP*AP*GP*CP*CP*AP*G)-3', 5'-                  
COMPND   2 R(*GP*CP*UP*GP*GP*GP*AP*GP* UP*CP*C)-3'                              
KEYWDS    LEADZYME, LEAD-DEPENDENT CLEAVAGE, TRNA INTERNAL LOOP, RNA,           
KEYWDS   2 BULGED NUCLEOTIDES                                                   
EXPDTA    X-RAY DIFFRACTION                                                     
AUTHOR    J. E.WEDEKIND, D. B.MCKAY                                             
JRNL        AUTH   J.E.WEDEKIND, D.B.MCKAY                                      
JRNL        TITL   CRYSTAL STRUCTURE OF A LEAD-DEPENDENT RIBOZYME               
JRNL        TITL 2 REVEALING METAL BINDING SITES RELEVANT TO                    
JRNL        TITL 3 CATALYSIS.                                                   
JRNL        REF    NAT.STRUCT.BIOL.              V.   6   261 1999              
JRNL        REFN   ASTM NSBIEW  US ISSN 1072-8368                               
REMARK   1                                                                      
SEQRES   1 A   13    C   G   G   A   C   C   G   A   G   C   C   A   G          
SEQRES   1 B   11    G   C   U   G   G   G   A   G   U   C   C                  
SEQRES   1 C   13    C   G   G   A   C   C   G   A   G   C   C   A   G          
SEQRES   1 D   11    G   C   U   G   G   G   A   G   U   C   C                  
HETNAM      MG MAGNESIUM ION                                                    
FORMUL   5   MG    2(MG1 2+)                                                    
CRYST1   60.400   60.400  133.100  90.00  90.00 120.00 P 61 2 2     24          
ORIGX1      1.000000  0.000000  0.000000        0.00000                         
ORIGX2      0.000000  1.000000  0.000000        0.00000                         
ORIGX3      0.000000  0.000000  1.000000        0.00000                         
SCALE1      0.016556  0.009559  0.000000        0.00000                         
SCALE2      0.000000  0.019118  0.000000        0.00000                         
SCALE3      0.000000  0.000000  0.007513        0.00000                         
ATOM      1  O5*   C A  18      18.811  37.348  48.634  1.00 15.82           O  
ATOM      2  C5*   C A  18      17.564  38.007  48.873  1.00 20.67           C  
ATOM      3  C4*   C A  18      16.399  37.147  48.432  1.00 22.08           C  
ATOM      4  O4*   C A  18      16.105  37.391  47.021  1.00 19.57           O  
ATOM      5  C3*   C A  18      16.627  35.646  48.524  1.00 20.06           C  
ATOM      6  O3*   C A  18      16.443  35.167  49.859  1.00 21.76           O  
ATOM      7  C2*   C A  18      15.632  35.109  47.490  1.00 17.81           C  
ATOM      8  O2*   C A  18      14.294  35.055  47.915  1.00 11.18           O  
ATOM      9  C1*   C A  18      15.742  36.171  46.395  1.00 17.51           C  
ATOM     10  N1    C A  18      16.775  35.820  45.408  1.00 16.15           N  
ATOM     11  C2    C A  18      16.470  34.849  44.460  1.00 15.72           C  
"""

# from 1CX0.pdb
mixed_strand_pdb =\
"""
SEQRES   8 A   4  ALA LYS MSE ALA
SEQRES   1 B   6    G   G   C   C   G   G
"""

# from 1EHZ.pdb
modified_bases_single_pdb=\
"""
SEQADV 1EHZ 2MG A   10  GB   M10263      G    10 TRNA
SEQADV 1EHZ H2U A   16  GB   M10263      U    16 TRNA
SEQADV 1EHZ H2U A   17  GB   M10263      A    17 TRNA
SEQADV 1EHZ M2G A   26  GB   M10263      G    26 TRNA
SEQADV 1EHZ OMC A   32  GB   M10263      C    32 TRNA
SEQRES   1 A   76    G   C   G   G   A   U   U   U   A 2MG   C   U   C
SEQRES   2 A   76    A   G H2U H2U   G   G   G   A   G   A   G   C M2G
"""

modified_bases_double_pdb=\
"""
SEQADV 1EHZ 2MG A   2   GB   M10263      G    10 TRNA
SEQADV 1EHZ 2MG B   4   GB   M10263      U    16 TRNA
SEQRES   1 A   76    G   2MG  
SEQRES   2 B   76    A   2MG
"""

#GCUC
short_single_rnaview =\
"""
PDB data file name: fake.pdb
BEGIN_base-pair
      1_4,  :     1 G-C     4  : W/W cis         n/a
      2_4,  :     2 C-C     4  :      stacked
END_base-pair
  The total base pairs =  2 (from   3 bases)
------------------------------------------------
 Standard  WW--cis  WW-tran  HH--cis  HH-tran  SS--cis  SS-tran
        7        5        0        0        0        0        0
  WH--cis  WH-tran  WS--cis  WS-tran  HS--cis  HS-tran
        0        0        0        0        0        0
------------------------------------------------
"""
# GUU CAC
short_double_rnaview =\
"""
PDB data file name: fake.pdb
BEGIN_base-pair
      1_6,  A:     1 G-C     6 B: W/W cis         n/a
      2_5,  A:     2 U-A     5 B:      stacked
END_base-pair
  The total base pairs =  2 (from   3 bases)
------------------------------------------------
 Standard  WW--cis  WW-tran  HH--cis  HH-tran  SS--cis  SS-tran
        7        5        0        0        0        0        0
  WH--cis  WH-tran  WS--cis  WS-tran  HS--cis  HS-tran
        0        0        0        0        0        0
------------------------------------------------
"""
short_invalid_rnaview =\
"""
PDB data file name: fake.pdb
BEGIN_base-pair
      _4,  :     1 G-C     4  : W/W cis         n/a
      2_4,  :     2 C-C     4  :      stacked
END_base-pair
  The total base pairs =  2 (from   3 bases)
------------------------------------------------
 Standard  WW--cis  WW-tran  HH--cis  HH-tran  SS--cis  SS-tran
        7        5        0        0        0        0        0
  WH--cis  WH-tran  WS--cis  WS-tran  HS--cis  HS-tran
        0        0        0        0        0        0
------------------------------------------------
"""
if __name__ == '__main__':
    main()
    
