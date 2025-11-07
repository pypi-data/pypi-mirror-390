# Tuning and benchmarking

## Tuning

pyMEPACK function interfaces allow to use tuning capabilities of MEPACK by
providing two optional parameters:

* `block_size` (0 or (0,0) by default)

  For Lyapunov and Stein solvers, `block_size` parameter accepts a positive
  integer, which denotes the dimension of a square block.

  For Sylvester solvers `block_size` is a tuple of two elements, denoting the
  size of a rectangular block.

* `solver` (0 by default)

  Possible values are 0, 1, 2, or 3

If 0 is supplied to `block_size` or `solver` parameters, the default MEPACK
configuration will be applied.

For more on `solver` and `block_size` selection see the MEPACK's tuning guide.

## Benchmarking

### block_size and solver selection

Selection of an optimal block_size for a given solver can be done by running

```python
import benchmarks
import numpy as np
benchmarks.block_size_bench(solver,shape='G',repeat=3, precision=np.double, path_to_test_data=None)
```

in your Python3 environment. Where

* `solver` is the name of solver (e.g. "gelyap")
* `shape` specifies the form of the matrices with
    * 'G' for General matrix
    * 'H' for Upper Hessenberg matrix
    * 'F' for Factorized matrix
* `repeat` is the minimal number of runs for each set of parameters
* `precision` is the precision of the input data (np.single or np.double)
* `path_to_test_data` - path to and .hdf5 file with the test data. More on that see below.

#### comparing against slycot

To compare the pyMEPACK's performance against the Slycot library, run

```python
import benchmarks_slicot
import numpy as np
benchmarks.slycot_bench(solver, shape='G', repeat=3, path_to_test_data=None)
```

The meaning of the parameters is the same as for the `block_size_bench` funciton.

#### benchmarking data

By default, benchmarking data is generated as described in the Testing section.

If so is desired, one can specify a path to an `.hdf5` file with the custom benchmarking examples. To see how one can put the test data into an `.hdf5` file using `h5py` library, see `/misc/h5_test_data.py`. This file can be used to generate random data for the factorized Lyapunov equation.

The `.hdf5` file should have a certain structure, for the benchmarking algorithm to be able to retrieve the data:

* Each group name should correspond to the size of the problem (500, 1000, 2000, 3000, 4000 or 5000)

* Inside each group there should be datasets named after matrices that are passed on input of the solver (see solvers documentation for the exact name)

  For example, structure of an `.hdf5` file with test data for `gelyap` should be

  ```
  /500  /A
        /Q
        /X

  /1000 /A
        /Q
        /X
  ....
  ```

  The meaning of matrices A and Q depends on the `shape` parameter value of the invoked benchmarking function

  (if `shape = 'F'`, `/A` and `/Q` are expected to contain schur factorization of the original matrix A)

  In case when the benchmark is run with the single precision, the loaded data will be automatically converted to the correct precision.
