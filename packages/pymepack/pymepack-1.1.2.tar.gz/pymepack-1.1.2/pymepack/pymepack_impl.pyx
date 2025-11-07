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
cimport scipy.linalg.cython_lapack as lapack_pointers

ctypedef fused numeric_t:
    cnp.npy_float
    cnp.npy_double

cnp.import_array()

def mepack_init():
    pymepack_def.mepack_init()

include "solvers.pyx"
include "residuals.pyx"


