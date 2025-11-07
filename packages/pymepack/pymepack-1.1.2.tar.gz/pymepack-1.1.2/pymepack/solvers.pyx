#
# pymepack - a python interface for MEPACK,
#
# Copyright (C) 2023 Martin Koehler, Aleksey Maleyko
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#



cimport pymepack_def
from scipy import linalg
from abc import ABC, abstractmethod
import numpy as np
cimport numpy as cnp


def gelyap(
        cnp.ndarray[numeric_t, ndim=2] A not None,
        cnp.ndarray[numeric_t, ndim=2] X not None,
        cnp.ndarray[numeric_t, ndim=2] Q = None,
        trans = False, hess = False,
        int block_size = 0, int solver = 1, inplace=False):
    """
    *wrapper for mepack_double_gelyap.*

    Solves a Lyapunov equation of the form
    ::

           A * X  +  X * A^T = Y               (1)
      or
           A^T * X  +  X * A = Y               (2)

    where A, the right hand side Y and the solution X are (n,n) matrices.
    The matrix A can be supplied either as a general matrix or upper
    Hessenberg matrix or factorized in terms of its Schur decomposition.

    The solver switches automatically between single and double precision
    based on the precision of input arrays.

    :param trans: Specifies the form of an equation with respect to A:

            == False:  Equation (1) is solved.

            == True:   Equation (2) is solved,

            defaults to False
    :type trans: bool, optional
    :param hess: Specifies if A is in upper Hessenberg form.
        If hess = True, the value of Q is ignored,
        defaults to False
    :type hess: bool, optional
    :param A:
        If hess == True,
            The matrix A is given as an upper Hessenberg matrix and its
            Schur decomposition A = Q*S*Q**T will be computed.
            A is overwritten with its schur decomposition S.

        Otherwise:

        If Q is None,
            The matrix A is given as a general matrix and its
            Schur decomposition A = Q*S*Q**T will be computed.
            A is overwritten with its schur decomposition S.
        If Q is not None,
           the matrix A contains its (quasi-) upper triangular matrix S
           being the Schur decomposition of A. A = Q*S*Q**T
    :type A: (n,n) numpy array
    :param Q:
        If Q is None, a (n,n) matrix containing the Schur vectors of A
            is returned.
        If Q is not None, it contains the Schur vectors of A, the matrix A
            contains its Schur decomposition,
            defaults to None
    :type Q: (n,n) numpy array,
        optional
    :param X:
        On input, X contains the right hand side Y.
        On output, X contains the solution of the Equation (1) or (2)
        Right hand side Y and the solution X are symmetric (n,n) matrices.
    :type X: (n,n) numpy array
    :param block_size: sets the block size for the equation,
        defaults to 0
    :type block_size: int, optional
    :param solver: sets solver, defaults to 1
    :type solver: int, optional
    :param inplace:
       if inplace=False, gelyap works with copies of the matrices,
       defaults to False
    :type inplace: bool,optional
    :raise ValueError:

        on A,Q or X type, shape or contingency mismatch

        when Q is not None and hess = True

    :return: (X, A, Q)

             if inplace == True, the tuple contains their references to the

             modified input matrices. Otherwise, the tuple contains their

             newly allocated copies.

    .. HINT::
       |hintFortranLayout|
    """
    if numeric_t is cnp.npy_float:
        pymepack_def.mepack_single_trlyap_blocksize_set (block_size)
    elif numeric_t is cnp.npy_double:
        pymepack_def.mepack_double_trlyap_blocksize_set (block_size)

    pymepack_def.mepack_trlyap_frontend_solver_set(solver)
    params = { 'A': A, 'Q': Q, 'X': X, 'trans_A': trans, 'hess_A': hess, 'inplace': inplace}
    return GelyapSolver(params).execute()


def gestein(
        cnp.ndarray[numeric_t, ndim=2] A not None,
        cnp.ndarray[numeric_t, ndim=2] X not None,
        cnp.ndarray[numeric_t, ndim=2] Q = None,
        trans = False, hess = False,
        int block_size = 0, int solver = 1, inplace=False):
    """
    *wrapper for mepack_double_gestein.*

    Solves a Stein equation of the form
    ::

          A * X * A^T - X = Y               (1)
      or
          A^T * X * A - X = Y               (2)

    where A, the right hand side Y and the solution X are (n,n) matrices.
    The matrix A can be supplied either as a general matrix or upper
    Hessenberg matrix or factorized in terms of its Schur decomposition.

    The solver switches automatically between single and double precision
    based on the precision of input arrays.

    :param trans: Specifies the form of an equation with respect to A:

            == False:  Equation (1) is solved.

            == True:   Equation (2) is solved,

            defaults to False
    :type trans: bool, optional
    :param hess: Specifies if A is in upper Hessenberg form.
        If hess = True, the value of Q is ignored,
        defaults to False
    :type hess: bool, optional
    :param A:
        If hess == True,
            The matrix A is given as an upper Hessenberg matrix and its
            Schur decomposition A = Q*S*Q**T will be computed.
            A is overwritten with its schur decomposition S.

        Otherwise:

        If Q is None,
            The matrix A is given as a general matrix and its
            Schur decomposition A = Q*S*Q**T will be computed.
            A is overwritten with its schur decomposition S.
        If Q is not None,
           the matrix A contains its (quasi-) upper triangular matrix S
           being the Schur decomposition of A. A = Q*S*Q**T
    :type A: (n,n) numpy array
    :param Q:
        If Q is None, a (n,n) matrix containing the Schur vectors of A
            is returned.
        If Q is not None, it contains the Schur vectors of A, the matrix A
            contains its Schur decomposition,
            defaults to None
    :type Q: (n,n) numpy array,
        optional
    :param X:
        On input, X contains the right hand side Y.
        On output, X contains the solution of the Equation (1) or (2)
        Right hand side Y and the solution X are symmetric (n,n) matrices.
    :type X: (n,n) numpy array
    :param block_size: sets the block size for the equation,
        defaults to 0
    :type block_size: int, optional
    :param solver: sets solver, defaults to 1
    :type solver: int, optional
    :param inplace:
       if inplace=False, gelyap works with copies of the matrices,
       defaults to False
    :type inplace: bool, optional
    :raise ValueError:

        on A,Q or X type, shape or contingency mismatch

        when Q is not None and hess = True

    :return: (X, A, Q)

             if inplace == True, the tuple contains their references to the

             modified input matrices. Otherwise, the tuple contains their

             newly allocated copies.

    .. HINT::
       |hintFortranLayout|
    """
    if numeric_t is cnp.npy_float:
        pymepack_def.mepack_single_trstein_blocksize_set (block_size)
    elif numeric_t is cnp.npy_double:
        pymepack_def.mepack_double_trstein_blocksize_set (block_size)

    pymepack_def.mepack_trstein_frontend_solver_set(solver)
    params = { 'A': A, 'Q': Q, 'X': X, 'trans_A': trans,'hess_A': hess ,'inplace': inplace}
    return GesteinSolver(params).execute()


def gglyap(
        cnp.ndarray[numeric_t, ndim=2] A not None,
        cnp.ndarray[numeric_t, ndim=2] B not None,
        cnp.ndarray[numeric_t, ndim=2] X not None,
        cnp.ndarray[numeric_t, ndim=2] Q = None,
        cnp.ndarray[numeric_t, ndim=2] Z = None,
        trans = False, hess = False,
        int block_size = 0, int solver = 1, inplace=False):
    """
    *wrapper for mepack_double_gglyap.*

    Solves a generalized Lyapunov equation of the form
    ::

          A * X * B^T + B * X * A^T = Y               (1)
      or
          A^T * X * B + B^T * X * A = Y               (2)

    where (A,B) is a (n,n) matrix pencil. The right hand side Y and
    the solution X are (n,n) matrices. The matrix pencil (A,B) is either
    in general form, in generalized Hessenberg form, or in generalized
    Schur form where Q and Z also need to be provided.

    The solver switches automatically between single and double precision
    based on the precision of input arrays.

    :param trans: Specifies the form of an equation with respect to A:

            == False:  Equation (1) is solved.

            == True:   Equation (2) is solved,

            defaults to False
    :type trans: bool, optional
    :param hess: Specifies if (A,B) is in generalized Hessenberg form.
        If hess = True, the values of Q and Z are ignored,
        defaults to False
    :type hess: bool, optional
    :param A:
        If hess == True,
            the matrix A is an upper Hessenberg matrix of the generalized
            Hessenberg form (A,B) and its Schur decomposition A = Q*S*Z**T
            will be computed.
            If inplace == True, A is overwritten with S.

        Otherwise:

        If Q and Z are None,
            The matrix A is given as a general matrix and it is overwritten
            with quasi upper triangular matrix S of the generalized
            schur decomposition of (A,B) where A = Q*S*Z^T.
        If Q and Z are not None,
            the matrix A contains its (quasi-) upper triangular matrix S
            of the generalized  Schur decomposition of (A,B).
    :type A: (n,n) numpy array
    :param B:
        If hess == True,
            the matrix B is the upper triangular matrix of the generalized
            Hessenberg form (A,B) and its Schur decomposition B = Q*R*Z**T
            will be computed.
            If inplace == True, B is overwritten with R.

        Otherwise:

        If Q and Z are None,
            the matrix B is given as general matrix and it is overwritten
            with the upper triangular matrix R of the generalized
            Schur decomposition of (A,B) where B = Q*R*Z^T.
        If Q and Z are not None,
            the matrix B contains its upper triangular matrix R of the
            generalized Schur decomposition of (A,B).
    :type B: (n,n) numpy array
    :param Q:
        If Q is None, a (n,n) matrix containing the left Schur vectors
            of (A,B) is returned.
        If Q is not None, it contains the left Schur vectors of (A,B),
            defaults to None
    :type Q: (n,n) numpy array,
        optional
    :param Z:
        If Z is None, a (n,n) matrix containing the right Schur vectors
            of (A,B) is returned.
        If Z is not None, it contains the right Schur vectors of (A,B),
            defaults to None
    :type Z: (n,n) numpy array,
        optional
    :param X:
        On input, X contains the right hand side Y.
        On output, X contains the solution of the Equation (1) or (2)
        Right hand side Y and the solution X are symmetric (n,n) matrices.
    :type X: (n,n) numpy array
    :param block_size: sets the block size for the equation,
        defaults to 0
    :type block_size: int, optional
    :param solver: sets solver, defaults to 1
    :type solver: int, optional
    :param inplace:
        if inplace=False, gelyap works with copies of the matrices,
        defaults to False
    :type inplace: bool, optional
    :raise ValueError: on A,B,Q,Z or X type, shape or contingency
        mismatch. The ValueError is also raised when Q and Z do not
        give the same result for the 'is None' test.
    :return: (X, A, B, Q, Z)

             if inplace == True, the tuple contains their references to the

             modified input matrices. Otherwise, the tuple contains their

             newly allocated copies.

    .. HINT::
       |hintFortranLayout|
    """
    if numeric_t is cnp.npy_float:
        pymepack_def.mepack_single_tglyap_blocksize_set (block_size)
    elif numeric_t is cnp.npy_double:
        pymepack_def.mepack_double_tglyap_blocksize_set (block_size)

    pymepack_def.mepack_tglyap_frontend_solver_set(solver)
    params = { 'A': A, 'B': B, 'Q': Q, 'Z': Z, 'X': X,
            'trans_A': trans, 'hess_AB': hess, 'inplace': inplace}
    return GGLyapSolver(params).execute()


def ggstein(
        cnp.ndarray[numeric_t, ndim=2] A not None,
        cnp.ndarray[numeric_t, ndim=2] B not None,
        cnp.ndarray[numeric_t, ndim=2] X not None,
        cnp.ndarray[numeric_t, ndim=2] Q = None,
        cnp.ndarray[numeric_t, ndim=2] Z = None,
        trans = False, hess = False,
        int block_size = 0, int solver = 1, inplace=False):
    """
    *wrapper for mepack_double_ggstein.*

    Solves a generalized Stein equation of the form
    ::

          A * X * A^T + B * X * B^T = Y           (1)
      or
          A^T * X * A + B^T * X * B = Y           (2)

    where (A,B) is a (n,n) matrix pencil. The right hand side Y and
    the solution X are (n,n) matrices. The matrix pencil (A,B) is either
    in general form, in generalized Hessenberg form, or in generalized
    Schur form where Q and Z also need to be provided.

    The solver switches automatically between single and double precision
    based on the precision of input arrays.

    :param trans: Specifies the form of an equation with respect to A:

            == False:  Equation (1) is solved.

            == True:   Equation (2) is solved,

            defaults to False
    :type trans: bool, optional
    :param hess: Specifies if (A,B) is in generalized Hessenberg form.
        If hess = True, the values of Q and Z are ignored,
        defaults to False
    :type hess: bool, optional
    :param A:
        If hess == True,
            the matrix A is an upper Hessenberg matrix of the generalized
            Hessenberg form (A,B) and its Schur decomposition A = Q*S*Z**T
            will be computed.
            If inplace == True, A is overwritten with S.

        Otherwise:

        If Q and Z are None,
            The matrix A is given as a general matrix and it is overwritten
            with quasi upper triangular matrix S of the generalized
            schur decomposition of (A,B) where A = Q*S*Z^T.
        If Q and Z are not None,
            the matrix A contains its (quasi-) upper triangular matrix S
            of the generalized  Schur decomposition of (A,B).
    :type A: (n,n) numpy array
    :param B:
        If hess == True,
            the matrix B is the upper triangular matrix of the generalized
            Hessenberg form (A,B) and its Schur decomposition B = Q*R*Z**T
            will be computed.
            If inplace == True, B is overwritten with R.

        Otherwise:

        If Q and Z are None,
            the matrix B is given as general matrix and it is overwritten
            with the upper triangular matrix R of the generalized
            Schur decomposition of (A,B) where B = Q*R*Z^T.
        If Q and Z are not None,
            the matrix B contains its upper triangular matrix R of the
            generalized Schur decomposition of (A,B).
    :type B: (n,n) numpy array
    :param Q:
        If Q is None, a (n,n) matrix containing the left Schur vectors
            of (A,B) is returned.
        If Q is not None, it contains the left Schur vectors of (A,B),
            defaults to None
    :type Q: (n,n) numpy array,
        optional
    :param Z:
        If Z is None, a (n,n) matrix containing the right Schur vectors
            of (A,B) is returned.
        If Z is not None, it contains the right Schur vectors of (A,B),
            defaults to None
    :type Z: (n,n) numpy array,
        optional
    :param X:
        On input, X contains the right hand side Y.
        On output, X contains the solution of the Equation (1) or (2)
        Right hand side Y and the solution X are symmetric (n,n) matrices.
    :type X: (n,n) numpy array
    :param block_size: sets the block size for the equation,
        defaults to 0
    :type block_size: int, optional
    :param solver: sets solver, defaults to 1
    :type solver: int, optional
    :param inplace:
        if inplace=False, gelyap works with copies of the matrices,
        defaults to False
    :type inplace: bool, optional
    :raise ValueError: on A,B,Q,Z or X type, shape or contingency
        mismatch. The ValueError is also raised when Q and Z do not
        give the same result for the 'is None' test.
    :return: (X, A, B, Q, Z)

             if inplace == True, the tuple contains their references to the

             modified input matrices. Otherwise, the tuple contains their

             newly allocated copies.

    .. HINT::
       |hintFortranLayout|
    """
    if numeric_t is cnp.npy_float:
        pymepack_def.mepack_single_tgstein_blocksize_set (block_size)
    elif numeric_t is cnp.npy_double:
        pymepack_def.mepack_double_tgstein_blocksize_set (block_size)

    pymepack_def.mepack_tgstein_frontend_solver_set(solver)
    params = { 'A': A, 'B': B, 'Q': Q, 'Z': Z, 'X': X,
            'trans_A': trans, 'hess_AB': hess, 'inplace': inplace}
    return GGSteinSolver(params).execute()


def gelyap_refine(
        cnp.ndarray[numeric_t, ndim=2] A not None,
        cnp.ndarray[numeric_t, ndim=2] Y not None,
        cnp.ndarray[numeric_t, ndim=2] AS = None,
        cnp.ndarray[numeric_t, ndim=2] Q = None,
        cnp.ndarray[numeric_t, ndim=2] X = None,
        trans = False, int max_it = 10, numeric_t tau = 0.1,
        int block_size = 0, int solver = 1):
    """
    *wrapper for mepack_double_gelyap_refine.*

    Solves a standard Lyapunov equation of the form
    ::

          A * X  +  X * A^T = Y         (1)
      or
          A^T * X  +  X * A = Y         (2)

    where A is a (n,n) general matrix using iterative refinement.
    The right hand side Y and the solution X are (n,n) matrices. The
    matrix A needs to be provided as the original data as well as in
    Schur decomposition since both are required in the iterative
    refinement process.

    The solver switches automatically between single and double precision
    based on the precision of input arrays.

    :param A: The original matrix A defining the equation.
    :type A: (n,n) numpy array
    :param Y: The right hand side Y.
    :type Y: (n,n) numpy array
    :param AS: AS contains the Schur decomposition of A,
        defaults to None
    :type AS: (n,n) numpy array,
        optional
    :param Q: Q contains the Schur vectors for A as returned by DGEES,
        defaults to None
    :type Q: (n,n) numpy array,
        optional
    :param X: X is either None or contains the initial guess. If given, X
        is copied and modified to contain the solution X on output,
        defaults to None
    :type X: (n,n) numpy array,
        optional
    :param trans: Specifies the form of an equation with respect to A:

            == False:  Equation (1) is solved.

            == True:   Equation (2) is solved,

            defaults to False
    :type trans: bool, optional
    :param max_it: the maximum number of iterations that are performed,
        2 <= max_it <= 100, defaults to 10
    :type max_it: int, optional
    :param tau: the additional security factor for the stopping
        criterion, defaults to 0.1
    :type tau: double, optional
    :param block_size: sets the block size for the equation,
        defaults to 0
    :type block_size: int, optional
    :param solver: sets solver, defaults to 1
    :type solver: int, optional
    :raise ValueError: on A, Y, AS, Q or X type, shape or contingency
        mismatch. The ValueError is also raised when AS and Q do not
        produce the same result of the 'is None' test.
    :return: (X, max_it, tau, convlog)

             X: the solution

             max_it: the number of iteration steps taken by the algorithm

             tau: the last relative residual
             when the stopping criterion got valid

             convlog: (max_it,) double precision array containing
             the convergence history of the iterative refinement.
             convlog[i] contains the maximum relative residual before
             it is solved for the i-th time.

    .. HINT::
       |hintFortranLayout|
    """
    if numeric_t is cnp.npy_float:
        pymepack_def.mepack_single_trlyap_blocksize_set (block_size)
    elif numeric_t is cnp.npy_double:
        pymepack_def.mepack_double_trlyap_blocksize_set (block_size)

    pymepack_def.mepack_trlyap_frontend_solver_set(solver)
    params = { 'A': A, 'Y': Y, 'AS': AS, 'Q': Q, 'X': X, 'trans_A': trans,
               'max_it': max_it, 'tau': tau}
    return GelyapRefineSolver(params).execute()


def gestein_refine(
        cnp.ndarray[numeric_t, ndim=2] A not None,
        cnp.ndarray[numeric_t, ndim=2] Y not None,
        cnp.ndarray[numeric_t, ndim=2] AS = None,
        cnp.ndarray[numeric_t, ndim=2] Q = None,
        cnp.ndarray[numeric_t, ndim=2] X = None,
        trans = False, int max_it = 10, numeric_t tau = 0.1,
        int block_size = 0, int solver = 1):
    """
    *wrapper for mepack_double_gestein_refine.*

    Solves a standard Stein equation of the form
    ::

          A * X * A^T - X = Y          (1)
      or
          A^T * X * A - X = Y          (2)

    where A is a (n,n) matrix using iterative refinement.
    The right hand side Y and the solution X are (n,n) matrices.
    The matrix A needs to be provided as the original data as well as in
    Schur decomposition since both are required in the iterative
    refinement process.

    The solver switches automatically between single and double precision
    based on the precision of input arrays.

    :param A: The original matrix A defining the equation.
    :type A: (n,n) numpy array
    :param Y: The right hand side Y.
    :type Y: (n,n) numpy array
    :param AS: AS contains the Schur decomposition of A, defaults to None
    :type AS: (n,n) numpy array,
        optional
    :param Q: Q contains the Schur vectors for A as returned by DGEES,
        defaults to None
    :type Q: (n,n) numpy array,
        optional
    :param X: X is either None or contains the initial guess. If given,
        X is copied and modified to contain the solution X on output,
        defaults to None
    :type X: (n,n) numpy array,
        optional
    :param trans: Specifies the form of an equation with respect to A:

            == False:  Equation (1) is solved.

            == True:   Equation (2) is solved,

            defaults to False
    :type trans: bool, optional
    :param max_it: the maximum number of iterations that are performed,
        2 <= max_it <= 100, defaults to 10
    :type max_it: int, optional
    :param tau: the additional security factor for the stopping
        criterion, defaults to 0.1
    :type tau: double, optional
    :param block_size: sets the block size for the equation,
        defaults to 0
    :type block_size: int, optional
    :param solver: sets solver, defaults to 1
    :type solver: int, optional
    :raise ValueError: on A, Y, AS, Q or X type, shape or contingency
        mismatch. The ValueError is also raised when AS and Q do not
        produce the same result of the 'is None' test.
    :return: (X, max_it, tau, convlog)

            X: the solution

            max_it: the number of iteration steps taken by the algorithm

            tau: the last relative residual
            when the stopping criterion got valid

            convlog: (max_it,) double precision array containing
            the convergence history of the iterative refinement.
            convlog[i] contains the maximum relative residual
            before it is solved for the i-th time.

    .. HINT::
       |hintFortranLayout|
    """
    if numeric_t is cnp.npy_float:
        pymepack_def.mepack_single_trstein_blocksize_set (block_size)
    elif numeric_t is cnp.npy_double:
        pymepack_def.mepack_double_trstein_blocksize_set (block_size)

    pymepack_def.mepack_trstein_frontend_solver_set(solver)
    params = { 'A': A, 'Y': Y, 'AS': AS, 'Q': Q, 'X': X, 'trans_A': trans,
               'max_it': max_it, 'tau': tau}
    return GesteinRefineSolver(params).execute()


