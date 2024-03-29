#!usr/bin/env python
#metric_scaling.py

"""
Functions for doing principal coordinates analysis on a distance matrix

Calculations performed as described in:

Principles of Multivariate analysis: A User's Perspective. W.J. Krzanowski 
Oxford University Press, 2000. p106.

Revision History:

12-7-05:Cathy Lozupone: wrote code
"""

from Numeric import *
from MLab import eig

def principal_coordinates_analysis(distance_matrix):
    """Takes a distance matrix and returns principal coordinate results

    point_matrix: each row is an axis and the columns are points within the axis
    eigvals: correspond to the rows and indicate the amount of the variation
        that that the axis in that row accounts for
    """
    E_matrix = make_E_matrix(distance_matrix)
    F_matrix = make_F_matrix(E_matrix)
    eigvals, eigvecs = run_eig(F_matrix)
    eigvals = eigvals.real
    eigvecs = eigvecs.real
    point_matrix = get_principal_coordinates(eigvals, eigvecs)

    return point_matrix, eigvals

def make_E_matrix(dist_matrix):
    """takes a distance matrix (dissimilarity matrix) and returns an E matrix

    input and output matrices are Numeric array objects of type Float

    squares and divides by -2 each element in the matrix
    """
    return (dist_matrix * dist_matrix) / -2.0

def make_F_matrix(E_matrix):
    """takes an E matrix and returns an F matrix

    input is output of make_E_matrix

    for each element in matrix subtract mean of corresponding row and 
    column and add the mean of all elements in the matrix
    """
    num_rows, num_cols = shape(E_matrix)
    #make a vector of the means for each row and column
    column_means = add.reduce(E_matrix) / num_rows
    trans_matrix = transpose(E_matrix)
    row_sums = add.reduce(trans_matrix)
    row_means = row_sums / num_cols
    #calculate the mean of the whole matrix
    matrix_mean = sum(row_sums) / (num_rows * num_cols)
    #adjust each element in the E matrix to make the F matrix
    for i, row in enumerate(E_matrix):
        for j, val in enumerate(row):
            E_matrix[i,j] = E_matrix[i,j] - row_means[i] - \
                    column_means[j] + matrix_mean
    return E_matrix

def run_eig(F_matrix):
    """takes an F-matrix and returns eigenvalues and eigenvectors"""

    #use eig to get vector of eigenvalues and matrix of eigenvectors
    #these are already normalized such that
    # vi'vi = 1 where vi' is the transpose of eigenvector i
    eigvals, eigvecs = eig(F_matrix)
    return eigvals, eigvecs

def get_principal_coordinates(eigvals, eigvecs):
    """converts eigvals and eigvecs to point matrix
    
    normalized eigenvectors with eigenvalues"""

    #get the coordinates of the n points on the jth axis of the Euclidean
    #representation as the elements of (sqrt(eigvalj))eigvecj
    #must take the absolute value of the eigvals since they can be negative
    return eigvecs * sqrt(abs(eigvals))[:,NewAxis]

def output_pca(PCA_matrix, eigvals, names):
    """Creates a string output for principal coordinates analysis results. 

    PCA_matrix and eigvals are generated with the get_principal_coordinates 
    function. Names is a list of names that corresponds to the columns in the
    PCA_matrix. It is the order that samples were represented in the initial
    distance matrix.

    returns tab-delimited text that can be opened in Excel for analysis"""
    output = []
    #get order to output eigenvectors values. reports the eigvecs according
    #to their cooresponding eigvals from greatest to least
    vector_order = list(argsort(eigvals))
    vector_order.reverse()
    
    #make the header line and append to output
    header = 'pc vector number \t'
    for i in range(len(eigvals)):
        header = header + str(i+1) + '\t'
    output.append(header)
    #make data lines for eigenvectors and add to output
    for name_i, name in enumerate(names):
        new_line = name + '\t'
        for vec_i in vector_order:
            new_line = new_line + str(PCA_matrix[vec_i,name_i]) + '\t'
        output.append(new_line)
    #make data line for eigvals and append to output
    output.append('\n')
    eigval_line = 'eigvals' + '\t'
    for vec_i in vector_order:
        eigval_line = eigval_line + str(eigvals[vec_i]) + '\t'
    output.append(eigval_line)
    #make data line for percent variaion explained by eigvecs for output
    percents = (eigvals/sum(eigvals))*100
    percents_line = '% variation explained' + '\t'
    for vec_i in vector_order:
        percents_line = percents_line + str(percents[vec_i]) + '\t'
    output.append(percents_line)

    return ('\n').join(output)

