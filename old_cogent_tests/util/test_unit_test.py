#!/usr/bin/env python
#file evo/test_unit_test.py
"""Tests for cogent.util.unit_test, an extension of the built-in PyUnit framework.

Owner: Rob Knight rob@spot.colorado.edu

Revision History

4/23/03 Rob Knight: initially written. Had to find out how to extract error 
message from sys.exc_info for testing.

4/29/03 Rob Knight: docstrings now meet guidelines.

8/4/03 Rob Knight: changed module names.

8/10/03 Rob Knight: added test for None in lists passed to assertFloatEqual.

9/17/03 Rob Knight: renamed file; added tests for assertSameItems, 
assertEqualItems, assertContains, assertNotContains.

5/2/04 Rob Knight: removed the dependency on the order in which ids are assigned
from assertSameItems (MacOSX doesn't assign the ids monotonically, although
Linux does). This change only affects the tests, not the code.

6/8/04 Rob Knight: further relaxed the assertSameItems test to account for
platform differences. Now checks that the error is raised, but doesn't check
the specific string it returns.

10/28/04 Rob Knight: added array tests. Note: now depends on installation of
Numeric, but that's OK because so does the rest of Cogent...

2/9/05 Rob Knight: added test for FakeRandom.

1/13/05 Sandra Smit: added some more tests for array data.
"""
from old_cogent.util.unit_test import TestCase, main, FakeRandom
from Numeric import array, zeros
from sys import exc_info

class FakeRandomTests(TestCase):
    """Tests FakeRandom class."""
    
    def test_call_constant(self):
        """FakeRandom __call__ should return next item from list if constant"""
        const = FakeRandom([1])
        self.assertEqual(const(), 1)
        self.assertRaises(IndexError, const)

    def test_call_constant_wrap(self):
        """FakeRandom __call__ should wrap for one-item list if specified"""
        const = FakeRandom([1], True)
        for i in range(10):
            self.assertEqual(const(), True)

    def test_call_var(self):
        """FakeRandom __call__ should work with a multi-item list"""
        f = FakeRandom([1,2,3])
        self.assertEqual(f(), 1)
        self.assertEqual(f(), 2)
        self.assertEqual(f(), 3)
        self.assertRaises(IndexError, f)

    def test_call_var_wrap(self):
        """FakeRandom __call__ should work with a multi-item wrapped list"""
        f = FakeRandom([1,2,3], True)
        result = [f() for i in range(10)]
        self.assertEqual(result, [1,2,3,1,2,3,1,2,3,1])

    def test_cal_var_args(self):
        """FakeRandom __call__ should ignore extra args"""
        f = FakeRandom([[1,2,3]], True)
        for i in range(5):
            result = f((5,5))    #shape parameter ignored
            self.assertEqual(result, [1,2,3])

