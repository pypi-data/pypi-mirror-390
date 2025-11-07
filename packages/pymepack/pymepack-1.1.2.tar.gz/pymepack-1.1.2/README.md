# python-mepack (pyMEPACK)

**Version:**  1.1.2

Copyright 2023-2024 by Martin Köhler, MPI-Magdeburg

## Description

Python Interface for [MEPACK](https://www.mpi-magdeburg.mpg.de/projects/mepack)
- a Fortran software library for the solution of dense Sylvester-like matrix equations.

The pyMEPACK interfaces routines solving the following equations:

* Standard Lyapunov equations (`gelyap`) $`AX + XA^T = Y`$
* Standard Stein (Discrete-Time Lyapunov) equations (`gestein`)$`AXA^T - X = Y`$
* Generalized Lyapunov equations (`gglyap`) $`AXB^T + BXA^T = Y`$
* Generalized Stein (Discrete-Time Lyapunov) Equation (`ggstein`) $`AXA^T - BXB^T = Y`$
* Standard Sylvester equations (`gesylv`) $`AX + XB = Y`$
* Discrete-time Sylvester equations (`gesylv2`) $`AXB + X = Y`$
* Generalized Sylvester equations (`ggsylv`) $`AXB + CXD = Y`$
* Generalized coupled Sylvester equations (`ggcsylv`) $`AR + LB = E, CR + LD = F`$
* Dual generalized coupled Sylvester equations (`ggcsylv_dual`) $`AR + CL = E, RB + LD = F`$

The library includes single and double precision solvers with iterative refinement for the above equations.

## Dependencies

To install and run pyMEPACK the following components are required:

* [MEPACK](https://www.mpi-magdeburg.mpg.de/projects/mepack) Version 1.1.1
* a BLAS and LAPACK implementation
* Python 3.7.0 +
* Cython 0.29.28 +
* numpy 1.20.3 +
* scipy 1.5.4 +
* setuptools 59.0.0 +
* configparser 5.2.0 +
* parameterized 0.8.0 + (only for tests)
* h5py 3.6.0 + (only for benchmarks)
* slycot 0.4.0 (only for benchmarks)
* Sphinx 5.0.2 + (for documentation)

## Installation

pyMEPACK requires MEPACK to be installed on your system. See MEPACK's
installation guide for detail (https://gitlab.mpi-magdeburg.mpg.de/software/mepack-release/-/blob/master/doc/install.md?ref_type=heads).

If MEPACK is not installed in a default location or the BLAS and LAPACK library
are not named `blas` and `lapack` the `pymepack.cfg` file can be used to setup
these differences. See [pymepack.cfg-sample](./pymepack.cfg-sample) for details.

The installation of pyMEPACK is done by executing the following commands in the
root directory of the project:
```bash
pip install .
```
or
```bash
pip install --user .
```

After a successful installation, pyMEPACK can be imported via `import pymepack`.


## Documentation

Documentation of the pyMEPACK functions is accessible in the form of
\_\_doc\_\_ strings.

HTML Documentation can be build with Sphinx inside the `docs` directory:
```bash
(cd ./docs && make html)
```

## How to use pyMEPACK

The interface of pyMEPACK is very concise and easy to work with. The following
code snippet solves a Lyapunov equation and computes the relative residual of
the solution.

```python
#!/usr/bin/env python3

import pymepack as pme
import numpy as np
import scipy as sp

n = 1000

# Prepare
A = np.triu(np.ones((n,n))) + np.diag(np.ones((n)))
X = np.ones((n,n))
Y = A @ X + X @ A.conj().T

# Solve
Xcomp, *_ = pme.gelyap(A, Y)

# Compute the residual
RelRes = pme.res_gelyap(A, Xcomp, Y)

print("Size = {:d} RelRes = {:e}".format(n, RelRes))
```

## Testing

pyMEPACK contains a test suite. This is executed via
``` bash
(cd /tmp && python3 -m unittest -v pymepack.tests)
```
The test suite cannot run from the root of source code after installation.


### Test data

`gelyap` , `gglyap` , `gestein` and `ggstein` solvers, as well as their
respective versions with iterative refinement are tested on examples provided
in SLICOT benchmark collections, namely `BB03AD` and `BB04AD` [1,2].

All the Sylvester solvers are tested using randomization. We use `numpy.random`
module and supply the random generator with a seed to avoid build instability.
Last tested with numpy.version = 1.24.1. The non-symmetric stable matrices are
constructed as in the example 4.1 in [1].

## Tuning and Benchmarks

See [Benchmark and Tuning](./benchmark/README.md).

## License

pyMEPACK, like MEPACK it self, is license under GPLv3.


## Authors

* Martin Köhler, MPI Magdeburg
* Aleksey Maleyko, MPI Magdeburg

## Citation

```
Martin Köhler. (2024). MEPACK: Matrix Equation PACKage (1.1.1). Zenodo. https://doi.org/10.5281/zenodo.10568848
```

## References

[1] Benner, P., 2004. Factorized solution of Sylvester equations with applications in control. *sign (H)*, *1*, p.2.

[2] D. Kressner, V. Mehrmann, and T. Penzl. CTLEX - a Collection of Benchmark Examples for Continuous-Time Lyapunov Equations. SLICOT Working Note 1999-6, 1999.

[3] D. Kressner, V. Mehrmann, and T. Penzl. DTLEX - a Collection of Benchmark Examples for Discrete-Time Lyapunov Equations. SLICOT Working Note 1999-7, 1999.


