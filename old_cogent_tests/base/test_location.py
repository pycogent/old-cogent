#!/usr/bin/env python
#file evo/test_span.py

"""Unit tests for Range and Span classes.

Revision History

11/12/03 Rob Knight: initially written for PyEvolve.
12/27/03 Rob Knight: added Point.
"""
from old_cogent.util.unit_test import TestCase, main
from old_cogent.base.location import Range, Span, Point, SpansOnly, RangeFromString

class SpanTests(TestCase):
    """Tests of the Span object."""
    def setUp(self):
        """Define some standard Spans"""
        self.empty = Span(0, 0)
        self.full = Span(35, 30)    #will convert to (30, 35) internally
        self.overlapping = Span(32, 36)
        self.inside = Span(31, 32)
        self.before = Span(25, 30)
        self.after = Span(35, 40)
        self.reverse = Span(30, 35, True)
        self.spans_zero = Span(-5, 5)
        
    def test_init(self):
        """Span object should init with Start, End, and Length"""
        s = Span(0)
        self.assertEqual(s.Start, 0)
        self.assertEqual(s.End, 1)
        self.assertEqual(s.Reverse, False)
        #to get an empty interval, must specify start and end explicitly
        t = Span(0, 0)
        self.assertEqual(t.Start, 0)
        self.assertEqual(t.End, 0)
        self.assertEqual(t.Reverse, False)
        #should be able to specify direction also
        u = Span(5, 15, True)
        self.assertEqual(u.Start, 5)
        self.assertEqual(u.End, 15)
        self.assertEqual(u.Reverse, True)
        #should be able to init from another span
        v = Span(u)
        self.assertEqual(v.Start, 5)
        self.assertEqual(v.End, 15)
        self.assertEqual(v.Reverse, True)

    def test_contains(self):
        """Span object contains its start but not its end"""
        assert not 0 in self.empty
        assert 30 in self.full
        assert 34 in self.full
        assert 35 not in self.full
        assert self.inside in self.full
        assert self.overlapping not in self.full
        assert 0 in self.spans_zero
        assert -5 in self.spans_zero
        assert 5 not in self.spans_zero

    def test_overlaps(self):
        """Span objects should be able to overlap points or spans"""
        assert self.full.overlaps(self.overlapping)
        assert not self.full.overlaps(self.before)
        assert not self.before.overlaps(self.overlapping)
        assert not self.full.overlaps(self.after)
        assert not self.after.overlaps(self.before)
        assert self.full.overlaps(self.inside)
        assert self.spans_zero.overlaps(self.empty)
        assert self.empty.overlaps(self.spans_zero)

    def test_reverse(self):
        """Span reverse should change direction"""
        assert not self.empty.Reverse
        self.empty.reverse()
        assert self.empty.Reverse
        self.empty.reverse()
        assert not self.empty.Reverse
        assert self.reverse.Reverse
        self.reverse.reverse()
        assert not self.reverse.Reverse

    def test_iter(self):
        """Span iter should loop through (integer) contents"""
        self.assertEqual(list(iter(self.empty)), [])
        self.assertEqual(list(iter(self.full)), [30,31,32,33,34])
        self.assertEqual(list(iter(self.spans_zero)),[-5,-4,-3,-2,-1,0,1,2,3,4])
        self.assertEqual(list(iter(self.inside)), [31])
        self.assertEqual(list(self.reverse), [34,33,32,31,30])

    def test_str(self):
        """Span str should print start, stop, reverse"""
        self.assertEqual(str(self.empty), '(0,0,False)')
        self.assertEqual(str(self.full), '(30,35,False)')
        self.assertEqual(str(self.reverse), '(30,35,True)')

    def test_len(self):
        """Span len should return difference between start and end"""
        self.assertEqual(len(self.empty), 0)
        self.assertEqual(len(self.full), 5)
        self.assertEqual(len(self.inside),1)
        self.assertEqual(len(self.spans_zero), 10)

    def test_cmp(self):
        """Span cmp should support sort by 1st/2nd index and direction"""
        s, e, f, r, i, o = self.spans_zero, self.empty, self.full, \
            self.reverse, self.inside, self.overlapping

        n = Span(30, 36)

        expected_order = [s, e, f, r, n, i, o]
        first = expected_order[:]
        first.sort()
        second = [r, o, f, s, e, i, n]
        second.sort()
        for i, j in zip(first, second):
            assert i is j

        for i, j in zip(first, expected_order):
            assert i is j

    def test_startsBefore(self):
        """Span startsBefore should match hand-calculated results"""
        e, f = self.empty, self.full
        assert e.startsBefore(f)
        assert not f.startsBefore(e)
        assert e.startsBefore(1)
        assert e.startsBefore(1000)
        assert not e.startsBefore(0)
        assert not e.startsBefore(-1)
        assert not f.startsBefore(30)
        assert f.startsBefore(31)
        assert f.startsBefore(1000)
        
    def test_startsAfter(self):
        """Span startsAfter should match hand-calculated results"""
        e, f = self.empty, self.full
        assert not e.startsAfter(f)
        assert f.startsAfter(e)
        assert not e.startsAfter(1)
        assert not e.startsAfter(1000)
        assert not e.startsAfter(0)
        assert e.startsAfter(-1)
        assert f.startsAfter(29)
        assert not f.startsAfter(30)
        assert not f.startsAfter(31)
        assert not f.startsAfter(1000)

    def test_startsAt(self):
        """Span startsAt should return True if input matches"""
        e, f = self.empty, self.full
        s = Span(30, 1000)
        assert e.startsAt(0)
        assert f.startsAt(30)
        assert s.startsAt(30)
        assert f.startsAt(s)
        assert s.startsAt(f)
        assert not e.startsAt(f)
        assert not e.startsAt(-1)
        assert not e.startsAt(1)
        assert not f.startsAt(29)

    def test_startsInside(self):
        """Span startsInside should return True if input starts inside span"""
        e, f, i, o = self.empty, self.full, self.inside, self.overlapping
        assert not e.startsInside(0)
        assert not f.startsInside(30)
        assert not e.startsInside(f)
        assert i.startsInside(f)
        assert not f.startsInside(i)
        assert o.startsInside(f)
        assert not o.endsInside(i)
        
    def test_endsBefore(self):
        """Span endsBefore should match hand-calculated results"""
        e, f = self.empty, self.full
        assert e.endsBefore(f)
        assert not f.endsBefore(e)
        assert e.endsBefore(1)
        assert e.endsBefore(1000)
        assert not e.endsBefore(0)
        assert not e.endsBefore(-1)
        assert not f.endsBefore(30)
        assert not f.endsBefore(31)
        assert f.endsBefore(1000)
        
    def test_endsAfter(self):
        """Span endsAfter should match hand-calculated results"""
        e, f = self.empty, self.full
        assert not e.endsAfter(f)
        assert f.endsAfter(e)
        assert not e.endsAfter(1)
        assert not e.endsAfter(1000)
        assert not e.endsAfter(0)
        assert e.endsAfter(-1)
        assert f.endsAfter(29)
        assert f.endsAfter(30)
        assert f.endsAfter(34)
        assert not f.endsAfter(35)
        assert not f.endsAfter(1000)

    def test_endsAt(self):
        """Span endsAt should return True if input matches"""
        e, f = self.empty, self.full
        s = Span(30, 1000)
        t = Span(-100, 35)
        assert e.endsAt(0)
        assert f.endsAt(35)
        assert s.endsAt(1000)
        assert not f.endsAt(s)
        assert not s.endsAt(f)
        assert f.endsAt(t)
        assert t.endsAt(f)

    def test_endsInside(self):
        """Span endsInside should return True if input ends inside span"""
        e, f, i, o = self.empty, self.full, self.inside, self.overlapping
        assert not e.endsInside(0)
        assert not f.endsInside(30)
        assert not f.endsInside(34)
        assert not f.endsInside(35)
        assert not e.endsInside(f)
        assert i.endsInside(f)
        assert not f.endsInside(i)
        assert not o.endsInside(f)
        assert not o.endsInside(i)
        assert e.endsInside(Span(-1,1))
        assert e.endsInside(Span(0,1))
        assert not e.endsInside(Span(-1,0))

