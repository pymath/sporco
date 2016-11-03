from __future__ import division
from builtins import object

import pytest
import numpy as np

from sporco.admm import cbpdn
import sporco.linalg as sl



class TestSet01(object):

    def setup_method(self, method):
        np.random.seed(12345)


    def test_01(self):
        N = 16
        Nd = 5
        Cs = 3
        M = 4
        D = np.random.randn(Nd, Nd, M)
        s = np.random.randn(N, N, Cs)
        lmbda = 1e-1
        b = cbpdn.ConvBPDN(D, s, lmbda, dimK=0)
        assert(b.dimC == 1)
        assert(b.dimK == 0)


    def test_02(self):
        N = 16
        Nd = 5
        Cs = 3
        K = 5
        M = 4
        D = np.random.randn(Nd, Nd, M)
        s = np.random.randn(N, N, Cs, K)
        lmbda = 1e-1
        b = cbpdn.ConvBPDN(D, s, lmbda)
        assert(b.dimC == 1)
        assert(b.dimK == 1)


    def test_03(self):
        N = 16
        Nd = 5
        Cd = 3
        M = 4
        D = np.random.randn(Nd, Nd, Cd, M)
        s = np.random.randn(N, N, Cd)
        lmbda = 1e-1
        b = cbpdn.ConvBPDN(D, s, lmbda)
        assert(b.dimC == 1)
        assert(b.dimK == 0)


    def test_04(self):
        N = 16
        Nd = 5
        Cd = 3
        K = 5
        M = 4
        D = np.random.randn(Nd, Nd, Cd, M)
        s = np.random.randn(N, N, Cd, K)
        lmbda = 1e-1
        b = cbpdn.ConvBPDN(D, s, lmbda)
        assert(b.dimC == 1)
        assert(b.dimK == 1)


    def test_05(self):
        N = 16
        Nd = 5
        K = 2
        M = 4
        D = np.random.randn(Nd, Nd, M)
        s = np.random.randn(N, N, K)
        lmbda = 1e-1
        b = cbpdn.ConvBPDN(D, s, lmbda)
        assert(b.dimC == 0)
        assert(b.dimK == 1)


    def test_06(self):
        N = 16
        Nd = 5
        M = 4
        D = np.random.randn(Nd, Nd, M)
        s = np.random.randn(N, N)
        lmbda = 1e-1
        try:
            b = cbpdn.ConvBPDN(D, s, lmbda)
            b.solve()
        except Exception as e:
            print(e)
            assert(0)


    def test_07(self):
        N = 16
        Nd = 5
        M = 4
        D = np.random.randn(Nd, Nd, M)
        s = np.random.randn(N, N)
        try:
            b = cbpdn.ConvBPDN(D, s)
            b.solve()
        except Exception as e:
            print(e)
            assert(0)


    def test_08(self):
        N = 64
        M = 4
        Nd = 8
        D = np.random.randn(Nd, Nd, M)
        X0 = np.zeros((N, N, M))
        xr = np.random.randn(N, N, M)
        xp = np.abs(xr) > 3
        X0[xp] = np.random.randn(X0[xp].size)
        S = np.sum(sl.ifftn(sl.fftn(D, (N, N), (0,1)) *
                   sl.fftn(X0, None, (0,1)), None, (0,1)).real, axis=2)
        lmbda = 1e-4
        rho = 1e-1
        opt = cbpdn.ConvBPDN.Options({'Verbose' : False, 'MaxMainIter' : 500,
                                      'RelStopTol' : 1e-3, 'rho' : rho,
                                      'LinSolveCheck' : True,
                                      'AutoRho' : {'Enabled' : False}})
        b = cbpdn.ConvBPDN(D, S, lmbda, opt)
        b.solve()
        X1 = b.Y.squeeze()
        assert(sl.rrs(X0,X1) < 5e-5)
        Sr = b.reconstruct().squeeze()
        assert(sl.rrs(S,Sr) < 1e-4)


    def test_09(self):
        N = 63
        M = 4
        Nd = 8
        D = np.random.randn(Nd, Nd, M)
        X0 = np.zeros((N, N, M))
        xr = np.random.randn(N, N, M)
        xp = np.abs(xr) > 3
        X0[xp] = np.random.randn(X0[xp].size)
        S = np.sum(sl.ifftn(sl.fftn(D, (N, N), (0,1)) *
                   sl.fftn(X0, None, (0,1)), None, (0,1)).real, axis=2)
        lmbda = 1e-4
        rho = 1e-1
        opt = cbpdn.ConvBPDN.Options({'Verbose' : False, 'MaxMainIter' : 500,
                                      'RelStopTol' : 1e-3, 'rho' : rho,
                                      'AutoRho' : {'Enabled' : False}})
        b = cbpdn.ConvBPDN(D, S, lmbda, opt)
        b.solve()
        X1 = b.Y.squeeze()
        assert(sl.rrs(X0,X1) < 5e-5)
        Sr = b.reconstruct().squeeze()
        assert(sl.rrs(S,Sr) < 1e-4)


    def test_10(self):
        N = 16
        Nd = 5
        Cs = 3
        M = 4
        D = np.random.randn(Nd, Nd, M)
        s = np.random.randn(N, N, Cs)
        lmbda = 1e-1
        try:
            b = cbpdn.ConvBPDN(D, s, lmbda, dimK=0)
            b.solve()
        except Exception as e:
            print(e)
            assert(0)


    def test_11(self):
        N = 16
        Nd = 5
        Cs = 3
        M = 4
        D = np.random.randn(Nd, Nd, M)
        s = np.random.randn(N, N, Cs)
        lmbda = 1e-1
        try:
            b = cbpdn.ConvBPDNJoint(D, s, lmbda, dimK=0)
            b.solve()
        except Exception as e:
            print(e)
            assert(0)


    def test_12(self):
        N = 16
        Nd = 5
        M = 4
        D = np.random.randn(Nd, Nd, M)
        s = np.random.randn(N, N)
        lmbda = 1e-1
        mu = 1e-2
        try:
            b = cbpdn.ConvElasticNet(D, s, lmbda, mu)
            b.solve()
        except Exception as e:
            print(e)
            assert(0)


    def test_13(self):
        N = 16
        Nd = 5
        M = 4
        D = np.random.randn(Nd, Nd, M)
        s = np.random.randn(N, N)
        lmbda = 1e-1
        mu = 1e-2
        try:
            b = cbpdn.ConvBPDNGradReg(D, s, lmbda, mu)
            b.solve()
        except Exception as e:
            print(e)
            assert(0)


    def test_15(self):
        N = 16
        Nd = 5
        M = 4
        D = np.random.randn(Nd, Nd, M)
        s = np.random.randn(N, N)
        lmbda = 1e-1
        try:
            b = cbpdn.ConvBPDNMaskDcpl(D, s, lmbda)
            b.solve()
        except Exception as e:
            print(e)
            assert(0)


    def test_16(self):
        N = 16
        Nd = 5
        M = 4
        D = np.random.randn(Nd, Nd, M)
        s = np.random.randn(N, N)
        w = np.ones(s.shape)
        lmbda = 1e-1
        try:
            b = cbpdn.AddMaskSim(cbpdn.ConvBPDN, D, s, w, lmbda)
            b.solve()
        except Exception as e:
            print(e)
            assert(0)

