from ctypes import *
import _ctypes

dll = CDLL(_ctypes.__file__)

def test1():
    """
    >>> f = dll._testfunc_i_bhilfd
    >>> f.argtypes = [c_byte, c_short, c_int, c_long, c_float, c_double]
    >>> f(1, 2, 3, 4, 5.0, 6.0)
    21

    >>> f(-1, -2, -3, -4, -5.0, -6.0)
    -21

    >>> f = dll._testfunc_f_bhilfd
    >>> f.argtypes = [c_int, c_int, c_int, c_int, c_float, c_double]
    >>> f.restype = "f"
    >>> f(1, 2, 3, 4, 5.0, 6.0)
    21.0
    
    >>> f = dll._testfunc_d_bhilfd
    >>> f.argtypes = [c_int, c_int, c_int, c_int, c_float, c_double]
    >>> f.restype = "d"
    >>> f(1, 2, 3, 4, 5.5, 6.5)
    22.0

    >>> f = dll._testfunc_i_bhilfd
    >>> f.argtypes = [c_ubyte, c_ushort, c_uint, c_ulong, c_float, c_double]
    >>> f(1, 2, 3, 4, 5.0, 6.0)
    21
    
    >>> f(-1, -2, -3, -4, -5, -6)
    Traceback (most recent call last):
       ...
    ValueError: Value out of range
    
    
    """

def test2():
    """
    >>> f = dll._testfunc_s_s
    >>> f.restype = "z"
    >>> f("123")
    '123'
    
    >>> print f(None)
    None
    
    """

def test(*args, **kw):
    import doctest, test_functions
    doctest.testmod(test_functions, *args, **kw)

if __name__ == '__main__':
    test()
