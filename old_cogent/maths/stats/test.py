#!/usr/bin/env python
#file evo/stats/test.py

"""Provides standard statistical tests. Tests produce statistic and P-value.

Owner: Rob Knight rob@spot.colorado.edu

Status: Stable

Revision History

3/03 Rob Knight: written, mostly using Gary Strangman's stats.py

4/14-28/03 Rob Knight: rewritten to eliminate dependence on Gary Strangman's
stats module: the probability calculations were not accurate in the required
range. Now uses stats functions translated from Cephes. Also cleaned up
docstrings to match guidelines.

5/7/03 Rob Knight: made t and Gfit tests more robust (now return sensible
results if there is no variation or if some of the observeds are zero,
instead of raising errors).
Cleaned up G_2_by_2 to use loops instead of redudant code.

5/8/03 Rob Knight: adjusted docstrings to separate Usage more clearly.

6/15/03 Rob Knight: trapped ZeroDivisionError in bayes_updates.

8/4/03 Rob Knight: added correlation and correlation_matrix. Changed module 
name. Changed tests to use the Statistics interface.

8/7/03 Rob Knight: changed most of the t test method names and consolidated the
tail handling in one place. Added the single-value t test. Simplified 
handling of bad data (i.e. cases where t is undefined): now returns 
(None, None) instead of a spurious result, so check for this in client and 
treat accordingly.

8/21/03 Rob Knight: added combinations and multiple_comparisons.

9/17/03 Rob Knight: moved log_one_minus and one_minus_exp to special. Renamed
functions with underscore convention.

10/14/03 Rob Knight: changed imports.

11/1/03 Rob Knight: changed multiple_comparisons to use one_minus_exp (greatly
improves accuracy when p is small). Added multiple_inverse and multiple_n.

11/10/03 Rob Knight: added regression and Fisher's method for combining 
probabilities.

12/16/03 Rob Knight: correlation now explicitly checks that r is within +/- 1 
(and rounds off if necessary), since some lists gave out-of-bounds values for
r (notably, [1,2,3] correlated against itself gave 1.000000002).

2/15/05 Sandra Smit: added f_value and f_two_sample as implementation of 
the F test.

3/25/05 Micah Hamady: changed fishers to return 0.0 when one of pvalues is zero
instead of raising an exception.

5/23/05 Cathy Lozupone: added calc_contingency_expected, G_fit_from_Dict2D,
chi_square_from_Dict2D, and MonteCarloP

1/26/06 Cathy Lozupone: added regress residuals

1/27/06 Cathy Lozupone: added stddev_from_mean

2/2/06 Cathy Lozupone: added regress_R2

2/2/06 Rob Knight: added G_ind for general arrays.
"""
from __future__ import division
from old_cogent.maths.stats.distribution import chi_high, z_low, z_high, zprob, \
     t_high, t_low, tprob, f_high, f_low, fprob
from old_cogent.maths.stats.special import lgam, log_one_minus, one_minus_exp
from old_cogent.base.stats import Numbers
from old_cogent.base.dict2d import Dict2D

from operator import add
from Numeric import sqrt, log, exp, ravel, nonzero, take, sum

class ZeroExpectedError(ValueError):
    """Class for handling tests where an expected value was zero."""
    pass
   
