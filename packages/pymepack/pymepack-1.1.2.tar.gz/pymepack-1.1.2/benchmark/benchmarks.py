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

import sys
from pymepack import tests
import numpy as np
import timeit
import pymepack
import h5py as hp
from scipy import linalg

#solvers supporting upper Hessenberg form
support_hess = ["gelyap","gestein","gesylv","gesylv2"]

MIN_BENCH_TIME_SECS = 5
WRONG_SHAPE_ARG_ERR_MSG = """Wrong shape argument!\n Accepted values are:\n
'G' for general matrix;\n
'H' for upper Hessenberg matrix;\n
'F' for factorized matrix.\n"""

gelyap_setup = {
    "display_order":["gelyap_s1", "gelyap_s2", "gelyap_s3"],
    "gelyap_s1":{
        "display_name": "gelyap(solver=1)",
        "stmt": "pymepack.gelyap(a,x,q,hess=AHESS,block_size=bs)",
        "setup": "X.refresh(); A.refresh(); Q.refresh();"
                 "a = A.get_data();x = X.get_data();"
                 "q = Q.get_data() if FACT == 'F' else None"
    },
    "gelyap_s2":{
        "display_name": "gelyap(solver=2)",
        "stmt": "pymepack.gelyap(a,x,q,hess=AHESS,solver=2,block_size=bs)",
        "setup": "X.refresh(); A.refresh(); Q.refresh();"
        "a = A.get_data(); x = X.get_data();"
        "q = Q.get_data() if FACT == 'F' else None"
    },
    "gelyap_s3":{
        "display_name": "gelyap(solver=3)",
        "stmt": "pymepack.gelyap(a,x,q,hess=AHESS,solver=3,block_size=bs)",
        "setup": "X.refresh(); A.refresh(); Q.refresh();"
                 "a = A.get_data(); x = X.get_data();"
                 "q = Q.get_data() if FACT == 'F' else None"
    }
}

gestein_setup = {
    "display_order":["gestein_s1", "gestein_s2", "gestein_s3"],
    "gestein_s1":{
        "display_name": "gestein(solver=1)",
        "stmt": "pymepack.gestein(a,x,q,hess=AHESS,block_size=bs)",
        "setup": "X.refresh(); A.refresh(); a = A.get_data();x = X.get_data();"
                 "q = Q.refresh().get_data() if FACT == 'F' else None"
    },
    "gestein_s2":{
        "display_name": "gestein(solver=2)",
        "stmt": "pymepack.gestein(a,x,q,hess=AHESS,solver=2,block_size=bs)",
        "setup": "X.refresh(); A.refresh(); a = A.get_data();x = X.get_data();"
                 "q = Q.refresh().get_data() if FACT == 'F' else None"
    },
    "gestein_s3":{
        "display_name": "gestein(solver=3)",
        "stmt": "pymepack.gestein(a,x,q,hess=AHESS,solver=3,block_size=bs)",
        "setup": "X.refresh(); A.refresh(); a = A.get_data();x = X.get_data();"
                 "q = Q.refresh().get_data() if FACT == 'F' else None"
    }
}

gglyap_setup = {
    "display_order":["gglyap_s1", "gglyap_s2", "gglyap_s3"],
    "gglyap_s1":{
        "display_name": "gglyap(solver=1)",
        "stmt": "pymepack.gglyap(a,b,x,q,z,block_size=bs)",
        "setup": "X.refresh();A.refresh();B.refresh();Q.refresh();Z.refresh();"
                 "a = A.get_data(); b = B.get_data(); x = X.get_data();"
                 "q = Q.get_data() if FACT == 'F' else None;"
                 "z = Z.get_data() if FACT == 'F' else None"
    },
    "gglyap_s2":{
        "display_name": "gglyap(solver=2)",
        "stmt": "pymepack.gglyap(a,b,x,q,z,solver=2,block_size=bs)",
        "setup": "X.refresh();A.refresh();B.refresh();Q.refresh();Z.refresh();"
                 "a = A.get_data(); b = B.get_data(); x = X.get_data();"
                 "q = Q.get_data() if FACT == 'F' else None;"
                 "z = Z.get_data() if FACT == 'F' else None"

    },
    "gglyap_s3":{
        "display_name": "gglyap(solver=3)",
        "stmt": "pymepack.gglyap(a,b,x,q,z,solver=3,block_size=bs)",
        "setup": "X.refresh();A.refresh();B.refresh();Q.refresh();Z.refresh();"
                 "a = A.get_data(); b = B.get_data(); x = X.get_data();"
                 "q = Q.get_data() if FACT == 'F' else None;"
                 "z = Z.get_data() if FACT == 'F' else None"
    }
}

