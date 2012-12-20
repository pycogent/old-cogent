#!/usr/bin/env python
# file util/test_array.py: unit tests for array utils
"""Provides tests for array.py

Owner: ?

Status: Development

Revision History:
File started by Rob and Jeremy: tests for functions gapped_to_ungapped, 
    ungapped_to_gapped, masked_to_unmasked, unmasked_to_masked, pairs_to_array  
    
9/15/05 Sandra Smit: added tests for ln_2, log2, safe_p_log_p, safe_log, 
    row_uncertainty, column_uncertainty, row_degeneracy, column_degeneracy,
    hamming_distance, norm, euclidean_distance
2/8/06 Sandra Smit: fixed array tests for nan. Added tests for integer -> float
"""
from old_cogent.util.unit_test import main, TestCase
from old_cogent.util.array import gapped_to_ungapped, unmasked_to_masked, \
    ungapped_to_gapped, masked_to_unmasked, pairs_to_array,\
    ln_2, log2, safe_p_log_p, safe_log, row_uncertainty, column_uncertainty,\
    row_degeneracy, column_degeneracy, hamming_distance, norm,\
    euclidean_distance
from Numeric import array, zeros, Float64, transpose, sqrt


class arrayTests(TestCase):
    """Tests of top-level functions."""
    def setUp(self):
        """set up some standard sequences and masks"""
        self.s1 = array('ACT-G')
        self.s2 = array('--CT')
        self.s3 = array('AC--')
        self.s4 = array('AC')
        self.s5 = array('--')
        self.m1 = array([0,0,0,1,0])
        self.m2 = array([1,1,0,0])
        self.m3 = array([0,0,1,1])
        self.m4 = array([0,0])
        self.m5 = array([1,1])
    
    def test_unmasked_to_masked(self):
        """unmasked_to_masked should match hand-calculated results"""
        u2m = unmasked_to_masked
        self.assertEqual(u2m(self.m1), array([0,1,2,4]))
        self.assertEqual(u2m(self.m2), array([2,3]))
        self.assertEqual(u2m(self.m3), array([0,1]))
        self.assertEqual(u2m(self.m4), array([0,1]))
        self.assertEqual(u2m(self.m5), array([]))

    def test_ungapped_to_gapped(self):
        """ungapped_to_gapped should match hand-calculated results"""
        u2g = ungapped_to_gapped
        self.assertEqual(u2g(self.s1, '-'), array([0,1,2,4]))
        self.assertEqual(u2g(self.s2, '-'), array([2,3]))
        self.assertEqual(u2g(self.s3, '-'), array([0,1]))
        self.assertEqual(u2g(self.s4, '-'), array([0,1]))
        self.assertEqual(u2g(self.s5, '-'), array([]))

    def test_masked_to_unmasked(self):
        """masked_to_unmasked should match hand-calculated results"""
        m2u = masked_to_unmasked
        self.assertEqual(m2u(self.m1), array([0,1,2,2,3]))
        self.assertEqual(m2u(self.m1, True), array([0,1,2,-1,3]))
        self.assertEqual(m2u(self.m2), array([-1,-1,0,1]))
        self.assertEqual(m2u(self.m2, True), array([-1,-1,0,1]))
        self.assertEqual(m2u(self.m3), array([0,1,1,1]))
        self.assertEqual(m2u(self.m3, True), array([0,1,-1,-1]))
        self.assertEqual(m2u(self.m4), array([0,1]))
        self.assertEqual(m2u(self.m4, True), array([0,1]))
        self.assertEqual(m2u(self.m5), array([-1,-1]))
        self.assertEqual(m2u(self.m5, True), array([-1,-1]))
        
    def test_gapped_to_ungapped(self):
        """gapped_to_ungapped should match hand-calculated results"""
        g2u = gapped_to_ungapped
        self.assertEqual(g2u(self.s1, '-'), array([0,1,2,2,3]))
        self.assertEqual(g2u(self.s1, '-', True), array([0,1,2,-1,3]))
        self.assertEqual(g2u(self.s2, '-'), array([-1,-1,0,1]))
        self.assertEqual(g2u(self.s2, '-', True), array([-1,-1,0,1]))
        self.assertEqual(g2u(self.s3, '-'), array([0,1,1,1]))
        self.assertEqual(g2u(self.s3, '-', True), array([0,1,-1,-1]))
        self.assertEqual(g2u(self.s4, '-'), array([0,1]))
        self.assertEqual(g2u(self.s4, '-', True), array([0,1]))
        self.assertEqual(g2u(self.s5, '-'), array([-1,-1]))
        self.assertEqual(g2u(self.s5, '-', True), array([-1,-1]))

    def test_pairs_to_array(self):
        """pairs_to_array should match hand-calculated results"""
        p2a = pairs_to_array
        p1 = [0, 1, 0.5]
        p2 = [2, 3, 0.9]
        p3 = [1, 2, 0.6]
        pairs = [p1, p2, p3]
        self.assertEqual(p2a(pairs), \
            array([[0,.5,0,0],[0,0,.6,0],[0,0,0,.9],[0,0,0,0]]))
        #try it without weights -- should assign 1
        new_pairs = [[0,1],[2,3],[1,2]]
        self.assertEqual(p2a(new_pairs), \
            array([[0,1,0,0],[0,0,1,0],[0,0,0,1],[0,0,0,0]]))
        #try it with explicit array size
        self.assertEqual(p2a(pairs, 5), \
            array([[0,.5,0,0,0],[0,0,.6,0,0],[0,0,0,.9,0],[0,0,0,0,0],\
            [0,0,0,0,0]]))
        #try it when we want to map the indices into gapped coords
        #we're effectively doing ABCD -> -A--BC-D-
        transform = array([1,4,5,7])
        result = p2a(pairs, transform=transform)
        self.assertEqual(result.shape, (8,8))
        exp = zeros((8,8), Float64)
        exp[1,4] = 0.5
        exp[4,5] = 0.6
        exp[5,7] = 0.9
        self.assertEqual(result, exp)

        result = p2a(pairs, num_items=9, transform=transform)
        self.assertEqual(result.shape, (9,9))
        exp = zeros((9,9), Float64)
        exp[1,4] = 0.5
        exp[4,5] = 0.6
        exp[5,7] = 0.9
        self.assertEqual(result, exp)
         
