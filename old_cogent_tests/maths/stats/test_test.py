#!/usr/bin/env python
#file evo/stats/test_test.py

"""Unit tests for statistical tests and utility functions.

Owner: Rob Knight rob@spot.colorado.edu

Revision History

3/2/03-3/12-03 Rob Knight: written as part of ADBAnalysis.

4/21-26/03 Rob Knight: revised to use test data from R instead of spreadsheets.

4/29/03 Rob Knight: revised to clean up docstrings.

5/7/03 Rob Knight: added tests for t-tests in the case where the variance is 0.

8/4/03 Rob Knight: added tests for correlation and correlation_matrix. Changed
module names.

8/7/03 Rob Knight: updated tests to reflect new API (now return None for bad
values and also changed many of the method names).

8/21/03 Rob Knight: added tests for combinations and multiple_comparisons.

8/22/03 Rob Knight: added test for multiple_comparisons when p is large.

9/17/03 Rob Knight: changed variable names to underscore convention. Changed
imports.

10/14/03 Rob Knight: changed imports.

11/1/03 Rob Knight: added tests for new multiple comparisons helpers.

11/10/03 Rob Knight: added tests for regression and Fisher's method.

12/16/03 Rob Knight: added test for correlation after out-of-bounds result
reported by Greg Caporaso.

2/15/05 Sandra Smit: added tests for f_value and f_two_sample.

5/23/05 Cathy Lozupone: added tests for calc_contingency_expected, 
G_fit_from_Dict2D, chi_square_from_Dict2D, and MonteCarloP

1/26/06 Cathy Lozupone: added tests for regress residuals
1/27/06 Cathy Lozupone: added tests for stddev_from_mean
2/4/06 Cathy Lozupone: added test for regress_R2
"""

from old_cogent.util.unit_test import TestCase, main
from old_cogent.maths.stats.test import tail, G_2_by_2,G_fit, likelihoods,\
    posteriors, bayes_updates, t_paired, t_one_sample, t_two_sample, \
    t_one_observation,correlation, correlation_matrix, z_test, z_tailed_prob, \
    t_tailed_prob, \
    reverse_tails, ZeroExpectedError, combinations, multiple_comparisons, \
    multiple_inverse, multiple_n, fisher, regress, regress_major,\
    f_value, f_two_sample, calc_contingency_expected, G_fit_from_Dict2D, \
    chi_square_from_Dict2D, MonteCarloP, regress_residuals, safe_sum_p_log_p, \
    G_ind, regress_origin, stddev_from_mean, regress_R2
from old_cogent.base.stats import Numbers
from old_cogent.base.dict2d import Dict2D
from Numeric import array
import math