ggstein_setup = {
    "display_order":["ggstein_s1", "ggstein_s2", "ggstein_s3"],
    "ggstein_s1":{
        "display_name": "ggstein(solver=1)",
        "stmt": "pymepack.ggstein(a,b,x,q,z,block_size=bs)",
        "setup": "X.refresh(); A.refresh(); B.refresh();"
                 "a = A.get_data(); b = B.get_data(); x = X.get_data();"
                 "q = Q.refresh().get_data() if FACT == 'F' else None;"
                 "z = Z.refresh().get_data() if FACT == 'F' else None"
    },
    "ggstein_s2":{
        "display_name": "ggstein(solver=2)",
        "stmt": "pymepack.ggstein(a,b,x,q,z,solver=2,block_size=bs)",
        "setup": "X.refresh(); A.refresh(); B.refresh();"
                 "a = A.get_data(); b = B.get_data(); x = X.get_data();"
                 "q = Q.refresh().get_data() if FACT == 'F' else None;"
                 "z = Z.refresh().get_data() if FACT == 'F' else None"
    },
    "ggstein_s3":{
        "display_name": "ggstein(solver=3)",
        "stmt": "pymepack.ggstein(a,b,x,q,z,solver=3,block_size=bs)",
        "setup": "X.refresh(); A.refresh(); B.refresh();"
                 "a = A.get_data(); b = B.get_data(); x = X.get_data();"
                 "q = Q.refresh().get_data() if FACT == 'F' else None;"
                 "z = Z.refresh().get_data() if FACT == 'F' else None"
    }
}

gesylv_setup = {
    "display_order":["gesylv_s1", "gesylv_s2", "gesylv_s3"],
    "gesylv_s1":{
        "display_name": "gesylv(solver=1)",
        "stmt": "pymepack.gesylv(a,b,x,qa,qb,"
                "hess_A=AHESS,hess_B=BHESS,block_size=(bs,bs))",
        "setup": "X.refresh(); A.refresh(); B.refresh();"
                 "QA.refresh(); QB.refresh();"
                 "a = A.get_data();b = B.get_data();x = X.get_data();"
                 "qa = QA.get_data() if FACT == 'F' else None;"
                 "qb = QB.get_data() if FACT == 'F' else None"
    },
    "gesylv_s2":{
        "display_name": "gesylv(solver=2)",
        "stmt": "pymepack.gesylv(a,b,x,qa,qb,"
                "hess_A=AHESS,hess_B=BHESS,solver=2,block_size=(bs,bs))",
        "setup": "X.refresh(); A.refresh(); B.refresh();"
                 "QA.refresh(); QB.refresh();"
                 "a = A.get_data();b = B.get_data();x = X.get_data();"
                "qa = QA.get_data() if FACT == 'F' else None;"
                 "qb = QB.get_data() if FACT == 'F' else None"
    },
    "gesylv_s3":{
        "display_name": "gesylv(solver=3)",
        "stmt": "pymepack.gesylv(a,b,x,qa,qb,"
                "hess_A=AHESS,hess_B=BHESS,solver=3,block_size=(bs,bs))",
        "setup": "X.refresh(); A.refresh(); B.refresh();"
                 "QA.refresh(); QB.refresh();"
                 "a = A.get_data();b = B.get_data();x = X.get_data();"
                 "qa = QA.get_data() if FACT == 'F' else None;"
                 "qb = QB.get_data() if FACT == 'F' else None"
    }
}

