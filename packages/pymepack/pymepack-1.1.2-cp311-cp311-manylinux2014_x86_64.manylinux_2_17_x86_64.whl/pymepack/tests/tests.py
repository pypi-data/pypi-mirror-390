### python3 -m unittest -v tests

import unittest
import pymepack
import pymepack.generator as benchmarks
import pymepack.lapack as lapack_pointers

import numpy as np
from numpy.linalg import norm
from scipy import linalg
from parameterized import parameterized
from abc import ABC, abstractmethod
import sys

#only for finding a new seed
#on a normal call
#should always end up in the else branch
if sys.argv[-1].isnumeric():
    np.random.seed(int(sys.argv[-1]))
else:
    np.random.seed(2)
N = 128
def bound(precision=np.double):
    if precision == np.double:
        return N * 100 * np.finfo(np.double).eps
    elif precision == np.single:
        return N * 100 * np.finfo(np.single).eps

not_within_bound_err_msg = "forward error is not within the bound"
no_improvement_err_msg = "forward error did not improve after refinement"

def generate_nsym_stbl_matrix(N = N):
    U = np.linalg.qr(np.random.rand(N,N))[0]
    e1 = np.zeros((N,1))
    e1[0,0] = 1
    eN = np.zeros((1,N))
    eN[0,N-1] = 1
    eigenVals = [np.random.uniform(-1 / N, -1) for _ in range(N)]
    return (U.T).dot(np.diag(eigenVals) + np.matmul(e1,eN)).dot(U)

def _ggbal(JOB, A, B, precision=np.double):
    lscale = np.ndarray(shape=(A.shape[0],), dtype=precision)
    rscale = np.ndarray(shape=(A.shape[0],), dtype=precision)
    work = np.ndarray(shape=(A.shape[0],), dtype=precision)
    n = A.shape[0]
    lda = A.shape[0]
    ldb = B.shape[0]
    if precision == np.double:
        A, B, ilo, ihi, info = lapack_pointers.dggbal(JOB.encode(), n, A, B,
            lscale, rscale, work, lda, ldb, overwrite_a = True, overwrite_b = True )
    elif precision == np.single:
        A, B, ilo, ihi, info = lapack_pointers.sggbal(JOB.encode(), n, A, B,
            lscale, rscale, work, lda, ldb, overwrite_a = True, overwrite_b = True )
    return (ilo, ihi, info)

def _ormqr(SIDE, TRANS, A, TAU, C, precision=np.double):
    lwork = A.shape[0] if SIDE.upper() == "R" else A.shape[1]
    work = np.ndarray(shape=(lwork,), dtype=precision)
    info = np.ndarray(shape=(1,), dtype=np.int32)
    m = C.shape[0]
    n = C.shape[1]
    k = TAU.shape[0]
    ldc = C.shape[0]
    lda = A.shape[0]
    info[0] = 0
    if precision == np.double:
        C, info = lapack_pointers.dormqr(SIDE.encode(), TRANS.encode(),
            m, n, k, A, TAU, C, work, lwork, lda, ldc, overwrite_c = True)
    elif precision == np.single:
        C, info = lapack_pointers.sormqr(SIDE.encode(), TRANS.encode(),
            m, n, k, A, TAU, C, work, lwork, lda, ldc, overwrite_c = True)
    return info

def _orgqr(M, N, K, A, TAU, precision=np.double):
    lwork = A.shape[1]
    work = np.ndarray(shape=(lwork,), dtype=precision)
    info = np.ndarray(shape=(1,), dtype=np.int32)
    lda = A.shape[0]
    if precision == np.double:
        A, info = lapack_pointers.dorgqr(M, N, K, A, TAU, work, lwork, lda, overwrite_a = True)
    elif precision == np.single:
        A, info = lapack_pointers.sorgqr(M, N, K, A, TAU, work, lwork, lda, overwrite_a = True)
    return info

def _gghrd(COMPQ, COMPZ, N, ILO, IHI, A, B, Q, Z, precision=np.double):
    lda = A.shape[0]
    ldb = B.shape[0]
    ldq = Q.shape[0]
    ldz = Z.shape[0]
    if precision == np.double:
        A, B, Q, Z, info = lapack_pointers.dgghrd(COMPQ.encode(), COMPZ.encode(), N, ILO, IHI,
            A, B, Q, Z, lda, ldb, ldq, ldz, overwrite_a = True, overwrite_b = True,
            overwrite_q = True, overwrite_z = True)
    elif precision == np.single:
        A, B, Q, Z, info = lapack_pointers.sgghrd(COMPQ.encode(), COMPZ.encode(), N, ILO, IHI,
            A, B, Q, Z, lda, ldb, ldq, ldz, overwrite_a = True, overwrite_b = True,
            overwrite_q = True, overwrite_z = True)
    return info

def generalized_hess_form(A, B, precision=np.double):
        ilo, ihi, _ = _ggbal("P", A, B, precision=precision)
        irows = ihi + 1 - ilo
        m = A.shape[0]
        if precision == np.double:
            _, tau, *_ = linalg.lapack.dgeqrf(B[(ilo-1):, (ilo-1):], overwrite_a = 1)
        elif precision == np.single:
            _, tau, *_ = linalg.lapack.sgeqrf(B[(ilo-1):, (ilo-1):], overwrite_a = 1)
        _ormqr("L", "T", B[(ilo-1):,(ilo-1):], tau, A[(ilo-1):,(ilo-1):], precision=precision)
        Q = np.identity(m, dtype = precision).copy(order="F")
        Z = np.identity(m, dtype = precision).copy(order="F")
        if irows > 1:
            Q[ilo:,(ilo-1):] += np.tril(B[ilo:,(ilo-1):])
        _orgqr(irows, irows, irows, Q[(ilo-1):,(ilo-1):], tau, precision=precision)
        _gghrd("V", "V", m, ilo, ihi, A, B, Q, Z, precision=precision)


class TestDataAbstract(ABC):
    def __init__(self, group, num, N = N):
        self.nr = np.ndarray(shape=(2,),dtype=int)
        self.nr[0] = group
        self.nr[1] = num
        self.vec = np.ndarray(shape=(8,),dtype=int)
        self.m = 1
        self.e = np.zeros(shape=(N,N),dtype=np.double)
        self.a = np.zeros(shape=(N,N),dtype=np.double)
        self.y = np.zeros(shape=(N,N),dtype=np.double)
        self.b = np.zeros(shape=(self.m,N),dtype=np.double)
        self.x = np.zeros(shape=(N,N),dtype=np.double)
        self.u = np.zeros(shape=(N,N),dtype=np.double)
        self.note = '0'*70
        self.dwork = np.zeros(shape=(10 * N,),dtype=np.double)
        self.info = 0
        self.N = N

    @abstractmethod
    def _set_params(self):
        pass

    @abstractmethod
    def _call_collection_routine(self):
        pass

    def get_example(self):
        self._set_params()
        return self._call_collection_routine()

class GELYAP(TestDataAbstract):

    def _set_params(self, p1 = 1.01, p2 = 1.01):
        self.defv = 'N'
        self.dpar = np.ndarray(shape=(7,),dtype=np.double)
        self.dpar[0] = p1
        self.dpar[1] = p2
        self.ipar = np.ndarray(shape=(1,),dtype=int)
        self.ipar[0] = self.N

    def _call_collection_routine(self):
        (E,A,Y,X) = benchmarks.bb03ad(self.defv, self.nr, self.dpar, self.ipar,
                      self.vec, self.N, self.m, self.e, self.a, self.y, self.b,
                      self.x, self.u, self.dwork)
        return (A,Y,X)


class GESTEIN(TestDataAbstract):

    def _set_params(self, p1=1.01, p2=1.01):
        self.defv = 'N'
        self.dpar = np.ndarray(shape=(7,),dtype=np.double)
        self.dpar[0] = p1
        self.dpar[1] = p2
        self.ipar = np.ndarray(shape=(1,),dtype=int)
        self.ipar[0] = self.N

    def _call_collection_routine(self):
        (E,A,Y,X) = benchmarks.bb04ad(self.defv, self.nr, self.dpar, self.ipar,
                      self.vec, self.N, self.m, self.e, self.a, self.y, self.b,
                      self.x, self.u, self.dwork)
        return (A,Y,X)

class GGLYAP(TestDataAbstract):

    def _set_params(self, p1 = 10):
        self.defv = 'N'
        self.dpar = np.ndarray(shape=(7,),dtype=np.double)
        self.dpar[0] = p1
        self.ipar = np.ndarray(shape=(1,),dtype=int)
        self.ipar[0] = self.N

    def _call_collection_routine(self):
        (E,A,Y,X) = benchmarks.bb03ad(self.defv, self.nr, self.dpar, self.ipar,
                      self.vec, self.N, self.m, self.e, self.a, self.y, self.b,
                      self.x, self.u, self.dwork)
        return (E,A,Y,X)

class GGSTEIN(TestDataAbstract):

    def _set_params(self, p1 = 10):
        self.defv = 'N'
        self.dpar = np.ndarray(shape=(7,),dtype=np.double)
        self.dpar[0] = p1
        self.ipar = np.ndarray(shape=(1,),dtype=int)
        self.ipar[0] = self.N

    def _call_collection_routine(self):
        (E,A,Y,X) = benchmarks.bb04ad(self.defv, self.nr, self.dpar, self.ipar,
                      self.vec, self.N, self.m, self.e, self.a, self.y, self.b,
                      self.x, self.u, self.dwork)

        return (E,A,Y,X)