class TestsTests(TestCase):
    """Tests miscellaneous functions."""

    def test_tail(self):
        """tail should return x/2 if test is true; 1-(x/2) otherwise"""
        self.assertFloatEqual(tail(0.25, 'a'=='a'), 0.25/2)
        self.assertFloatEqual(tail(0.25, 'a'!='a'), 1-(0.25/2))

    def test_combinations(self):
        """combinations should return correct binomial coefficient"""
        self.assertFloatEqual(combinations(5,3), 10)
        self.assertFloatEqual(combinations(5,2), 10)
        #only one way to pick no items or the same number of items
        self.assertFloatEqual(combinations(123456789, 0), 1)
        self.assertFloatEqual(combinations(123456789, 123456789), 1)
        #n ways to pick one item
        self.assertFloatEqual(combinations(123456789, 1), 123456789)
        #n(n-1)/2 ways to pick 2 items
        self.assertFloatEqual(combinations(123456789, 2), 123456789*123456788/2)
        #check an arbitrary value in R
        self.assertFloatEqual(combinations(1234567, 12), 2.617073e64)
    
    def test_multiple_comparisons(self):
        """multiple_comparisons should match values from R"""
        self.assertFloatEqual(multiple_comparisons(1e-7, 10000), 1-0.9990005)
        self.assertFloatEqual(multiple_comparisons(0.05, 10), 0.4012631)
        self.assertFloatEqual(multiple_comparisons(1e-20, 1), 1e-20)
        self.assertFloatEqual(multiple_comparisons(1e-300, 1), 1e-300)
        self.assertFloatEqual(multiple_comparisons(0.95, 3),0.99987499999999996)
        self.assertFloatEqual(multiple_comparisons(0.75, 100),0.999999999999679)
        self.assertFloatEqual(multiple_comparisons(0.5, 1000),1)
        self.assertFloatEqual(multiple_comparisons(0.01, 1000),0.99995682875259)
        self.assertFloatEqual(multiple_comparisons(0.5, 5), 0.96875)
        self.assertFloatEqual(multiple_comparisons(1e-20, 10), 1e-19)

    def test_multiple_inverse(self):
        """multiple_inverse should invert multiple_comparisons results"""
        #NOTE: multiple_inverse not very accurate close to 1
        self.assertFloatEqual(multiple_inverse(1-0.9990005, 10000), 1e-7)
        self.assertFloatEqual(multiple_inverse(0.4012631 , 10), 0.05)
        self.assertFloatEqual(multiple_inverse(1e-20, 1), 1e-20)
        self.assertFloatEqual(multiple_inverse(1e-300, 1), 1e-300)
        self.assertFloatEqual(multiple_inverse(0.96875, 5), 0.5)
        self.assertFloatEqual(multiple_inverse(1e-19, 10), 1e-20)

    def test_multiple_n(self):
        """multiple_n should swap parameters in multiple_comparisons"""
        self.assertFloatEqual(multiple_n(1e-7, 1-0.9990005), 10000)
        self.assertFloatEqual(multiple_n(0.05, 0.4012631), 10)
        self.assertFloatEqual(multiple_n(1e-20, 1e-20), 1)
        self.assertFloatEqual(multiple_n(1e-300, 1e-300), 1)
        self.assertFloatEqual(multiple_n(0.95,0.99987499999999996),3)
        self.assertFloatEqual(multiple_n(0.5,0.96875),5)
        self.assertFloatEqual(multiple_n(1e-20, 1e-19), 10)

    def test_fisher(self):
        """fisher results should match p 795 Sokal and Rohlf"""
        self.assertFloatEqual(fisher([0.073,0.086,0.10,0.080,0.060]), 
            0.0045957946540917905)

    def test_regress(self):
        """regression slope, intercept should match p 459 Sokal and Rohlf"""
        x = [0, 12, 29.5,43,53,62.5,75.5,85,93]
        y = [8.98, 8.14, 6.67, 6.08, 5.90, 5.83, 4.68, 4.20, 3.72]
        self.assertFloatEqual(regress(x, y), (-0.05322, 8.7038), 0.001)
        #higher precision from OpenOffice
        self.assertFloatEqual(regress(x, y), (-0.05322215,8.70402730))

    def test_regress_origin(self):
        """regression slope constrained through origin should match Excel"""
        x = array([1,2,3,4])
        y = array([4,2,6,8])
        self.assertFloatEqual(regress_origin(x, y), (1.9333333,0))

    def test_regress_R2(self):
        """regress_R2 returns the R^2 value of a regression"""
        x = [1.0,2.0,3.0,4.0,5.0]
        y = [2.1,4.2,5.9,8.4,9.6]
        result = regress_R2(x, y)
        self.assertFloatEqual(result, 0.99171419347896)

    def test_regress_residuals(self):
        """regress_residuals reprts error for points in linear regression"""
        x = [1.0,2.0,3.0,4.0,5.0]
        y = [2.1,4.2,5.9,8.4,9.6]
        result = regress_residuals(x, y)
        self.assertFloatEqual(result, [-0.1, 0.08, -0.14, 0.44, -0.28])

    def test_stddev_from_mean(self):
        """stddev_from_mean returns num std devs from mean for each val in x"""
        x = [2.1, 4.2, 5.9, 8.4, 9.6]
        result = stddev_from_mean(x)
        self.assertFloatEqual(result, [-1.292463399014413, -0.60358696806764478, -0.045925095396451399, 0.77416589382589174, 1.1678095686526162]) 

    def test_regress_major(self):
        """major axis regression should match p 589 Sokal and Rohlf"""
        #Note that the Sokal and Rohlf example flips the axes, such that the
        #equation is for explaining x in terms of y, not y in terms of x.
        #Behavior here is the reverse, for easy comparison with regress.
        y = [159, 179, 100, 45, 384, 230, 100, 320, 80, 220, 320, 210]
        x = [14.40, 15.20, 11.30, 2.50, 22.70, 14.90, 1.41, 15.81, 4.19, 15.39,
             17.25, 9.52]
        self.assertFloatEqual(regress_major(x, y), (18.93633,-32.55208))