def G_2_by_2(a, b, c, d, williams=1, directional=1):
    """G test for independence in a 2 x 2 table.

    Usage: G, prob = G_2_by_2(a, b, c, d, willliams, directional)

    Cells are in the order:
    
        a b
        c d
    
    a, b, c, and d can be int, float, or long.
    williams is a boolean stating whether to do the Williams correction.
    directional is a boolean stating whether the test is 1-tailed.
    
    Briefly, computes sum(f ln f) for cells - sum(f ln f) for
    rows and columns + f ln f for the table.
    
    Always has 1 degree of freedom

    To generalize the test to r x c, use the same protocol:
    2*(cells - rows/cols + table), then with (r-1)(c-1) df.

    Note that G is always positive: to get a directional test,
    the appropriate ratio (e.g. a/b > c/d) must be tested
    as a separate procedure. Find the probability for the
    observed G, and then either halve or halve and subtract from
    one depending on whether the directional prediction was
    upheld. 
    
    The default test is now one-tailed (Rob Knight 4/21/03).

    See Sokal & Rohlf (1995), ch. 17. Specifically, see box 17.6 (p731).
    """
    cells = [a, b, c, d]
    n = sum(cells)
    #return 0 if table was empty
    if not n:
        return (0, 1)
    #raise error if any counts were negative
    if min(cells) < 0:
        raise ValueError, \
        "G_2_by_2 got negative cell counts(s): must all be >= 0."
    
    G = 0
    #Add x ln x for items, adding zero for items whose counts are zero
    for i in filter(None, cells):
        G += i * log(i)
    #Find totals for rows and cols
    ab = a + b
    cd = c + d
    ac = a + c
    bd = b + d
    rows_cols = [ab, cd, ac, bd]
    #exit if we are missing a row or column entirely: result counts as
    #never significant
    if min(rows_cols) == 0:
        return (0, 1)
    #Subtract x ln x for rows and cols
    for i in filter(None, rows_cols):
        G -= i * log(i)
    #Add x ln x for table
    G += n * log(n) 
    #Result needs to be multiplied by 2 
    G *= 2

    #apply Williams correction
    if williams:
        q = 1 + ((  ( (n/ab) + (n/cd) ) -1 ) * ( ( (n/ac) + (n/bd) ) -1))/(6*n)
        G /= q

    p = chi_high(max(G,0), 1)
    
    #find which tail we were in if the test was directional
    if directional:
        is_high =  ((b == 0) or (d != 0 and (a/b > c/d)))
        p = tail(p, is_high)
        if not is_high:
            G = -G
    return G, p

def safe_sum_p_log_p(a, base=None):
    """Calculates p * log(p) safely for an array that may contain zeros."""
    flat = ravel(a)
    nz = take(flat, nonzero(flat))
    logs = log(nz)
    if base:
        logs /= log(base)
    return sum(nz * logs)
    

def G_ind(m, williams=False):
    """Returns G test for independence in an r x c table.
    
    Requires input data as a Numeric array. From Sokal and Rohlf p 738.
    """
    f_ln_f_elements = safe_sum_p_log_p(m)
    f_ln_f_rows = safe_sum_p_log_p(sum(m))
    f_ln_f_cols = safe_sum_p_log_p(sum(m,1))
    tot = sum(ravel(m))
    f_ln_f_table = tot * log(tot)

    df = (len(m)-1) * (len(m[0])-1)
    G = 2*(f_ln_f_elements-f_ln_f_rows-f_ln_f_cols+f_ln_f_table)
    if williams:
        q = 1+((tot*sum(1.0/sum(m,1))-1)*(tot*sum(1.0/sum(m))-1)/ \
            (6*tot*df))
        G = G/q
    return G, chi_high(max(G,0), df)

def calc_contingency_expected(matrix):
        """Calculates expected frequencies from a table of observed frequencies

        The input matrix is a dict2D object and represents a frequency table
        with different variables in the rows and columns. (observed
        frequencies as values)
                                
        The expected value is calculated with the following equation:
            Expected = row_total x column_total / overall_total
                                            
        The returned matrix (dict2D) has lists of the observed and the 
        expected frequency as values
        """
        #transpose matrix for calculating column totals
        t_matrix = matrix.copy()
        t_matrix.transpose()

        overall_total = sum(list(matrix.Items))
        #make new matrix for storing results
        result = matrix.copy()

        #populate result with expected values
        for row in matrix:
            row_sum = sum(matrix[row].values())
            for item in matrix[row]:
                column_sum = sum(t_matrix[item].values())
                #calculate expected frequency
                Expected = (row_sum * column_sum)/overall_total
                result[row][item] = [result[row][item]]
                result[row][item].append(Expected)
        return result

