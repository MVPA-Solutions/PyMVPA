#emacs: -*- mode: python-mode; py-indent-offset: 4; indent-tabs-mode: nil -*-
#ex: set sts=4 ts=4 sw=4 et:
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the PyMVPA package for the
#   copyright and license terms.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Unit tests for PyMVPA recursive feature elimination"""

import unittest
import numpy as N
from sets import Set

from mvpa.datasets.maskeddataset import MaskedDataset
from mvpa.algorithms.rfe import RFE
from mvpa.algorithms.featsel import \
     StopNBackHistoryCriterion, FractionTailSelector, \
     FixedNElementTailSelector, BestDetector
from mvpa.algorithms.linsvmweights import LinearSVMWeights
from mvpa.clfs.svm import LinearNuSVMC
from mvpa.clfs.transerror import TransferError
from mvpa.misc.transformers import Absolute

from mvpa.misc.state import UnknownStateError

class RFETests(unittest.TestCase):

    def getData(self):
        data = N.random.standard_normal(( 100, 3, 2, 4 ))
        labels = N.concatenate( ( N.repeat( 0, 50 ),
                                  N.repeat( 1, 50 ) ) )
        chunks = N.repeat( range(5), 10 )
        chunks = N.concatenate( (chunks, chunks) )
        return MaskedDataset(samples=data, labels=labels, chunks=chunks)


    def testBestDetector(self):
        bd = BestDetector()

        # for empty history -- no best
        self.failUnless(bd([]) == False)
        # we got the best if we have just 1
        self.failUnless(bd([1]) == True)
        # we got the best if we have the last minimal
        self.failUnless(bd([1, 0.9, 0.8]) == True)

        # test for alternative func
        bd = BestDetector(func=max)
        self.failUnless(bd([0.8, 0.9, 1.0]) == True)
        self.failUnless(bd([0.8, 0.9, 1.0]+[0.9]*9) == False)
        self.failUnless(bd([0.8, 0.9, 1.0]+[0.9]*10) == False)

        # test to detect earliest and latest minimum
        bd = BestDetector(lastminimum=True)
        self.failUnless(bd([3, 2, 1, 1, 1, 2, 1]) == True)
        bd = BestDetector()
        self.failUnless(bd([3, 2, 1, 1, 1, 2, 1]) == False)


    def testStopCriterion(self):
        """Test stopping criterions"""
        stopcrit = StopNBackHistoryCriterion()
        # for empty history -- no best but just go
        self.failUnless(stopcrit([]) == False)
        # should not stop if we got 10 more after minimal
        self.failUnless(stopcrit(
            [1, 0.9, 0.8]+[0.9]*(stopcrit.steps-1)) == False)
        # should stop if we got 10 more after minimal
        self.failUnless(stopcrit(
            [1, 0.9, 0.8]+[0.9]*stopcrit.steps) == True)

        # test for alternative func
        stopcrit = StopNBackHistoryCriterion(BestDetector(func=max))
        self.failUnless(stopcrit([0.8, 0.9, 1.0]+[0.9]*9) == False)
        self.failUnless(stopcrit([0.8, 0.9, 1.0]+[0.9]*10) == True)

        # test to detect earliest and latest minimum
        stopcrit = StopNBackHistoryCriterion(BestDetector(lastminimum=True))
        self.failUnless(stopcrit([3, 2, 1, 1, 1, 2, 1]) == False)
        stopcrit = StopNBackHistoryCriterion(steps=4)
        self.failUnless(stopcrit([3, 2, 1, 1, 1, 2, 1]) == True)


    def testFeatureSelector(self):
        """Test feature selector"""
        # remove 10% weekest
        selector = FractionTailSelector(0.1)
        dataset = N.array([3.5, 10, 7, 5, -0.4, 0, 0, 2, 10, 9])
        # == rank [4, 5, 6, 7, 0, 3, 2, 9, 1, 8]
        target10 = N.array([0, 1, 2, 3, 5, 6, 7, 8, 9])
        target30 = N.array([0, 1, 2, 3, 7, 8, 9])

        self.failUnlessRaises(UnknownStateError,
                              selector.__getitem__, 'ndiscarded')
        self.failUnless((selector(dataset) == target10).all())
        selector.felements = 0.30      # discard 30%
        self.failUnless(selector.felements == 0.3)
        self.failUnless((selector(dataset) == target30).all())
        self.failUnless(selector['ndiscarded'] == 3) # se 3 were discarded

        selector = FixedNElementTailSelector(1)
        dataset = N.array([3.5, 10, 7, 5, -0.4, 0, 0, 2, 10, 9])
        self.failUnless((selector(dataset) == target10).all())

        selector.nelements = 3
        self.failUnless(selector.nelements == 3)
        self.failUnless((selector(dataset) == target30).all())
        self.failUnless(selector['ndiscarded'] == 3)


    def testRFE(self):
        svm = LinearNuSVMC()

        # sensitivity analyser and transfer error quantifier use the SAME clf!
        sens_ana = LinearSVMWeights(svm)
        trans_error = TransferError(svm)
        # because the clf is already trained when computing the sensitivity
        # map, prevent retraining for transfer error calculation
        # Use absolute of the svm weights as sensitivity
        rfe = RFE(Absolute(sens_ana),
                  trans_error,
                  feature_selector=FixedNElementTailSelector(1),
                  train_clf=False)

        wdata = self.getData()
        wdata_nfeatures = wdata.nfeatures
        tdata = self.getData()
        tdata_nfeatures = tdata.nfeatures

        sdata, stdata = rfe(wdata, tdata)

        # fail if orig datasets are changed
        self.failUnless(wdata.nfeatures == wdata_nfeatures)
        self.failUnless(tdata.nfeatures == tdata_nfeatures)

        # check that the features set with the least error is selected
        if len(rfe['errors']):
            e = N.array(rfe['errors'])
            self.failUnless(sdata.nfeatures == wdata_nfeatures - e.argmin())
        else:
            self.failUnless(sdata.nfeatures == wdata_nfeatures)

        # silly check if nfeatures is in decreasing order
        nfeatures = N.array(rfe['nfeatures']).copy()
        nfeatures.sort()
        self.failUnless( (nfeatures[::-1] == rfe['nfeatures']).all() )

        # check if history has elements for every step
        self.failUnless(Set(rfe['history'])
                        == Set(range(len(N.array(rfe['errors'])))))

        # Last (the largest number) can be present multiple times even
        # if we remove 1 feature at a time -- just need to stop well
        # in advance when we have more than 1 feature left ;)
        self.failUnless(rfe['nfeatures'][-1]
                        == len(N.where(rfe['history']
                                       ==max(rfe['history']))[0]))

        # XXX add a test where sensitivity analyser and transfer error do not
        # use the same classifier



def suite():
    return unittest.makeSuite(RFETests)


if __name__ == '__main__':
    import test_runner