class GTests(TestCase):
    """Tests implementation of the G tests for fit and independence."""
    def test_G_2_by_2_2tailed_equal(self):
        """G_2_by_2 should return 0 if all cell counts are equal"""
        self.assertFloatEqual(0, G_2_by_2(1, 1, 1, 1, False, False)[0])
        self.assertFloatEqual(0, G_2_by_2(100, 100, 100, 100, False, False)[0])
        self.assertFloatEqual(0, G_2_by_2(100, 100, 100, 100, True, False)[0])
   
    def test_G_2_by_2_bad_data(self):
        """G_2_by_2 should raise ValueError if any counts are negative"""
        self.assertRaises(ValueError, G_2_by_2, 1, -1, 1, 1)
   
    def test_G_2_by_2_2tailed_examples(self):
        """G_2_by_2 values should match examples in Sokal & Rohlf"""
        #example from p 731, Sokal and Rohlf (1995)
        #without correction
        self.assertFloatEqual(G_2_by_2(12, 22, 16, 50, False, False)[0], 
            1.33249, 0.0001)
        self.assertFloatEqual(G_2_by_2(12, 22, 16, 50, False, False)[1], 
            0.24836, 0.0001)
        #with correction
        self.assertFloatEqual(G_2_by_2(12, 22, 16, 50, True, False)[0],
            1.30277, 0.0001)
        self.assertFloatEqual(G_2_by_2(12, 22, 16, 50, True, False)[1],
            0.25371, 0.0001)

    def test_G_2_by_2_1tailed_examples(self):
        """G_2_by_2 values should match values from codon_binding program"""
        #first up...the famous arginine case
        self.assertFloatEqualAbs(G_2_by_2(36, 16, 38, 106), (29.111609, 0),
            0.00001)
        #then some other miscellaneous positive and negative values
        self.assertFloatEqualAbs(G_2_by_2(0,52,12,132), (-7.259930, 0.996474),
            0.00001)
        self.assertFloatEqualAbs(G_2_by_2(5,47,14,130), (-0.000481, 0.508751),
            0.00001)
        self.assertFloatEqualAbs(G_2_by_2(5,47,36,108), (-6.065167, 0.993106),
            0.00001)

    def test_calc_contingency_expected(self):
        """calcContingencyExpected returns new matrix with expected freqs"""
        matrix = Dict2D({'rest_of_tree': {'env1': 2, 'env3': 1, 'env2': 0},
                  'b': {'env1': 1, 'env3': 1, 'env2': 3}})
        result = calc_contingency_expected(matrix)
        self.assertFloatEqual(result['rest_of_tree']['env1'], [2, 1.125])
        self.assertFloatEqual(result['rest_of_tree']['env3'], [1, 0.75])
        self.assertFloatEqual(result['rest_of_tree']['env2'], [0, 1.125])
        self.assertFloatEqual(result['b']['env1'], [1, 1.875])
        self.assertFloatEqual(result['b']['env3'], [1, 1.25])
        self.assertFloatEqual(result['b']['env2'], [3, 1.875])
        
    def test_Gfit_unequal_lists(self):
        """Gfit should raise errors if lists unequal"""
        #lists must be equal
        self.assertRaises(ValueError, G_fit, [1, 2, 3], [1, 2])

    def test_Gfit_negative_observeds(self):
        """Gfit should raise ValueError if any observeds are negative."""
        self.assertRaises(ValueError, G_fit, [-1, 2, 3], [1, 2, 3])
    
    def test_Gfit_nonpositive_expecteds(self):
        """Gfit should raise ZeroExpectedError if expecteds are zero/negative"""
        self.assertRaises(ZeroExpectedError, G_fit, [1, 2, 3], [0, 1, 2])
        self.assertRaises(ZeroExpectedError, G_fit, [1, 2, 3], [-1, 1, 2])
    
    def test_Gfit_good_data(self):
        """Gfit tests for fit should match examples in Sokal and Rohlf"""
        #example from p. 699, Sokal and Rohlf (1995)
        obs = [63, 31, 28, 12, 39, 16, 40, 12]
        exp = [ 67.78125, 22.59375, 22.59375, 7.53125, 45.18750,
                15.06250, 45.18750, 15.06250]
        #without correction
        self.assertFloatEqualAbs(G_fit(obs, exp, False)[0], 8.82397, 0.00002)
        self.assertFloatEqualAbs(G_fit(obs, exp, False)[1], 0.26554, 0.00002)
        #with correction
        self.assertFloatEqualAbs(G_fit(obs, exp)[0], 8.76938, 0.00002)
        self.assertFloatEqualAbs(G_fit(obs, exp)[1], 0.26964, 0.00002)
        
        #example from p. 700, Sokal and Rohlf (1995)
        obs = [130, 46]
        exp = [132, 44]
        #without correction
        self.assertFloatEqualAbs(G_fit(obs, exp, False)[0], 0.12002, 0.00002)
        self.assertFloatEqualAbs(G_fit(obs, exp, False)[1], 0.72901, 0.00002)
        #with correction
        self.assertFloatEqualAbs(G_fit(obs, exp)[0], 0.11968, 0.00002)
        self.assertFloatEqualAbs(G_fit(obs, exp)[1], 0.72938, 0.00002)

    def test_safe_sum_p_log_p(self):
        """safe_sum_p_log_p should ignore zero elements, not raise error"""
        m = array([2,4,0,8])
        self.assertEqual(safe_sum_p_log_p(m,2), 2*1+4*2+8*3)

    def test_G_ind(self):
        """G test for independence should match Sokal and Rohlf p 738 values"""
        a = array([[29,11],[273,191],[8,31],[64,64]])
        self.assertFloatEqual(G_ind(a)[0], 28.59642)
        self.assertFloatEqual(G_ind(a, True)[0], 28.31244)

    def test_G_fit_from_Dict2D(self):
        """G_fit_from_Dict2D runs G-fit on data in a Dict2D
        """
        matrix = Dict2D({'Marl': {'val':[2, 5.2]},
                        'Chalk': {'val':[10, 5.2]},
                        'Sandstone':{'val':[8, 5.2]},
                        'Clay':{'val':[2, 5.2]},
                        'Limestone':{'val':[4, 5.2]}
                        })
        g_val, prob = G_fit_from_Dict2D(matrix)
        self.assertFloatEqual(g_val, 9.84923)
        self.assertFloatEqual(prob, 0.04304536)

    def test_chi_square_from_Dict2D(self):
        """chi_square_from_Dict2D calcs a Chi-Square and p value from Dict2D"""
        #test1
        obs_matrix = Dict2D({'rest_of_tree': {'env1': 2, 'env3': 1, 'env2': 0},
                  'b': {'env1': 1, 'env3': 1, 'env2': 3}})
        input_matrix = calc_contingency_expected(obs_matrix)
        test, csp = chi_square_from_Dict2D(input_matrix)
        self.assertFloatEqual(test, 3.0222222222222221)
        #test2
        test_matrix_2 = Dict2D({'Marl': {'val':[2, 5.2]},
                                'Chalk': {'val':[10, 5.2]},
                                'Sandstone':{'val':[8, 5.2]},
                                'Clay':{'val':[2, 5.2]},
                                'Limestone':{'val':[4, 5.2]}
                                })
        test2, csp2 = chi_square_from_Dict2D(test_matrix_2)
        self.assertFloatEqual(test2, 10.1538461538)
        self.assertFloatEqual(csp2, 0.0379143890013)
        #test3
        matrix3_obs = Dict2D({'AIDS':{'Males':4, 'Females':2, 'Both':3},
                        'No_AIDS':{'Males':3, 'Females':16, 'Both':2}
                       })
        matrix3 = calc_contingency_expected(matrix3_obs)
        test3, csp3 = chi_square_from_Dict2D(matrix3)
        self.assertFloatEqual(test3, 7.6568405139833722)
        self.assertFloatEqual(csp3, 0.0217439383468)

