#!/usr/bin/env python
#file cogent/base/location.py

"""Provides Range, Span, Point: classes for dealing with parts of sequences.

Status: Prototype

Owner: Rob Knight rob@spot.colorado.edu

Span is a region with a start, an end, and a direction. Range is an ordered
collection of Spans (note: Range does _not_ support the list interface, but
you can always access Range.Spans directly).

Implementation Notes

Span and Range behave much like Python's slices: a Span contains the element 
after its Start but does not contain the element after its End. It may help to 
think of the Span indices occurring _between_ the list elements:

    a b c d e
   | | | | | |
   0 1 2 3 4 5

...so that a Span whose Start is its End contains no elements (e.g. 2:2), and
a Span whose End is 2 more than its start contains 2 elements (e.g. 2:4 has c
and d), etc. Similarly, Span(0,2) does _not_ overlap Span(2,3), since the 
former contains a and b while the latter contains c.

A Point is a Span whose Start and End refer to the same object, i.e. the same
position in the sequence. A Point occurs between elements in the sequence,
and so does not contain any elements itself.

WARNING: this differs from the way e.g. NCBI handles sequence indices, where
the sequence is 1-based, a single index is treated as containing one element,
the point 3 contains exactly one element, 3, rather than no elements, and a 
range from 2:4 contains 2, 3 and 4, _not_ just 2 and 3.

Revision History

11/12/03 Rob Knight: Originally written for PyEvolve
12/27/03 Rob Knight: added Point as special case of Span
"""
from old_cogent.util.misc import FunctionWrapper, ClassChecker, ConstrainedList, iterable
from itertools import chain
from string import strip

class SpanI(object):
    """Abstract interface for Span and Range objects.
    
    Required properties: Start, End (must both be numbers)
    """
    def __contains__(self, other):
        """Returns True if other entirely contained in self."""
        raise NotImplementedError

    def overlaps(self, other):
        """Returns True if any positions in self are also in other."""
        raise NotImplementedError

    def reverse(self):
        """Reverses self."""
        raise NotImplementedError

    def __iter__(self):
        """Iterates over indices contained in self."""
        raise NotImplementedError

    def __str__(self):
        """Returns string representation of self."""
        return '(%s,%s)' % (self.Start, self.End)

    def __len__(self):
        """Returns length of self."""
        raise NotImplementedError

    def __cmp__(self):
        """Compares indices of self with indices of other."""
        raise NotImplementedError
    
    def startsBefore(self, other):
        """Returns True if self starts before other or other.Start."""
        try:
            return self.Start < other.Start
        except AttributeError:
            return self.Start < other

    def startsAfter(self, other):
        """Returns True if self starts after other or after other.Start."""
        try:
            return self.Start > other.Start
        except AttributeError:
            return self.Start > other

    def startsAt(self, other):
        """Returns True if self starts at the same place as other."""
        try:
            return self.Start == other.Start
        except AttributeError:
            return self.Start == other

    def startsInside(self, other):
        """Returns True if self's start in other or equal to other."""
        try:
            return self.Start in other
        except (AttributeError, TypeError):  #count other as empty span
            return False

    def endsBefore(self, other):
        """Returns True if self ends before other or other.End."""
        try:
            return self.End < other.End
        except AttributeError:
            return self.End < other

    def endsAfter(self, other):
        """Returns True if self ends after other or after other.End."""
        try:
            return self.End > other.End
        except AttributeError:
            return self.End > other

    def endsAt(self, other):
        """Returns True if self ends at the same place as other."""
        try:
            return self.End == other.End
        except AttributeError:
            return self.End == other

    def endsInside(self, other):
        """Returns True if self's end in other or equal to other."""
        try:
            return self.End in other
        except (AttributeError, TypeError):  #count other as empty span
            return False

