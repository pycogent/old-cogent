#!/usr/bin/env python
#file evo/test_tree.py
"""Tests of classes for dealing with trees and phylogeny.

Owner: Rob Knight rob@spot.colorado.edu

Revision History

9/17/03 Rob Knight: originally written for PyEvolve. 

9/25/03 Rob Knight: added test to make sure node can't be its own ancestor.

10/14/03 Rob Knight: added Children property.

10/29/03 Rob Knight: added Siblings property. Also added test for slicing after
discovering inauspicious interaction with ConstrainedList __getslice__ and
__getitem__, which dutifully coerce the result into the same class as self,
even though in this case the result must be a list and not a TreeNode since
a node can only have one parent.

12/27/03 Rob Knight: changed PhyloNode str() slightly to better handle edge
cases (in particular, suppress 'None' for nodes without data).

2/17/04 Rob Knight: added test to make sure it's possible to set a slice to
what it was already.

2/19/04 Rob Knight: added tests for traverse().

3/24/04 Rob Knight: added tests for copy and deepcopy from the copy module.
Specifically, copy should always fail (can't have a proper shallow copy since
Parent/Child relations break), but deepcopy should always succeed.

5/21/04 Rob Knight: changed PhyloNode str tests to allow None values and to 
check that the PAUP-compatible output works.

7/14/04 Cathy Lozupone: changed PhyloNode str() test to reflect change where
branchlengths set to None are ignored

2/8/06 Rob Knight: added tests for attrTable and friends.
"""
from copy import copy, deepcopy
from old_cogent.base.tree import TreeNode, TreeError, DuplicateNodeError, PhyloNode
from old_cogent.parse.tree import DndParser
from old_cogent.util.unit_test import TestCase, main
from Numeric import array, resize, sqrt
from MLab import std as stdev
from sets import Set