class LikelihoodTests(TestCase):
    """Tests implementations of likelihood calculations."""

    def test_likelihoods_unequal_list_lengths(self):
        """likelihoods should raise ValueError if input lists unequal length"""
        self.assertRaises(ValueError, likelihoods, [1, 2], [1])

    def test_likelihoods_equal_priors(self):
        """likelihoods should equal Pr(D|H) if priors the same"""
        equal = [0.25, 0.25, 0.25,0.25]
        unequal = [0.5, 0.25, 0.125, 0.125]
        equal_answer = [1, 1, 1, 1]
        unequal_answer = [2, 1, 0.5, 0.5]
        for obs, exp in zip(likelihoods(equal, equal), equal_answer):
            self.assertFloatEqual(obs, exp)

        for obs, exp in zip(likelihoods(unequal, equal), unequal_answer):
            self.assertFloatEqual(obs, exp)

    def test_likelihoods_equal_evidence(self):
        """likelihoods should return vector of 1's if evidence equal for all"""
        equal = [0.25, 0.25, 0.25,0.25]
        unequal = [0.5, 0.25, 0.125, 0.125]
        equal_answer = [1, 1, 1, 1]
        unequal_answer = [2, 1, 0.5, 0.5]
        not_unity = [0.7, 0.7, 0.7, 0.7]
        
        for obs, exp in zip(likelihoods(equal, unequal), equal_answer):
            self.assertFloatEqual(obs, exp)

        #should be the same if evidences don't sum to 1
        for obs, exp in zip(likelihoods(not_unity, unequal), equal_answer):
            self.assertFloatEqual(obs, exp)

    def test_likelihoods_unequal_evidence(self):
        """likelihoods should update based on weighted sum if evidence unequal"""
        not_unity = [1, 0.5, 0.25, 0.25]
        unequal = [0.5, 0.25, 0.125, 0.125]
        products = [1.4545455, 0.7272727, 0.3636364, 0.3636364]

        #if priors and evidence both unequal, likelihoods should change
        #(calculated using StarCalc)
        for obs, exp in zip(likelihoods(not_unity, unequal), products):
            self.assertFloatEqual(obs, exp)
        
    def test_posteriors_unequal_lists(self):
        """posteriors should raise ValueError if input lists unequal lengths"""
        self.assertRaises(ValueError, posteriors, [1, 2, 3], [1])

    def test_posteriors_good_data(self):
        """posteriors should return products of paired list elements"""
        first = [0, 0.25, 0.5, 1, 0.25]
        second = [0.25, 0.5, 0, 0.1, 1]
        product = [0, 0.125, 0, 0.1, 0.25]
        for obs, exp in zip(posteriors(first, second), product):
            self.assertFloatEqual(obs, exp)

