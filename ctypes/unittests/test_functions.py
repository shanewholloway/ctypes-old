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
    
    >>> f = dll._testfunc_i_bhilfd
    >>> f.argtypes = [c_byte, c_short, c_int, c_long, c_float, c_double]
    >>> f.restype = "h"
    >>> f(1, 2, 3, 0x400000, 5.0, 6.0)
    17

    >>> f = dll._testfunc_q_bhilfd
    >>> f.restype = "q"
    >>> f.argtypes = [c_byte, c_short, c_int, c_long, c_float, c_double]
    >>> f(1, 2, 3, 4, 5.0, 6.0)
    21L

    >>> f = dll._testfunc_q_bhilfdq
    >>> f.restype = "q"
    >>> f.argtypes = [c_byte, c_short, c_int, c_long, c_float, c_double, c_longlong]
    >>> f(1, 2, 3, 4, 5.0, 6.0, 21)
    42L

    """

def test2():
    """
    >>> f = dll._testfunc_p_p
    >>> f.restype = "z"
    >>> f("123")
    '123'
    
    >>> print f(None)
    None
    
    """

def test_callbacks():
    """
    >>> f = dll._testfunc_callback_i_if
    >>> class MyCallback(CFunction):
    ...     _stdcall_ = 0
    ...     _types_ = "i"

    >>>
    >>> def callback(value):
    ...     print "called back with", value
    
    >>> cb = MyCallback(callback)
    >>> f(-10, cb)
    called back with -10
    called back with -5
    called back with -2
    called back with -1
    -10
    
    """

def test(*args, **kw):
    import doctest, test_functions
    doctest.testmod(test_functions, *args, **kw)

if __name__ == '__main__':
    test()