lyap_test_parameters = [
        ['eq1_double' ,False, np.double],
        ['eq2_double', True, np.double],
        ['eq1_single' ,False, np.single],
        ['eq2_single', True, np.single]
    ]

class TestStandardLyapunovSolver(unittest.TestCase):

    def get_data(self, shape = 'G', precision = np.double):
        (A,Y,X) = GELYAP(4,1).get_example()
        if precision == np.single:
            A,Y,X=(A.astype(np.single),Y.astype(np.single),X.astype(np.single))
        if shape == 'F':
            if precision == np.single:
                schur = linalg.lapack.sgees(lambda: None, A)
            elif precision == np.double:
                schur = linalg.lapack.dgees(lambda: None, A)
            return ((A.copy(order='F'),Y.copy(order='F')),
                    (schur[0], schur[4]),
                    Y.copy(order='F'))
        elif shape == 'G':
            return ((A.copy(order='F'),Y.copy(order='F')),
                    (A.copy(order='F'), Y.copy(order='F')))
        else:
            if precision == np.single:
                H = linalg.lapack.sgehrd(A)[0]
            if precision == np.double:
                H = linalg.lapack.dgehrd(A)[0]
            H = np.triu(H, -1)
            return ((H,                 Y.copy(order='F')),
                    (H.copy(order='F'), Y.copy(order='F')))

    def rel_residual(self, trans, A, X, Y):
        return pymepack.res_gelyap(A, X, Y, trans = trans)

    @parameterized.expand(lyap_test_parameters)
    def test_gelyap_gem_inplace(self, name, trans, precision):
        (A_init, Y), (A, X) = self.get_data(precision=precision)
        pymepack.gelyap(A, X, trans = trans, inplace=True)
        self.assertLess(self.rel_residual(trans,A_init,X,Y), bound(precision))

    @parameterized.expand(lyap_test_parameters)
    def test_gelyap_gem_copy(self, name, trans, precision):
        (A_init, Y), (A, X) = self.get_data(precision=precision)

        res = pymepack.gelyap(A, X, inplace=False, trans = trans)
        self.assertEqual(len(res), 3)
        self.assertTrue((A_init ==  A).all())
        self.assertTrue((Y == X).all())

        self.assertLess(self.rel_residual(trans,A_init,res[0],Y),bound(precision))

    @parameterized.expand(lyap_test_parameters)
    def test_gelyap_schur_inplace(self, name, trans, precision):
        (A_init, Y), (A, Q), X = self.get_data(shape='F', precision=precision)

        pymepack.gelyap(A, X, Q, trans = trans, inplace=True)
        self.assertLess(self.rel_residual(trans, A_init,X,Y), bound(precision))

    @parameterized.expand(lyap_test_parameters)
    def test_gelyap_schur_copy(self, name, trans, precision):
        (A_init, Y), (A, Q), X = self.get_data(shape='F', precision=precision)
        schur = (A.copy(order='F'), Q.copy(order='F'))

        res = pymepack.gelyap(A, X, Q, inplace=False, trans = trans)
        self.assertEqual(len(res), 3)
        self.assertTrue((schur[0] ==  A).all())
        self.assertTrue((schur[1] ==  Q).all())
        self.assertTrue((Y == X).all())

        self.assertLess(self.rel_residual(trans, A_init, res[0], Y),bound(precision))

    @parameterized.expand(lyap_test_parameters)
    def test_gelyap_hess_inplace(self, name, trans, precision):
        (H_init, Y), (H, X) = self.get_data(shape='H', precision=precision)
        pymepack.gelyap(H, X, trans = trans, hess=True, inplace=True)
        self.assertLess(self.rel_residual(trans,H_init,X,Y), bound(precision))

    @parameterized.expand(lyap_test_parameters)
    def test_gelyap_hess_copy(self, name, trans, precision):
        (H_init, Y), (H, X) = self.get_data(shape='H', precision=precision)

        res = pymepack.gelyap(H, X, inplace=False, trans = trans, hess = True)
        self.assertEqual(len(res), 3)
        self.assertTrue((H_init ==  H).all())
        self.assertTrue((Y == X).all())

        self.assertLess(self.rel_residual(trans,H_init,res[0],Y),bound(precision))

    @parameterized.expand(lyap_test_parameters)
    def test_gelyap_refine(self, name, trans, precision):
        (A_init, Y), (AS, Q), *_ = self.get_data(shape='F', precision=precision)

        (X_refined, max_it, tau, convlog) = pymepack.gelyap_refine(
                        A_init, Y, AS, Q, trans = trans
                    )
        self.assertLess(self.rel_residual(trans,A_init,X_refined,Y),bound(precision),
                not_within_bound_err_msg)
        X_no_ref, *_ = pymepack.gelyap(AS, Y, Q, inplace=False, trans = trans)
        self.assertLess(self.rel_residual(trans, A_init,X_refined,Y),
                        self.rel_residual(trans, A_init,X_no_ref, Y),
                        no_improvement_err_msg)


class TestStandardSteinSolver(unittest.TestCase):
    def get_data(self, shape = 'G', precision=np.double):
        (A,Y,X) = GESTEIN(4,1).get_example()
        if precision == np.single:
            A,Y,X=(A.astype(np.single),Y.astype(np.single),X.astype(np.single))
        if shape == 'F':
            if precision == np.single:
                schur = linalg.lapack.sgees(lambda: None, A)
            elif precision == np.double:
                schur = linalg.lapack.dgees(lambda: None, A)
            return ((A.copy(order='F'),Y.copy(order='F')),
                    (schur[0], schur[4]),
                    Y.copy(order='F'))
        elif shape == 'G':
            return ((A.copy(order='F'),Y.copy(order='F')),
                    (A.copy(order='F'), Y.copy(order='F')))
        else:
            if precision == np.single:
                H = linalg.lapack.sgehrd(A)[0].copy(order='F')
            elif precision == np.double:
                H = linalg.lapack.dgehrd(A)[0].copy(order='F')
            H  = np.triu(H, -1).copy(order='F')
            return ((H,                 Y.copy(order='F')),
                    (H.copy(order='F'), Y.copy(order='F')))

    def rel_residual(self, trans, A, X, Y):
        return pymepack.res_gestein(A, X, Y, trans = trans)

    @parameterized.expand(lyap_test_parameters)
    def test_gestein_gem_inplace(self, name, trans, precision):
        (A_init, Y), (A, X) = self.get_data(precision=precision)
        pymepack.gestein(A, X, trans = trans, inplace=True)
        self.assertLess(self.rel_residual(trans,A_init,X,Y), bound(precision))


    @parameterized.expand(lyap_test_parameters)
    def test_gestein_gem_copy(self, name, trans, precision):
        (A_init, Y), (A, X) = self.get_data(precision=precision)

        res = pymepack.gestein(A, X, inplace=False, trans = trans)
        self.assertEqual(len(res), 3)
        self.assertTrue((A_init ==  A).all())
        self.assertTrue((Y == X).all())

        self.assertLess(self.rel_residual(trans,A_init,res[0],Y),bound(precision))

    @parameterized.expand(lyap_test_parameters)
    def test_gestein_schur_inplace(self, name, trans, precision):
        (A_init, Y), (A, Q), X = self.get_data(shape='F', precision=precision)
        pymepack.gestein(A, X, Q, trans = trans, inplace=True)
        self.assertLess(self.rel_residual(trans, A_init,X,Y), bound(precision))

    @parameterized.expand(lyap_test_parameters)
    def test_gestein_schur_copy(self, name, trans, precision):
        (A_init, Y), (A, Q), X = self.get_data(shape='F', precision=precision)
        schur = (A.copy(order='F'), Q.copy(order='F'))

        res = pymepack.gestein(A, X, Q, inplace=False, trans = trans)
        self.assertEqual(len(res), 3)
        self.assertTrue((schur[0] ==  A).all())
        self.assertTrue((schur[1] ==  Q).all())
        self.assertTrue((Y == X).all())

        self.assertLess(self.rel_residual(trans, A_init, res[0], Y),bound(precision))

    @parameterized.expand(lyap_test_parameters)
    def test_gestein_hess_inplace(self, name, trans, precision):
        (H_init, Y), (H, X) = self.get_data(shape='H', precision=precision)
        pymepack.gestein(H, X, trans = trans, hess=True, inplace=True)
        self.assertLess(self.rel_residual(trans,H_init,X,Y), bound(precision))

    @parameterized.expand(lyap_test_parameters)
    def test_gestein_hess_copy(self, name, trans, precision):
        (H_init, Y), (H, X) = self.get_data(shape='H', precision=precision)

        res = pymepack.gestein(H, X, inplace=False, trans = trans, hess = True)
        self.assertEqual(len(res), 3)
        self.assertTrue((H_init ==  H).all())
        self.assertTrue((Y == X).all())

        self.assertLess(self.rel_residual(trans,H_init,res[0],Y),bound(precision))

    @parameterized.expand(lyap_test_parameters)
    def test_gestein_refine(self, name, trans, precision):
        (A_init, Y), (AS, Q), *_ = self.get_data(shape='F', precision=precision)

        (X_refined, max_it, tau, convlog) = pymepack.gestein_refine(
                        A_init, Y, AS, Q, trans = trans
                    )
        self.assertLess(self.rel_residual(trans,A_init,X_refined,Y),bound(precision),
                not_within_bound_err_msg)
        X_no_ref, *_ = pymepack.gestein(AS, Y, Q, inplace=False, trans = trans)
        self.assertLess(self.rel_residual(trans, A_init,X_refined,Y),
                        self.rel_residual(trans, A_init,X_no_ref, Y),
                        no_improvement_err_msg)


