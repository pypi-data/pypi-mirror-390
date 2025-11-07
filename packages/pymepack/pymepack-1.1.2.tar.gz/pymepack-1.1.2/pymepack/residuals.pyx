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
import numpy as np
cimport numpy as cnp

def res_gelyap(
        cnp.ndarray[numeric_t, ndim=2] A not None,
        cnp.ndarray[numeric_t, ndim=2] X not None,
        cnp.ndarray[numeric_t, ndim=2] Y not None,
        trans = False, numeric_t scale = 1.0):
    """
    ``res_gelyap(A, X, Y[, trans = False, scale = 1.0])``

    *wrapper for mepack_(single|double)_residual_lyap.*

    Compute the relative residual for the Lyapunov equation
    ::

           A * X  +  X * A^T = Y               (1)
      or
           A^T * X  +  X * A = Y               (2)

    where A, the right hand side Y, and the solution X are (n,n) matrices.
    The relative residual is computed via
    ::

                  || SCALE*Y - op(A)*X - X * op(A)**T ||_F
         RelRes = -----------------------------------------          (3)
                   ( 2*||A||_F*||X||_F + SCALE * ||Y||_F )

    where op(A) reflects the transpose operator from Equation (1) or (2).


    :param trans: Specifies the form of an equation with respect to A:

            == False:  The residual of Equation (1) is computed.

            == True:   The residual of Equation (2) is computed.

            defaults to False
    :type trans: bool, optional
    :param A:
        The coefficient matrix A.
    :type A: (n,n) numpy array
    :param X:
        The solution of the Lyapunov Equation (1) or (2).
    :type X: (n,n) numpy array
    :param Y:
        The right hand side of the Lyapunov Equation (1) or (2).
    :type Y: (n,n) numpy array
    :param scale:
       Scaling factor of the equation.
       defaults to 1.0
    :type scale: double,optional
    :raise Exception:
        If the underlying mepack routine mepack_*_residual_lyap fails
        due to invalid input parameters or memory allocation.
    :return: RelRes
             The relative residual as given by Equation (3).

    .. HINT::
       |hintFortranLayout|
    """
    cdef char * TRANS_A
    if trans:
        TRANS_A = 'T'
    else:
        TRANS_A = 'N'

    if not A.flags.f_contiguous:
        A = np.asfortranarray(A)
    if not X.flags.f_contiguous:
        X = np.asfortranarray(X)
    if not Y.flags.f_contiguous:
        Y = np.asfortranarray(Y)

    if numeric_t is cnp.float32_t:
        relres = pymepack_def.mepack_single_residual_lyap(TRANS_A, A.shape[0],
                         &A[0,0], A.shape[0],
                         &X[0,0], X.shape[0],
                         &Y[0,0], Y.shape[0],
                         scale)

    elif numeric_t is cnp.float64_t:
        relres = pymepack_def.mepack_double_residual_lyap(TRANS_A, A.shape[0],
                         &A[0,0], A.shape[0],
                         &X[0,0], X.shape[0],
                         &Y[0,0], Y.shape[0],
                         scale)
    if relres < 0:
        raise Exception('mepack_(single|double)_residual_lyap failed with code ' + str(int(relres)))

    return relres