def gglyap_refine(
        cnp.ndarray[numeric_t, ndim=2] A not None,
        cnp.ndarray[numeric_t, ndim=2] B not None,
        cnp.ndarray[numeric_t, ndim=2] Y not None,
        cnp.ndarray[numeric_t, ndim=2] AS = None,
        cnp.ndarray[numeric_t, ndim=2] BS = None,
        cnp.ndarray[numeric_t, ndim=2] Q = None,
        cnp.ndarray[numeric_t, ndim=2] Z = None,
        cnp.ndarray[numeric_t, ndim=2] X = None,
        trans = False, int max_it = 10, numeric_t tau = 0.1,
        int block_size = 0, int solver = 1):
    """
    *wrapper for mepack_double_gglyap_refine.*

    Solves a generalized Lyapunov equation of the form
    ::

          A * X * B^T + B * X * A^T = Y        (1)
      or
          A^T * X * B + B^T * X * A = Y        (2)

    where A is a (n,n) matrix using iterative refinement.
    The right hand side Y and the solution X are (n,n) matrices.
    The matrix pencil (A,B) needs to be provided as the original
    data as well as in generalized Schur decomposition since both
    are required in the iterative refinement process.

    The solver switches automatically between single and double precision
    based on the precision of input arrays.

    :param A: The original matrix A defining the equation.
    :type A: (n,n) numpy array
    :param B: The original matrix B defining the equation.
    :param B: (n,n) numpy array
    :param Y: The right hand side Y.
    :type Y: (n,n) numpy array
    :param AS: AS contains the generalized Schur decomposition of A,
        defaults to None
    :type AS: (n,n) numpy array,
        optional
    :param BS: BS contains the generalized Schur decomposition of B,
        defaults to None
    :type BS: (n,n) numpy array,
        optional
    :param Q: Q contains the left generalized Schur vectors of (A,B)
        as returned by DGGES3, defaults to None
    :type Q: (n,n) numpy array,
        optional
    :param Z: Z contains the right generalized Schur vectors of (A,B)
        as returned by DGGES3, defaults to None
    :type Z: (n,n) numpy array,
        optional
    :param X: X is either None or contains the initial guess. If given,
        X is copied and modified to contain the solution X on output,
        defaults to None
    :type X: (n,n) numpy array,
        optional
    :param trans: Specifies the form of an equation with respect to A:

            == False:  Equation (1) is solved.

            == True:   Equation (2) is solved,

            defaults to False
    :type trans: bool, optional
    :param max_it: the maximum number of iterations that are performed,
        2 <= max_it <= 100, defaults to 10
    :type max_it: int, optional
    :param tau: the additional security factor for the stopping
        criterion, defaults to 0.1
    :type tau: double, optional
    :param block_size: sets the block size for the equation,
        defaults to 0
    :type block_size: int, optional
    :param solver: sets solver, defaults to 1
    :type solver: int, optional
    :raise ValueError: on A, B, Y, AS, BS, Q, Z or X type, shape or contingency
        mismatch. The ValueError is also raised when AS, BS, Q, Z do not
        produce the same result of the 'is None' test.
    :return: (X, max_it, tau, convlog), where

            X: the solution

            max_it: the number of iteration steps taken by the algorithm

            tau: the last relative residual
            when the stopping criterion got valid

            convlog: (max_it,) double precision array containing
            the convergence history of the iterative refinement.
            convlog[i] contains the maximum relative residual
            before it is solved for the i-th time.

    .. HINT::
       |hintFortranLayout|
    """

    if numeric_t is cnp.npy_float:
        pymepack_def.mepack_single_tglyap_blocksize_set (block_size)
    elif numeric_t is cnp.npy_double:
        pymepack_def.mepack_double_tglyap_blocksize_set (block_size)

    pymepack_def.mepack_tglyap_frontend_solver_set(solver)
    params = { 'A': A, 'B': B, 'Y': Y, 'AS': AS, 'BS':BS, 'Q': Q,
               'Z':Z, 'X': X, 'trans_A': trans,'max_it': max_it, 'tau': tau}
    return GGLyapRefineSolver(params).execute()


def ggstein_refine(
        cnp.ndarray[numeric_t, ndim=2] A not None,
        cnp.ndarray[numeric_t, ndim=2] B not None,
        cnp.ndarray[numeric_t, ndim=2] Y not None,
        cnp.ndarray[numeric_t, ndim=2] AS = None,
        cnp.ndarray[numeric_t, ndim=2] BS = None,
        cnp.ndarray[numeric_t, ndim=2] Q = None,
        cnp.ndarray[numeric_t, ndim=2] Z = None,
        cnp.ndarray[numeric_t, ndim=2] X = None,
        trans = False, int max_it = 10, numeric_t tau = 0.1,
        int block_size = 0, int solver = 1):
    """
    *wrapper for mepack_double_ggstein_refine.*

    Solves a generalized Stein equation of the following forms:
    ::

          A * X * A^T - B * X * B^T = Y       (1)
      or
          A^T * X * A - B^T * X * B = Y       (2)

    where A is a (n,n) matrix using iterative refinement.
    The right hand side Y and the solution X are (n,n) matrices.
    The matrix pencil (A,B) needs to be provided as the original data
    as well as in generalized Schur decomposition since both are required
    in the iterative refinement process.

    The solver switches automatically between single and double precision
    based on the precision of input arrays.

    :param A: The original matrix A defining the equation.
    :type A: (n,n) numpy array
    :param B: The original matrix B defining the equation.
    :param B: (n,n) numpy array
    :param Y: The right hand side Y.
    :type Y: (n,n) numpy array
    :param AS: AS contains the generalized Schur decomposition of A,
        defaults to None
    :type AS: (n,n) numpy array,
        optional
    :param BS: BS contains the generalized Schur decomposition of B,
        defaults to None
    :type BS: (n,n) numpy array,
        optional
    :param Q: Q contains the left generalized Schur vectors of (A,B)
        as returned by DGGES3, defaults to None
    :type Q: (n,n) numpy array,
        optional
    :param Z: Z contains the right generalized Schur vectors of (A,B)
        as returned by DGGES3, defaults to None
    :type Z: (n,n) numpy array,
        optional
    :param X: X is either None or contains the initial guess. If given,
        X is copied and modified to contain the solution X on output,
        defaults to None
    :type X: (n,n) numpy array,
        optional
    :param trans: Specifies the form of an equation with respect to A:

            == False:  Equation (1) is solved.

            == True:   Equation (2) is solved,

            defaults to False
    :type trans: bool, optional
    :param max_it: the maximum number of iterations that are performed,
        2 <= max_it <= 100, defaults to 10
    :type max_it: int, optional
    :param tau: the additional security factor for the stopping
        criterion, defaults to 0.1
    :type tau: double, optional
    :param block_size: sets the block size for the equation,
        defaults to 0
    :type block_size: int, optional
    :param solver: sets solver, defaults to 1
    :type solver: int, optional
    :raise ValueError: on A, B, Y, AS, BS, Q, Z, X type, shape or contingency
        mismatch. The ValueError is also raised when AS, BS, Q, Z do not
        produce the same result of the 'is None' test.
    :return: (X, max_it, tau, convlog)

            X: the solution

            max_it: the number of iteration steps taken by the algorithm

            tau: the last relative residual
            when the stopping criterion got valid

            convlog: (max_it,) double precision array containing
            the convergence history of the iterative refinement.
            convlog[i] contains the maximum relative residual
            before it is solved for the i-th time.

    .. HINT::
       |hintFortranLayout|
    """
    if numeric_t is cnp.npy_float:
        pymepack_def.mepack_single_tgstein_blocksize_set (block_size)
    elif numeric_t is cnp.npy_double:
        pymepack_def.mepack_double_tgstein_blocksize_set (block_size)

    pymepack_def.mepack_tgstein_frontend_solver_set(solver)
    params = { 'A': A, 'B': B, 'Y': Y, 'AS': AS, 'BS':BS, 'Q': Q,
               'Z':Z, 'X': X, 'trans_A': trans,'max_it': max_it, 'tau': tau}
    return GGSteinRefineSolver(params).execute()


def gesylv(cnp.ndarray[numeric_t, ndim=2] A not None,
           cnp.ndarray[numeric_t, ndim=2] B not None,
           cnp.ndarray[numeric_t, ndim=2] X not None,
           cnp.ndarray[numeric_t, ndim=2] QA = None,
           cnp.ndarray[numeric_t, ndim=2] QB = None,
           numeric_t sgn = 1.0, trans_A = False, trans_B = False,
           hess_A = False, hess_B = False,
           block_size = (0,0), int solver = 1, inplace=False):

    """
    *wrapper for mepack_double_gesylv.*

    Solves a Sylvester equation of the following forms
    ::

          op1(A) * X  +  X * op2(B) = Y       (1)
      or
          op1(A) * X  -  X * op2(B) = Y       (2)

    where A is a (m,m) matrix and B is a (n,n) matrix. The right hand
    side Y and the solution X are (m,n) matrices.
    The matrix A (as well as B) can be either a general unreduced matrix
    or an upper Hessenberg matrix or a (quasi-) upper triangular factor.
    In the last case QA and QB provide the Schur-vectors of the
    matrices A and B respectively.

    The solver switches automatically between single and double precision
    based on the precision of input arrays.

    :param A:
        If hess_A == True,
            The matrix A is given as an upper Hessenberg matrix and its
            Schur decomposition A = QA*S*QA**T will be computed.
            If inplace == True, A is overwritten with its schur
            decomposition S.

        Otherwise:

        If QA is None,
            The matrix A is given as a general matrix and its
            Schur decomposition A = QA*S*QA**T will be computed.
            If inplace == True, A is overwritten with its Schur
            decomposition S.
        If QA is not None,
           the matrix A contains its (quasi-) upper triangular matrix S
           being the Schur decomposition of A. A = QA*S*QA**T
    :type A: (m,m) numpy array
    :param QA:
        If QA is None, a (m,m) matrix containing the Schur vectors of A
            is returned.
        If QA is not None, it contains the Schur vectors of A, the matrix A
            contains its Schur decomposition,
            defaults to None
    :type QA: (m,m) numpy array,
        optional
    :param B:
        If hess_B == True,
            The matrix B is given as an upper Hessenberg matrix and its
            Schur decomposition B = QB*R*QB**T will be computed.
            If inplace == True, B is overwritten with its Schur
            decomposition R.

        Otherwise:

        If QB is None,
            The matrix B is given as a general matrix and its
            Schur decomposition B = QB*R*QB**T will be computed.
            If inplace == True, B is overwritten with its Schur
            decomposition R.
        If QB is not None,
            the matrix B contains its (quasi-) upper triangular matrix R
            being the Schur decomposition of B. B = QB*R*QB**T
    :type B: (n,n) numpy array
    :param QB:
        If QB is None, a (n,n) matrix containing the Schur vectors of B
            is returned.
        If QB is not None, it contains the Schur vectors of B, the matrix B
            contains its Schur decomposition,
            defaults to None
    :type QB: (n,n) numpy array,
        optional
    :param X:
        On input, X contains the right hand side Y.
        On output, X contains the solution of the Equation (1) or (2)
        Right hand side Y and the solution X are symmetric (m,n) matrices.
    :type X: (m,n) numpy array
    :param sgn:
        Specifies the sign between the two parts of the Sylvester equation.

            == 1 :  Solve Equation (1)

            == -1:  Solve Equation (2),

            defaults to 1
    :type sgn: int, optional
    :param trans_A: Specifies the form of an equation with respect to A:

            == False:  op1(A) = A

            == True:   op1(A) = A^T,

            defaults to False
    :type trans_A: bool, optional
    :param trans_B: Specifies the form of an equation with respect to B:

            == False:  op2(B) = B

            == True:   op2(B) = B^T,

            defaults to False
    :type trans_B: bool, optional
    :param block_size: sets the block size dimensions for the solver,
        defaults to (0,0)
    :type block_size: (int,int), optional
    :param solver: sets solver, defaults to 1
    :type solver: int, optional
    :param inplace:
        if inplace == False, gesylv works with copies of the matrices,
        defaults to False
    :type inplace: bool, optional
    :raise ValueError:

        on A, B, QA, QB, X type, shape or contingency mismatch

        when hess_A == True and QA is not None

        when hess_B == True and QB is not None
    :return: (X, A, QA, B, QB)

             if inplace == True, the tuple contains their references to the

             modified input matrices. Otherwise, the tuple contains their

             newly allocated copies.

    .. HINT::
       |hintFortranLayout|
    """
    if numeric_t is cnp.npy_float:
        pymepack_def.mepack_single_trsylv_blocksize_mb_set(block_size[0])
        pymepack_def.mepack_single_trsylv_blocksize_nb_set(block_size[1])
    elif numeric_t is cnp.npy_double:
        pymepack_def.mepack_double_trsylv_blocksize_mb_set(block_size[0])
        pymepack_def.mepack_double_trsylv_blocksize_nb_set(block_size[1])

    pymepack_def.mepack_trsylv_frontend_solver_set(solver)
    params = { 'A': A, 'B': B, 'X': X, 'QA': QA, 'QB': QB, 'sgn': sgn,
            'trans_A': trans_A, 'trans_B': trans_B, 'hess_A': hess_A,
            'hess_B': hess_B, 'inplace': inplace}
    return GesylvSolver(params).execute()

def gesylv2(cnp.ndarray[numeric_t, ndim=2] A not None,
            cnp.ndarray[numeric_t, ndim=2] B not None,
            cnp.ndarray[numeric_t, ndim=2] X not None,
            cnp.ndarray[numeric_t, ndim=2] QA = None,
            cnp.ndarray[numeric_t, ndim=2] QB = None,
            numeric_t sgn = 1.0, trans_A = False, trans_B = False,
            hess_A = False, hess_B = False,
            block_size = (0,0), int solver = 1, inplace=False):

    """
    *wrapper for mepack_double_gesylv2.*

    Solves a Sylvester equation of the following forms
    ::

          op1(A) * X * op2(B) + X = Y       (1)
      or
          op1(A) * X * op2(B) - X = Y       (2)

    where A is a (m,m) matrix and B is a (n,n) matrix. The right hand
    side Y and the solution X are (m,n) matrices.
    The matrix A (as well as B) can be either a general unreduced matrix
    or an upper Hessenberg matrix or a (quasi-) upper triangular factor.
    In the last case QA and QB provide the Schur-vectors of the
    matrices A and B respectively.

    The solver switches automatically between single and double precision
    based on the precision of input arrays.

    :param A:
        If hess_A == True,
            The matrix A is given as an upper Hessenberg matrix and its
            Schur decomposition A = QA*S*QA**T will be computed.
            If inplace == True, A is overwritten with its schur
            decomposition S.

        Otherwise:

        If QA is None,
            The matrix A is given as a general matrix and its
            Schur decomposition A = QA*S*QA**T will be computed.
            If inplace == True, A is overwritten with its Schur
            decomposition S.
        If QA is not None,
           the matrix A contains its (quasi-) upper triangular matrix S
           being the Schur decomposition of A. A = QA*S*QA**T
    :type A: (m,m) numpy array
    :param QA:
        If QA is None, a (m,m) matrix containing the Schur vectors of A
            is returned.
        If QA is not None, it contains the Schur vectors of A, the matrix A
            contains its Schur decomposition,
            defaults to None
    :type QA: (m,m) numpy array,
        optional
    :param B:
        If hess_B == True,
            The matrix B is given as an upper Hessenberg matrix and its
            Schur decomposition B = QB*R*QB**T will be computed.
            If inplace == True, B is overwritten with its Schur
            decomposition R.

        Otherwise:

        If QB is None,
            The matrix B is given as a general matrix and its
            Schur decomposition B = QB*R*QB**T will be computed.
            If inplace == True, B is overwritten with its Schur
            decomposition R.
        If QB is not None,
            the matrix B contains its (quasi-) upper triangular matrix R
            being the Schur decomposition of B. B = QB*R*QB**T
    :type B: (n,n) numpy array
    :param QB:
        If QB is None, a (n,n) matrix containing the Schur vectors of B
            is returned.
        If QB is not None, it contains the Schur vectors of B, the matrix B
            contains its Schur decomposition,
            defaults to None
    :type QB: (n,n) numpy array,
        optional
    :param X:
        On input, X contains the right hand side Y.
        On output, X contains the solution of the Equation (1) or (2)
        Right hand side Y and the solution X are symmetric (m,n) matrices.
    :type X: (m,n) numpy array
    :param sgn:
        Specifies the sign between the two parts of the Sylvester equation.

            == 1 :  Solve Equation (1)

            == -1:  Solve Equation (2),

            defaults to 1
    :type sgn: int, optional
    :param trans_A: Specifies the form of an equation with respect to A:

            == False:  op1(A) = A

            == True:   op1(A) = A^T,

            defaults to False
    :type trans_A: bool, optional
    :param trans_B: Specifies the form of an equation with respect to B:

            == False:  op2(B) = B

            == True:   op2(B) = B^T,

            defaults to False
    :type trans_B: bool, optional
    :param block_size: sets the block size (rows,cols) for the solver,
        defaults to (0,0)
    :type block_size: (int,int), optional
    :param solver: sets solver, defaults to 1
    :type solver: int, optional
    :param inplace:
        if inplace == False, gesylv works with copies of the matrices,
        defaults to False
    :type inplace: bool, optional
    :raise ValueError:

        on A, B, QA, QB, X type, shape or contingency mismatch

        when hess_A == True and QA is not None

        when hess_B == True and QB is not None
    :return: (X, A, QA, B, QB)

             if inplace == True, the tuple contains their references to the

             modified input matrices. Otherwise, the tuple contains their

             newly allocated copies.

    .. HINT::
       |hintFortranLayout|
    """
    if numeric_t is cnp.npy_float:
        pymepack_def.mepack_single_trsylv2_blocksize_mb_set(block_size[0])
        pymepack_def.mepack_single_trsylv2_blocksize_nb_set(block_size[1])
    elif numeric_t is cnp.npy_double:
        pymepack_def.mepack_double_trsylv2_blocksize_mb_set(block_size[0])
        pymepack_def.mepack_double_trsylv2_blocksize_nb_set(block_size[1])


    pymepack_def.mepack_trsylv2_frontend_solver_set(solver)
    params = { 'A': A, 'B': B, 'X': X, 'QA': QA, 'QB': QB, 'sgn': sgn,
            'trans_A': trans_A, 'trans_B': trans_B, 'hess_A': hess_A,
            'hess_B': hess_B, 'inplace': inplace}
    return GesylvSolver2(params).execute()

def gesylv_refine(
        cnp.ndarray[numeric_t, ndim=2] A not None,
        cnp.ndarray[numeric_t, ndim=2] B not None,
        cnp.ndarray[numeric_t, ndim=2] Y not None,
        cnp.ndarray[numeric_t, ndim=2] AS = None,
        cnp.ndarray[numeric_t, ndim=2] BS = None,
        cnp.ndarray[numeric_t, ndim=2] Q = None,
        cnp.ndarray[numeric_t, ndim=2] R = None,
        cnp.ndarray[numeric_t, ndim=2] X = None,
        numeric_t sgn = 1.0, trans_A = False, trans_B = False, int max_it = 10,
        numeric_t tau = 0.1, block_size = (0,0), int solver = 1):

    """
    *wrapper for mepack_double_gesylv_refine.*

    Solves a Sylvester equation of the following forms
    ::

          op1(A) * X  +  X * op2(B) = Y        (1)
      or
          op1(A) * X  -  X * op2(B) = Y        (2)

    where A is a (m,m) matrix and B is a (n,n) matrix
    using iterative refinement. The right hand side Y
    and the solution X are (m,n) matrices.
    The matrices A and B need to be given in the original form as well as
    in their Schur decomposition since both are required in the iterative
    refinement procedure. If Schur decomposition for either A or B is not
    given, it's calculated automatically on the start of the procedure.

    The solver switches automatically between single and double precision
    based on the precision of input arrays.

    :param A: The original matrix A defining the equation.
    :type A: (m,m) numpy array
    :param B: The original matrix B defining the equation.
    :type B: (n,n) numpy array
    :param Y: The right hand side Y.
    :type Y: (m,n) numpy array
    :param AS: AS contains the Schur decomposition of A, defaults to None
    :type AS: (m,m) numpy array,
        optional
    :param BS: BS contains the Schur decomposition of B, defaults to None
    :type BS: (n,n) numpy array,
        optional
    :param Q: Q contains the Schur vectors for A as returned by DGEES,
        defaults to None
    :type Q: (m,m) numpy array,
        optional
    :param R: R contains the Schur vectors for B as returned by DGEES,
        defaults to None
    :type R: (n,n) numpy array,
        optional
    :param X: X is either None or contains the initial guess. If given,
        X is copied and modified to contain the solution X on output,
        defaults to None
    :type X: (m,n) numpy array,
        optional
    :param sgn:
        Specifies the sign between both terms.

            == 1 :  Solve Equation (1)

            == -1:  Solve Equation (2),

            defaults to 1
    :type sgn: int, optional
    :param trans_A: Specifies the form of an equation with respect to A:

            == False:  op1(A) = A

            == True:   op1(A) = A^T,

            defaults to False
    :type trans_A: bool, optional
    :param trans_B: Specifies the form of an equation with respect to B:

            == False:  op2(B) = B

            == True:   op2(B) = B^T,

            defaults to False
    :type trans_B: bool, optional
    :param max_it: the maximum number of iterations that are performed,
        2 <= max_it <= 100, defaults to 10
    :type max_it: int, optional
    :param tau: the additional security factor for the stopping
        criterion, defaults to 0.1
    :type tau: double, optional
    :param block_size: sets the block size for the equation,
        defaults to (0,0)
    :type block_size: (int,int), optional
    :param solver: sets solver, defaults to 1
    :type solver: int, optional
    :raise ValueError: on A, B, Y, AS, BS, Q, R, X type, shape
        or contingency mismatch. The ValueError is also raised
        when AS and  Q or BS and R do not produce the same result
        of the 'is None' test.
    :return: (X, max_it, tau, convlog)

            X: the solution

            max_it: the number of iteration steps taken by the algorithm

            tau: the last relative residual
            when the stopping criterion got valid

            convlog: (max_it,) double precision array containing
            the convergence history of the iterative refinement.
            convlog[i] contains the maximum relative residual
            before it is solved for the i-th time.

    .. HINT::
       |hintFortranLayout|
    """
    if numeric_t is cnp.npy_float:
        pymepack_def.mepack_single_trsylv_blocksize_mb_set(block_size[0])
        pymepack_def.mepack_single_trsylv_blocksize_nb_set(block_size[1])
    elif numeric_t is cnp.npy_double:
        pymepack_def.mepack_double_trsylv_blocksize_mb_set(block_size[0])
        pymepack_def.mepack_double_trsylv_blocksize_nb_set(block_size[1])

    pymepack_def.mepack_trsylv_frontend_solver_set(solver)
    params = { 'A': A, 'B': B, 'Y': Y, 'AS': AS, 'BS': BS,
               'Q': Q, 'R': R, 'X': X, 'sgn': sgn, 'trans_A': trans_A,
               'trans_B': trans_B, 'max_it': max_it, 'tau': tau}
    return GesylvRefineSolver(params).execute()

