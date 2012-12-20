#!/usr/bin/env python
#file evo/parsers/test_tree.py
"""Unit tests for tree parsers.

Revision History

Written 12/27/03 by Rob Knight

5/21/04 Rob Knight: changed tests to reflect revised string
format for PhyloNode.

11/4/04 Rob Knight: changed PhyloNode tests to reflect the new policy that
branch lengths are suppressed in the output if they are None.
"""
from old_cogent.parse.tree import DndTokenizer, DndParser
from old_cogent.parse.record import RecordError
from old_cogent.base.tree import PhyloNode
from old_cogent.util.unit_test import TestCase, main

sample = """
(
(
xyz:0.28124,
(
def:0.24498,
mno:0.03627)
:0.17710)
:0.04870,

abc:0.05925,
(
ghi:0.06914,
jkl:0.13776)
:0.09853);
"""

node_data_sample = """
(
(
xyz:0.28124,
(
def:0.24498,
mno:0.03627)
'A':0.17710)
B:0.04870,

abc:0.05925,
(
ghi:0.06914,
jkl:0.13776)
C:0.09853);
"""


empty = '();'
single = '(abc:3);'
double = '(abc:3, def:4);'
onenest = '(abc:3, (def:4, ghi:5):6 );'
nodedata = '(abc:3, (def:4, ghi:5)jkl:6 );'

class DndTokenizerTests(TestCase):
    """Tests of the DndTokenizer factory function."""

    def test_data(self):
        """DndTokenizer should work as expected on real data"""
        exp = \
        ['(', '(', 'xyz', ':', '0.28124',',', '(', 'def', ':', '0.24498',\
        ',', 'mno', ':', '0.03627', ')', ':', '0.17710', ')', ':', '0.04870', \
        ',', 'abc', ':', '0.05925', ',', '(', 'ghi', ':', '0.06914', ',', \
        'jkl', ':', '0.13776', ')', ':', '0.09853', ')', ';']
        #split it up for debugging on an item-by-item basis
        obs = list(DndTokenizer(sample))
        self.assertEqual(len(obs), len(exp))
        for i, j in zip(obs, exp):
            self.assertEqual(i, j)
        #try it all in one go
        self.assertEqual(list(DndTokenizer(sample)), exp)


class DndParserTests(TestCase):
    """Tests of the DndParser factory function."""
    def test_empty(self):
        """DndParser should produce an empty PhyloNode on null data"""
        t = DndParser(empty)
        assert not t
        self.assertEqual(t, PhyloNode())
        self.assertEqual(str(t), 'None')

    def test_single(self):
        """DndParser should produce a single-child PhyloNode on minimal data"""
        t = DndParser(single)
        self.assertEqual(len(t), 1)
        child = t[0]
        self.assertEqual(child.Data, 'abc')
        self.assertEqual(child.BranchLength, 3)
        self.assertEqual(str(t), '(abc:3.0)')

    def test_double(self):
        """DndParser should produce a double-child PhyloNode from data"""
        t = DndParser(double)
        self.assertEqual(len(t), 2)
        self.assertEqual(str(t), '(abc:3.0,def:4.0)')

    def test_onenest(self):
        """DndParser should work correctly with nested data"""
        t = DndParser(onenest)
        self.assertEqual(len(t), 2)
        self.assertEqual(len(t[0]), 0)  #first child is terminal
        self.assertEqual(len(t[1]), 2)  #second child has two children
        self.assertEqual(str(t), '(abc:3.0,(def:4.0,ghi:5.0):6.0)')
        
    def test_nodedata(self):
        """DndParser should assign Data to internal nodes correctly"""
        t = DndParser(nodedata)
        self.assertEqual(len(t), 2)
        self.assertEqual(len(t[0]), 0)  #first child is terminal
        self.assertEqual(len(t[1]), 2)  #second child has two children
        self.assertEqual(str(t), '(abc:3.0,(def:4.0,ghi:5.0)jkl:6.0)')
        info_dict = {}
        for node in t.traverse():
            info_dict[node.Data] = node.BranchLength
        self.assertEqual(info_dict['abc'], 3.0)
        self.assertEqual(info_dict['def'], 4.0)
        self.assertEqual(info_dict['ghi'], 5.0)
        self.assertEqual(info_dict['jkl'], 6.0)

    def test_data(self):
        """DndParser should work as expected on real data"""
        t = DndParser(sample)
        tdata = DndParser(node_data_sample)
        self.assertEqual(str(t), '((xyz:0.28124,(def:0.24498,mno:0.03627):0.1771):0.0487,abc:0.05925,(ghi:0.06914,jkl:0.13776):0.09853)')
        self.assertEqual(str(tdata), "((xyz:0.28124,(def:0.24498,mno:0.03627)'A':0.1771)B:0.0487,abc:0.05925,(ghi:0.06914,jkl:0.13776)C:0.09853)")

    def test_bad(self):
        """DndParser should fail if parens unbalanced"""
        left = '((abc:3)'
        right = '(abc:3))'
        self.assertRaises(RecordError, DndParser, left)
        self.assertRaises(RecordError, DndParser, right)

class PhyloNodeTests(TestCase):
    """Check that PhyloNode works the way I think"""
    def test_ops(self):
        """Basic PhyloNode operations should work as expected"""
        p = PhyloNode()
        self.assertEqual(str(p), '()')
        p.Data = 'abc'
        self.assertEqual(str(p), '()abc')
        p.BranchLength = 3
        self.assertEqual(str(p), '()abc')   #suppress branch from root
        q = PhyloNode()
        p.append(q)
        self.assertEqual(str(p), '(None)abc')
        r = PhyloNode()
        q.append(r)
        self.assertEqual(str(p), '((None))abc')
        r.Data = 'xyz'
        self.assertEqual(str(p), '((xyz))abc')
        q.BranchLength = 2
        self.assertEqual(str(p), '((xyz):2)abc')

if __name__ == '__main__':
    main()