gesylv2_setup = {
    "display_order":["gesylv2_s1", "gesylv2_s2", "gesylv2_s3"],
    "gesylv2_s1":{
        "display_name": "gesylv2(solver=1)",
        "stmt": "pymepack.gesylv2(a,b,x,qa,qb,"
                "hess_A=AHESS,hess_B=BHESS,block_size=(bs,bs))",
        "setup": "X.refresh(); A.refresh(); B.refresh();"
                 "QA.refresh(); QB.refresh();"
                 "a = A.get_data();b = B.get_data();x = X.get_data();"
                 "qa = QA.get_data() if FACT == 'F' else None;"
                 "qb = QB.get_data() if FACT == 'F' else None"
    },
    "gesylv2_s2":{
        "display_name": "gesylv2(solver=2)",
        "stmt": "pymepack.gesylv2(a,b,x,qa,qb,"
                "hess_A=AHESS,hess_B=BHESS,solver=2,block_size=(bs,bs))",
        "setup": "X.refresh(); A.refresh(); B.refresh();"
                 "QA.refresh(); QB.refresh();"
                 "a = A.get_data();b = B.get_data();x = X.get_data();"
                 "qa = QA.get_data() if FACT == 'F' else None;"
                 "qb = QB.get_data() if FACT == 'F' else None"
    },
    "gesylv2_s3":{
        "display_name": "gesylv2(solver=3)",
        "stmt": "pymepack.gesylv2(a,b,x,qa,qb,"
                "hess_A=AHESS,hess_B=BHESS,solver=3,block_size=(bs,bs))",
        "setup": "X.refresh(); A.refresh(); B.refresh();"
                 "QA.refresh(); QB.refresh();"
                 "a = A.get_data();b = B.get_data();x = X.get_data();"
                 "qa = QA.get_data() if FACT == 'F' else None;"
                 "qb = QB.get_data() if FACT == 'F' else None"
    }
}

ggsylv_setup = {
    "display_order": ["ggsylv_s1", "ggsylv_s2", "ggsylv_s3"],
    "ggsylv_s1":{
        "display_name": "ggsylv(solver=1)",
        "stmt": "pymepack.ggsylv(a,b,c,d,x,qa,za,qb,zb,block_size=(bs,bs))",
        "setup": "X.refresh();A.refresh();B.refresh();C.refresh();D.refresh();"
                 "QA.refresh();ZA.refresh();QB.refresh();ZB.refresh();"
                 "a = A.get_data();b = B.get_data();x = X.get_data();"
                 "c = C.get_data();d = D.get_data();"
                 "qa = QA.get_data() if FACT == 'F' else None;"
                 "za = ZA.get_data() if FACT == 'F' else None;"
                 "qb = QB.get_data() if FACT == 'F' else None;"
                 "zb = ZB.get_data() if FACT == 'F' else None"
    },
    "ggsylv_s2":{
        "display_name": "ggsylv(solver=2)",
        "stmt": "pymepack.ggsylv(a,b,c,d,x,qa,za,qb,zb,"
                                 "solver=2,block_size=(bs,bs))",
        "setup": "X.refresh();A.refresh();B.refresh();C.refresh();D.refresh();"
                 "QA.refresh();ZA.refresh();QB.refresh();ZB.refresh();"
                 "a = A.get_data();b = B.get_data();x = X.get_data();"
                 "c = C.get_data();d = D.get_data();"
                 "qa = QA.get_data() if FACT == 'F' else None;"
                 "za = ZA.get_data() if FACT == 'F' else None;"
                 "qb = QB.get_data() if FACT == 'F' else None;"
                 "zb = ZB.get_data() if FACT == 'F' else None"
    },
    "ggsylv_s3":{
        "display_name": "ggsylv(solver=3)",
        "stmt": "pymepack.ggsylv(a,b,c,d,x,qa,za,qb,zb,"
                                 "solver=3,block_size=(bs,bs))",
        "setup": "X.refresh();A.refresh();B.refresh();C.refresh();D.refresh();"
                 "QA.refresh();ZA.refresh();QB.refresh();ZB.refresh();"
                 "a = A.get_data();b = B.get_data();x = X.get_data();"
                 "c = C.get_data();d = D.get_data();"
                 "qa = QA.get_data() if FACT == 'F' else None;"
                 "za = ZA.get_data() if FACT == 'F' else None;"
                 "qb = QB.get_data() if FACT == 'F' else None;"
                 "zb = ZB.get_data() if FACT == 'F' else None"
    }
}