class TreeNodeTests(TestCase):
    """Tests of the TreeNode class."""

    def setUp(self):
        """Define some standard TreeNode for testing"""
        self.Empty = TreeNode()
        self.Single = TreeNode(Data='a')
        self.Child = TreeNode(Data='b')
        self.OneChild = TreeNode(Data='a', Children=[self.Child])
        self.Multi = TreeNode(Data = 'a', Children='bcd')
        self.Repeated = TreeNode(Data='x', Children='aaa')
        self.BigData = map(TreeNode, '0123456789')
        self.BigParent = TreeNode(Data = 'x', Children = self.BigData)
        self.Comparisons = map(TreeNode, 'aab')
        
        nodes = dict([(x, TreeNode(x)) for x in 'abcdefgh'])
        nodes['a'].append(nodes['b'])
        nodes['b'].append(nodes['c'])
        nodes['c'].append(nodes['d'])
        nodes['c'].append(nodes['e'])
        nodes['c'].append(nodes['f'])
        nodes['f'].append(nodes['g'])
        nodes['a'].append(nodes['h'])
        self.TreeNode = nodes
        self.TreeRoot = nodes['a']
   
    def test_init_empty(self):
        """Empty TreeNode should init OK"""
        t = self.Empty
        self.assertEqual(t.Data, None)
        self.assertEqual(t.Parent, None)
        self.assertEqual(len(t), 0)

    def test_init_full(self):
        """TreeNode should init OK with parent, data, and children"""
        t = self.Empty
        u = TreeNode(Parent=t, Data='abc', Children='xyz')
        self.assertEqual(u.Data, 'abc')
        assert u.Parent is t
        assert u in t
        self.assertEqual(u[0].Data, 'x')
        self.assertEqual(u[1].Data, 'y')
        self.assertEqual(u[2].Data, 'z')
        self.assertEqual(len(u), 3)

    def test_Data(self):
        """TreeNode should forward attributes to self.Data"""
        t = self.Single
        self.assertEqual(t.upper(), 'A')
        t.Data = {3:'a'}
        self.assertEqual(t.keys(), [3])
        self.assertRaises(AttributeError, getattr, t, 'upper')
        t.Data = 'x'
        self.assertEqual(t.upper(), 'X')
        self.assertRaises(AttributeError, getattr, t, 'keys')

    def test_Parent(self):
        """TreeNode Parent should hold correct data and be mutable"""
        #check initial conditions
        self.assertEqual(self.Single.Parent, None)
        #set parent and check parent/child relations
        self.Single.Parent = self.Empty
        assert self.Single.Parent is self.Empty
        self.assertEqual(self.Empty[0], self.Single)
        assert self.Single in self.Empty
        self.assertEqual(len(self.Empty), 1)
        #check that we can't make a node its own parent
        try:
            self.Single.Parent = self.Single
        except TreeError:
            pass
        else:
            self.fail, "Shouldn't allow node to be its own parent."
        #reset parent and check parent/child relations
        self.Single.Parent = self.OneChild
        assert self.Single.Parent is self.OneChild
        assert self.Single not in self.Empty
        assert self.Single is self.OneChild[-1]

        #following is added to check that we don't screw up when there are
        #nodes with different ids that still compare equal
        last = self.Repeated[-1]
        last.Parent = self.OneChild
        self.assertEqual(len(self.Repeated),  2)
        for i in self.Repeated:
            assert i.Parent is self.Repeated
        assert last.Parent is self.OneChild

        #check that we can't make a node its own ancestor
        a, b, c = map(TreeNode, 'abc')
        a.append(b)
        b.append(c)
        self.assertRaises(TreeError, setattr, a, 'Parent', c)

    def test_Index(self):
        """TreeNode Index should hold correct data and be mutable"""
        first = TreeNode('a')
        second = TreeNode('b')
        third = TreeNode('c')
        fourth = TreeNode('0', Children=[first, second, third])
        self.assertEqual(len(fourth), 3)
        self.assertEqual(first.Index, 0)
        self.assertEqual(second.Index, 1)
        self.assertEqual(third.Index, 2)
        del fourth[0]
        self.assertEqual(second.Index, 0)
        self.assertEqual(third.Index, 1)
        self.assertEqual(len(fourth), 2)
        assert first.Parent is None
        second.Index = 1
        self.assertEqual(third.Index, 0)
        self.assertEqual(second.Index, 1)

    def test_removeNode(self):
        """TreeNode removeNode should delete node by id, not value"""
        parent = self.Repeated
        children = list(self.Repeated)
        self.assertEqual(len(parent), 3)
        self.assertEqual(parent.removeNode(children[1]), True)
        self.assertEqual(len(parent), 2)
        assert children[0].Parent is parent
        assert children[1].Parent is None
        assert children[2].Parent is parent
        self.assertEqual(children[0], children[1])
        self.assertEqual(parent.removeNode(children[1]), False)
        self.assertEqual(len(parent), 2)
        self.assertEqual(parent.removeNode(children[0]), True)
        self.assertEqual(len(parent), 1)
    
    def test_add(self):
        """TreeNode __add__ should return copy of self with list(other) added"""
        self.assertEqual(self.OneChild + 'abc', [self.Child, 'a', 'b', 'c'])
        self.assertRaises(TypeError, self.OneChild.__add__, 3)

    def test_delitem(self):
        """TreeNode __delitem__ should delete item and set parent to None"""
        self.assertEqual(self.Child.Parent, self.OneChild)
        self.assertEqual(len(self.OneChild), 1)
        del self.OneChild[0]
        self.assertEqual(self.OneChild.Parent, None)
        self.assertEqual(len(self.OneChild), 0)

        nodes = self.BigData
        parent = self.BigParent
        self.assertEqual(len(parent), 10)
        for n in nodes:
            assert n.Parent is parent
        del parent[-1]
        self.assertEqual(nodes[-1].Parent, None)
        self.assertEqual(len(parent), 9)
        del parent[1:6:2]
        self.assertEqual(len(parent), 6)
        for i, n in enumerate(nodes):
            if i in [0,2,4,6,7,8]:
                assert n.Parent is parent
            else:
                assert n.Parent is None

    def test_delslice(self):
        """TreeNode __delslice__ should delete items from start to end"""
        parent = self.BigParent
        nodes = self.BigData
        self.assertEqual(len(parent), 10)
        del parent[3:-2]
        self.assertEqual(len(parent), 5)
        for i, n in enumerate(nodes):
            if i in [3,4,5,6,7]:
               assert n.Parent is None
            else:
                assert n.Parent is parent

    def test_eq(self):
        """TreeNode should compare equal if same id or same data"""
        t, u, v = self.Comparisons
        self.assertEqual(t, t)
        assert t is not u
        self.assertEqual(t, u)
        self.assertNotEqual(t, v)
    
        f = TreeNode(1.0)
        g = TreeNode(1)
        self.assertEqual(f, g)
        f.Data += 0.1
        self.assertNotEqual(f, g)

    def test_ge(self):
        """TreeNode should compare ge by id or data"""
        t, u, v = self.Comparisons
        self.assertEqual(t >= t, True)
        self.assertEqual(t >= u, True)
        self.assertEqual(t >= v, False)
        self.assertEqual(v >= t, True)

    def test_gt(self):
        """TreeNode should compare gt by id or data"""
        t, u, v = self.Comparisons
        self.assertEqual(t > t, False)
        self.assertEqual(t > u, False)
        self.assertEqual(t > v, False)
        self.assertEqual(v > t, True)

    def test_iadd(self):
        """TreeNode iadd should add nodes inplace, setting parent correctly"""
        t, u, v = self.Comparisons
        self.assertEqual(len(t), 0)
        t += [u,v]
        self.assertEqual(len(t), 2)
        assert u.Parent is t
        assert v.Parent is t
        self.assertEqual(len(self.OneChild), 1)
        assert self.Child.Parent is self.OneChild
        t += [self.Child]
        assert self.Child.Parent is t
        self.assertEqual(len(t), 3)
        assert t[-1] is self.Child
        self.assertEqual(len(self.OneChild), 0)
        #note: will pass iadd of wrong type along to self.Data
        #maybe this should be changed?
        self.assertRaises(AttributeError, getattr, t, 'iadd')
        
    def test_imul(self):
        """TreeNode imul should raise NotImplementedError"""
        self.assertRaises(NotImplementedError, self.OneChild.__imul__, [3])

    def test_le(self):
        """TreeNode should compare le by id or data"""
        t, u, v = self.Comparisons
        self.assertEqual(t <= t, True)
        self.assertEqual(t <= u, True)
        self.assertEqual(t <= v, True)
        self.assertEqual(v <= t, False)

    def test_lt(self):
        """TreeNode should compare lt by id or data"""
        t, u, v = self.Comparisons
        self.assertEqual(t < t, False)
        self.assertEqual(t < u, False)
        self.assertEqual(t < v, True)
        self.assertEqual(v < t, False)

    def test_mul(self):
        """TreeNode mul should return a list with n copies of nodes"""
        parent, child = self.OneChild, self.Child
        self.assertEqual(parent * 3, [child] * 3)
        for i in parent * 3:
            assert i is child

    def test_ne(self):
        """TreeNode should compare ne by id or data"""
        t, u, v = self.Comparisons
        self.assertEqual(t != t, False)
        self.assertEqual(t != u, False)
        self.assertEqual(t != v, True)
        self.assertEqual(v != t, True)

    def test_rmul(self):
        """TreeNode rmul should return a list with n copies of nodes"""
        parent, child = self.OneChild, self.Child
        self.assertEqual(3 * parent, 3 * [child])
        for i in 3 * parent:
            assert i is child

    def test_setitem(self):
        """TreeNode setitem should set item or extended slice of nodes"""
        parent, nodes = self.BigParent, self.BigData
        t = TreeNode(1)
        parent[0] = t
        assert parent[0] is t
        assert t.Parent is parent
        assert nodes[0].Parent is None
        
        u = TreeNode(2)
        parent[-2] = u
        assert parent[8] is u
        assert u.Parent is parent
        assert nodes[8].Parent is None
        
        parent[1:6:2] = 'xyz'
        for i in [1,3,5]:
            assert nodes[i].Parent is None
        self.assertEqual(parent[1].Data, 'x')
        self.assertEqual(parent[3].Data, 'y')
        self.assertEqual(parent[5].Data, 'z')
        for i in parent:
            assert i.Parent is parent

        a, b, c = map(TreeNode, 'abc')
        a.append(b)
        b.append(c)
        self.assertRaises(TreeError, c.append, a)
       
    def test_setslice(self):
        """TreeNode setslice should set old-style slice of nodes"""
        parent, nodes = self.BigParent, self.BigData
        self.assertEqual(len(parent), 10)
        parent[5:] = []
        self.assertEqual(len(parent), 5)
        for i in range(5, 10):
            assert nodes[i].Parent is None
        parent[1:3] = 'abcd'
        self.assertEqual(len(parent), 7)
        for i in parent:
            assert i.Parent is parent
        data_list = [i.Data for i in parent]
        self.assertEqual(data_list, list('0abcd34'))
        parent[1:3] = parent[2:3]
        data_list = [i.Data for i in parent]
        self.assertEqual(data_list, list('0bcd34'))

    def test_str(self):
        """TreeNode str should give Newick-style representation"""
        self.assertEqual(str(self.Empty), 'None')
        self.assertEqual(str(self.OneChild), 'a(b)')
        self.assertEqual(str(self.BigParent), 'x(0,1,2,3,4,5,6,7,8,9)')
        self.BigParent[-1].extend('abc')
        self.assertEqual(str(self.BigParent), 'x(0,1,2,3,4,5,6,7,8,9(a,b,c))')

    def test_append(self):
        """TreeNode append should add item to end of self"""
        self.OneChild.append(TreeNode('c'))
        self.assertEqual(len(self.OneChild), 2)
        self.assertEqual(self.OneChild[-1].Data, 'c')
        self.OneChild.append(6)
        self.assertEqual(len(self.OneChild), 3)
        self.assertEqual(self.OneChild[-1].Data, 6)
        #check that refs are updated when moved from one tree to another
        empty = TreeNode()
        empty.append(self.OneChild[-1])
        self.assertEqual(len(empty), 1)
        self.assertEqual(empty[0].Data, 6)
        self.assertEqual(empty[0].Parent, empty)
        self.assertEqual(self.OneChild[-1].Data, 'c')

    def test_extend(self):
        """TreeNode extend should add many items to end of self"""
        self.Empty.extend('abcdefgh')
        data = ''.join([i.Data for i in self.Empty])
        self.assertEqual(data, 'abcdefgh')

    def test_insert(self):
        """TreeNode insert should insert item at specified index"""
        parent, nodes = self.BigParent, self.BigData
        self.assertEqual(len(parent), 10)
        parent.insert(3, 5)
        self.assertEqual(len(parent), 11)
        self.assertEqual(parent[3].Data, 5)
        self.assertEqual(parent[4].Data, '3')
        parent.insert(-1, 123)
        self.assertEqual(len(parent), 12)
        self.assertEqual(parent[-1].Data, '9')
        self.assertEqual(parent[-2].Data, 123)

    def test_pop(self):
        """TreeNode pop should remove and return child at specified index"""
        parent, nodes = self.BigParent, self.BigData
        self.assertEqual(len(parent), 10)
        last = parent.pop()
        assert last is nodes[-1]
        assert last.Parent is None
        self.assertEqual(len(parent), 9)
        assert parent[-1] is nodes[-2]
        first = parent.pop(0)
        assert first is nodes[0]
        assert first.Parent is None
        self.assertEqual(len(parent), 8)
        assert parent[0] is nodes[1]
        second_to_last = parent.pop(-2)
        assert second_to_last is nodes[-3]

    def test_remove(self):
        """TreeNode remove should remove by value, not id"""
        nodes = map(TreeNode, 'abc'*3)
        parent = TreeNode(Children=nodes)
        self.assertEqual(len(parent), 9)
        parent.remove('a')
        self.assertEqual(len(parent), 8)
        self.assertEqual(''.join([i.Data for i in parent]), 'bcabcabc')
        new_node = TreeNode('a')
        parent.remove(new_node)
        self.assertEqual(len(parent), 7)
        self.assertEqual(''.join([i.Data for i in parent]), 'bcbcabc')
    
    def test_Ancestors(self):
        """TreeNode ancestors should provide list of ancestors, deepest first"""
        nodes, tree = self.TreeNode, self.TreeRoot
        self.assertEqual(nodes['a'].Ancestors, [])
        self.assertEqual(nodes['b'].Ancestors, [nodes['a']])
        self.assertEqual(nodes['d'].Ancestors, nodes['f'].Ancestors)
        self.assertEqual(nodes['g'].Ancestors, \
            [nodes['f'], nodes['c'], nodes['b'], nodes['a']])

    def test_lastCommonAncestor(self):
        """TreeNode LastCommonAncestor should provide last common ancestor"""
        nodes, tree = self.TreeNode, self.TreeRoot
        a = nodes['a']
        b = nodes['b']
        c = nodes['c']
        d = nodes['d']
        e = nodes['e']
        f = nodes['f']
        g = nodes['g']
        h = nodes['h']
       
        self.assertEqual(a.lastCommonAncestor(a), a)
        self.assertEqual(a.lastCommonAncestor(b), a)
        self.assertEqual(a.lastCommonAncestor(g), a)
        self.assertEqual(a.lastCommonAncestor(h), a)

        self.assertEqual(b.lastCommonAncestor(g), b)
        self.assertEqual(b.lastCommonAncestor(d), b)
        self.assertEqual(b.lastCommonAncestor(a), a)
        self.assertEqual(b.lastCommonAncestor(h), a)

        self.assertEqual(d.lastCommonAncestor(f), c)
        self.assertEqual(d.lastCommonAncestor(g), c)
        self.assertEqual(d.lastCommonAncestor(a), a)
        self.assertEqual(d.lastCommonAncestor(h), a)

        self.assertEqual(g.lastCommonAncestor(g), g)
        self.assertEqual(g.lastCommonAncestor(f), f)
        self.assertEqual(g.lastCommonAncestor(e), c)
        self.assertEqual(g.lastCommonAncestor(c), c)
        self.assertEqual(g.lastCommonAncestor(b), b)
        self.assertEqual(g.lastCommonAncestor(a), a)
        self.assertEqual(g.lastCommonAncestor(h), a)

        t = TreeNode('h')
        for i in [a,b,c,d,e,f,g,h]:
            self.assertEqual(i.lastCommonAncestor(t), None)
            self.assertEqual(t.lastCommonAncestor(i), None)

        u = TreeNode('a', Children=[t])

        #can possibly share ancestor if not requiring node identity
        self.assertEqual(t.lastCommonAncestor(g, require_identity=False).Data,\
            'a')
            
    def test_Root(self):
        """TreeNode Root should find root of tree"""
        nodes, root = self.TreeNode, self.TreeRoot
        for i in nodes.values():
            assert i.Root is root

    def test_Children(self):
        """TreeNode Children should allow getting/setting children"""
        nodes = self.TreeNode
        for n in nodes:
            node = nodes[n]
            self.assertEqual(list(node), node.Children)

        t = TreeNode(Children='abc')
        self.assertEqual(len(t), 3)
        u, v = TreeNode('u'), TreeNode('v')
        t.Children = [u,v]

        assert t[0] is u
        assert t[1] is v
        self.assertEqual(len(t), 2)

    def test_TerminalChildren(self):
        """TreeNode TerminalChildren should return all terminal children"""
        self.assertEqual(self.Empty.TerminalChildren, [])
        self.assertEqual(self.Child.TerminalChildren, [])
        self.assertEqual(self.OneChild.TerminalChildren, [self.Child])
        
        nodes, tree = self.TreeNode, self.TreeRoot
        a = nodes['a']
        b = nodes['b']
        c = nodes['c']
        d = nodes['d']
        e = nodes['e']
        f = nodes['f']
        g = nodes['g']
        h = nodes['h']

        self.assertEqual(g.TerminalChildren, [])
        self.assertEqual(f.TerminalChildren, [g])
        self.assertEqual(e.TerminalChildren, [])
        self.assertEqual(d.TerminalChildren, [])
        self.assertEqual(c.TerminalChildren, [d,e])
        self.assertEqual(b.TerminalChildren, [])
        self.assertEqual(h.TerminalChildren, [])
        self.assertEqual(a.TerminalChildren, [h])

    def test_NonTerminalChildren(self):
        """TreeNode NonTerminalChildren should return all non-terminal children"""
        self.assertEqual(self.Empty.NonTerminalChildren, [])
        self.assertEqual(self.Child.NonTerminalChildren, [])
        self.assertEqual(self.OneChild.NonTerminalChildren, [])
        
        nodes, tree = self.TreeNode, self.TreeRoot
        a = nodes['a']
        b = nodes['b']
        c = nodes['c']
        d = nodes['d']
        e = nodes['e']
        f = nodes['f']
        g = nodes['g']
        h = nodes['h']

        self.assertEqual(g.NonTerminalChildren, [])
        self.assertEqual(f.NonTerminalChildren, [])
        self.assertEqual(e.NonTerminalChildren, [])
        self.assertEqual(d.NonTerminalChildren, [])
        self.assertEqual(c.NonTerminalChildren, [f])
        self.assertEqual(b.NonTerminalChildren, [c])
        self.assertEqual(h.NonTerminalChildren, [])
        self.assertEqual(a.NonTerminalChildren, [b])

    def test_ChildGroups(self):
        """TreeNode ChildGroups should divide children by grandchild presence"""
        parent = TreeNode(Children='aababbbaaabbbababbb')
        for node in parent:
            if node == 'a':
                node.append('def')
        groups = parent.ChildGroups
        self.assertEqual(len(groups), 10)
        exp_group_sizes = [2,1,1,3,3,3,1,1,1,3]
        obs_group_sizes = [len(i) for i in groups]
        self.assertEqual(obs_group_sizes, exp_group_sizes)

        parent = TreeNode(Children='aab')
        for node in parent:
            if node == 'a':
                node.append('def')
        groups = parent.ChildGroups
        self.assertEqual(len(groups), 2)
        self.assertEqual([len(i) for i in groups], [2,1])

        parent = TreeNode(Children='aaaaa')
        groups = parent.ChildGroups
        self.assertEqual(len(groups), 1)
        self.assertEqual(len(groups[0]), 5)

        parent = TreeNode(Children='aaba')
        for node in parent:
            if node == 'a':
                node.append('def')
        groups = parent.ChildGroups
        self.assertEqual(len(groups), 3)
        self.assertEqual([len(i) for i in groups], [2,1,1])
        

    def test_TerminalDescendants(self):
        """TreeNode TerminalDescendants should return all terminal descendants"""
        self.assertEqual(self.Empty.TerminalDescendants, [])
        self.assertEqual(self.Child.TerminalDescendants, [])
        self.assertEqual(self.OneChild.TerminalDescendants, [self.Child])
        
        nodes, tree = self.TreeNode, self.TreeRoot
        a = nodes['a']
        b = nodes['b']
        c = nodes['c']
        d = nodes['d']
        e = nodes['e']
        f = nodes['f']
        g = nodes['g']
        h = nodes['h']

        self.assertEqual(g.TerminalDescendants, [])
        self.assertEqual(f.TerminalDescendants, [g])
        self.assertEqual(e.TerminalDescendants, [])
        self.assertEqual(d.TerminalDescendants, [])
        self.assertEqual(c.TerminalDescendants, [d,e,g])
        self.assertEqual(b.TerminalDescendants, [d,e,g])
        self.assertEqual(h.TerminalDescendants, [])
        self.assertEqual(a.TerminalDescendants, [d,e,g,h])

    def test_traverse(self):
        """TreeNode traverse should iterate over nodes in tree."""
        e = self.Empty
        s = self.Single
        o = self.OneChild
        m = self.Multi
        r = self.TreeRoot

        self.assertEqual([i.Data for i in e.traverse()], [None])
        self.assertEqual([i.Data for i in e.traverse(False, False)], [None])
        self.assertEqual([i.Data for i in e.traverse(True, True)], [None])

        self.assertEqual([i.Data for i in s.traverse()], ['a'])
        self.assertEqual([i.Data for i in s.traverse(True, True)], ['a'])
        self.assertEqual([i.Data for i in s.traverse(True, False)], ['a'])
        self.assertEqual([i.Data for i in s.traverse(False, True)], ['a'])
        self.assertEqual([i.Data for i in s.traverse(False, False)], ['a'])

        self.assertEqual([i.Data for i in o.traverse()], ['a','b'])
        self.assertEqual([i.Data for i in o.traverse(True, True)],['a','b','a'])
        self.assertEqual([i.Data for i in o.traverse(True, False)], ['a', 'b'])
        self.assertEqual([i.Data for i in o.traverse(False, True)], ['b', 'a'])
        self.assertEqual([i.Data for i in o.traverse(False, False)], ['b'])

        self.assertEqual([i.Data for i in m.traverse()], ['a','b','c','d'])
        self.assertEqual([i.Data for i in m.traverse(True, True)],\
            ['a','b','c','d','a'])
        self.assertEqual([i.Data for i in m.traverse(True, False)], \
            ['a', 'b','c','d'])
        self.assertEqual([i.Data for i in m.traverse(False, True)], \
            ['b', 'c', 'd', 'a'])
        self.assertEqual([i.Data for i in m.traverse(False, False)], \
            ['b', 'c', 'd'])

        self.assertEqual([i.Data for i in r.traverse()], \
            ['a','b','c','d', 'e', 'f', 'g', 'h'])
        self.assertEqual([i.Data for i in r.traverse(True, True)],\
            ['a','b','c','d','e','f','g','f','c','b','h','a'])
        self.assertEqual([i.Data for i in r.traverse(True, False)], \
            ['a', 'b','c','d','e','f','g','h'])
        self.assertEqual([i.Data for i in r.traverse(False, True)], \
            ['d','e','g','f','c','b','h','a'])
        self.assertEqual([i.Data for i in r.traverse(False, False)], \
            ['d','e','g','h'])

    def test_Siblings(self):
        """TreeNode Siblings should return all siblings, not self"""
        self.assertEqual(self.Empty.Siblings, [])
        self.assertEqual(self.Child.Siblings, [])
        self.assertEqual(self.OneChild.Siblings, [])
        
        nodes, tree = self.TreeNode, self.TreeRoot
        a = nodes['a']
        b = nodes['b']
        c = nodes['c']
        d = nodes['d']
        e = nodes['e']
        f = nodes['f']
        g = nodes['g']
        h = nodes['h']

        self.assertEqual(g.Siblings, [])
        self.assertEqual(f.Siblings, [d,e])
        self.assertEqual(e.Siblings, [d,f])
        self.assertEqual(d.Siblings, [e,f])
        self.assertEqual(c.Siblings, [])
        self.assertEqual(b.Siblings, [h])
        self.assertEqual(h.Siblings, [b])
        self.assertEqual(a.Siblings, [])

    def test_slice(self):
        """TreeNode slicing should return list, not TreeNode"""
        nodes = self.TreeNode
        c, d, e, f = nodes['c'],nodes['d'],nodes['e'],nodes['f']
        assert c[:] is not c
        self.assertEqual(c[:], [d,e,f])
        self.assertEqual(c[1:2], [e])
        self.assertEqual(c[0:3:2], [d,f])

    def test_separation(self):
        """TreeNode separation should return correct number of edges"""
        nodes, tree = self.TreeNode, self.TreeRoot
        a = nodes['a']
        b = nodes['b']
        c = nodes['c']
        d = nodes['d']
        e = nodes['e']
        f = nodes['f']
        g = nodes['g']
        h = nodes['h']

        self.assertEqual(a.separation(a), 0)
        self.assertEqual(c.separation(c), 0)
        self.assertEqual(a.separation(h), 1)
        self.assertEqual(g.separation(h), 5)
        self.assertEqual(f.separation(d), 2)
        self.assertEqual(f.separation(c), 1)
        self.assertEqual(c.separation(f), 1)

    def test_copy(self):
        """copy.copy should raise TypeError on TreeNode"""
        t = TreeNode('t')
        u = TreeNode('u')
        t.append(u)
        self.assertRaises(TypeError, copy, t)
        self.assertRaises(TypeError, copy, u)

    def test_deepcopy(self):
        """copy.deepcopy should work on TreeNode"""
        t = TreeNode(['t'])
        u = TreeNode(['u'])
        t.append(u)

        c = deepcopy(u)
        assert c is not u
        assert c.Data == u.Data
        assert c.Data is not u.Data
        #note: Data _is_ same object if it's immutable, e.g. a string.
        #deepcopy doesn't copy data for immutable objects.
    
        #need to check that we also copy arbitrary attributes
        t.XYZ = [3]
        c = deepcopy(t)
        assert c is not t
        assert c[0] is not u
        assert c[0].Data is not u.Data
        assert c[0].Data == u.Data
        assert c.XYZ == t.XYZ
        assert c.XYZ is not t.XYZ

        t = self.TreeRoot
        c = deepcopy(t)
        self.assertEqual(str(c), str(t))

    def test_copy(self):
        """TreeNode.copy() should produce deep copy"""
        t = TreeNode(['t'])
        u = TreeNode(['u'])
        t.append(u)

        c = u.copy()
        assert c is not u
        assert c.Data == u.Data
        assert c.Data is not u.Data
        #note: Data _is_ same object if it's immutable, e.g. a string.
        #deepcopy doesn't copy data for immutable objects.
    
        #need to check that we also copy arbitrary attributes
        t.XYZ = [3]
        c = t.copy()
        assert c is not t
        assert c[0] is not u
        assert c[0].Data is not u.Data
        assert c[0].Data == u.Data
        assert c.XYZ == t.XYZ
        assert c.XYZ is not t.XYZ

        t = self.TreeRoot
        c = t.copy()
        self.assertEqual(str(c), str(t))

    def test_clear(self):
        """TreeNode clear should erase a subtree."""
        t = self.TreeRoot
        n = self.TreeNode
        n['f'].clear()
        self.assertEqual(str(t), 'a(b(c(d,e,f)),h)')
        n['b'].clear()
        self.assertEqual(str(t), 'a(b,h)')
        assert n['g'].Parent is None

    def test_nameUnnamedNodes(self):
        """nameUnnamedNodes assigns an arbitrary value when Data == None"""
        tree, tree_nodes = self.TreeRoot, self.TreeNode
        tree_nodes['b'].Data = 'node2'
        tree_nodes['c'].Data = None
        tree_nodes['f'].Data = None
        tree_nodes['e'].Data = 'node3'
        tree.nameUnnamedNodes()
        self.assertEqual(tree_nodes['c'].Data, 'node1')
        self.assertEqual(tree_nodes['f'].Data, 'node4')

    def test_makeTreeArray(self):
        """makeTreeArray maps nodes to the descendants in them"""
        tree = self.TreeRoot
        result, node_list = tree.makeTreeArray()
        self.assertEqual(result, \
                array([[1,1,1,1], [1,1,1,0], [1,1,1,0],[0,0,1,0]]))
        nodes = [node.Data for node in node_list]
        self.assertEqual(nodes, ['a', 'b', 'c', 'f'])
        #test if works with a dec_list supplied
        dec_list = ['d', 'added', 'e', 'g', 'h']
        result2, node_list = tree.makeTreeArray(dec_list)
        self.assertEqual(result2, \
                array([[1,0,1,1,1], [1,0,1,1,0], [1,0,1,1,0], [0,0,0,1,0]]))
    
    def test_removeDeleted(self):
        """removeDeleted should remove all nodes where is_deleted tests true."""
        tree = DndParser('((a:3,(b:2,(c:1,d:1):1):1):2,(e:3,f:3):2);',
            constructor=TreeNode)
        result_not_deleted = deepcopy(tree)
        tree.removeDeleted(lambda x: x.Data in [])
        self.assertEqual(str(tree),str(result_not_deleted))
        deleted = Set(['b','d','e','f'])
        result_tree = DndParser('((a:3,((c:1):1):1):2);',constructor=TreeNode)
        is_deleted = lambda x: x.Data in deleted
        tree.removeDeleted(is_deleted)
        self.assertEqual(str(tree),str(result_tree))
    
    def test_prune(self):
        """prune should recconstruct correct topology of tree."""
        tree = DndParser('((a:3,((c:1):1):1):2);',constructor=TreeNode)
        tree.prune()
        result_tree = DndParser('((a:3,c:1));',constructor=TreeNode)
        self.assertEqual(str(tree),str(result_tree))


    def test_setDescendantTips(self):
        """setDescendantTips should set correct list of tips."""
        r = self.TreeRoot
        n = self.TreeNode
        r.setDescendantTips()
        self.assertEqual(n['e'].DescendantTips, [n['e']])
        self.assertEqual(r.DescendantTips, [n['d'],n['e'],n['g'],n['h']])
        self.assertEqual(n['c'].DescendantTips, [n['d'], n['e'], n['g']])
        self.assertEqual(n['f'].DescendantTips, [n['g']])

    def test_setDescendantTipProperty(self):
        """setDescendantTipProperty should set correct property and value"""
        leaf_dict = {'d':2, 'e':1, 'g':6, 'h':7}
        means_dict = leaf_dict.copy()
        means_dict.update({'f':6, 'c':3, 'b':3, 'a':4})
        stdevs_dict = {'d':0, 'e':0, 'g':0, 'f':0, 'c':stdev([2,1,6]), \
            'b':stdev([2,1,6]), 'h':0, 'a':stdev([2,1,6,7])}

        def set_leaf_f(node):
            return leaf_dict[node.Data]

        r = self.TreeRoot
        r.setDescendantTipProperty(set_leaf_f, 'x')
        for node in r.traverse():
            self.assertEqual(node.xMean, means_dict[node.Data])
            self.assertFloatEqual(node.xStdev, stdevs_dict[node.Data])

    def test_mapAttr(self):
        """Tree mapattr should correctly change the attributes in-place"""
        t = DndParser('(a,(c,b)x,d)')
        t.mapAttr({'a':'aa','b':'bb','c':'cc','x':'xx'}) # d left out
        self.assertEqual(str(t), '(aa,(cc,bb)xx,d)')
        t = DndParser('(a,(c,b)x,d)')
        f = lambda x: x in list('abcx') and x*3 or x
        t.mapAttr(f) # d left out
        self.assertEqual(str(t), '(aaa,(ccc,bbb)xxx,d)')
        #check that it works if you set a different attribute than you read
        t = DndParser('(a,(c,b)x,d)')
        t.mapAttr(f, new_attr='xxx')
        for n in t.traverse(self_before=True, self_after=False):
            if n in list('abcx'):
                self.assertEqual(n.xxx, n.Data*3)
            else:
                self.assertEqual(n.xxx, n.Data)

    def test_changeFromParent(self):
        """TreeNode changeFromParent should record change from parent"""
        t = DndParser('(a,(c,b)x,d)')
        t.mapAttr({'a':5, 'c':3, 'b':7, 'x':2, 'd':1})
        self.assertEqual(t[1][0].changeFromParent('Data'), 1)
        self.assertEqual(t[1][1].changeFromParent('Data'), 5)
        f = lambda x: x.Data * 2
        self.assertEqual(t[1][0].changeFromParent(f), 2)
        self.assertEqual(t[1][1].changeFromParent(f), 10)

    def test_attrTable(self):
        """"TreeNode attrTable should return correct table of attributes"""
        t = DndParser('(a,(c,b)x,d)')
        f1 = lambda x: x in list('abcx') and x*2 or x
        f2 = lambda x: x in list('abcx') and x*3 or x
        f3 = lambda x: x in list('abcx') and x*4 or x
        t.mapAttr(f1, new_attr='xx')
        t.mapAttr(f2, new_attr='xxx')
        t.mapAttr(f3, new_attr='xxxx')
        table = t.attrTable(['xx','xxxx'])
        self.assertEqual(table, [[None, None], ['aa','aaaa'],['xx','xxxx'],\
            ['cc','cccc'],['bb','bbbb'],['d','d']])
        

        
