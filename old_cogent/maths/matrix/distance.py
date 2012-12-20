#!/usr/bin/env python
#file evo/matrices/distance.py

"""Code supporting distance matrices with arbitrary row/column labels.

Currently used to support amino acid distance matrices and similar.

Owner: Greg Caporaso caporaso@colorado.edu

Status: Stable?

Revision History

10/9/03 Greg Caporaso: File creation, class transfered from aaindexrecord.py

10/10/03 Greg Caporaso: Fully tested, including reworking of transform and init

10/29/03 Greg Caporaso: Debugging of init to function correctly, addition of
Power attribute and elementPow method

4/21/04 Greg Caporaso: Now inherits from Dict2D, added strict parameter

4/26/04 Greg Caporaso: strict removed, inherits from new Dict2D

5/7/04 Greg Caporaso: Made RowOrder and ColOrder alphabetical for easier testing
"""

from old_cogent.util.misc import Delegator
from old_cogent.base.dict2d import Dict2D
from copy import deepcopy

class DistanceMatrix(Dict2D, Delegator):
    """ 2D dict giving distances from A to B and vice versa """

    # default set of amino acids
    RowOrder = list('ACDEFGHIKLMNPQRSTVWY')
    ColOrder = list('ACDEFGHIKLMNPQRSTVWY')
    Pad = True
    
    def __init__(self, data=None, RowOrder=None, ColOrder=None, Default=None,
        Pad=None, RowConstructor=None, info=None):
        """ Init dict with pre-exisitng data: dict of dicts
            Usage:
                data = distance matrix in form acceptable by Dict2D class
                RowOrder = list of 'interesting keys', default is the set of
                    all amino acids
                ColOrder = list of 'interesting keys', default is the set of
                    all amino acids
                Default = value to set padded elements to
                Pad = boolean describing whether to fill object to hold all 
                    possible elements based on RowOrder and ColOrder
                RowConstructor = constructor to use when building inner 
                    objects, default dict
                info = the AAIndexRecord object

            Power = Power the original matrix has been raised to yield current
              matrix
        """
        if RowOrder is not None:
            self.RowOrder = RowOrder
        if ColOrder is not None:
            self.ColOrder = ColOrder
        if Pad is not None:
            self.Pad = Pad
        # Initialize super class attributes
        Dict2D.__init__(self, data=data, RowOrder=self.RowOrder,\
                ColOrder=self.ColOrder, Default=Default, Pad=self.Pad,\
                RowConstructor=RowConstructor)
        Delegator.__init__(self, info)
        
        # The power to which the original data has been raised to give
        # the current data, starts at 1., modified by elementPow()
        # accessed as self.Power
        self.__dict__['Power'] = 1.

    def elementPow(self, power, ignore_invalid=True):
        """ Raises all elements in matrix to power
            
            power: the power to raise all elements in the matrix to,
                must be a floatable value or a TypeError is raise
            ignore_invalid: leaves invalid (not floatable) 
                matrix data untouched
        
        """
        try:
            n = float(power)
        except ValueError:
            raise TypeError, 'Must pass a floatable value to elementPow'
       
        if ignore_invalid:
            def Pow(x):
                try:
                    return x**n
                except TypeError:
                    return x
        else:
            def Pow(x):
                return x**n
            
        self.scale(Pow)
        self.Power = self.Power * n
                                
    def copy(self):
        """ Returns a deep copy of the DistanceMatrix object """
        # Is there a better way to do this? It's tricky to keep the delegator
        # part functioning
        return deepcopy(self)
    
