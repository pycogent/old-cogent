#!/usr/bin/env python
# test_muscle.py
"""
Provides tests for muscle.py

Owner: Catherine Lozupone (lozupone@colorado.edu)

Status: Development

Revision History:
12/20/06 Cathy Lozupone: started writing
"""
from os import getcwd, remove, rmdir, mkdir
from old_cogent.util.unit_test import TestCase, main
from old_cogent.util.misc import flatten
from old_cogent.app.muscle import Muscle, muscle_seqs, aln_tree_seqs

class GeneralSetUp(TestCase):

    def setUp(self):
        """Muscle general setUp method for all tests"""
        self.seqs1 = ['ACUGCUAGCUAGUAGCGUACGUA','GCUACGUAGCUAC',
            'GCGGCUAUUAGAUCGUA']
        self.labels1 = ['>1','>2','>3']
        self.lines1 = flatten(zip(self.labels1,self.seqs1))

        self.seqs2=['UAGGCUCUGAUAUAAUAGCUCUC','UAUCGCUUCGACGAUUCUCUGAUAGAGA',
            'UGACUACGCAU']
        self.labels2=['>a','>b','>c']
        self.lines2 = flatten(zip(self.labels2,self.seqs2))

        try:
            mkdir('/tmp/ct')
        except OSError: #dir already exists
            pass

        try:
            #create sequence files
            f = open('/tmp/ct/seq1.txt','w')
            f.write('\n'.join(self.lines1))
            f.close()
            g = open('/tmp/ct/seq2.txt','w')
            g.write('\n'.join(self.lines2))
            g.close()
        except OSError:
            pass

class MuscleTests(GeneralSetUp):
    """Tests for the Clustalw application controller"""

    def test_base_command(self):
        """Clustalw BaseCommand should return the correct BaseCommand"""
        c = Muscle()
        self.assertEqual(c.BaseCommand,\
            ''.join(['cd ',getcwd(),'/; ','muscle']))
        c.Parameters['-in'].on('seq.txt')
        self.assertEqual(c.BaseCommand,\
            ''.join(['cd ',getcwd(),'/; ','muscle -in seq.txt']))
        c.Parameters['-cluster2'].on('neighborjoining')
        self.assertEqual(c.BaseCommand,\
            ''.join(['cd ',getcwd(),'/; ','muscle -cluster2 neighborjoining' +
            ' -in seq.txt']))

    def test_changing_working_dir(self):
        """Clustalw BaseCommand should change according to WorkingDir"""
        c = Muscle(WorkingDir='/tmp/muscle_test')
        self.assertEqual(c.BaseCommand,\
            ''.join(['cd ','/tmp/muscle_test','/; ','muscle']))
        c = Muscle()
        c.WorkingDir = '/tmp/muscle_test2'
        self.assertEqual(c.BaseCommand,\
            ''.join(['cd ','/tmp/muscle_test2','/; ','muscle']))
        
        #removing the dirs is proof that they were created at the same time
        #if the dirs are not there, an OSError will be raised
        rmdir('/tmp/muscle_test')
        rmdir('/tmp/muscle_test2')
    
    def test_aln_tree_seqs(self):
        "aln_tree_seqs returns the muscle alignment and tree from iteration2"
        tree, aln = aln_tree_seqs('/tmp/ct/seq1.txt', 
                                   tree_type="neighborjoining",
                                   WorkingDir='/tmp',
                                   clean_up=True)
        self.assertEqual(str(tree), '((1:1.125,2:1.125):0.375,3:1.5)')
        self.assertEqual(len(aln), 6)
        self.assertEqual(aln[-2], '>3\n')
        self.assertEqual(aln[-1], 'GCGGCUAUUAGAUCGUA------\n')

if __name__ == '__main__':
    main()