ggcsylv_setup = {
    "display_order": ["ggcsylv_s1", "ggcsylv_s2", "ggcsylv_s3"],
    "ggcsylv_s1":{
        "display_name": "ggcsylv(solver=1)",
        "stmt": "pymepack.ggcsylv(a,b,c,d,e,f,qa,za,qb,zb,block_size=(bs,bs))",
        "setup": "A.refresh();B.refresh();C.refresh();D.refresh();"
                 "E.refresh();F.refresh();"
                 "QA.refresh();ZA.refresh();QB.refresh();ZB.refresh();"
                 "a = A.get_data();b = B.get_data();"
                 "c = C.get_data();d = D.get_data();"
                 "e = E.get_data();f = F.get_data();"
                 "qa = QA.get_data() if FACT == 'F' else None;"
                 "za = ZA.get_data() if FACT == 'F' else None;"
                 "qb = QB.get_data() if FACT == 'F' else None;"
                 "zb = ZB.get_data() if FACT == 'F' else None"

    },
    "ggcsylv_s2":{
        "display_name": "ggcsylv(solver=2)",
        "stmt": "pymepack.ggcsylv(a,b,c,d,e,f,qa,za,qb,zb,"
                                     "solver=2,block_size=(bs,bs))",
        "setup": "A.refresh();B.refresh();C.refresh();D.refresh();"
                 "E.refresh();F.refresh();"
                 "QA.refresh();ZA.refresh();QB.refresh();ZB.refresh();"
                 "a = A.get_data();b = B.get_data();"
                 "c = C.get_data();d = D.get_data();"
                 "e = E.get_data();f = F.get_data();"
                 "qa = QA.get_data() if FACT == 'F' else None;"
                 "za = ZA.get_data() if FACT == 'F' else None;"
                 "qb = QB.get_data() if FACT == 'F' else None;"
                 "zb = ZB.get_data() if FACT == 'F' else None"
    },
    "ggcsylv_s3":{
        "display_name": "ggcsylv(solver=3)",
        "stmt": "pymepack.ggcsylv(a,b,c,d,e,f,qa,za,qb,zb,"
                                     "solver=3,block_size=(bs,bs))",
        "setup": "A.refresh();B.refresh();C.refresh();D.refresh();"
                 "E.refresh();F.refresh();"
                 "QA.refresh();ZA.refresh();QB.refresh();ZB.refresh();"
                 "a = A.get_data();b = B.get_data();"
                 "c = C.get_data();d = D.get_data();"
                 "e = E.get_data();f = F.get_data();"
                 "qa = QA.get_data() if FACT == 'F' else None;"
                 "za = ZA.get_data() if FACT == 'F' else None;"
                 "qb = QB.get_data() if FACT == 'F' else None;"
                 "zb = ZB.get_data() if FACT == 'F' else None"

    }
}

