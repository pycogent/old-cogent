#!/usr/bin/env python
#file cogent_tests.motif.test_k_word.py

"""Tests for k_word motif finder.

Owner: Jeremy Widmann jeremy.widmann@colorado.edu

Revision History

March 2006 Jeremy Widmann:  File Rewritten. Lost original when HD crashed.
"""

from __future__ import division
from old_cogent.util.unit_test import TestCase, main
from old_cogent.motif.k_word import *
from old_cogent.base.alphabet import DnaAlphabet, RnaAlphabet, ProteinAlphabet
from copy import copy, deepcopy

class KWordModuleFinderTests(TestCase):
    """Tests for KWordModuleFinder.
    """
    
    def setUp(self):
        """Setup function for KWordModuleFinder tests.
        """
        
        self.RnaAlignment = {'seq_0':'ACUCU',
                             'seq_1':'CAUGA',
                             'seq_2':'ACUCUC'}
        self.ProteinAlignment = {
            'seq_0': 'MAELNFKAIEEKWQKRWLEAK',
            'seq_1': 'LNFKAIEEKWQKRWLEAKIFE'}
        
        self.ProteinReduced = {
            'seq_0': 'LGHLSFHGLHHHFSHHFLHGH',
            'seq_1': 'LSFHGLHHHFSHHFLHGHLFH'}
        
        self.RnaModuleDict5 =  {'ACUCU':
        Module({('seq_0', 0): ModuleInstance('ACUCU',Location('seq_0',0,5)),
                ('seq_2', 0): ModuleInstance('ACUCU',Location('seq_2',0,5))}),
                                'CAUGA':
        Module({('seq_1', 0): ModuleInstance('CAUGA',Location('seq_1',0,5))}),
                                'CUCUC':
        Module({('seq_2', 1): ModuleInstance('CUCUC',Location('seq_2',1,6))})}
        
        self.RnaModuleOrder = ['ACUCU', 'CUCUC', 'CAUGA']
        
        self.ProteinModuleDict15 = {'AELNFKAIEEKWQKR': 
        Module({('seq_0', 1):\
            ModuleInstance('AELNFKAIEEKWQKR',Location('seq_0',1,16))}),
                                    'ELNFKAIEEKWQKRW':
        Module({('seq_0', 2):\
            ModuleInstance('ELNFKAIEEKWQKRW',Location('seq_0',2,17))}),
                                    'LNFKAIEEKWQKRWL':
        Module({('seq_0', 3):\
            ModuleInstance('LNFKAIEEKWQKRWL',Location('seq_0',3,18)),
                ('seq_1', 0):
            ModuleInstance('LNFKAIEEKWQKRWL',Location('seq_1',0,15))}),
                                    'FKAIEEKWQKRWLEA':
        Module({('seq_1', 2):\
            ModuleInstance('FKAIEEKWQKRWLEA',Location('seq_1',2,17)),
                ('seq_0', 5):\
            ModuleInstance('FKAIEEKWQKRWLEA',Location('seq_0',5,20))}),
                                    'KAIEEKWQKRWLEAK':
        Module({('seq_1', 3):\
            ModuleInstance('KAIEEKWQKRWLEAK',Location('seq_1',3,18)),
                ('seq_0', 6):
            ModuleInstance('KAIEEKWQKRWLEAK',Location('seq_0',6,21))}),
                                    'AIEEKWQKRWLEAKI':
        Module({('seq_1', 4):\
            ModuleInstance('AIEEKWQKRWLEAKI',Location('seq_1',4,19))}),
                                    'MAELNFKAIEEKWQK':
        Module({('seq_0', 0):\
            ModuleInstance('MAELNFKAIEEKWQK',Location('seq_0',0,15))}),
                                    'NFKAIEEKWQKRWLE':
        Module({('seq_0', 4):\
            ModuleInstance('NFKAIEEKWQKRWLE',Location('seq_0',4,19)),
                ('seq_1', 1):\
            ModuleInstance('NFKAIEEKWQKRWLE',Location('seq_1',1,16))}),
                                    'IEEKWQKRWLEAKIF':
        Module({('seq_1', 5):\
            ModuleInstance('IEEKWQKRWLEAKIF',Location('seq_1',5,20))}),
                                    'EEKWQKRWLEAKIFE':
        Module({('seq_1', 6):\
            ModuleInstance('EEKWQKRWLEAKIFE',Location('seq_1',6,21))})}
        
        self.ProteinModuleOrder = ['NFKAIEEKWQKRWLE','LNFKAIEEKWQKRWL',\
            'KAIEEKWQKRWLEAK','FKAIEEKWQKRWLEA','MAELNFKAIEEKWQK',\
            'IEEKWQKRWLEAKIF','ELNFKAIEEKWQKRW','EEKWQKRWLEAKIFE',\
            'AIEEKWQKRWLEAKI','AELNFKAIEEKWQKR']
        
        self.ProteinReducedDict15 ={'SFHGLHHHFSHHFLH': 
        Module({('seq_0', 4):\
            ModuleInstance('SFHGLHHHFSHHFLH',Location('seq_0',4,19)),
                ('seq_1', 1):\
            ModuleInstance('SFHGLHHHFSHHFLH',Location('seq_1',1,16))}),
                                    'FHGLHHHFSHHFLHG':
        Module({('seq_1', 2):\
            ModuleInstance('FHGLHHHFSHHFLHG',Location('seq_1',2,17)),
                ('seq_0', 5):\
            ModuleInstance('FHGLHHHFSHHFLHG',Location('seq_0',5,20))}),
                                    'GHLSFHGLHHHFSHH':
        Module({('seq_0', 1):\
            ModuleInstance('GHLSFHGLHHHFSHH',Location('seq_0',1,16))}),
                                    'LSFHGLHHHFSHHFL':
        Module({('seq_0', 3):\
            ModuleInstance('LSFHGLHHHFSHHFL',Location('seq_0',3,18)),
                ('seq_1', 0):\
            ModuleInstance('LSFHGLHHHFSHHFL',Location('seq_1',0,15))}),
                                    'GLHHHFSHHFLHGHL':
        Module({('seq_1', 4):\
            ModuleInstance('GLHHHFSHHFLHGHL',Location('seq_1',4,19))}),
                                    'HLSFHGLHHHFSHHF':
        Module({('seq_0', 2):\
            ModuleInstance('HLSFHGLHHHFSHHF',Location('seq_0',2,17))}),
                                    'LGHLSFHGLHHHFSH':
        Module({('seq_0', 0):\
            ModuleInstance('LGHLSFHGLHHHFSH',Location('seq_0',0,15))}),
                                    'HGLHHHFSHHFLHGH': 
        Module({('seq_1', 3):\
            ModuleInstance('HGLHHHFSHHFLHGH',Location('seq_1',3,18)),
                ('seq_0', 6):\
            ModuleInstance('HGLHHHFSHHFLHGH',Location('seq_0',6,21))}),
                                    'LHHHFSHHFLHGHLF':
        Module({('seq_1', 5):\
            ModuleInstance('LHHHFSHHFLHGHLF',Location('seq_1',5,20))}),
                                    'HHHFSHHFLHGHLFH':
        Module({('seq_1', 6):\
            ModuleInstance('HHHFSHHFLHGHLFH',Location('seq_1',6,21))})}
        
        self.ProteinReducedOrder = ['SFHGLHHHFSHHFLH','LSFHGLHHHFSHHFL',\
            'HGLHHHFSHHFLHGH','FHGLHHHFSHHFLHG','LHHHFSHHFLHGHLF',\
            'LGHLSFHGLHHHFSH','HLSFHGLHHHFSHHF','HHHFSHHFLHGHLFH',\
            'GLHHHFSHHFLHGHL','GHLSFHGLHHHFSHH']
    def test_init(self):
        """Tests for __init__ for KWordModuleFinder.
        """
        #Test Rna
        rna_finder = KWordModuleFinder(self.RnaAlignment,RnaAlphabet)
        self.assertEqual(rna_finder.Alignment, self.RnaAlignment)
        self.assertEqual(rna_finder.Alphabet, RnaAlphabet)
        self.assertEqual(rna_finder.ModuleDict,{})
        self.assertEqual(rna_finder.ModuleOrder,[])
        #Test Protein
        protein_finder = KWordModuleFinder(self.ProteinAlignment\
            ,ProteinAlphabet)
        self.assertEqual(protein_finder.Alignment, self.ProteinAlignment)
        self.assertEqual(protein_finder.Alphabet, ProteinAlphabet)
        self.assertEqual(protein_finder.ModuleDict,{})
        self.assertEqual(protein_finder.ModuleOrder,[])
    
    def test_rna_finder(self):
        """Tests KWordModuleFinder for Rna.
        """
        rna_finder = KWordModuleFinder(self.RnaAlignment,RnaAlphabet)
        rna_finder(5)
        self.assertEqual(rna_finder.ModuleDict,self.RnaModuleDict5)
        self.assertEqual(rna_finder.ModuleOrder,self.RnaModuleOrder)
    
    def test_protein_finder(self):
        """Tests KWordModuleFinder for Protein.
        """
        protein_finder = \
            KWordModuleFinder(self.ProteinAlignment,ProteinAlphabet)
        protein_finder(15)
        self.assertEqual(protein_finder.ModuleDict,self.ProteinModuleDict15)
        self.assertEqual(protein_finder.ModuleOrder,self.ProteinModuleOrder)

    def test_protein_reduced_finder(self):
        """Tests KWordModuleFinder for Protein.
        """
        reduced_finder = \
            KWordModuleFinder(self.ProteinReduced,ProteinAlphabet)
        reduced_finder(15)
        self.assertEqual(reduced_finder.ModuleDict,self.ProteinReducedDict15)
        self.assertEqual(reduced_finder.ModuleOrder,self.ProteinReducedOrder)