class SpansOnlyTests(TestCase):
    """Check that SpansOnly does correct conversions."""
    def test_init(self):
        """SpansOnly should init with specified items"""
        s = SpansOnly([3, 4])
        self.assertEqual(s, [Span(3,4), Span(4,5)])
        s = SpansOnly([6, Span(50,60,True)])
        self.assertEqual(s, [Span(6,7), Span(50,60,True)])

class RangeInterfaceTests(SpanTests):
    """A single-element Range should behave like the corresponding Span."""
    def setUp(self):
        """Define some standard Spans"""
        self.empty = Range(Span(0, 0))
        self.full = Range(Span(30, 35))
        self.overlapping = Range(Span(32, 36))
        self.inside = Range(Span(31, 32))
        self.before = Range(Span(25, 30))
        self.after = Range(Span(35, 40))
        self.reverse = Range(Span(30, 35, True))
        self.spans_zero = Range(Span(-5, 5))

    def test_str(self):
        """Range str should print start, stop, reverse for each Span"""
        #note that the Range adds an extra level of parens, since it can
        #contain more than one Span.
        self.assertEqual(str(self.empty), '((0,0,False))')
        self.assertEqual(str(self.full), '((30,35,False))')
        self.assertEqual(str(self.reverse), '((30,35,True))')

 