ggcsylv_dual_setup = {
    "display_order": ["ggcsylv_d_s1", "ggcsylv_d_s2", "ggcsylv_d_s3"],
    "ggcsylv_d_s1":{
        "display_name": "ggcsylv_dual(solver=1)",
        "stmt": "pymepack.ggcsylv_dual(a,b,c,d,e,f,qa,za,qb,zb,"
                                              "block_size=(bs,bs))",
        "setup": "A.refresh();B.refresh();C.refresh();D.refresh();"
                 "E.refresh();F.refresh();"
                 "QA.refresh();ZA.refresh();QB.refresh();ZB.refresh();"
                 "a = A.get_data();b = B.get_data();"
                 "c = C.get_data();d = D.get_data();"
                 "e = E.get_data();f = F.get_data();"
                 "qa = QA.get_data() if FACT == 'F' else None;"
                 "za = ZA.get_data() if FACT == 'F' else None;"
                 "qb = QB.get_data() if FACT == 'F' else None;"
                 "zb = ZB.get_data() if FACT == 'F' else None"
    },
    "ggcsylv_d_s2":{
        "display_name": "ggcsylv_dual(solver=2)",
        "stmt": "pymepack.ggcsylv_dual(a,b,c,d,e,f,qa,za,qb,zb,"
                                     "solver=2,block_size=(bs,bs))",
        "setup": "A.refresh();B.refresh();C.refresh();D.refresh();"
                 "E.refresh();F.refresh();"
                 "QA.refresh();ZA.refresh();QB.refresh();ZB.refresh();"
                 "a = A.get_data();b = B.get_data();"
                 "c = C.get_data();d = D.get_data();"
                 "e = E.get_data();f = F.get_data();"
                 "qa = QA.get_data() if FACT == 'F' else None;"
                 "za = ZA.get_data() if FACT == 'F' else None;"
                 "qb = QB.get_data() if FACT == 'F' else None;"
                 "zb = ZB.get_data() if FACT == 'F' else None"
    },
    "ggcsylv_d_s3":{
        "display_name": "ggcsylv_dual(solver=3)",
        "stmt": "pymepack.ggcsylv(a,b,c,d,e,f,qa,za,qb,zb,"
                                     "solver=3,block_size=(bs,bs))",
        "setup": "A.refresh();B.refresh();C.refresh();D.refresh();"
                 "E.refresh();F.refresh();"
                 "QA.refresh();ZA.refresh();QB.refresh();ZB.refresh();"
                 "a = A.get_data();b = B.get_data();"
                 "c = C.get_data();d = D.get_data();"
                 "e = E.get_data();f = F.get_data();"
                 "qa = QA.get_data() if FACT == 'F' else None;"
                 "za = ZA.get_data() if FACT == 'F' else None;"
                 "qb = QB.get_data() if FACT == 'F' else None;"
                 "zb = ZB.get_data() if FACT == 'F' else None"
    }
}

class Inplace_test_data:

    def set_data(self, data_source):
        self.__data = np.copy(data_source)
        self.__backup = np.copy(data_source)
        self.id = 1
        self.__data_refreshed = False
        return self


    def refresh(self):
        if self.id == 1:
            self.id = 2
            self.__data = np.copy(self.__backup)
        else:
            self.id = 1
            self.__backup = np.copy(self.__data)
        self.__data_refreshed = True
        return self

    def get_data(self):
        if not self.__data_refreshed:
            raise Exception(
                    "'refresh()' was not called" +
                    "before retrieving test data"
                    )
        self.__data_refreshed = False
        if self.id == 1:
            return np.asfortranarray(self.__data)
        else:
            return np.asfortranarray(self.__backup)

def read_ds_if_exists(h5_file, path, destinaiton, precision=np.double):
    if path in h5_file:
        dset = h5_file[path]
        array = np.ndarray(shape=dset.shape, dtype=np.double, order='C')
        dset.read_direct(array)
        destinaiton.set_data(array.astype(precision))

def ds_path(mx_name):
    return '/' + str(M) + '/' + mx_name

