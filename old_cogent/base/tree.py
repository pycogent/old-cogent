#!/usr/bin/env python
#file evo/tree.py

"""Classes for dealing with trees and phylogeny.

Owner: Rob Knight rob@spot.colorado.edu

Status: Stable

Revision History

9/17/03 Rob Knight: originally written for PyEvolve. Inspiration from the 
ViennaTree class in BayesFold, and the NcbiTaxon class written by Jason 
Carnes.

9/20/03 Rob Knight: cleaned up reference handling. Now supports full list
interface.

9/25/03 Rob Knight: now do deeper check to make sure we can't make a node's
ancestor its descendant.

10/12/03 Rob Knight: fixed __repr__.

10/14/03 Rob Knight: added Children property.

10/29/03 Rob Knight: fixed slicing. Added Siblings property.

12/27/03 Rob Knight: changed PhyloNode str() to change handling of root node.

2/17/04 Rob Knight: changed order of operations in __setslice__ so that the
list that's inserted can contain elements that were already children of the
node (previously failed with DuplicateNodeError). All unit tests still pass.

2/19/04 Rob Knight: added TreeNode traverse().

3/24/04 Rob Knight: added code to handle copy.copy and copy.deepcopy to
TreeNode. The fact that nodes have self.Parent as an attribute caused problems
when copying, since self.Parent was set before the append. Added copy() method.
Added clear() for erasing subtrees.

5/21/04 Rob Knight: added BranchLength and Weight as intrinsic properties of
PhyloNode (rather than letting them end up in the delegated object). Changed
string format to put the labels after the nodes to which they refer rather than
before them so that trees can be read by other programs.

7/14/04 Cathy Lozupone: changed PhyloNode str() so that branchlengths set to
None are ignored

5/23/05 Cathy Lozupone: added nameUnnamedNodes and makeTreeArray

8/3/05 Rob Knight: added scaleBranchLengths and setTipDistances. Warning: not
tested yet!

9/13/05 Jeremy Widmann: added removeDeleted and prune.

2/8/06 Rob Knight: added methods for attribute mapping and recovering table
of attributes.

3/7/06 Micah Hamady: added setContainsChildCache, containsChild, setIds, and uniqueIds need to add better doc strings after merge & rename. Added set_branchlength to collapaseNode

3/13/06 Micah Hamady: added check for None in PhyloNode distance function 
"""
from copy import deepcopy
from old_cogent.util.misc import ClassChecker, Delegator, ConstrainedList, \
    ConstraintError
from Numeric import array, resize, sqrt, zeros, nonzero, take
from MLab import mean, std as stdev
from random import choice

class TreeError(Exception):
    """Base class for tree-related problems."""
    pass

class DuplicateNodeError(TreeError):
    """Raised when trying to add multiple copies of the same node."""
    pass

