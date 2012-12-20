#/usr/bin/env python
#file evo/parsers/tree.py

"""Parsers for tree formats.

Owner: Rob Knight rob@spot.colorado.edu

Status: Development

Implementation Notes

The algorithm used here is fairly general: should possibly make the code
generalizable to tree strings that use alternative delimiters and symbols.
However, I can't think of any cases where alternatives are used, so this is
left to future work.

Should possibly build a dict of {label:TreeNode} while parsing to make it
convenient to fill in additional data later, e.g. to fill in sequences from
their numeric labels in Newick format. Alternatively, maybe TreeNode should
get a buildIndex() method that performs the equivalent task.

As of 12/27/03, should be capable of parsing the ClustalW .dnd files without
difficulty.

Revision History

Written 12/27/03 by Rob Knight.

3/9/04 Rob Knight: added constructor argument to DndParser to facilitate
using subclasses of PhyloNode.

11/4/04 Rob Knight: added explicit code for setting children as well as
parents to allow tree classes that don't automatically put in bidirectional
parent/child links. Refactored code that makes the new child into its own
function.

12/8/05 Cathy Lozupone: Changed DndParser/DndTokenizer so that tokens are 
ignored if they are within single quotes. This is so that Arb files where
group names contain tokens can be read. Arb places the nodes names within
single quotes if there are symbols.
"""
from old_cogent.base.tree import PhyloNode
from old_cogent.parse.record import RecordError
from string import strip, maketrans

_dnd_token_str = '(:),;'
_dnd_tokens = dict.fromkeys(_dnd_token_str)
_dnd_tokens_and_spaces = _dnd_token_str + ' \t\v\n'

remove_dnd_tokens = maketrans(_dnd_tokens_and_spaces, \
    '-'*len(_dnd_tokens_and_spaces))

def safe_for_tree(s):
    """Makes string s safe for DndParser by removing significant chars."""
    return s.translate(remove_dnd_tokens)

def bad_dnd_tokens(s, is_valid_name):
    """Returns list of bad dnd tokens from s, using is_valid_name for names.
    
    Useful for finding trees with misformatted names that break parsing.
    """
    for t in DndTokenizer(s):
        if t in _dnd_tokens:
            continue
        #also OK if it's a number
        try:
            float(t)
            continue
        except: #wasn't a number -- further tests
            pass
        if is_valid_name(t):
            continue
        #if we got here, nothing worked, so yield the current token
        yield t
        

def DndTokenizer(data):
    """Tokenizes data into a stream of punctuation, labels and lengths.
    
    Note: data should all be a single sequence, e.g. a single string.
    """
    in_quotes = False
    saved = []
    for d in data:
        if d == "'":
            in_quotes = not(in_quotes)
        if d in _dnd_tokens and not in_quotes:
            curr = ''.join(saved).strip()
            if curr:
                yield curr
            yield d
            saved = []
        else:
            saved.append(d)

def DndParser(lines, constructor=PhyloNode):
    """Returns tree from the Clustal .dnd file format, and anything equivalent.
    
    Will work even if lines is a single string, but will inefficiently
    re-join it into a string. Better to pass in as a list of one string.

    Tree is made up of cogent.base.tree.PhyloNode objects, with branch lengths
    (by default, although you can pass in an alternative constructor 
    explicitly).
    """
    data = ''.join(lines)
    left_count = data.count('(')
    right_count = data.count(')')
    if left_count != right_count:
        raise RecordError, "Found %s left parens but %s right parens." % \
            (left_count, right_count)
    
    tokens = DndTokenizer(data)
    curr_node = None
    state = 'PreColon'
    state1 = 'PreClosed'
    for t in tokens:
        if t == ':':    #expecting branch length
            state = 'PostColon'
            #prevent state reset
            continue
        if t == ')':  #closing the current node
            curr_node = curr_node.Parent
            state1 = 'PostClosed'
            continue
        if t == '(':    #opening a new node
            curr_node = _new_child(curr_node, constructor)
        elif t == ';':  #end of data
            break
        elif t == ',':  #separator: next node adds to this node's parent
            curr_node = curr_node.Parent
        elif state == 'PreColon' and state1 == 'PreClosed':   #data for the current node
            new_node = _new_child(curr_node, constructor)
            new_node.Data = t
            curr_node = new_node
        elif state == 'PreColon' and state1 == 'PostClosed':
            curr_node.Data = t
        elif state == 'PostColon':  #length data for the current node
            curr_node.BranchLength = float(t)
        else:   #can't think of a reason to get here
            raise RecordError, "Incorrect PhyloNode state? %s" % t
        state = 'PreColon'  #get here for any non-colon token
        state1 = 'PreClosed'
        
    if curr_node is not None and curr_node.Parent is not None:
        raise RecordError, "Didn't get back to root of tree."
   
    return curr_node    #this should be the root of the tree

def _new_child(old_node, constructor):
    """Returns new_node which has old_node as its parent."""
    new_node = constructor()
    new_node.Parent = old_node
    if old_node is not None:
        if new_node not in old_node.Children:
            old_node.Children.append(new_node)
    return new_node