def gesylv2_refine(
        cnp.ndarray[numeric_t, ndim=2] A not None,
        cnp.ndarray[numeric_t, ndim=2] B not None,
        cnp.ndarray[numeric_t, ndim=2] Y not None,
        cnp.ndarray[numeric_t, ndim=2] AS = None,
        cnp.ndarray[numeric_t, ndim=2] BS = None,
        cnp.ndarray[numeric_t, ndim=2] Q = None,
        cnp.ndarray[numeric_t, ndim=2] R = None,
        cnp.ndarray[numeric_t, ndim=2] X = None,
        numeric_t sgn = 1.0, trans_A = False, trans_B = False,
        int max_it = 10, numeric_t tau = 0.1, block_size = (0,0), int solver = 1):

    """
    *wrapper for mepack_double_gesylv2_refine.*

    Solves a Sylvester equation of the following forms
    ::

          op1(A) * X * op2(B) + X = Y       (1)
      or
          op1(A) * X * op2(B) - X = Y       (2)

    where A is a (m,m) matrix and B is a (n,n) matrix
    using iterative refinement. The right hand side Y
    and the solution X are (m,n) matrices.
    The matrices A and B need to be given in the original form as well as
    in their Schur decomposition since both are required in the iterative
    refinement procedure. If Schur decomposition for either A or B is not
    given, it's calculated automatically on the start of the procedure.

    The solver switches automatically between single and double precision
    based on the precision of input arrays.

    :param A: The original matrix A defining the equation.
    :type A: (m,m) numpy array
    :param B: The original matrix B defining the equation.
    :type B: (n,n) numpy array
    :param Y: The right hand side Y.
    :type Y: (m,n) numpy array
    :param AS: AS contains the Schur decomposition of A, defaults to None
    :type AS: (m,m) numpy array,
        optional
    :param BS: BS contains the Schur decomposition of B, defaults to None
    :type BS: (n,n) numpy array,
        optional
    :param Q: Q contains the Schur vectors for A as returned by DGEES,
        defaults to None
    :type Q: (m,m) numpy array,
        optional
    :param R: R contains the Schur vectors for B as returned by DGEES,
        defaults to None
    :type R: (n,n) numpy array,
        optional
    :param X: X is either None or contains the initial guess. If given,
        X is copied and modified to contain the solution X on output,
        defaults to None
    :type X: (m,n) numpy array,
        optional
    :param sgn:
        Specifies the sign between both terms.

            == 1 :  Solve Equation (1)

            == -1:  Solve Equation (2),

            defaults to 1
    :type sgn: int, optional
    :param trans_A: Specifies the form of an equation with respect to A:

            == False:  op1(A) = A

            == True:   op1(A) = A^T,

            defaults to False
    :type trans_A: bool, optional
    :param trans_B: Specifies the form of an equation with respect to B:

            == False:  op2(B) = B

            == True:   op2(B) = B^T,

            defaults to False
    :type trans_B: bool, optional
    :param max_it: the maximum number of iterations that are performed,
        2 <= max_it <= 100, defaults to 10
    :type max_it: int, optional
    :param tau: the additional security factor for the stopping
        criterion, defaults to 0.1
    :type tau: double, optional
    :param block_size: sets the block size for the equation,
        defaults to (0,0)
    :type block_size: (int,int), optional
    :param solver: sets solver, defaults to 1
    :type solver: int, optional
    :raise ValueError: on A, B, Y, AS, BS, Q, R, X type, shape or contingency
        mismatch. The ValueError is also raised when AS and  Q or BS and R
        do not produce the same result of the 'is None' test.
    :return: (X, max_it, tau, convlog)

            X: the solution

            max_it: the number of iteration steps taken by the algorithm

            tau: the last relative residual
            when the stopping criterion got valid

            convlog: (max_it,) double precision array containing
            the convergence history of the iterative refinement.
            convlog[i] contains the maximum relative residual
            before it is solved for the i-th time.

    .. HINT::
       |hintFortranLayout|
    """
    if numeric_t is cnp.npy_float:
        pymepack_def.mepack_single_trsylv2_blocksize_mb_set(block_size[0])
        pymepack_def.mepack_single_trsylv2_blocksize_nb_set(block_size[1])
    elif numeric_t is cnp.npy_double:
        pymepack_def.mepack_double_trsylv2_blocksize_mb_set(block_size[0])
        pymepack_def.mepack_double_trsylv2_blocksize_nb_set(block_size[1])
    pymepack_def.mepack_trsylv2_frontend_solver_set(solver)

    params = { 'A': A, 'B': B, 'Y': Y, 'AS': AS, 'BS': BS,
               'Q': Q, 'R': R, 'X': X, 'sgn': sgn, 'trans_A': trans_A,
               'trans_B': trans_B, 'max_it': max_it, 'tau': tau}

    return GesylvRefineSolver2(params).execute()

def ggsylv(
        cnp.ndarray[numeric_t, ndim=2] A not None,
        cnp.ndarray[numeric_t, ndim=2] B not None,
        cnp.ndarray[numeric_t, ndim=2] C not None,
        cnp.ndarray[numeric_t, ndim=2] D not None,
        cnp.ndarray[numeric_t, ndim=2] X not None,
        cnp.ndarray[numeric_t, ndim=2] QA = None,
        cnp.ndarray[numeric_t, ndim=2] ZA = None,
        cnp.ndarray[numeric_t, ndim=2] QB = None,
        cnp.ndarray[numeric_t, ndim=2] ZB = None,
        numeric_t sgn = 1.0, trans_AC = False, trans_BD = False,
        hess_AC = False, hess_BD = False,
        block_size = (0,0), int solver = 1, inplace=False):

    """
    *wrapper for mepack_double_ggsylv.*

    Solves a generalized Sylvester equation of the following forms
    ::

          op1(A) * X * op2(B) + op1(C) * X * op2(D) = Y         (1)
      or
          op1(A) * X * op2(B) - op1(С) * X * op2(D) = Y         (2)

    where (A,C) is a (m,m) matrix pencil and (B,D) is a (n,n) matrix pencil.
    The right hand side Y and the solution X are (m,n) matrices. The matrix
    pencils (A,C) and (B,D) can be either given as general unreduced matrices,
    as generalized Hessenberg form, or in terms of their generalized Schur
    decomposition.
    If they are given as general matrices or as a generalized Hessenberg form
    their generalized Schur decomposition will be computed.

    The solver switches automatically between single and double precision
    based on the precision of input arrays.

    :param hess_AC: Specifies if (A,C) is in generalized Hessenberg form.
        If hess_AC = True, the values of QA and ZA are ignored,
        defaults to False
    :type hess_AC: bool, optional
    :param hess_BD: Specifies if (B,D) is in generalized Hessenberg form.
        If hess_BD = True, the values of QB and ZB are ignored,
        defaults to False
    :type hess_BD: bool, optional
    :param A:
        If hess_AC == True,
            the matrix A is an upper Hessenberg matrix of the generalized
            Hessenberg form (A,C) and its Schur decomposition A = QA*S*ZA**T
            will be computed.
            If inplace == True, A is overwritten with S.

        Otherwise:

        If QA and ZA are None,
            The matrix A is given as a general matrix and its
            Schur decomposition A = QA*S*ZA**T will be computed.
            If inplace == True, A is overwritten with S.
        If QA and ZA are not None,
            the matrix pencil (A,C) is already in generalized Schur
            form. The matrix A contains its (quasi-) upper triangular
            matrix S of the Schur decomposition of (A,C).
    :type A: (m,m) numpy array
    :param C:
        If hess_AC == True,
            the matrix C is the upper triangular matrix of the generalized
            Hessenberg form (A,C) and its Schur decomposition C = QA*R*ZA**T
            will be computed.
            If inplace == True, C is overwritten with R.

        Otherwise:

        If QA and ZA are None,
            The matrix C is given as a general matrix and its
            Schur decomposition C = QA*R*ZA**T will be computed.
            If inplace == True, C is overwritten with R.
        If QA and ZA are not None,
            the matrix pencil (A,C) is already in generalized Schur
            form. The matrix C contains its (quasi-) upper triangular
            matrix R of the Schur decomposition of (A,C).
    :type C: (m,m) numpy array
    :param QA:
        If QA is None, a (m,m) matrix containing the left Schur vectors
            of (A,C) is returned.
        If QA is not None, it contains the left Schur vectors of (A,C),
            defaults to None
    :type QA: (m,m) numpy array,
        optional
    :param ZA:
        If ZA is None, a (m,m) matrix containing the right Schur vectors
            of (A,C) is returned.
        If ZA is not None, it contains the right Schur vectors of (A,C),
            defaults to None
    :type ZA: (m,m) numpy array,
        optional
    :param B:
        If hess_BD == True,
            the matrix B is an upper Hessenberg matrix of the generalized
            Hessenberg form (B,D) and its Schur decomposition B = QB*U*ZB**T
            will be computed.
            If inplace == True, B is overwritten with U.

        Otherwise:

        If QB and ZB are None,
            The matrix B is given as a general matrix and its
            Schur decomposition B = QB*U*ZB**T will be computed.
            If inplace == True, B is overwritten with U.
        If QB and ZB are not None,
            the matrix pencil (B,D) is already in generalized Schur
            form. The matrix B contains its (quasi-) upper triangular
            matrix U of the Schur decomposition of (B,D).
    :type B: (n,n) numpy array
    :param D:
        If hess_BD == True,
            the matrix D is the upper triangular matrix of the generalized
            Hessenberg form (B,D) and its Schur decomposition D = QB*V*ZB**T
            will be computed.
            If inplace == True, D is overwritten with V.

        Otherwise:

        If QB and ZB are None,
            The matrix D is given as a general matrix and its
            Schur decomposition D = QB*V*ZB**T will be computed.
            If inplace == True, D is overwritten with V.
        If QB and ZB are not None,
            the matrix pencil (B,D) is already in generalized Schur
            form. The matrix D contains its (quasi-) upper triangular
            matrix V of the Schur decomposition of (B,D).
    :type D: (n,n) numpy array
    :param QB:
        If QB is None, a (n,n) matrix containing the left Schur vectors
            of (B,D) is returned.
        If QB is not None, it contains the left Schur vectors of (B,D),
            defaults to None
    :type QB: (n,n) numpy array,
        optional
    :param ZB:
        If ZB is None, a (n,n) matrix containing the right Schur vectors
            of (B,D) is returned.
        If ZB is not None, it contains the right Schur vectors of (B,D),
            defaults to None
    :type ZB: (n,n) numpy array,
        optional
    :param X:
        On input, X contains the right hand side Y.
        On output, X contains the solution of the Equation (1) or (2)
        Right hand side Y and the solution X are (m,n) matrices.
    :type X: (m,n) numpy array
    :param sgn:
        Specifies the sign between the two parts of the Sylvester equation.

            == 1 :  Solve Equation (1)

            == -1:  Solve Equation (2),

            defaults to 1
    :type sgn: int, optional
    :param trans_AC: Specifies the form of an equation with respect to A and C:

            == False:  op1(A) = A

            == True:   op1(A) = A^T,

            defaults to False
    :type trans_AC: bool, optional
    :param trans_BD: Specifies the form of an equation with respect to B and D:

            == False:  op2(B) = B

            == True:   op2(B) = B^T,

            defaults to False
    :type trans_BD: bool, optional
    :param block_size: sets the block size (rows,cols) for the solver,
        defaults to (0,0)
    :type block_size: (int,int), optional
    :param solver: sets solver, defaults to 1
    :type solver: int, optional
    :param inplace:
        if inplace == False, gesylv works with copies of the matrices,
        defaults to False
    :type inplace: bool,optional
    :raise ValueError: on A, B, C, D, QA, ZA, QB, ZB, X type, shape or
        contingency mismatch or when QA and ZA or QB and ZB do not yield
        the same result of the 'is None' test.
    :return: (X, A,C,QA,ZA, B,D,QB,ZB)

             if inplace == True, the tuple contains their references to the

             modified input matrices. Otherwise, the tuple contains their

             newly allocated copies.

    .. HINT::
       |hintFortranLayout|
    """

    if numeric_t is cnp.npy_float:
        pymepack_def.mepack_single_tgsylv_blocksize_mb_set(block_size[0])
        pymepack_def.mepack_single_tgsylv_blocksize_nb_set(block_size[1])
    elif numeric_t is cnp.npy_double:
        pymepack_def.mepack_double_tgsylv_blocksize_mb_set(block_size[0])
        pymepack_def.mepack_double_tgsylv_blocksize_nb_set(block_size[1])

    pymepack_def.mepack_tgsylv_frontend_solver_set(solver)

    params = { 'A': A, 'B': B, 'C': C, 'D': D,
            'QA': QA, 'ZA': ZA, 'QB': QB, 'ZB': ZB, 'X': X,
            'sgn': sgn, 'trans_A': trans_AC, 'trans_B': trans_BD,
            'sgn': sgn, 'trans_A': trans_AC, 'trans_B': trans_BD,
            'hess_AC': hess_AC, 'hess_BD': hess_BD, 'inplace': inplace}

    return GGSylvSolver(params).execute()

def ggsylv_refine(
        cnp.ndarray[numeric_t, ndim=2] A not None,
        cnp.ndarray[numeric_t, ndim=2] B not None,
        cnp.ndarray[numeric_t, ndim=2] C not None,
        cnp.ndarray[numeric_t, ndim=2] D not None,
        cnp.ndarray[numeric_t, ndim=2] Y not None,
        cnp.ndarray[numeric_t, ndim=2] AS = None,
        cnp.ndarray[numeric_t, ndim=2] BS = None,
        cnp.ndarray[numeric_t, ndim=2] CS = None,
        cnp.ndarray[numeric_t, ndim=2] DS = None,
        cnp.ndarray[numeric_t, ndim=2] Q = None,
        cnp.ndarray[numeric_t, ndim=2] Z = None,
        cnp.ndarray[numeric_t, ndim=2] U = None,
        cnp.ndarray[numeric_t, ndim=2] V = None,
        cnp.ndarray[numeric_t, ndim=2] X = None,
        numeric_t sgn = 1.0, trans_AC = False, trans_BD = False,
        int max_it = 10, numeric_t tau = 0.1, block_size = (0,0), int solver = 1):

    """
    *wrapper for mepack_double_ggsylv_refine.*

    Solves a generalized Sylvester equation of the following forms
    ::

          op1(A) * X * op2(B) + op1(C) * X * op2(D) = Y       (1)
      or
          op1(A) * X * op2(B) - op1(С) * X * op2(D) = Y       (2)

    with iterative refinement. (A,C) is a (m,m) matrix pencil and (B,D) is
    a (n,n) matrix pencil.
    The right hand side Y and the solution X are (m,n) matrices.
    The matrix pencils (A,C) and (B,D) need to be given in the original
    form as well as in their generalized Schur decomposition, since both
    are required in the iterative refinement procedure.

    The solver switches automatically between single and double precision
    based on the precision of input arrays.

    :param A: The original matrix A defining the equation.
    :type A: (m,m) numpy array
    :param B: The original matrix B defining the equation.
    :type B: (n,n) numpy array
    :param C: The original matrix C defining the equation.
    :type C: (m,m) numpy array
    :param D: The original matrix D defining the equation.
    :type D: (n,n) Fortran-contiguous double precis
    :param Y: The right hand side Y.
    :type Y: (m,n) numpy array
    :param AS: AS contains the generalized Schur decomposition of A,
        defaults to None
    :type AS: (m,m) numpy array,
        optional
    :param BS: BS contains the generalized Schur decomposition of B,
        defaults to None
    :type BS: (n,n) numpy array,
        optional
    :param CS: CS contains the generalized Schur decomposition of C,
        defaults to None
    :type CS: (m,m) numpy array,
        optional
    :param DS: DS contains the generalized Schur decomposition of D,
        defaults to None
    :type DS: (n,n) numpy array,
        optional
    :param Q: Q contains the left generalized Schur vectors for (A,C)
        as returned by DGGES, defaults to None
    :type Q: (m,m) numpy array,
        optional
    :param Z: Z contains the right generalized Schur vectors for (A,C)
        as returned by DGGES, defaults to None
    :type Z: (m,m) numpy array,
        optional
    :param U: U contains the left generalized Schur vectors for (B,D)
        as returned by DGGES, defaults to None
    :type U: (n,n) numpy array,
        optional
    :param V: V contains the right generalized Schur vectors for (B,D)
        as returned by DGGES, defaults to None
    :type V: (n,n) numpy array,
        optional
    :param X: X is either None or contains the initial guess. If given,
        X is copied and modified to contain the solution X on output,
        defaults to None
    :type X: (m,n) numpy array,
        optional
    :param sgn:
        Specifies the sign between the two parts of the Sylvester equation.

            == 1 :  Solve Equation (1)

            == -1:  Solve Equation (2),

            defaults to 1
    :type sgn: int, optional
    :param trans_AC: Specifies the form of an equation with respect to A and C:

            == False:  op1(A) = A

            == True:   op1(A) = A^T,

            defaults to False
    :type trans_AC: bool, optional
    :param trans_BD: Specifies the form of an equation with respect to B and D:

            == False:  op2(B) = B

            == True:   op2(B) = B^T,

            defaults to False
    :type trans_BD: bool, optional
    :param max_it: the maximum number of iterations that are performed,
        2 <= max_it <= 100, defaults to 10
    :type max_it: int, optional
    :param tau: the additional security factor for the stopping
        criterion, defaults to 0.1
    :type tau: double, optional
    :param block_size: sets the block size (rows,cols) for the solver,
        defaults to (0,0)
    :type block_size: (int,int), optional
    :param solver: sets solver, defaults to 1
    :type solver: int, optional
    :raise ValueError: on A, B, C, D, QA, ZA, QB, ZB, X type, shape or
        contingency mismatch. The ValueError is also raised when
        AS,CS,Q,Z or BS,DS,U,V do not produce the same result of the
        'is None' test.
    :return: (X, max_it, tau, convlog)

            X: the solution

            max_it: the number of iteration steps taken by the algorithm

            tau: the last relative residual
            when the stopping criterion got valid

            convlog: (max_it,) double precision array containing
            the convergence history of the iterative refinement.
            convlog[i] contains the maximum relative residual
            before it is solved for the i-th time.

    .. HINT::
       |hintFortranLayout|
    """
    if numeric_t is cnp.npy_float:
        pymepack_def.mepack_single_tgsylv_blocksize_mb_set(block_size[0])
        pymepack_def.mepack_single_tgsylv_blocksize_nb_set(block_size[1])
    elif numeric_t is cnp.npy_double:
        pymepack_def.mepack_double_tgsylv_blocksize_mb_set(block_size[0])
        pymepack_def.mepack_double_tgsylv_blocksize_nb_set(block_size[1])

    pymepack_def.mepack_tgsylv_frontend_solver_set(solver)

    params = { 'A': A, 'B': B, 'C': C, 'D': D, 'X':X, 'Y':Y,
            'AS': AS, 'BS': BS, 'CS': CS, 'DS': DS, 'Q':Q, 'Z': Z,
            'U': U, 'V': V, 'sgn': sgn, 'trans_A': trans_AC,
            'trans_B': trans_BD, 'max_it': max_it, 'tau': tau}

    return GGSylvRefineSolver(params).execute()