class TreeNode(ConstrainedList, Delegator):
    """Holds information about generic tree: nodes forward to self.Data."""

    _exclude_from_copy = dict.fromkeys(['_handler', '_data', '_parent'])
    
    def __init__(self, Data=None, Children=None, Parent=None):
        """Returns new TreeNode, intialized with Data and maybe Children/Parent.
        
        Note: Parent is handled automatically when a node is appended to the
        children of another node.

        Desirable input for (phylogenetic) trees:
        - Newick string
        - Nexus block for tree, plus taxon map.
        - another tree object
        """
        #allocate slots for private vars: make sure they don't get captured
        #by self.Data!
        self.__dict__['_data'] = None
        self.__dict__['_parent'] = None
        self.__dict__['_handler'] = None
        Delegator.__init__(self, Data)
        node_checker = ClassChecker(self.__class__)
        ConstrainedList.__init__(self, [], node_checker)
        self.Data = Data
        self.Parent = Parent
        if Children:
            self.extend(Children)

    def __getslice__(self, *args, **kwargs):
        """Override ConstrainedList: make sure slice is just a list."""
        return list.__getslice__(self, *args, **kwargs)

    def __getitem__(self, index):
        """Override ConstrainedList: make sure slice is just a list."""
        return list.__getitem__(self, index)

    def __copy__(self):
        """Shallow copy is not allowed because a node has only one parent."""
        raise TypeError, "Can't perform a shallow copy on a TreeNode."

    def __deepcopy__(self, memo=None, _nil=[]):
        """Deep copy returns a copy of the node, its children, and their data.
        
        Note: can ignore memo and _nil, since integrity constraints prevent the
        tree from containing cycles. However, they need to be there to maintain
        deepcopy interface.
        """
        result = self.__class__()
        for k in self.__dict__:
            if k not in self._exclude_from_copy:
                result.__dict__[k] = deepcopy(self.__dict__[k])
        result.Data = deepcopy(self.Data)
        for c in self:
            result.append(c.__deepcopy__())
        return result
        
    copy = __deepcopy__

    def clear(self):
        """Deletes the subtree containing all children of self.

        Useful for releasing memory held by large trees.

        Note: does not affect self, but only its children.
        """
        for i in self:
            i.clear()
        self[:] = []
        
    def _get_data(self):
        """Accessor for node data."""
        if not hasattr(self, '_data'):
            self._data = None
        return self._data

    def _set_data(self, data):
        """Mutator for node data: forwards attributes correctly."""
        self._data = data
        self._handler = data

    Data = property(_get_data, _set_data)

    def nameUnnamedNodes(self):
        """sets the Data property of unnamed nodes to an arbitrary value

        Internal nodes are often unnamed and so this function assigns a
        value for referencing."""
        #make a list of the names that are already in the tree
        names_in_use = []
        for node in self.traverse():
            if node.Data:
                names_in_use.append(node.Data)
        #assign unique names to the Data property of nodes where Data = None
        name_index = 1
        for node in self.traverse():
            if not node.Data:
                new_name = 'node' + str(name_index)
                #choose a new name if name is already in tree
                while new_name in names_in_use:
                    name_index += 1
                    new_name = 'node' + str(name_index)
                node.Data = new_name
                names_in_use.append(new_name)
                name_index += 1
    
    def _get_parent(self):
        """Accessor for parent."""
        if not hasattr(self, '_parent'):
            self._parent = None
        return self._parent

    def _set_parent(self, Parent):
        """Mutator for parent: cleans up ref from old parent."""
        if Parent is self:
            raise TreeError, "Can't make node %s its own parent." % `self`
        if hasattr(Parent, 'Ancestors'):
            for a in Parent.Ancestors:
                if a is self:
                    raise TreeError, "Can't make node %s its own ancestor." \
                    % `self`
        curr_parent = self._parent
        if curr_parent is not None:
            curr_parent.removeNode(self)
            self._parent = None
        if Parent is not None:
            Parent.append(self)

    Parent = property(_get_parent, _set_parent)

    def _get_index(self):
        """Accessor for index: returns position of self in parent's list."""
        if self.Parent is None:
            return None
        else:
            return self.Parent.index(self)

    def _set_index(self, index):
        """Mutator for index: moves self to new location in parent's list.
        
        NOTE: index is relative to the new list after self is removed, not to
        the old list before self is removed.
        """
        if self.Parent is None:
            raise TreeError, "Can't set Index in node %s without parent." % self
        else:
            curr_parent = self.Parent
            curr_parent.removeNode(self)
            curr_parent.insert(index, self)

    Index = property(_get_index, _set_index)

    def _prepare_node_for_addition(self, item):
        """Given item, turns item into a node suitable for addition to self."""
        #check if item has parent, and, if so, that current node isn't it
        if hasattr(item, 'Parent'):
            curr_parent = item.Parent
            if curr_parent is self:
                raise DuplicateNodeError, "Node %s is already a child of %s" %\
                    (item, self)
            for a in self.Ancestors:
                if a is item:
                    raise TreeError, \
                "Can't make %s a child of its descendant %s" % (item, self)
                
            if curr_parent is not None:
                curr_parent.removeNode(item)
            new_node = item
        else:
            #no parent: need to turn item into a node, using item as data
            new_node = self.__class__(Data=item)
        new_node._parent = self #direct access to avoid circular ref
        return new_node

    def removeNode(self, target):
        """Removes node by identity instead of value.
        
        Returns True if node was present, False otherwise.
        """
        for i, curr_node in enumerate(self):
            if curr_node is target:
                del self[i]
                return True
        return False

    def __add__(self, other):
        """Returns list containing items in self and items in other."""
        return list(self) + list(other)
    
    def __delitem__(self, index):
        """Deletes item at specified index from self."""
        if isinstance(index, slice):
            indices = index.indices(len(self))
            for i in range(*indices):
                self[i]._parent = None
        else:
            self[index]._parent = None
        super(TreeNode, self).__delitem__(index)
        
    def __delslice__(self, start, stop):
        """Deletes all items between start and stop from self."""
        del self[start:stop:1]

    def __eq__(self, other):
        """Compares for equality first by identity, then by Data."""
        if self is other:
            return True
        try:
            return self.Data == other.Data
        except AttributeError:
            return self.Data == other

    def __ge__(self, other):
        """Compares self >= other first by identity, then by Data."""
        if self is other:
            return True
        try:
            return self.Data >= other.Data
        except AttributeError:
            return self.Data >= other
 
    def __gt__(self, other):
        """Compares self > other first by identity, then by Data."""
        if self is other:
            return False
        try:
            return self.Data > other.Data
        except AttributeError:
            return self.Data > other

    def __iadd__(self, items):
        """Appends everything in items to self in place."""
        new_nodes = map(self._prepare_node_for_addition, items)
        return super(TreeNode, self).__iadd__(new_nodes)
      
    def __imul__(self, x):
        """Not allowed: would require deep copy to replicate nodes."""
        raise NotImplementedError, \
            "Cannot replicate tree nodes without deep copy."
 
    def __le__(self, other):
        """Compares self <= other first by identity, then by Data."""
        if self is other:
            return True
        try:
            return self.Data <= other.Data
        except AttributeError:
            return self.Data <= other
 
    def __lt__(self, other):
        """Compares self < other first by identity, then by Data."""
        if self is other:
            return False
        try:
            return self.Data < other.Data
        except AttributeError:
            return self.Data < other

    def __mul__(self, x):
        """Returns a list containing x copies of the nodes in self."""
        return list(self) * x
    
    def __ne__(self, other):
        """Compares self != other first by identity, then by Data."""
        if self is other:
            return False
        try:
            return self.Data != other.Data
        except AttributeError:
            return self.Data != other
        
    def __rmul__(self, x):
        """Returns a lsit containing x copies of the nodes in self."""
        return list(self) * x
    
    def __setitem__(self, index, item):
        """Sets self[index] to item, cleaning up references."""
        if isinstance(index, slice):
            indices = range(*index.indices(len(self)))
            for i in indices:
                self[i]._parent = None
            new_nodes = map(self._prepare_node_for_addition, item)
            super(TreeNode, self).__setitem__(index, new_nodes)
        else:
            self[index]._parent = None
            new_node = self._prepare_node_for_addition(item)
            super(TreeNode, self).__setitem__(index, new_node)
        
    def __setslice__(self, start, stop, items):
        """Sets self[start:stop] to the sequence items."""
        for i in range(start, min(stop, len(self))):
            self[i]._parent = None
        new_nodes = map(self._prepare_node_for_addition, items)
        super(TreeNode, self).__setslice__(start, stop, new_nodes)
     
    def __str__(self):
        """Returns informal Newick-like representation of self."""
        if self:
            return str(self.Data) + '(' + ','.join(map(str, self)) + ')'
        else:
            return str(self.Data)

    def append(self, item):
        """Appends item to self, setting parent to self."""
        new_node = self._prepare_node_for_addition(item)
        super(TreeNode, self).append(new_node)

    def extend(self, item):
        """Like __iadd__, but returns None."""
        self += item
  
    def insert(self, position, item):
        """Inserts item into children at position, setting parent to self."""
        new_node = self._prepare_node_for_addition(item)
        super(TreeNode, self).insert(position, new_node)

    def pop(self, index=-1):
        """Removes item at specified index, resetting parent."""
        item = super(TreeNode, self).pop(index)
        item._parent = None
        return item

    def remove(self, item):
        """Removes first instance of item from self."""
        position = self.index(item)
        self[position]._parent = None
        super(TreeNode, self).remove(item)

    def _get_ancestors(self):
        """Returns all ancestors back to the root."""
        result = []
        curr = self
        while curr.Parent is not curr: #may not be its own parent
            if curr.Parent is None:
                break
            result.append(curr.Parent)
            curr = curr.Parent
        return result

    Ancestors = property(_get_ancestors)

    def lastCommonAncestor(self, other, require_identity=True):
        """Finds last common ancestor of self and other, or None.
        
        if require_identity, tests by identity instead of equality
        """
        #detect trivial case
        if self is other:
            return self
        #otherwise, check the list of ancestors
        my_ancestors = [self] + self.Ancestors
        other_ancestors = [other] + other.Ancestors
        other_ancestors.reverse()
        LCA = None
        #convert to id if checking by identity
        if require_identity:
            other_ids = map(id, other_ancestors)
            my_ids = map(id, my_ancestors)
            for index, i in enumerate(other_ids):
                if i not in my_ids:
                    break
                else:
                    LCA = index
            if LCA is None:
                return None
            else:
                return other_ancestors[LCA]
        #get here if we're only checking by equality
        for a in other_ancestors:
            if a not in my_ancestors:
                break
            else:
                LCA = a
        return LCA

    def _get_root(self):
        """Returns root of the tree self is in."""
        if self.Parent in (None, self):
            return self
        else:
            return self.Ancestors[-1]
    
    Root = property(_get_root)

    def _get_children(self):
        """Returns all children: equivalent of list(self)"""
        return list(self)
    def _set_children(self, Children):
        """Sets Children to supplied data."""
        self[:] = Children

    Children = property(_get_children, _set_children)

    def _get_terminal_children(self):
        """Returns direct children in self that have no descendants."""
        return [i for i in self if not i]
    
    TerminalChildren = property(_get_terminal_children)

    def _get_nonterminal_children(self):
        """Returns direct children in self that have descendants."""
        return filter(None, self)

    NonTerminalChildren = property(_get_nonterminal_children)

    def _get_child_groups(self):
        """Returns list containing lists of children sharing a state.
        
        In other words, returns runs of terminal and nonterminal children.
        """
        #bail out in trivial cases of 0 or 1 item
        if not self:
            return []
        if len(self) == 1:
            return [self[0]]
        #otherwise, have to do it properly... 
        result = []
        curr = []
        state = None
        for i in self:
            curr_state = bool(i)
            if curr_state == state:
                curr.append(i)
            else:
                if curr:
                    result.append(curr)
                    curr = []
                curr.append(i)
                state = curr_state
        #handle last group
        result.append(curr)
        return result

    ChildGroups = property(_get_child_groups)

    def _get_terminal_descendants(self):
        """Returns all terminal descendants of self in a flat list."""
        result = []
        for i in self:
            if not i:
                result.append(i)
            else:
                result.extend(i.TerminalDescendants)
        return result

    TerminalDescendants = property(_get_terminal_descendants)

    def traverse(self, self_before=True, self_after=False):
        """Returns iterator over descendants.

        self_before includes each node before its descendants if True.
        self_after includes each node after its descendants if True.  
        
        self_before and self_after are independent. If neither is True, only
        terminal nodes will be returned.

        Note that if self is terminal, it will only be included once even if
        self_before and self_after are both True.

        This is a depth-first traversal. Since the trees are not binary,
        preorder and postorder traversals are possible, but inorder traversals
        would depend on the data in the tree and are not handled here.
        """
        if self:
            if self_before:
                yield self
            for child in self:
                for i in child.traverse(self_before, self_after):
                    yield i
            if self_after:
                yield self
        else:
            yield self

        
                
        
            

    def _get_siblings(self):
        """Returns all nodes that are children of the same parent as self.

        Note: excludes self from the list.
        """
        if self.Parent is None:
            return []
        else:
            result = self.Parent[:]
            del result[self.Index]
            return result

    Siblings = property(_get_siblings)
                

    def separation(self, other):
        """Returns number of edges separating self and other."""
        #detect trivial case
        if self is other:
            return 0
        #otherwise, check the list of ancestors
        my_ancestors = [self] + self.Ancestors
        other_ancestors = [other] + other.Ancestors
        my_ancestors.reverse()
        other_ancestors.reverse()
        other_ids = map(id, other_ancestors)
        my_ids = map(id, my_ancestors)
        #will implicitly find the LCA by id, then take all the branch length
        #from (not including) the LCA to self and other.
        my_index = None
        for other_index, i in enumerate(other_ids):
            try:
                my_index = my_ids.index(i)
            except ValueError:
                other_index -= 1 #ran off the end of the other list
                break
        if my_index is None:
            return None

        return len(my_ancestors)-my_index+len(other_ancestors)-other_index-2

    def __repr__(self):
        c = self.__class__
        return "<%s.%s object at %s>" % (c.__module__,c.__name__,hex(id(self)))

    def makeTreeArray(self, dec_list=None):
        """Makes an array with nodes in rows and descendants in columns.
        
        A value of 1 indicates that the decendant is a descendant of that node/
        A value of 0 indicates that it is not
        
        also returns a list of nodes in the same order as they are listed
        in the array"""
        #get a list of internal nodes
        node_list = [node for node in self.traverse() if node.Children]
        node_list.sort()
        
        #get a list of TerminalDescendants Data if one is not supplied
        if not dec_list:
            dec_list = [dec.Data for dec in self.TerminalDescendants]
            dec_list.sort()
        #make a blank array of the right dimensions to alter
        result = resize(array([0]), (len(node_list), len(dec_list)))
        #put 1 in the column for each child of each node
        for i, node in enumerate(node_list):
            children = [dec.Data for dec in node.TerminalDescendants]
            for j, dec in enumerate(dec_list):
                if dec in children:
                    result[i,j] = 1
        return result, node_list
    
    def removeDeleted(self,is_deleted):
        """Removes all nodes where is_deleted tests true.
        
        Internal nodes that have no children as a result of removing deleted
        are also removed.
        """
        #Traverse tree
        for node in list(self.traverse(self_before=False,self_after=True)):
            #if node is deleted
            if is_deleted(node):
                #Store current parent
                curr_parent=node.Parent
                #Set current node's parent to None (this deletes node)
                node.Parent=None
                #While there are no chilren at node and not at root
                while (not curr_parent.Children) and (curr_parent is not None):
                    #Save old parent
                    old_parent=curr_parent
                    #Get new parent
                    curr_parent=curr_parent.Parent
                    #remove old node from tree
                    old_parent.Parent=None
    
    def prune(self):
        """Reconstructs correct topology after nodes have been removed.
        
        Internal nodes with only one child will be removed and new connections
        will be made to reflect change.
        """
        #traverse tree
        for node in self.traverse(self_after=True,self_before=False):
            #save current parent
            curr_parent=node.Parent
            #If not at the root
            if curr_parent is not None:
                #if current node only has 1 child
                if len(node.Children) == 1:
                    #save child
                    child=node.Children[0]
                    #remove current node by setting parent to None
                    node.Parent=None
                    #Connect child to current node's parent
                    child.Parent=curr_parent

    def setDescendantTips(self):
        """Sets n.DescendantTips on each node."""
        for n in self.traverse(self_before=False, self_after=True):
            if not n.Children:
                n.DescendantTips = [n]
            else:
                curr = []
                for c in n.Children:
                    curr.extend(c.DescendantTips)
                n.DescendantTips = curr

    def setDescendantTipProperty(self,f,prop_name='Trait',force_recalc=False):
        """Sets n.propMean, n.propStdev) of f(node) for all nodes in self.
        
        These correspond to T_i and S_i respectively in AOT, Ackerley 2004.
        
        Example usage:
        (a) You have a dict mapping leaf -> property:
            leaf_f = lambda node: d[node.Data]
        (b) You have the property stored in leaf.prop_xyz:
            leaf_f = lambda node: node.prop_xyz

        tree.setDescendantTipProperty(leaf_f, 'MyProp') will set on each node
        n.MyPropMean and n.MyPropStdev.
        """
        for node in self.traverse(self_before=False, self_after=True):
            if force_recalc or not hasattr(node, 'DescendantTips'):
                node.setDescendantTips()
            values = map(f, node.DescendantTips)
            setattr(node, prop_name+'Mean', mean(values))
            if len(values) > 1:
                std = stdev(values)
            else:
                std = 0
            setattr(node, prop_name+'Stdev', std)

    def mapAttr(self, label_map, attr='Data', new_attr='Data', \
        self_before=True, self_after=False):
        """Maps attr according to label_map.

        label_map should be a dict {old:new} or a function f(old) -> new.

        If label_map is a dict, leaves unchanged any nodes not in the map.

        attr: attribute to read from (default: 'Data')
        
        new_attr: attribute to write to (default: 'Data', i.e. overwrites orig)
        
        self_before, self_after: passed to traverse().
        """
        if isinstance(label_map, dict):
            f = lambda k: label_map.get(k, k)   #unchanged if unmapped
        else:
            f = label_map
        for node in self.traverse(self_before=self_before, \
            self_after=self_after):
            setattr(node, new_attr, f(getattr(node, attr)))

    def changeFromParent(self, f):
        """Calculates f(self) - f(parent).
        
        If f is a string instead of a function, assume it's an attribute
        instead.
        """
        if isinstance(f, str):
            return getattr(self, f) - getattr(self.Parent, f)
        else:
            return f(self) - f(self.Parent)

    def attrTable(self, attrs, self_before=True,self_after=False, default=None):
        """Returns list of lists containing each attr at each node, or default.
        
        attrs: list of attr names to collect, in order

        self_before, self_after: passed to traverse().
        """
        result = []
        for node in self.traverse(self_before, self_after):
            curr = []
            for a in attrs:
                if hasattr(node, a):
                    curr.append(getattr(node,a))
                else:
                    res.append(default)
            result.append(curr)
        return result

    def setContainsChildCache(self):
        """Sets "LeafSet", "NumLeaves", and "TotalNodes" properties
       
        Will cache Data property of terminal descendants for much faster
        tree operations.

        Need to call before containsChild() will work 
        """
        for n in self.traverse(self_before=False, self_after=True):
            setattr(n, "LeafSet", set([x.Data for x in n.TerminalDescendants]))
            setattr(n, "NumLeaves", len(n.LeafSet))
            total_nodes = 1

            if n.Children:
                for ix, child in enumerate(n.Children):
                    total_nodes += child.TotalNodes
            setattr(n, "TotalNodes", total_nodes) 

    def containsChild(self, other_leaf_key):
        """Return true if other_leaf_key is child of current node"""
        return other_leaf_key in self.LeafSet

    def setIds(self, id_fun=lambda x: x.Data.split("_")[-1]):
        """
        Sets "LeafLabel", "LeafCts", and "ContainsAll" attributes

        id_fun: function that takes node and generate a unique id (label)
            for each node. By default will create a label consisting of 
            the string to the right of the last underscore in the data
            attribute. E.g. if the node has data label of 1234_HSA, the
            function will return a unique lable of "HSA". the idea being
            that if your tree has multiple human (HSA) sequences, the
            result of the function will be multiple nodes w/the same
            label. 

        The LeafLabel attribute is the the result of the id_fun function.

        The LeafCts attribute is an array with counts of the leaves with the 
            same label.

        The ContainsAll attribute is True when it contains every instance 
            of the LeafLabels of its terminal descendants. E.g. the set
            of LeafLabels of its terminal descendants occur nowhere else
            in the tree. 

        This is used by the uniqueIds function to remove duplicate species
        from the tree but can be used for any label you choose.
        """
        labels =  [id_fun(x)  for x in self.TerminalDescendants]
        u_labels = list(set(labels))
        len_u_labels = len(u_labels)
        labels_dict =  dict(zip(u_labels, range(len_u_labels)))
        all_cts = zeros(len(u_labels))

        for label in labels: 
            all_cts[labels_dict[label]] += 1
      
        for n in self.traverse(self_before=False, self_after=True):
            if not n.Children:
                setattr(n, "LeafLabel", id_fun(n))
                setattr(n, "LeafCts", zeros(len_u_labels))
                n.LeafCts[labels_dict[n.LeafLabel]] = 1
            else:
                n.LeafCts = zeros(len_u_labels)
                for c in n.Children:
                    n.LeafCts += c.LeafCts 
            nzero = nonzero(n.LeafCts)
            total = sum(take(all_cts, nzero)- take(n.LeafCts, nzero))
            setattr(n, "ContainsAll", (total == 0))
     
    def uniqueIds(self, id_fun=lambda x: x.Data.split("_")[-1],
                  set_branchlength=False):
        """
        Randomly remove duplicate id label nodes from tree (e.g. species)

        Collapases tree and remove duplicate labels as defined by id_fun. 
        
        E.g. if you have a tree w/duplicate sequences from species, will
        produce a tree with exactly 1 sequence per species.

        By default expects Data property to be set with "gi_species" which then         sets the LeafLabel attribute to species. E.g 123456_HSA -> HSA or 
        883834_DME -> DME but you can define any function that takes a node 
        and produces a label.

        id_fun: See doc string for setIds.

        set_branchlength: if True, will propagate branchlengths

        After LeafLabel and ContainsAll attributes are set for the tree,
        collapses all nodes where ContainsAll = False. Then randomly
        removes all but one of the duplicated nodes so you are left with
        a tree with exatly one node per LeafLabel (e.g. species).
        """
        # label nodes 
        self.setIds(id_fun) 

        # delete internal nodes
        for n in self.traverse():
            if not n.ContainsAll and n.Children and n.Parent:
                self.collapseNode(n, set_branchlength)

        # bin up all duplicates
        del_bins = {} 
        for lab_tup in [(x.LeafLabel, x) for x in self.TerminalDescendants \
                                         if not x.ContainsAll ]:
            label, cur_node = lab_tup
            if label not in del_bins:
                del_bins[label] = []
            del_bins[label].append(cur_node)

        # randomly pick one of the nodes to keep, delete the rest
        for cur_label, dn in del_bins.items():
            keep = choice(dn) 

            for cur in [y for y in dn if y != keep]:
                cur_parent = cur.Parent
                cur.Parent = None
                if len(cur_parent) == 1 and cur_parent.Parent:
                    self.collapseNode(cur_parent,  set_branchlength)