def res_gglyap(
        cnp.ndarray[numeric_t, ndim=2] A not None,
        cnp.ndarray[numeric_t, ndim=2] B not None,
        cnp.ndarray[numeric_t, ndim=2] X not None,
        cnp.ndarray[numeric_t, ndim=2] Y not None,
        trans = False, numeric_t scale = 1.0):
    """
    ``res_gglyap(A, B, X, Y[, trans = False, scale = 1.0])``

    *wrapper for mepack_(single|double)_residual_glyap.*

    Compute the relative residual for the generalized Lyapunov equation
    ::

           A * X * B^T +  B * X * A^T = Y               (1)
      or
           A^T * X * B +  B^T * X * A = Y               (2)

    where A, B, the right hand side Y, and the solution X are (n,n) matrices.
    The relative residual is computed via
    ::

                  || SCALE*Y - op(A)*X*op(B)**T - op(B)*X*op(A)**T ||_F
         RelRes = -----------------------------------------------------    (3)
                   ( 2*||A||_F*||B||_F*||X||_F + SCALE * ||Y||_F )

    where op(A) reflects the transpose operator from Equation (1) or (2).


    :param trans: Specifies the form of an equation with respect to A:

            == False:  The residual of Equation (1) is computed.

            == True:   The residual of Equation (2) is computed.

            defaults to False
    :type trans: bool, optional
    :param A:
        The coefficient matrix A.
    :type A: (n,n) numpy array
    :param B:
        The coefficient matrix B.
    :type B: (n,n) numpy array
    :param X:
        The solution of the Lyapunov Equation (1) or (2).
    :type X: (n,n) numpy array
    :param Y:
        The right hand side of the Lyapunov Equation (1) or (2).
    :type Y: (n,n) numpy array
    :param scale:
       Scaling factor of the equation.
       defaults to 1.0
    :type scale: double,optional
    :raise Exception:
        If the underlying mepack routine mepack_*_residual_glyap fails
        due to invalid input parameters or memory allocation.
    :return: RelRes
             The relative residual as given by Equation (3).

    .. HINT::
       |hintFortranLayout|
    """
    cdef char * TRANS_A
    if trans:
        TRANS_A = 'T'
    else:
        TRANS_A = 'N'

    if not A.flags.f_contiguous:
        A = np.asfortranarray(A)
    if not B.flags.f_contiguous:
        B = np.asfortranarray(B)
    if not X.flags.f_contiguous:
        X = np.asfortranarray(X)
    if not Y.flags.f_contiguous:
        Y = np.asfortranarray(Y)

    if numeric_t is cnp.float32_t:
        relres = pymepack_def.mepack_single_residual_glyap(TRANS_A, A.shape[0],
                         &A[0,0], A.shape[0],
                         &B[0,0], B.shape[0],
                         &X[0,0], X.shape[0],
                         &Y[0,0], Y.shape[0],
                         scale)

    elif numeric_t is cnp.float64_t:
        relres = pymepack_def.mepack_double_residual_glyap(TRANS_A, A.shape[0],
                         &A[0,0], A.shape[0],
                         &B[0,0], B.shape[0],
                         &X[0,0], X.shape[0],
                         &Y[0,0], Y.shape[0],
                         scale)
    if relres < 0:
        raise Exception('mepack_(single|double)_residual_glyap failed with code ' + str(int(relres)))

    return relres

def res_gestein(
        cnp.ndarray[numeric_t, ndim=2] A not None,
        cnp.ndarray[numeric_t, ndim=2] X not None,
        cnp.ndarray[numeric_t, ndim=2] Y not None,
        trans = False, numeric_t scale = 1.0):
    """
    ``res_gestein(A, X, Y[, trans = False, scale = 1.0])``

    *wrapper for mepack_(single|double)_residual_stein.*

    Compute the relative residual for the Stein equation
    ::

           A * X * A^T - X = Y               (1)
      or
           A^T * X * A - X = Y               (2)

    where A, the right hand side Y, and the solution X are (n,n) matrices.
    The relative residual is computed via
    ::

                       || SCALE*Y - op(A)*X*op(A)**T + X ||_F
         RelRes = -----------------------------------------------    (3)
                   ( (||A||_F**2 + 1)||X||_F + SCALE * ||Y||_F )

    where op(A) reflects the transpose operator from Equation (1) or (2).


    :param trans: Specifies the form of an equation with respect to A:

            == False:  The residual of Equation (1) is computed.

            == True:   The residual of Equation (2) is computed.

            defaults to False
    :type trans: bool, optional
    :param A:
        The coefficient matrix A.
    :type A: (n,n) numpy array
    :param X:
        The solution of the Stein Equation (1) or (2).
    :type X: (n,n) numpy array
    :param Y:
        The right hand side of the Stein Equation (1) or (2).
    :type Y: (n,n) numpy array
    :param scale:
       Scaling factor of the equation.
       defaults to 1.0
    :type scale: double,optional
    :raise Exception:
        If the underlying mepack routine mepack_*_residual_stein fails
        due to invalid input parameters or memory allocation.
    :return: RelRes
             The relative residual as given by Equation (3).

    .. HINT::
       |hintFortranLayout|

    """
    cdef char * TRANS_A
    if trans:
        TRANS_A = 'T'
    else:
        TRANS_A = 'N'

    if not A.flags.f_contiguous:
        A = np.asfortranarray(A)
    if not X.flags.f_contiguous:
        X = np.asfortranarray(X)
    if not Y.flags.f_contiguous:
        Y = np.asfortranarray(Y)

    if numeric_t is cnp.float32_t:
        relres = pymepack_def.mepack_single_residual_stein(TRANS_A, A.shape[0],
                         &A[0,0], A.shape[0],
                         &X[0,0], X.shape[0],
                         &Y[0,0], Y.shape[0],
                         scale)

    elif numeric_t is cnp.float64_t:
        relres = pymepack_def.mepack_double_residual_stein(TRANS_A, A.shape[0],
                         &A[0,0], A.shape[0],
                         &X[0,0], X.shape[0],
                         &Y[0,0], Y.shape[0],
                         scale)
    if relres < 0:
        raise Exception('mepack_(single|double)_residual_stein failed with code ' + str(int(relres)))

    return relres