def G_fit(obs, exp, williams=1):
    """G test for fit between two lists of counts.

    Usage: test, prob = G_fit(obs, exp, williams)
    
    obs and exp are two lists of numbers.
    williams is a boolean stating whether to do the Williams correction.
    
    SUM(2 f(obs)ln (f(obs)/f(exp)))
    
    See Sokal and Rohlf chapter 17.
    """
    k = len(obs)
    if k != len(exp):
        raise ValueError, "G_fit requires two lists of equal length."
    G = 0
    n = 0
    
    for o, e in zip(obs, exp):
        if o < 0:
            raise ValueError, \
            "G_fit requires all observed values to be positive."
        if e <= 0:
            raise ZeroExpectedError, \
            "G_fit requires all expected values to be positive."
        if o:   #if o is zero, o * log(o/e) must be zero as well.
            G += o * log(o/e)
            n += o
    
    G *= 2
    if williams:
        q = 1 + (k + 1)/(6*n)
        G /= q

    return G, chi_high(G, k - 1)

def G_fit_from_Dict2D(data):
    """G test for fit on a Dict2D

    data is a dict2D. Values are a list containing the observed
    and expected frequencies (can be created with calc_contingency_expected)
    """
    obs_counts = []
    exp_counts = []
    for item in data.Items:
        if len(item) == 2:
		obs_counts.append(item[0])
		exp_counts.append(item[1])
    g_val, prob = G_fit(obs_counts, exp_counts)
    return g_val, prob

def chi_square_from_Dict2D(data):
    """Chi Square test on a Dict2D

    data is a Dict2D. The values are a list of the observed (O)
    and expected (E) frequencies,(can be created with calc_contingency_expected)

    The chi-square value (test) is the sum of (O-E)^2/E over the items in data

    degrees of freedom are calculated from data as:
    (r-1)*(c-1) if cols and rows are both > 1
    otherwise is just 1 - the # of rows or columns
    (whichever is greater than 1)
    
    """
    test =  sum([((item[0] - item[1]) * (item[0] - item[1]))/item[1] \
                   for item in data.Items])
    num_rows = len(data)
    num_cols = len([col for col in data.Cols])
    if num_rows == 1:
        df = num_cols - 1
    elif num_cols == 1:
        df = num_rows - 1
    elif num_rows == 0 or num_cols == 0:
        raise ValueError, "data matrix must have data"
    else:
        df = (len(data) - 1) * (len([col for col in data.Cols]) - 1)
    
    return test, chi_high(test, df)
    

def likelihoods(d_given_h, priors):
    """Calculate likelihoods through marginalization, given Pr(D|H) and priors.

    Usage: scores = likelihoods(d_given_h, priors)

    d_given_h and priors are equal-length lists of probabilities. Returns
    a list of the same length of numbers (not probabilities).
    """
    #check that the lists of Pr(D|H_i) and priors are equal
    length = len(d_given_h)
    if length != len(priors):
        raise ValueError, "Lists not equal lengths."
    #find weighted sum of Pr(H_i) * Pr(D|H_i)
    wt_sum = 0
    for d, p in zip(d_given_h, priors):
        wt_sum += d * p
    #divide each Pr(D|H_i) by the weighted sum and multiply by its prior
    #to get its likelihood
    return [d/wt_sum for d in d_given_h]

def posteriors(likelihoods, priors):
    """Calculate posterior probabilities given priors and likelihoods.

    Usage: probabilities = posteriors(likelihoods, priors)

    likelihoods is a list of numbers. priors is a list of probabilities.
    Returns a list of probabilities (0-1).
    """
    #Check that there is a prior for each likelihood
    if len(likelihoods) != len(priors):
        raise ValueError, "Lists not equal lengths."
    #Posterior probability is defined as prior * likelihood
    return [l * p for l, p in zip(likelihoods, priors)]