class BayesUpdateTests(TestCase):
    """Tests implementation of Bayes calculations"""

    def setUp(self):
        first = [0.25, 0.25, 0.25]
        second = [0.1, 0.75, 0.3]
        third = [0.95, 1e-10, 0.2]
        fourth = [0.01, 0.9, 0.1]
        bad = [1, 2, 1, 1, 1]
        self.bad = [first, bad, second, third]
        self.test = [first, second, third, fourth]
        self.permuted = [fourth, first, third, second]
        self.deleted = [second, fourth, third]
        self.extra = [first, second, first, third, first, fourth, first]

        #BEWARE: low precision in second item, so need to adjust threshold
        #for assertFloatEqual accordingly (and use assertFloatEqualAbs).
        self.result = [0.136690646154, 0.000000009712, 0.863309344133]
       
    def test_bayes_updates_bad_data(self):
        """bayes_updates should raise ValueError on unequal-length lists"""
        self.assertRaises(ValueError, bayes_updates, self.bad)

    def test_bayes_updates_good_data(self):
        """bayes_updates should match hand calculations of probability updates"""
        #result for first -> fourth calculated by hand
        for obs, exp in zip(bayes_updates(self.test), self.result):
            self.assertFloatEqualAbs(obs, exp, 1e-11)

    def test_bayes_updates_permuted(self):
        """bayes_updates should not be affected by order of inputs"""
        for obs, exp in zip(bayes_updates(self.permuted), self.result):
            self.assertFloatEqualAbs(obs, exp, 1e-11)

    def test_bayes_update_nondiscriminating(self):
        """bayes_updates should be unaffected by extra nondiscriminating data"""
        #deletion of non-discriminating evidence should not affect result
        for obs, exp in zip(bayes_updates(self.deleted), self.result):
            self.assertFloatEqualAbs(obs, exp, 1e-11)
        #additional non-discriminating evidence should not affect result
        for obs, exp in zip(bayes_updates(self.extra), self.result):
            self.assertFloatEqualAbs(obs, exp, 1e-11)
        