class TestGeneralizedLyapunovSolver(unittest.TestCase):

    def get_data(self, shape = 'G', precision=np.double):
        (B,A,Y,X) = GGLYAP(4,3).get_example()
        B = B.astype(precision)
        A = A.astype(precision)
        Y = Y.astype(precision)
        X = X.astype(precision)
        if shape == 'F':
            schur = linalg.qz(A,B)
            return ((A.copy(order='F'), B.copy(order='F'), Y.copy(order='F')),
                    schur,
                    Y.copy(order='F'))
        elif shape == 'G':
            return ((A.copy(order='F'), B.copy(order='F'), Y.copy(order='F')),
                    (A.copy(order='F'), B.copy(order='F'), Y.copy(order='F')))
        elif shape == 'H':
            A_hess = A.copy(order="F")
            B_hess = B.copy(order="F")
            generalized_hess_form(A_hess, B_hess, precision=precision)
            return ((A_hess, B_hess, Y.copy(order="F")),
                    (A_hess.copy(order="F"), B_hess.copy(order="F"),
                        Y.copy(order="F")))
        else:
            raise ValueError('unknown shape')

    def rel_residual(self, trans, A, B, X, Y):
        return pymepack.res_gglyap(A, B, X, Y, trans = trans)

    @parameterized.expand(lyap_test_parameters)
    def test_gglyap_gem_inplace(self, name, trans, precision):
        (A_init, B_init, Y), (A, B, X) = self.get_data(precision=precision)
        pymepack.gglyap(A, B, X, trans = trans, inplace=True)
        self.assertLess(self.rel_residual(trans,A_init,B_init,X,Y), bound(precision))

    @parameterized.expand(lyap_test_parameters)
    def test_gglyap_gem_copy(self, name, trans, precision):
        (A_init, B_init, Y), (A, B, X) = self.get_data(precision=precision)

        res = pymepack.gglyap(A, B, X, inplace=False, trans = trans)
        self.assertEqual(len(res), 5)
        self.assertTrue((A_init == A).all())
        self.assertTrue((B_init == B).all())
        self.assertTrue((Y == X).all())

        self.assertLess(self.rel_residual(trans,A_init, B_init, res[0],Y),
                        bound(precision))

    @parameterized.expand(lyap_test_parameters)
    def test_gglyap_schur_inplace(self, name, trans, precision):
        (A_init, B_init, Y), (A, B, Q, Z), X = self.get_data(shape='F', precision=precision)

        pymepack.gglyap(A, B, X, Q, Z, trans = trans, inplace=True)
        self.assertLess(self.rel_residual(trans, A_init, B_init, X, Y),
                        bound(precision))

    @parameterized.expand(lyap_test_parameters)
    def test_gglyap_schur_copy(self, name, trans, precision):
        (A_init, B_init, Y), (A, B, Q, Z), X = self.get_data(shape='F', precision=precision)
        schur = (A.copy(order='F'), B.copy(order='F'),
                 Q.copy(order='F'), Z.copy(order='F'))

        res = pymepack.gglyap(A, B, X, Q, Z, inplace=False, trans = trans)
        self.assertEqual(len(res), 5)
        self.assertTrue((schur[0] == A).all())
        self.assertTrue((schur[1] == B).all())
        self.assertTrue((schur[2] == Q).all())
        self.assertTrue((schur[3] == Z).all())
        self.assertTrue((Y == X).all())

        self.assertLess(self.rel_residual(trans, A_init, B_init, res[0], Y),
                        bound(precision))

    @parameterized.expand(lyap_test_parameters)
    def test_gglyap_hess_inplace(self, name, trans, precision):
        (A_init, B_init, Y), (A, B, X) = self.get_data(shape='H', precision=precision)
        pymepack.gglyap(A, B, X, trans = trans, hess=True, inplace=True)
        self.assertLess(self.rel_residual(trans,A_init,B_init,X,Y), bound(precision))

    @parameterized.expand(lyap_test_parameters)
    def test_gglyap_hess_copy(self, name, trans, precision):
        (A_init, B_init, Y), (A, B, X) = self.get_data(shape='H', precision=precision)
        res = pymepack.gglyap(A, B, X, inplace=False, trans=trans, hess=True)
        self.assertEqual(len(res), 5)
        self.assertTrue((A_init == A).all())
        self.assertTrue((B_init == B).all())
        self.assertTrue((Y == X).all())

        self.assertLess(self.rel_residual(trans,A_init, B_init, res[0],Y),
                        bound(precision))

    @parameterized.expand(lyap_test_parameters)
    def test_gglyap_hess_inplace(self, name, trans, precision):
        (A_init, B_init, Y), (A, B, X) = self.get_data(shape='H', precision=precision)
        pymepack.gglyap(A, B, X, trans = trans, hess=True, inplace=True)
        self.assertLess(self.rel_residual(trans,A_init,B_init,X,Y), bound(precision))

    @parameterized.expand(lyap_test_parameters)
    def test_gglyap_hess_copy(self, name, trans, precision):
        (A_init, B_init, Y), (A, B, X) = self.get_data(shape='H', precision=precision)
        res = pymepack.gglyap(A, B, X, inplace=False, trans=trans, hess=True)
        self.assertEqual(len(res), 5)
        self.assertTrue((A_init == A).all())
        self.assertTrue((B_init == B).all())
        self.assertTrue((Y == X).all())

        self.assertLess(self.rel_residual(trans,A_init, B_init, res[0],Y),
                        bound(precision))

    @parameterized.expand(lyap_test_parameters)
    def test_gglyap_refine(self, name, trans, precision):
        (A_init, B_init, Y), (AS, BS, Q, Z), *_ = self.get_data(shape='F',precision=precision)

        X_no_ref, *_ = pymepack.gglyap(AS, BS, Y, Q, Z, inplace=False,
                                     trans=trans)
        (X_refined, max_it, tau, convlog) = pymepack.gglyap_refine(
                    A_init, B_init, Y, AS, BS, Q, Z, trans=trans
                    )
        self.assertLess(self.rel_residual(trans,A_init,
                                               B_init,X_refined,Y),
                        bound(precision),
                        not_within_bound_err_msg)

        self.assertLess(self.rel_residual(trans,A_init,B_init,
                                                            X_refined,Y),
                        self.rel_residual(trans,A_init,B_init,
                                                            X_no_ref,Y),
                        no_improvement_err_msg)