class KWordModuleConsolidatorNucleotideTests(TestCase):
    """Tests for KWordModuleConsolidatorNucleotide class.
    """
    
    def setUp(self):
        """Set up for KWordModuleConsolidatorNucleotide tests.
        """
        self.RnaAlignment = {'seq_0':'ACUCU',
                             'seq_1':'CAUGA',
                             'seq_2':'ACUCUC'}
        self.KFinder=KWordModuleFinder(self.RnaAlignment,RnaAlphabet)
        self.KFinder(5)
                
        self.RnaModuleDict5 =  {'ACUCU':
        Module({('seq_0', 0): ModuleInstance('ACUCU',Location('seq_0',0,5)),
                ('seq_2', 0): ModuleInstance('ACUCU',Location('seq_2',0,5))}),
                                'CAUGA':
        Module({('seq_1', 0): ModuleInstance('CAUGA',Location('seq_1',0,5))}),
                                'CUCUC':
        Module({('seq_2', 1): ModuleInstance('CUCUC',Location('seq_2',1,6))})}
        
        self.ModulesNoMismatch = [self.RnaModuleDict5['ACUCU'],\
            self.RnaModuleDict5['CUCUC'], self.RnaModuleDict5['CAUGA']]
        
        self.ModulesSixMismatches = copy(self.RnaModuleDict5['ACUCU'])
        self.ModulesSixMismatches.update(copy(self.RnaModuleDict5['CUCUC']))
        self.ModulesSixMismatches.update(copy(self.RnaModuleDict5['CAUGA']))
    
    def test_consolidate_no_mismatch(self):
        """Consolidating allowing no mismatches should return correct Modules.
        """
        k_consolidator=KWordModuleConsolidatorNucleotide(self.KFinder)
        k_consolidator(0)
        self.assertEqual(k_consolidator.Modules,self.ModulesNoMismatch)
    
    def test_consolidate_one_mismatch(self):
        """Consolidating allowing 1 mismatch should return correct Modules.
        """
        k_consolidator=KWordModuleConsolidatorNucleotide(self.KFinder)
        k_consolidator(1)
        self.assertEqual(k_consolidator.Modules,self.ModulesNoMismatch)
    
    def test_consolidate_six_mismatches(self):
        """Consolidating allowing 6 mismatches should result in one Module.
        """
        k_consolidator=KWordModuleConsolidatorNucleotide(self.KFinder)
        k_consolidator(6)
        self.assertEqual(k_consolidator.Modules,[self.ModulesSixMismatches])


