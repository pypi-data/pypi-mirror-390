Interface to BB03AD and BB04AD
==============================

The interface to `BB03AD` and `BB04AD` is created using f2c and numpy.f2py
in an offline phase since the numpy.distutils way compiling fortran sources is
deprecated. Once the python API changes, you have to create a folder `pyXY`,
where `X` is the python major number and `Y` is the python minor number. Then
execute:
```
cd pyXY
python3 -m numpy.f2py ../benchmarks.pyf
```
futhermore, you have to copy the `fortranobject.c` and `fortranobject.h` file
from your numpy installation to this folder. Afterwards you have to edit the top
most `setup.py` accordingly.