class TestGeneralizedSteinSolver(unittest.TestCase):

    def get_data(self, shape = 'G', precision=np.double):
        (B,A,Y,X) = GGLYAP(4,3).get_example()
        B = B.astype(precision)
        A = A.astype(precision)
        Y = Y.astype(precision)
        X = X.astype(precision)
        if shape == 'F':
            schur = linalg.qz(A,B)
            return ((A.copy(order='F'), B.copy(order='F'), Y.copy(order='F')),
                    schur,
                    Y.copy(order='F'))
        elif shape == 'G':
            return ((A.copy(order='F'), B.copy(order='F'), Y.copy(order='F')),
                    (A.copy(order='F'), B.copy(order='F'), Y.copy(order='F')))
        elif shape == 'H':
            A_hess = A.copy(order="F")
            B_hess = B.copy(order="F")
            generalized_hess_form(A_hess, B_hess, precision=precision)
            return ((A_hess, B_hess, Y.copy(order="F")),
                    (A_hess.copy(order="F"), B_hess.copy(order="F"),
                        Y.copy(order="F")))
        else:
            raise ValueError('unknown shape')

    def rel_residual(self, trans, A, B, X, Y):
        return pymepack.res_ggstein(A, B, X, Y, trans = trans)

    @parameterized.expand(lyap_test_parameters)
    def test_ggstein_gem_inplace(self, name, trans, precision):
        (A_init, B_init, Y), (A, B, X) = self.get_data(precision=precision)
        pymepack.ggstein(A, B, X, trans = trans, inplace=True)
        self.assertLess(self.rel_residual(trans,A_init,B_init,X,Y), bound(precision))

    @parameterized.expand(lyap_test_parameters)
    def test_ggstein_gem_copy(self, name, trans, precision):
        (A_init, B_init, Y), (A, B, X) = self.get_data(precision=precision)

        res = pymepack.ggstein(A, B, X, inplace=False, trans = trans)
        self.assertEqual(len(res), 5)
        self.assertTrue((A_init == A).all())
        self.assertTrue((B_init == B).all())
        self.assertTrue((Y == X).all())

        self.assertLess(self.rel_residual(trans,A_init, B_init, res[0],Y),
                        bound(precision))

    @parameterized.expand(lyap_test_parameters)
    def test_ggstein_schur_inplace(self, name, trans, precision):
        (A_init, B_init, Y), (A, B, Q, Z), X = self.get_data(shape='F', precision=precision)

        pymepack.ggstein(A, B, X, Q, Z, trans = trans, inplace=True)
        self.assertLess(self.rel_residual(trans, A_init, B_init, X, Y),
                        bound(precision))

    @parameterized.expand(lyap_test_parameters)
    def test_ggstein_schur_copy(self, name, trans, precision):
        (A_init, B_init, Y), (A, B, Q, Z), X = self.get_data(shape='F', precision=precision)
        schur = (A.copy(order='F'), B.copy(order='F'),
                 Q.copy(order='F'), Z.copy(order='F'))

        res = pymepack.ggstein(A, B, X, Q, Z, inplace=False, trans = trans)
        self.assertEqual(len(res), 5)
        self.assertTrue((schur[0] == A).all())
        self.assertTrue((schur[1] == B).all())
        self.assertTrue((schur[2] == Q).all())
        self.assertTrue((schur[3] == Z).all())
        self.assertTrue((Y == X).all())

        self.assertLess(self.rel_residual(trans, A_init, B_init, res[0], Y),
                        bound(precision))

    @parameterized.expand(lyap_test_parameters)
    def test_ggstein_hess_inplace(self, name, trans, precision):
        (A_init, B_init, Y), (A, B, X) = self.get_data(shape='H', precision=precision)
        pymepack.ggstein(A, B, X, trans = trans, hess=True, inplace=True)
        self.assertLess(self.rel_residual(trans,A_init,B_init,X,Y), bound(precision))

    @parameterized.expand(lyap_test_parameters)
    def test_ggstein_hess_copy(self, name, trans, precision):
        (A_init, B_init, Y), (A, B, X) = self.get_data(shape='H', precision=precision)

        res = pymepack.ggstein(A, B, X, inplace=False, trans=trans, hess=True)
        self.assertEqual(len(res), 5)
        self.assertTrue((A_init == A).all())
        self.assertTrue((B_init == B).all())
        self.assertTrue((Y == X).all())

        self.assertLess(self.rel_residual(trans,A_init, B_init, res[0],Y),
                        bound(precision))

    @parameterized.expand(lyap_test_parameters)
    def test_ggstein_hess_inplace(self, name, trans, precision):
        (A_init, B_init, Y), (A, B, X) = self.get_data(shape='H', precision=precision)
        pymepack.ggstein(A, B, X, trans = trans, hess=True, inplace=True)
        self.assertLess(self.rel_residual(trans,A_init,B_init,X,Y), bound(precision))

    @parameterized.expand(lyap_test_parameters)
    def test_ggstein_hess_copy(self, name, trans, precision):
        (A_init, B_init, Y), (A, B, X) = self.get_data(shape='H', precision=precision)

        res = pymepack.ggstein(A, B, X, inplace=False, trans=trans, hess=True)
        self.assertEqual(len(res), 5)
        self.assertTrue((A_init == A).all())
        self.assertTrue((B_init == B).all())
        self.assertTrue((Y == X).all())

        self.assertLess(self.rel_residual(trans,A_init, B_init, res[0],Y),
                        bound(precision))

    @parameterized.expand(lyap_test_parameters)
    def test_ggstein_refine(self, name, trans, precision):
        (A_init, B_init, Y), (AS, BS, Q, Z), *_ = self.get_data(shape='F', precision=precision)

        X_no_ref, *_ = pymepack.ggstein(AS, BS, Y, Q, Z,
                                      inplace=False, trans=trans)
        (X_refined, max_it, tau, convlog) = pymepack.ggstein_refine(
                    A_init, B_init, Y, AS, BS, Q, Z, trans=trans
                    )
        self.assertLess(self.rel_residual(trans,A_init,B_init,
                                                            X_refined,Y),
                        bound(precision),
                        not_within_bound_err_msg)

        self.assertLess(self.rel_residual(trans,A_init,B_init,
                                                            X_refined,Y),
                        self.rel_residual(trans,A_init,B_init,
                                                            X_no_ref,Y),
                        no_improvement_err_msg)

gesylv_test_parameters = [
        ['eq1_A_B_double',False,False,1,np.double],
        ['eq1_A_B_tr_double',False,True,1,np.double],
        ['eq1_A_tr_B_double',True,False,1,np.double],
        ['eq1_A_tr_B_tr_double',True,True,1,np.double],
        ['eq2_A_B_double',False,False,-1,np.double],
        ['eq2_A_B_tr_double',False,True,-1,np.double],
        ['eq2_A_tr_B_double',True,False,-1,np.double],
        ['eq2_A_tr_B_tr_double',True,True,-1,np.double],
        ['eq1_A_B_single',False,False,1,np.single],
        ['eq1_A_B_tr_single',False,True,1,np.single],
        ['eq1_A_tr_B_single',True,False,1,np.single],
        ['eq1_A_tr_B_tr_single',True,True,1,np.single],
        ['eq2_A_B_single',False,False,-1,np.single],
        ['eq2_A_B_tr_single',False,True,-1,np.single],
        ['eq2_A_tr_B_single',True,False,-1,np.single],
        ['eq2_A_tr_B_tr_single',True,True,-1,np.single]

    ]

class TestStandardSylvesterSolver(unittest.TestCase):

    def get_data(self, shape = 'G', N = N, precision=np.double):
        A = generate_nsym_stbl_matrix(N).copy(order='F')
        B = generate_nsym_stbl_matrix(N).copy(order='F')
        Y = np.matmul(np.random.rand(N,1), np.random.rand(1,N)).copy(order='F')
        A = A.astype(precision)
        B = B.astype(precision)
        Y = Y.astype(precision)
        if shape == 'H':
            if precision == np.double:
                AH = np.triu(linalg.lapack.dgehrd(A)[0], -1)
                BH = np.triu(linalg.lapack.dgehrd(B)[0], -1)
            elif precision == np.single:
                AH = np.triu(linalg.lapack.sgehrd(A)[0], -1)
                BH = np.triu(linalg.lapack.sgehrd(B)[0], -1)
            return (AH,BH,Y)
        elif shape == 'F':
            if precision == np.double:
                A_Schur = linalg.lapack.dgees(lambda: None, A)
                B_Schur = linalg.lapack.dgees(lambda: None, B)
            elif precision == np.single:
                A_Schur = linalg.lapack.sgees(lambda: None, A)
                B_Schur = linalg.lapack.sgees(lambda: None, B)
            return (A,B,Y,A_Schur,B_Schur)
        elif shape == 'G':
            return (A,B,Y)
        else:
            raise ValueError('unknown shape')


    def rel_residual(self, transA, transB, sgn, A, B, X, Y):
        return pymepack.res_gesylv(A, B, X, Y, transa = transA, transb = transB,
                sign = sgn)

    @parameterized.expand(gesylv_test_parameters)
    def test_gesylv_gem_inplace(self, name, trans_A, trans_B, sgn, precision):
        (A,B,Y) = self.get_data(precision=precision)
        (A_c,B_c,X) = (A.copy(order='F'),B.copy(order='F'),Y.copy(order='F'))
        pymepack.gesylv(A_c, B_c, X, sgn=sgn, trans_A=trans_A, trans_B=trans_B,
                        inplace=True)
        self.assertLess(
                self.rel_residual(trans_A, trans_B, sgn, A,B,X,Y),
                bound(precision))

    @parameterized.expand(gesylv_test_parameters)
    def test_gesylv_gem_copy(self, name, trans_A, trans_B, sgn, precision):
        (A,B,Y) = self.get_data(precision=precision)
        (A_c,B_c,X) = (A.copy(order='F'),B.copy(order='F'),Y.copy(order='F'))

        res,_,_,_,_ = pymepack.gesylv(A_c, B_c, X,
                    sgn=sgn, trans_A=trans_A, trans_B=trans_B,inplace=False)

        self.assertTrue((A_c == A).all())
        self.assertTrue((B_c == B).all())
        self.assertTrue((X == Y).all())
        self.assertLess(
                self.rel_residual(trans_A, trans_B, sgn, A,B,res,Y),
                bound(precision))

    @parameterized.expand(gesylv_test_parameters)
    def test_gesylv_schur_inplace(self, name, trans_A, trans_B, sgn,precision):
        (A,B,Y,A_Schur,B_Schur) = self.get_data(shape='F',precision=precision)
        X = Y.copy(order='F')

        pymepack.gesylv(A_Schur[0].copy(order='F'), B_Schur[0].copy(order='F'),
                X, A_Schur[4].copy(order='F'), B_Schur[4].copy(order='F'),
                sgn=sgn, trans_A = trans_A, trans_B = trans_B, inplace=True)

        self.assertLess(
                self.rel_residual(trans_A, trans_B, sgn, A,B,X,Y),
                bound(precision))

    @parameterized.expand(gesylv_test_parameters)
    def test_gesylv_schur_copy(self, name, trans_A, trans_B, sgn, precision):
        (A,B,Y,A_Schur,B_Schur) = self.get_data(shape='F', precision=precision)
        X = Y.copy(order='F')

        res,_,_,_,_ = pymepack.gesylv(
                A_Schur[0].copy(order='F'), B_Schur[0].copy(order='F'),
                X, A_Schur[4].copy(order='F'), B_Schur[4].copy(order='F'),
                sgn=sgn, trans_A = trans_A, trans_B = trans_B,inplace=False)

        self.assertTrue((X == Y).all())
        self.assertLess(
                self.rel_residual(trans_A, trans_B, sgn, A,B,res,Y),
                bound(precision))

    @parameterized.expand(gesylv_test_parameters)
    def test_gesylv_hess_inplace(self, name, trans_A, trans_B, sgn, precision):
        (A,B,Y) = self.get_data(shape = 'H', precision=precision)
        (A_c,B_c,X) = (A.copy(order='F'),B.copy(order='F'),Y.copy(order='F'))
        pymepack.gesylv(A_c, B_c, X, hess_A=True, hess_B=True,
                sgn=sgn, trans_A=trans_A, trans_B=trans_B, inplace=True)
        self.assertLess(
                self.rel_residual(trans_A, trans_B, sgn, A,B,X,Y),
                bound(precision))

    @parameterized.expand(gesylv_test_parameters)
    def test_gesylv_hess_copy(self, name, trans_A, trans_B, sgn, precision):
        (A,B,Y) = self.get_data(shape = 'H', precision=precision)
        (A_c,B_c,X) = (A.copy(order='F'),B.copy(order='F'),Y.copy(order='F'))

        res,_,_,_,_ = pymepack.gesylv(A_c, B_c, X, hess_A=True, hess_B=True,
                    sgn=sgn, trans_A=trans_A, trans_B=trans_B,inplace=False)

        self.assertTrue((A_c == A).all())
        self.assertTrue((B_c == B).all())
        self.assertTrue((X == Y).all())
        self.assertLess(
                self.rel_residual(trans_A, trans_B, sgn, A,B,res,Y),
                bound(precision))

    @parameterized.expand(gesylv_test_parameters)
    def test_gesylv_refine(self, name, trans_A, trans_B, sgn, precision):
        (A,B,Y,A_Schur,B_Schur) = self.get_data(shape='F', precision=precision)

        (X_refined, max_it, tau, convlog) = pymepack.gesylv_refine(
                    A, B, Y, AS = A_Schur[0], BS = B_Schur[0],
                    Q = A_Schur[4], R = B_Schur[4], sgn = sgn,
                    trans_A = trans_A, trans_B = trans_B
                    )
        self.assertLess(
                self.rel_residual(trans_A,trans_B, sgn, A,B, X_refined,Y),
                bound(precision),
                not_within_bound_err_msg)

        res_no_ref,_,_,_,_ = pymepack.gesylv(
                A_Schur[0].copy(order='F'), B_Schur[0].copy(order='F'),
                Y, A_Schur[4].copy(order='F'), B_Schur[4].copy(order='F'),
                sgn=sgn, trans_A = trans_A, trans_B = trans_B,inplace=False)

        self.assertLess(
                self.rel_residual(trans_A,trans_B,sgn, A,B, X_refined,Y),
                self.rel_residual(trans_A,trans_B,sgn, A,B, res_no_ref,Y),
                no_improvement_err_msg)