def ggcsylv(
        cnp.ndarray[numeric_t, ndim=2] A not None,
        cnp.ndarray[numeric_t, ndim=2] B not None,
        cnp.ndarray[numeric_t, ndim=2] C not None,
        cnp.ndarray[numeric_t, ndim=2] D not None,
        cnp.ndarray[numeric_t, ndim=2] E not None,
        cnp.ndarray[numeric_t, ndim=2] F not None,
        cnp.ndarray[numeric_t, ndim=2] QA = None,
        cnp.ndarray[numeric_t, ndim=2] ZA = None,
        cnp.ndarray[numeric_t, ndim=2] QB = None,
        cnp.ndarray[numeric_t, ndim=2] ZB = None,
        numeric_t sgn1 = 1.0, numeric_t sgn2 = 1.0,
        trans_AC = False, trans_BD = False,
        hess_AC = False, hess_BD = False,
        block_size = (0,0), int solver = 1, inplace=False):

    """
    *wrapper for mepack_double_ggcsylv.*

    Solves a generalized coupled Sylvester equation of the following form
    ::

        op1(A) * R + sgn1 * L * op2(B) = E
                                                 (1)
        op1(C) * R + sgn2 * L * op2(D) = F

    where (A,C) is a (m,m) matrix pencil and (B,D) is a (n,n) matrix pencil.
    The right hand side (E,F) and the solution (R,L) are (m,n) matrix pencils.
    The matrix pencils (A,C) and (B,D) can be either given as general
    unreduced matrices, as generalized Hessenberg form, or in terms of their
    generalized Schur decomposition.

    If they are given as general matrices or as a generalized Hessenberg form
    their generalized Schur decomposition will be computed.

    The solver switches automatically between single and double precision
    based on the precision of input arrays.

    :param hess_AC: Specifies if (A,C) is in generalized Hessenberg form.
        If hess_AC = True, the values of QA and ZA are ignored,
        defaults to False
    :type hess_AC: as generalized Hessenberg form, bool, optional
    :param hess_BD: Specifies if (B,D) is in generalized Hessenberg form.
        If hess_BD = True, the values of QB and ZB are ignored,
        defaults to False
    :type hess_BD: bool, optional
    :param A:
        If hess_AC == True,
            the matrix A is an upper Hessenberg matrix of the generalized
            Hessenberg form (A,C) and its Schur decomposition A = QA*S*ZA**T
            will be computed.
            If inplace == True, A is overwritten with S.

        Otherwise:

        If QA and ZA are None,
            The matrix A is given as a general matrix and its
            Schur decomposition A = QA*S*ZA**T will be computed.
            If inplace == True, A is overwritten with S.
        If QA and ZA are not None,
            the matrix pencil (A,C) is already in generalized Schur
            form. The matrix A contains its (quasi-) upper triangular
            matrix S of the Schur decomposition of (A,C).
    :type A: (m,m) numpy array
    :param C:
        If hess_AC == True,
            the matrix C is the upper triangular matrix of the generalized
            Hessenberg form (A,C) and its Schur decomposition C = QA*R*ZA**T
            will be computed.
            If inplace == True, C is overwritten with R.

        Otherwise:

        If QA and ZA are None,
            The matrix C is given as a general matrix and its
            Schur decomposition C = QA*R*ZA**T will be computed.
            If inplace == True, C is overwritten with R.
        If QA and ZA are not None,
            the matrix pencil (A,C) is already in generalized Schur
            form. The matrix C contains its (quasi-) upper triangular
            matrix R of the Schur decomposition of (A,C).
    :type C: (m,m) numpy array
    :param QA:
        If QA is None, a (m,m) matrix containing the left Schur vectors
            of (A,C) is returned.
        If QA is not None, it contains the left Schur vectors of (A,C),
            defaults to None
    :type QA: (m,m) numpy array,
        optional
    :param ZA:
        If ZA is None, a (m,m) matrix containing the right Schur vectors
            of (A,C) is returned.
        If ZA is not None, it contains the right Schur vectors of (A,C),
            defaults to None
    :type ZA: (m,m) numpy array,
        optional
    :param B:
        If hess_BD == True,
            the matrix B is an upper Hessenberg matrix of the generalized
            Hessenberg form (B,D) and its Schur decomposition B = QB*U*ZB**T
            will be computed.
            If inplace == True, B is overwritten with U.

        Otherwise:

        If QB and ZB are None,
            The matrix B is given as a general matrix and its
            Schur decomposition B = QB*U*ZB**T will be computed.
            If inplace == True, B is overwritten with U.
        If QB and ZB are not None,
           the matrix pencil (B,D) is already in generalized Schur
           form. The matrix B contains its (quasi-) upper triangular
           matrix U of the Schur decomposition of (B,D).
    :type B: (n,n) numpy array
    :param D:
        If hess_BD == True,
            the matrix D is the upper triangular matrix of the generalized
            Hessenberg form (B,D) and its Schur decomposition D = QB*V*ZB**T
            will be computed.
            If inplace == True, D is overwritten with V.

        Otherwise:

        If QB and ZB are None,
            The matrix D is given as a general matrix and its
            Schur decomposition D = QB*V*ZB**T will be computed.
            If inplace == True, D is overwritten with V.
        If QB and ZB are not None,
           the matrix pencil (B,D) is already in generalized Schur
           form. The matrix D contains its (quasi-) upper triangular
           matrix V of the Schur decomposition of (B,D).
    :type D: (n,n) numpy array
    :param QB:
        If QB is None, a (n,n) matrix containing the left Schur vectors
            of (B,D) is returned.
        If QB is not None, it contains the left Schur vectors of (B,D),
            defaults to None
    :type QB: (n,n) numpy array,
        optional
    :param ZB:
        If ZB is None, a (n,n) matrix containing the right Schur vectors
            of (B,D) is returned.
        If ZB is not None, it contains the right Schur vectors of (B,D),
            defaults to None
    :type ZB: (n,n) numpy array,
        optional
    :param E:
        On input, E contains the right hand side Y.
        On output, E contains the solution R.
    :type E: (m,n) numpy array
    :param F:
        On input, F contains the right hand side F.
        On output, F contains the solution L.
        Right hand side Y and the solution X are (m,n) matrices.
    :type F: (m,n) numpy array
    :param sgn1: Specifies the sign in the first equation.
        Possible values: +/- 1 , defaults to 1
    :type sgn1: int, optional
    :param sgn2: Specifies the sign in the second equation.
        Possible values: +/- 1 , defaults to 1
    :type sgn2: int, optional
    :param trans_AC: Specifies the form of an equation with respect to A and C:

            == False:  op1(A) = A

            == True:   op1(A) = A^T,

            defaults to False
    :type trans_AC: bool, optional
    :param trans_BD: Specifies the form of an equation with respect to B and D:

            == False:  op2(B) = B

            == True:   op2(B) = B^T,

            defaults to False
    :type trans_BD: bool, optional
    :param block_size: sets the block size (rows,cols) for the solver,
        defaults to (0,0)
    :type block_size: (int,int), optional
    :param solver: sets solver, defaults to 1
    :type solver: int, optional
    :param inplace:
        if inplace == False, solver works with copies of the matrices,
        defaults to False
    :type inplace: bool,optional
    :raise ValueError: on A, B, C, D, QA, ZA, QB, ZB, E, F type, shape or
        contingency mismatch or when QA and ZA or QB and ZB do not yield
        the same result of the 'is None' test.
    :return: (E,F, A,C,QA,ZA, B,D,QB,ZB)

             if inplace == True, the tuple contains their references to the

             modified input matrices. Otherwise, the tuple contains their

             newly allocated copies.

    .. HINT::
       |hintFortranLayout|
    """
    if numeric_t is cnp.npy_float:
        pymepack_def.mepack_single_tgcsylv_blocksize_mb_set(block_size[0])
        pymepack_def.mepack_single_tgcsylv_blocksize_nb_set(block_size[1])
    elif numeric_t is cnp.npy_double:
        pymepack_def.mepack_double_tgcsylv_blocksize_mb_set(block_size[0])
        pymepack_def.mepack_double_tgcsylv_blocksize_nb_set(block_size[1])

    pymepack_def.mepack_tgcsylv_frontend_solver_set(solver)

    params = { 'A': A, 'B': B, 'C': C, 'D': D, 'E': E, 'F': F,
            'QA': QA, 'ZA': ZA, 'QB': QB, 'ZB': ZB, 'sgn1': sgn1, 'sgn2': sgn2,
            'trans_A': trans_AC, 'trans_B': trans_BD,
            'hess_AC': hess_AC, 'hess_BD': hess_BD, 'inplace': inplace}

    return GGCSylvSolver(params).execute()

def ggcsylv_refine(
        cnp.ndarray[numeric_t, ndim=2] A not None,
        cnp.ndarray[numeric_t, ndim=2] B not None,
        cnp.ndarray[numeric_t, ndim=2] C not None,
        cnp.ndarray[numeric_t, ndim=2] D not None,
        cnp.ndarray[numeric_t, ndim=2] E not None,
        cnp.ndarray[numeric_t, ndim=2] F not None,
        cnp.ndarray[numeric_t, ndim=2] AS = None,
        cnp.ndarray[numeric_t, ndim=2] BS = None,
        cnp.ndarray[numeric_t, ndim=2] CS = None,
        cnp.ndarray[numeric_t, ndim=2] DS = None,
        cnp.ndarray[numeric_t, ndim=2] Q = None,
        cnp.ndarray[numeric_t, ndim=2] Z = None,
        cnp.ndarray[numeric_t, ndim=2] U = None,
        cnp.ndarray[numeric_t, ndim=2] V = None,
        cnp.ndarray[numeric_t, ndim=2] R = None,
        cnp.ndarray[numeric_t, ndim=2] L = None,
        numeric_t sgn1 = 1.0, numeric_t sgn2 = 1.0, trans_AC = False,trans_BD = False,
        int max_it = 10, numeric_t tau = 0.1, block_size = (0,0), int solver = 1):

    """
    *wrapper for mepack_double_ggcsylv_refine.*

    Solves a coupled generalized Sylvester equation of the following form
    ::

        op1(A) * R + sgn1 * L * op2(B) = E
                                                 (1)
        op1(C) * R + sgn2 * L * op2(D) = F

    with iterative refinement. (A,C) is a (m,m) matrix pencil and (B,D) is
    a (n,n) matrix pencil.
    The right hand side (E,F) and the solution (R,L) are (m,n) matrix
    pencils.
    The matrix pencils (A,C) and (B,D) need to be given in the original
    form as well as in their generalized Schur decomposition, since both
    are required in the iterative refinement procedure.

    The solver switches automatically between single and double precision
    based on the precision of input arrays.

    :param A: The original matrix A defining the equation.
    :type A: (m,m) numpy array
    :param B: The original matrix B defining the equation.
    :type B: (n,n) numpy array
    :param C: The original matrix C defining the equation.
    :type C: (m,m) numpy array
    :param D: The original matrix D defining the equation.
    :type D: (n,n) Fortran-contiguous double precis
    :param E: The right hand side E.
    :type E: (m,n) numpy array
    :param F: The right hand side F.
    :type F: (m,n) numpy array
    :param AS: AS contains the generalized Schur decomposition of A,
        defaults to None
    :type AS: (m,m) numpy array,
        optional
    :param BS: BS contains the generalized Schur decomposition of B,
        defaults to None
    :type BS: (n,n) numpy array,
        optional
    :param CS: CS contains the generalized Schur decomposition of C,
        defaults to None
    :type CS: (m,m) numpy array,
        optional
    :param DS: DS contains the generalized Schur decomposition of D,
        defaults to None
    :type DS: (n,n) numpy array,
        optional
    :param Q: Q contains the left generalized Schur vectors for (A,C)
        as returned by DGGES, defaults to None
    :type Q: (m,m) numpy array,
        optional
    :param Z: Z contains the right generalized Schur vectors for (A,C)
        as returned by DGGES, defaults to None
    :type Z: (m,m) numpy array,
        optional
    :param U: U contains the left generalized Schur vectors for (B,D)
        as returned by DGGES, defaults to None
    :type U: (n,n) numpy array,
        optional
    :param V: V contains the right generalized Schur vectors for (B,D)
        as returned by DGGES, defaults to None
    :type V: (n,n) numpy array,
        optional
    :param R: R is either None or contains the initial guess for the first
        solution. If given, R is copied and modified to contain the
        solution R on output, defaults to None
    :type R: (m,n) numpy array,
        optional
    :param L: L is either None or contains the initial guess for the
        second solution. If given, L is copied and modified to contain the
        solution L on output, defaults to None
    :type L: (m,n) numpy array,
        optional
    :param sgn1: Specifies the sign in the first equation.
        Possible values: +/- 1 , defaults to 1
    :type sgn1: int, optional
    :param sgn2: Specifies the sign in the second equation.
        Possible values: +/- 1 , defaults to 1
    :type sgn2: int, optional
    :param trans_AC: Specifies the form of an equation with respect to A and C:

            == False:  op1(A) = A

            == True:   op1(A) = A^T,

            defaults to False
    :type trans_AC: bool, optional
    :param trans_BD: Specifies the form of an equation with respect to B and D:

            == False:  op2(B) = B

            == True:   op2(B) = B^T,

            defaults to False
    :type trans_BD: bool, optional
    :param max_it: the maximum number of iterations that are performed,
        2 <= max_it <= 100, defaults to 10
    :type max_it: int, optional
    :param tau: the additional security factor for the stopping
        criterion, defaults to 0.1
    :type tau: double, optional
    :param block_size: sets the block size (rows,cols) for the solver,
        defaults to (0,0)
    :type block_size: (int,int), optional
    :param solver: sets solver, defaults to 1
    :type solver: int, optional
    :raise ValueError: on A, B, C, D, QA, ZA, QB, ZB, E, F, R, L type,
        shape or contingency mismatch. The ValueError is also raised when
        AS,CS,Q,Z or BS,DS,U,V do not produce the same result of the
        'is None' test.
    :return: (R, L, max_it, tau, convlog)

            (R, L): the solution

            max_it: the number of iteration steps taken by the algorithm

            tau: the last relative residual
            when the stopping criterion got valid

            convlog: (max_it,) double precision array containing
            the convergence history of the iterative refinement.
            convlog[i] contains the maximum relative residual
            before it is solved for the i-th time.

    .. HINT::
       |hintFortranLayout|
    """
    if numeric_t is cnp.npy_float:
        pymepack_def.mepack_single_tgcsylv_blocksize_mb_set(block_size[0])
        pymepack_def.mepack_single_tgcsylv_blocksize_nb_set(block_size[1])
    elif numeric_t is cnp.npy_double:
        pymepack_def.mepack_double_tgcsylv_blocksize_mb_set(block_size[0])
        pymepack_def.mepack_double_tgcsylv_blocksize_nb_set(block_size[1])

    pymepack_def.mepack_tgcsylv_frontend_solver_set(solver)

    params = { 'A': A, 'B': B, 'C': C, 'D': D, 'E': E, 'F': F, 'R': R, 'L': L,
            'AS': AS, 'BS': BS, 'CS': CS, 'DS': DS,'Q': Q,'Z': Z,'U': U,'V': V,
            'sgn1': sgn1, 'sgn2': sgn2, 'trans_A': trans_AC,
            'trans_B': trans_BD, 'max_it': max_it, 'tau': tau}

    return GGCSylvRefineSolver(params).execute()

def ggcsylv_dual(
        cnp.ndarray[numeric_t, ndim=2] A not None,
        cnp.ndarray[numeric_t, ndim=2] B not None,
        cnp.ndarray[numeric_t, ndim=2] C not None,
        cnp.ndarray[numeric_t, ndim=2] D not None,
        cnp.ndarray[numeric_t, ndim=2] E not None,
        cnp.ndarray[numeric_t, ndim=2] F not None,
        cnp.ndarray[numeric_t, ndim=2] QA = None,
        cnp.ndarray[numeric_t, ndim=2] ZA = None,
        cnp.ndarray[numeric_t, ndim=2] QB = None,
        cnp.ndarray[numeric_t, ndim=2] ZB = None,
        numeric_t sgn1 = 1.0, numeric_t sgn2 = 1.0,
        trans_AC = False, trans_BD = False,
        hess_AC = False, hess_BD = False,
        block_size = (0,0), int solver = 1, inplace=False):
    """
    *wrapper for mepack_double_ggcsylv_dual.*

    Solves a generalized coupled Sylvester equation of the following form
    ::

        op1(A)^T * R + op1(C)^T * L               =  E
                                                             (1)
        sgn1 * R * op2(B)^T + sgn2 * L * op2(D)^T =  F

    where (A,C) is a (m,m) matrix pencil and (B,D) is a (n,n) matrix pencil.
    The right hand side (E,F) and the solution (R,L) are (m,n) matrix pencils.
    The matrix pencils (A,C) and (B,D) can be either given as general
    unreduced matrices, as generalized Hessenberg form, or in terms of their
    generalized Schur decomposition.
    If they are given as general matrices or as a generalized Hessenberg form
    their generalized Schur decomposition will be computed.

    The equation (1) is the dual to the generalized coupled Sylvester equation
    ::

        op1(A) * R + sgn1 * L * op2(B) = E
                                                             (2)
        op1(C) * R + sgn2 * L * op2(D) = F

    The equation (1) is the dual one to equation (2) with respect to the
    underlying linear system.
    Let Z be the matrix formed by rewriting (2) into its Kronecker form.
    This yields
    ::

            |kron(I, op1(A)   sgn1*kron(op2(B)^T,I)| |Vec R| |Vec E|
      Z X = |                                      |*|     |=|     |
            |kron(I, op1(C))  sgn2*kron(op2(D)^T,I)| |Vec L| |Vec F|

    Regarding Z^T one obtains
    ::

              |kron(I, op1(A)^T)    kron(I, op1(C)^T)  | |Vec R| |Vec E|
      Z^T X = |                                        |*|     |=|     |
              |sgn1*kron(op2(B),I)  sgn2*kron(op2(D),I)| |Vec L| |Vec F|

    which belongs to the Sylvester equation (1). For this reason
    the parameters trans_AC and trans_BD are expressed in terms of the
    Sylvester equation (2).

    The solver switches automatically between single and double precision
    based on the precision of input arrays.

    :param hess_AC: Specifies if (A,C) is in generalized Hessenberg form.
        If hess_AC = True, the values of QA and ZA are ignored,
        defaults to False
    :type hess_AC: as generalized Hessenberg form, bool, optional
    :param hess_BD: Specifies if (B,D) is in generalized Hessenberg form.
        If hess_BD = True, the values of QB and ZB are ignored,
        defaults to False
    :type hess_BD: bool, optional
    :param A:
        If hess_AC == True,
            the matrix C is the upper triangular matrix of the generalized
            Hessenberg form (A,C) and its Schur decomposition C = QA*R*ZA**T
            will be computed.
            If inplace == True, C is overwritten with R.

        Otherwise:

        If QA and ZA are None,
            The matrix A is given as a general matrix and its
            Schur decomposition A = QA*S*ZA**T will be computed.
            If inplace == True, A is overwritten with S.
        If QA and ZA are not None,
            the matrix pencil (A,C) is already in generalized Schur
            form. The matrix A contains its (quasi-) upper triangular
            matrix S of the Schur decomposition of (A,C).
    :type A: (m,m) numpy array
    :param C:
        If hess_AC == True,
            the matrix C is the upper triangular matrix of the generalized
            Hessenberg form (A,C) and its Schur decomposition C = QA*R*ZA**T
            will be computed.
            If inplace == True, C is overwritten with R.

        Otherwise:

        If QA and ZA are None,
            The matrix C is given as a general matrix and its
            Schur decomposition C = QA*R*ZA**T will be computed.
            If inplace == True, C is overwritten with R.
        If QA and ZA are not None,
            the matrix pencil (A,C) is already in generalized Schur
            form. The matrix C contains its (quasi-) upper triangular
            matrix R of the Schur decomposition of (A,C).
    :type C: (m,m) numpy array
    :param QA:
        If QA is None, a (m,m) matrix containing the left Schur vectors
            of (A,C) is returned.
        If QA is not None, it contains the left Schur vectors of (A,C),
            defaults to None
    :type QA: (m,m) numpy array,
        optional
    :param ZA:
        If ZA is None, a (m,m) matrix containing the right Schur vectors
            of (A,C) is returned.
        If ZA is not None, it contains the right Schur vectors of (A,C),
            defaults to None
    :type ZA: (m,m) numpy array,
        optional
    :param B:
        If hess_BD == True,
            the matrix B is an upper Hessenberg matrix of the generalized
            Hessenberg form (B,D) and its Schur decomposition B = QB*U*ZB**T
            will be computed.
            If inplace == True, B is overwritten with U.

        Otherwise:

        If QB and ZB are None,
            The matrix B is given as a general matrix and its
            Schur decomposition B = QB*U*ZB**T will be computed.
            If inplace == True, B is overwritten with U.
        If QB and ZB are not None,
            the matrix pencil (B,D) is already in generalized Schur
            form. The matrix B contains its (quasi-) upper triangular
            matrix U of the Schur decomposition of (B,D).
    :type B: (n,n) numpy array
    :param D:
        If hess_BD == True,
            the matrix D is the upper triangular matrix of the generalized
            Hessenberg form (B,D) and its Schur decomposition D = QB*V*ZB**T
            will be computed.
            If inplace == True, D is overwritten with V.

        Otherwise:

        If QB and ZB are None,
            The matrix D is given as a general matrix and its
            Schur decomposition D = QB*V*ZB**T will be computed.
            If inplace == True, D is overwritten with V.
        If QB and ZB are not None,
           the matrix pencil (B,D) is already in generalized Schur
           form. The matrix D contains its (quasi-) upper triangular
           matrix V of the Schur decomposition of (B,D).
    :type D: (n,n) numpy array
    :param QB:
        If QB is None, a (n,n) matrix containing the left Schur vectors
            of (B,D) is returned.
        If QB is not None, it contains the left Schur vectors of (B,D),
            defaults to None
    :type QB: (n,n) numpy array,
        optional
    :param ZB:
        If ZB is None, a (n,n) matrix containing the right Schur vectors
            of (B,D) is returned.
        If ZB is not None, it contains the right Schur vectors of (B,D),
            defaults to None
    :type ZB: (n,n) numpy array,
        optional
    :param E:
        On input, E contains the right hand side Y.
        On output, E contains the solution R.
    :type E: (m,n) numpy array
    :param F:
        On input, F contains the right hand side F.
        On output, F contains the solution L.
        Right hand side Y and the solution X are (m,n) matrices.
    :type F: (m,n) numpy array
    :param sgn1: Specifies the sign in the first equation.
        Possible values: +/- 1 , defaults to 1
    :type sgn1: int, optional, optional
    :param sgn2: Specifies the sign in the second equation.
        Possible values: +/- 1 , defaults to 1
    :type sgn2: int, optional
    :param trans_AC: Specifies the form of an equation with respect to A and C:

            == False:  op1(A) = A

            == True:   op1(A) = A^T,

            defaults to False
    :type trans_AC: bool, optional
    :param trans_BD: Specifies the form of an equation with respect to B and D:

            == False:  op2(B) = B

            == True:   op2(B) = B^T,

            defaults to False
    :type trans_BD: bool, optional
    :param block_size: sets the block size (rows,cols) for the solver,
        defaults to (0,0)
    :type block_size: (int,int), optional
    :param solver: sets solver, defaults to 1
    :type solver: int, optional
    :param inplace:
        if inplace == False, solver works with copies of the matrices,
        defaults to False
    :type inplace: bool,optional
    :raise ValueError: on A, B, C, D, QA, ZA, QB, ZB, E, F type, shape or
        contingency mismatch or when QA and ZA or QB and ZB do not yield
        the same result of the 'is None' test.
    :return: (E,F, A,C,QA,ZA, B,D,QB,ZB)

             if inplace == True, the tuple contains their references to the

             modified input matrices. Otherwise, the tuple contains their

             newly allocated copies.

    .. HINT::
       |hintFortranLayout|
    """
    if numeric_t is cnp.float32_t:
        pymepack_def.mepack_single_tgcsylv_dual_blocksize_mb_set(block_size[0])
        pymepack_def.mepack_single_tgcsylv_dual_blocksize_nb_set(block_size[1])
    elif numeric_t is cnp.float64_t:
        pymepack_def.mepack_double_tgcsylv_dual_blocksize_mb_set(block_size[0])
        pymepack_def.mepack_double_tgcsylv_dual_blocksize_nb_set(block_size[1])


    pymepack_def.mepack_tgcsylv_dual_frontend_solver_set(solver)

    params = { 'A': A, 'B': B, 'C': C, 'D': D, 'E': E, 'F': F,
            'QA': QA, 'ZA': ZA, 'QB': QB, 'ZB': ZB, 'sgn1': sgn1, 'sgn2': sgn2,
            'trans_A': trans_AC, 'trans_B': trans_BD, 'hess_AC': hess_AC,
            'hess_BD': hess_BD, 'inplace': inplace}

    return GGCSylvDualSolver(params).execute()