def res_ggstein(
        cnp.ndarray[numeric_t, ndim=2] A not None,
        cnp.ndarray[numeric_t, ndim=2] B not None,
        cnp.ndarray[numeric_t, ndim=2] X not None,
        cnp.ndarray[numeric_t, ndim=2] Y not None,
        trans = False, numeric_t scale = 1.0):
    """
    ``res_ggstein(A, B, X, Y[, trans = False, scale = 1.0])``

    *wrapper for mepack_(single|double)_residual_gstein.*

    Compute the relative residual for the generalized Stein equation
    ::

           A * X * A^T -  B * X * B^T = Y               (1)
      or
           A^T * X * A -  B^T * X * B = Y               (2)

    where A, B, the right hand side Y, and the solution X are (n,n) matrices.
    The relative residual is computed via
    ::

                    || SCALE*Y - op(A)*X*op(A)**T + op(B)*X*op(B)**T ||_F
         RelRes = ---------------------------------------------------------    (3)
                   ( (||A||_F**2 + ||B||_F**2)*||X||_F + SCALE * ||Y||_F )

    where op(A) reflects the transpose operator from Equation (1) or (2).


    :param trans: Specifies the form of an equation with respect to A:

            == False:  The residual of Equation (1) is computed.

            == True:   The residual of Equation (2) is computed.

            defaults to False
    :type trans: bool, optional
    :param A:
        The coefficient matrix A.
    :type A: (n,n) numpy array
    :param B:
        The coefficient matrix B.
    :type B: (n,n) numpy array
    :param X:
        The solution of the Stein Equation (1) or (2).
    :type X: (n,n) numpy array
    :param Y:
        The right hand side of the Stein Equation (1) or (2).
    :type Y: (n,n) numpy array
    :param scale:
       Scaling factor of the equation.
       defaults to 1.0
    :type scale: double,optional
    :raise Exception:
        If the underlying mepack routine mepack_*_residual_gstein fails
        due to invalid input parameters or memory allocation.
    :return: RelRes
             The relative residual as given by Equation (3).

    .. HINT::
       |hintFortranLayout|
    """
    cdef char * TRANS_A
    if trans:
        TRANS_A = 'T'
    else:
        TRANS_A = 'N'

    if not A.flags.f_contiguous:
        A = np.asfortranarray(A)
    if not B.flags.f_contiguous:
        B = np.asfortranarray(B)
    if not X.flags.f_contiguous:
        X = np.asfortranarray(X)
    if not Y.flags.f_contiguous:
        Y = np.asfortranarray(Y)

    if numeric_t is cnp.float32_t:
        relres = pymepack_def.mepack_single_residual_gstein(TRANS_A, A.shape[0],
                         &A[0,0], A.shape[0],
                         &B[0,0], B.shape[0],
                         &X[0,0], X.shape[0],
                         &Y[0,0], Y.shape[0],
                         scale)

    elif numeric_t is cnp.float64_t:
        relres = pymepack_def.mepack_double_residual_gstein(TRANS_A, A.shape[0],
                         &A[0,0], A.shape[0],
                         &B[0,0], B.shape[0],
                         &X[0,0], X.shape[0],
                         &Y[0,0], Y.shape[0],
                         scale)
    if relres < 0:
        raise Exception('mepack_(single|double)_residual_gstein failed with code ' + str(int(relres)))

    return relres