class TestStandardSylvesterSolver2(unittest.TestCase):

    def get_data(self, shape = 'G', N = N, precision=np.double):
        A = generate_nsym_stbl_matrix(N).copy(order='F')
        B = generate_nsym_stbl_matrix(N).copy(order='F')
        Y = np.matmul(np.random.rand(N,1), np.random.rand(1,N)).copy(order='F')
        A = A.astype(precision)
        B = B.astype(precision)
        Y = Y.astype(precision)
        if shape == 'H':
            if precision == np.double:
                AH = np.triu(linalg.lapack.dgehrd(A)[0], -1)
                BH = np.triu(linalg.lapack.dgehrd(B)[0], -1)
            elif precision == np.single:
                AH = np.triu(linalg.lapack.sgehrd(A)[0], -1)
                BH = np.triu(linalg.lapack.sgehrd(B)[0], -1)
            return (AH,BH,Y)
        elif shape == 'F':
            if precision == np.double:
                A_Schur = linalg.lapack.dgees(lambda: None, A)
                B_Schur = linalg.lapack.dgees(lambda: None, B)
            elif precision == np.single:
                A_Schur = linalg.lapack.sgees(lambda: None, A)
                B_Schur = linalg.lapack.sgees(lambda: None, B)
            return (A,B,Y,A_Schur,B_Schur)
        elif shape == 'G':
            return (A,B,Y)
        else:
            raise ValueError('unknown shape')

    def rel_residual(self, transA, transB, sgn, A, B, X, Y):
        return pymepack.res_gesylv2(A, B, X, Y, transa = transA, transb = transB, sign = sgn)

    @parameterized.expand(gesylv_test_parameters)
    def test_gesylv2_gem_inplace(self, name, trans_A, trans_B, sgn, precision):
        (A,B,Y) = self.get_data(precision=precision)
        (A_c,B_c,X) = (A.copy(order='F'),B.copy(order='F'),Y.copy(order='F'))
        pymepack.gesylv2(A_c, B_c, X, sgn=sgn, trans_A=trans_A,trans_B=trans_B,
                         inplace=True)
        self.assertLess(
                self.rel_residual(trans_A, trans_B, sgn, A,B,X,Y),
                bound(precision))

    @parameterized.expand(gesylv_test_parameters)
    def test_gesylv2_gem_copy(self, name, trans_A, trans_B, sgn, precision):
        (A,B,Y) = self.get_data(precision=precision)
        (A_c,B_c,X) = (A.copy(order='F'),B.copy(order='F'),Y.copy(order='F'))

        res,_,_,_,_ = pymepack.gesylv2(A_c, B_c, X,
                    sgn=sgn, trans_A=trans_A, trans_B=trans_B,inplace=False)

        self.assertTrue((A_c == A).all())
        self.assertTrue((B_c == B).all())
        self.assertTrue((X == Y).all())
        self.assertLess(
                self.rel_residual(trans_A, trans_B, sgn, A,B,res,Y),
                bound(precision))

    @parameterized.expand(gesylv_test_parameters)
    def test_gesylv2_schur_inplace(self, name, trans_A, trans_B, sgn, precision):
        (A,B,Y,A_Schur,B_Schur) = self.get_data(shape='F', precision=precision)
        X = Y.copy(order='F')

        pymepack.gesylv2(A_Schur[0].copy(order='F'),B_Schur[0].copy(order='F'),
                X, A_Schur[4].copy(order='F'), B_Schur[4].copy(order='F'),
                sgn=sgn, trans_A = trans_A, trans_B = trans_B, inplace=True)

        self.assertLess(
                self.rel_residual(trans_A, trans_B, sgn, A,B,X,Y),
                bound(precision))

    @parameterized.expand(gesylv_test_parameters)
    def test_gesylv2_schur_copy(self, name, trans_A, trans_B, sgn, precision):
        (A,B,Y,A_Schur,B_Schur) = self.get_data(shape='F', precision=precision)
        X = Y.copy(order='F')

        res,_,_,_,_ = pymepack.gesylv2(
                A_Schur[0].copy(order='F'), B_Schur[0].copy(order='F'),
                X, A_Schur[4].copy(order='F'), B_Schur[4].copy(order='F'),
                sgn=sgn, trans_A = trans_A, trans_B = trans_B,inplace=False)

        self.assertTrue((X == Y).all())
        self.assertLess(
                self.rel_residual(trans_A, trans_B, sgn, A,B,res,Y),
                bound(precision))

    @parameterized.expand(gesylv_test_parameters)
    def test_gesylv2_hess_inplace(self, name, trans_A, trans_B, sgn, precision):
        (A,B,Y) = self.get_data(shape='H', precision=precision)
        (A_c,B_c,X) = (A.copy(order='F'),B.copy(order='F'),Y.copy(order='F'))
        pymepack.gesylv2(A_c, B_c, X, hess_A=True, hess_B=True,
                sgn=sgn, trans_A=trans_A,trans_B=trans_B, inplace=True)
        self.assertLess(
                self.rel_residual(trans_A, trans_B, sgn, A,B,X,Y),
                bound(precision))

    @parameterized.expand(gesylv_test_parameters)
    def test_gesylv2_hess_copy(self, name, trans_A, trans_B, sgn, precision):
        (A,B,Y) = self.get_data(shape='H', precision=precision)
        (A_c,B_c,X) = (A.copy(order='F'),B.copy(order='F'),Y.copy(order='F'))

        res,_,_,_,_ = pymepack.gesylv2(A_c, B_c, X, hess_A=True, hess_B=True,
                    sgn=sgn, trans_A=trans_A, trans_B=trans_B,inplace=False)

        self.assertTrue((A_c == A).all())
        self.assertTrue((B_c == B).all())
        self.assertTrue((X == Y).all())
        self.assertLess(
                self.rel_residual(trans_A, trans_B, sgn, A,B,res,Y),
                bound(precision))

    @parameterized.expand(gesylv_test_parameters)
    def test_gesylv2_refine(self, name, trans_A, trans_B, sgn, precision):
        (A,B,Y,A_Schur,B_Schur) = self.get_data(shape='F', precision=precision)

        (X_refined, max_it, tau, convlog) = pymepack.gesylv2_refine(
                    A, B, Y, AS = A_Schur[0], BS = B_Schur[0],
                    Q = A_Schur[4], R = B_Schur[4], sgn = sgn,
                    trans_A = trans_A, trans_B = trans_B
                    )
        self.assertLess(
                self.rel_residual(trans_A,trans_B, sgn, A,B, X_refined,Y),
                bound(precision),
                not_within_bound_err_msg)

        res_no_ref,_,_,_,_ = pymepack.gesylv2(
                A_Schur[0].copy(order='F'), B_Schur[0].copy(order='F'),
                Y, A_Schur[4].copy(order='F'), B_Schur[4].copy(order='F'),
                sgn=sgn, trans_A = trans_A, trans_B = trans_B,inplace=False)

        self.assertLess(
                self.rel_residual(trans_A,trans_B,sgn, A,B, X_refined,Y),
                self.rel_residual(trans_A,trans_B,sgn, A,B, res_no_ref,Y),
                no_improvement_err_msg)