class RangeTests(TestCase):
    """Tests of the Range object."""
    def setUp(self):
        """Set up a few standard ranges."""
        self.one = Range(Span(0,100))
        self.two = Range([Span(3,5), Span(8, 11)])
        self.three = Range([Span(6,7), Span(15, 17), Span(30, 35)])
        self.overlapping = Range([Span(6, 10), Span(7,3)])
        self.single = Range(0)
        self.singles = Range([3, 11])
        self.twocopy = Range(self.two)
        self.twothree = Range([self.two, self.three])
        self.empty = Range([Span(6,6), Span(8,8)])

    def test_init(self):
        """Range init from Spans, numbers, or Ranges should work OK."""
        #single span
        self.assertEqual(self.one, Span(0,100))
        #list of spans
        self.assertEqual(self.two.Spans, [Span(3,5), Span(8,11)])
        #another range
        self.assertEqual(self.two, self.twocopy)
        #list of ranges
        self.assertEqual(self.twothree.Spans, [Span(3,5), Span(8,11),
            Span(6,7), Span(15,17), Span(30,35)])
        #list of numbers
        self.assertEqual(self.singles.Spans, [Span(3,4), Span(11,12)])
        #single number
        self.assertEqual(self.single.Spans, [Span(0,1)])
        #nothing
        self.assertEqual(Range().Spans, [])
        
    def test_str(self):
        """Range str should print nested with parens"""
        self.assertEqual(str(self.one), '((0,100,False))')
        self.assertEqual(str(self.twothree), 
'((3,5,False),(8,11,False),(6,7,False),(15,17,False),(30,35,False))')
        self.assertEqual(str(self.single), '((0,1,False))')

    def test_len(self):
        """Range len should sum span lengths"""
        self.assertEqual(len(self.one), 100)
        self.assertEqual(len(self.single), 1)
        self.assertEqual(len(self.empty), 0)
        self.assertEqual(len(self.three), 8)

    def test_cmp(self):
        """Ranges should compare equal if they have the same spans"""
        self.assertEqual(self.twothree, Range([Span(3,5), Span(8, 11),
            Span(6,7), Span(15, 17), Span(30, 35)]))
        self.assertEqual(Range(), Range())

    def test_start_end(self):
        """Range Start and End should behave as expected"""
        self.assertEqual(self.one.Start, 0)
        self.assertEqual(self.one.End, 100)
        self.assertEqual(self.overlapping.Start, 3)
        self.assertEqual(self.overlapping.End, 10)
        self.assertEqual(self.three.Start, 6)
        self.assertEqual(self.three.End, 35)

    def test_reverse(self):
        """Range reverse method should reverse each span"""
        for s in self.overlapping.Spans:
            assert not s.Reverse
        self.overlapping.reverse()
        for s in self.overlapping.Spans:
            assert s.Reverse
        self.overlapping.Spans.append(Span(0, 100))
        self.overlapping.reverse()
        for s in self.overlapping.Spans[0:1]:
            assert not s.Reverse
        assert self.overlapping.Spans[-1].Reverse

    def test_Reverse(self):
        """Range Reverse property should return True if any span reversed"""
        assert not self.one.Reverse
        self.one.reverse()
        assert self.one.Reverse
        assert not self.two.Reverse
        self.two.Spans.append(Span(0,100,True))
        assert self.two.Reverse
        self.two.reverse()
        assert self.two.Reverse

    def test_contains(self):
        """Range contains an item if any span contains it"""
        assert 50 in self.one
        assert 0 in self.one
        assert 99 in self.one
        assert 100 not in self.one
        assert 6 in self.three
        assert 7 not in self.three
        assert 8 not in self.three
        assert 14 not in self.three
        assert 15 in self.three
        assert 29 not in self.three
        assert 30 in self.three
        assert 34 in self.three
        assert 35 not in self.three
        assert 40 not in self.three
        #should work if a span is added
        self.three.Spans.append(40)
        assert 40 in self.three
        #should work for spans
        assert Span(31, 33) in self.three
        assert Span(31, 37) not in self.three
        #span contains itself
        assert self.twocopy in self.two
        #should work for ranges
        assert Range([6, Span(15,16), Span(30,33)]) in self.three
        #should work for copy, except when extra piece added
        threecopy = Range(self.three)
        assert threecopy in self.three
        threecopy.Spans.append(1000)
        assert threecopy not in self.three
        self.three.Spans.append(Span(950, 1050))
        assert threecopy in self.three
        assert self.three not in threecopy

    def test_overlaps(self):
        """Range overlaps should return true if any component overlapping"""
        assert self.two.overlaps(self.one)
        assert self.one.overlaps(self.two)
        assert self.three.overlaps(self.one)
        #two and three are interleaved but not overlapping
        assert not self.two.overlaps(self.three)
        assert not self.three.overlaps(self.two)
        assert self.one.overlaps(self.empty)
        assert self.empty.overlaps(self.one)
        assert self.singles.overlaps(self.two)

    def test_overlapsExtent(self):
        """Range overlapsExtent should return true for interleaved ranges"""
        assert self.two.overlapsExtent(self.three)
        assert self.three.overlapsExtent(self.two)
        assert not self.single.overlapsExtent(self.two)
        assert not self.single.overlapsExtent(self.three)
        assert self.one.overlapsExtent(self.three)

    def test_sort(self):
        """Range sort should sort component spans"""
        one = self.one
        one.sort()
        self.assertEqual(one.Spans, [Span(100,0)])
        one.Spans.append(Span(-20,-10))
        self.assertEqual(one.Spans, [Span(0,100),Span(-20,-10)])
        one.sort()
        self.assertEqual(one.Spans, [Span(-20,-10),Span(0,100)])
        one.Spans.append(Span(-20, -10, True))
        self.assertEqual(one.Spans, [Span(-20,-10),Span(0,100), 
            Span(-20,-10,True)])
        one.sort()
        self.assertEqual(one.Spans, [Span(-20,-10),Span(-20,-10,True), 
            Span(0,100)])

    def test_iter(self):
        """Range iter should iterate through each span in turn"""
        self.assertEqual(list(iter(self.two)), [3,4,8,9,10])
        self.two.Spans.insert(1, Span(103, 101, True))
        self.assertEqual(list(iter(self.two)), [3,4,102,101,8,9,10])

    def test_Extent(self):
        """Range extent should span limits of range"""
        self.assertEqual(self.one.Extent, Span(0,100))
        self.assertEqual(self.three.Extent, Span(6,35))
        self.assertEqual(self.singles.Extent, Span(3, 12))
        self.assertEqual(self.single.Extent, Span(0,1))
        self.three.Spans.append(Span(100, 105, True))
        self.assertEqual(self.three.Extent, Span(6,105))
        self.three.Spans.append(Span(-100, -1000))
        self.assertEqual(self.three.Extent, Span(-1000,105))

    def test_simplify(self):
        """Range reduce should group overlapping ranges"""
        #consolidate should have no effect when no overlap
        r = self.two
        r.simplify()
        self.assertEqual(r.Spans, [Span(3,5), Span(8,11)])
        #should consolidate an overlap of the same direction
        r.Spans.append(Span(-1, 4))
        r.simplify()
        self.assertEqual(r.Spans, [Span(-1,5), Span(8,11)])
        #should also consolidate _adjacent_ spans of the same direction
        r.Spans.append(Span(11,14))
        r.simplify()
        self.assertEqual(r.Spans, [Span(-1,5), Span(8,14)])
        #bridge should cause consolidations
        s = Range(r)
        s.Spans.append(Span(5,8))
        s.simplify()
        self.assertEqual(s.Spans, [Span(-1,14)])
        #ditto for bridge that overlaps everything
        s = Range(r)
        s.Spans.append(Span(-100, 100))
        s.simplify()
        self.assertEqual(s.Spans, [Span(-100,100)])
        #however, can't consolidate span in other orientation
        s = Range(r)
        s.Spans.append(Span(-100, 100, True))
        self.assertEqual(s.Spans, [Span(-1,5), Span(8,14), Span(-100,100,True)])