class PhyloNodeTests(TestCase):
    """Tests of phylogeny-specific methods."""
    def setUp(self):
        """Creates a standard tree"""
        nodes = dict([(x, PhyloNode(x)) for x in 'abcdefgh'])
        nodes['a'].append(nodes['b'])
        nodes['b'].append(nodes['c'])
        nodes['c'].append(nodes['d'])
        nodes['c'].append(nodes['e'])
        nodes['c'].append(nodes['f'])
        nodes['f'].append(nodes['g'])
        nodes['a'].append(nodes['h'])
        self.TreeNode = nodes
        self.TreeRoot = nodes['a']
        nodes['a'].BranchLength = None
        nodes['b'].BranchLength = 0
        nodes['c'].BranchLength = 3
        nodes['d'].BranchLength = 1
        nodes['e'].BranchLength = 4
        nodes['f'].BranchLength = 2
        nodes['g'].BranchLength = 3
        nodes['h'].BranchLength = 2

    def test_distance(self):
        """PhyloNode Distance should report correct distance between nodes"""
        nodes, tree = self.TreeNode, self.TreeRoot
        a = nodes['a']
        b = nodes['b']
        c = nodes['c']
        d = nodes['d']
        e = nodes['e']
        f = nodes['f']
        g = nodes['g']
        h = nodes['h']
       
        self.assertEqual(a.distance(a), 0)
        self.assertEqual(a.distance(b), 0)
        self.assertEqual(a.distance(c), 3)
        self.assertEqual(a.distance(d), 4)
        self.assertEqual(a.distance(e), 7)
        self.assertEqual(a.distance(f), 5)
        self.assertEqual(a.distance(g), 8)
        self.assertEqual(a.distance(h), 2)
    
        self.assertEqual(b.distance(a), 0)
        self.assertEqual(b.distance(b), 0)
        self.assertEqual(b.distance(c), 3)
        self.assertEqual(b.distance(d), 4)
        self.assertEqual(b.distance(e), 7)
        self.assertEqual(b.distance(f), 5)
        self.assertEqual(b.distance(g), 8)
        self.assertEqual(b.distance(h), 2)
        
        self.assertEqual(c.distance(a), 3)
        self.assertEqual(c.distance(b), 3)
        self.assertEqual(c.distance(c), 0)
        self.assertEqual(c.distance(d), 1)
        self.assertEqual(c.distance(e), 4)
        self.assertEqual(c.distance(f), 2)
        self.assertEqual(c.distance(g), 5)
        self.assertEqual(c.distance(h), 5)
        
        self.assertEqual(d.distance(a), 4)
        self.assertEqual(d.distance(b), 4)
        self.assertEqual(d.distance(c), 1)
        self.assertEqual(d.distance(d), 0)
        self.assertEqual(d.distance(e), 5)
        self.assertEqual(d.distance(f), 3)
        self.assertEqual(d.distance(g), 6)
        self.assertEqual(d.distance(h), 6)
        
        self.assertEqual(e.distance(a), 7)
        self.assertEqual(e.distance(b), 7)
        self.assertEqual(e.distance(c), 4)
        self.assertEqual(e.distance(d), 5)
        self.assertEqual(e.distance(e), 0)
        self.assertEqual(e.distance(f), 6)
        self.assertEqual(e.distance(g), 9)
        self.assertEqual(e.distance(h), 9)
        
        self.assertEqual(f.distance(a), 5)
        self.assertEqual(f.distance(b), 5)
        self.assertEqual(f.distance(c), 2)
        self.assertEqual(f.distance(d), 3)
        self.assertEqual(f.distance(e), 6)
        self.assertEqual(f.distance(f), 0)
        self.assertEqual(f.distance(g), 3)
        self.assertEqual(f.distance(h), 7)
        
        self.assertEqual(g.distance(a), 8)
        self.assertEqual(g.distance(b), 8)
        self.assertEqual(g.distance(c), 5)
        self.assertEqual(g.distance(d), 6)
        self.assertEqual(g.distance(e), 9)
        self.assertEqual(g.distance(f), 3)
        self.assertEqual(g.distance(g), 0)
        self.assertEqual(g.distance(h), 10)

        self.assertEqual(h.distance(a), 2)
        self.assertEqual(h.distance(b), 2)
        self.assertEqual(h.distance(c), 5)
        self.assertEqual(h.distance(d), 6)
        self.assertEqual(h.distance(e), 9)
        self.assertEqual(h.distance(f), 7)
        self.assertEqual(h.distance(g), 10)
        self.assertEqual(h.distance(h), 0)

    def test_str(self):
        """PhyloNode str should give expected results"""
        nodes, tree = self.TreeNode, self.TreeRoot
        a = nodes['a']
        b = nodes['b']
        c = nodes['c']
        d = nodes['d']
        e = nodes['e']
        f = nodes['f']
        g = nodes['g']
        h = nodes['h']
        
        self.assertEqual(str(h), 'h:2')
        self.assertEqual(str(f), '(g:3)f:2')
        self.assertEqual(str(a), '(((d:1,e:4,(g:3)f:2)c:3)b:0,h:2)a')
        #check that None isn't converted any more
        h.BranchLength = None
        c.BranchLength = None   #need to test both leaf and internal node
        self.assertEqual(str(a), '(((d:1,e:4,(g:3)f:2)c)b:0,h)a')

    def test_setWeightedProperty(self):
        """setWeightedProperty should calculate and set correct property"""
        leaf_dict = {'d':2, 'e':1, 'g':6, 'h':7}
        means_dict = leaf_dict.copy()
        c_val = (2.0/1+1.0/4+6.0/2)/(1/1+1.0/4+1.0/2)
        delta = 0.01
        a_val = (c_val/delta + 7.0/2)/(1.0/delta + 1.0/2)
        means_dict.update({'f':6, 'c':c_val, 'b':c_val, 'a':a_val})
        c_stdev =sqrt(((2-c_val)**2 +(1-c_val)**2 + (6-c_val)**2)/3)
        stdevs_dict = {'d':0, 'e':0, 'g':0, 'f':0, \
            'c': c_stdev, 'b':0, 'h':0, \
            'a':sqrt(((a_val-c_val)**2+(a_val-7)**2)/2)}

        def set_leaf_f(node):
            return leaf_dict[node.Data]

        r = self.TreeRoot
        r.setWeightedProperty(set_leaf_f, 'x', branch_delta=delta)
        for node in r.traverse(self_before=False, self_after=True):
            self.assertEqual(node.xWeightedMean, means_dict[node.Data])
            self.assertFloatEqual(node.xWeightedStdev, stdevs_dict[node.Data])

    def test_collapseNode(self):
        "collapseNode removes an internal node and attaches Children to Parent"
        nodes, tree = self.TreeNode, self.TreeRoot
        a = nodes['a']
        b = nodes['b']
        c = nodes['c']
        d = nodes['d']
        e = nodes['e']
        f = nodes['f']
        g = nodes['g']
        h = nodes['h']
        tree.collapseNode(f)
        self.assertEqual(str(tree), '(((d:1,e:4,g:5)c:3)b:0,h:2)a')
        tree.collapseNode(c)
        self.assertEqual(str(tree), '((d:4,e:7,g:8)b:0,h:2)a')

#run if called from command line
if __name__ == '__main__':
    main()
