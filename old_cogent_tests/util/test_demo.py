#!/usr/bin/env python
#file evo/test_demo.py

"""Unit tests for demonstration classes.

Revision History

10/12/03 Rob Knight: initially written.
"""

from old_cogent.util.unit_test import TestCase, main
from old_cogent.util.demo import Example, Demonstration, QuickDemo
from old_cogent.util.misc import ConstraintError
from StringIO import StringIO
import sys

class ExampleTests(TestCase):
    """Tests of the Example object"""
    def setUp(self):
        """Setup for each test: resets sys.stdout to string we can read."""
        self.orig_out = sys.stdout
        sys.stdout = StringIO()

    def tearDown(self):
        """After each test, set sys.stdout back to what it was."""
        sys.stdout = self.orig_out
    
    def test_init(self):
        """Example init should work as expected"""
        #empty: Comment and Code are both ''
        e = Example()
        assert not e.Comment
        assert not e.Code
        #if one parameter, inits Comment
        e = Example('test')
        self.assertEqual(e.Comment, 'test')
        assert not e.Code
        #of two parameters, inits Comment and Code
        e = Example('test', 'a=3')
        self.assertEqual(e.Comment, 'test')
        self.assertEqual(e.Code, 'a=3')

    def test_call_empty(self):
        """Empty example should do nothing when called"""
        #try with stdout
        e = Example()
        e()
        sys.stdout.seek(0)
        self.assertEqual(sys.stdout.read(), '')

    def test_call_comment_only(self):
        """Example with only comment should print as expected"""
        e = Example('testing')
        e()
        sys.stdout.seek(0)
        self.assertEqual(sys.stdout.read(), '\n# testing\n')

    def test_call_comment_multiline(self):
        """Example with multiline comment should print as expected"""
        e = Example('\n\ntesting\n\nagain\n\n\n')
        e()
        sys.stdout.seek(0)
        self.assertEqual(sys.stdout.read(), '\n# testing\n# again\n')
         
    def test_call_code_only(self):
        """Example with only code should print as expected"""
        e = Example(None, 'a = 3')
        e()
        sys.stdout.seek(0)
        self.assertEqual(sys.stdout.read(), '>>> a = 3\n')

    def test_call_code_multiline(self):
        """Example with multiline code should print as expected"""
        e = Example('', '\n\na=3\n\nb=4\n\n\n')
        e()
        sys.stdout.seek(0)
        self.assertEqual(sys.stdout.read(), '>>> a=3\n>>> b=4\n')

    def test_call_code_indented(self):
        """Example with indented code should print as expected"""
        e = Example('', """
if 3 > 0:
    print True
else:
    print False
print 3 + 4
""")
        e()
        sys.stdout.seek(0)
        self.assertEqual(sys.stdout.read(), \
""">>> if 3 > 0:
...     print True
... else:
...     print False
>>> print 3 + 4
True
7
""")

    def test_call_code_traceback(self):
        """Example with code causing traceback should print as expected"""
        e = Example('', '\n\na=3\n\na/=0\n\n\n')
        e()
        sys.stdout.seek(0)
        self.assertEqual(sys.stdout.read(), """>>> a=3
>>> a/=0
Traceback:
    exceptions.ZeroDivisionError: integer division or modulo by zero
""")

    def test_call_both(self):
        """Example with comment and code should print as expected"""
        e = Example('Set a to 3', 'a = 3')
        e()
        sys.stdout.seek(0)
        self.assertEqual(sys.stdout.read(), '\n# Set a to 3\n>>> a = 3\n')

class DemonstrationTests(TestCase):
    """Tests of the Demonstration class."""
    
    def test_init_empty(self):
        """Demonstration() should be empty list with OutFile = None"""
        d = Demonstration()
        assert d.OutFile is None
        self.assertEqual(d, [])
        
    def test_list_ops(self):
        """Demonstration should support list interface"""
        d = Demonstration()
        e = Example()
        d.append(e)
        self.assertEqual(d, [e])
        f = Example('Test')
        d += [f]
        self.assertEqual(d, [e,f])

    def test_naughty_addition_prevented(self):
        """Demonstration should prohibit addition of non-Examples"""
        d = Demonstration()
        self.assertRaises(ConstraintError, d.append, 'xyz')

    def test_call(self):
        """Demonstration call should run all of the component tests"""
        orig_out = sys.stdout
        sys.stdout = StringIO()
        d = Demonstration()
        d.append(Example('test comment'))
        d.append(Example(None, 'a = 3'))
        d.append(Example('value of a should be 3', 'print a'))
        d()
        sys.stdout.seek(0)
        self.assertEqual(sys.stdout.read(),
"""
# test comment
>>> a = 3

# value of a should be 3
>>> print a
3
""")
        sys.stdout = orig_out

class QuickDemoTests(TestCase):
    """Tests of the QuickDemo factory function"""
    
    def test_init_default(self):
        """QuickDemo should write to stdout if to_string not supplied """
        orig_out = sys.stdout
        sys.stdout = StringIO()
        QuickDemo([
    'test comment',
    [None, 'a = 3'],
    ['value of a should be 3', 'print a'],
])
        sys.stdout.seek(0)
        self.assertEqual(sys.stdout.read(),
"""
# test comment
>>> a = 3

# value of a should be 3
>>> print a
3
""")
        sys.stdout = orig_out

    def test_init_string(self):
        """QuickDemo should redirect output to string if requested """
        q = QuickDemo([
    'test comment',
    [None, 'a = 3'],
    ['value of a should be 3', 'print a'],
], to_string=True)
        self.assertEqual(q,
"""
# test comment
>>> a = 3

# value of a should be 3
>>> print a
3
""")

#run the following if invoked from command-line
if __name__ == "__main__":
    main()
