#!/usr/bin/env python
#file evo/unit_test.py
"""Extension of the built-in unittest framework for floating-point comparisons.

Owner: Rob Knight rob@spot.colorado.edu

Status: Stable

Specific Extensions

assertFloatEqual, assertFloatEqualAbs, and assertFloatEqualRel give fine-
grained control over how floating point numbers (or lists thereof) are tested 
for equality. assertContains and assertNotContains give more helpful error 
messages when testing whether an observed item is present or absent in a set 
of possiblities. assertSameItems and assertEqualItems test the items in a list 
for pairwise identity and equality respectively (i.e. the observed and 
expected values must have the same number of each item, though the order can 
differ); assertNotEqualItems verifies that two lists do not contain the same
set of items.

Revision History

2/13/03 Rob Knight: first written

4/22-24/03 Rob Knight: changed assertFloatEqual, reinforced distinction 
between expected and observed in interface and error messages.

4/29/03 Rob Knight: docstrings now meet guidelines.

5/8/03 Rob Knight: minor changes to docstrings.

8/4/03 Rob Knight: changed name of module.

8/10/03 Rob Knight: added support for None and other non-numeric items in lists
compared by the assertFloatEqual methods.

9/17/03 Rob Knight: changed module name to unittest. Added self.assertSameItems,
self.assertEqualItems, self.assertContains, self.assertNotContains.

10/29/03 Rob Knight: changed module name to unit_test. Changed 
self.assertSameItems to use more robust algorithm that is stable against
objects that compare equal or are incomparable.

10/21/04 Rob Knight: changed self.failUnlessEqual to use not(==) instead of
!= to preserve same behavior as built-in unittest module.

10/28/04 Rob Knight: tests for equality and inequality now work on arrays as
well (including nested arrays).

2/9/05 Rob Knight: added FakeRandom class for testing functions that require
random numbers.

1/13/06 Sandra Smit: changed _is_equal to handle all array cases (especially
empty arrays).

4/9/2006 Micah Hamady: changed maxint so xrange works on x86_64
"""
from unittest import main, TestCase as orig_TestCase, TestSuite
from sys import maxint
indices = xrange(1000000)
#indices = xrange(maxint)
from old_cogent.util.misc import recursive_flatten

class FakeRandom(object):
    """Drop-in substitute for random.random that provides items from list."""
    
    def __init__(self, data, circular=False):
        """Returns new FakeRandom object, using list of items in data.

        circular: if True (default is False), wraps the list around. Otherwise,
        raises IndexError when we run off the end of the list.
        
        WARNING: data must always be iterable, even if it's a single item.
        """
        self._data = data
        self._ptr = -1
        self._circular = circular

    def __call__(self, *args, **kwargs):
        """Returns next item from the list in self._data.
        
        Raises IndexError when we run out of data.
        """
        self._ptr += 1
        #wrap around if circular
        if self._circular:
            if self._ptr >= len(self._data):
                self._ptr = 0
        return self._data[self._ptr]

