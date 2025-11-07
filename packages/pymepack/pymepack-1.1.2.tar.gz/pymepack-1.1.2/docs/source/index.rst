.. pymepack documentation master file, created by
   sphinx-quickstart on Wed Jun 22 04:27:13 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pymepack's documentation!
====================================

Python Interface for `MEPACK <https://www.mpi-magdeburg.mpg.de/projects/mepack>`_ - a Fortran software library for the solution of dense Sylvester-like matrix equations.

Contents
----------
.. toctree::
   :maxdepth: 2

   lyap_stein

   sylvester

Description
-----------

The pyMEPACK solves the following equations in single and double precision:

* Standard Lyapunov equations (:mod:`gelyap <pymepack.gelyap>`): `A X + X A^T = Y`
* Standard Stein (Discrete-Time Lyapunov) equations (:mod:`gestein <pymepack.gestein>`): `A X A^T - X = Y`
* Generalized Lyapunov equations (:mod:`gglyap <pymepack.gglyap>`): `A X B^T + B X A^T = Y`
* Generalized Stein (Discrete-Time Lyapunov) Equation (:mod:`ggstein <pymepack.ggstein>`): `A X A^T - B X B^T = Y`
* Standard Sylvester equations (:mod:`gesylv <pymepack.gesylv>`): `A X + X B = Y`
* Discrete-time Sylvester equations (:mod:`gesylv2 <pymepack.gesylv2>`): `A X B + X = Y`
* Generalized Sylvester equations (:mod:`ggsylv <pymepack.ggsylv>`): `A X B + C X D = Y`
* Generalized coupled Sylvester equations (:mod:`ggcsylv <pymepack.ggcsylv>`): `A R + L B = E; C R + L D = F`
* Dual generalized coupled Sylvester equations (:mod:`ggcsylv_dual <pymepack.ggcsylv_dual>`): `A R + C L = E; R B + L D = F`

The solvers switch automatically between single and double precision based on the precision of input arrays.

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