def read_test_data(path_to_test_data, precision=np.double):
    h5_file = hp.File(path_to_test_data,'r')

    A_inplace = Inplace_test_data()
    B_inplace = Inplace_test_data()
    C_inplace = Inplace_test_data()
    D_inplace = Inplace_test_data()
    E_inplace = Inplace_test_data()
    F_inplace = Inplace_test_data()
    Q_inplace = Inplace_test_data()
    Z_inplace = Inplace_test_data()
    X_inplace = Inplace_test_data()
    QA_inplace = Inplace_test_data()
    ZA_inplace = Inplace_test_data()
    QB_inplace = Inplace_test_data()
    ZB_inplace = Inplace_test_data()

    read_ds_if_exists(h5_file, ds_path('A'), A_inplace, precision)
    read_ds_if_exists(h5_file, ds_path('B'), B_inplace, precision)
    read_ds_if_exists(h5_file, ds_path('C'), C_inplace, precision)
    read_ds_if_exists(h5_file, ds_path('D'), D_inplace, precision)
    read_ds_if_exists(h5_file, ds_path('E'), E_inplace, precision)
    read_ds_if_exists(h5_file, ds_path('F'), F_inplace, precision)
    read_ds_if_exists(h5_file, ds_path('Q'), Q_inplace, precision)
    read_ds_if_exists(h5_file, ds_path('Z'), Z_inplace, precision)
    read_ds_if_exists(h5_file, ds_path('X'), X_inplace, precision)
    read_ds_if_exists(h5_file, ds_path('QA'), QA_inplace, precision)
    read_ds_if_exists(h5_file, ds_path('ZA'), ZA_inplace, precision)
    read_ds_if_exists(h5_file, ds_path('QB'), QB_inplace, precision)
    read_ds_if_exists(h5_file, ds_path('ZB'), ZB_inplace, precision)

    h5_file.close()

    globals()['A'] = A_inplace
    globals()['B'] = B_inplace
    globals()['C'] = C_inplace
    globals()['D'] = D_inplace
    globals()['E'] = E_inplace
    globals()['F'] = F_inplace
    globals()['Q'] = Q_inplace
    globals()['Z'] = Z_inplace
    globals()['X'] = X_inplace
    globals()['QA'] = QA_inplace
    globals()['ZA'] = ZA_inplace
    globals()['QB'] = QB_inplace
    globals()['ZB'] = ZB_inplace
    return


