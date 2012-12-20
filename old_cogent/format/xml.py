#!/usr/bin/env python
#file evo/writers/xml.py

"""Provides lightweight XML-writing class.

Owner: Rob Knight rob@spot.colorado.edu

Status: Prototype

Usage:

    x = Xml(Tag='inner', Attributes={'color':'red'})
    y = Xml(Tag='outer', Attributes={'color':'blue'}, Children=[x, 'abc'])
    print str(y)
    <outer color="blue">\\n<inner color="red" />\\nabc\\n</outer>
    
Implementation Notes

The interaction between Delegator and MappedRecord is rather subtle. 
MappedRecord pretends to have every item, so hasattr() always returns True. 
Delegator (of which TreeNode is a subclass) forwards requests to its _handler, 
so if its _handler is a MappedRecord hasattr() always returns True for it as 
well. This led to a problem where Xml would set attributes such as _parent 
and _data in its handler instead of itself, leading to circular references and 
other such unpleasantries.

The solution was to change Delegator so that for __setattr__ calls
it first looks in the object's __dict__, then in itself, then in its 
handler, and then sets it in itself as a new attribute if all of the above
fail. I don't think this will cause problems with class data, since you
can't change class data with __setattr__ on the objects anyway, but this
interaction is something to watch out for. TreeNode now explicitly creates
the private attributes it needs in its own __dict__, which is probably a
good policy for classes that inherit from Delegator in general.

The is_not_empty function is needed because an Xml object is ultimately a
list, and returns False if it has no items (i.e. Children). However, 
empty tags are widely useful in XML. Overriding __nonzero__ is not an 
option, however, since it would break many TreeNode methods that rely on
__nonzero__ to decide whether a node has children or not. Solution is to
check Xml objects for presence of tag, attributes and children, any of
which makes them non-empty for display purposes. Note that this also allows
us to handle textnodes containing numeric 0 or bool False not converted
to strings, which would otherwise be stripped out by the filter(). The
filter provides a useful purpose in stripping out truly empty text nodes,
arrays, dicts, and other miscellany.

Revision History

9/23/03 Rob Knight: Adapted from bayesxml.py in BayesFold.

10/14/03 Rob Knight: Rewrote to use TreeNode and MappedRecord.

11/12/03 Rob Knight: moved into cogent.format
"""
from old_cogent.util.misc import unreserve
from old_cogent.base.tree import TreeNode
from old_cogent.parse.record import MappedRecord
        
def is_not_empty(x):
    """Needed for filtering tag output correctly."""
    if x:
        return True
    elif x == 0:
        return True
    elif x is False:
        return True
    elif isinstance(x, Xml):
        if x.Tag or x.Children or x.Attributes:
            return True
    else:
        return False

class Xml(TreeNode):
    """Base class for objects that can write themselves as XML.
    
    Derived classes may override __init__ and/or __str__ to present simplified
    interface and/or specialized needs.
    """
    def __init__(self, Tag=None, Children=None, Attributes=None, Parent=None,
        Data=None, Delimiter='\n'):
        """Returns new Xml object with specified Tag and othe attributes.
        
        Tag:        Text containing the tag name.
        Children:   Any child nodes. Will be converted to Xml objects.
        Attributes: dict containing name: value pairs for attributes.
        Parent:     Parent node.
        Data:       Synonym for Attributes: present mainly to support TreeNode
                    interface. Both Data and Attributes may be present.
        Delimiter:  Separates successive elements (default: \\n). Note that if
                    the delimiter is '', adjacent text nodes will be 
                    concatenated.
        """
        super(Xml, self).__init__()
        if Data is None:
            Data = MappedRecord()
        self.Data = Data
        self.__dict__['Tag'] = Tag
        self.__dict__['Delimiter'] = Delimiter
        if Attributes is not None:
            self.Data.update(dict(Attributes))
        if Children:
            self.extend(Children)

    def _get_text_nodes(self):
        """Returns all children of self whose Data is text."""
        return [i for i in self if isinstance(i.Data, str)]

    TextNodes = property(_get_text_nodes)

    def __str__(self):
        """Provides support for str(self), writing current object as XML."""
        if not self.Tag: #probably a text node
            if self.Data:
                return str(self.Data)
            else:
                return ''
        
        sep = self.Delimiter or ''
        attributes = self.Attributes.items()
        attributes.sort()
        attribute_text =  ' '.join([unreserve(str(key)) + '="'+ str(val) + '"' 
                              for key, val in attributes])
        element_text = sep.join(map(str, filter(is_not_empty, self)))
       
        pieces = ['<%s' % self.Tag] #always start with an open tag
        #add space-delimited list of attributes within tag if necessary
        if attribute_text:
            pieces.extend([' ', attribute_text])
        #add newline-delimited list of elements between tags if necessary
        if element_text:
            pieces.extend(['>',sep, element_text, sep,'</%s>' % self.Tag])
        #use empty tag closing form if there weren't any elements
        else:
            pieces.append(' />')
        #return the whole lot as a string
        return ''.join(pieces)

    def _get_attributes(self):
        """Accessor for Attributes"""
        return self.Data

    Attributes = property(_get_attributes)

