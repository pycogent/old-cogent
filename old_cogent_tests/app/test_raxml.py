#!/bin/env python
#file test_raxml.py
"""
Tests for raxml app controller

Owner: Micah Hamady (hamady@colorado.edu) 

Status: Stub - No tests complete 

Revision History:

10/31/2005 - Initial version written - Micah Hamady

"""
from os import getcwd, remove, rmdir, mkdir
from old_cogent.util.unit_test import TestCase, main
from old_cogent.util.misc import flatten
from old_cogent.app.raxml import Raxml,raxml_alignment
from old_cogent.parse.phylip import get_align_for_phylip
from StringIO import StringIO

class GenericRaxml(TestCase):

    def setUp(self):
        """Setup data for raxml tests"""
        #self.seqs1 = ['ACUGCUAGCUAGUAGCGUACGUA','GCUACGUAGCUAC',
        #    'GCGGCUAUUAGAUCGUA']
        #self.labels1 = ['>1','>2','>3']
        #self.lines1 = flatten(zip(self.labels1,self.seqs1))
        #self.stdout1 = STDOUT1
        #self.aln1 = ALIGN1
        #self.dnd1 = DND1

        #try:
        #    mkdir('/tmp/ct')
        #except OSError: #dir already exists
        #    pass

        #try:
        #    #create sequence files
        #    f = open('/tmp/ct/seq1.txt','w')
        #    f.write('\n'.join(self.lines1))
        #    f.close()

        #except OSError:
        #    pass

        self.align1 = get_align_for_phylip(StringIO(PHYLIP_FILE))



class RaxmlTests(GenericRaxml):
    """Tests for the Raxml application controller"""

    def test_raxml(self):
        """raxml BaseCommand should return the correct BaseCommand"""
        #raise ValueError, "Need to test raxml base command"
        #c = Clustalw()
        #self.assertEqual(c.BaseCommand,\
        #    ''.join(['cd ',getcwd(),'/; ','clustalw -align']))
        #c.Parameters['-infile'].on('seq.txt')
        #self.assertEqual(c.BaseCommand,\
        #    ''.join(['cd ',getcwd(),'/; ','clustalw -infile=seq.txt -align']))
        #c.Parameters['-align'].off()
        #self.assertEqual(c.BaseCommand,\
        #    ''.join(['cd ',getcwd(),'/; ','clustalw -infile=seq.txt']))
        #c.Parameters['-nopgap'].on()
        #c.Parameters['-infile'].off()
        #self.assertEqual(c.BaseCommand,\
        #    ''.join(['cd ',getcwd(),'/; ','clustalw -nopgap']))
        pass

   
class raxmlTests(GenericRaxml):
    """Tests for module level functions in raxml.py"""
   
       
    def test_raxml_alignment(self):
        """raxml_alignment should work as expected"""
        phy_node, parsimony_phy_node, log_likelihood, total_exec \
            = raxml_alignment(self.align1)
    
        #print phy_node, parsimony_phy_node, log_likelihood, total_exec
        #raise ValueError, "Need to test raxml_alignment function "
        #res = alignUnalignedSeqs(self.seqs1,WorkingDir='/tmp/ct')
        #self.assertNotEqual(res['StdErr'],None)
        #self.assertEqual(res['Align'].read(),self.aln1)
        #self.assertEqual(res['Dendro'].read(),self.dnd1)
        #res.cleanUp()
        
        #suppress stderr and stdout
        #res = alignUnalignedSeqs(self.seqs1,WorkingDir='/tmp/ct',\
        #    SuppressStderr=True,SuppressStdout=True)
        #self.assertEqual(res['StdOut'],None)
        #self.assertEqual(res['StdErr'],None)
        #self.assertEqual(res['Align'].read(),self.aln1)
        #self.assertEqual(res['Dendro'].read(),self.dnd1)
        #res.cleanUp()
        pass
    
PHYLIP_FILE= """ 7 50
Species001   UGCAUGUCAG UAUAGCUUUA GUGAAACUGC GAAUGGCUCA UUAAAUCAGU
Species002   UGCAUGUCAG UAUAGCUUUA GUGAAACUGC GAAUGGCUNN UUAAAUCAGU
Species003   UGCAUGUCAG UAUAGCAUUA GUGAAACUGC GAAUGGCUCA UUAAAUCAGU
Species004   UGCAUGUCAG UAUAACUUUG GUGAAACUGC GAAUGGCUCA UUAAAUCAGU
Species005   NNNNNNNNNN UAUAUCUUAU GUGAAACUUC GAAUGCCUCA UUAAAUCAGU
Species006   UGCAUGUCAG UAUAGCUUUG GUGAAACUGC GAAUGGCUCA UUAAAUCAGU
Species007   UGCAUGUCAG UAUAACUUUG GUGAAACUGC GAAUGGCUCA UUAAAUCAGU
""" 

if __name__ == '__main__':
    main()
