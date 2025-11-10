import numpy as np


def isinteger(num):
    return isinstance(num, (int, float,np.int8,np.int16,np.int32, np.int64))


def islist(num):
    return isinstance(num, (list, tuple, np.ndarray,range))


def isfloat(num):
    return isinstance(num, (float, np.float32, np.float64,np.float128,np.float256))


def isreal(num):
    return isinteger(num) or isfloat(num)


def iscomplex(num):
    return isinteger(num) or isfloat(num) or isinstance(num, (complex,np.complex64, np.complex128,np.complex256,np.complex512))
