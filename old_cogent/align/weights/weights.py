#!/bin/env python
#weights.py
"""Computes weights for alignment.  This functionality will migrate to
PhyloNode, but is being tested in a subclass for now. Originally
implemented by Micah Hamady.
"""
from __future__ import division
from old_cogent.base.tree import PhyloNode

class WeightNode(PhyloNode):
    """Adds capacity to weight nodes to PhyloNode."""
    MinBranch=1e-9      # Min branch length
    MaxBranch=1e9       # Max branch length
    NodeWeight=0        # Default node weight
    BranchSum = 0       # Default branch sum

    def __init__(self, Data=None, Children=None, Parent=None):
        """Returns new WeightNode object."""
        super(WeightNode, self).__init__(Data, Children, Parent)

        self.NodeWeight = 0     #weight of this node
        self.BranchSum = 0      #sum of branch length exiting this node

    def clipBranchLengths(self, max_val=None, min_val=None):
        """Clips all branch lengths in self and children to max_val and min_val.

        max_val and min_val default to self.MaxBranch and self.MinBranch.
        """
        if max_val is None: max_val = self.MaxBranch
        if min_val is None: min_val = self.MinBranch
        for i in self.traverse():
            bl = i.BranchLength
            if bl > max_val:
                i.BranchLength = max_val
            elif bl < min_val:
                i.BranchLength = min_val

    def setBranchSum(self):
        """Sets BranchSum for self and all its children, recursively."""
        total = 0
        for child in self:
            child.setBranchSum()
            total += child.BranchSum
            total += child.BranchLength
        self.BranchSum = total

    def _set_node_weights(self):
        """Sets NodeWeight for each node. Assumes BranchSum previously set.
        
        Private because it's unsafe: use self.setWeights().
        """
        parent = self.Parent
        if parent is None: #root of tree always has weight of 1.0
            self.NodeWeight = 1.0
        else:
            self.NodeWeight = parent.NodeWeight * \
                (self.BranchLength + self.BranchSum)/parent.BranchSum
        for child in self:
            child._set_node_weights()

    def leafWeights(self):
        """Returns a dict of {leaf, weight} mappings.
        
        Assumes you've already called setWeights.
        """
        return dict([(x.Data,x.NodeWeight) for x in self.Leaves])

    def setWeights(self, eps=None):
        """Computes the weighted contribution of each node.

        Sets self.BranchSum and self.NodeWeight for each node.

        Assumes that it is being called on the root of the tree, but doesn't
        check (so can also be used on subtrees if necessary).
        """
        self.clipBranchLengths(min_val=eps)
        self.setBranchSum()
        self._set_node_weights()
        
    def _get_leaves(self):  
        """Returns list of leaves in the subtree starting at self.

        Differs from TerminalDescendants in that if it's called on a leaf node
        it will return a list containing that node rather than an empty list.
        TerminalDescendants is guaranteed to return only descendants, never
        the node itself.
        """
        if self:
            leaves = []
            for child in self:
                leaves.extend(child._get_leaves())
            return leaves
        else:
            return [self]
            
    # gets leaves in tree  
    Leaves = property(_get_leaves)

    def printNodes(self, leaves_only=True):
        """Debug to print out nodes in tree, or just leaves.
        """
        if self:
            for child in self:
                child.printNodes(leaves_only)
        if not (leaves_only and self):
            print "Data: %s, Weight: %s" % (self.Data, str(self.NodeWeight))

if __name__ == '__main__':
    #quick test; replace with proper unit tests
    a, b, c, d, e, r, s, t, u = [WeightNode(Data=i) for i in 'abcderstu']

    
    s.BranchLength = 5
    r.append(s)
    
    u.BranchLength = 6
    r.append(u)


    a.BranchLength = 4
    s.append(a)


    t.BranchLength = 3
    s.append(t)

    b.BranchLength = 1
    t.append(b)

    c.BranchLength = 2
    t.append(c)

    d.BranchLength = 7
    u.append(d)

    e.BranchLength = 8
    u.append(e)

    
   
    print "Original tree:"
    print r
    r.setWeights()
    
    print "Branch lengths:"
    for node in r.traverse():
        print node.Data, '\t', node.BranchLength
        
    print "Branch sums:"
    for node in r.traverse():
        print node.Data, '\t', node.BranchSum
        
    print "Leaf weights:"
    print r.leafWeights()
    print sum(r.leafWeights().values())
    print

    print
    print "Node weights:"
    for node in r.traverse():
        print node.Data, '\t', node.NodeWeight
    print

    print "Sum leaves"
    print sum(map(lambda x: x.NodeWeight, r.Leaves))

    #print "leaves only"
    #r.printNodes(True)
    #print "All"
    #r.printNodes(False)

    #print map(lambda a: a.Data, r.Leaves)
    #print map(lambda a: a.Data, t.Leaves)