class KWordModuleConsolidatorProteinTests(TestCase):
    """Tests for KWordModuleConsolidatorNucleotide class.
    """
    
    def setUp(self):
        """Set up for KWordModuleConsolidatorProtein tests.
        """
        
        self.ProteinAlignment = {
            'seq_0': 'MAELNFKAIEEKWQKRWLEAK',
            'seq_1': 'LNFKAIEEKWQKRWLEAKIFE'}
        
        self.ProteinReduced = {
            'seq_0': 'LGHLSFHGLHHHFSHHFLHGH',
            'seq_1': 'LSFHGLHHHFSHHFLHGHLFH'}
        
        self.KFinderProtein=\
            KWordModuleFinder(self.ProteinAlignment,ProteinAlphabet)
        self.KFinderProtein(15)
        
        self.ProteinModuleDict15 = self.KFinderProtein.ModuleDict
        
        self.ProteinNoMismatch = [\
            self.ProteinModuleDict15['NFKAIEEKWQKRWLE'],
            self.ProteinModuleDict15['LNFKAIEEKWQKRWL'],
            self.ProteinModuleDict15['KAIEEKWQKRWLEAK'],
            self.ProteinModuleDict15['FKAIEEKWQKRWLEA'],
            self.ProteinModuleDict15['MAELNFKAIEEKWQK'],
            self.ProteinModuleDict15['IEEKWQKRWLEAKIF'],
            self.ProteinModuleDict15['ELNFKAIEEKWQKRW'],
            self.ProteinModuleDict15['EEKWQKRWLEAKIFE'],
            self.ProteinModuleDict15['AIEEKWQKRWLEAKI'],
            self.ProteinModuleDict15['AELNFKAIEEKWQKR']]
                
        self.KFinderReduced=\
            KWordModuleFinder(self.ProteinReduced,ProteinAlphabet)
        self.KFinderReduced(15)
        
        self.ReducedModuleDict15 = self.KFinderReduced.ModuleDict
        
        self.ReducedNoMismatch = [\
            self.ReducedModuleDict15['SFHGLHHHFSHHFLH'],
            self.ReducedModuleDict15['LSFHGLHHHFSHHFL'],
            self.ReducedModuleDict15['HGLHHHFSHHFLHGH'],
            self.ReducedModuleDict15['FHGLHHHFSHHFLHG'],
            self.ReducedModuleDict15['LHHHFSHHFLHGHLF'],
            self.ReducedModuleDict15['LGHLSFHGLHHHFSH'],
            self.ReducedModuleDict15['HLSFHGLHHHFSHHF'],
            self.ReducedModuleDict15['HHHFSHHFLHGHLFH'],
            self.ReducedModuleDict15['GLHHHFSHHFLHGHL'],
            self.ReducedModuleDict15['GHLSFHGLHHHFSHH']]
        
        self.ReducedModuleDict15['LGHLSFHGLHHHFSH'].update(\
                self.ReducedModuleDict15['HHHFSHHFLHGHLFH']),
        self.ReducedEightMismatches = [\
            self.ReducedModuleDict15['SFHGLHHHFSHHFLH'],
            self.ReducedModuleDict15['LSFHGLHHHFSHHFL'],
            self.ReducedModuleDict15['HGLHHHFSHHFLHGH'],
            self.ReducedModuleDict15['FHGLHHHFSHHFLHG'],
            self.ReducedModuleDict15['LHHHFSHHFLHGHLF'],
            self.ReducedModuleDict15['LGHLSFHGLHHHFSH'],
            self.ReducedModuleDict15['HLSFHGLHHHFSHHF'],
            self.ReducedModuleDict15['GLHHHFSHHFLHGHL'],
            self.ReducedModuleDict15['GHLSFHGLHHHFSHH']]
        
    
    def test_consolidate_protein_no_mismatch(self):
        """Consolidating allowing no mismatches should return correct Modules.
        """
        k_consolidator=KWordModuleConsolidatorProtein(copy(self.KFinderProtein))
        k_consolidator(0)
        self.assertEqual(k_consolidator.Modules,self.ProteinNoMismatch)
    
    def test_consolidate_protein_one_mismatch(self):
        """Consolidating allowing one mismatches should return correct Modules.
        """
        k_consolidator=KWordModuleConsolidatorProtein(copy(self.KFinderProtein))
        k_consolidator(1)
        self.assertEqual(k_consolidator.Modules,self.ProteinNoMismatch)
    
    def test_consolidate_reduced_no_mismatch(self):
        """Consolidating allowing no mismatches should return correct Modules.
        """
        k_consolidator=KWordModuleConsolidatorProtein(copy(self.KFinderReduced))
        k_consolidator(0)
        self.assertEqual(k_consolidator.Modules,self.ReducedNoMismatch)
    
    def test_consolidate_reduced_ten_mismatches(self):
        """Consolidating allowing one mismatches should return correct Modules.
        """
        k_consolidator=KWordModuleConsolidatorProtein(copy(self.KFinderReduced))
        k_consolidator(8)
        self.assertEqual(k_consolidator.Modules,self.ReducedEightMismatches)