class PhyloNode(TreeNode):
    """Contains phylogeny-specific tree methods.
    
    Assumes that the Data for each node has a BranchLength property, possibly
    None rather than 0.

    PhyloNode is guaranteed to have BranchLength and Weight properties.
    """
    def __init__(self, Data=None, Children=None, Parent=None, BranchLength=None,
        Weight=None):
        """Adds BranchLength and Weight to superclass __init__."""
        super(PhyloNode, self).__init__(Data, Children, Parent)
        self.__dict__['BranchLength'] = BranchLength
        self.__dict__['Weight'] = Weight

    def distance(self, other):
        """Returns total distance using self.BranchLength, 0 if not found"""
        #detect trivial case
        if other is None:
            raise ValueError, "Distance undefined when other node is None."

        if self is other:
            return 0
        #otherwise, check the list of ancestors
        my_ancestors = [self] + self.Ancestors
        other_ancestors = [other] + other.Ancestors
        my_ancestors.reverse()
        other_ancestors.reverse()
        other_ids = map(id, other_ancestors)
        my_ids = map(id, my_ancestors)
        #will implicitly find the LCA by id, then take all the branch length
        #from (not including) the LCA to self and other.
        my_index = None
        for other_index, i in enumerate(other_ids):
            try:
                my_index = my_ids.index(i)
            except ValueError:
                other_index -= 1 #ran off the end of the other list
                break
        if my_index is None:
            return None

        return sum([i.BranchLength or 0 for i in my_ancestors[my_index+1:]])\
          + sum([i.BranchLength or 0 for i in other_ancestors[other_index+1:]])

    def __str__(self):
        """Returns string representation of self, in Newick format."""
        if hasattr(self, 'Label'):
            label = str(self.Label)
        elif hasattr(self, 'Id'):
            label = str(self.Id)
        else:
            if (self.Data is None) and (self or not self.Parent):    
                #no label if empty and internal
                label = ''
            else:
                label = str(self.Data)
        if self:
            child_string = ','.join(map(str, self))
         
        if self.Parent is None: #root of tree
            if self:
                return '(%s)%s' % (child_string, label)
            else:
                return '()%s' % label
        else:   #internal node
            if self:
                if self.BranchLength != None:
                    return '(%s)%s:%s' % \
                        (child_string, label, self.BranchLength)
                else:
                    return '(%s)%s' % \
                        (child_string, label)
            else:
                if self.BranchLength != None:
                    return '%s:%s' % (label, self.BranchLength)
                else:
                    return '%s' % (label)
                
    def collapseNode(self, node, set_branchlength=True):
        """Removes an internal node annd attaches Children to Parent

        Adds the branchlength of the removed node to the child node
        
        node: The node to remove
        set_branchlength: if True, will propagate BranchLength attribute"""
        #save the identity of the parent
        parent = node.Parent
        #remove node from tree by setting parent to None
        node.Parent = None
        #attach children to parent
        for child in node.Children:
            child.Parent = parent
            if set_branchlength:
                child.BranchLength = child.BranchLength + node.BranchLength

    def setTipDistances(self):
        """Sets distance from each node to the most distant tip."""
        for node in self.traverse(self_before=False, self_after=True):
            if node.Children:
                node.TipDistance = max([c.BranchLength + c.TipDistance for \
                    c in node.Children])
            else:
                node.TipDistance = 0

    def scaleBranchLengths(self, max_length=100, ultrametric=False):
        """Scales BranchLengths in place to integers for ascii output.

        Warning: tree might not be exactly the length you specify.

        Set ultrametric=True if you want all the root-tip distances to end
        up precisely the same.
        """
        self.setTipDistances()
        orig_max = max([n.TipDistance for n in self.traverse()])
        if not ultrametric: #easy case -- just scale and round
            for node in self.traverse():
                curr = node.BranchLength
                if curr is not None:
                    node.ScaledBranchLength =  \
                        max(1, int(round(1.0*curr/orig_max*max_length)))
        else:   #hard case -- need to make sure they all line up at the end
            for node in self.traverse(self_before=False, self_after=True):
                if not node.Children:   #easy case: ignore tips
                    node.DistanceUsed = 0
                    continue
                #if we get here, we know the node has children
                #figure out what distance we want to set for this node
                ideal_distance=int(round(node.TipDistance/orig_max*max_length))
                min_distance = max([c.DistanceUsed for c in node.Children]) + 1
                distance = max(min_distance, ideal_distance)
                for c in node.Children:
                    c.ScaledBranchLength = distance - c.DistanceUsed
                node.DistanceUsed = distance
        #reset the BranchLengths
        for node in self.traverse(self_before=True, self_after=False):
            if node.BranchLength is not None:
                node.BranchLength = node.ScaledBranchLength
            if hasattr(node, 'ScaledBranchLength'):
                del node.ScaledBranchLength
            if hasattr(node, 'DistanceUsed'):
                del node.DistanceUsed
            if hasattr(node, 'TipDistance'):
                del node.TipDistance

    def setWeightedProperty(self, f, prop_name='Prop', branch_delta=1e-4):
        """Sets weighted property based on branch length at each node.
        
        branch_delta is minimum branch length to use for weighting purposes
        (can't handle zero branch length).

        The WeightedMean is equivalent to A_i and the WeightedStdev is
        equivalent to D_i in AOT.

        Example usage:
        (a) You have a dict mapping leaf -> property:
            leaf_f = lambda node: d[node.Data]
        (b) You have the property stored in leaf.prop_xyz:
            leaf_f = lambda node: node.prop_xyz

        tree.setWeightedProperty(leaf_f, 'MyProp') will set on each node
        n.MyPropWeightedMean and n.MyPropWeightedStdev.
        """
        mean_name = prop_name+'WeightedMean'
        stdev_name = prop_name+'WeightedStdev'
        for n in self.traverse(self_before=False, self_after=True):
            if not n.Children:
                setattr(n, mean_name, f(n))
                setattr(n, stdev_name, 0)
            else:
                num = 0
                den = 0
                branchlengths = [max(c.BranchLength, branch_delta) \
                    for c in n.Children]
                child_vals = [getattr(c, mean_name) for c in n.Children]

                num = sum([(1.0*i)/j for i, j in zip(child_vals, branchlengths)])
                den = sum([1.0/j for j in branchlengths])
                result = num/den
                setattr(n, mean_name, result)
                std = sqrt(sum([(c-result)**2 for c in child_vals])\
                    /len(child_vals))
                setattr(n, stdev_name, std)

    
if __name__ == '__main__':
    from old_cogent.parse.tree import DndParser
    s = '((a:7.9,((b:0.1,c:0.1):0.1,d:0.2):7.7):0.1,e:8.0)'
    t = DndParser(s)
    print t
    t.scaleBranchLengths(8, ultrametric=True)
    print t