def ggcsylv_dual_refine(
        cnp.ndarray[numeric_t, ndim=2] A not None,
        cnp.ndarray[numeric_t, ndim=2] B not None,
        cnp.ndarray[numeric_t, ndim=2] C not None,
        cnp.ndarray[numeric_t, ndim=2] D not None,
        cnp.ndarray[numeric_t, ndim=2] E not None,
        cnp.ndarray[numeric_t, ndim=2] F not None,
        cnp.ndarray[numeric_t, ndim=2] AS = None,
        cnp.ndarray[numeric_t, ndim=2] BS = None,
        cnp.ndarray[numeric_t, ndim=2] CS = None,
        cnp.ndarray[numeric_t, ndim=2] DS = None,
        cnp.ndarray[numeric_t, ndim=2] Q = None,
        cnp.ndarray[numeric_t, ndim=2] Z = None,
        cnp.ndarray[numeric_t, ndim=2] U = None,
        cnp.ndarray[numeric_t, ndim=2] V = None,
        cnp.ndarray[numeric_t, ndim=2] R = None,
        cnp.ndarray[numeric_t, ndim=2] L = None,
        numeric_t sgn1 = 1.0, numeric_t sgn2 = 1.0, trans_AC = False,trans_BD = False,
        int max_it = 10, numeric_t tau = 0.1, block_size = (0,0), int solver = 1):

    """
    *wrapper for mepack_double_ggcsylv_dual_refine.*

    Solves a generalized coupled Sylvester equation of the following form
    ::

        op1(A)^T * R + op1(C)^T * L               =  E
                                                             (1)
        sgn1 * R * op2(B)^T + sgn2 * L * op2(D)^T =  F

    with iterative refinement. (A,C) is a (m,m) matrix pencil and (B,D) is
    a (n,n) matrix pencil.
    The right hand side (E,F) and the solution (R,L) are (m,n) matrix
    pencils.
    The matrix pencils (A,C) and (B,D) need to be given in the original
    form as well as in their generalized Schur decomposition, since both
    are required in the iterative refinement procedure.

    The equation (1) is the dual to the generalized coupled Sylvester equation
    ::

        op1(A) * R + sgn1 * L * op2(B) = E
        op1(C) * R + sgn2 * L * op2(D) = F

    The equation (1) is the dual one to equation (2) with respect to the
    underlying linear system.
    Let Z be the matrix formed by rewriting (2) into its Kronecker form.
    This yields
    ::

            |kron(I, op1(A)   sgn1*kron(op2(B)^T,I)| |Vec R| |Vec E|
      Z X = |                                      |*|     |=|     |
            |kron(I, op1(C))  sgn2*kron(op2(D)^T,I)| |Vec L| |Vec F|

    Regarding Z^T one obtains
    ::

              |kron(I, op1(A)^T)   kron(I, op1(C)^T)  | |Vec R| |Vec E|
      Z^T X = |                                       |*|     |=|     |
              |sgn1*kron(op2(B),I) sgn2*kron(op2(D),I)| |Vec L| |Vec F|


    which belongs to the Sylvester equation (1). For this reason
    the parameters trans_AC and trans_BD are expressed in terms of the
    Sylvester equation (2).

    The solver switches automatically between single and double precision
    based on the precision of input arrays.

    :param A: The original matrix A defining the equation.
    :type A: (m,m) numpy array
    :param B: The original matrix B defining the equation.
    :type B: (n,n) numpy array
    :param C: The original matrix C defining the equation.
    :type C: (m,m) numpy array
    :param D: The original matrix D defining the equation.
    :type D: (n,n) Fortran-contiguous double precis
    :param E: The right hand side E.
    :type E: (m,n) numpy array
    :param F: The right hand side F.
    :type F: (m,n) numpy array
    :param AS: AS contains the generalized Schur decomposition of A,
        defaults to None
    :type AS: (m,m) numpy array,
        optional
    :param BS: BS contains the generalized Schur decomposition of B,
        defaults to None
    :type BS: (n,n) numpy array,
        optional
    :param CS: CS contains the generalized Schur decomposition of C,
        defaults to None
    :type CS: (m,m) numpy array,
        optional
    :param DS: DS contains the generalized Schur decomposition of D,
        defaults to None
    :type DS: (n,n) numpy array,
        optional
    :param Q: Q contains the left generalized Schur vectors for (A,C)
        as returned by DGGES, defaults to None
    :type Q: (m,m) numpy array,
        optional
    :param Z: Z contains the right generalized Schur vectors for (A,C)
        as returned by DGGES, defaults to None
    :type Z: (m,m) numpy array,
        optional
    :param U: U contains the left generalized Schur vectors for (B,D)
        as returned by DGGES, defaults to None
    :type U: (n,n) numpy array,
        optional
    :param V: V contains the right generalized Schur vectors for (B,D)
        as returned by DGGES, defaults to None
    :type V: (n,n) numpy array,
        optional
    :param R: R is either None or contains the initial guess for the first
        solution. If given, R is copied and modified to contain the
        solution R on output, defaults to None
    :type R: (m,n) numpy array,
        optional
    :param L: L is either None or contains the initial guess for the
        second solution. If given, L is copied and modified to contain the
        solution L on output, defaults to None
    :type L: (m,n) numpy array,
        optional
    :param sgn1: Specifies the sign in the first equation.
        Possible values: +/- 1 , defaults to 1
    :type sgn1: int, optional
    :param sgn2: Specifies the sign in the second equation.
        Possible values: +/- 1 , defaults to 1
    :type sgn2: int, optional
    :param trans_AC: Specifies the form of an equation with respect to A and C:

            == False:  op1(A) = A

            == True:   op1(A) = A^T,

            defaults to False
    :type trans_AC: bool, optional
    :param trans_BD: Specifies the form of an equation with respect to B and D:

            == False:  op2(B) = B

            == True:   op2(B) = B^T,

            defaults to False
    :type trans_BD: bool, optional
    :param max_it: the maximum number of iterations that are performed,
        2 <= max_it <= 100, defaults to 10
    :type max_it: int, optional
    :param tau: the additional security factor for the stopping criterion,
        defaults to 0.1
    :type tau: double, optional
    :param block_size: sets the block size (rows,cols) for the solver,
        defaults to (0,0)
    :type block_size: (int,int), optional
    :param solver: sets solver, defaults to 1
    :type solver: int, optional
    :raise ValueError: on A, B, C, D, QA, ZA, QB, ZB, E, F, R, L type,
        shape or contingency mismatch. The ValueError is also raised when
        AS,CS,Q,Z or BS,DS,U,V do not produce the same result of the
        'is None' test.
    :return: (R, L, max_it, tau, convlog)

            (R, L): the solution

            max_it: the number of iteration steps taken by the algorithm

            tau: the last relative residual
            when the stopping criterion got valid

            convlog: (max_it,) double precision array containing
            the convergence history of the iterative refinement.
            convlog[i] contains the maximum relative residual
            before it is solved for the i-th time.

    .. HINT::
       |hintFortranLayout|
    """
    if numeric_t is cnp.npy_float:
        pymepack_def.mepack_single_tgcsylv_dual_blocksize_mb_set(block_size[0])
        pymepack_def.mepack_single_tgcsylv_dual_blocksize_nb_set(block_size[1])
    elif numeric_t is cnp.npy_double:
        pymepack_def.mepack_double_tgcsylv_dual_blocksize_mb_set(block_size[0])
        pymepack_def.mepack_double_tgcsylv_dual_blocksize_nb_set(block_size[1])

    pymepack_def.mepack_tgcsylv_dual_frontend_solver_set(solver)

    params = { 'A': A, 'B': B, 'C': C, 'D': D, 'E': E, 'F': F, 'R': R, 'L': L,
            'AS': AS, 'BS': BS, 'CS': CS, 'DS': DS,'Q': Q,'Z': Z,'U': U,'V': V,
            'sgn1': sgn1, 'sgn2': sgn2, 'trans_A': trans_AC,
            'trans_B': trans_BD, 'max_it': max_it, 'tau': tau}

    return GGCSylvDualRefineSolver(params).execute()


mx_not_square_err_msg = '{0} needs to be a square matrix. {0}.shape = ({}, {})'
dims_mismatch_err_msg = '{0} and {1} have incompatible dimensions {0}.shape = ({}, {}) {1}.shape = ({},{})'
not_f_cont_err_msg = 'ndarray {} has to be Fortran contiguous when inplace set to \'True\''

cdef class FusedMatrix:
    cdef double [::1, :] d_Mx
    cdef float  [::1, :] f_Mx
    cdef cnp.NPY_TYPES type

    def __init__(self, matrix):
        if matrix.dtype.type is np.single:
            self.f_Mx = matrix
            self.type = cnp.NPY_FLOAT
        elif matrix.dtype.type is np.double:
            self.d_Mx = matrix
            self.type = cnp.NPY_DOUBLE
        else:
            raise ValueError(f'{matrix.dtype} is not supported')

    cdef double [::1, :] dval(self):
        return self.d_Mx

    cdef float [::1, :] fval(self):
        return self.f_Mx

    def val(self):
        if self.type == cnp.NPY_FLOAT:
            return self.f_Mx
        elif self.type == cnp.NPY_DOUBLE:
            return self.d_Mx


cdef class FusedVector:
    cdef float  [:] f_arr
    cdef double [:] d_arr
    cdef cnp.NPY_TYPES type

    def __init__(self, array):
        if array.dtype.type is np.single:
            self.f_arr = array
            self.type = cnp.NPY_FLOAT
        elif array.dtype.type is np.double:
            self.d_arr = array
            self.type = cnp.NPY_DOUBLE
        else:
            raise ValueError(f'{array.dtype} is not supported')
# maybe check if the returned value is set and raise an error if not
    cdef float  [:] fval(self):
        return self.f_arr

    cdef double [:] dval(self):
        return self.d_arr

    def val(self):
        if self.type == cnp.NPY_FLOAT:
            return self.f_arr
        elif self.type == cnp.NPY_DOUBLE:
            return self.d_arr

cdef class MepackSolverTemplate:
    cdef dict input_params
    cdef FusedMatrix A
    cdef FusedMatrix B
    cdef FusedMatrix C
    cdef FusedMatrix D
    cdef FusedMatrix E
    cdef FusedMatrix F
    cdef FusedMatrix Y
    cdef FusedMatrix AS
    cdef FusedMatrix BS
    cdef FusedMatrix CS
    cdef FusedMatrix DS
    cdef FusedMatrix Q
    cdef FusedMatrix Z
    cdef FusedMatrix U
    cdef FusedMatrix V
    cdef FusedMatrix R
    cdef FusedMatrix L
    cdef FusedMatrix QA
    cdef FusedMatrix ZA
    cdef FusedMatrix QB
    cdef FusedMatrix ZB
    cdef FusedMatrix X
    cdef str FACTA
    cdef str FACTB
    cdef str TRANS_A
    cdef str TRANS_B
    cdef FusedVector sgn
    cdef FusedVector sgn2
    cdef size_t ldwork
    cdef FusedVector work
    cdef FusedVector scale
    cdef int [:] info
    cdef int [:] max_it
    cdef FusedVector tau
    cdef FusedVector convlog
    cdef str guess
    cdef cnp.NPY_TYPES precision
    cdef str solver_prefix

    def __init__(self, params):
        if params['A'].dtype.type is np.single:
            self.precision = cnp.NPY_FLOAT
            self.solver_prefix = "sla_"
            self.scale = FusedVector(np.ndarray(shape=(1,), dtype=np.single))
            self.tau = FusedVector(np.ndarray(shape=(1,), dtype=np.single))
        elif params['A'].dtype.type is np.double:
            self.precision = cnp.NPY_DOUBLE
            self.solver_prefix = "dla_"
            self.scale = FusedVector(np.ndarray(shape=(1,), dtype=np.double))
            self.tau = FusedVector(np.ndarray(shape=(1,), dtype=np.double))
        self.input_params = params
        self.info = np.ndarray(shape=(1,), dtype=np.int32)
        if self.precision == cnp.NPY_FLOAT:
            self.scale = FusedVector( np.ndarray(shape=(1,), dtype=np.single) )
            self.sgn = FusedVector( np.ndarray(shape=(1,), dtype=np.single) )
            self.sgn2 = FusedVector( np.ndarray(shape=(1,), dtype=np.single) )
        elif self.precision == cnp.NPY_DOUBLE:
            self.scale = FusedVector( np.ndarray(shape=(1,), dtype=np.double) )
            self.sgn = FusedVector( np.ndarray(shape=(1,), dtype=np.double) )
            self.sgn2 = FusedVector( np.ndarray(shape=(1,), dtype=np.double) )
        self.scale.val()[0] = 1.0
        self.max_it = np.ndarray(shape=(1,), dtype=np.int32)


    cdef void _validate_matrices_contingency(self):
        if 'inplace' in self.input_params.keys() and not self.input_params['inplace']:
            return #return if inplace is disabled
        if 'inplace' not in self.input_params.keys():
            return #return if a solver with refinement is executed
        for key, value in self.input_params.items():
            if (type(value) is np.ndarray and value.ndim == 2 and
                not value.flags.f_contiguous):
                    raise ValueError(not_f_cont_err_msg.format(key))

    cdef void _validate_params(self):
        pass

    cdef void _create_execution_params(self):
        pass

    cdef void _compute_workspace(self):
        pass

    cdef void _set_workspace(self):
        if self.precision == cnp.NPY_DOUBLE:
            self.work = FusedVector(np.ndarray(shape=(self.ldwork,), dtype=np.double))
        elif self.precision == cnp.NPY_FLOAT:
            self.work = FusedVector(np.ndarray(shape=(self.ldwork,), dtype=np.single))

    cdef void _set_convlog(self):
        if self.precision == cnp.NPY_FLOAT:
            self.convlog = FusedVector(np.ndarray(shape=(self.max_it[0],), dtype=np.single))
        elif self.precision == cnp.NPY_DOUBLE:
            self.convlog = FusedVector(np.ndarray(shape=(self.max_it[0],), dtype=np.double))

    cdef void _execute_mepack_solver(self):
        pass

    def _get_execution_results(self):
        pass

    def execute(self):
        self._validate_matrices_contingency()
        self._validate_params()
        self._create_execution_params()
        self._compute_workspace()
        self._set_workspace()
        self._execute_mepack_solver()
        return self._get_execution_results()


cdef class GelyapSolver(MepackSolverTemplate):

    cdef void _validate_params(self):
        params = self.input_params
        A,X,Q,hess = (params['A'], params['X'], params['Q'], params['hess_A'])
        if A.shape[0] != A.shape[1]:
            raise ValueError(mx_not_square_err_msg.format("A", A.shape[0], A.shape[1]))
        if Q is not None and hess:
            raise ValueError('A is provided as a Schur form while hess=True')
        if A.shape != X.shape:
            raise ValueError(dims_mismatch_err_msg.format("A", "X", A.shape[0], A.shape[1], X.shape[0], X.shape[1]))
        if Q is not None and A.shape != Q.shape:
            raise ValueError(dims_mismatch_err_msg.format.format("A", "Q", A.shape[0], A.shape[1], Q.shape[0], Q.shape[1]))

    cdef void _create_execution_params(self):
        params = self.input_params
        A,X,Q,hess,inplace = (params['A'],params['X'],params['Q'],
                                params['hess_A'],params['inplace'])
        if Q is not None:
            self.FACTA = 'F'
            self.Q = FusedMatrix(Q)
        else:
            if hess:
                self.FACTA = 'H'
            else:
                self.FACTA = 'N'
            self.Q = FusedMatrix(np.zeros_like(A, order='F'))

        self.A = FusedMatrix(A if inplace else A.copy(order='F'))
        self.X = FusedMatrix(X if inplace else X.copy(order='F'))
        self.TRANS_A = 'T' if params['trans_A'] else 'N'

    cdef void _compute_workspace(self):
        ldwork = pymepack_def.mepack_memory_frontend(
            (self.solver_prefix + 'gelyap').encode(), self.FACTA.encode(), self.FACTA.encode(),
            self.A.val().shape[0], self.A.val().shape[0])
        if ldwork < 0:
            raise Exception('memory allocation failed with code ' + str(ldwork))
        self.ldwork = ldwork

    cdef void _execute_mepack_solver(self):
        if self.precision == cnp.NPY_DOUBLE:
            pymepack_def.mepack_double_gelyap(self.FACTA.encode(), self.TRANS_A.encode(),
                                       self.A.dval().shape[0],
                                       &(self.A.dval()[0,0]), self.A.dval().shape[0],
                                       &(self.Q.dval()[0,0]), self.Q.dval().shape[0],
                                       &(self.X.dval()[0,0]), self.X.dval().shape[0],
                                       &(self.scale.dval()[0]),
                                       &(self.work.dval()[0]),
                                       self.ldwork,
                                       &self.info[0])
        elif self.precision == cnp.NPY_FLOAT:
            pymepack_def.mepack_single_gelyap(self.FACTA.encode(), self.TRANS_A.encode(),
                                       self.A.fval().shape[0],
                                       &(self.A.fval()[0,0]), self.A.fval().shape[0],
                                       &(self.Q.fval()[0,0]), self.Q.fval().shape[0],
                                       &(self.X.fval()[0,0]), self.X.fval().shape[0],
                                       &(self.scale.fval()[0]),
                                       &(self.work.fval()[0]),
                                       self.ldwork,
                                       &self.info[0])

    def _get_execution_results(self):
        return (np.asarray(self.X.val()),
                np.asarray(self.A.val()),
                np.asarray(self.Q.val()))