ggsylv_test_parameters = [
        ['A_B_p_double',False,False,1,np.double],
        ['A_B_tr_p_double',False,True,1,np.double],
        ['A_tr_B_p_double',True,False,1,np.double],
        ['A_tr_B_tr_p_double',True,True,1,np.double],
        ['A_B_m_double',False,False,-1,np.double],
        ['A_B_tr_m_double',False,True,-1,np.double],
        ['A_tr_B_m_double',True,False,-1,np.double],
        ['A_tr_B_tr_m_double',True,True,-1,np.double],
        ['A_B_p_single',False,False,1,np.single],
        ['A_B_tr_p_single',False,True,1,np.single],
        ['A_tr_B_p_single',True,False,1,np.single],
        ['A_tr_B_tr_p_single',True,True,1,np.single],
        ['A_B_m_single',False,False,-1,np.single],
        ['A_B_tr_m_single',False,True,-1,np.single],
        ['A_tr_B_m_single',True,False,-1,np.single],
        ['A_tr_B_tr_m_single',True,True,-1,np.single]
    ]
class TestGGSylvSolver(unittest.TestCase):

    def get_data(self, fact = False, N = N, precision=np.double):
        A = generate_nsym_stbl_matrix(N).copy(order='F')
        B = generate_nsym_stbl_matrix(N).copy(order='F')
        C = generate_nsym_stbl_matrix(N).copy(order='F')
        D = generate_nsym_stbl_matrix(N).copy(order='F')
        Y = np.matmul(np.random.rand(N,1), np.random.rand(1,N)).copy(order='F')

        A = A.astype(precision)
        B = B.astype(precision)
        C = C.astype(precision)
        D = C.astype(precision)
        Y = Y.astype(precision)
        return (A,B,C,D,Y)

    def rel_residual(self,transA,transB,sgn,A, B, C, D, X, Y):
        return pymepack.res_ggsylv(A, B, C, D, X, Y, transa = transA,
                transb = transB, sign = sgn)

    @parameterized.expand(ggsylv_test_parameters)
    def test_ggsylv_gem_inplace(self, name, trans_A, trans_B, sgn, precision):
        (A,B,C,D,Y) = self.get_data(precision=precision)
        (A_c,B_c,C_c,D_c,X) = (A.copy(order='F'),B.copy(order='F'),
                                 C.copy(order='F'),D.copy(order='F'),
                                 Y.copy(order='F'))
        pymepack.ggsylv(A_c, B_c, C_c, D_c, X, sgn=sgn,
                         trans_AC = trans_A, trans_BD = trans_B, inplace=True)
        self.assertLess(
                self.rel_residual(trans_A,trans_B,sgn,A,B,C,D,X,Y),
                bound(precision))

    @parameterized.expand(ggsylv_test_parameters)
    def test_ggsylv_gem_copy(self, name, trans_A, trans_B, sgn, precision):
        (A,B,C,D,Y) = self.get_data(precision=precision)
        (A_c,B_c,C_c,D_c,X) = (A.copy(order='F'),B.copy(order='F'),
                                 C.copy(order='F'),D.copy(order='F'),
                                 Y.copy(order='F'))
        X_out,_,_,_,_,_,_,_,_ = pymepack.ggsylv(A_c, B_c, C_c, D_c, X, sgn=sgn,
                         trans_AC=trans_A, trans_BD=trans_B, inplace=False)

        self.assertTrue((A_c == A).all())
        self.assertTrue((B_c == B).all())
        self.assertTrue((C_c == C).all())
        self.assertTrue((D_c == D).all())
        self.assertTrue((X == Y).all())
        self.assertLess(
                self.rel_residual(trans_A,trans_B,sgn,A,B,C,D,X_out,Y),
                bound(precision))

    @parameterized.expand(ggsylv_test_parameters)
    def test_ggsylv_schur_inplace(self, name, trans_A, trans_B, sgn, precision):
        (A,B,C,D,Y) = self.get_data(precision=precision)
        A_c, C_c, QA, ZA = linalg.qz(A,C)[0:4]
        B_c, D_c, QB, ZB = linalg.qz(B,D)[0:4]
        X = Y.copy(order='F')

        pymepack.ggsylv(A_c, B_c, C_c, D_c, X, QA, ZA, QB, ZB, sgn=sgn, 
                        trans_AC=trans_A,trans_BD=trans_B, inplace=True)
        self.assertLess(
                self.rel_residual(trans_A, trans_B, sgn,A,B,C,D,X,Y),
                bound(precision))

    @parameterized.expand(ggsylv_test_parameters)
    def test_ggsylv_schur_copy(self, name, trans_A, trans_B, sgn, precision):
        (A,B,C,D,Y) = self.get_data(precision=precision)
        A_c, C_c, QA, ZA = linalg.qz(A,C)[0:4]
        B_c, D_c, QB, ZB = linalg.qz(B,D)[0:4]
        X = Y.copy(order='F')


        X_out,_,_,_,_,_,_,_,_ = pymepack.ggsylv(A_c, B_c, C_c, D_c, X,
                             QA, ZA, QB, ZB, sgn=sgn, trans_AC = trans_A,
                             trans_BD = trans_B, inplace=False)

        self.assertTrue((X == Y).all())
        self.assertLess(
                self.rel_residual(trans_A,trans_B,sgn,A,B,C,D,X_out,Y),
                bound(precision))

    @parameterized.expand(ggsylv_test_parameters)
    def test_ggsylv_hess_inplace(self, name, trans_A, trans_B, sgn, precision):
        (A,B,C,D,Y) = self.get_data(precision=precision)
        generalized_hess_form(A,C,precision=precision)
        generalized_hess_form(B,D,precision=precision)
        (A_c,B_c,C_c,D_c,X) = (A.copy(order='F'),B.copy(order='F'),
                                 C.copy(order='F'),D.copy(order='F'),
                                 Y.copy(order='F'))
        pymepack.ggsylv(A_c, B_c, C_c, D_c, X, sgn=sgn, hess_AC = True,
                hess_BD=True, trans_AC=trans_A, trans_BD=trans_B, inplace=True)
        self.assertLess(
                self.rel_residual(trans_A,trans_B,sgn,A,B,C,D,X,Y),
                bound(precision))

    @parameterized.expand(ggsylv_test_parameters)
    def test_ggsylv_hess_copy(self, name, trans_A, trans_B, sgn, precision):
        (A,B,C,D,Y) = self.get_data(precision=precision)
        generalized_hess_form(A,C,precision=precision)
        generalized_hess_form(B,D,precision=precision)
        (A_c,B_c,C_c,D_c,X) = (A.copy(order='F'),B.copy(order='F'),
                                 C.copy(order='F'),D.copy(order='F'),
                                 Y.copy(order='F'))
        X_out, *_ = pymepack.ggsylv(A_c, B_c, C_c, D_c, X, sgn=sgn,
                hess_AC=True, hess_BD=True, trans_AC=trans_A, trans_BD=trans_B,
                inplace=False)

        self.assertTrue((A_c == A).all())
        self.assertTrue((B_c == B).all())
        self.assertTrue((C_c == C).all())
        self.assertTrue((D_c == D).all())
        self.assertTrue((X == Y).all())
        self.assertLess(
                self.rel_residual(trans_A,trans_B,sgn,A,B,C,D,X_out,Y),
                bound(precision))

    @parameterized.expand(ggsylv_test_parameters)
    def test_ggsylv_refine(self, name, trans_A, trans_B, sgn, precision):
        (A,B,C,D,Y) = self.get_data(precision=precision)
        AS,CS,Q,Z = linalg.qz(A,C)[0:4]
        BS,DS,U,V = linalg.qz(B,D)[0:4]

        X_refined, max_it, tau, convlog = pymepack.ggsylv_refine(
                    A, B, C, D, Y, AS = AS, BS = BS, CS = CS, DS = DS,
                    Q = Q, Z = Z, U = U, V = V, sgn = sgn,
                    trans_AC = trans_A, trans_BD = trans_B
                    )
        self.assertLess(
             self.rel_residual(trans_A,trans_B, sgn, A,B,C,D,X_refined,Y),
             bound(precision),
             not_within_bound_err_msg)

        X_no_ref,_,_,_,_,_,_,_,_ = pymepack.ggsylv(AS, BS, CS, DS, Y,
                             Q, Z, U, V, sgn=sgn, trans_AC = trans_A,
                             trans_BD = trans_B, inplace=False)

        self.assertLess(
             self.rel_residual(trans_A,trans_B,sgn,A,B,C,D,X_refined,Y),
             self.rel_residual(trans_A,trans_B,sgn,A,B,C,D, X_no_ref,Y),
             no_improvement_err_msg)



ggcsylv_test_parameters = [
        ['A_B_pp_double',False,False,1,1,np.double],
        ['A_B_tr_pp_double',False,True,1,1,np.double],
        ['A_tr_B_pp_double',True,False,1,1,np.double],
        ['A_tr_B_tr_pp_double',True,True,1,1,np.double],
        ['A_B_mp_double',False,False,-1,1,np.double],
        ['A_B_tr_mp_double',False,True,-1,1,np.double],
        ['A_tr_B_mp_double',True,False,-1,1,np.double],
        ['A_tr_B_tr_mp_double',True,True,-1,1,np.double],
        ['A_B_pm_double',False,False,1,-1,np.double],
        ['A_B_tr_pm_double',False,True,1,-1,np.double],
        ['A_tr_B_pm_double',True,False,1,-1,np.double],
        ['A_tr_B_tr_pm_double',True,True,1,-1,np.double],
        ['A_B_mm_double',False,False,-1,-1,np.double],
        ['A_B_tr_mm_double',False,True,-1,-1,np.double],
        ['A_tr_B_mm_double',True,False,-1,-1,np.double],
        ['A_tr_B_tr_mm_double',True,True,-1,-1,np.double],
        ['A_B_pp_single',False,False,1,1,np.single],
        ['A_B_tr_pp_single',False,True,1,1,np.single],
        ['A_tr_B_pp_single',True,False,1,1,np.single],
        ['A_tr_B_tr_pp_single',True,True,1,1,np.single],
        ['A_B_mp_single',False,False,-1,1,np.single],
        ['A_B_tr_mp_single',False,True,-1,1,np.single],
        ['A_tr_B_mp_single',True,False,-1,1,np.single],
        ['A_tr_B_tr_mp_single',True,True,-1,1,np.single],
        ['A_B_pm_single',False,False,1,-1,np.single],
        ['A_B_tr_pm_single',False,True,1,-1,np.single],
        ['A_tr_B_pm_single',True,False,1,-1,np.single],
        ['A_tr_B_tr_pm_single',True,True,1,-1,np.single],
        ['A_B_mm_single',False,False,-1,-1,np.single],
        ['A_B_tr_mm_single',False,True,-1,-1,np.single],
        ['A_tr_B_mm_single',True,False,-1,-1,np.single],
        ['A_tr_B_tr_mm_single',True,True,-1,-1,np.single]
    ]

