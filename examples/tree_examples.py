#!/usr/bin/env python
#test script for tree classes

from old_cogent.base.tree import TreeNode
from old_cogent.util.demo import QuickDemo
from sys import stdout

demo = QuickDemo(
[
    "Demonstration for tree classes.",
    "Written 10/12/03 by Rob Knight, rob@spot.colorado.edu",
    """
A tree is a data structure that holds parent-child relations among nodes.
Here, the basic building block of trees is the TreeNode class. A TreeNode
has several important properties:
\t
    Parent: the node from which the node is descended, or None.
    Data: the data the node carries.
    Children: a list of nodes descended from this node.
\t
Since tree data structures are recursive, any TreeNode can be thought of as
the root of a tree containing its children, and all their descendants.
\t
This script demonstrates many of the important properties of TreeNode.
\t
""",

    ["Can construct a TreeNode with data from any object", "t = TreeNode('x')"],
    [None, 'print t'],
    "Can construct TreeNode directly with any sequence as Children",
    [None, "t = TreeNode('x', Children='abc')"],
    [None, "print t"],
    ["TreeNode behaves just like a normal list, e.g. with slicing","t[:] = []"],
    [None, "print t"],
    "For the rest of the demonstration, define some standard nodes",
    [None, "a,b,c,d,e,f = map(TreeNode, 'abcdef')"],
    ["Can build the tree using standard list methods", "a.extend([b,c])"],
    [None, "print a"],
    [None, "b.append(d)"],
    [None, "print a"],
    [None, "d[:] = [e,f]"],
    [None, "print a"],
    "Can rearrange tree by appending an existing node somewhere else...",
    [None, "c.append(d)"],
    [None, "print a"],
    ["...or by re-setting a node's parent", "d.Parent = b"],
    [None, "print a"],
    "Setting a node's parent to None removes it from the tree", 
    [None, "d.Parent = None"],
    [None, "print a"],
    [None, "print d"],
    "However, the subtrees remain in memory, and can be reattached.",
    [None, "a.Parent = d"],
    [None, "print d"],
    "Trying to set a node's parent to one of its descendants raises an error", 
    [None, "d.Parent = a"],
    ["Solution is to break the Parent ref first.", "a.Parent = None"],
    [None, "d.Parent = a"],
    [None, "print a"],
    ["A node can only appear in its parent's list once.", "d[-1] = e"],
    ["(need to set tree back the way it was, since demo caught the exception)", 
        "d[-1] = f"],
    "Nodes have lots of useful methods and properties.",
    ["Index returns a node's index in its parent", """
for node in [a,b,c,d,e,f]:
    print node.Data, ':', node.Index"""],
    ["Root returns the node at the root of the node's tree", """
for node in [a,b,c,d,e,f]:
    print node.Data, ':', node.Root.Data"""],
    "lastCommonAncestor(x) returns the last common ancestor of the node and x",
    [None, "print c.lastCommonAncestor(b).Data"],
    "LCA works even if one of the two nodes _is_ the ancestor.",
    [None, "print c.lastCommonAncestor(a).Data"],
    """Note that the following methods return a list of references to the nodes.
To get the data instead, use a map or list comprehension.""",
    ["Define function to extract data with map", "getdata = lambda x: x.Data"],
    ["Ancestors returns a list of a node's ancestors.", "print c.Ancestors"],
    ["Use getdata function defined above to get Data instead of nodes"],
    [None, "print map(getdata, c.Ancestors)"],
    "TerminalDescendents returns all childless nodes descended from the node",
    [None, "print map(getdata, a.TerminalDescendants)"],
    "TerminalChildren returns childless immediate descendants",
    [None, "print map(getdata, a.TerminalChildren)"],
    "NonTerminalChildren returns immediate descendants with children",
    [None, "print map(getdata, a.NonTerminalChildren)"],
    ["A TreeNode forwards attributes (incl. methods) to its data", "print a"],
    [None, "print a.Data"],
    [None, "print a.upper()"],
    [None, "a.Data = {'x': 3, 'y':4}"],
    [None, "print a.keys()"],
    ["a.upper() now raises an error", "print a.upper()"],
    ["This concludes the tree demo."]
])