def init_test_data(solver, shape, precision=np.double):
    test_data_source = None
    A_inplace = Inplace_test_data()
    B_inplace = Inplace_test_data()
    C_inplace = Inplace_test_data()
    D_inplace = Inplace_test_data()
    E_inplace = Inplace_test_data()
    F_inplace = Inplace_test_data()
    Q_inplace = Inplace_test_data()
    Z_inplace = Inplace_test_data()
    X_inplace = Inplace_test_data()
    QA_inplace = Inplace_test_data()
    ZA_inplace = Inplace_test_data()
    QB_inplace = Inplace_test_data()
    ZB_inplace = Inplace_test_data()
    QA = None
    QB = None
    ZA = None
    ZB = None
    X = None

    if solver.lower() == "gelyap" or solver.lower() == "gestein":
        if solver.lower() == "gelyap":
            test_data_source = tests.GELYAP(4,1,M)
        else:
            test_data_source = tests.GESTEIN(4,1,M)
        test_data_source._set_params(1.000000001,1.000000001)
        (A,X,_) = test_data_source._call_collection_routine() #X array corresponds to Y in the equation
        A = A.astype(precision)
        X = X.astype(precision)
        if shape == "F":
            if precision == np.double:
                schur_dec = linalg.lapack.dgees(lambda: None, A)
            elif precision == np.single:
                schur_dec = linalg.lapack.sgees(lambda: None, A)
            A_inplace.set_data(schur_dec[0])
            Q_inplace.set_data(schur_dec[4])
        elif shape == "G":
            Q = np.zeros((M, M), dtype=precision)
            A_inplace.set_data(A)
            Q_inplace.set_data(Q)
        else:
            if precision == np.double:
                H = linalg.lapack.dgehrd(A)[0]
            elif precision == np.single:
                H = linalg.lapack.sgehrd(A)[0]
            H = np.triu(H, -1)
            A_inplace.set_data(H)
            Q = np.zeros((M, M), dtype=precision)
            Q_inplace.set_data(Q)
    elif solver.lower() == "gglyap" or solver.lower() == "ggstein":
        if solver.lower() == "gglyap":
            test_data_source = tests.GGLYAP(4,3,M)
        else:
            test_data_source = tests.GGSTEIN(4,3,M)
        test_data_source._set_params()
        (B,A,X,_) = test_data_source._call_collection_routine()
        B = B.astype(precision)
        A = A.astype(precision)
        X = X.astype(precision)
        if shape == "F":
            schur = linalg.qz(A, B)
            A_inplace.set_data(schur[0])
            B_inplace.set_data(schur[1])
            Q_inplace.set_data(schur[2])
            Z_inplace.set_data(schur[3])
        else:
            Q = np.zeros((M, M), dtype=precision)
            Z = np.zeros((M, M), dtype=precision)
            A_inplace.set_data(A)
            B_inplace.set_data(B)
            Q_inplace.set_data(Q)
            Z_inplace.set_data(Z)
    elif solver.lower() == "gesylv" or solver.lower() == "gesylv2":
        (A,B,X) = tests.TestStandardSylvesterSolver().get_data(N = M, precision=precision)
        if shape == "F":
            if precision == np.double:
                A_Schur = linalg.lapack.dgees(lambda: None, A)
                B_Schur = linalg.lapack.dgees(lambda: None, B)
            elif precision == np.single:
                A_Schur = linalg.lapack.sgees(lambda: None, A)
                B_Schur = linalg.lapack.sgees(lambda: None, B)
            A, QA = (A_Schur[0], A_Schur[4])
            B, QB = (B_Schur[0], B_Schur[4])
        elif shape == "H":
            if precision == np.double:
                A = np.triu(linalg.lapack.dgehrd(A)[0], -1)
                B = np.triu(linalg.lapack.dgehrd(A)[0], -1)
            elif precision == np.single:
                A = np.triu(linalg.lapack.sgehrd(A)[0], -1)
                B = np.triu(linalg.lapack.sgehrd(A)[0], -1)
        A_inplace.set_data(A)
        B_inplace.set_data(B)
    elif solver.lower() == "ggsylv":
        (A,B,C,D,X) = tests.TestGGSylvSolver().get_data(N = M, precision=precision)
        if shape == "F":
            A, C, QA, ZA = linalg.qz(A,C)[0:4]
            B, D, QB, ZB = linalg.qz(B,D)[0:4]
        A_inplace.set_data(A)
        B_inplace.set_data(B)
        C_inplace.set_data(C)
        D_inplace.set_data(D)
    elif solver.lower() == "ggcsylv" or solver.lower() == "ggcsylv_dual":
        (A,B,C,D,E,F) = tests.TestGGCSylvSolver().get_data(N = M, precision=precision)
        if shape == "F":
            A, C, QA, ZA = linalg.qz(A,C)[0:4]
            B, D, QB, ZB = linalg.qz(B,D)[0:4]
        A_inplace.set_data(A)
        B_inplace.set_data(B)
        C_inplace.set_data(C)
        D_inplace.set_data(D)
        E_inplace.set_data(E)
        F_inplace.set_data(F)
    X_inplace.set_data(X)
    QA_inplace.set_data(QA)
    ZA_inplace.set_data(ZA)
    QB_inplace.set_data(QB)
    ZB_inplace.set_data(ZB)
    globals()['A'] = A_inplace
    globals()['B'] = B_inplace
    globals()['C'] = C_inplace
    globals()['D'] = D_inplace
    globals()['E'] = E_inplace
    globals()['F'] = F_inplace
    globals()['Q'] = Q_inplace
    globals()['Z'] = Z_inplace
    globals()['X'] = X_inplace
    globals()['QA'] = QA_inplace
    globals()['ZA'] = ZA_inplace
    globals()['QB'] = QB_inplace
    globals()['ZB'] = ZB_inplace
    return