class Span(SpanI):
    """Span object: start, end and direction of single span."""
    
    def __init__(self, Start, End=None, Reverse=False):
        """Returns a new Span object, with Start, End, and Reverse properties.

        If End is not supplied, it is set to Start + 1 (providing a 1-element
        range).
        Reverse defaults to False.
        """
        #special handling in case we were passed another Span
        if isinstance(Start, Span):
            self.Start, self.End, self.Reverse = Start.Start, Start.End, \
                Start.Reverse
        else:
            #reverse start and end so that start is always first
            if End is None:
                End = Start + 1
            elif Start > End:
                Start, End = End, Start
                
            self.Start = Start
            self.End = End
            self.Reverse = Reverse

    def __contains__(self, other):
        """Returns True if other completely contained in self.
        
        other must either be a number or have Start and End properties.
        """
        try:
            return other.Start >= self.Start and other.End <= self.End
        except AttributeError:
            #other is scalar: must be _less_ than self.End,
            #for the same reason that 3 is not in range(3).
            return other >= self.Start and other < self.End

    def overlaps(self, other):
        """Returns True if any positions in self are also in other."""
        #remember to subtract 1 from the Ends, since self.End isn't really
        #in self...
        try:
            return (self.Start in other) or (other.Start in self)
        except AttributeError:  #other was probably a number?
            return other in self

    def reverse(self):
        """Reverses self."""
        self.Reverse = not self.Reverse

    def __iter__(self):
        """Iterates over indices contained in self.
        
        NOTE: to make sure that the same items are contained whether going 
        through the range in forward or reverse, need to adjust the indices
        by 1 if going backwards.
        """
        if self.Reverse:
            return iter(xrange(self.End-1, self.Start-1, -1))
        else:
            return iter(xrange(self.Start, self.End, 1))

    def __str__(self):
        """Returns string representation of self."""
        return '(%s,%s,%s)' % (self.Start, self.End, bool(self.Reverse))

    def __len__(self):
        """Returns length of self."""
        return self.End - self.Start

    def __cmp__(self, other):
        """Compares indices of self with indices of other."""
        if hasattr(other, 'Start') and hasattr(other, 'End'):
            return cmp(self.Start, other.Start) or cmp(self.End, other.End) \
                or cmp(self.Reverse, other.Reverse)
        else:
            return object.__cmp__(self, other)

class SpansOnly(ConstrainedList):
    """List that converts elements to Spans on addition."""
    Mask = FunctionWrapper(Span)
    _constraint = ClassChecker(Span)

