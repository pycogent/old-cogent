#!/usr/bin/env python
#file: cogent/maths/geometry.py
"""
Revision History:
8/16/04 Sandra Smit: written center_of_mass functions

9/30/04 Rob Knight: added distance function
"""
from Numeric import array, take, NewAxis, sum
from math import sqrt
from __future__ import division

def center_of_mass(coordinates, weights=-1):
    """Calculates the center of mass for a dataset.

    coordinates, weights can be two things:
    either: coordinates = array of coordinates, where one column contains 
        weights, weights = index of column that contains the weights
    or: coordinates = array of coordinates, weights = array of weights

    weights = -1 by default, because the simplest case is one dataset, where
        the last column contains the weights.
    If weights is given as a vector, it can be passed in as row or column.
    """
    if isinstance(weights,int):
        return center_of_mass_one_array(coordinates,weights)
    else:
        return center_of_mass_two_array(coordinates,weights)

def center_of_mass_one_array(data,weight_idx=-1):
    """Calculates the center of mass for a dataset

    data should be an array of x1,...,xn,r coordinates, where r is the 
        weight of the point
    """
    data = array(data)
    coord_idx = range(data.shape[1])
    del coord_idx[weight_idx]
    coordinates = take(data,(coord_idx),1)
    weights = take(data,(weight_idx,),1)
    return sum(coordinates * weights)/sum(weights)

def center_of_mass_two_array(coordinates,weights):
    """Calculates the center of mass for a set of weighted coordinates

    coordinates should be an array of coordinates
    weights should be an array of weights. Should have same number of items
        as the coordinates. Can be either row or column.
    """
    coordinates = array(coordinates)
    weights = array(weights)
    try:
        return sum(coordinates * weights)/sum(weights)
    except ValueError:
        weights = weights[:,NewAxis]
        return sum(coordinates * weights)/sum(weights)

def distance(first, second):
    """Calculates Euclideas distance between two vectors (or arrays).

    WARNING: Vectors have to be the same dimension.
    """
    return sqrt(sum(((first - second) ** 2).flat))