def resolve_benchmark_setup(solver):
    if solver.lower() == "gelyap":
        benchmark_setup = gelyap_setup
    elif solver.lower() == "gglyap":
        benchmark_setup = gglyap_setup
    elif solver.lower() == "gestein":
        benchmark_setup = gestein_setup
    elif solver.lower() == "ggstein":
        benchmark_setup = ggstein_setup
    elif solver.lower() == "gesylv":
       benchmark_setup = gesylv_setup
    elif solver.lower() == "gesylv2":
       benchmark_setup = gesylv2_setup
    elif solver.lower() == "ggsylv":
       benchmark_setup = ggsylv_setup
    elif solver.lower() == "ggcsylv":
       benchmark_setup = ggcsylv_setup
    elif solver.lower() == "ggcsylv_dual":
       benchmark_setup = ggcsylv_dual_setup
    else:
        raise ValueError('solver name is incorrect')
    return benchmark_setup

def block_size_bench(solver, shape='G', repeat=3, precision=np.double, path_to_test_data=None):

    benchmark_setup = resolve_benchmark_setup(solver)

    if shape not in ["G", "H", "F"]:
        raise ValueError(WRONG_SHAPE_ARG_ERR_MSG)

    if shape == "H" and solver.lower() not in support_hess:
        raise ValueError("No support for Hessenberg form for solver: "+solver)
    if precision not in [np.double,np.single]:
        raise ValueError("Selected precision is not supported")

    bound = "|".ljust(5)
    header = ["M".ljust(6) + bound]
    header.append("BS".ljust(6) + bound)

    for key in benchmark_setup['display_order']:
        if key == "slycot":
            continue
        header.append(benchmark_setup[key]["display_name"].ljust(17) + bound)
    header = ''.join(header)

    print(header)

    M_values = [500, 1000, 2000, 3000, 4000, 5000]
    block_sizes = [0,16, 32, 64, 96, 128]
    for M in M_values:
        globals()['M'] = M
        if path_to_test_data is not None:
            read_test_data(path_to_test_data,precision=precision)
        else:
            init_test_data(solver, shape, precision=precision)

        globals()['FACT'] = "F" if shape == "F" else "N"
        globals()['AHESS'] = shape == "H"
        globals()['BHESS'] = shape == "H"

        line = "-" * (len(header) - 4)
        print(line)
        for bs in block_sizes:
            globals()['bs'] = bs
            for key in benchmark_setup['display_order']:
                if key == "slycot":
                    continue
                benchmark_setup[key]['timings'] = []

            min_total_runtime = 0
            while min_total_runtime < MIN_BENCH_TIME_SECS:
                for key in benchmark_setup['display_order']:
                    if key == "slycot":
                        continue
                    benchmark_setup[key]['timings'] += timeit.repeat(
                        stmt = benchmark_setup[key]['stmt'],
                        setup = benchmark_setup[key]['setup'],
                        repeat=repeat, number = 1, globals=globals())
                total_timings = []
                for key in benchmark_setup['display_order']:
                    if key == "slycot":
                        continue
                    total_timings.append(sum(benchmark_setup[key]['timings']))
                min_total_runtime = min(total_timings)

            line = [str(M).ljust(6) + bound]
            line.append(str(bs).ljust(6) + bound)
            for key in benchmark_setup['display_order']:
                if key == "slycot":
                    continue
                line.append(
                        ("{:.7f}".format(
                         min(benchmark_setup[key]['timings']))).ljust(17)
                    )
                line.append(bound)

            print(''.join(line))