class StatTests(TestCase):
    """Tests that the t and z tests are implemented correctly"""

    def setUp(self):
        self.x = [   
                7.33, 7.49, 7.27, 7.93, 7.56,
                7.81, 7.46, 6.94, 7.49, 7.44,
                7.95, 7.47, 7.04, 7.10, 7.64,
            ]

        self.y = [   
                7.53, 7.70, 7.46, 8.21, 7.81,
                8.01, 7.72, 7.13, 7.68, 7.66,
                8.11, 7.66, 7.20, 7.25, 7.79,
            ]


    def test_t_paired_2tailed(self):
        """t_paired should match values from Sokal & Rohlf p 353"""
        x, y = self.x, self.y
        #check value of t and the probability for 2-tailed
        self.assertFloatEqual(t_paired(y, x)[0], 19.7203, 1e-4)
        self.assertFloatEqual(t_paired(y, x)[1], 1.301439e-11, 1e-4)

    def test_t_paired_no_variance(self):
        """t_paired should return None if lists are invariant"""
        x = [1, 1, 1]
        y = [0, 0, 0]
        self.assertEqual(t_paired(x,x), (None, None))
        self.assertEqual(t_paired(x,y), (None, None))
        
    def test_t_paired_1tailed(self):
        """t_paired should match pre-calculated 1-tailed values"""
        x, y = self.x, self.y
        #check probability for 1-tailed low and high
        self.assertFloatEqual(
            t_paired(y, x, "low")[1], 1-(1.301439e-11/2), 1e-4)
        self.assertFloatEqual(
            t_paired(x, y, "high")[1], 1-(1.301439e-11/2), 1e-4)
        self.assertFloatEqual(
            t_paired(y, x, "high")[1], 1.301439e-11/2, 1e-4)
        self.assertFloatEqual(
            t_paired(x, y, "low")[1], 1.301439e-11/2, 1e-4)

    def test_t_paired_specific_difference(self):
        """t_paired should allow a specific difference to be passed"""
        x, y = self.x, self.y
        #difference is 0.2, so test should be non-significant if 0.2 passed
        self.failIf(t_paired(y, x, exp_diff=0.2)[0] > 1e-10)
        #same, except that reversing list order reverses sign of difference
        self.failIf(t_paired(x, y, exp_diff=-0.2)[0] > 1e-10)
        #check that there's no significant difference from the true mean
        self.assertFloatEqual(
            t_paired(y, x,exp_diff=0.2)[1], 1, 1e-4)
            
    def test_t_paired_bad_data(self):
        """t_paired should raise ValueError on lists of different lengths"""
        self.assertRaises(ValueError, t_paired, self.y, [1, 2, 3])

    def test_t_two_sample(self):
        """t_two_sample should match example on p.225 of Sokal and Rohlf"""
        I =  Numbers([7.2, 7.1, 9.1, 7.2, 7.3, 7.2, 7.5])
        II = Numbers([8.8, 7.5, 7.7, 7.6, 7.4, 6.7, 7.2])
        self.assertFloatEqual(t_two_sample(I, II), (-0.1184, 0.45385 * 2), 
            0.001)

    def test_t_two_sample_no_variance(self):
        """t_two_sample should return None if lists are invariant"""
        x = Numbers([1, 1, 1])
        y = Numbers([0, 0, 0])
        self.assertEqual(t_two_sample(x,x), (None, None))
        self.assertEqual(t_two_sample(x,y), (None, None))

    def test_t_one_sample(self):
        """t_one_sample results should match those from R"""
        x = Numbers(range(-5,5))
        y = Numbers(range(-1,10))
        self.assertFloatEqualAbs(t_one_sample(x), (-0.5222, 0.6141), 1e-4)
        self.assertFloatEqualAbs(t_one_sample(y), (4, 0.002518), 1e-4)
        #do some one-tailed tests as well
        self.assertFloatEqualAbs(t_one_sample(y, tails='low'),(4, 0.9987),1e-4)
        self.assertFloatEqualAbs(t_one_sample(y,tails='high'),(4,0.001259),1e-4)
   
    def test_t_two_sample_switch(self):
        """t_two_sample should call t_one_observation if 1 item in sample."""
        sample = Numbers([4.02, 3.88, 3.34, 3.87, 3.18])
        x = Numbers([3.02])
        self.assertFloatEqual(t_two_sample(x,sample),(-1.5637254,0.1929248))
        self.assertFloatEqual(t_two_sample(sample, x),(-1.5637254,0.1929248))
        #can't do the test if both samples have single item
        self.assertEqual(t_two_sample(x,x), (None, None))
   
    def test_t_one_observation(self):
        """t_one_observation should match p. 228 of Sokal and Rohlf"""
        sample = Numbers([4.02, 3.88, 3.34, 3.87, 3.18])
        x = 3.02
        #note that this differs after the 3rd decimal place from what's in the
        #book, because Sokal and Rohlf round their intermediate steps...
        self.assertFloatEqual(t_one_observation(x,sample),\
            (-1.5637254,0.1929248))
    
    def test_reverse_tails(self):
        """reverse_tails should return 'high' if tails was 'low' or vice versa"""
        self.assertEqual(reverse_tails('high'), 'low')
        self.assertEqual(reverse_tails('low'), 'high')
        self.assertEqual(reverse_tails(None), None)
        self.assertEqual(reverse_tails(3), 3)

    def test_tail(self):
        """tail should return prob/2 if test is true, or 1-(prob/2) if false"""
        self.assertFloatEqual(tail(0.25, True), 0.125)
        self.assertFloatEqual(tail(0.25, False), 0.875)
        self.assertFloatEqual(tail(1, True), 0.5)
        self.assertFloatEqual(tail(1, False), 0.5)
        self.assertFloatEqual(tail(0, True), 0)
        self.assertFloatEqual(tail(0, False), 1)

    def test_z_test(self):
        """z_test should give correct values"""
        sample = Numbers([1,2,3,4,5])
        self.assertFloatEqual(z_test(sample, 3, 1), (0,1))
        self.assertFloatEqual(z_test(sample, 3, 2, 'high'), (0,0.5))
        self.assertFloatEqual(z_test(sample, 3, 2, 'low'), (0,0.5))
        #check that population mean and variance, and tails, can be set OK.
        self.assertFloatEqual(z_test(sample, 0, 1), (6.7082039324993694, \
            1.9703444711798951e-11))
        self.assertFloatEqual(z_test(sample, 1, 10), (0.44721359549995793, \
            0.65472084601857694))
        self.assertFloatEqual(z_test(sample, 1, 10, 'high'), \
            (0.44721359549995793, 0.65472084601857694/2))
        self.assertFloatEqual(z_test(sample, 1, 10, 'low'), \
            (0.44721359549995793, 1-(0.65472084601857694/2)))
    