cdef class GelyapRefineSolver(MepackSolverTemplate):

    cdef void _validate_params(self):
        params = self.input_params
        A,AS,Q,Y = (params['A'],params['AS'],params['Q'],params['Y'])
        if A.shape[0] != A.shape[1]:
            raise ValueError(mx_not_square_err_msg.format("A", A.shape[0], A.shape[1]))
        if not(A.shape == Y.shape):
            raise ValueError('A and Y have incompatible dimensions')
        if not(AS is None and Q is None or AS is not None and Q is not None):
            err_msg = 'both matrices AS and Q should be provided or skipped'
            raise ValueError(err_msg)
        if Q is not None and A.shape != Q.shape:
            raise ValueError(dims_mismatch_err_msg.format.format("A", "Q", A.shape[0], A.shape[1], Q.shape[0], Q.shape[1]))
        if AS is not None and A.shape != AS.shape:
            raise ValueError(dims_mismatch_err_msg.format.format("A", "AS", A.shape[0], A.shape[1], AS.shape[0], AS.shape[1]))

    cdef void _create_execution_params(self):
        params = self.input_params
        A,AS,X,Y,Q = (params['A'],params['AS'],params['X'],
                      params['Y'],params['Q'])
        if Q is None:
            schur_dec = linalg.lapack.dgees(lambda: None, A)
            self.AS = FusedMatrix(schur_dec[0].copy(order='F'))
            self.Q = FusedMatrix(schur_dec[4].copy(order='F'))
        else:
            self.AS = FusedMatrix(AS.astype(AS.dtype, order='F', copy=False))
            self.Q = FusedMatrix(Q.astype(Q.dtype, order='F', copy=False))

        self.A = FusedMatrix(A.astype(A.dtype, order='F', copy=False))
        self.Y = FusedMatrix(Y.astype(Y.dtype, order='F', copy=False))
        if X is None:
            self.X = FusedMatrix(np.zeros_like(A, order='F'))
            self.guess = 'N'
        else:
            self.X = FusedMatrix(X.copy(order='F'))
            self.guess = 'I'

        self.max_it[0] = params['max_it']
        self.tau.val()[0] = params['tau']
        self.TRANS_A = 'T' if params['trans_A'] else 'N'
        self._set_convlog()

    cdef void _compute_workspace(self):
        ldwork = pymepack_def.mepack_memory_frontend(
            (self.solver_prefix + 'gelyap_refine').encode(), 'N'.encode(), 'N'.encode(),
            self.A.val().shape[0], self.A.val().shape[0])
        if ldwork < 0:
            raise Exception('memory allocation failed with code ' + str(ldwork))
        self.ldwork = ldwork

    cdef void _execute_mepack_solver(self):
        if self.precision == cnp.NPY_DOUBLE:
            pymepack_def.mepack_double_gelyap_refine(self.TRANS_A.encode(),
                              self.guess.encode(),
                              self.A.dval().shape[0],
                              &self.A.dval()[0,0], self.A.dval().shape[0],
                              &self.X.dval()[0,0], self.A.dval().shape[0],
                              &self.Y.dval()[0,0], self.Y.dval().shape[0],
                              &self.AS.dval()[0,0], self.AS.dval().shape[0],
                              &self.Q.dval()[0,0], self.Q.dval().shape[0],
                              &self.max_it[0],
                              &self.tau.dval()[0],
                              &self.convlog.dval()[0],
                              &self.work.dval()[0],
                              self.ldwork,
                              &self.info[0])
        elif self.precision == cnp.NPY_FLOAT:
            pymepack_def.mepack_single_gelyap_refine(self.TRANS_A.encode(),
                              self.guess.encode(),
                              self.A.fval().shape[0],
                              &self.A.fval()[0,0], self.A.fval().shape[0],
                              &self.X.fval()[0,0], self.A.fval().shape[0],
                              &self.Y.fval()[0,0], self.Y.fval().shape[0],
                              &self.AS.fval()[0,0], self.AS.fval().shape[0],
                              &self.Q.fval()[0,0], self.Q.fval().shape[0],
                              &self.max_it[0],
                              &self.tau.fval()[0],
                              &self.convlog.fval()[0],
                              &self.work.fval()[0],
                              self.ldwork,
                              &self.info[0])

    def _get_execution_results(self):
        return (np.asarray(self.X.val()), self.max_it[0], self.tau.val()[0],
                np.asarray(self.convlog.val()))


cdef class GesteinSolver(GelyapSolver):

    cdef void _compute_workspace(self):
        ldwork = pymepack_def.mepack_memory_frontend(
            'dla_gestein'.encode(), self.FACTA.encode(), self.FACTA.encode(),
            self.A.val().shape[0], self.A.val().shape[0])
        if ldwork < 0:
            raise Exception('memory allocation failed with code ' + str(ldwork))
        self.ldwork = ldwork

    cdef void _execute_mepack_solver(self):
        if self.precision == cnp.NPY_DOUBLE:
            pymepack_def.mepack_double_gestein(self.FACTA.encode(), self.TRANS_A.encode(),
                                       self.A.dval().shape[0],
                                       &self.A.dval()[0,0], self.A.dval().shape[0],
                                       &self.Q.dval()[0,0], self.Q.dval().shape[0],
                                       &self.X.dval()[0,0], self.X.dval().shape[0],
                                       &self.scale.dval()[0],
                                       &self.work.dval()[0],
                                       self.ldwork,
                                       &self.info[0])
        if self.precision == cnp.NPY_FLOAT:
            pymepack_def.mepack_single_gestein(self.FACTA.encode(), self.TRANS_A.encode(),
                                       self.A.fval().shape[0],
                                       &self.A.fval()[0,0], self.A.fval().shape[0],
                                       &self.Q.fval()[0,0], self.Q.fval().shape[0],
                                       &self.X.fval()[0,0], self.X.fval().shape[0],
                                       &self.scale.fval()[0],
                                       &self.work.fval()[0],
                                       self.ldwork,
                                       &self.info[0])


cdef class GesteinRefineSolver(GelyapRefineSolver):
    cdef void _compute_workspace(self):
        ldwork = pymepack_def.mepack_memory_frontend(
            'dla_gestein_refine'.encode(), 'N'.encode(), 'N'.encode(),
            self.A.val().shape[0], self.A.val().shape[0])
        if ldwork < 0:
            raise Exception('memory allocation failed with code ' + str(ldwork))
        self.ldwork = ldwork


    cdef void _execute_mepack_solver(self):
        if self.precision == cnp.NPY_DOUBLE:
            pymepack_def.mepack_double_gestein_refine(self.TRANS_A.encode(),
                              self.guess.encode(),
                              self.A.dval().shape[0],
                              &self.A.dval()[0,0], self.A.dval().shape[0],
                              &self.X.dval()[0,0], self.A.dval().shape[0],
                              &self.Y.dval()[0,0], self.Y.dval().shape[0],
                              &self.AS.dval()[0,0], self.AS.dval().shape[0],
                              &self.Q.dval()[0,0], self.Q.dval().shape[0],
                              &self.max_it[0],
                              &self.tau.dval()[0],
                              &self.convlog.dval()[0],
                              &self.work.dval()[0],
                              self.ldwork,
                              &self.info[0])
        elif self.precision == cnp.NPY_FLOAT:
            pymepack_def.mepack_single_gestein_refine(self.TRANS_A.encode(),
                              self.guess.encode(),
                              self.A.fval().shape[0],
                              &self.A.fval()[0,0], self.A.fval().shape[0],
                              &self.X.fval()[0,0], self.A.fval().shape[0],
                              &self.Y.fval()[0,0], self.Y.fval().shape[0],
                              &self.AS.fval()[0,0], self.AS.fval().shape[0],
                              &self.Q.fval()[0,0], self.Q.fval().shape[0],
                              &self.max_it[0],
                              &self.tau.fval()[0],
                              &self.convlog.fval()[0],
                              &self.work.fval()[0],
                              self.ldwork,
                              &self.info[0])

cdef class GGLyapSolver(MepackSolverTemplate):
    cdef void _validate_params(self):
        params = self.input_params
        A,B,Q,Z,X=(params['A'],params['B'],params['Q'],params['Z'],params['X'])
        hess = params['hess_AB']

        if A.shape[0] != A.shape[1]:
            raise ValueError(mx_not_square_err_msg.format("A", A.shape[0], A.shape[1]))
        if not(params['A'].shape == params['B'].shape == params['X'].shape):
            raise ValueError('A, B and X have incompatible dimensions')
        if not (Q is None and Z is None or Q is not None and Z is not None):
            err_msg = 'both matrices Q and Z should be provided or skipped'
            raise ValueError(err_msg)
        if hess and Q is not None:
            err_msg='(A,B) is given as Schur factorization while hess_AB=True'
            raise ValueError(err_msg)

    cdef void _create_execution_params(self):
        params = self.input_params
        A,B,Q,Z,X,hess,inplace = (params['A'],params['B'],params['Q'],
                             params['Z'], params['X'],params['hess_AB'],
                             params['inplace'])

        if Q is None:
            if hess:
                self.FACTA = 'H'
            else:
                self.FACTA = 'N'
            self.Q = FusedMatrix(np.zeros_like(A, order='F'))
            self.Z = FusedMatrix(np.zeros_like(A, order='F'))
        elif Q is not None:
            self.FACTA = 'F'
            self.Q = FusedMatrix(Q if inplace else Q.copy(order='F'))
            self.Z = FusedMatrix(Z if inplace else Z.copy(order='F'))

        self.A = FusedMatrix(A if inplace else A.copy(order='F'))
        self.B = FusedMatrix(B if inplace else B.copy(order='F'))
        self.X = FusedMatrix(X if inplace else X.copy(order='F'))
        self.TRANS_A = 'T' if params['trans_A'] else 'N'

    cdef void _compute_workspace(self):
        ldwork = pymepack_def.mepack_memory_frontend(
                'dla_gglyap'.encode(), self.FACTA.encode(), self.FACTA.encode(),
                self.A.val().shape[0], self.A.val().shape[0])
        if ldwork < 0:
            raise Exception('memory allocation failed with code ' + str(ldwork))
        self.ldwork = ldwork


    cdef void _execute_mepack_solver(self):
        if self.precision == cnp.NPY_DOUBLE:
            pymepack_def.mepack_double_gglyap(self.FACTA.encode(), self.TRANS_A.encode(),
                                       self.A.dval().shape[0],
                                       &self.A.dval()[0,0], self.A.dval().shape[0],
                                       &self.B.dval()[0,0], self.B.dval().shape[0],
                                       &self.Q.dval()[0,0], self.Q.dval().shape[0],
                                       &self.Z.dval()[0,0], self.Z.dval().shape[0],
                                       &self.X.dval()[0,0], self.X.dval().shape[0],
                                       &self.scale.dval()[0],
                                       &self.work.dval()[0],
                                       self.ldwork,
                                       &self.info[0])
        elif self.precision == cnp.NPY_FLOAT:
            pymepack_def.mepack_single_gglyap(self.FACTA.encode(), self.TRANS_A.encode(),
                                       self.A.fval().shape[0],
                                       &self.A.fval()[0,0], self.A.fval().shape[0],
                                       &self.B.fval()[0,0], self.B.fval().shape[0],
                                       &self.Q.fval()[0,0], self.Q.fval().shape[0],
                                       &self.Z.fval()[0,0], self.Z.fval().shape[0],
                                       &self.X.fval()[0,0], self.X.fval().shape[0],
                                       &self.scale.fval()[0],
                                       &self.work.fval()[0],
                                       self.ldwork,
                                       &self.info[0])


    def _get_execution_results(self):
        return (np.asarray(self.X.val()),
                np.asarray(self.A.val()), np.asarray(self.B.val()),
                np.asarray(self.Q.val()), np.asarray(self.Z.val()))

cdef class GGSteinSolver(GGLyapSolver):

    cdef void _set_exec_workspace(self):
        ldwork = pymepack_def.mepack_memory_frontend(
                'dla_ggstein'.encode(), self.FACTA.encode(), self.FACTA.encode(),
                self.A.val().shape[0], self.A.val().shape[0])
        if ldwork < 0:
            raise Exception('memory allocation failed with code ' + str(ldwork))
        self.ldwork = ldwork


    cdef void _execute_mepack_solver(self):
        if self.precision == cnp.NPY_DOUBLE:
            pymepack_def.mepack_double_ggstein(self.FACTA.encode(), self.TRANS_A.encode(),
                                       self.A.dval().shape[0],
                                       &self.A.dval()[0,0], self.A.dval().shape[0],
                                       &self.B.dval()[0,0], self.B.dval().shape[0],
                                       &self.Q.dval()[0,0], self.Q.dval().shape[0],
                                       &self.Z.dval()[0,0], self.Z.dval().shape[0],
                                       &self.X.dval()[0,0], self.X.dval().shape[0],
                                       &self.scale.dval()[0],
                                       &self.work.dval()[0],
                                       self.ldwork,
                                       &self.info[0])
        elif self.precision == cnp.NPY_FLOAT:
            pymepack_def.mepack_single_ggstein(self.FACTA.encode(), self.TRANS_A.encode(),
                                       self.A.fval().shape[0],
                                       &self.A.fval()[0,0], self.A.fval().shape[0],
                                       &self.B.fval()[0,0], self.B.fval().shape[0],
                                       &self.Q.fval()[0,0], self.Q.fval().shape[0],
                                       &self.Z.fval()[0,0], self.Z.fval().shape[0],
                                       &self.X.fval()[0,0], self.X.fval().shape[0],
                                       &self.scale.fval()[0],
                                       &self.work.fval()[0],
                                       self.ldwork,
                                       &self.info[0])


cdef class GGLyapRefineSolver(MepackSolverTemplate):
    cdef void _validate_params(self):
        params = self.input_params
        AS,BS,Q,Z=(params['AS'],params['BS'],params['Q'],params['Z'])
        if ( not all(v is not None for v in [AS, BS, Q, Z]) and
             not all(v is None for v in [AS, BS, Q, Z])         ):
            err_msg="matrices AS,BS,Q,Z should be provided together or skipped"
            raise ValueError(err_msg)

    cdef void _create_execution_params(self):
        params = self.input_params
        A,B,Y,AS,BS,Q,Z,X=(params['A'],params['B'],params['Y'],params['AS'],
                         params['BS'],params['Q'],params['Z'],params['X'])
        if AS is None:
            schur = linalg.qz(A,B)
            self.AS = FusedMatrix(schur[0].copy(order='F'))
            self.BS = FusedMatrix(schur[1].copy(order='F'))
            self.Q = FusedMatrix(schur[2].copy(order='F'))
            self.Z = FusedMatrix(schur[3].copy(order='F'))
        else:
            self.AS = FusedMatrix(AS.astype(AS.dtype, order='F', copy=False))
            self.BS = FusedMatrix(BS.astype(BS.dtype, order='F', copy=False))
            self.Q = FusedMatrix(Q.astype(Q.dtype, order='F', copy=False))
            self.Z = FusedMatrix(Z.astype(Z.dtype, order='F', copy=False))
        self.A = FusedMatrix(A.astype(A.dtype, order='F', copy=False))
        self.B = FusedMatrix(B.astype(B.dtype, order='F', copy=False))
        self.Y = FusedMatrix(Y.astype(Y.dtype, order='F', copy=False))
        if X is None:
            self.X = FusedMatrix(np.zeros_like(A, order='F'))
            self.guess = 'N'
        else:
            self.X = FusedMatrix(X.copy(order='F'))
            self.guess = 'I'
        self.max_it[0] = params['max_it']
        self.tau.val()[0] = params['tau']
        self.TRANS_A = 'T' if params['trans_A'] else 'N'
        self._set_convlog()

    cdef void _compute_workspace(self):
        ldwork = pymepack_def.mepack_memory_frontend(
                'dla_gglyap_refine'.encode(), 'N'.encode(), 'N'.encode(),
                self.A.val().shape[0], self.A.val().shape[0])
        if ldwork < 0:
            raise Exception('memory allocation failed with code ' + str(ldwork))
        self.ldwork = ldwork

    cdef void _execute_mepack_solver(self):
        if self.precision == cnp.NPY_DOUBLE:
            pymepack_def.mepack_double_gglyap_refine(self.TRANS_A.encode(),
                              self.guess.encode(),
                              self.A.dval().shape[0],
                              &self.A.dval()[0,0], self.A.dval().shape[0],
                              &self.B.dval()[0,0], self.B.dval().shape[0],
                              &self.X.dval()[0,0], self.X.dval().shape[0],
                              &self.Y.dval()[0,0], self.Y.dval().shape[0],
                              &self.AS.dval()[0,0], self.AS.dval().shape[0],
                              &self.BS.dval()[0,0], self.BS.dval().shape[0],
                              &self.Q.dval()[0,0], self.Q.dval().shape[0],
                              &self.Z.dval()[0,0], self.Z.dval().shape[0],
                              &self.max_it[0],
                              &self.tau.dval()[0],
                              &self.convlog.dval()[0],
                              &self.work.dval()[0],
                              self.ldwork,
                              &self.info[0])
        if self.precision == cnp.NPY_FLOAT:
            pymepack_def.mepack_single_gglyap_refine(self.TRANS_A.encode(),
                              self.guess.encode(),
                              self.A.fval().shape[0],
                              &self.A.fval()[0,0], self.A.fval().shape[0],
                              &self.B.fval()[0,0], self.B.fval().shape[0],
                              &self.X.fval()[0,0], self.X.fval().shape[0],
                              &self.Y.fval()[0,0], self.Y.fval().shape[0],
                              &self.AS.fval()[0,0], self.AS.fval().shape[0],
                              &self.BS.fval()[0,0], self.BS.fval().shape[0],
                              &self.Q.fval()[0,0], self.Q.fval().shape[0],
                              &self.Z.fval()[0,0], self.Z.fval().shape[0],
                              &self.max_it[0],
                              &self.tau.fval()[0],
                              &self.convlog.fval()[0],
                              &self.work.fval()[0],
                              self.ldwork,
                              &self.info[0])

    def _get_execution_results(self):
        return (np.asarray(self.X.val()), self.max_it[0], self.tau.val()[0],
                np.asarray(self.convlog.val()))

cdef class GGSteinRefineSolver(GGLyapRefineSolver):
    cdef void _compute_workspace(self):
        ldwork = pymepack_def.mepack_memory_frontend(
                'dla_ggstein_refine'.encode(), 'N'.encode(), 'N'.encode(),
                self.A.val().shape[0], self.A.val().shape[0])
        if ldwork < 0:
            raise Exception('memory allocation failed with code ' + str(ldwork))
        self.ldwork = ldwork

    cdef void _execute_mepack_solver(self):
        if self.precision == cnp.NPY_DOUBLE:
            pymepack_def.mepack_double_ggstein_refine(self.TRANS_A.encode(),
                              self.guess.encode(),
                              self.A.dval().shape[0],
                              &self.A.dval()[0,0], self.A.dval().shape[0],
                              &self.B.dval()[0,0], self.B.dval().shape[0],
                              &self.X.dval()[0,0], self.X.dval().shape[0],
                              &self.Y.dval()[0,0], self.Y.dval().shape[0],
                              &self.AS.dval()[0,0], self.AS.dval().shape[0],
                              &self.BS.dval()[0,0], self.BS.dval().shape[0],
                              &self.Q.dval()[0,0], self.Q.dval().shape[0],
                              &self.Z.dval()[0,0], self.Z.dval().shape[0],
                              &self.max_it[0],
                              &self.tau.dval()[0],
                              &self.convlog.dval()[0],
                              &self.work.dval()[0],
                              self.ldwork,
                              &self.info[0])
        elif self.precision == cnp.NPY_FLOAT:
            pymepack_def.mepack_single_ggstein_refine(self.TRANS_A.encode(),
                              self.guess.encode(),
                              self.A.fval().shape[0],
                              &self.A.fval()[0,0], self.A.fval().shape[0],
                              &self.B.fval()[0,0], self.B.fval().shape[0],
                              &self.X.fval()[0,0], self.X.fval().shape[0],
                              &self.Y.fval()[0,0], self.Y.fval().shape[0],
                              &self.AS.fval()[0,0], self.AS.fval().shape[0],
                              &self.BS.fval()[0,0], self.BS.fval().shape[0],
                              &self.Q.fval()[0,0], self.Q.fval().shape[0],
                              &self.Z.fval()[0,0], self.Z.fval().shape[0],
                              &self.max_it[0],
                              &self.tau.fval()[0],
                              &self.convlog.fval()[0],
                              &self.work.fval()[0],
                              self.ldwork,
                              &self.info[0])


cdef class GesylvSolver(MepackSolverTemplate):

    cdef void _validate_params(self):
        params = self.input_params
        if params['QA'] is not None and params['hess_A']:
            raise ValueError("A is provided as a Schur form while hess_A=True")
        if params['QB'] is not None and params['hess_B']:
            raise ValueError("A is provided as a Schur form while hess_B=True")
        if (params['X'].shape[0] != params['A'].shape[0] or
            params['X'].shape[1] != params['B'].shape[0]   ):
            raise ValueError('X has dimensions incompatible with A and B')

    cdef void _create_execution_params(self):
        params = self.input_params
        A,B,X,QA,QB,hess_A,hess_B,inplace = (params['A'],params['B'],params['X'],
                                 params['QA'],params['QB'],params['hess_A'],
                                 params['hess_B'],params['inplace'])

        if QA is not None:
            self.FACTA = 'F'
            self.QA = FusedMatrix(QA)
        else:
            if hess_A:
                self.FACTA = 'H'
            else:
                self.FACTA = 'N'
            self.QA = FusedMatrix(np.zeros_like(A, order='F'))

        if QB is not None:
            self.FACTB = 'F'
            self.QB = FusedMatrix(QB)
        else:
            if hess_B:
                self.FACTB = 'H'
            else:
                self.FACTB = 'N'
            self.QB = FusedMatrix(np.zeros_like(B, order='F'))


        self.A = FusedMatrix(A if inplace else A.copy(order='F'))
        self.B = FusedMatrix(B if inplace else B.copy(order='F'))
        self.X = FusedMatrix(X if inplace else X.copy(order='F'))

        self.TRANS_A = 'T' if params['trans_A'] else 'N'
        self.TRANS_B = 'T' if params['trans_B'] else 'N'
        self.sgn.val()[0] = params['sgn']

    cdef void _compute_workspace(self):
        ldwork = pymepack_def.mepack_memory_frontend(
            'dla_gesylv'.encode(), self.FACTA.encode(), self.FACTB.encode(),
            self.A.val().shape[0], self.B.val().shape[0])
        if ldwork < 0:
            raise Exception('memory allocation failed with code ' + str(ldwork))
        self.ldwork = ldwork


    cdef void _execute_mepack_solver(self):
        if self.precision == cnp.NPY_DOUBLE:
            pymepack_def.mepack_double_gesylv(self.FACTA.encode(),
                          self.FACTB.encode(),
                          self.TRANS_A.encode(),
                          self.TRANS_B.encode(),
                          self.sgn.dval()[0],
                          self.A.dval().shape[0],
                          self.B.dval().shape[0],
                          &(self.A.dval()[0,0]), self.A.dval().shape[0],
                          &self.B.dval()[0,0], self.B.dval().shape[0],
                          &self.QA.dval()[0,0], self.QA.dval().shape[0],
                          &self.QB.dval()[0,0], self.QB.dval().shape[0],
                          &self.X.dval()[0,0], self.X.dval().shape[0],
                          &self.scale.dval()[0],
                          &self.work.dval()[0],
                          self.ldwork,
                          &self.info[0])
        elif self.precision == cnp.NPY_FLOAT:
            pymepack_def.mepack_single_gesylv(self.FACTA.encode(),
                          self.FACTB.encode(),
                          self.TRANS_A.encode(),
                          self.TRANS_B.encode(),
                          self.sgn.fval()[0],
                          self.A.fval().shape[0],
                          self.B.fval().shape[0],
                          &(self.A.fval()[0,0]), self.A.fval().shape[0],
                          &self.B.fval()[0,0], self.B.fval().shape[0],
                          &self.QA.fval()[0,0], self.QA.fval().shape[0],
                          &self.QB.fval()[0,0], self.QB.fval().shape[0],
                          &self.X.fval()[0,0], self.X.fval().shape[0],
                          &self.scale.fval()[0],
                          &self.work.fval()[0],
                          self.ldwork,
                          &self.info[0])


    def _get_execution_results(self):
        return (np.asarray(self.X.val()),
                np.asarray(self.A.val()),
                np.asarray(self.QA.val()),
                np.asarray(self.B.val()),
                np.asarray(self.QB.val()))

