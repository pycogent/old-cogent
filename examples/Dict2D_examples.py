#!/usr/bin/env python
# Dict2D_examples.py

# Owner: Greg Caporaso caporaso@colorado.edu

from old_cogent.base.dict2d import Dict2D, largest
from old_cogent.util.demo import QuickDemo
from old_cogent.base.stats import Freqs

demo = QuickDemo(
[
    "Demonstration of the Dict2D class",
    "Written by Greg Caporaso caporaso@colorado.edu 5/6/04",
    """
A Dict2D is meant to be a common interface for any 2D mapping types
where the top level is a dict.
\t
This example is meant to illustrate a lot of its functionality
""",
["Several objects can be used to create a Dict2D",None],
["No data creates an empty dict", "d = Dict2D()"],
[None, "print d"],
["A dict of dicts", "d = Dict2D(data={'a':{'a':1,'b':2},'b':{'a':3,'b':4}})"],
[None, "print d"],
["Indices data", "d = Dict2D(data=[('a','a',1),('a','b',2),('b','a',3),('b','b',4)])"],
[None, "print d"],
["List data, note you must also define a RowOrder and ColOrder",\
"d = Dict2D(data=[[1,2,3],[4,5,6]], RowOrder=['a','b'], ColOrder=['d','e','f'])"],
[None, "print d"],
["RowOrder and ColOrder are lists of the 'interesting' row keys and column keys",
"d = Dict2D(data={'a':{'c':5}}, RowOrder=['a','b'], ColOrder=['c','d'])"],
[None, "print d"],
["""If RowOrder and ColOrder are both passed in, along with setting Pad=True,
the Dict2D will be filled with the default value to conatin all rows and 
cols.""",
"d = Dict2D(data={'a':{'c':5}}, RowOrder=['a','b'], ColOrder=['c','d'], Pad=True)"],
[None, "print d"],
["""You can change the default value for Pad with self.Default """, 
"d = Dict2D(data={'a':{'c':5}}, RowOrder=['a','b'], ColOrder=['c','d'], Pad=True, Default=42)"],
[None, "print d"],
["""The only remaining constructor argument is RowConstructor, this allows 
you to optionally pass a different constructor (default==dict()) for the inner 
layer of the Dict2D. For example you could make all inner objects into 
cogent.base.stats.Freqs objects""",
"d = Dict2D(data={'a':{'a':1,'b':2}}, RowConstructor=Freqs)"],
[None, "print d"],
["Note the data type of d['a']", "print type(d['a'])"],

["""The pad() method can be called after initialization to achieve the same 
effect as passing Pad=True to the constructor. pad() optionally a default 
parameter, which by default is self.Default""", 
"d = Dict2D(data={'a':{'b':1}}, RowOrder=['a','b'], ColOrder=['a','b'])"],
[None, "print d"],
[None, "d.pad(default=42)"],
[None, "print d"],
["""If pad() is called and RowOrder and ColOrder haven't been set, it 
pads all rows to contain data for all existing column keys""",
"d = Dict2D(data={'a':{'c':1}, 'b':{'d':3}}, Default=42)"],
[None, "print d"],
[None, "d.pad()"],
[None, "print d"],
["""The purge() method is used to get rid of unwanted elements. Calling 
purge will remove any elements whose row or column key is not in RowOrder 
or ColOrder respectively""",
"d = Dict2D(data={'a':{'a':0,'b':1,'c':2}, 'b':{'b':5, 'c':9}, 'c':{'b':5}}, RowOrder=['a','b'], ColOrder=['a','b'])"],
[None, "print d"],
[None, "d.purge()"],
[None, "print d"],
["""The fill() method is similar to pad(), it takes parameters to list rows 
and cols, and fills them with val. By default, RowOrder and ColOrder are not 
touched, but can be overwritten by passing set_orders=True). All values 
optional except val""", 
"d.fill(val=42, rows=['c'],cols=['y','z'],set_orders=True)"],
[None, "print d"],
[None, "print d.RowOrder"],
[None, "print d.ColOrder"],
["""The square() method will fill a Dict2D with necessary values to make it 
square""", "d = Dict2D({'a':{'a':1, 'b':2}, 'b':{'a':0}})"],
[None, "print d"],
[None, "d.square()"],
[None, "print d"],
["""Optionally square() can fill in columns that exist in one row but not in
others by passinging reset_order=True""",
"d = Dict2D({'a':{'a':1, 'b':2}, 'b':{'c':0}})"],
[None, "print d"],
[None, "d.square(default=42, reset_order=True)"],
[None, "print d"],

["""There are several built-in operations for working on matrices:""",None],
["""Setting up a Dict2D for examples""",
"d = Dict2D({'a':{'a':1,'b':2,'c':3}, 'b':{'a':4, 'b':5, 'c':6}}, RowOrder=list('ab'), ColOrder=('abc'))"],
[None, 'print d'],
["""setDiag() allows you to set the diagonal to a certain value""",
"d.setDiag(val=99)"],
[None,"print d"],
["""scale() allows for the application of a function to all elements in the 
Dict2D""", """def add_one(x):
\treturn x + 1
d.scale(f=add_one)"""],
[None,"print d"],
["""transpose() swaps all self[r][c] -> self[c][r]""", "d.transpose()"],
[None,"print d"],
["""reflect() reflects items across the diagonal based on a function that is
passed in. Several are defined and available to use, or you may define your
own. In this example, largest is used, which sets self[r][c] and self[c][r]
to the larger value of the two. Reflect only works if 
RowOrder and ColOrder exist and are equal. Items that don't lie within the
scope of RowOrder and ColOrder will be ignored.""", "d.RowOrder=list('ab')"],
[None, "d.reflect(method=largest)"],
[None, "print d"],

["""All methods operate on the Dict2D object. If you wish to create a new 
object to work on leaving your original untouched you should use the copy() 
method which makes a deep copy of the Dict2D""", 
"d = Dict2D(data={'a':{'a':1, 'b':2}, 'b':{'a':5, 'b':6}})"],
[None, "c = d.copy()"],
[None, "c.setDiag(42)"],
[None, "print c"],
["...and the original remains untouched", "print d"],

["""A Dict2D can be converted to a list of lists based on specified RowOrder
and ColOrder. The list will be padded as called for in self.Pad, and will
raise an error on missing values if self.Pad=False. Headers describing the
row keys and col keys will be included if specified, but will not be by 
default""", 
"d = Dict2D(data={'a':{'a':1, 'b':2}, 'b':{'a':5, 'b':6}}, RowOrder=list('ab'), ColOrder=('ba'))"],
[None, "print d.toLists(headers=True)"],

["""There are several ways to learn about the keys present in the Dict2D 
object""",
"d = Dict2D(data={'a':{'a':1, 'b':2}, 'b':{'a':5, 'c':6}})"],
["Get the row keys", "print d.rowKeys()"],
["Get all existing column keys", "print d.colKeys()"],
["Get column keys that are shared between all rows", "print d.sharedColKeys()"],

["""Iterators exist for Rows, Cols, and Items. If Dict2D is sparse, an error will
be raised if self.Pad == False, otherwise self.Default will be returned for
missing elements.""",
"d = Dict2D(data={'a':{'a':1, 'b':2}, 'b':{'a':5, 'c':6}}, Pad=True)"],
[None, """for r in d.Rows:
\tprint r
"""],
[None,"""for c in d.Cols:
\tprint c
"""],
[None,"""for i in d.Items:
\tprint i
"""],

["""There are several ways to select for Rows, Cols, and Items based on how
they evaluate in an arbitrary boolean function. Setting up some functions and 
objects to analyze for example.""",
"""def is_zero(x):
\treturn x == 0.
"""],
[None,"""def sum_to_zero(l):
\tsum = 0
\tfor i in l:
\t\tsum += i
\treturn sum == 0.
"""],
[None,"""d = Dict2D({'a':{'a':1,'b':0,'c':-1},'b':{'a':0, 'b':3, 'c':42},'c':{'a':-1, 'b':9, 'c':-41}})"""],
["""Return indices of rows whose elements sum to zero""",
"print d.getRowIndices(f=sum_to_zero)"],
["""Return rows whose elements sum to zero""",
"print d.getRowsIf(f=sum_to_zero)"],
["""Return indices of columns whose elements sum to zero""",
"print d.getColIndices(f=sum_to_zero)"],
["""Return columns whose elements sum to zero""",
"print d.getColsIf(f=sum_to_zero)"],
["""Return indices of items which are zero.""",
"print d.getItemIndices(f=is_zero)"],
["""Return items which are zero (silly example, but you get the idea)""",
"print d.getItemsIf(f=is_zero)"],
["""You can also select specific rows, cols, or items, and create a NEW OBJECT
with that data, for example""",
"c = d.getRows(rows=['a','b'])"],
[None,"print c"],
["Note original remains the same", "print d"],
["... same thing exists for cols", "c = d.getCols(cols=['b','c'])"],
[None,"print c"],
["... and for items", "c = d.getItems(items=[('a','b'),('c','a')])"],
[None,"print c"],
["""Additionally all of these selections methods have a negate parameter, which if
passed in as True, returns data corresponding to a result of False when tested
against f, for example:""",
"print d.getRowIndices(f=sum_to_zero)"],
[None,"print d.getRowIndices(f=sum_to_zero, negate=True)"],
  
["""Dict2D objects also define a method to write them out in delimited form,
which is useful for storing data in a file which can later be read back into 
a Dict2D object. (You can additionally define Orders and turn headers off)""", 
"print d.toDelimited()"]
])
