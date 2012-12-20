#!/usr/bin/env python
#file evo/stats/test_histogram.py
"""Provides tests for Histogram

Owner: Sandra Smit (Sandra.Smit@colorado.edu)
Status: Development

Revision History:

2/26/04 Written by Sandra Smit

2/26/04 Rob Knight: added test for clear(), and broke some of the tests into
separate methods.
"""

from old_cogent.util.unit_test import TestCase, main
from old_cogent.maths.stats.histogram import Histogram
from old_cogent.base.location import Span

class HistogramTests(TestCase):
    """Tests for Histogram class"""
    
    def test_init_no_bins(self):
        """Histogram should raise error if initialized without bins"""
        # you deserve an Error if you initialize your histogram
        # without providing Bins
        self.assertRaises(AttributeError, Histogram)
    
    def test_init_bins(self):
        """Histogram should set _bins property correctly"""
        bins = [Span(0,2),Span(2,4),Span(4,6)]
        bins_only = Histogram(bins=bins)
        self.assertEqual(bins_only._bins, bins)

    def test_init_bins_data(self):
        """Histogram should fill bins with data if supplied"""
        # most basic histogram, bins and data
        data = [1,3,5,'A']
        bins = [Span(0,2),Span(2,4),Span(4,6)]
        data_and_bins = Histogram(data=data,bins=bins)
        self.assertEqual(data_and_bins._bins,bins)
        self.assertEqual(data_and_bins._values,[[1],[3],[5]])
        self.assertEqual(data_and_bins.Other,['A'])

    def test_call(self):
        """Histogram __call__ should update with new data"""
        data = [1,3,5,'A']
        bins = [Span(0,2),Span(2,4),Span(4,6)]
        data_and_bins = Histogram(data=data,bins=bins)
        #update the histogram
        data_and_bins([4,5,6,7])
        self.assertEqual(data_and_bins._values,[[1],[3],[5,4,5]])
        self.assertEqual(data_and_bins.Other,['A',6,7])

    def test_mapping(self):
        """Histogram Mapping should apply correct function to values"""
        # bins, data, mapping
        data = ['A','AAA','CCCCC','GGGGGGGGGGGGGG']
        bins = [Span(0,2),Span(2,4),Span(4,6)]
        mapping = Histogram(data=data,bins=bins,Mapping=len)
        self.assertEqual(mapping._values, [['A'],['AAA'],['CCCCC']])
        self.assertEqual(mapping.Other,['GGGGGGGGGGGGGG'])

    def test_multi(self):
        """Histogram Multi should allow values to match multiple bins"""
        #bins, data, multi=True
        bins2 = [Span(0,5),Span(3,8),Span(6,10)]
        data2 = [0,1,2,3,4,5,6,7,8,9,10]
        not_multi = Histogram(data2,bins2)
        self.assertEqual(not_multi._values,[[0,1,2,3,4],[5,6,7],[8,9]])
        self.assertEqual(not_multi.Other,[10])
        multi = Histogram(data2,bins2,Multi=True)
        self.assertEqual(multi._values,[[0,1,2,3,4],[3,4,5,6,7],[6,7,8,9]])
        self.assertEqual(multi.Other,[10])

    def test_toFreqs(self):
        """Histogram toFreqs() should return a Freqs object"""
        h = Histogram(range(0,20),bins=[Span(0,3),Span(3,10),
            Span(10,18),Span(18,20)])
        constructor=str
        f = h.toFreqs()
        self.assertEqual(f[constructor(Span(0,3))],3)
        self.assertEqual(f[constructor(Span(3,10))],7)
        self.assertEqual(f[constructor(Span(10,18))],8)
        self.assertEqual(f[constructor(Span(18,20))],2)

    def test_clear(self):
        """Histogram clear should reset all data"""
        data = [1,3,5,'A']
        bins = [Span(0,2),Span(2,4),Span(4,6)]
        data_and_bins = Histogram(data=data,bins=bins)
        self.assertEqual(data_and_bins._bins,bins)
        self.assertEqual(data_and_bins._values,[[1],[3],[5]])
        self.assertEqual(data_and_bins.Other,['A'])
        data_and_bins.clear()
        self.assertEqual(data_and_bins._values,[[],[],[]])
        self.assertEqual(data_and_bins.Other,[])
        
        
if __name__ == '__main__':
    main()