cdef class GesylvSolver2(GesylvSolver):
    cdef void _compute_workspace(self):
        ldwork = pymepack_def.mepack_memory_frontend(
            'dla_gesylv2'.encode(), self.FACTA.encode(), self.FACTB.encode(),
            self.A.val().shape[0], self.B.val().shape[0])
        if ldwork < 0:
            raise Exception('memory allocation failed with code ' + str(ldwork))
        self.ldwork = ldwork

    cdef void _execute_mepack_solver(self):
        if self.precision == cnp.NPY_DOUBLE:
            pymepack_def.mepack_double_gesylv2(self.FACTA.encode(),
                          self.FACTB.encode(),
                          self.TRANS_A.encode(),
                          self.TRANS_B.encode(),
                          self.sgn.dval()[0],
                          self.A.dval().shape[0],
                          self.B.dval().shape[0],
                          &(self.A.dval()[0,0]), self.A.dval().shape[0],
                          &self.B.dval()[0,0], self.B.dval().shape[0],
                          &self.QA.dval()[0,0], self.QA.dval().shape[0],
                          &self.QB.dval()[0,0], self.QB.dval().shape[0],
                          &self.X.dval()[0,0], self.X.dval().shape[0],
                          &self.scale.dval()[0],
                          &self.work.dval()[0],
                          self.ldwork,
                          &self.info[0])
        elif self.precision == cnp.NPY_FLOAT:
            pymepack_def.mepack_single_gesylv2(self.FACTA.encode(),
                          self.FACTB.encode(),
                          self.TRANS_A.encode(),
                          self.TRANS_B.encode(),
                          self.sgn.fval()[0],
                          self.A.fval().shape[0],
                          self.B.fval().shape[0],
                          &(self.A.fval()[0,0]), self.A.fval().shape[0],
                          &self.B.fval()[0,0], self.B.fval().shape[0],
                          &self.QA.fval()[0,0], self.QA.fval().shape[0],
                          &self.QB.fval()[0,0], self.QB.fval().shape[0],
                          &self.X.fval()[0,0], self.X.fval().shape[0],
                          &self.scale.fval()[0],
                          &self.work.fval()[0],
                          self.ldwork,
                          &self.info[0])

cdef class GesylvRefineSolver(GesylvSolver):
    cdef void _validate_params(self):
        params = self.input_params
        AS,BS,Q,R = (params['AS'], params['BS'], params['Q'], params['R'])

        if params['X'] is not None:
            super._validate_params()

        if ( not all(v is not None for v in [AS, Q]) and
             not all(v is None for v in [AS, Q])         ):
            err_msg = 'both matrices AS and Q should be provided or skipped'
            raise ValueError(err_msg)
        if ( not all(v is not None for v in [BS, R]) and
             not all(v is None for v in [BS, R])         ):
            err_msg = 'both matrices BS and R should be provided or skipped'
            raise ValueError(err_msg)

    cdef void _create_execution_params(self):
        params = self.input_params
        A,B,Y,AS,BS,Q,R,X = (params['A'],params['B'],params['Y'],params['AS'],
                             params['BS'],params['Q'],params['R'],params['X'])

        self.A = FusedMatrix(A.astype(A.dtype, order='F', copy=False))
        self.B = FusedMatrix(B.astype(B.dtype, order='F', copy=False))
        self.Y = FusedMatrix(Y.astype(Y.dtype, order='F', copy=False))

        if AS is None:
            schur_dec = linalg.lapack.dgees(lambda: None, A)
            self.AS = FusedMatrix(schur_dec[0].copy(order='F'))
            self.Q  = FusedMatrix(schur_dec[4].copy(order='F'))
        else:
            self.AS = FusedMatrix(AS.astype(AS.dtype, order='F', copy=False))
            self.Q = FusedMatrix(Q.astype(Q.dtype, order='F', copy=False))

        if BS is None:
            schur_dec = linalg.lapack.dgees(lambda: None, B)
            self.BS = FusedMatrix(schur_dec[0].copy(order='F'))
            self.R  = FusedMatrix(schur_dec[4].copy(order='F'))
        else:
            self.BS = FusedMatrix(BS.astype(BS.dtype, order='F', copy=False))
            self.R = FusedMatrix(R.astype(R.dtype, order='F', copy=False))

        if X is None:
            self.X = FusedMatrix(np.zeros((A.shape[0], B.shape[0]), dtype=A.dtype, order='F'))
            self.guess = 'N'
        else:
            self.X = FusedMatrix(X.copy(order='F'))
            self.guess = 'I'

        self.sgn.val()[0] = params['sgn']
        self.TRANS_A = 'T' if params['trans_A'] else 'N'
        self.TRANS_B = 'T' if params['trans_B'] else 'N'
        self.max_it[0] = params['max_it']
        self.tau.val()[0] = params['tau']
        self._set_convlog()

    cdef void _compute_workspace(self):
        ldwork = pymepack_def.mepack_memory_frontend(
            'dla_gesylv_refine'.encode(), 'N'.encode(), 'N'.encode(),
            self.A.val().shape[0], self.B.val().shape[0])
        if ldwork < 0:
            raise Exception('memory allocation failed with code ' + str(ldwork))
        self.ldwork = ldwork

    cdef void _execute_mepack_solver(self):
        if self.precision == cnp.NPY_DOUBLE:
            pymepack_def.mepack_double_gesylv_refine(self.TRANS_A.encode(), self.TRANS_B.encode(),
                              self.guess.encode(), self.sgn.dval()[0],
                              self.A.dval().shape[0], self.B.dval().shape[0],
                              &self.A.dval()[0,0], self.A.dval().shape[0],
                              &self.B.dval()[0,0], self.B.dval().shape[0],
                              &self.X.dval()[0,0], self.X.dval().shape[0],
                              &self.Y.dval()[0,0], self.Y.dval().shape[0],
                              &self.AS.dval()[0,0],self.AS.dval().shape[0],
                              &self.BS.dval()[0,0],self.BS.dval().shape[0],
                              &self.Q.dval()[0,0], self.Q.dval().shape[0],
                              &self.R.dval()[0,0], self.R.dval().shape[0],
                              &self.max_it[0], &self.tau.dval()[0],
                              &self.convlog.dval()[0],
                              &self.work.dval()[0], self.ldwork,
                              &self.info[0])
        elif self.precision == cnp.NPY_FLOAT:
            pymepack_def.mepack_single_gesylv_refine(self.TRANS_A.encode(), self.TRANS_B.encode(),
                              self.guess.encode(), self.sgn.fval()[0],
                              self.A.fval().shape[0], self.B.fval().shape[0],
                              &self.A.fval()[0,0], self.A.fval().shape[0],
                              &self.B.fval()[0,0], self.B.fval().shape[0],
                              &self.X.fval()[0,0], self.X.fval().shape[0],
                              &self.Y.fval()[0,0], self.Y.fval().shape[0],
                              &self.AS.fval()[0,0],self.AS.fval().shape[0],
                              &self.BS.fval()[0,0],self.BS.fval().shape[0],
                              &self.Q.fval()[0,0], self.Q.fval().shape[0],
                              &self.R.fval()[0,0], self.R.fval().shape[0],
                              &self.max_it[0], &self.tau.fval()[0],
                              &self.convlog.fval()[0],
                              &self.work.fval()[0], self.ldwork,
                              &self.info[0])

    def _get_execution_results(self):
        return (np.asarray(self.X.val()), self.max_it[0],
                self.tau.val()[0], np.asarray(self.convlog.val()))

cdef class GesylvRefineSolver2(GesylvRefineSolver):

    cdef void _compute_workspace(self):
        ldwork = pymepack_def.mepack_memory_frontend(
            'dla_gesylv2_refine'.encode(), 'N'.encode(), 'N'.encode(),
            self.A.val().shape[0], self.B.val().shape[0])
        if ldwork < 0:
            raise Exception('memory allocation failed with code ' + str(ldwork))
        self.ldwork = ldwork

    cdef void _execute_mepack_solver(self):
        if self.precision == cnp.NPY_DOUBLE:
            pymepack_def.mepack_double_gesylv2_refine(self.TRANS_A.encode(), self.TRANS_B.encode(),
                              self.guess.encode(), self.sgn.dval()[0],
                              self.A.dval().shape[0], self.B.dval().shape[0],
                              &self.A.dval()[0,0], self.A.dval().shape[0],
                              &self.B.dval()[0,0], self.B.dval().shape[0],
                              &self.X.dval()[0,0], self.X.dval().shape[0],
                              &self.Y.dval()[0,0], self.Y.dval().shape[0],
                              &self.AS.dval()[0,0],self.AS.dval().shape[0],
                              &self.BS.dval()[0,0],self.BS.dval().shape[0],
                              &self.Q.dval()[0,0], self.Q.dval().shape[0],
                              &self.R.dval()[0,0], self.R.dval().shape[0],
                              &self.max_it[0], &self.tau.dval()[0],
                              &self.convlog.dval()[0],
                              &self.work.dval()[0], self.ldwork,
                              &self.info[0])
        elif self.precision == cnp.NPY_FLOAT:
            pymepack_def.mepack_single_gesylv2_refine(self.TRANS_A.encode(), self.TRANS_B.encode(),
                              self.guess.encode(), self.sgn.fval()[0],
                              self.A.fval().shape[0], self.B.fval().shape[0],
                              &self.A.fval()[0,0], self.A.fval().shape[0],
                              &self.B.fval()[0,0], self.B.fval().shape[0],
                              &self.X.fval()[0,0], self.X.fval().shape[0],
                              &self.Y.fval()[0,0], self.Y.fval().shape[0],
                              &self.AS.fval()[0,0],self.AS.fval().shape[0],
                              &self.BS.fval()[0,0],self.BS.fval().shape[0],
                              &self.Q.fval()[0,0], self.Q.fval().shape[0],
                              &self.R.fval()[0,0], self.R.fval().shape[0],
                              &self.max_it[0], &self.tau.fval()[0],
                              &self.convlog.fval()[0],
                              &self.work.fval()[0], self.ldwork,
                              &self.info[0])


cdef class GGSylvSolver(MepackSolverTemplate):
    cdef void _validate_params(self):
        params = self.input_params
        A,B,C,D,X,QA,ZA,QB,ZB = (params['A'],params['B'],params['C'],
                               params['D'], params['X'],
                               params['QA'],params['ZA'],
                               params['QB'],params['ZB'])
        hess_AC,hess_BD = (params['hess_AC'],params['hess_BD'])
        if(A.shape != C.shape):
            raise ValueError('A and C must have same shape')
        if(B.shape != D.shape):
            raise ValueError('B and D must have same shape')
        if (X.shape[0] != A.shape[0] or
            X.shape[1] != B.shape[0]   ):
            err_msg = 'X has dimensions incompatible with (A,C) and (B,D)'
            raise ValueError(err_msg)
        if ( not all(v is not None for v in [QA, ZA]) and
             not all(v is None for v in [QA, ZA])         ):
            err_msg = 'both matrices QA and ZA should be provided or skipped'
            raise ValueError(err_msg)
        if ( not all(v is not None for v in [QB, ZB]) and
             not all(v is None for v in [QB, ZB])         ):
            err_msg = 'both matrices QB and ZB should be provided or skipped'
            raise ValueError(err_msg)
        if hess_AC and QA is not None:
            err_msg='(A,C) is given as Schur factorization while hess_AC=True'
            raise ValueError(err_msg)
        if hess_BD and QB is not None:
            err_msg='(B,D) is given as Schur factorization while hess_DB=True'
            raise ValueError(err_msg)

    cdef void _create_execution_params(self):
        params = self.input_params
        A,B,C,D,X,QA,ZA,QB,ZB = (params['A'],params['B'],params['C'],
                                   params['D'],params['X'],
                                   params['QA'],params['ZA'],
                                   params['QB'],params['ZB'])
        hess_AC,hess_BD,inplace = (params['hess_AC'],params['hess_BD'],
                                   params['inplace'])

        if QA is None:
            if hess_AC:
                self.FACTA = 'H'
            else:
                self.FACTA = 'N'
            self.QA = FusedMatrix(np.zeros_like(A, order='F'))
            self.ZA = FusedMatrix(np.zeros_like(A, order='F'))
        else:
            self.FACTA = 'F'
            self.QA = FusedMatrix(QA)
            self.ZA = FusedMatrix(ZA)

        if QB is None:
            if hess_BD:
                self.FACTB = 'H'
            else:
                self.FACTB = 'N'
            self.QB = FusedMatrix(np.zeros_like(B, order='F'))
            self.ZB = FusedMatrix(np.zeros_like(B, order='F'))
        else:
            self.FACTB = 'F'
            self.QB = FusedMatrix(QB)
            self.ZB = FusedMatrix(ZB)

        self.A = FusedMatrix(A if inplace else A.copy(order='F'))
        self.B = FusedMatrix(B if inplace else B.copy(order='F'))
        self.C = FusedMatrix(C if inplace else C.copy(order='F'))
        self.D = FusedMatrix(D if inplace else D.copy(order='F'))
        self.X = FusedMatrix(X if inplace else X.copy(order='F'))

        self.TRANS_A = 'T' if params['trans_A'] else 'N'
        self.TRANS_B = 'T' if params['trans_B'] else 'N'
        self.sgn.val()[0] = params['sgn']

    cdef void _compute_workspace(self):
        ldwork = pymepack_def.mepack_memory_frontend(
            'dla_ggsylv'.encode(), self.FACTA.encode(), self.FACTB.encode(),
            self.A.val().shape[0], self.B.val().shape[0])
        if ldwork < 0:
            raise Exception('memory allocation failed with code ' + str(ldwork))
        self.ldwork = ldwork

    cdef void _execute_mepack_solver(self):
        if self.precision == cnp.NPY_DOUBLE:
            pymepack_def.mepack_double_ggsylv(self.FACTA.encode(),
                              self.FACTB.encode(),
                              self.TRANS_A.encode(), self.TRANS_B.encode(),
                              self.sgn.dval()[0],
                              self.A.dval().shape[0], self.B.dval().shape[0],
                              &self.A.dval()[0,0], self.A.dval().shape[0],
                              &self.B.dval()[0,0], self.B.dval().shape[0],
                              &self.C.dval()[0,0], self.C.dval().shape[0],
                              &self.D.dval()[0,0], self.D.dval().shape[0],
                              &self.QA.dval()[0,0],self.QA.dval().shape[0],
                              &self.ZA.dval()[0,0],self.ZA.dval().shape[0],
                              &self.QB.dval()[0,0], self.QB.dval().shape[0],
                              &self.ZB.dval()[0,0], self.ZB.dval().shape[0],
                              &self.X.dval()[0,0], self.X.dval().shape[0],
                              &self.scale.dval()[0],
                              &self.work.dval()[0], self.ldwork,
                              &self.info[0])
        elif self.precision == cnp.NPY_FLOAT:
            pymepack_def.mepack_single_ggsylv(self.FACTA.encode(),
                              self.FACTB.encode(),
                              self.TRANS_A.encode(), self.TRANS_B.encode(),
                              self.sgn.fval()[0],
                              self.A.fval().shape[0], self.B.fval().shape[0],
                              &self.A.fval()[0,0], self.A.fval().shape[0],
                              &self.B.fval()[0,0], self.B.fval().shape[0],
                              &self.C.fval()[0,0], self.C.fval().shape[0],
                              &self.D.fval()[0,0], self.D.fval().shape[0],
                              &self.QA.fval()[0,0],self.QA.fval().shape[0],
                              &self.ZA.fval()[0,0],self.ZA.fval().shape[0],
                              &self.QB.fval()[0,0], self.QB.fval().shape[0],
                              &self.ZB.fval()[0,0], self.ZB.fval().shape[0],
                              &self.X.fval()[0,0], self.X.fval().shape[0],
                              &self.scale.fval()[0],
                              &self.work.fval()[0], self.ldwork,
                              &self.info[0])

    def _get_execution_results(self):
        return (np.asarray(self.X.val()),
                np.asarray(self.A.val()), np.asarray(self.C.val()),
                np.asarray(self.QA.val()),np.asarray(self.ZA.val()),
                np.asarray(self.B.val()), np.asarray(self.D.val()),
                np.asarray(self.QB.val()),np.asarray(self.ZB.val()))

cdef class GGSylvRefineSolver(MepackSolverTemplate):

    cdef void _validate_params_common(self):
        params = self.input_params
        A,B,C,D,AS,BS,CS,DS,Q,Z,U,V = (params['A'],params['B'],params['C'],
                               params['D'], params['AS'],params['BS'],
                               params['CS'],params['DS'],
                               params['Q'],params['Z'],params['U'],params['V'])
        if(A.shape != C.shape):
            raise ValueError('A and C must have same shape')
        if(B.shape != D.shape):
            raise ValueError('B and D must have same shape')
        if ( not all(v is not None for v in [AS, CS, Q, Z]) and
             not all(v is None for v in [AS, CS, Q, Z])         ):
            err = "complete generalized Schur decomposition of (A,C) "
            msg = "should be given or skipped"
            raise ValueError(err + msg)
        if ( not all(v is not None for v in [BS, DS, U, V]) and
             not all(v is None for v in [BS, DS, U, V])         ):
            err = "complete generalized Schur decomposition of (B,D) "
            msg = "should be given or skipped"
            raise ValueError(err + msg)

    cdef void _validate_params(self):
        params = self.input_params
        X,A,B =  (params['X'],params['A'],params['B'])
        if (X is not None and
                ( X.shape[0] != A.shape[0] or
                  X.shape[1] != B.shape[0]   )):
            err_msg = 'X has dimensions incompatible with (A,C) and (B,D)'
            raise ValueError(err_msg)
        self._validate_params_common()

    cdef void _create_execution_params_common(self):
        params = self.input_params
        A,B,C,D,AS,BS,CS,DS,Q,Z,U,V = (params['A'],params['B'],params['C'],
                             params['D'],params['AS'],
                             params['BS'],params['CS'],params['DS'],
                             params['Q'],params['Z'],params['U'],params['V'])

        self.A = FusedMatrix(A.astype(A.dtype, order='F', copy=False))
        self.B = FusedMatrix(B.astype(B.dtype, order='F', copy=False))
        self.C = FusedMatrix(C.astype(C.dtype, order='F', copy=False))
        self.D = FusedMatrix(D.astype(D.dtype, order='F', copy=False))

        if AS is None:
            qz = linalg.qz(A,C)[0:4]
            self.AS = FusedMatrix(qz[0].copy(order='F'))
            self.CS = FusedMatrix(qz[1].copy(order='F'))
            self.Q  = FusedMatrix(qz[2].copy(order='F'))
            self.Z  = FusedMatrix(qz[3].copy(order='F'))
        else:
            self.AS = FusedMatrix(AS.astype(AS.dtype, order='F', copy=False))
            self.CS = FusedMatrix(CS.astype(CS.dtype, order='F', copy=False))
            self.Q  = FusedMatrix(Q.astype(Q.dtype, order='F', copy=False))
            self.Z  = FusedMatrix(Z.astype(Z.dtype, order='F', copy=False))

        if BS is None:
            qz = linalg.qz(B,D)[0:4]
            self.BS = FusedMatrix(qz[0].copy(order='F'))
            self.DS = FusedMatrix(qz[1].copy(order='F'))
            self.U  = FusedMatrix(qz[2].copy(order='F'))
            self.V  = FusedMatrix(qz[3].copy(order='F'))
        else:
            self.BS = FusedMatrix(BS.astype(BS.dtype, order='F', copy=False))
            self.DS = FusedMatrix(DS.astype(DS.dtype, order='F', copy=False))
            self.U  = FusedMatrix(U.astype(U.dtype, order='F', copy=False))
            self.V  = FusedMatrix(V.astype(V.dtype, order='F', copy=False))

        self.TRANS_A = 'T' if params['trans_A'] else 'N'
        self.TRANS_B = 'T' if params['trans_B'] else 'N'
        self.max_it[0] = params['max_it']
        self.tau.val()[0] = params['tau']
        self._set_convlog()

    cdef void _create_execution_params(self):
        params = self.input_params
        self.Y = FusedMatrix(params['Y'])
        X,A,B = (params['X'],params['A'],params['B'])
        if X is None:
            self.X = FusedMatrix(np.zeros((A.shape[0], B.shape[0]), dtype=A.dtype, order='F'))
            self.guess = 'N'
        else:
            self.X = FusedMatrix(X.copy(order='F'))
            self.guess = 'I'
        self.sgn.val()[0] = params['sgn']
        self._create_execution_params_common()

    cdef void _compute_workspace(self):
        ldwork = pymepack_def.mepack_memory_frontend(
            'dla_ggsylv_refine'.encode(), 'F'.encode(), 'F'.encode(),
            self.A.val().shape[0], self.B.val().shape[0])
        if ldwork < 0:
            raise Exception('memory allocation failed with code ' + str(ldwork))
        self.ldwork = ldwork

    cdef void _execute_mepack_solver(self):
        if self.precision == cnp.NPY_DOUBLE:
            pymepack_def.mepack_double_ggsylv_refine(self.TRANS_A.encode(), self.TRANS_B.encode(),
                              self.guess.encode(), self.sgn.dval()[0],
                              self.A.dval().shape[0], self.B.dval().shape[0],
                              &self.A.dval()[0,0], self.A.dval().shape[0],
                              &self.B.dval()[0,0], self.B.dval().shape[0],
                              &self.C.dval()[0,0], self.C.dval().shape[0],
                              &self.D.dval()[0,0], self.D.dval().shape[0],
                              &self.X.dval()[0,0], self.X.dval().shape[0],
                              &self.Y.dval()[0,0], self.Y.dval().shape[0],
                              &self.AS.dval()[0,0],self.AS.dval().shape[0],
                              &self.BS.dval()[0,0],self.BS.dval().shape[0],
                              &self.CS.dval()[0,0],self.CS.dval().shape[0],
                              &self.DS.dval()[0,0],self.DS.dval().shape[0],
                              &self.Q.dval()[0,0], self.Q.dval().shape[0],
                              &self.Z.dval()[0,0], self.Z.dval().shape[0],
                              &self.U.dval()[0,0], self.U.dval().shape[0],
                              &self.V.dval()[0,0], self.V.dval().shape[0],
                              &self.max_it[0], &self.tau.dval()[0],
                              &self.convlog.dval()[0],
                              &self.work.dval()[0], self.ldwork,
                              &self.info[0])
        elif self.precision == cnp.NPY_FLOAT:
            pymepack_def.mepack_single_ggsylv_refine(self.TRANS_A.encode(), self.TRANS_B.encode(),
                              self.guess.encode(), self.sgn.fval()[0],
                              self.A.fval().shape[0], self.B.fval().shape[0],
                              &self.A.fval()[0,0], self.A.fval().shape[0],
                              &self.B.fval()[0,0], self.B.fval().shape[0],
                              &self.C.fval()[0,0], self.C.fval().shape[0],
                              &self.D.fval()[0,0], self.D.fval().shape[0],
                              &self.X.fval()[0,0], self.X.fval().shape[0],
                              &self.Y.fval()[0,0], self.Y.fval().shape[0],
                              &self.AS.fval()[0,0],self.AS.fval().shape[0],
                              &self.BS.fval()[0,0],self.BS.fval().shape[0],
                              &self.CS.fval()[0,0],self.CS.fval().shape[0],
                              &self.DS.fval()[0,0],self.DS.fval().shape[0],
                              &self.Q.fval()[0,0], self.Q.fval().shape[0],
                              &self.Z.fval()[0,0], self.Z.fval().shape[0],
                              &self.U.fval()[0,0], self.U.fval().shape[0],
                              &self.V.fval()[0,0], self.V.fval().shape[0],
                              &self.max_it[0], &self.tau.fval()[0],
                              &self.convlog.fval()[0],
                              &self.work.fval()[0], self.ldwork,
                              &self.info[0])

    def _get_execution_results(self):
        return (np.asarray(self.X.val()), self.max_it[0],
                self.tau.val()[0], np.asarray(self.convlog.val()))