class TestGGCSylvSolver(unittest.TestCase):

    def get_data(self, fact = False, N = N, precision=np.double):
        A = generate_nsym_stbl_matrix(N).copy(order='F')
        B = generate_nsym_stbl_matrix(N).copy(order='F')
        C = generate_nsym_stbl_matrix(N).copy(order='F')
        D = generate_nsym_stbl_matrix(N).copy(order='F')
        E = np.matmul(np.random.rand(N,1), np.random.rand(1,N)).copy(order='F')
        F = np.matmul(np.random.rand(N,1), np.random.rand(1,N)).copy(order='F')

        A = A.astype(precision)
        B = B.astype(precision)
        C = C.astype(precision)
        D = D.astype(precision)
        E = E.astype(precision)
        F = F.astype(precision)
        return (A,B,C,D,E,F)

    def rel_residual(self,transA,transB,sgn1,sgn2,A, B, C, D, E, F, R, L):
        return pymepack.res_ggcsylv(A, B, C, D, R, L, E, F,
                transa = transA, transb = transB, sign1 = sgn1, sign2 = sgn2)

    @parameterized.expand(ggcsylv_test_parameters)
    def test_ggcsylv_gem_inplace(self, name, trans_A, trans_B, sgn1, sgn2, precision):
        (A,B,C,D,E,F) = self.get_data(precision=precision)
        (A_c,B_c,C_c,D_c,R,L) = (A.copy(order='F'),B.copy(order='F'),
                                 C.copy(order='F'),D.copy(order='F'),
                                 E.copy(order='F'),F.copy(order='F'))
        pymepack.ggcsylv(A_c, B_c, C_c, D_c, R, L, sgn1=sgn1, sgn2=sgn2,
                         trans_AC = trans_A, trans_BD = trans_B, inplace=True)
        self.assertLess(
                self.rel_residual(trans_A, trans_B, sgn1, sgn2,
                                       A,B,C,D,E,F,R,L),
                bound(precision))

    @parameterized.expand(ggcsylv_test_parameters)
    def test_ggcsylv_gem_copy(self, name, trans_A, trans_B, sgn1, sgn2, precision):
        (A,B,C,D,E,F) = self.get_data(precision=precision)
        (A_c,B_c,C_c,D_c,R,L) = (A.copy(order='F'),B.copy(order='F'),
                                 C.copy(order='F'),D.copy(order='F'),
                                 E.copy(order='F'),F.copy(order='F'))
        R_out,L_out,_,_,_,_,_,_,_,_= pymepack.ggcsylv(A_c, B_c, C_c, D_c, R, L,
                             sgn1=sgn1, sgn2=sgn2, trans_AC = trans_A,
                             trans_BD = trans_B, inplace=False)

        self.assertTrue((A_c == A).all())
        self.assertTrue((B_c == B).all())
        self.assertTrue((C_c == C).all())
        self.assertTrue((D_c == D).all())
        self.assertTrue((E == R).all())
        self.assertTrue((F == L).all())
        self.assertLess(
                self.rel_residual(trans_A,trans_B,sgn1,sgn2,
                                        A,B,C,D,E,F,R_out,L_out),
                bound(precision))

    @parameterized.expand(ggcsylv_test_parameters)
    def test_ggcsylv_schur_inplace(self, name, trans_A, trans_B, sgn1, sgn2, precision):
        (A,B,C,D,E,F) = self.get_data(precision=precision)
        A_c, C_c, QA, ZA = linalg.qz(A,C)[0:4]
        B_c, D_c, QB, ZB = linalg.qz(B,D)[0:4]
        R = E.copy(order='F')
        L = F.copy(order='F')

        pymepack.ggcsylv(A_c, B_c, C_c, D_c, R, L, QA, ZA, QB, ZB,
                         sgn1=sgn1, sgn2=sgn2, trans_AC = trans_A,
                         trans_BD = trans_B, inplace=True)
        self.assertLess(
                self.rel_residual(trans_A, trans_B, sgn1, sgn2,
                                       A,B,C,D,E,F,R,L),
                bound(precision))

    @parameterized.expand(ggcsylv_test_parameters)
    def test_ggcsylv_schur_copy(self, name, trans_A, trans_B, sgn1, sgn2, precision):
        (A,B,C,D,E,F) = self.get_data(precision=precision)
        A_c, C_c, QA, ZA = linalg.qz(A,C)[0:4]
        B_c, D_c, QB, ZB = linalg.qz(B,D)[0:4]
        R = E.copy(order='F')
        L = F.copy(order='F')


        R_out,L_out,_,_,_,_,_,_,_,_=pymepack.ggcsylv(A_c, B_c, C_c, D_c, R, L,
                             QA, ZA, QB, ZB,
                             sgn1=sgn1, sgn2=sgn2, trans_AC = trans_A,
                             trans_BD = trans_B, inplace=False)

        self.assertTrue((E == R).all())
        self.assertTrue((F == L).all())
        self.assertLess(
                self.rel_residual(trans_A,trans_B,sgn1,sgn2,
                                        A,B,C,D,E,F,R_out,L_out),
                bound(precision))

    @parameterized.expand(ggcsylv_test_parameters)
    def test_ggcsylv_hess_inplace(self, name, trans_A, trans_B, sgn1, sgn2, precision):
        (A,B,C,D,E,F) = self.get_data(precision=precision)
        generalized_hess_form(A,C,precision=precision)
        generalized_hess_form(B,D,precision=precision)
        (A_c,B_c,C_c,D_c,R,L) = (A.copy(order='F'),B.copy(order='F'),
                                 C.copy(order='F'),D.copy(order='F'),
                                 E.copy(order='F'),F.copy(order='F'))
        pymepack.ggcsylv(A_c, B_c, C_c, D_c, R, L, sgn1=sgn1, sgn2=sgn2,
                         hess_AC=True, hess_BD=True,
                         trans_AC = trans_A, trans_BD = trans_B, inplace=True)
        self.assertLess(
                self.rel_residual(trans_A, trans_B, sgn1, sgn2,
                                       A,B,C,D,E,F,R,L),
                bound(precision))

    @parameterized.expand(ggcsylv_test_parameters)
    def test_ggcsylv_hess_copy(self, name, trans_A, trans_B, sgn1, sgn2, precision):
        (A,B,C,D,E,F) = self.get_data(precision=precision)
        generalized_hess_form(A,C,precision=precision)
        generalized_hess_form(B,D,precision=precision)
        (A_c,B_c,C_c,D_c,R,L) = (A.copy(order='F'),B.copy(order='F'),
                                 C.copy(order='F'),D.copy(order='F'),
                                 E.copy(order='F'),F.copy(order='F'))
        R_out,L_out,*_= pymepack.ggcsylv(A_c, B_c, C_c, D_c, R, L,
                             sgn1=sgn1, sgn2=sgn2, hess_AC=True, hess_BD=True,
                             trans_AC = trans_A, trans_BD = trans_B,
                             inplace=False)

        self.assertTrue((A_c == A).all())
        self.assertTrue((B_c == B).all())
        self.assertTrue((C_c == C).all())
        self.assertTrue((D_c == D).all())
        self.assertTrue((E == R).all())
        self.assertTrue((F == L).all())
        self.assertLess(
                self.rel_residual(trans_A,trans_B,sgn1,sgn2,
                                        A,B,C,D,E,F,R_out,L_out),
                bound(precision))

    @parameterized.expand(ggcsylv_test_parameters)
    def test_ggcsylv_refine(self, name, trans_A, trans_B, sgn1, sgn2, precision):
        (A,B,C,D,E,F) = self.get_data(precision=precision)
        AS,CS,Q,Z = linalg.qz(A,C)[0:4]
        BS,DS,U,V = linalg.qz(B,D)[0:4]
        R_refined, L_refined, _,_,_ = pymepack.ggcsylv_refine(
                    A, B, C, D, E, F, AS = AS, BS = BS, CS = CS, DS = DS,
                    Q = Q, Z = Z, U = U, V = V, sgn1 = sgn1, sgn2 = sgn2,
                    trans_AC = trans_A, trans_BD = trans_B)
        self.assertLess(
             self.rel_residual(trans_A,trans_B, sgn1, sgn2,
                                    A,B,C,D,E,F,R_refined,L_refined),
             bound(precision),
             not_within_bound_err_msg)

        R_no_ref,L_no_ref,_,_,_,_,_,_,_,_ = pymepack.ggcsylv(AS, BS, CS, DS,
                             E, F, Q, Z, U, V,
                             sgn1=sgn1, sgn2=sgn2, trans_AC = trans_A,
                             trans_BD = trans_B, inplace=False)
        self.assertLess(
             self.rel_residual(trans_A,trans_B,sgn1,sgn2,
                                    A,B,C,D,E,F,R_refined,L_refined),
             self.rel_residual(trans_A,trans_B,sgn1,sgn2,
                                    A,B,C,D,E,F,R_no_ref,L_no_ref),
             no_improvement_err_msg)



