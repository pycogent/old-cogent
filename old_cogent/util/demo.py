#!/usr/bin/env python
#file evo/demo.py

"""Provides class for self-running demos.

Owner: Rob Knight rob@spot.colorado.edu

Status: Stable

Usage:  QuickDemo([[comment_1, code_1], [comment_2, code_2], ...], [to_string])

This module provides three main components:
    
    Example: class for a self-running example
    Demonstration: class that holds a list of Examples
    QuickDemo: factory method that constructs a Demonstration from a sequence
        of (comment, code) pairs

In practice, most of the time QuickDemo is what you want unless your needs are
specialized.

QuickDemo expects a sequence of (comment, code) pairs. Comment should be a
string: code should be a string containing valid Python code that can be
executed by the exec built-in function. If only one string is supplied, it
will be treated as a comment. Comment strings can also be supplied raw, e.g.

    q = QuickDemo('This is a test:', ['init','a=3'], ['print', 'print a'])

...will correctly treat 'This is a test' as a comment string rather than raising
an exception. More than two items in the sequence will, however, cause an
exception to be raised.

Multiline strings are acceptable both as code and as comment. QuickDemo strips
out all completely blank lines: to preserve blank lines inside a multiline 
string, start the line with a non-printing character such as a space or a tab.
This feature allows you to start the comment or code on the line after the 
triple quote without having the extra line appear in the output. For example:

    q = QuickDemo(['''
This is a multi-line comment.
\\t
It extends over several lines.
'''])

...will correctly print:

# This is a multi-line comment.
#
# It extends over several lines.

...without the leading and trailing # line that you would otherwise get.

The QuickDemo output is rather like the Python interpreter's:

    q = QuickDemo(['testing', ['set a', 'a=3'], [None, 'print a']])
    print q

# testing

# set a
>>> a=3
>>> print a
3

All comments insert a blank line before the comment is printed.

By default, QuickDemo prints the output to stdout in real time (i.e. as each
code string is executed). However, if the optional to_string parameter is set
to True (it's False by default), QuickDemo will instead store up everything that
gets sent to stdout and return it as a single string. Note that tracebacks are
caught and sent to stdout, not to stderr.

Revision History

10/12/03 Rob Knight: initially written after problems keeping real and 
pre-calculated results in sync with tree test.

10/30/03 Rob Knight: fixed behavior of multiline code blocks: now prints >>>
instead of ... when the code is unindented, unless the line starts with
else, elif, except, or finally.
"""
from old_cogent.util.misc import ConstrainedList, ClassChecker
import sys  #need to be able to modify sys.stdout
from sys import exc_info, _getframe
from traceback import format_tb
from StringIO import StringIO

class Example(object):
    """An example consists of a comment and optionally some code to execute.
    
    The Comment should be a string, possibly containing line breaks, that
    will be printed before the code and code result.
    
    The Code should be a string that can be exec'ed.
    """
    def __init__(self, *args):
        """Returns new Example object.
        
        First arg is the Comment, second is the Code.
        """
        num_args = len(args)
        if num_args > 2:
            raise TypeError, \
            "Example is initialized with Comment and Code, not %s" % (args,)
        elif len(args) == 2:
            self.Comment, self.Code = args
        elif len(args) == 1:
            self.Comment, self.Code = args[0], ''
        else:
            self.Comment, self.Code = '', ''

    def __call__(self, namespace=None):
        """Writes the comment, the code, and the result to sys.stdout."""
        out = sys.stdout
        comment = self.Comment

        if namespace is None:
            namespace = locals()
        
        if comment:
            out.write('\n')
            comment_lines = comment.split('\n')
            for c in filter(None, comment_lines):
                out.write('# ' + c + '\n')
                out.flush()
        
        code = self.Code
        if code:
            code_lines = code.split('\n')
            for c in filter(None, code_lines):
                if c.startswith(' ') or c.startswith('else') or \
                    c.startswith('elif') or c.startswith('except') \
                    or c.startswith('finally'):
                    out.write('... ' + c + '\n')
                else:
                    out.write('>>> ' + c + '\n')
                out.flush()
            try:
                exec self.Code in namespace
            except:
                type_, value, traceback = exc_info()
                out.write('Traceback:'+'\n')
                out.write("    %s: %s\n" % (type_, value))

is_example = ClassChecker(Example)

class Demonstration(ConstrainedList):
    """Holds list of examples: when run, prints each example in order."""
    def __init__(self, data=None, OutFile=None):
        """Returns new Demonstration object.

        Demonstration provides full list interface, so can append examples.
        """
        self.OutFile = OutFile
        super(Demonstration, self).__init__(data, Constraint=is_example)

    def __call__(self, my_vars=None):
        """Runs the Demonstration, optionally in namespace my_vars."""
        outfile = self.OutFile or sys.stdout
        orig_stdout = sys.stdout
        if outfile is not sys.stdout:
            sys.stdout = outfile

        if my_vars is None:
            my_vars = {}    #create our own namespace
        my_vars.update(locals())

        #print "MY VARS:"
        #print my_vars
            
        for i in self:
            i(my_vars)
        
        if sys.stdout is not orig_stdout:
            sys.stdout = orig_stdout

def QuickDemo(data, to_string=False):
    """Builds a Demonstration from a list of (comment, code) tuples and runs it.

    If there is one item in an entry, it will be treated as a comment. If there
    are two, it's (comment, code). More than two raises an exception.

    If you want to put in a line of code without a comment, the entry should
    look like ('', code).

    By default, writes output to sys.stdout. However, if to_string is True,
    stdout is redirected to a StringIO object and the string containing the
    data from this object is returned at the end.

    Remember that blank lines will be stripped out of both comments and code.
    A good way around this is to put a tab at the start of internal lines in
    comments that you want to preserve.
    """

    my_vars = {}
    my_vars.update(locals())
    caller = _getframe(1)
    my_vars.update(caller.f_locals)

    examples = []

    if to_string:
        outfile = StringIO()
    else:
        outfile = sys.stdout
    
    for d in data:
        if not d:
            continue    #skip any empty items
        if isinstance(d, str):  #shouldn't happen, but treat it as a comment
            examples.append(Example(d))
        else:
            examples.append(Example(*d))
    Demonstration(examples, outfile)(my_vars)
    if to_string:
        outfile.seek(0)
        return outfile.read()
    else:
        return None