def res_gesylv(
        cnp.ndarray[numeric_t, ndim=2] A not None,
        cnp.ndarray[numeric_t, ndim=2] B not None,
        cnp.ndarray[numeric_t, ndim=2] X not None,
        cnp.ndarray[numeric_t, ndim=2] Y not None,
        transa = False, transb = False, numeric_t sign = 1.0, numeric_t scale = 1.0):
    """
    ``res_gesylv(A, B, X, Y[, transa = False, transb = False, sign = 1.0, scale = 1.0])``

    *wrapper for mepack_(single|double)_residual_sylv.*

    Compute the relative residual for the Sylvester equation
    ::

           opA(A) * X  +  sign * X * opB(B) = Y               (1)

    where A is an (m,m) matrix, B is an (n,n) matrix, and
    the solution X and the right hand side Y are (m,n) matrices.
    The relative residual is computed via
    ::

                   || SCALE*Y - opA(A)*X - sign* X * opB(B) ||_F
      RelRes = ------------------------...........-----------------   (2)
                ((||A||_F + ||B||_F) * ||X||_F + SCALE * ||Y||_F )


    :param transa: Specifies the form of an equation with respect to A:

            == False:  opA(A) = A.

            == True:   opA(A) = A^T

            defaults to False
    :type transa: bool, optional

    :param transb: Specifies the form of an equation with respect to B:

            == False:  opB(B) = B.

            == True:   opB(B) = B^T

            defaults to False
    :type transb: bool, optional

    :param sign: Specifies the sign between the two parts of the Equation (1)
        Allowed values are 1.0 and -1.0.

        defaults to 1.0
    :type sign: scalar value (1.0, -1.0), optional

    :param A:
        The coefficient matrix A.
    :type A: (m,m) numpy array

    :param B:
        The coefficient matrix B.
    :type B: (n,n) numpy array

    :param X:
        The solution of the Sylvester Equation (1).
    :type X: (m,n) numpy array

    :param Y:
        The right hand side of the Sylvester Equation (1).
    :type Y: (m,n) numpy array

    :param scale:
       Scaling factor of the equation.
       defaults to 1.0
    :type scale: double,optional

    :raise Exception:
        If the underlying mepack routine mepack_*_residual_sylv fails
        due to invalid input parameters or memory allocation.
    :return: RelRes
             The relative residual as given by Equation (2).

    .. HINT::
       |hintFortranLayout|
    """
    cdef char * TRANS_A
    cdef char * TRANS_B

    if transa:
        TRANS_A = 'T'
    else:
        TRANS_A = 'N'
    if transb:
        TRANS_B = 'T'
    else:
        TRANS_B = 'N'

    if not A.flags.f_contiguous:
        A = np.asfortranarray(A)
    if not B.flags.f_contiguous:
        B = np.asfortranarray(B)
    if not X.flags.f_contiguous:
        X = np.asfortranarray(X)
    if not Y.flags.f_contiguous:
        Y = np.asfortranarray(Y)

    if numeric_t is cnp.float32_t:
        relres = pymepack_def.mepack_single_residual_sylv(TRANS_A, TRANS_B, sign, A.shape[0], B.shape[0],
                         &A[0,0], A.shape[0],
                         &B[0,0], B.shape[0],
                         &X[0,0], X.shape[0],
                         &Y[0,0], Y.shape[0],
                         scale)

    elif numeric_t is cnp.float64_t:
        relres = pymepack_def.mepack_double_residual_sylv(TRANS_A, TRANS_B, sign, A.shape[0], B.shape[0],
                         &A[0,0], A.shape[0],
                         &B[0,0], B.shape[0],
                         &X[0,0], X.shape[0],
                         &Y[0,0], Y.shape[0],
                         scale)
    if relres < 0:
        raise Exception('mepack_(single|double)_residual_sylv failed with code ' + str(int(relres)))

    return relres