cdef class GGCSylvRefineSolver(GGSylvRefineSolver):
    cdef void _validate_params(self):
        params = self.input_params
        E,F,R,L,A,B = (params['E'],params['F'],params['R'], params['L'],
                       params['A'],params['B'])
        if ( E.shape[0] != A.shape[0] or
                  E.shape[1] != B.shape[0] ):
            err_msg = 'E has dimensions incompatible with (A,C) and (B,D)'
            raise ValueError(err_msg)
        if (E.shape != F.shape):
            raise ValueError('E and F must have same shape')
        if ( not all(v is not None for v in [R,L]) and
             not all(v is None for v in [R,L])         ):
            err_msg = 'both R and L should be given or skipped'
            raise ValueError(err_msg)
        self._validate_params_common()

    cdef void _create_execution_params(self):
        params = self.input_params
        self.E, self.F = (FusedMatrix(params['E']), FusedMatrix(params['F']))
        R,L,A,B = (params['R'],params['L'],params['A'],params['B'])
        if R is None:
            self.R = FusedMatrix(np.zeros((A.shape[0], B.shape[0]), dtype = A.dtype, order='F'))
            self.L = FusedMatrix(np.zeros((A.shape[0], B.shape[0]), dtype = A.dtype, order='F'))
            self.guess = 'N'
        else:
            self.R = FusedMatrix(R.copy(order='F'))
            self.L = FusedMatrix(L.copy(order='F'))
            self.guess = 'I'
        self.sgn.val()[0] = params['sgn1']
        self.sgn2.val()[0] = params['sgn2']
        self._create_execution_params_common()

    cdef void _compute_workspace(self):
        ldwork = pymepack_def.mepack_memory_frontend(
            'dla_ggcsylv_refine'.encode(), 'F'.encode(), 'F'.encode(),
            self.A.val().shape[0], self.B.val().shape[0])
        if ldwork < 0:
            raise Exception('memory allocation failed with code ' + str(ldwork))
        self.ldwork = ldwork

    cdef void _execute_mepack_solver(self):
        if self.precision == cnp.NPY_DOUBLE:
            pymepack_def.mepack_double_ggcsylv_refine(self.TRANS_A.encode(), self.TRANS_B.encode(),
                              self.guess.encode(), self.sgn.dval()[0], self.sgn2.dval()[0],
                              self.A.dval().shape[0], self.B.dval().shape[0],
                              &self.A.dval()[0,0], self.A.dval().shape[0],
                              &self.B.dval()[0,0], self.B.dval().shape[0],
                              &self.C.dval()[0,0], self.C.dval().shape[0],
                              &self.D.dval()[0,0], self.D.dval().shape[0],
                              &self.R.dval()[0,0], self.R.dval().shape[0],
                              &self.L.dval()[0,0], self.L.dval().shape[0],
                              &self.E.dval()[0,0], self.E.dval().shape[0],
                              &self.F.dval()[0,0], self.F.dval().shape[0],
                              &self.AS.dval()[0,0],self.AS.dval().shape[0],
                              &self.BS.dval()[0,0],self.BS.dval().shape[0],
                              &self.CS.dval()[0,0],self.CS.dval().shape[0],
                              &self.DS.dval()[0,0],self.DS.dval().shape[0],
                              &self.Q.dval()[0,0], self.Q.dval().shape[0],
                              &self.Z.dval()[0,0], self.Z.dval().shape[0],
                              &self.U.dval()[0,0], self.U.dval().shape[0],
                              &self.V.dval()[0,0], self.V.dval().shape[0],
                              &self.max_it[0], &self.tau.dval()[0],
                              &self.convlog.dval()[0],
                              &self.work.dval()[0], self.ldwork,
                              &self.info[0])
        elif self.precision == cnp.NPY_FLOAT:
            pymepack_def.mepack_single_ggcsylv_refine(self.TRANS_A.encode(), self.TRANS_B.encode(),
                              self.guess.encode(), self.sgn.fval()[0], self.sgn2.fval()[0],
                              self.A.fval().shape[0], self.B.fval().shape[0],
                              &self.A.fval()[0,0], self.A.fval().shape[0],
                              &self.B.fval()[0,0], self.B.fval().shape[0],
                              &self.C.fval()[0,0], self.C.fval().shape[0],
                              &self.D.fval()[0,0], self.D.fval().shape[0],
                              &self.R.fval()[0,0], self.R.fval().shape[0],
                              &self.L.fval()[0,0], self.L.fval().shape[0],
                              &self.E.fval()[0,0], self.E.fval().shape[0],
                              &self.F.fval()[0,0], self.F.fval().shape[0],
                              &self.AS.fval()[0,0],self.AS.fval().shape[0],
                              &self.BS.fval()[0,0],self.BS.fval().shape[0],
                              &self.CS.fval()[0,0],self.CS.fval().shape[0],
                              &self.DS.fval()[0,0],self.DS.fval().shape[0],
                              &self.Q.fval()[0,0], self.Q.fval().shape[0],
                              &self.Z.fval()[0,0], self.Z.fval().shape[0],
                              &self.U.fval()[0,0], self.U.fval().shape[0],
                              &self.V.fval()[0,0], self.V.fval().shape[0],
                              &self.max_it[0], &self.tau.fval()[0],
                              &self.convlog.fval()[0],
                              &self.work.fval()[0], self.ldwork,
                              &self.info[0])

    def _get_execution_results(self):
        return (np.asarray(self.R.val()), np.asarray(self.L.val()), self.max_it[0],
                self.tau.val()[0], np.asarray(self.convlog.val()))


cdef class GGCSylvSolver(MepackSolverTemplate):
    cdef void _validate_params(self):
        params = self.input_params
        A,B,C,D,E,F,QA,ZA,QB,ZB = (params['A'],params['B'],params['C'],
                                   params['D'],params['E'],params['F'],
                                   params['QA'],params['ZA'],
                                   params['QB'],params['ZB'])
        hess_AC,hess_BD = (params['hess_AC'], params['hess_BD'])

        if(A.shape != C.shape):
            raise ValueError('A and C must have same shape')
        if(B.shape != D.shape):
            raise ValueError('B and D must have same shape')
        if (E.shape[0] != A.shape[0] or
            E.shape[1] != B.shape[0]   ):
            raise ValueError('E has dimensions incompatible with A and B')
        if (F.shape[0] != C.shape[0] or
            F.shape[1] != D.shape[0]   ):
            raise ValueError('F has dimensions incompatible with C and D')
        if ( not all(v is not None for v in [QA, ZA]) and
             not all(v is None for v in [QA, ZA])         ):
            err_msg = 'both matrices QA and ZA should be provided or skipped'
            raise ValueError(err_msg)
        if ( not all(v is not None for v in [QB, ZB]) and
             not all(v is None for v in [QB, ZB])         ):
            err_msg = 'both matrices QB and ZB should be provided or skipped'
            raise ValueError(err_msg)
        if hess_AC and QA is not None:
            err_msg='(A,C) is given as Schur factorization while hess_AC=True'
            raise ValueError(err_msg)
        if hess_BD and QB is not None:
            err_msg='(B,D) is given as Schur factorization while hess_DB=True'
            raise ValueError(err_msg)

    cdef void _create_execution_params(self):
        params = self.input_params
        A,B,C,D,E,F,QA,ZA,QB,ZB = (params['A'],params['B'],params['C'],
                                   params['D'],params['E'],params['F'],
                                   params['QA'],params['ZA'],
                                   params['QB'],params['ZB'])
        hess_AC,hess_BD,inplace = (params['hess_AC'],params['hess_BD'],
                                   params['inplace'])

        if QA is None:
            if hess_AC:
                self.FACTA = 'H'
            else:
                self.FACTA = 'N'
            self.QA = FusedMatrix(np.zeros_like(A, order='F'))
            self.ZA = FusedMatrix(np.zeros_like(A, order='F'))
        else:
            self.FACTA = 'F'
            self.QA = FusedMatrix(QA)
            self.ZA = FusedMatrix(ZA)

        if QB is None:
            if hess_BD:
                self.FACTB = 'H'
            else:
                self.FACTB = 'N'
            self.QB = FusedMatrix(np.zeros_like(B, order='F'))
            self.ZB = FusedMatrix(np.zeros_like(B, order='F'))
        else:
            self.FACTB = 'F'
            self.QB = FusedMatrix(QB)
            self.ZB = FusedMatrix(ZB)

        self.A = FusedMatrix(A if inplace else A.copy(order='F'))
        self.B = FusedMatrix(B if inplace else B.copy(order='F'))
        self.C = FusedMatrix(C if inplace else C.copy(order='F'))
        self.D = FusedMatrix(D if inplace else D.copy(order='F'))
        self.E = FusedMatrix(E if inplace else E.copy(order='F'))
        self.F = FusedMatrix(F if inplace else F.copy(order='F'))

        self.TRANS_A = 'T' if params['trans_A'] else 'N'
        self.TRANS_B = 'T' if params['trans_B'] else 'N'
        self.sgn.val()[0] = params['sgn1']
        self.sgn2.val()[0] = params['sgn2']

    cdef void _compute_workspace(self):
        ldwork = pymepack_def.mepack_memory_frontend(
            'dla_ggcsylv'.encode(), self.FACTA.encode(), self.FACTB.encode(),
            self.A.val().shape[0], self.B.val().shape[0])
        if ldwork < 0:
            raise Exception('memory allocation failed with code ' + str(ldwork))
        self.ldwork = ldwork

    cdef void _execute_mepack_solver(self):
        if self.precision == cnp.NPY_DOUBLE:
            pymepack_def.mepack_double_ggcsylv(self.FACTA.encode(),
                              self.FACTB.encode(),
                              self.TRANS_A.encode(), self.TRANS_B.encode(),
                              self.sgn.dval()[0], self.sgn2.dval()[0],
                              self.A.dval().shape[0], self.B.dval().shape[0],
                              &self.A.dval()[0,0], self.A.dval().shape[0],
                              &self.B.dval()[0,0], self.B.dval().shape[0],
                              &self.C.dval()[0,0], self.C.dval().shape[0],
                              &self.D.dval()[0,0], self.D.dval().shape[0],
                              &self.QA.dval()[0,0],self.QA.dval().shape[0],
                              &self.ZA.dval()[0,0],self.ZA.dval().shape[0],
                              &self.QB.dval()[0,0], self.QB.dval().shape[0],
                              &self.ZB.dval()[0,0], self.ZB.dval().shape[0],
                              &self.E.dval()[0,0], self.E.dval().shape[0],
                              &self.F.dval()[0,0], self.F.dval().shape[0],
                              &self.scale.dval()[0],
                              &self.work.dval()[0], self.ldwork,
                              &self.info[0])
        elif self.precision == cnp.NPY_FLOAT:
            pymepack_def.mepack_single_ggcsylv(self.FACTA.encode(),
                              self.FACTB.encode(),
                              self.TRANS_A.encode(), self.TRANS_B.encode(),
                              self.sgn.fval()[0], self.sgn2.fval()[0],
                              self.A.fval().shape[0], self.B.fval().shape[0],
                              &self.A.fval()[0,0], self.A.fval().shape[0],
                              &self.B.fval()[0,0], self.B.fval().shape[0],
                              &self.C.fval()[0,0], self.C.fval().shape[0],
                              &self.D.fval()[0,0], self.D.fval().shape[0],
                              &self.QA.fval()[0,0],self.QA.fval().shape[0],
                              &self.ZA.fval()[0,0],self.ZA.fval().shape[0],
                              &self.QB.fval()[0,0], self.QB.fval().shape[0],
                              &self.ZB.fval()[0,0], self.ZB.fval().shape[0],
                              &self.E.fval()[0,0], self.E.fval().shape[0],
                              &self.F.fval()[0,0], self.F.fval().shape[0],
                              &self.scale.fval()[0],
                              &self.work.fval()[0], self.ldwork,
                              &self.info[0])

    def _get_execution_results(self):
        return (np.asarray(self.E.val()), np.asarray(self.F.val()),
                np.asarray(self.A.val()), np.asarray(self.C.val()),
                np.asarray(self.QA.val()),np.asarray(self.ZA.val()),
                np.asarray(self.B.val()), np.asarray(self.D.val()),
                np.asarray(self.QB.val()),np.asarray(self.ZB.val()))

cdef class GGCSylvDualSolver(GGCSylvSolver):
    cdef void _compute_workspace(self):
        ldwork = pymepack_def.mepack_memory_frontend(
            'dla_ggcsylv_dual'.encode(), self.FACTA.encode(),self.FACTB.encode(),
            self.A.val().shape[0], self.B.val().shape[0])
        if ldwork < 0:
            raise Exception('memory allocation failed with code ' + str(ldwork))
        self.ldwork = ldwork

    cdef void _execute_mepack_solver(self):
        if self.precision == cnp.NPY_DOUBLE:
            pymepack_def.mepack_double_ggcsylv_dual(self.FACTA.encode(),
                              self.FACTB.encode(),
                              self.TRANS_A.encode(), self.TRANS_B.encode(),
                              self.sgn.dval()[0], self.sgn2.dval()[0],
                              self.A.dval().shape[0], self.B.dval().shape[0],
                              &self.A.dval()[0,0], self.A.dval().shape[0],
                              &self.B.dval()[0,0], self.B.dval().shape[0],
                              &self.C.dval()[0,0], self.C.dval().shape[0],
                              &self.D.dval()[0,0], self.D.dval().shape[0],
                              &self.QA.dval()[0,0],self.QA.dval().shape[0],
                              &self.ZA.dval()[0,0],self.ZA.dval().shape[0],
                              &self.QB.dval()[0,0], self.QB.dval().shape[0],
                              &self.ZB.dval()[0,0], self.ZB.dval().shape[0],
                              &self.E.dval()[0,0], self.E.dval().shape[0],
                              &self.F.dval()[0,0], self.F.dval().shape[0],
                              &self.scale.dval()[0],
                              &self.work.dval()[0], self.ldwork,
                              &self.info[0])
        elif self.precision == cnp.NPY_FLOAT:
            pymepack_def.mepack_single_ggcsylv_dual(self.FACTA.encode(),
                              self.FACTB.encode(),
                              self.TRANS_A.encode(), self.TRANS_B.encode(),
                              self.sgn.fval()[0], self.sgn2.fval()[0],
                              self.A.fval().shape[0], self.B.fval().shape[0],
                              &self.A.fval()[0,0], self.A.fval().shape[0],
                              &self.B.fval()[0,0], self.B.fval().shape[0],
                              &self.C.fval()[0,0], self.C.fval().shape[0],
                              &self.D.fval()[0,0], self.D.fval().shape[0],
                              &self.QA.fval()[0,0],self.QA.fval().shape[0],
                              &self.ZA.fval()[0,0],self.ZA.fval().shape[0],
                              &self.QB.fval()[0,0], self.QB.fval().shape[0],
                              &self.ZB.fval()[0,0], self.ZB.fval().shape[0],
                              &self.E.fval()[0,0], self.E.fval().shape[0],
                              &self.F.fval()[0,0], self.F.fval().shape[0],
                              &self.scale.fval()[0],
                              &self.work.fval()[0], self.ldwork,
                              &self.info[0])

cdef class GGCSylvDualRefineSolver(GGCSylvRefineSolver):
    cdef void _compute_workspace(self):
        ldwork = pymepack_def.mepack_memory_frontend(
            'dla_ggcsylv_dual_refine'.encode(), 'F'.encode(), 'F'.encode(),
            self.A.val().shape[0], self.B.val().shape[0])
        if ldwork < 0:
            raise Exception('memory allocation failed with code ' + str(ldwork))
        self.ldwork = ldwork

    cdef void _execute_mepack_solver(self):
        if self.precision == cnp.NPY_DOUBLE:
            pymepack_def.mepack_double_ggcsylv_dual_refine(self.TRANS_A.encode(),
                              self.TRANS_B.encode(),
                              self.guess.encode(), self.sgn.dval()[0], self.sgn2.dval()[0],
                              self.A.dval().shape[0], self.B.dval().shape[0],
                              &self.A.dval()[0,0], self.A.dval().shape[0],
                              &self.B.dval()[0,0], self.B.dval().shape[0],
                              &self.C.dval()[0,0], self.C.dval().shape[0],
                              &self.D.dval()[0,0], self.D.dval().shape[0],
                              &self.R.dval()[0,0], self.R.dval().shape[0],
                              &self.L.dval()[0,0], self.L.dval().shape[0],
                              &self.E.dval()[0,0], self.E.dval().shape[0],
                              &self.F.dval()[0,0], self.F.dval().shape[0],
                              &self.AS.dval()[0,0],self.AS.dval().shape[0],
                              &self.BS.dval()[0,0],self.BS.dval().shape[0],
                              &self.CS.dval()[0,0],self.CS.dval().shape[0],
                              &self.DS.dval()[0,0],self.DS.dval().shape[0],
                              &self.Q.dval()[0,0], self.Q.dval().shape[0],
                              &self.Z.dval()[0,0], self.Z.dval().shape[0],
                              &self.U.dval()[0,0], self.U.dval().shape[0],
                              &self.V.dval()[0,0], self.V.dval().shape[0],
                              &self.max_it[0], &self.tau.dval()[0],
                              &self.convlog.dval()[0],
                              &self.work.dval()[0], self.ldwork,
                              &self.info[0])
        elif self.precision == cnp.NPY_FLOAT:
            pymepack_def.mepack_single_ggcsylv_dual_refine(self.TRANS_A.encode(),
                              self.TRANS_B.encode(),
                              self.guess.encode(), self.sgn.fval()[0], self.sgn2.fval()[0],
                              self.A.fval().shape[0], self.B.fval().shape[0],
                              &self.A.fval()[0,0], self.A.fval().shape[0],
                              &self.B.fval()[0,0], self.B.fval().shape[0],
                              &self.C.fval()[0,0], self.C.fval().shape[0],
                              &self.D.fval()[0,0], self.D.fval().shape[0],
                              &self.R.fval()[0,0], self.R.fval().shape[0],
                              &self.L.fval()[0,0], self.L.fval().shape[0],
                              &self.E.fval()[0,0], self.E.fval().shape[0],
                              &self.F.fval()[0,0], self.F.fval().shape[0],
                              &self.AS.fval()[0,0],self.AS.fval().shape[0],
                              &self.BS.fval()[0,0],self.BS.fval().shape[0],
                              &self.CS.fval()[0,0],self.CS.fval().shape[0],
                              &self.DS.fval()[0,0],self.DS.fval().shape[0],
                              &self.Q.fval()[0,0], self.Q.fval().shape[0],
                              &self.Z.fval()[0,0], self.Z.fval().shape[0],
                              &self.U.fval()[0,0], self.U.fval().shape[0],
                              &self.V.fval()[0,0], self.V.fval().shape[0],
                              &self.max_it[0], &self.tau.fval()[0],
                              &self.convlog.fval()[0],
                              &self.work.fval()[0], self.ldwork,
                              &self.info[0])