class PointTests(TestCase):
    """Tests of the Point class."""
    def test_init(self):
        """Point should require a Start, and should accept a Reverse"""
        self.assertRaises(TypeError, Point)
        p = Point(0)
        self.assertEqual(p.Start, 0)
        self.assertEqual(p.End, 0)
        self.assertEqual(p.Reverse, False)
        q = Point(-5, True)
        self.assertEqual(q.Start, -5)
        self.assertEqual(q.End, -5)
        self.assertEqual(q.Reverse, True)

    def test_equality(self):
        """Two Points should test equal if they occur at the same location"""
        p = Point(0)
        q = Point(0)
        r = Point(1)
        self.assertEqual(p, q)
        self.assertNotEqual(p, r)

    def test_overlap(self):
        """A Point should overlap a Span that contains it, and vice versa"""
        p = Point(5)
        s = Span(4, 6)
        assert p.overlaps(s)
        assert s.overlaps(p)

    def test_change(self):
        """Changing a Point's Start should affect its End, and vice versa"""
        p = Point(5)
        self.assertEqual(p.End, 5)
        self.assertEqual(p.Start, 5)
        p.End = 3
        self.assertEqual(p.End, 3)
        self.assertEqual(p.Start, 3)
        p.Start = 7
        self.assertEqual(p.End, 7)
        self.assertEqual(p.Start, 7)

class RangeFromStringTests(TestCase):
    """Tests of the RangeFromString factory function."""
    def test_init(self):
        self.assertEqual(RangeFromString(''), Range())
        self.assertEqual(RangeFromString('  3  , 4\t, ,, 10  ,'), 
            Range([3,4,10]))
        self.assertEqual(RangeFromString('3,4-10,1-5'), 
            Range([Span(3), Span(4,10), Span(1,5)]))

#run the following if invoked from command-line
if __name__ == "__main__":
    main()