class CorrelationTests(TestCase):
    """Tests of correlation coefficients."""
    def test_correlation(self):
        """Correlations and significance should match R's cor.test()"""
        x = [1,2,3,5]
        y = [0,0,0,0]
        z = [1,1,1,1]
        a = [2,4,6,8]
        b = [1.5, 1.4, 1.2, 1.1]
        c = [15, 10, 5, 20]

        bad = [1,2,3]   #originally gave r = 1.0000000002
        
        self.assertFloatEqual(correlation(x,x), (1, 0))
        self.assertFloatEqual(correlation(x,y), (0,1))
        self.assertFloatEqual(correlation(y,z), (0,1))
        self.assertFloatEqualAbs(correlation(x,a), (0.9827076, 0.01729), 1e-5)
        self.assertFloatEqualAbs(correlation(x,b), (-0.9621405, 0.03786), 1e-5)
        self.assertFloatEqualAbs(correlation(x,c), (0.3779645, 0.622), 1e-3)
        self.assertEqual(correlation(bad,bad), (1, 0))

    def test_correlation_matrix(self):
        """Correlations in matrix should match values from R"""
        a = [2,4,6,8]
        b = [1.5, 1.4, 1.2, 1.1]
        c = [15, 10, 5, 20]
        m = correlation_matrix([a,b,c])
        self.assertFloatEqual(m[0], [1.0])
        self.assertFloatEqual(m[1], [correlation(b,a)[0], 1.0])
        self.assertFloatEqual(m[2], [correlation(c,a)[0], correlation(c,b)[0], \
            1.0])