class KWordMotifFinderTests(TestCase):
    """Tests for KWordMotifFinder.
    """
    
    def setUp(self):
        """Set up for KWordMotifFinderTests.
        """
        self.RnaAlignment = {'seq_0':'ACUCU',
                             'seq_1':'CAUGA',
                             'seq_2':'ACUCUC'}
        
        self.RnaModuleFinder = KWordModuleFinder(self.RnaAlignment,RnaAlphabet)
        self.RnaModuleFinder(5)
        self.RnaConsolidator = \
            KWordModuleConsolidatorNucleotide(self.RnaModuleFinder)
        self.RnaConsolidator(0)
        self.RnaMotifs = [Motif(mod) for mod in self.RnaConsolidator.Modules]
        del(mod)

        self.ProteinAlignment = {
            'seq_0': 'MAELNFKAIEEKWQKRWLEAK',
            'seq_1': 'LNFKAIEEKWQKRWLEAKIFE'}
        self.ProteinAlignmentBaseFrequency = \
            {'A': 5, 'E': 8, 'F': 3, 'I': 3, 'K': 8,\
             'M': 1, 'L': 4, 'N': 2, 'Q': 2, 'R': 2, 'W': 4}
        
        self.ProteinModuleFinder = \
            KWordModuleFinder(self.ProteinAlignment,ProteinAlphabet)
        self.ProteinModuleFinder(15)
        self.ProteinConsolidator = \
            KWordModuleFilterProtein(self.ProteinModuleFinder,\
                self.ProteinAlignment)
        self.ProteinConsolidator(0,0)
        self.ProteinMotifs = \
            [Motif(mod) for mod in self.ProteinConsolidator.Modules]
        del(mod)
        
        self.ProteinReduced = {
            'seq_0': 'LGHLSFHGLHHHFSHHFLHGH',
            'seq_1': 'LSFHGLHHHFSHHFLHGHLFH'}
        
        self.ProteinReducedBaseFrequency = \
            {'H': 18, 'S': 4, 'L': 8, 'G': 5, 'F': 7}
        
        self.ReducedModuleFinder = \
            KWordModuleFinder(self.ProteinReduced,ProteinAlphabet)
        self.ReducedModuleFinder(15)
        self.ReducedConsolidator = \
            KWordModuleFilterProtein(self.ReducedModuleFinder,\
                self.ProteinReduced)
        self.ReducedConsolidator(0,0)
        self.ReducedMotifs = \
            [Motif(mod) for mod in self.ReducedConsolidator.Modules]
        del(mod)
    
    def test_motif_finder_rna(self):
        """KWordMotifFinder should return correct RNA motifs.
        """
        #Test with a p-value threshold of 1 to get all motifs
        rna_motif_finder = KWordMotifFinder(self.RnaConsolidator.Modules,\
                                            self.RnaAlignment,\
                                            Mismatches=0,
                                            BaseFrequency={})
        rna_results = rna_motif_finder(1)
        rna_modules = [mod.Modules[0] for mod in rna_results.Motifs]
        self.assertEqual(rna_modules,self.RnaConsolidator.Modules)
   
    def test_motif_finder_protein(self):
        """KWordMotifFinder should return correct Protein motifs.
        """
        #Test with a p-value threshold of 1 to get all motifs
        protein_motif_finder = \
            KWordMotifFinder(self.ProteinConsolidator.Modules,\
            self.ProteinAlignment,Mismatches=0,\
                BaseFrequency=self.ProteinAlignmentBaseFrequency)
        protein_results = protein_motif_finder(1)
        protein_modules = [mod.Modules[0] for mod in protein_results.Motifs]
        self.assertEqual(protein_modules,self.ProteinConsolidator.Modules)

    def test_motif_finder_reduced(self):
        """KWordMotifFinder should return correct reduced Protein motifs.
        """
        #Test with a p-value threshold of 1 to get all motifs
        reduced_motif_finder = \
            KWordMotifFinder(self.ReducedConsolidator.Modules,\
            self.ProteinReduced,Mismatches=0,\
                BaseFrequency=self.ProteinReducedBaseFrequency)
        reduced_results = reduced_motif_finder(1,alphabet_len=5)
        reduced_modules = [mod.Modules[0] for mod in reduced_results.Motifs]
        self.assertEqual(reduced_modules,self.ReducedConsolidator.Modules)

if __name__ == "__main__":
    main()