def bayes_updates(ds_given_h, priors = None):
    """Successively apply lists of Pr(D|H) to get Pr(H|D) by marginalization.

    Usage: final_probs = bayes_updates(ds_given_h, [priors])

    ds_given_h is a list (for each form of evidence) of lists of probabilities.
    priors is optionally a list of the prior probabilities.
    Returns a list of posterior probabilities.
    """
    try:
        first_list = ds_given_h[0]
        length = len(first_list)
        #calculate flat prior if none was passed
        if not priors:
            priors = [1/length] * length
        #apply each form of data to the priors to get posterior probabilities
        for index, d in enumerate(ds_given_h):
            #first, ignore the form of data if all the d's are the same
            all_the_same = True
            first_element = d[0]
            for i in d:
                if i != first_element:
                    all_the_same = False
                    break
            if not all_the_same:    #probabilities won't change
                if len(d) != length:
                    raise ValueError, "bayes_updates requires equal-length lists."
                liks = likelihoods(d, priors)
                pr = posteriors(liks, priors)
                priors = pr
        return priors #posteriors after last calculation are 'priors' for next
    #return column of zeroes if anything went wrong, e.g. if the sum of one of
    #the ds_given_h is zero.
    except ZeroDivisionError:
        return [0] * length

def t_paired (a,b, tails=None, exp_diff=0):
    """Returns t and prob for TWO RELATED samples of scores a and b.  
    
    From Sokal and Rohlf (1995), p. 354.
    Calculates the vector of differences and compares it to exp_diff
    using the 1-sample t test.

    Usage:   t, prob = t_paired(a, b, tails, exp_diff)
    
    t is a float; prob is a probability.
    a and b should be equal-length lists of paired observations (numbers).
    tails should be None (default), 'high', or 'low'.
    exp_diff should be the expected difference in means (a-b); 0 by default.
    """
    n = len(a)
    if n != len(b):
        raise ValueError, 'Unequal length lists in ttest_paired.'
    try:
        diffs = Numbers([a_i - b_i for a_i, b_i in zip(a, b)])
        return t_one_sample(diffs, popmean=exp_diff, tails=tails)
    except (ZeroDivisionError, ValueError, AttributeError, TypeError):
        return (None, None)

def t_one_sample(a,popmean=0, tails=None):
    """Returns t for ONE group of scores a, given a population mean.

    Usage:   t, prob = t_one_sample(a, popmean, tails)

    t is a float; prob is a probability.
    a should support Mean, StandardDeviation, and Count.
    popmean should be the expected mean; 0 by default.
    tails should be None (default), 'high', or 'low'.
"""
    try:
        n = a.Count
        t = (a.Mean - popmean)/(a.StandardDeviation/sqrt(n))
    except (ZeroDivisionError, ValueError, AttributeError, TypeError):
        return None, None
    prob = t_tailed_prob(t, n-1, tails)
    return t, prob


def t_two_sample (a, b, tails=None, exp_diff=0):
    """Returns t, prob for two INDEPENDENT samples of scores a, and b.  
    
    From Sokal and Rohlf, p 223.  

    Usage:   t, prob = t_two_sample(a,b, tails, exp_diff)

    t is a float; prob is a probability.
    a and b should be lists of observations (numbers) supporting Mean, Count,
    and Variance. Need not be equal.
    tails should be None (default), 'high', or 'low'.
    exp_diff should be the expected difference in means (a-b); 0 by default.
 """
    try:
        #see if we need to back off to the single-observation for single-item
        #groups
        n1 = a.Count
        if n1 < 2:
            return t_one_observation(a.Sum, b, tails, exp_diff)
        n2 = b.Count
        if n2 < 2:
            return t_one_observation(b.Sum, a, reverse_tails(tails), exp_diff)
        #otherwise, calculate things properly
        x1 = a.Mean
        x2 = b.Mean
        df = n1+n2-2
        svar = ((n1-1)*a.Variance + (n2-1)*b.Variance)/df
        t = (x1-x2-exp_diff)/sqrt(svar*(1/n1 + 1/n2))
    except (ZeroDivisionError, ValueError, AttributeError, TypeError):
        #bail out if the sample sizes are wrong, the values aren't numeric or
        #aren't present, etc.
        return (None, None)
    prob = t_tailed_prob(t, df, tails)
    return t, prob