class TestGGCSylvDualSolver(unittest.TestCase):

    def get_data(self, fact = False, N = N, precision=np.double):
        A = generate_nsym_stbl_matrix(N).copy(order='F')
        B = generate_nsym_stbl_matrix(N).copy(order='F')
        C = generate_nsym_stbl_matrix(N).copy(order='F')
        D = generate_nsym_stbl_matrix(N).copy(order='F')
        E = np.matmul(np.random.rand(N,1), np.random.rand(1,N)).copy(order='F')
        F = np.matmul(np.random.rand(N,1), np.random.rand(1,N)).copy(order='F')

        A = A.astype(precision)
        B = B.astype(precision)
        C = C.astype(precision)
        D = D.astype(precision)
        E = E.astype(precision)
        F = F.astype(precision)

        return (A,B,C,D,E,F)


    def rel_residual(self,transA,transB,sgn1,sgn2,A, B, C, D, E, F, R, L):
        return pymepack.res_ggcsylv_dual(A, B, C, D, R, L, E, F,
                transa = transA, transb = transB, sign1 = sgn1, sign2 = sgn2)

    @parameterized.expand(ggcsylv_test_parameters)
    def test_ggcsylv_dual_gem_inplace(self,name,trans_A,trans_B,sgn1,sgn2,precision):
        (A,B,C,D,E,F) = self.get_data(precision=precision)
        (A_c,B_c,C_c,D_c,R,L) = (A.copy(order='F'),B.copy(order='F'),
                                 C.copy(order='F'),D.copy(order='F'),
                                 E.copy(order='F'),F.copy(order='F'))
        pymepack.ggcsylv_dual(A_c, B_c, C_c, D_c, R, L, sgn1=sgn1, sgn2=sgn2,
                         trans_AC = trans_A, trans_BD = trans_B, inplace=True)
        self.assertLess(
                self.rel_residual(trans_A, trans_B, sgn1, sgn2,
                                       A,B,C,D,E,F,R,L),
                bound(precision))

    @parameterized.expand(ggcsylv_test_parameters)
    def test_ggcsylv_dual_gem_copy(self,name,trans_A,trans_B,sgn1,sgn2,precision):
        (A,B,C,D,E,F) = self.get_data(precision=precision)
        (A_c,B_c,C_c,D_c,R,L) = (A.copy(order='F'),B.copy(order='F'),
                                 C.copy(order='F'),D.copy(order='F'),
                                 E.copy(order='F'),F.copy(order='F'))
        R_out,L_out,_,_,_,_,_,_,_,_=pymepack.ggcsylv_dual(A_c,B_c,C_c,D_c,R,L,
                             sgn1=sgn1, sgn2=sgn2, trans_AC = trans_A,
                             trans_BD = trans_B, inplace=False)

        self.assertTrue((A_c == A).all())
        self.assertTrue((B_c == B).all())
        self.assertTrue((C_c == C).all())
        self.assertTrue((D_c == D).all())
        self.assertTrue((E == R).all())
        self.assertTrue((F == L).all())
        self.assertLess(
                self.rel_residual(trans_A,trans_B,sgn1,sgn2,
                                        A,B,C,D,E,F,R_out,L_out),
                bound(precision))

    @parameterized.expand(ggcsylv_test_parameters)
    def test_ggcsylv_dual_schur_inplace(self,name,trans_A,trans_B,sgn1,sgn2,precision):
        (A,B,C,D,E,F) = self.get_data(precision=precision)
        A_c, C_c, QA, ZA = linalg.qz(A,C)[0:4]
        B_c, D_c, QB, ZB = linalg.qz(B,D)[0:4]
        R = E.copy(order='F')
        L = F.copy(order='F')
        pymepack.ggcsylv_dual(A_c, B_c, C_c, D_c, R, L, QA, ZA, QB, ZB,
                sgn1=sgn1, sgn2=sgn2, trans_AC = trans_A, trans_BD = trans_B,
                inplace=True)
        self.assertLess(
                self.rel_residual(trans_A, trans_B, sgn1, sgn2,
                                       A,B,C,D,E,F,R,L),
                bound(precision))

    @parameterized.expand(ggcsylv_test_parameters)
    def test_ggcsylv_dual_schur_copy(self, name, trans_A, trans_B, sgn1, sgn2, precision):
        (A,B,C,D,E,F) = self.get_data(precision=precision)
        A_c, C_c, QA, ZA = linalg.qz(A,C)[0:4]
        B_c, D_c, QB, ZB = linalg.qz(B,D)[0:4]
        R = E.copy(order='F')
        L = F.copy(order='F')
        R_out,L_out,_,_,_,_,_,_,_,_ = pymepack.ggcsylv_dual(A_c, B_c, C_c, D_c,
                R, L, QA, ZA, QB, ZB, sgn1=sgn1, sgn2=sgn2, trans_AC = trans_A,
                trans_BD = trans_B, inplace = False)
        self.assertTrue((E == R).all())
        self.assertTrue((F == L).all())
        self.assertLess(
                self.rel_residual(trans_A, trans_B, sgn1, sgn2,
                                       A,B,C,D,E,F,R_out,L_out),
                bound(precision))

    @parameterized.expand(ggcsylv_test_parameters)
    def test_ggcsylv_dual_hess_inplace(self,name,trans_A,trans_B,sgn1,sgn2,precision):
        (A,B,C,D,E,F) = self.get_data(precision=precision)
        generalized_hess_form(A,C,precision=precision)
        generalized_hess_form(B,D,precision=precision)
        (A_c,B_c,C_c,D_c,R,L) = (A.copy(order='F'),B.copy(order='F'),
                                 C.copy(order='F'),D.copy(order='F'),
                                 E.copy(order='F'),F.copy(order='F'))
        pymepack.ggcsylv_dual(A_c, B_c, C_c, D_c, R, L, sgn1=sgn1, sgn2=sgn2,
                         hess_AC = True, hess_BD = True,
                         trans_AC = trans_A, trans_BD = trans_B, inplace=True)
        self.assertLess(
                self.rel_residual(trans_A, trans_B, sgn1, sgn2,
                                       A,B,C,D,E,F,R,L),
                bound(precision))

    @parameterized.expand(ggcsylv_test_parameters)
    def test_ggcsylv_dual_hess_copy(self,name,trans_A,trans_B,sgn1,sgn2,precision):
        (A,B,C,D,E,F) = self.get_data(precision=precision)
        generalized_hess_form(A,C,precision=precision)
        generalized_hess_form(B,D,precision=precision)
        (A_c,B_c,C_c,D_c,R,L) = (A.copy(order='F'),B.copy(order='F'),
                                 C.copy(order='F'),D.copy(order='F'),
                                 E.copy(order='F'),F.copy(order='F'))
        R_out,L_out,*_=pymepack.ggcsylv_dual(A_c,B_c,C_c,D_c,R,L,
                sgn1=sgn1, sgn2=sgn2, hess_AC=True, hess_BD=True,
                trans_AC = trans_A, trans_BD = trans_B, inplace=False)

        self.assertTrue((A_c == A).all())
        self.assertTrue((B_c == B).all())
        self.assertTrue((C_c == C).all())
        self.assertTrue((D_c == D).all())
        self.assertTrue((E == R).all())
        self.assertTrue((F == L).all())
        self.assertLess(
                self.rel_residual(trans_A,trans_B,sgn1,sgn2,
                                        A,B,C,D,E,F,R_out,L_out),
                bound(precision))

    @parameterized.expand(ggcsylv_test_parameters)
    def test_ggcsylv_dual_refine(self, name, trans_A, trans_B, sgn1, sgn2, precision):
        (A,B,C,D,E,F) = self.get_data(precision=precision)
        AS,CS,Q,Z = linalg.qz(A,C)[0:4]
        BS,DS,U,V = linalg.qz(B,D)[0:4]
        R_refined, L_refined, _,_,_ = pymepack.ggcsylv_dual_refine(
                    A, B, C, D, E, F, AS = AS, BS = BS, CS = CS, DS = DS,
                    Q = Q, Z = Z, U = U, V = V, sgn1 = sgn1, sgn2 = sgn2,
                    trans_AC = trans_A, trans_BD = trans_B)
        self.assertLess(
             self.rel_residual(trans_A,trans_B, sgn1, sgn2,
                                    A,B,C,D,E,F,R_refined,L_refined),
             bound(precision),
             not_within_bound_err_msg)

        R_no_ref,L_no_ref,_,_,_,_,_,_,_,_ = pymepack.ggcsylv_dual(AS, BS,
                             CS, DS, E, F, Q, Z, U, V,
                             sgn1=sgn1, sgn2=sgn2, trans_AC = trans_A,
                             trans_BD = trans_B, inplace=False)
        self.assertLess(
             self.rel_residual(trans_A,trans_B,sgn1,sgn2,
                                    A,B,C,D,E,F,R_refined,L_refined),
             self.rel_residual(trans_A,trans_B,sgn1,sgn2,
                                    A,B,C,D,E,F,R_no_ref,L_no_ref),
             no_improvement_err_msg)


if __name__ == '__main__':
    unittest.main(verbosity=2)