def res_gesylv2(
        cnp.ndarray[numeric_t, ndim=2] A not None,
        cnp.ndarray[numeric_t, ndim=2] B not None,
        cnp.ndarray[numeric_t, ndim=2] X not None,
        cnp.ndarray[numeric_t, ndim=2] Y not None,
        transa = False, transb = False, numeric_t sign = 1.0, numeric_t scale = 1.0):
    """
    ``res_gesylv2(A, B, X, Y[, transa = False, transb = False, sign = 1.0, scale = 1.0])``

    *wrapper for mepack_(single|double)_residual_sylv2.*

    Compute the relative residual for the discrete-time Sylvester equation
    ::

           opA(A) * X * opB(B) +  sign * X  = Y               (1)

    where A is an (m,m) matrix, B is an (n,n) matrix, and
    the solution X and the right hand side Y are (m,n) matrices.
    The relative residual is computed via
    ::

                  || SCALE*Y - opA(A)*X*opB(B) - sign * X ||_F
      RelRes = ------------------------...........-----------------   (2)
                ((||A||_F *||B||_F + 1) * ||X||_F + SCALE * ||Y||_F )


    :param transa: Specifies the form of an equation with respect to A:

            == False:  opA(A) = A.

            == True:   opA(A) = A^T

            defaults to False
    :type transa: bool, optional

    :param transb: Specifies the form of an equation with respect to B:

            == False:  opB(B) = B.

            == True:   opB(B) = B^T

            defaults to False
    :type transb: bool, optional

    :param sign: Specifies the sign between the two parts of the Equation (1)
        Allowed values are 1.0 and -1.0.

        defaults to 1.0
    :type sign: scalar value (1.0, -1.0), optional

    :param A:
        The coefficient matrix A.
    :type A: (m,m) numpy array

    :param B:
        The coefficient matrix B.
    :type B: (n,n) numpy array

    :param X:
        The solution of the Sylvester Equation (1).
    :type X: (m,n) numpy array

    :param Y:
        The right hand side of the Sylvester Equation (1).
    :type Y: (m,n) numpy array

    :param scale:
       Scaling factor of the equation.
       defaults to 1.0
    :type scale: double,optional

    :raise Exception:
        If the underlying mepack routine mepack_*_residual_sylv2 fails
        due to invalid input parameters or memory allocation.
    :return: RelRes
             The relative residual as given by Equation (2).

    .. HINT::
       |hintFortranLayout|
    """
    cdef char * TRANS_A
    cdef char * TRANS_B

    if transa:
        TRANS_A = 'T'
    else:
        TRANS_A = 'N'
    if transb:
        TRANS_B = 'T'
    else:
        TRANS_B = 'N'

    if not A.flags.f_contiguous:
        A = np.asfortranarray(A)
    if not B.flags.f_contiguous:
        B = np.asfortranarray(B)
    if not X.flags.f_contiguous:
        X = np.asfortranarray(X)
    if not Y.flags.f_contiguous:
        Y = np.asfortranarray(Y)

    if numeric_t is cnp.float32_t:
        relres = pymepack_def.mepack_single_residual_sylv2(TRANS_A, TRANS_B, sign, A.shape[0], B.shape[0],
                         &A[0,0], A.shape[0],
                         &B[0,0], B.shape[0],
                         &X[0,0], X.shape[0],
                         &Y[0,0], Y.shape[0],
                         scale)

    elif numeric_t is cnp.float64_t:
        relres = pymepack_def.mepack_double_residual_sylv2(TRANS_A, TRANS_B, sign, A.shape[0], B.shape[0],
                         &A[0,0], A.shape[0],
                         &B[0,0], B.shape[0],
                         &X[0,0], X.shape[0],
                         &Y[0,0], Y.shape[0],
                         scale)
    if relres < 0:
        raise Exception('mepack_(single|double)_residual_sylv2 failed with code ' + str(int(relres)))

    return relres


def res_ggsylv(
        cnp.ndarray[numeric_t, ndim=2] A not None,
        cnp.ndarray[numeric_t, ndim=2] B not None,
        cnp.ndarray[numeric_t, ndim=2] C not None,
        cnp.ndarray[numeric_t, ndim=2] D not None,
        cnp.ndarray[numeric_t, ndim=2] X not None,
        cnp.ndarray[numeric_t, ndim=2] Y not None,
        transa = False, transb = False, numeric_t sign = 1.0, numeric_t scale = 1.0):
    """
    ``res_ggsylv(A, B, C, D, X, Y[, transa = False, transb = False, sign = 1.0, scale = 1.0])``

    *wrapper for mepack_(single|double)_residual_gsylv.*

    Compute the relative residual for the generalized Sylvester equation
    ::

           opA(A) * X * opB(B) + sign * opA(C) * X * opB(D) = Y               (1)

    where A and C are (m,m) matrices, B and D are (n,n) matrices, and
    the solution X and the right hand side Y are (m,n) matrices.
    The relative residual is computed via
    ::

               || SCALE*Y - opA(A)*X*opB(B) - sign*opA(C) X * opB(D) ||_F
      RelRes = ------------------------...........--------------------------------   (2)
                ((||A||_F ||B||_F + ||C||_F||D||_F) * ||X||_F + SCALE * ||Y||_F )


    :param transa: Specifies the form of an equation with respect to A:

            == False:  opA(A) = A.

            == True:   opA(A) = A^T

            defaults to False
    :type transa: bool, optional

    :param transb: Specifies the form of an equation with respect to B:

            == False:  opB(B) = B.

            == True:   opB(B) = B^T

            defaults to False
    :type transb: bool, optional

    :param sign: Specifies the sign between the two parts of the Equation (1)
        Allowed values are 1.0 and -1.0.

        defaults to 1.0
    :type sign: scalar value (1.0, -1.0), optional

    :param A:
        The coefficient matrix A.
    :type A: (m,m) numpy array

    :param B:
        The coefficient matrix B.
    :type B: (n,n) numpy array

    :param C:
        The coefficient matrix C.
    :type C: (m,m) numpy array

    :param D:
        The coefficient matrix D.
    :type D: (n,n) numpy array

    :param X:
        The solution of the generalized Sylvester Equation (1).
    :type X: (m,n) numpy array

    :param Y:
        The right hand side of the generalized Sylvester Equation (1).
    :type Y: (m,n) numpy array

    :param scale:
       Scaling factor of the equation.
       defaults to 1.0
    :type scale: double,optional

    :raise Exception:
        If the underlying mepack routine mepack_*_residual_gsylv fails
        due to invalid input parameters or memory allocation.
    :return: RelRes
             The relative residual as given by Equation (2).

    .. HINT::
       |hintFortranLayout|
    """
    cdef char * TRANS_A
    cdef char * TRANS_B

    if transa:
        TRANS_A = 'T'
    else:
        TRANS_A = 'N'
    if transb:
        TRANS_B = 'T'
    else:
        TRANS_B = 'N'

    if not A.flags.f_contiguous:
        A = np.asfortranarray(A)
    if not B.flags.f_contiguous:
        B = np.asfortranarray(B)
    if not C.flags.f_contiguous:
        C = np.asfortranarray(C)
    if not D.flags.f_contiguous:
        D = np.asfortranarray(D)
    if not X.flags.f_contiguous:
        X = np.asfortranarray(X)
    if not Y.flags.f_contiguous:
        Y = np.asfortranarray(Y)

    if numeric_t is cnp.float32_t:
        relres = pymepack_def.mepack_single_residual_gsylv(TRANS_A, TRANS_B, sign, A.shape[0], B.shape[0],
                         &A[0,0], A.shape[0],
                         &B[0,0], B.shape[0],
                         &C[0,0], C.shape[0],
                         &D[0,0], D.shape[0],
                         &X[0,0], X.shape[0],
                         &Y[0,0], Y.shape[0],
                         scale)

    elif numeric_t is cnp.float64_t:
        relres = pymepack_def.mepack_double_residual_gsylv(TRANS_A, TRANS_B, sign, A.shape[0], B.shape[0],
                         &A[0,0], A.shape[0],
                         &B[0,0], B.shape[0],
                         &C[0,0], C.shape[0],
                         &D[0,0], D.shape[0],
                         &X[0,0], X.shape[0],
                         &Y[0,0], Y.shape[0],
                         scale)
    if relres < 0:
        raise Exception('mepack_(single|double)_residual_gsylv failed with code ' + str(int(relres)))

    return relres

