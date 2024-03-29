#!/usr/bin/env python
#test_UPGMA_numeric.py

"""
tests for functions to cluster using UPGMA 

Takes an array and list of PhyloNode objects corresponding to the array
as input

Revision History:

9-29-04: started writing

8/4/05 Rob Knight: Ported Jeremy's fix from the version in TreeStats. Fixed
UPGMA unit test so that tree is ultrametric.
"""

from old_cogent.util.unit_test import TestCase, main
from old_cogent.base.tree import PhyloNode
from Numeric import array, Float
from old_cogent.cluster.UPGMA import find_smallest_index, condense_matrix, \
        condense_node_order, UPGMA_cluster, inputs_from_dict2D
from old_cogent.base.dict2d import Dict2D

class UPGMATests(TestCase):
    """test the functions to cluster using UPGMA using Numeric"""

    def setUp(self):
        """creates inputs"""
        #create a list of PhyloNode objects
        a = PhyloNode()
        a.Data = 'a'
        b = PhyloNode()
        b.Data = 'b'
        c = PhyloNode()
        c.Data = 'c'
        d = PhyloNode()
        d.Data = 'd'
        e = PhyloNode()
        e.Data = 'e'
        self.node_order = [a, b, c, d, e]
        #create a Numeric matrix object to cluster
        self.matrix = array(([9999999, 1, 4, 20, 22], \
                        [1, 9999999, 5, 21, 23], \
                        [4, 5, 9999999, 10, 12], \
                        [20, 21, 10, 9999999, 2], \
                        [22, 23, 12, 2, 9999999]), Float)
        
    def test_find_smallest_index(self):
        """find_smallest_index returns the index of smallest value in array
        """
        matrix = self.matrix
        index = find_smallest_index(matrix)
        self.assertEqual(index, (0,1))

    def test_condense_matrix(self):
        """condense_array joins two rows and columns identified by indices
        """
        matrix = self.matrix
        index = find_smallest_index(matrix)
        result = condense_matrix(matrix, index, 9999999999)
        self.assertFloatEqual(result[0, 0], 5000000.0)
        self.assertEqual(result[1, 4], 9999999999)
        self.assertEqual(result[0, 1], 9999999999)
        self.assertEqual(result[0, 2], 4.5)
        self.assertEqual(result[2, 0], 4.5)
        self.assertEqual(result[0, 4], 22.5)
        self.assertEqual(result[4, 4], 9999999)
        self.assertEqual(result[4, 0], 22.5)

    def test_condense_node_order(self):
        """condense_node_order condenses nodes in list based on index info
        """
        matrix = self.matrix
        index = find_smallest_index(matrix)
        node_order = self.node_order
        node_order = condense_node_order(matrix, index, node_order)
        self.assertEqual(node_order[1], None)
        self.assertEqual(node_order[0].__str__(), '(a:0.5,b:0.5)')
        self.assertEqual(node_order[2].__str__(), '()c')
        self.assertEqual(node_order[3].__str__(), '()d')
        self.assertEqual(node_order[4].__str__(), '()e')

    def test_UPGMA_cluster(self):
        """UPGMA_cluster clusters nodes based on info in a matrix with UPGMA
        """
        matrix = self.matrix
        node_order = self.node_order
        large_number = 9999999999
        tree = UPGMA_cluster(matrix, node_order, large_number)
        self.assertEqual(str(tree), \
                '(((a:0.5,b:0.5):1.75,c:2.25):5.875,(d:1.0,e:1.0):7.125)')

    def test_inputs_from_dict2D(self):
        """inputs_from_dict2D makes an array object and PhyloNode list"""
        matrix = [('1', '2', 0.86), ('2', '1', 0.86), \
                ('1', '3', 0.92), ('3', '1', 0.92), ('2', '3', 0.67), \
                ('3', '2', 0.67)]
        row_order = ['3', '2', '1']
        matrix_d2d = Dict2D(matrix, RowOrder=row_order, \
                ColOrder=row_order, Pad=True, Default = 999999999999999)
        matrix_array, PhyloNode_order = inputs_from_dict2D(matrix_d2d)
        self.assertFloatEqual(matrix_array[0][2], 0.92)
        self.assertFloatEqual(matrix_array[1][0], 0.67)
        self.assertEqual(PhyloNode_order[0].Data, '3')
        self.assertEqual(PhyloNode_order[2].Data, '1')

#run if called from command line
if __name__ == '__main__':
       main()
