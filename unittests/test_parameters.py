#
# unit tests for converting parameters to function calls.
#
# When you assign an argtypes sequence to a function loaded from a dll,
# ctypes internally looks for a .from_param() classmethod on the sequence
# items and stores it as a converter.
#
# Calling the function later with actual arguments uses the converter function
# to convert the parameter into something else.
#
# The converted value must either be a Python integer, a C data type instance itself,
# or a 'magic' object which is currently a 3-tuple.
#
# The first element of this tuple is a one-character format code 'c', 'i', 'q',
# 'f' or 'd'.
#
# The second element is either an integer (for the 'c', 'i' codes),
# 

def test_float():
    """
    >>> from ctypes import c_float

    >>> c_float.from_param(2)
    ('f', 2.0, None)

    >>> # Hm, this *should* work...
    >>> c_float.from_param(2000000000000000L)
    Traceback (most recent call last):
      ...
    TypeError: expected number instead of long instance

    >>> c_float.from_param(-2.0)
    ('f', -2.0, None)
    """


def test_double():
    """
    >>> from ctypes import c_double

    >>> c_double.from_param(2)
    ('d', 2.0, None)

    >>> c_double.from_param(2000000000000000L)
    Traceback (most recent call last):
      ...
    TypeError: expected number instead of long instance

    >>> c_double.from_param(-2.0)
    ('d', -2.0, None)
    """

def test_integer():
    """
    >>> from ctypes import c_byte, c_ubyte, c_short, c_ushort
    >>> from ctypes import c_int, c_uint, c_long, c_ulong
    >>> signed_types = [c_byte, c_short, c_int, c_long]
    >>> unsigned_types = [c_ubyte, c_ushort, c_uint, c_ulong]

    >>> [t.from_param(10) for t in signed_types + unsigned_types]
    [10, 10, 10, 10, 10, 10, 10, 10]

    >>> [t.from_param(-10) for t in signed_types + unsigned_types]
    [-10, -10, -10, -10, -10, -10, -10, -10]

    >>> [t.from_param(10L) for t in signed_types + unsigned_types]
    [10, 10, 10, 10, 10, 10, 10, 10]

    >>> [t.from_param(t(10)) for t in signed_types]
    [c_byte(10), c_short(10), c_int(10), c_long(10)]

    >>> [t.from_param(t(10)) for t in unsigned_types]
    [c_ubyte(10), c_ushort(10), c_uint(10), c_ulong(10)]
    """

def test_strings():
    """
    >>> from ctypes import c_string
    >>> c_string.from_param("123")
    '123'

    >>> c_string.from_param(c_string("123"))
    <c_string '123'>

    >>> # NULL pointers can be specified by using None:
    >>> c_string.from_param(None)
    0

    """

def test(*args, **kw):
    import doctest, test_parameters
    doctest.testmod(test_parameters, *args, **kw)

if __name__ == '__main__':
    test()