def res_ggcsylv(
        cnp.ndarray[numeric_t, ndim=2] A not None,
        cnp.ndarray[numeric_t, ndim=2] B not None,
        cnp.ndarray[numeric_t, ndim=2] C not None,
        cnp.ndarray[numeric_t, ndim=2] D not None,
        cnp.ndarray[numeric_t, ndim=2] R not None,
        cnp.ndarray[numeric_t, ndim=2] L not None,
        cnp.ndarray[numeric_t, ndim=2] E not None,
        cnp.ndarray[numeric_t, ndim=2] F not None,
        transa = False, transb = False, numeric_t sign1 = 1.0, numeric_t sign2 = 1.0,
        numeric_t scale = 1.0):
    """
    ``res_ggcsylv(A, B, C, D, R, L, E, F[, transa = False, transb = False, sign1 = 1.0, sign2 = 1.0, scale = 1.0])``

    *wrapper for mepack_(single|double)_residual_csylv.*

    Compute the relative residual for the generalized coupled Sylvester equation
    ::

        opA(A) * R + sign1 * L * opB(B) = SCALE * E
                                                     (1)
        opA(C) * R + sign2 * L * opB(D) = SCALE * F


    where A and C are (m,m) matrices, B and D are (n,n) matrices, and
    the solutions R, L  and the right hand sides E, F are (m,n) matrices.
    The relative residual is computed via
    ::

                              || SCALE*E - opA(A)*R - SGN1*L*opB(B) ||_F
        RelRes = max( ------------------------------------------------------ ,
                        ((||A||_F*||R||_F+||B||_F*||L||-F) + SCALE*||E||_F)
                                                                                (2)
                              || SCALE*F - opA(C)*R - SGN2*L*opB(D) ||_F
                      ------------------------------------------------------ )
                        ((||C||_F*||R||_F+||D||_F*||L||_F) + SCALE*||F||_F)

    :param transa: Specifies the form of an equation with respect to A:

            == False:  opA(A) = A.

            == True:   opA(A) = A^T

            defaults to False
    :type transa: bool, optional

    :param transb: Specifies the form of an equation with respect to B:

            == False:  opB(B) = B.

            == True:   opB(B) = B^T

            defaults to False
    :type transb: bool, optional

    :param sign1: Specifies sign1 in the Equation (1)
        Allowed values are 1.0 and -1.0.

        defaults to 1.0
    :type sign1: scalar value (1.0, -1.0), optional

    :param sign2: Specifies sign1 in the Equation (1)
        Allowed values are 1.0 and -1.0.

        defaults to 1.0
    :type sign2: scalar value (1.0, -1.0), optional

    :param A:
        The coefficient matrix A.
    :type A: (m,m) numpy array

    :param B:
        The coefficient matrix B.
    :type B: (n,n) numpy array

    :param C:
        The coefficient matrix C.
    :type C: (m,m) numpy array

    :param D:
        The coefficient matrix D.
    :type D: (n,n) numpy array

    :param R:
        The first part of the  solution of the generalized coupled
        Sylvester Equation (1).
    :type R: (m,n) numpy array

    :param L:
        The second part of the  solution of the generalized coupled
        Sylvester Equation (1).
    :type L: (m,n) numpy array

    :param E:
        The right hand side of the first part of the generalized
        coupled Sylvester Equation (1).
    :type E: (m,n) numpy array

    :param F:
        The right hand side of the second part of the generalized
        coupled Sylvester Equation (1).
    :type F: (m,n) numpy array


    :param scale:
       Scaling factor of the equation.
       defaults to 1.0
    :type scale: double,optional

    :raise Exception:
        If the underlying mepack routine mepack_*_residual_csylv fails
        due to invalid input parameters or memory allocation.
    :return: RelRes
             The relative residual as given by Equation (2).

    .. HINT::
       |hintFortranLayout|
    """
    cdef char * TRANS_A
    cdef char * TRANS_B

    if transa:
        TRANS_A = 'T'
    else:
        TRANS_A = 'N'
    if transb:
        TRANS_B = 'T'
    else:
        TRANS_B = 'N'

    if not A.flags.f_contiguous:
        A = np.asfortranarray(A)
    if not B.flags.f_contiguous:
        B = np.asfortranarray(B)
    if not C.flags.f_contiguous:
        C = np.asfortranarray(C)
    if not D.flags.f_contiguous:
        D = np.asfortranarray(D)
    if not E.flags.f_contiguous:
        E = np.asfortranarray(E)
    if not F.flags.f_contiguous:
        F = np.asfortranarray(F)
    if not R.flags.f_contiguous:
        R = np.asfortranarray(R)
    if not L.flags.f_contiguous:
        L = np.asfortranarray(L)

    if numeric_t is cnp.float32_t:
        relres = pymepack_def.mepack_single_residual_csylv(TRANS_A, TRANS_B, sign1, sign2, A.shape[0], B.shape[0],
                         &A[0,0], A.shape[0],
                         &B[0,0], B.shape[0],
                         &C[0,0], C.shape[0],
                         &D[0,0], D.shape[0],
                         &R[0,0], R.shape[0],
                         &L[0,0], L.shape[0],
                         &E[0,0], E.shape[0],
                         &F[0,0], F.shape[0],
                         scale)

    elif numeric_t is cnp.float64_t:
        relres = pymepack_def.mepack_double_residual_csylv(TRANS_A, TRANS_B, sign1, sign2, A.shape[0], B.shape[0],
                         &A[0,0], A.shape[0],
                         &B[0,0], B.shape[0],
                         &C[0,0], C.shape[0],
                         &D[0,0], D.shape[0],
                         &R[0,0], R.shape[0],
                         &L[0,0], L.shape[0],
                         &E[0,0], E.shape[0],
                         &F[0,0], F.shape[0],
                         scale)
    if relres < 0:
        raise Exception('mepack_(single|double)_residual_csylv failed with code ' + str(int(relres)))

    return relres