def t_one_observation(x, sample, tails=None, exp_diff=0):
    """Returns t-test for significance of single observation versus a sample.
    
    Equation for 1-observation t (Sokal and Rohlf 1995 p 228):
    t = obs - mean - exp_diff / (var * sqrt((n+1)/n)) 
    df = n - 1
    """
    try:
        n = sample.Count
        t = (x - sample.Mean - exp_diff)/sample.StandardDeviation/sqrt((n+1)/n)
    except (ZeroDivisionError, ValueError, AttributeError, TypeError):
        return (None, None)
    prob = t_tailed_prob(t, n-1, tails)
    return t, prob
    
def correlation(x_items, y_items):
    """Returns Pearson correlation between x and y, and its significance."""
    sum_x = sum_y = sum_x_sq = sum_y_sq = sum_xy = n = 0
    for x, y in zip(x_items, y_items):
        n += 1
        sum_x += x
        sum_x_sq += x * x
        sum_y += y
        sum_y_sq += y * y
        sum_xy += x * y
    try:
        r = 1.0 * ((n * sum_xy) - (sum_x * sum_y)) / \
           (sqrt((n * sum_x_sq)-(sum_x*sum_x))*sqrt((n*sum_y_sq)-(sum_y*sum_y)))
    except (ZeroDivisionError, ValueError): #no variation
        r = 0.0
    #check we didn't get a naughty value for r due to rounding error
    if r > 1.0:
        r = 1.0
    elif r < -1.0:
        r = -1.0
    if n < 3:
        prob = 1
    else:
        try:
            t = r/sqrt((1 - (r*r))/(n-2))
            prob = tprob(t, n-2)
        except ZeroDivisionError: #r was presumably 1
            prob = 0
    return (r, prob)

def correlation_matrix(lists):
    """Returns pairwise correlations between each pair of lists."""
    num_lists = len(lists)
    result = []
    for x in range(num_lists):
        row = []
        for y in range(x+1):
            if y == x:
                row.append(1)
            else:
                row.append(correlation(lists[x],lists[y])[0]) 
                #just correl, not prob
        result.append(row)
    return result

def regress(x, y):
    """Returns coefficients to the regression line "y=ax+b" from x[] and y[].  

    Specifically, returns (slope, intercept) as a tuple from the regression of 
    y on x, minimizing the error in y assuming that x is precisely known.

    Basically, it solves 
        Sxx a + Sx b = Sxy
         Sx a +  N b = Sy
    where Sxy = \sum_i x_i y_i, Sx = \sum_i x_i, and Sy = \sum_i y_i.  The
    solution is
        a = (Sxy N - Sy Sx)/det
        b = (Sxx Sy - Sx Sxy)/det
    where det = Sxx N - Sx^2.  In addition,
        Var|a| = s^2 |Sxx Sx|^-1 = s^2 | N  -Sx| / det
           |b|       |Sx  N |          |-Sx Sxx|
        s^2 = {\sum_i (y_i - \hat{y_i})^2 \over N-2}
            = {\sum_i (y_i - ax_i - b)^2 \over N-2}
            = residual / (N-2)
        R^2 = 1 - {\sum_i (y_i - \hat{y_i})^2 \over \sum_i (y_i - \mean{y})^2}
            = 1 - residual/meanerror

    Adapted from the following URL:
    http://www.python.org/topics/scicomp/recipes_in_python.html
    """
    coords = zip(x, y)
    N = len(coords)
    Sx = Sy = Sxx = Syy = Sxy = 0.0
    for x, y in coords:
        Sx += x
        Sy += y
        Sxx += x*x
        Syy += y*y
        Sxy += x*y
    det = Sxx * N - Sx * Sx
    return (Sxy * N - Sy * Sx)/det, (Sxx * Sy - Sx * Sxy)/det

