#usr/bin/env python
#UPGMA_numeric.py

"""
Functions to cluster using UPGMA

Takes an array and a list of PhyloNode objects corresponding to the array 
as input. Can also generate this type of input from a Dict2D using
inputs_from_dict2D function.

Revision History:

9-27-04 to 9-30-04:Cathy Lozupone: wrote code

5-23-05: Cathy Lozupone: modified code so that it uses PhyloNode instead of
EnvsNode to store the UPGMA cluster.

8/4/05 Rob Knight: Ported Jeremy's fix to UPGMA_cluster so that the resulting
tree is ultrametric. Previous versions did not produce an ultrametric tree
because the distance from the tips so far was not subtracted from the distance
between clusters, which refers to the tip-to-tip distance.
"""

from Numeric import array, Float, ravel, argmin, take, sum, average
from old_cogent.base.tree import PhyloNode

def find_smallest_index(matrix):
    """returns the index of the smallest element in a Numeric array
    
    for UPGMA clustering elements on the diagonal should first be
    substituted with a very large number so that they are always 
    larger than the rest if the values in the array"""
    #get the shape of the array as a tuple (e.g. (3,3))
    shape = matrix.shape
    #turn into a 1 by x array and get the index of the lowest number
    matrix1D = ravel(matrix)
    lowest_index = argmin(matrix1D)
    #convert the lowest_index derived from matrix1D to one for the original
    #square matrix and return
    row_len = shape[0]
    return divmod(lowest_index, row_len)
   
def condense_matrix(matrix, smallest_index, large_value):
    """converges the rows and columns indicated by smallest_index
    
    Smallest index is returned from find_smallest_index.
    For both the rows and columns, the values for the two indices are
    averaged. The resulting vector replaces the first index in the array
    and the second index is replaced by an array with large numbers so that
    it is never chosen again with find_smallest_index.
    """
    first_index, second_index = smallest_index
    #get the rows and make a new vector that has their average
    rows = take(matrix, smallest_index)
    new_vector = average(rows)
    #replace info in the row and column for first index with new_vector
    matrix[first_index] = new_vector
    matrix[:, first_index] = new_vector
    #replace the info in the row and column for the second index with 
    #high numbers so that it is ignored
    matrix[second_index] = large_value
    matrix[:, second_index] = large_value
    return matrix

def condense_node_order(matrix, smallest_index, node_order):
    """condenses two nodes in node_order based on smallest_index info
    
    This function is used to create a tree while condensing a matrix
    with the condense_matrix function. The smallest_index is retrieved
    with find_smallest_index. The first index is replaced with a node object
    that combines the two nodes corresponding to the indices in node order.
    The second index in smallest_index is replaced with None.
    Also sets the branch length of the nodes to 1/2 of the distance between
    the nodes in the matrix"""
    index1 = smallest_index[0]
    index2 = smallest_index[1]
    node1 = node_order[index1]
    node2 = node_order[index2]
    #get the distance between the nodes and assign 1/2 the distance to the
    #BranchLength property of each node
    distance = matrix[index1, index2]
    nodes = [node1,node2]
    d = distance/2.0
    for n in nodes:
        if n.Children:
            n.BranchLength = d - n.Children[0].TipLength
        else:
            n.BranchLength = d
        n.TipLength = d
    #combine the two nodes into a new PhyloNode object
    new_node = PhyloNode()
    new_node.append(node1)
    new_node.append(node2)
    #replace the object at index1 with the combined node
    node_order[index1] = new_node
    #replace the object at index2 with None
    node_order[index2] = None
    return node_order

def UPGMA_cluster(matrix, node_order, large_number):
    """cluster with UPGMA
    
    matrix is a Numeric array.
    node_order is a list of PhyloNode objects corresponding to the matrix.
    large_number will be assigned to the matrix during the process and
    should be much larger than any value already in the matrix."""
    num_entries = len(node_order)
    tree = None
    for i in range(num_entries - 1):
        smallest_index = find_smallest_index(matrix)
        row_order = condense_node_order(matrix, smallest_index, node_order)
        matrix = condense_matrix(matrix, smallest_index, large_number)
        tree = node_order[smallest_index[0]]
    return tree

def inputs_from_dict2D(dict2d_matrix):
    """makes inputs for UPGMA_cluster from a Dict2D object
    
    Dict2D object is a distance matrix with labeled Rows. The diagonal
    elements should have a very large positive number assigned (e.g.1e305).
    
    The returned array is a Numeric array with the distances.
    PhyloNode_order is a list of PhyloNode objects with the Data property
    assigned from the Dict2D Row order.
    """
    matrix_lists = list(dict2d_matrix.Rows)
    matrix = array(matrix_lists, Float)
    row_order = dict2d_matrix.RowOrder
    PhyloNode_order = []
    for i in row_order:
        PhyloNode_order.append(PhyloNode(Data=i))
    return matrix, PhyloNode_order