def res_ggcsylv_dual(
        cnp.ndarray[numeric_t, ndim=2] A not None,
        cnp.ndarray[numeric_t, ndim=2] B not None,
        cnp.ndarray[numeric_t, ndim=2] C not None,
        cnp.ndarray[numeric_t, ndim=2] D not None,
        cnp.ndarray[numeric_t, ndim=2] R not None,
        cnp.ndarray[numeric_t, ndim=2] L not None,
        cnp.ndarray[numeric_t, ndim=2] E not None,
        cnp.ndarray[numeric_t, ndim=2] F not None,
        transa = False, transb = False, numeric_t sign1 = 1.0, numeric_t sign2 = 1.0,
        numeric_t scale = 1.0):
    """
    ``res_ggcsylv_dual(A, B, C, D, R, L, E, F[, transa = False, transb = False, sign1 = 1.0, sign2 = 1.0, scale = 1.0])``

    *wrapper for mepack_(single|double)_residual_csylv.*

    Compute the relative residual for the generalized coupled Sylvester equation
    ::

        op1(A)^T * R + op1(C)^T * L                 =  E
                                                             (1)
        sign1 * R * op2(B)^T + sign2 * L * op2(D)^T =  F

    where A and C are (m,m) matrices, B and D are (n,n) matrices, and
    the solutions R, L and the right hand sides E, F are (m,n) matrices.
    The relative residual is computed via
    ::

                         || SCALE*E - opA(A)**T *R - opA(C) ** T *L ||_F
        RelRes = max( ------------------------------------------------------- ,
                       ((||A||_F*||R||_F+||C||_F*||L||_F) + SCALE * ||E||_F)
                                                                                              (2)
                         || SCALE*F - SIGN1 * R  * opB(B)**T - SIGN2 * L * opB(D) **T ||_F
                      ----------------------------------------------------------------------
                         ((||B||_F*||R||_F+||D||_F*||L||_F) + SCALE * ||F||_F))

    :param transa: Specifies the form of an equation with respect to A:

            == False:  opA(A) = A.

            == True:   opA(A) = A^T

            defaults to False
    :type transa: bool, optional

    :param transb: Specifies the form of an equation with respect to B:

            == False:  opB(B) = B.

            == True:   opB(B) = B^T

            defaults to False
    :type transb: bool, optional

    :param sign1: Specifies sign1 in the Equation (1)
        Allowed values are 1.0 and -1.0.

        defaults to 1.0
    :type sign1: scalar value (1.0, -1.0), optional

    :param sign2: Specifies sign1 in the Equation (1)
        Allowed values are 1.0 and -1.0.

        defaults to 1.0
    :type sign2: scalar value (1.0, -1.0), optional

    :param A:
        The coefficient matrix A.
    :type A: (m,m) numpy array

    :param B:
        The coefficient matrix B.
    :type B: (n,n) numpy array

    :param C:
        The coefficient matrix C.
    :type C: (m,m) numpy array

    :param D:
        The coefficient matrix D.
    :type D: (n,n) numpy array

    :param R:
        The first part of the  solution of the generalized coupled
        Sylvester Equation (1).
    :type R: (m,n) numpy array

    :param L:
        The second part of the  solution of the generalized coupled
        Sylvester Equation (1).
    :type L: (m,n) numpy array

    :param E:
        The right hand side of the first part of the generalized
        coupled Sylvester Equation (1).
    :type E: (m,n) numpy array

    :param F:
        The right hand side of the second part of the generalized
        coupled Sylvester Equation (1).
    :type F: (m,n) numpy array


    :param scale:
       Scaling factor of the equation.
       defaults to 1.0
    :type scale: double,optional

    :raise Exception:
        If the underlying mepack routine mepack_*_residual_csylv_dual fails
        due to invalid input parameters or memory allocation.
    :return: RelRes
             The relative residual as given by Equation (2).

    .. HINT::
       |hintFortranLayout|
    """
    cdef char * TRANS_A
    cdef char * TRANS_B

    if transa:
        TRANS_A = 'T'
    else:
        TRANS_A = 'N'
    if transb:
        TRANS_B = 'T'
    else:
        TRANS_B = 'N'

    if not A.flags.f_contiguous:
        A = np.asfortranarray(A)
    if not B.flags.f_contiguous:
        B = np.asfortranarray(B)
    if not C.flags.f_contiguous:
        C = np.asfortranarray(C)
    if not D.flags.f_contiguous:
        D = np.asfortranarray(D)
    if not E.flags.f_contiguous:
        E = np.asfortranarray(E)
    if not F.flags.f_contiguous:
        F = np.asfortranarray(F)
    if not R.flags.f_contiguous:
        R = np.asfortranarray(R)
    if not L.flags.f_contiguous:
        L = np.asfortranarray(L)

    if numeric_t is cnp.float32_t:
        relres = pymepack_def.mepack_single_residual_csylv_dual(TRANS_A, TRANS_B, sign1, sign2, A.shape[0], B.shape[0],
                         &A[0,0], A.shape[0],
                         &B[0,0], B.shape[0],
                         &C[0,0], C.shape[0],
                         &D[0,0], D.shape[0],
                         &R[0,0], R.shape[0],
                         &L[0,0], L.shape[0],
                         &E[0,0], E.shape[0],
                         &F[0,0], F.shape[0],
                         scale)

    elif numeric_t is cnp.float64_t:
        relres = pymepack_def.mepack_double_residual_csylv_dual(TRANS_A, TRANS_B, sign1, sign2, A.shape[0], B.shape[0],
                         &A[0,0], A.shape[0],
                         &B[0,0], B.shape[0],
                         &C[0,0], C.shape[0],
                         &D[0,0], D.shape[0],
                         &R[0,0], R.shape[0],
                         &L[0,0], L.shape[0],
                         &E[0,0], E.shape[0],
                         &F[0,0], F.shape[0],
                         scale)
    if relres < 0:
        raise Exception('mepack_(single|double)_residual_csylv_dual failed with code ' + str(int(relres)))

    return relres


