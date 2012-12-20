#!/usr/bin/env python
#file evo/test_genetic_code.py

""" Unit tests for Genetic Code classes.

Revision History

8/29-30/03 Greg Caporaso: file creation; __init__, setUp(), test_init(), 
test_str(), test_cmp(), test_translateCodon(), test_translateRNAToProtein, 
main() written. All tests sucessfully complete. 

9/1/03 Rob Knight: cleaned up import statements; changed tests to reflect 
changes in interface (especially immutability and __getitem__). Tests now 
really do use unittest rather than just importing it.

9/5/03 Rob Knight: added tests for the standard genetic codes, and for the
new Name and StartCodons properties.

11/2/03 Rob Knight: added test for Blocks and Anticodons. Changed tests for
aa_lookup so that aa_lookup must now preserve the order of the codons.

2/19/04 Rob Knight: added test for Synonyms.
"""
from old_cogent.base.genetic_code import GeneticCode, GeneticCodeInitError,\
        InvalidCodonError, GeneticCodes
from old_cogent.util.unit_test import TestCase, main


class GeneticCodeTests(TestCase):
    """Tests of the GeneticCode class."""
        
    def setUp(self):
        """Set up some standard genetic code representations."""
        self.SGC = \
            "FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG"
        self.mt = \
            "FFLLSSSSYY**CCWWLLLLPPPPHHQQRRRRIIMMTTTTNNKKSS**VVVVAAAADDEEGGGG"
        self.AllG= \
            "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG"
        
        self.WrongLength= [
            "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG"
            "",
            "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        ]
        self.NcbiStandard = [
        'FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG',
        1,
        'Standard Nuclear',
        '---M---------------M---------------M----------------------------',
        ]

    def test_init(self):
        """GeneticCode init should work with correct-length sequences"""
        sgc = GeneticCode(self.SGC)
        self.assertEqual(sgc['UUU'], 'F')
        mt = GeneticCode(self.mt)
        self.assertEqual(mt['UUU'], 'F')
        allg = GeneticCode(self.AllG)
        self.assertEqual(allg['UUU'], 'G')
        for i in self.WrongLength:
            self.assertRaises(GeneticCodeInitError, GeneticCode, i)

    def test_standard_code(self):
        """Standard genetic code from NCBI should have correct properties"""
        sgc = GeneticCode(*self.NcbiStandard)
        self.assertEqual(sgc.CodeSequence, 
        'FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG')
        self.assertEqual(sgc.StartCodonSequence,
        '---M---------------M---------------M----------------------------')
        self.assertEqual(sgc.StartCodons, {'UUG':'M', 'CUG':'M', 'AUG':'M'})
        self.assertEqual(sgc.ID, 1)
        self.assertEqual(sgc.Name, 'Standard Nuclear')
        self.assertEqual(sgc['UUU'], 'F')
        self.assertEqual(sgc.isStart('ATG'), True)
        self.assertEqual(sgc.isStart('AAA'), False)
        self.assertEqual(sgc.isStop('UAA'), True)
        self.assertEqual(sgc.isStop('AAA'), False)

    def test_standard_code_lookup(self):
        """GeneticCodes should hold codes keyed by id as string and number"""
        sgc_new = GeneticCode(*self.NcbiStandard)
        sgc_number = GeneticCodes[1]
        sgc_string = GeneticCodes['1']
        for sgc in sgc_new, sgc_number, sgc_string: 
            self.assertEqual(sgc.CodeSequence, 
            'FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG')
            self.assertEqual(sgc.StartCodonSequence,
            '---M---------------M---------------M----------------------------')
            self.assertEqual(sgc.StartCodons, {'UUG':'M', 'CUG':'M', 'AUG':'M'})
            self.assertEqual(sgc.ID, 1)
            self.assertEqual(sgc.Name, 'Standard Nuclear')
            self.assertEqual(sgc['UUU'], 'F')
            self.assertEqual(sgc.isStart('ATG'), True)
            self.assertEqual(sgc.isStart('AAA'), False)
            self.assertEqual(sgc.isStop('UAA'), True)
            self.assertEqual(sgc.isStop('AAA'), False)

        mtgc = GeneticCodes[2]
        self.assertEqual(mtgc.Name, 'Vertebrate Mitochondrial')
        self.assertEqual(mtgc.isStart('AUU'), True)
        self.assertEqual(mtgc.isStop('UGA'), False)

        self.assertEqual(sgc_new.changes(mtgc), {'AGA':'R*', 'AGG':'R*', 
            'AUA':'IM', 'UGA':'*W'})
        self.assertEqual(mtgc.changes(sgc_new), {'AGA':'*R', 'AGG':'*R',
            'AUA':'MI', 'UGA':'W*'})
        self.assertEqual(mtgc.changes(mtgc), {})
        self.assertEqual(mtgc.changes(
            'FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'),
            {'AGA':'*R', 'AGG':'*R', 'AUA':'MI', 'UGA':'W*'})


    def test_str(self):
        """GeneticCode str() should return its code string"""
        code_strings = self.SGC, self.mt, self.AllG
        codes = map(GeneticCode, code_strings)
        for code, string in zip(codes, code_strings):
            self.assertEqual(str(code), string)
        #check an example directly in case strings are bad
        self.assertEqual(str(self.SGC), \
            "FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG")

    def test_cmp(self):
        """GeneticCode cmp() should act on code strings"""
        sgc_1 = GeneticCode(self.SGC)
        sgc_2 = GeneticCode(self.SGC)
        self.assertEqual(sgc_1 is sgc_2, False) #ensure different objects
        #self.assertNotEqual(sgc_1, sgc_2) # GREG
        self.assertEqual(sgc_1, sgc_2)
        mtgc = GeneticCode(self.mt)
        self.assertNotEqual(sgc_1, mtgc)

    def test_getitem_codon(self):
        """GeneticCode getitem should return amino acid for codon"""
        #specific checks of a particular codon in the standard code
        variant_codons = ['AUU', 'AuU', 'auu', 'ATT', 'Atu', 'atU']
        sgc = GeneticCode(self.SGC)
        for i in variant_codons:
            self.assertEqual(sgc[i], 'I')
        #full check for the standard code
        codons = [a+b+c for a in 'ucag' for b in 'TCAG' for c in 'UCAG']
        for codon, aa in zip(codons, self.SGC):
            self.assertEqual(sgc[codon], aa)
        #full check for another code
        allg = GeneticCode(self.AllG)
        for codon, aa in zip(codons, self.AllG):
            self.assertEqual(allg[codon], aa)
        #check that degenerate codon returns X
        self.assertEqual(sgc['NNN'], 'X')
        
    def test_getitem_aa(self):
        """GeneticCode getitem should return codon set for aa"""
        #for all G, should return all the codons (in some order)
        allg = GeneticCode(self.AllG)
        codons = [a+b+c for a in 'UCAG' for b in 'UCAG' for c in 'UCAG']
        g_codons = allg['G']
        codons_copy = codons[:]
        self.assertEqual(g_codons, codons_copy)

        #check some known cases in the standard genetic code
        sgc = GeneticCode(self.SGC)
        exp_ile = ['AUU', 'AUC', 'AUA']
        obs_ile = sgc['I']
        self.assertEqual(obs_ile, exp_ile)
        
        exp_arg = ['AGA', 'AGG', 'CGU', 'CGC', 'CGA', 'CGG']
        obs_arg = sgc['R']
        self.assertEqual(obs_ile, exp_ile)

        exp_leu = ['UUA','UUG','CUU','CUC','CUA','CUG']
        obs_leu = sgc['L']
        self.assertEqual(obs_leu, exp_leu)

        exp_met = ['AUG']
        obs_met = sgc['M']
        self.assertEqual(obs_met, exp_met)

        #unknown aa should return []
        self.assertEqual(sgc['U'], [])
        

    def test_getitem_invalid_length(self):
        """GeneticCode getitem should raise InvalidCodonError on wrong length"""
        sgc = GeneticCode(self.SGC)
        self.assertRaises(InvalidCodonError, sgc.__getitem__, 'AAAA')
        self.assertRaises(InvalidCodonError, sgc.__getitem__, 'AA')

    def test_Blocks(self):
        """GeneticCode Blocks should return correct list"""
        sgc = GeneticCode(self.SGC)
        exp_blocks = [
            ['UUU', 'UUC',],
            ['UUA', 'UUG',],
            ['UCU','UCC','UCA','UCG'],
            ['UAU','UAC'],
            ['UAA','UAG'],
            ['UGU','UGC'],
            ['UGA'],
            ['UGG'],
            ['CUU','CUC','CUA','CUG'],
            ['CCU','CCC','CCA','CCG'],
            ['CAU','CAC'],
            ['CAA','CAG'],
            ['CGU','CGC','CGA','CGG'],
            ['AUU','AUC'],
            ['AUA',],
            ['AUG',],
            ['ACU','ACC','ACA','ACG'],
            ['AAU','AAC'],
            ['AAA','AAG'],
            ['AGU','AGC'],
            ['AGA','AGG'],
            ['GUU','GUC','GUA','GUG'],
            ['GCU','GCC','GCA','GCG'],
            ['GAU','GAC'],
            ['GAA','GAG'],
            ['GGU','GGC','GGA','GGG'],
        ]
        self.assertEqual(sgc.Blocks, exp_blocks)

    def test_Anticodons(self):
        """GeneticCode Anticodons should return correct list"""
        sgc = GeneticCode(self.SGC)
        exp_anticodons = {
            'F': ['AAA', 'GAA',],
            'L': ['UAA', 'CAA', 'AAG','GAG','UAG','CAG'],
            'Y': ['AUA','GUA'],
            '*': ['UUA','CUA', 'UCA'],
            'C': ['ACA','GCA'],
            'W': ['CCA'],
            'S': ['AGA','GGA','UGA','CGA','ACU','GCU'],
            'P': ['AGG','GGG','UGG','CGG'],
            'H': ['AUG','GUG'],
            'Q': ['UUG','CUG'],
            'R': ['ACG','GCG','UCG','CCG','UCU','CCU'],
            'I': ['AAU','GAU','UAU'],
            'M': ['CAU',],
            'T': ['AGU','GGU','UGU','CGU'],
            'N': ['AUU','GUU'],
            'K': ['UUU','CUU'],
            'V': ['AAC','GAC','UAC','CAC'],
            'A': ['AGC','GGC','UGC','CGC'],
            'D': ['AUC','GUC'],
            'E': ['UUC','CUC'],
            'G': ['ACC','GCC','UCC','CCC'],
        }
        self.assertEqual(sgc.Anticodons, exp_anticodons)


    def test_translate(self):
        """GeneticCode translate should return correct amino acid string"""
        allg = GeneticCode(self.AllG)
        sgc = GeneticCode(self.SGC)
        mt = GeneticCode(self.mt)

        seq = 'AUGCAUGACUUUUGA'
        #      .  .  .  .  .        markers for codon start
        self.assertEqual(allg.translate(seq), 'GGGGG')
        self.assertEqual(allg.translate(seq, 1), 'GGGG')
        self.assertEqual(allg.translate(seq, 2), 'GGGG')
        self.assertEqual(allg.translate(seq, 3), 'GGGG')
        self.assertEqual(allg.translate(seq, 4), 'GGG')
        self.assertEqual(allg.translate(seq, 12), 'G')
        self.assertEqual(allg.translate(seq, 14), '')
        self.assertRaises(ValueError, allg.translate, seq, 15)
        self.assertRaises(ValueError, allg.translate, seq, 20)

        self.assertEqual(sgc.translate(seq), 'MHDF*')
        self.assertEqual(sgc.translate(seq, 3), 'HDF*')
        self.assertEqual(sgc.translate(seq, 6), 'DF*')
        self.assertEqual(sgc.translate(seq, 9), 'F*')
        self.assertEqual(sgc.translate(seq, 12), '*')
        self.assertEqual(sgc.translate(seq, 14), '')
        #check shortest translatable sequences
        self.assertEqual(sgc.translate('AAA'), 'K')
        self.assertEqual(sgc.translate(''), '')
        
        #check that different code gives different results
        self.assertEqual(mt.translate(seq), 'MHDFW')

        #check translation with invalid codon(s)
        self.assertEqual(sgc.translate('AAANNNCNC123UUU'), 'KXXXF')
        
    def test_sixframes(self):
        """GeneticCode sixframes should provide six-frame translation"""
        
        class fake_rna(str):
            """Fake RNA class with reverse-complement"""
            def __new__(cls, seq, rev):
                return str.__new__(cls, seq)
            def __init__(self, seq, rev):
                self.seq = seq
                self.rev = rev
            def rc(self):
                return self.rev

        test_rna = fake_rna('AUGCUAACAUAAA', 'UUUAUGUUAGCAU')
        #                    .  .  .  .  .    .  .  .  .  .
        sgc = GeneticCode(self.SGC)
        self.assertEqual(sgc.sixframes(test_rna), [
            'MLT*', 'C*HK', 'ANI', 'FMLA', 'LC*H', 'YVS'])

    def test_Synonyms(self):
        """GeneticCode Synonyms should return aa -> codon set mapping."""
        expected_synonyms = {
            'A':['GCU','GCC','GCA','GCG'],
            'C':['UGU', 'UGC'],
            'D':['GAU', 'GAC'],
            'E':['GAA','GAG'],
            'F':['UUU','UUC'],
            'G':['GGU','GGC','GGA','GGG'],
            'H':['CAU','CAC'],
            'I':['AUU','AUC','AUA'],
            'K':['AAA','AAG'],
            'L':['UUA','UUG','CUU','CUC','CUA','CUG'],
            'M':['AUG'],
            'N':['AAU','AAC'],
            'P':['CCU','CCC','CCA','CCG'],
            'Q':['CAA','CAG'],
            'R':['AGA','AGG','CGU','CGC','CGA','CGG'],
            'S':['UCU','UCC','UCA','UCG','AGU','AGC'],
            'T':['ACU','ACC','ACA','ACG'],
            'V':['GUU','GUC','GUA','GUG'],
            'W':['UGG'],
            'Y':['UAU','UAC'],
            '*':['UAA','UAG', 'UGA'],
        }
        obs_synonyms = GeneticCode(self.SGC).Synonyms
        #note that the lists will be arbitrary-order
        for i in expected_synonyms:
            self.assertEqualItems(obs_synonyms[i], expected_synonyms[i])

#Run tests if called from command line
if __name__ == '__main__':
    main()


