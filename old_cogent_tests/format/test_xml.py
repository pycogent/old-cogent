#!/usr/bin/env python
#file evo/writers/test_xml.py

"""Unit tests for Xml classes.

Revision History

9/23/03 Rob Knight: adapted from test_bayesxml.

11/12/03 Rob Knight: moved into cogent.format.
"""

from old_cogent.util.unit_test import TestCase, main
from old_cogent.format.xml import Xml

class XmlTests(TestCase):
    """Tests of the generic Xml object"""
    def test_init_tag_only(self):
        """Xml should allow initialization with just a tag"""
        xml = Xml('tag')
        self.assertEqual(str(xml), "<tag />")

    def test_init_nothing(self):
        """Xml should allow empty initialization"""
        xml = Xml()
        self.assertEqual(str(xml), '')

    def test_init_elements(self):
        """Xml should allow element nesting"""
        inners = map(Xml, ['inner'] * 3)
        outer = Xml('outer', inners)
        self.assertEqual(str(outer), 
        "<outer>\n<inner />\n<inner />\n<inner />\n</outer>")

    def test_init_string_elements(self):
        """Xml should accept list of elements as children"""
        xml = Xml('tag', ['abc', 'def', 'ghi'])
        self.assertEqual(str(xml), '<tag>\nabc\ndef\nghi\n</tag>')

    def test_init_attributes(self):
        """Xml should correctly handle attributes"""
        xml = Xml('tag', Attributes={1:'abc', 2:345})
        self.assertEqual(str(xml), '<tag 1="abc" 2="345" />')
        xml = Xml('tag', Attributes={'class_':'abc', 'xyz':345})
        self.assertEqual(str(xml), '<tag class="abc" xyz="345" />')
           
    def test_init_delimiter(self):
        """Xml should use delimiters correctly"""
        xml = Xml('tag', ['abc', 'def', 'ghi'], Delimiter='')
        self.assertEqual(str(xml), '<tag>abcdefghi</tag>')
    
    def test_getattr(self):
        """Xml should treat Attributes as properties of itself"""
        xml = Xml('tag', Attributes={'class_':'abc', 'xyz':345})
        self.assertEqual(xml.class_, 'abc')
        self.assertEqual(xml.xyz, 345)

    def test_setattr(self):
        """Xml should set Attributes as properties of itself"""

        x = Xml()
        x.class_ = 3
        self.assertEqual(x.class_, 3)
        x.class_ = 4
        self.assertEqual(x.class_, 4)
        
        xml = Xml('tag', Attributes={'class_':'abc', 'xyz':345})
        self.assertEqual(xml.class_, 'abc')
        xml.class_ = 3

        self.assertEqual(xml.class_, 3)
        self.assertEqual(xml.Attributes['class_'], 3)
        xml.__dict__['efg'] = [4]
        self.assertEqual(xml.efg, [4])
        assert 'efg' not in xml.Attributes
        xml.__dict__['class_'] = {4:5}
        self.assertEqual(xml.class_, {4:5})
        self.assertEqual(xml.Attributes['class_'], 3)
   
    def test_TextNodes(self):
        """Xml TextNodes should return correct list"""
        a, b, c = map(Xml, 'abc')
        x = Xml('tag', [a, 'abc', 'def', b, c, 'ghi'])
        self.assertEqual(a.TextNodes, [])
        a.append(b)
        self.assertEqual(a.TextNodes, [])
        a.append('xyz')
        self.assertEqual(a.TextNodes, ['xyz'])
        self.assertEqual(x.TextNodes, ['abc', 'def', 'ghi'])
  
#run the following if invoked from command-line
if __name__ == "__main__":
    main()