class ArrayMathTests(TestCase):
    
    def test_ln_2(self):
        """ln_2: should be constant"""
        self.assertFloatEqual(ln_2, 0.693147)

    def test_log2(self):
        """log2: should work fine on positive/negative numbers and zero"""
        self.assertEqual(log2(1),0)
        self.assertEqual(log2(2),1)
        self.assertEqual(log2(4),2)
        self.assertEqual(log2(8),3)
        self.assertEqual(log2(0),float('-inf'))
        #nan is the only thing that's not equal to itself
        self.assertNotEqual(log2(-1),log2(-1)) #now nan

    def test_safe_p_log_p(self):
        """safe_p_log_p: should handle pos/neg/zero/empty arrays as expected
        """
        #normal valid array
        a = array([[4,0,8],[2,16,4]])
        self.assertEqual(safe_p_log_p(a),array([[-8,0,-24],[-2,-64,-8]]))
        #just zeros
        a = array([[0,0],[0,0]])
        self.assertEqual(safe_p_log_p(a),array([[0,0],[0,0]]))
        #negative number
        self.assertNotEqual(safe_p_log_p(array([-4])),safe_p_log_p(array([-4])))
        #integer input, float output
        self.assertFloatEqual(safe_p_log_p(array([3])),array([-4.75488750]))
        #empty array
        self.assertEqual(safe_p_log_p(array([])),array([]))

    def test_safe_log(self):
        """safe_log: should handle pos/neg/zero/empty arrays as expected
        """
        #normal valid array
        a = array([[4,0,8],[2,16,4]])
        self.assertEqual(safe_log(a),array([[2,0,3],[1,4,2]]))
        #input integers, output floats
        self.assertFloatEqual(safe_log(array([1,2,3])),array([0,1,1.5849625]))
        #just zeros
        a = array([[0,0],[0,0]])
        self.assertEqual(safe_log(a),array([[0,0],[0,0]]))
        #negative number
        self.assertFloatEqual(safe_log(array([0,3,-4]))[0:2],array([0,1.5849625007]))
        self.assertNotEqual(safe_log(array([0,3,-4]))[2],\
            safe_log(array([0,3,-4]))[2])
        #empty array
        self.assertEqual(safe_log(array([])),array([]))
        #double empty array
        self.assertEqual(safe_log(array([[]])),array([[]]))

    def test_row_uncertainty(self):
        """row_uncertainty: should handle pos/neg/zero/empty arrays as expected
        """
        #normal valid array
        b = transpose(array([[.25,.2,.45,.25,1],[.25,.2,.45,0,0],\
            [.25,.3,.05,.75,0],[.25,.3,.05,0,0]]))
        self.assertFloatEqual(row_uncertainty(b),[2,1.97,1.47,0.81,0],1e-3)
        #one-dimensional array
        self.assertRaises(ValueError, row_uncertainty,\
            array([.25,.25,.25,.25]))
        #zeros
        self.assertEqual(row_uncertainty(array([[0,0]])),array([0]))
        #empty 2D array
        self.assertEqual(row_uncertainty(array([[]])),array([0]))
        self.assertEqual(row_uncertainty(array([[],[]])),array([0,0]))
        #negative number
        self.assertNotEqual(row_uncertainty(array([[-2]])),\
            row_uncertainty(array([[-2]])))

    def test_col_uncertainty(self):
        """column_uncertainty: should handle pos/neg/zero/empty arrays
        """
        b = array([[.25,.2,.45,.25,1],[.25,.2,.45,0,0],[.25,.3,.05,.75,0],\
            [.25,.3,.05,0,0]])
        self.assertFloatEqual(column_uncertainty(b),[2,1.97,1.47,0.81,0],1e-3)
        #one-dimensional array
        self.assertRaises(ValueError, column_uncertainty,\
            array([.25,.25,.25,.25]))
        #zeros
        self.assertEqual(column_uncertainty(array([[0,0]])),array([0,0]))
        #empty 2D array
        self.assertEqual(column_uncertainty(array([[]])),array([]))
        self.assertEqual(column_uncertainty(array([[],[]])),array([]))
        #negative number
        self.assertNotEqual(column_uncertainty(array([[-2]])),\
            column_uncertainty(array([[-2]])))

    def test_row_degeneracy(self):
        """row_degeneracy: should work with different cutoff values and arrays
        """
        a = array([[.1, .3, .4, .2],[.5, .3, 0, .2],[.8, 0, .1, .1]])
        self.assertEqual(row_degeneracy(a,cutoff=.75),[3,2,1])
        self.assertEqual(row_degeneracy(a,cutoff=.95),[4,3,3])
        #one-dimensional array
        self.assertRaises(ValueError, row_degeneracy,\
            array([.25,.25,.25,.25]))
        #if cutoff value is not found, results are clipped to the
        #number of columns in the array
        self.assertEqual(row_degeneracy(a,cutoff=2), [4,4,4])
        #same behavior on empty array
        self.assertEqual(row_degeneracy(array([[]])),[])

    def test_column_degeneracy(self):
        """column_degeneracy: should work with different cutoff values
        """
        a = array([[.1,.8,.3],[.3,.2,.3],[.6,0,.4]])
        self.assertEqual(column_degeneracy(a,cutoff=.75),[2,1,3])
        self.assertEqual(column_degeneracy(a,cutoff=.45),[1,1,2])
        #one-dimensional array
        self.assertRaises(ValueError, column_degeneracy,\
            array([.25,.25,.25,.25]))
        #if cutoff value is not found, results are clipped to the
        #number of rows in the array
        self.assertEqual(column_degeneracy(a,cutoff=2), [3,3,3])
        #same behavior on empty array
        self.assertEqual(column_degeneracy(array([[]])),[])

    def test_hamming_distance_same_length(self):
        """hamming_distance: should return # of chars different"""
        self.assertEqual(hamming_distance(array('ABC'),array('ABB')),1)
        self.assertEqual(hamming_distance(array('ABC'),array('ABC')),0)
        self.assertEqual(hamming_distance(array('ABC'),array('DDD')),3)
       
    def test_hamming_distance_diff_length(self):
        """hamming_distance: truncates at shortest sequence"""
        self.assertEqual(hamming_distance(array('ABC'),array('ABBDDD')),1)
        self.assertEqual(hamming_distance(array('ABC'),array('ABCDDD')),0)
        self.assertEqual(hamming_distance(array('ABC'),array('DDDDDD')),3)

    def test_norm(self):
        """norm: should return vector or matrix norm"""
        self.assertFloatEqual(norm(array([2,3,4,5])),sqrt(54))
        self.assertEqual(norm(array([1,1,1,1])),2)
        self.assertFloatEqual(norm(array([[2,3],[4,5]])),sqrt(54))
        self.assertEqual(norm(array([[1,1],[1,1]])),2)

    def test_euclidean_distance(self):
        """euclidean_distance: should return dist between 2 vectors or matrices
        """
        a = array([3,4])
        b = array([8,5])
        c = array([[2,3],[4,5]])
        d = array([[1,5],[8,2]])
        self.assertFloatEqual(euclidean_distance(a,b),sqrt(26))
        self.assertFloatEqual(euclidean_distance(c,d),sqrt(30))

    def test_euclidean_distance_unexpected(self):
        """euclidean_distance: works always when frames are aligned. UNEXPECTED!
        """
        a = array([3,4])
        b = array([8,5])
        c = array([[2,3],[4,5]])
        d = array([[1,5],[8,2]])
        e = array([[4,5],[4,5],[4,5]])
        f = array([1,1,1,1,1])
        self.assertFloatEqual(euclidean_distance(a,c),sqrt(4))
        self.assertFloatEqual(euclidean_distance(c,a),sqrt(4))
        self.assertFloatEqual(euclidean_distance(a,e),sqrt(6))

        #IT DOES RAISE AN ERROR WHEN THE FRAMES ARE NOT ALIGNED
        self.assertRaises(ValueError,euclidean_distance,c,e)
        self.assertRaises(ValueError,euclidean_distance,c,f)


if __name__ == '__main__':
    main()