class TestCaseTests(TestCase):
    """Tests for extension of the built-in unittest framework.

    For each test, includes an example of success and failure.
    """
    unequal_pairs = [
                    (1, 0),
                    ([], ()),
                    (None, 0),
                    ('', ' '),
                    (1, '1'),
                    (0, '0'),
                    ('', None),
                    (array([1,2,3]),array([1,2,4])),
                    (array([[1,2],[3,4]]), array([[1.0,2.0],[3.0,4.1]])),
                    (array([1]), array([1,2])),
                    (zeros(0), array([1])),
                    (array([1,1,1]), array([1])),
                    (array([[1,1],[1,1]]), array([1,1,1,1])),
                    (zeros(0), None),
                    (zeros(3), zeros(5)),
                    (zeros(0), ''),
                ]

    equal_pairs = [
                (1, 1),
                (0, 0),
                (5, 5L),
                (5, 5.0),
                (0, 0.0),
                ('', ''),
                (' ', ' '),
                ('a', 'a'),
                (None, None),
                ([0, 1], [0.0, 1.0]),
                (array([1,2,3]), array([1,2,3])),
                (array([[1,2],[3,4]]), array([[1.0,2.0],[3.0,4.0]])),
                (zeros(0), []),
                (zeros(0), zeros(0)),
                (array([]), zeros(0)),
                (zeros(3), zeros(3)),
                (array([0,0,0]), zeros(3)),
                (array([]), []), 
            ]

    small = 1e-7
    big = 1e-5
    
    within_1e6_abs_pairs = [
                (1, 1 + small),
                (1 + small, 1),
                (1, 1 - small),
                (1 - small, 1),
                (100000, 100000 - small),
                (-100000, -100000 - small),
                (-1, -1 + small),
                (-1, -1 - small),
                (0, small),
                (0, -small)
                ]
                
    within_1e6_rel_pairs = [
                (1, 1 + 1 * small),
                (1 + 1 * small, 1),
                (1, 1 - 1 * small),
                (1 - 1 * small, 1),
                (100000, 100000 - 100000 * small),
                (-100000, -100000 - 100000 * small),
                (-1, -1 + -1 * small),
                (-1, -1 - -1 * small),
            ]
 
    outside_1e6_abs_pairs = [
                (1, 1 + big),
                (1 + big, 1),
                (1, 1 - big),
                (1 - big, 1),
                (100000, 100000 - big),
                (-100000, -100000 - big),
                (-1, -1 + big),
                (-1, -1 - big),
                (0, big),
                (0, -big),
                (1e7, 1e7 + 1),
                ]
                
    outside_1e6_rel_pairs = [
                (1, 1 + 1 * big),
                (1 + 1 * big, 1),
                (1, 1 - 1 * big),
                (1 - 1 * big, 1),
                (100000, 100000 - 100000 * big),
                (-100000, -100000 - 100000 * big),
                (-1, -1 + -1 * big),
                (-1, -1 - -1 * big),
                (1e-30, 1e-30 + small),
                (0, small),
                (1e5, 1e5 + 1),
            ]
    def test_assertNotEqual_None(self):
        """assertNotEqual should raise exception with two copies of None"""
        try:
            self.assertNotEqual(None, None)
        except:
            message = str(exc_info()[1])
            self.assertEqual(message, 
            'Observed None and expected None: shouldn\'t test equal')
        else:
            raise AssertionError, \
            "unittests.assertNotEqual failed on input %s and %s" \
            % (`first`, `second`)

    def test_assertNotEqual_numbers(self):
        """assertNotEqual should raise exception with integer and float zero"""
        try:
            self.assertNotEqual(0, 0.0)
        except:
            message = str(exc_info()[1])
            self.assertEqual(message,
            'Observed 0 and expected 0.0: shouldn\'t test equal')
        else:
            raise AssertionError, \
            "unittests.assertNotEqual failed on input %s and %s" \
            % (`first`, `second`)

    def test_assertNotEqual_unequal(self):
        """assertNotEqual should not raise exception when values differ"""
        for first, second in self.unequal_pairs:
            try:
                self.assertNotEqual(first, second)
            except:
                raise AssertionError, \
                "unittests.assertNotEqual failed on input %s and %s" \
                % (`first`, `second`)

    def test_assertNotEqual_equal(self):
        """assertNotEqual should raise exception when values differ"""
        for first, second in self.equal_pairs:
            try:
                self.assertNotEqual(first, second)
            except:
                message = str(exc_info()[1])
                self.assertEqual(message,
                'Observed %s and expected %s: shouldn\'t test equal' \
                % (`first`, `second`))
            else:
                raise AssertionError, \
                "unittests.assertNotEqual failed on input %s and %s" \
                % (`first`, `second`)


    def test_assertEqual_None(self):
        """assertEqual should not raise exception with two copies of None"""
        try:
            self.assertEqual(None, None)
        except:
            raise AssertionError, \
            "unittests.assertEqual failed on input %s and %s" \
            % (`first`, `second`)

    def test_assertEqual_numbers(self):
        """assertEqual should not raise exception with integer and float zero"""
        try:
            self.assertEqual(0, 0.0)
        except:
            raise AssertionError, \
            "unittests.assertEqual failed on input %s and %s" \
            % (`first`, `second`)

    def test_assertEqual_unequal(self):
        """assertEqual should raise exception when values differ"""
        for first, second in self.unequal_pairs:
            try:
                self.assertEqual(first, second)
            except:
                message = str(exc_info()[1])
                self.assertEqual(message,
                'Got %s, but expected %s' \
                % (`first`, `second`))
            else:
                raise AssertionError, \
                "unittests.assertEqual failed on input %s and %s" \
                % (`first`, `second`)

    def test_assertEqual_equal(self):
        """assertEqual should not raise exception when values test equal"""
        for first, second in self.equal_pairs:
            try:
                self.assertEqual(first, second)
            except:
                raise AssertionError, \
                "unittests.assertEqual failed on input %s and %s" \
                % (`first`, `second`)

    def test_assertFloatEqualAbs_equal(self):
        """assertFloatEqualAbs should not raise exception when values within eps"""
        for first, second in self.within_1e6_abs_pairs:
            try:
                self.assertFloatEqualAbs(first, second, eps=1e-6)
            except:
                raise AssertionError, \
                "unittests.assertFloatEqualAbs failed on input %s and %s" \
                % (`first`, `second`)

    def test_assertFloatEqualAbs_threshold(self):
        """assertFloatEqualAbs should raise exception when eps is very small"""
        for first, second in self.within_1e6_abs_pairs:
            try:
                self.assertFloatEqualAbs(first, second, 1e-30)
            except:
                message = str(exc_info()[1])
                diff = first - second
                self.assertEqual(message,
                'Got %s, but expected %s (diff was %s)' \
                % (`first`, `second`, `diff`))
            else:
                raise AssertionError, \
                "unittests.assertFloatEqualAbs failed on input %s and %s" \
                % (`first`, `second`)


    def test_assertFloatEqualAbs_unequal(self):
        """assertFloatEqualAbs should raise exception when values differ by >eps"""
        for first, second in self.outside_1e6_abs_pairs:
            try:
                self.assertFloatEqualAbs(first, second)
            except:
                message = str(exc_info()[1])
                diff = first - second
                self.assertEqual(message,
                'Got %s, but expected %s (diff was %s)' \
                % (`first`, `second`, `diff`))
            else:
                raise AssertionError, \
                "unittests.assertFloatEqualAbs failed on input %s and %s" \
                % (`first`, `second`)

    def test_assertFloatEqualRel_equal(self):
        """assertFloatEqualRel should not raise exception when values within eps"""
        for first, second in self.within_1e6_rel_pairs:
            try:
                self.assertFloatEqualRel(first, second)
            except:
                raise AssertionError, \
                "unittests.assertFloatEqualRel failed on input %s and %s" \
                % (`first`, `second`)

    def test_assertFloatEqualRel_unequal(self):
        """assertFloatEqualRel should raise exception when eps is very small"""
        for first, second in self.within_1e6_rel_pairs:
            try:
                self.assertFloatEqualRel(first, second, 1e-30)
            except:
                message = str(exc_info()[1])
                diff = first - second
                self.assertEqual(message,
                'Got %s, but expected %s (diff was %s)' \
                % (`first`, `second`, `diff`))
            else:
                raise AssertionError, \
                "unittests.assertFloatEqualRel failed on input %s and %s" \
                % (`first`, `second`)


    def test_assertFloatEqualRel_unequal(self):
        """assertFloatEqualRel should raise exception when values differ by >eps"""
        for first, second in self.outside_1e6_rel_pairs:
            try:
                self.assertFloatEqualRel(first, second)
            except:
                message = str(exc_info()[1])
                diff = first - second
                self.assertEqual(message,
                'Got %s, but expected %s (diff was %s)' \
                % (`first`, `second`, `diff`))
            else:
                raise AssertionError, \
                "unittests.assertFloatEqualRel failed on input %s and %s" \
                % (`first`, `second`)


    def test_assertFloatEqualList_equal(self):
        """assertFloatEqual should work on two lists of similar values"""
        originals = [0, 1, -1, 10, -10, 100, -100]
        modified = [i + 1e-7 for i in originals]
        try:
            self.assertFloatEqual(originals, modified)
            self.assertFloatEqual([], [])   #test empty lists as well
        except:
            raise AssertionError, \
            "unittests.assertFloatEqual failed on lists of similar values"

    def test_assertFloatEqualList_unequal(self):
        """assertFloatEqual should fail on two lists of dissimilar values"""
        originals = [0, 1, -1, 10, -10, 100, -100]
        modified = [i + 1e-5 for i in originals]
        try:
            self.assertFloatEqual(originals, modified)
        except:
            pass            
        else:
            raise AssertionError, \
            "unittests.assertFloatEqual failed on lists of dissimilar values"

    def test_assertFloatEqual_mixed(self):
        """assertFloatEqual should work on equal lists of mixed types."""
        first = [i[0] for i in self.equal_pairs]
        second = [i[1] for i in self.equal_pairs]
        self.assertFloatEqual(first, second)

    def test_assertFloatEqualAbs_mixed(self):
        first = [i[0] for i in self.equal_pairs]
        second = [i[1] for i in self.equal_pairs]
        """assertFloatEqualAbs should work on equal lists of mixed types."""
        self.assertFloatEqualAbs(first, second)

    def test_assertFloatEqualRel_mixed(self):
        first = [i[0] for i in self.equal_pairs]
        second = [i[1] for i in self.equal_pairs]
        """assertFloatEqualRel should work on equal lists of mixed types."""
        self.assertFloatEqualRel(first, second)

    def test_assertFloatEqual_mixed_unequal(self):
        """assertFloatEqual should work on unequal lists of mixed types."""
        first = [i[0] for i in self.unequal_pairs]
        second = [i[1] for i in self.unequal_pairs]
        self.assertRaises(AssertionError, \
            self.assertFloatEqual, first, second)

    def test_assertFloatEqualAbs_mixed(self):
        """assertFloatEqualAbs should work on lists of mixed types."""
        first = [i[0] for i in self.unequal_pairs]
        second = [i[1] for i in self.unequal_pairs]
        self.assertRaises(AssertionError, \
            self.assertFloatEqualAbs, first, second)

    def test_assertFloatEqualRel_mixed(self):
        """assertFloatEqualRel should work on lists of mixed types."""
        first = [i[0] for i in self.unequal_pairs]
        second = [i[1] for i in self.unequal_pairs]
        self.assertRaises(AssertionError, \
            self.assertFloatEqualRel, first, second)

    def test_assertEqualItems(self):
        """assertEqualItems should raise exception if items not equal"""
        self.assertEqualItems('abc', 'abc')
        self.assertEqualItems('abc', 'cba')
        self.assertEqualItems('', '')
        self.assertEqualItems('abc', ['a','b','c'])
        self.assertEqualItems([0], [0.0])
        
        try:
            self.assertEqualItems('abc', 'abcd')
        except:
            message = str(exc_info()[1])
            self.assertEqual(message, 
            'Observed and expected are different lengths: 3 and 4')
        else:
            raise AssertionError, \
            "unittests.assertEqualItems failed on input %s and %s" \
            % (`first`, `second`)

        try:
            self.assertEqualItems('cab', 'acc')
        except:
            message = str(exc_info()[1])
            self.assertEqual(message, 
            'Observed b and expected c at sorted index 1')
        else:
            raise AssertionError, \
            "unittests.assertEqualItems failed on input %s and %s" \
            % (`first`, `second`)
        try:
            self.assertEqualItems('cba', 'yzx')
        except:
            message = str(exc_info()[1])
            self.assertEqual(message,
            'Observed a and expected x at sorted index 0')
        else:
            raise AssertionError, \
            "unittests.assertEqualItems failed on input %s and %s" \
            % (`first`, `second`)

    def test_assertSameItems(self):
        """assertSameItems should raise exception if items not same"""
        x = 0
        y = 'abcdef'
        z = 3
        y1 = 'abc' + 'def'
        z1 = 3.0

        y_id = id(y)
        z_id = id(z)
        y1_id = id(y1)
        z1_id = id(z1)

        assert y is not y1
        
        self.assertSameItems([x,y,z], [x,y,z])
        self.assertSameItems([x,y,z], [z,x,y])
        self.assertSameItems('', '')
        self.assertSameItems([x,y,z], (x,y,z))
        
        try:
            self.assertSameItems([x,y,z], [x,y,z,y])
        except:
            message = str(exc_info()[1])
            self.assertEqual(message,
            'Observed and expected are different lengths: 3 and 4')
        else:
            raise AssertionError, \
            "unittests.assertSameItems failed on input %s and %s" \
            % (`[x,y,z]`, `[x,y,z,y]`)

        try:
            first_list = [x,y,z]
            second_list = [y,x,z1]
            self.assertSameItems(first_list, second_list)
        except self.failureException:
            pass
        else:
            raise AssertionError, \
            "unittests.assertEqualItems failed on input %s and %s" \
            % (`[x,y,z]`, `[y,x,z1]`)
        try:
            self.assertSameItems([y], (y1,))
        except self.failureException:
            pass
        else:
            raise AssertionError, \
            "unittests.assertEqualItems failed on input %s and %s" \
            % (`[y]`, `(y1,)`)

    def test_assertNotEqualItems(self):
        """assertNotEqualItems should raise exception if all items equal"""
        self.assertNotEqualItems('abc', '')
        self.assertNotEqualItems('abc', 'cbad')
        self.assertNotEqualItems([0], [0.01])
        
        try:
            self.assertNotEqualItems('abc', 'abc')
        except:
            message = str(exc_info()[1])
            self.assertEqual(message, 
            "Observed 'abc' has same items as 'abc'")
        else:
            raise AssertionError, \
            "unittests.assertNotEqualItems failed on input %s and %s" \
            % (`'abc'`, `'abc'`)

        try:
            self.assertNotEqualItems('', [])
        except:
            message = str(exc_info()[1])
            self.assertEqual(message, "Observed '' has same items as []")
        else:
            raise AssertionError, \
            "unittests.assertNotEqualItems failed on input %s and %s" \
            % (`''`, `[]`)

    def test_assertContains(self):
        """assertContains should raise exception if item not in test set"""
        self.assertContains('abc', 'a')
        self.assertContains(['a', 'b', 'c'], 'a')
        self.assertContains(['a', 'b', 'c'], 'b')
        self.assertContains(['a', 'b', 'c'], 'c')
        self.assertContains({'a':1, 'b':2}, 'a')

        class _fake_container(object):
            def __contains__(self, other):
                return True

        fake = _fake_container()
        self.assertContains(fake, 'x')
        self.assertContains(fake, 3)
        self.assertContains(fake, {'a':'b'})
        
        try:
            self.assertContains('', [])
        except:
            message = str(exc_info()[1])
            self.assertEqual(message, "Item [] not found in ''")
        else:
            raise AssertionError, \
            "unittests.assertContains failed on input %s and %s" \
            % (`''`, `[]`)

        try:
            self.assertContains('abcd', 'x')
        except:
            message = str(exc_info()[1])
            self.assertEqual(message, "Item 'x' not found in 'abcd'")
        else:
            raise AssertionError, \
            "unittests.assertContains failed on input %s and %s" \
            % (`'abcd'`, `'x'`)

    def test_assertNotContains(self):
        """assertNotContains should raise exception if item in test set"""
        self.assertNotContains('abc', 'x')
        self.assertNotContains(['a', 'b', 'c'], 'x')
        self.assertNotContains('abc', None)
        self.assertNotContains(['a', 'b', 'c'], {'x':1})
        self.assertNotContains({'a':1, 'b':2}, 3.0)

        class _fake_container(object):
            def __contains__(self, other):
                return False

        fake = _fake_container()
        self.assertNotContains(fake, 'x')
        self.assertNotContains(fake, 3)
        self.assertNotContains(fake, {'a':'b'})
        
        try:
            self.assertNotContains('', '')
        except:
            message = str(exc_info()[1])
            self.assertEqual(message, "Item '' should not have been in ''")
        else:
            raise AssertionError, \
            "unittests.assertNotContains failed on input %s and %s" \
            % (`''`, `''`)

        try:
            self.assertNotContains('abcd', 'a')
        except:
            message = str(exc_info()[1])
            self.assertEqual(message, "Item 'a' should not have been in 'abcd'")
        else:
            raise AssertionError, \
            "unittests.assertNotContains failed on input %s and %s" \
            % (`'abcd'`, `'a'`)

        try:
            self.assertNotContains({'a':1, 'b':2}, 'a')
        except:
            message = str(exc_info()[1])
            self.assertEqual(message, \
            "Item 'a' should not have been in {'a': 1, 'b': 2}")
        else:
            raise AssertionError, \
            "unittests.assertNotContains failed on input %s and %s" \
            % (`{'a':1, 'b':2}`, `'a'`)

if __name__ == '__main__':
    main()
            