class Ftest(TestCase):
    """Tests for the F test"""

    def test_f_value(self):
        """f_value: should calculate the correct F value if possible"""
        a = Numbers([1,3,5,7,9,8,6,4,2])
        b = Numbers([5,4,6,3,7,6,4,5])
        self.assertEqual(f_value(a,b), (8,7,4.375))
        self.assertFloatEqual(f_value(b,a), (7,8,0.2285714))
        empty = Numbers()
        too_short = Numbers([4])
        self.assertRaises(ValueError, f_value, a, empty)
        self.assertRaises(ValueError, f_value, too_short, b)
    
    def test_f_two_sample(self):
        """f_two_sample should match values from R""" 
        
        #The expected values in this test are obtained through R.
        #In R the F test is var.test(x,y) different alternative hypotheses
        #can be specified (two sided, less, or greater).
        #The vectors are random samples from a particular normal distribution
        #(mean and sd specified).
        
        #a: 50 elem, mean=0 sd=1
        a = [-0.70701689, -1.24788845, -1.65516470,  0.10443876, -0.48526915, 
        -0.71820656, -1.02603596,  0.03975982, -2.23404324, -0.21509363,  
        0.08438468, -0.01970062, -0.67907971, -0.89853667,  1.11137131,  
        0.05960496, -1.51172084, -0.79733957, -1.60040659,  0.80530639, 
        -0.81715836, -0.69233474,  0.95750665,  0.99576429, -1.61340216,
        -0.43572590, -1.50862327,  0.92847551, -0.68382338, -1.12523522,
        -0.09147488,  0.66756023, -0.87277588, -1.36539039, -0.11748707, 
        -1.63632578, -0.31343078, -0.28176086,  0.33854483, -0.51785630, 
        2.25360559, -0.80761191, 1.18983499,  0.57080342, -1.44601700, 
        -0.53906955, -0.01975266, -1.37147915, -0.31537616,  0.26877544]

        #b: 50 elem, mean=0, sd=1.2
        b=[0.081418743,  0.276571612, -1.864316504,  0.675213612, -0.769202643,
         0.140372825, -1.426250184,  0.058617884, -0.819287409, -0.007701916,
        -0.782722020, -0.285891593,  0.661980419,  0.383225191,  0.622444946,
        -0.192446150,  0.297150571,  0.408896059, -0.167359383, -0.552381362,
         0.982168338,  1.439730446,  1.967616101, -0.579607307,  1.095590943,
         0.240591302, -1.566937143, -0.199091349, -1.232983905,  0.362378169,
         1.166061081, -0.604676222, -0.536560206, -0.303117595,  1.519222792,
        -0.319146503,  2.206220810, -0.566351124, -0.720397392, -0.452001377,
         0.250890097,  0.320685395, -1.014632725, -3.010346273, -1.703955054,
         0.592587381, -1.237451255,  0.172243366, -0.452641122, -0.982148581]
       
        #c: 60 elem, mean=5, sd=1
        c=[4.654329, 5.242129, 6.272640, 5.781779, 4.391241, 3.800752, 
        4.559463, 4.318922, 3.243020, 5.121280, 4.126385, 5.541131, 
        4.777480, 5.646913, 6.972584, 3.817172, 6.128700, 4.731467, 
        6.762068, 5.082983, 5.298511, 5.491125, 4.532369, 4.265552,
        5.697317, 5.509730, 2.935704, 4.507456, 3.786794, 5.548383, 
        3.674487, 5.536556, 5.297847, 2.439642, 4.759836, 5.114649, 
        5.986774, 4.517485, 4.579208, 4.579374, 2.502890, 5.190955, 
        5.983194, 6.766645, 4.905079, 4.214273, 3.950364, 6.262393,
        8.122084, 6.330007, 4.767943, 5.194029, 3.503136, 6.039079, 
        4.485647, 6.116235, 6.302268, 3.596693, 5.743316, 6.860152]

        #d: 30 elem, mean=0, sd =0.05 
        d=[ 0.104517366,  0.023039678,  0.005579091,  0.052928250,  0.020724823,
        -0.060823243, -0.019000890, -0.064133996, -0.016321594, -0.008898334,
        -0.027626992, -0.051946186,  0.085269587, -0.031190678,  0.065172938,
        -0.054628573,  0.019257306, -0.032427056, -0.058767356,  0.030927400,
         0.052247357, -0.042954937,  0.031842104,  0.094130522, -0.024828465,
         0.011320453, -0.016195062,  0.015631245, -0.050335598, -0.031658335]

        a,b,c,d = map(Numbers,[a,b,c,d])
        self.assertEqual(map(len,[a,b,c,d]), [50, 50, 60, 30])
        
        #allowed error. This big, because results from R 
        #are rounded at 4 decimals
        error = 1e-4 
                
        self.assertFloatEqual(f_two_sample(a,a), (49, 49, 1, 1), eps=error)
        self.assertFloatEqual(f_two_sample(a,b), (49, 49, 0.8575, 0.5925),
            eps=error)
        self.assertFloatEqual(f_two_sample(b,a), (49, 49, 1.1662, 0.5925),
            eps=error)
        self.assertFloatEqual(f_two_sample(a,b, tails='low'),
            (49, 49, 0.8575, 0.2963), eps=error)
        self.assertFloatEqual(f_two_sample(a,b, tails='high'), 
            (49, 49, 0.8575, 0.7037), eps=error)
        self.assertFloatEqual(f_two_sample(a,c),
            (49, 59, 0.6587, 0.1345), eps=error)
        #p value very small, so first check df's and F value
        self.assertFloatEqualAbs(f_two_sample(d,a, tails='low')[0:3],
            (29, 49, 0.0028), eps=error)
        assert f_two_sample(d,a, tails='low')[3] < 2.2e-16 #p value


    def test_MonteCarloP(self):
        """MonteCarloP  calcs a p-value from a val and list of random vals"""
        val = 3.0
        random_vals = [0.0,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0]

        #test for "high" tail (larger values than expected by chance)
        p_val = MonteCarloP(val, random_vals, 'high')
        self.assertEqual(p_val, 0.7)

        #test for "low" tail (smaller values than expected by chance)
        p_val = MonteCarloP(val, random_vals, 'low')
        self.assertEqual(p_val, 0.4)


#execute tests if called from command line
if __name__ == '__main__':
    main()