def regress_origin(x,y):
    """Returns coefficients to regression "y=ax+b" passing through origin.

    Requires vectors x and y of same length.
    See p. 351 of Zar (1999) Biostatistical Analysis.

    returns slope, intercept as a tuple.
    """
    return sum(x*y)/sum(x*x), 0

def regress_R2(x, y):
    """Returns the R^2 value for the regression of x and y
    
    Used the method explained on pg 334 ofJ.H. Zar, Biostatistical analysis,
    fourth edition. 1999
    """
    slope, intercept = regress(x,y)
    coords = zip(x, y)
    Sx = Sy = Syy = SXY =  0.0
    n = float(len(y))
    for x, y in coords:
        SXY += x*y
        Sx += x
        Sy += y
        Syy += y*y
    Sxy = SXY - (Sx*Sy)/n
    regSS = slope * Sxy
    totSS = Syy - ((Sy*Sy)/n)
    return regSS/totSS

def regress_residuals(x, y):
    """reports the residual (error) for each point from the linear regression"""
    slope, intercept = regress(x, y)
    coords = zip(x, y)
    residuals = []
    for x, y in coords:
        e = y - (slope * x) - intercept
        residuals.append(e)
    return residuals
    
def stddev_from_mean(x):
    """returns num standard deviations from the mean of each val in x[]"""
    x = Numbers(x)
    return [(val-x.Mean)/x.StandardDeviation for val in x]

def regress_major(x, y):
    """Returns major-axis regression line of y on x.

    Use in cases where there is error in both x and y.
    """
    coords = zip(y, x)
    N = len(coords)
    Sy = Sx = Syy = Sxx = Syx = 0.0
    for y, x in coords:
        Sy += y
        Sx += x
        Syy += y*y
        Sxx += x*x
        Syx += y*x
    var_y = (Syy-((Sy*Sy)/N))/(N-1)
    var_x = (Sxx-((Sx*Sx)/N))/(N-1)
    cov = (Syx-((Sy*Sx)/N))/(N-1)
    mean_y = Sy/N
    mean_x = Sx/N
    D = sqrt((var_y + var_x)*(var_y + var_x) - 4*(var_y*var_x - (cov*cov)))
    eigen_1 = (var_y + var_x + D)/2
    slope = cov/(eigen_1 - var_y)
    intercept = mean_y - (mean_x * slope)
    return (slope, intercept)
    

def z_test(a, popmean=0, popstdev=1, tails=None):
    """Returns z and probability score for a single sample of items.

Calculates the z-score on ONE sample of items with mean x, given a population 
mean and standard deviation (parametric).

Usage:   z, prob = z_test(a, popmean, popstdev, tails)

z is a float; prob is a probability.
a is a sample with Mean and Count.
popmean should be the parametric population mean; 0 by default.
popstdev should be the parametric population standard deviation, 1 by default.
tails should be None (default), 'high', or 'low'.
""" 
    try:
        z = (a.Mean - popmean)/popstdev*sqrt(a.Count)
        return z, z_tailed_prob(z, tails)
    except (ValueError, TypeError, ZeroDivisionError, AttributeError):
        return None

def z_tailed_prob(z, tails):
    """Returns appropriate p-value for given z, depending on tails."""
    if tails == 'high':
        return z_high(z)
    elif tails == 'low':
        return z_low(z)
    else:
        return zprob(z)

def t_tailed_prob(t, df, tails):
    """Return appropriate p-value for given t and df, depending on tails."""
    if tails == 'high':
        return t_high(t, df)
    elif tails == 'low':
        return t_low(t, df)
    else:
        return tprob(t,df)