class TestCase(orig_TestCase):
    """Adds some additional utility methods to unittest.TestCase.

    Notably, adds facilities for dealing with floating point numbers,
    and some common templates for replicated tests.

    BEWARE: Do not start any method with 'test' unless you want it to actually
    run as a test suite in every instance!
    """

    def errorCheck(self, call, known_errors):
        """Applies function to (data, error) tuples, checking for error
        """
        for (data, error) in known_errors:
            self.assertRaises(error, call, data)

    def valueCheck(self, call, known_values, arg_prefix='', eps=None):
        """Applies function to (data, expected) tuples, treating data as args
        """
        for (data, expected) in known_values:
                observed = eval('call(' + arg_prefix + 'data)')
                try:
                    allowed_diff = float(eps)
                except TypeError:
                    self.assertEqual(observed, expected)
                else:
                    self.assertFloatEqual(observed, expected, allowed_diff)

    def assertFloatEqualRel(self, obs, exp, eps=1e-6):
        """Tests whether two floating point numbers are approximately equal.

        Checks whether the distance is within epsilon relative to the value
        of the sum of observed and expected. Use this method when you expect
        the difference to be small relative to the magnitudes of the observed
        and expected values.
        """
        try:
            iter(obs)
            iter(exp)
        except TypeError:
            obs = [obs]
            exp = [exp]

        for observed, expected in zip(obs, exp):
            #try the cheap comparison first
            if observed == expected:
                continue
            try:
                sum = float(observed + expected)
                diff = float(observed - expected)
                if (sum == 0):
                    self.failIf(abs(diff) > abs(eps), \
                        "Got %s, but expected %s (diff was %s)" % \
                        (`observed`, `expected`, `diff`))
                else:
                    self.failIf(abs(diff/sum) > abs(eps), \
                        "Got %s, but expected %s (diff was %s)" % \
                        (`observed`, `expected`, `diff`))
            except (TypeError, ValueError, AttributeError, NotImplementedError):
                self.fail("Got %s, but expected %s" % \
                    (`observed`, `expected`))
    
    def assertFloatEqualAbs(self, obs, exp, eps=1e-6):
        """
        Tests whether two floating point numbers are approximately equal.

        Checks whether the absolute value of (a - b) is within epsilon. Use
        this method when you expect that one of the values should be very
        small, and the other should be zero.
        """
        try:
            iter(obs)
            iter(exp)
        except TypeError:
            obs = [obs]
            exp = [exp]

        for observed, expected in zip(obs, exp):
            #cheap comparison first
            if observed == expected:
                continue
            try:
                diff = observed - expected
                self.failIf(abs(diff) > abs(eps),
                        "Got %s, but expected %s (diff was %s)" % \
                        (`observed`, `expected`, `diff`))
            except (TypeError, ValueError, AttributeError, NotImplementedError):
                self.fail("Got %s, but expected %s" % \
                    (`observed`, `expected`))
    
    def assertFloatEqual(self, obs, exp, eps=1e-6, rel_eps=None, \
                         abs_eps=None):
        """Tests whether two floating point numbers are approximately equal.

        If one of the arguments is zero, tests the absolute magnitude of the
        difference; otherwise, tests the relative magnitude.

        Use this method as a reasonable default.
        """
        try:
            iter(obs)
            iter(exp)
        except TypeError:
            obs = [obs]
            exp = [exp]

        for observed, expected in zip(obs, exp):
            if self._is_equal(observed, expected):
                continue
            try:
                rel_eps = rel_eps or eps
                abs_eps = abs_eps or eps
                if (observed == 0) or (expected == 0):
                    self.assertFloatEqualAbs(observed, expected, abs_eps)
                else:
                    self.assertFloatEqualRel(observed, expected, rel_eps)
            except (TypeError, ValueError, AttributeError, NotImplementedError):
                self.fail("Got %s, but expected %s" % \
                        (`observed`, `expected`))
                                    
    def _is_equal(self, observed, expected):
        """Returns True if observed and expected are equal, False otherwise."""
        result = observed == expected
        
        if result is True or result is False:
            return result
        
        else: #dealing with sequences
            try:
                observed = observed.tolist()
            except AttributeError:
                pass
            try:
                expected = expected.tolist()
            except AttributeError:
                pass
            return observed == expected

    def failUnlessEqual(self, observed, expected, msg=None):
        """Fail if the two objects are unequal as determined by !=

        Overridden to make error message enforce order of observed, expected.
        """
        if not self._is_equal(observed, expected):
            raise self.failureException, \
            (msg or 'Got %s, but expected %s' % (`observed`, `expected`))

    def failIfEqual(self, observed, expected, msg=None):
        """Fail if the two objects are equal as determined by =="""
        if self._is_equal(observed, expected):
            raise self.failureException, \
            (msg or 'Observed %s and expected %s: shouldn\'t test equal'\
                % (`observed`, `expected`))
        
        #following needed to get our version instead of unittest's
    assertEqual = assertEquals = failUnlessEqual

    assertNotEqual = assertNotEquals = failIfEqual

    def assertEqualItems(self, observed, expected, msg=None):
        """Fail if the two items contain unequal elements"""
        obs_items = list(observed)
        exp_items = list(expected)
        if len(obs_items) != len(exp_items):
            raise self.failureException, \
            (msg or 'Observed and expected are different lengths: %s and %s' \
            % (len(obs_items), len(exp_items)))
            
        obs_items.sort()
        exp_items.sort()
        for obs, exp, index in zip(obs_items, exp_items, indices):
            if obs != exp:
                raise self.failureException, \
                (msg or 'Observed %s and expected %s at sorted index %s' \
                % (obs, exp, index))

    def assertSameItems(self, observed, expected, msg=None):
        """Fail if the two items contain non-identical elements"""
        obs_items = list(observed)
        exp_items = list(expected)
        if len(obs_items) != len(exp_items):
            raise self.failureException, \
            (msg or 'Observed and expected are different lengths: %s and %s' \
            % (len(obs_items), len(exp_items)))

        obs_ids = [(id(i), i) for i in obs_items]
        exp_ids = [(id(i), i) for i in exp_items]
        obs_ids.sort()
        exp_ids.sort()
        for obs, exp, index in zip(obs_ids, exp_ids, indices):
            o_id, o = obs
            e_id, e = exp
            if o_id != e_id:    #i.e. the ids are different
                raise self.failureException, \
                (msg or \
                'Observed %s <%s> and expected %s <%s> at sorted index %s' \
                % (o, o_id, e, e_id, index))

    def assertNotEqualItems(self, observed, expected, msg=None):
        """Fail if the two items contain only equal elements when sorted"""
        try:
            self.assertEqualItems(observed, expected, msg)
        except:
            pass
        else:
            raise self.failureException, \
            (msg or 'Observed %s has same items as %s'%(`observed`, `expected`))

    def assertContains(self, observed, item, msg=None):
        """Fail if item not in observed"""
        try:
            if item in observed:
                return
        except (TypeError, ValueError):
            pass
        raise self.failureException, \
        (msg or 'Item %s not found in %s' % (`item`, `observed`))

    def assertNotContains(self, observed, item, msg=None):
        """Fail if item in observed"""
        try:
            if item not in observed:
                return
        except (TypeError, ValueError):
            return
        raise self.failureException, \
        (msg or 'Item %s should not have been in %s' % (`item`, `observed`))