class Range(SpanI):
    """Complex object consisting of many spans."""
    
    def __init__(self, Spans=[]):
        """Returns a new Range object with data in Spans.
        """
        result = SpansOnly()
        #need to check if we got a single Span, since they define __iter__.
        if isinstance(Spans, Span):
            result.append(Spans)
        elif hasattr(Spans, 'Spans'):   #probably a single range object?
            result.extend(Spans.Spans)
        else:
            for s in iterable(Spans):
                if hasattr(s, 'Spans'):
                  result.extend(s.Spans)
                else:
                    result.append(s)
        self.Spans = result

    def __str__(self):
        """Returns string representation of self."""
        return '(%s)' % ','.join(map(str, self.Spans))

    def __len__(self):
        """Returns sum of span lengths.
        
        NOTE: if spans overlap, will count multiple times. Use reduce() to
        get rid of overlaps.
        """
        return sum(map(len, self.Spans))

    def __cmp__(self, other):
        """Compares spans of self with indices of other."""
        if hasattr(other, 'Spans'):
            return cmp(self.Spans, other.Spans)
        elif len(self.Spans) == 1 and hasattr(other, 'Start') and \
            hasattr(other, 'End'):
            return cmp(self.Spans[0].Start, other.Start) or \
                cmp(self.Spans[0].End, other.End)
        else:
            return object.__cmp__(self, other)

    def _get_start(self):
        """Finds earliest start of items in self.Spans."""
        return min([i.Start for i in self.Spans])
    Start = property(_get_start)

    def _get_end(self):
        """Finds latest end of items in self.Spans."""
        return max([i.End for i in self.Spans])
    End = property(_get_end)

    def _get_reverse(self):
        """Reverse is True if any piece is reversed."""
        for i in self.Spans:
            if i.Reverse:
                return True
        return False
    Reverse = property(_get_reverse)

    def reverse(self):
        """Reverses all spans in self."""
        for i in self.Spans:
            i.reverse()

    def __contains__(self, other):
        """Returns True if other completely contained in self.
        
        other must either be a number or have Start and End properties.
        """
        if hasattr(other, 'Spans'):
            for curr in other.Spans:
                found = False
                for i in self.Spans:
                    if curr in i:
                        found = True
                        break
                if not found:
                    return False
            return True
        else:
            for i in self.Spans:
                if other in i:
                    return True
            return False

    def overlaps(self, other):
        """Returns True if any positions in self are also in other."""
        if hasattr(other, 'Spans'):
            for i in self.Spans:
                for j in other.Spans:
                    if i.overlaps(j):
                        return True
        else:
            for i in self.Spans:
                if i.overlaps(other):
                    return True
        return False

    def overlapsExtent(self, other):
        """Returns True if any positions in self's extent also in other's."""
        if hasattr(other, 'Extent'):
            return self.Extent.overlaps(other.Extent)
        else:
            return self.Extent.overlaps(other)

    def sort(self):
        """Sorts the spans in self."""
        self.Spans.sort()

    def __iter__(self):
        """Iterates over indices contained in self."""
        return chain(*[iter(i) for i in self.Spans])

    def _get_extent(self):
        """Returns Span object representing the extent of self."""
        return Span(self.Start, self.End)
    Extent = property(_get_extent)

    def simplify(self):
        """Reduces the spans in self in-place to get fewest spans.

        Will not condense spans with opposite directions.

        Will condense adjacent but nonoverlapping spans (e.g. (1,3) and (4,5)).
        """
        forward = []
        reverse = []
        spans = self.Spans[:]
        spans.sort()
        for span in spans:
            if span.Reverse:
                direction = reverse
            else:
                direction = forward
                
            found_overlap = False
            for other in direction:
                if span.overlaps(other) or (span.Start == other.End) or \
                    (other.Start == span.End):  #handle adjacent spans also
                    other.Start = min(span.Start, other.Start)
                    other.End = max(span.End, other.End)
                    found_overlap = True
                    break
            if not found_overlap:
                direction.append(span)
        self.Spans[:] = forward + reverse

class Point(Span):
    """Point is a special case of Span, where Start always equals End.
    
    Note that, as per Python standard, a point is _between_ two elements
    in a sequence. In other words, a point does not contain any elements.
    If you want a single element, use a Span where End = Start + 1.

    A Point does have a direction (i.e. a Reverse property) to indicate
    where successive items would go if it were expanded.
    """

    def __init__(self, Start, Reverse=False):
        """Returns new Point object."""
        self.Reverse = Reverse
        self._start = Start
    
    def _get_start(self):
        """Returns self.Start."""
        return self._start

    def _set_start(self, Start):
        """Sets self.Start and self.End."""
        self._start = Start
        
    Start = property(_get_start, _set_start)
    End = Start     #start and end are synonyms for the same property

def RangeFromString(string, delimiter=','):
    """Returns Range object from string of the form 1-5,11,20,30-50.

    Ignores whitespace; expects values to be comma-delimited and positive.
    """
    result = Range()
    pairs = map(strip, string.split(delimiter))
    for p in pairs:
        if not p:   #adjacent delimiters?
            continue
        if '-' in p:    #treat as pair
            first, second = p.split('-')
            result.Spans.append(Span(int(first), int(second)))
        else:
            result.Spans.append(Span(int(p)))
    return result
            