def reverse_tails(tails):
    """Swaps high for low or vice versa, leaving other values alone."""
    if tails == 'high':
        return 'low'
    elif tails == 'low':
        return 'high'
    else:
        return tails

def tail(prob, test):
    """If test is true, returns prob/2. Otherwise returns 1-(prob/2).
    """
    prob /= 2
    if test:
        return prob
    else:
        return 1 - prob

def combinations(n, k):
    """Returns the number of ways of choosing k items from n.
    """
    return exp(lgam(n+1) - lgam(k+1) - lgam(n-k+1))

def multiple_comparisons(p, n):
    """Corrects P-value for n multiple comparisons.
    
    Calculates directly if p is large and n is small; resorts to logs
    otherwise to avoid rounding (1-p) to 1
    """
    if p > 1e-6:   #if p is large and n small, calculate directly
        return 1 - (1-p)**n
    else:   
        return one_minus_exp(-n * p)

def multiple_inverse(p_final, n):
    """Returns p_initial for desired p_final with n multiple comparisons.
    
    WARNING: multiple_inverse is not very reliable when p_final is very close
    to 1 (say, within 1e-4) since we then take the ratio of two very similar
    numbers.
    """
    return one_minus_exp(log_one_minus(p_final)/n)

def multiple_n(p_initial, p_final):
    """Returns number of comparisons such that p_initial maps to p_final.
    
    WARNING: not very accurate when p_final is very close to 1.
    """
    return log_one_minus(p_final)/log_one_minus(p_initial)

def fisher(probs):
    """Uses Fisher's method to combine multiple tests of a hypothesis.

    -2 * SUM(ln(P)) gives chi-squared distribution with 2n degrees of freedom.
    """
    try:
        return chi_high(-2 * sum(map(log, probs)), 2 * len(probs))
    except OverflowError, e:
        return 0.0 

def f_value(a,b):
    """Returns the num df, the denom df, and the F value.

    a, b: lists of values, must have Variance attribute (recommended to
    make them Numbers objects.

    The F value is always calculated by dividing the variance of a by the 
    variance of b, because R uses the same approach. In f_two_value it's 
    decided what p-value is returned, based on the relative sizes of the
    variances. 
    """
    if not a or not b or len(a) <= 1 or len(b) <= 1:
        raise ValueError, "Vectors should contain more than 1 element"
    F = a.Variance/b.Variance
    dfn = a.Count-1
    dfd = b.Count-1
    return dfn, dfd, F


def f_two_sample(a, b, tails=None):
    """Returns the dfn, dfd, F-value and probability for two samples a, and b.

    a and b: should be independent samples of scores. Should be lists of
    observations (numbers) supporting Variance.

    tails should be None(default, two-sided test), 'high' or 'low'.

    This implementation returns the same results as the F test in R.
    """
    dfn, dfd, F = f_value(a, b)
    if tails == 'low':
        return dfn, dfd, F, f_low(dfn, dfd, F)
    elif tails == 'high':
        return dfn, dfd, F, f_high(dfn, dfd, F)
    else:
        if a.Variance >= b.Variance:
            side='right'
        else:
            side='left'
        return dfn, dfd, F, fprob(dfn, dfd, F, side=side)


def MonteCarloP(value, rand_values, tail = 'high'):
    """takes a true value and a list of random values as
        input and returns a p-value

    tail indicates which side of the distribution to look at:
        low = look for smaller values than expected by chance
        high = look for larger values than expected by chance
    """
    pop_size= len(rand_values)
    rand_values.sort()
    if tail == 'high':
        num_better = pop_size
        for i, curr_val in enumerate(rand_values):
            if value <= curr_val:
                num_better = i
                break
        p_val = 1-(num_better / pop_size)
    elif tail == 'low':
        num_better = pop_size
        for i, curr_val in enumerate(rand_values):
            if value < curr_val:
                num_better = i
                break
        p_val = num_better / pop_size
    return p_val
