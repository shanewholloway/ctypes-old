#
# unit tests for converting parameters to function calls.
#

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

#
# What is the _as_parameter_ property?
#
# It is a read-only property, used when an instance of c_int, c_float
# and so on is passed to a function call.
#
# The _as_parameter_ property 'returns' a 3-tuple as described above,
# or a Python integer.


def test_float():
    # C floats are created from Python integers, longs, and floats.
    """
    >>> from ctypes import c_float

    >>> c_float.from_param(2)
    ('f', 2.0, None)

    >>> c_float.from_param(-2.0)
    ('f', -2.0, None)

    >>> c_float.from_param(10000000000L)
    ('f', 10000000000.0, None)

    >>> c_float.from_param(-10000000000L)
    ('f', -10000000000.0, None)

    >>> c_float.from_param(c_float(-2.0))
    c_float(-2.000000)
    
    >>> c_float(2.0)._as_parameter_
    ('f', 2.0, c_float(2.000000))

    >>> c_float(2.0)._as_parameter_ = None
    Traceback (most recent call last):
    TypeError: attribute '_as_parameter_' of '_ctypes._SimpleCData' objects is not writable
    
    """


def test_double():
    # C doubles are created from Python integers, longs, and floats.
    """
    >>> from ctypes import c_double

    >>> c_double.from_param(2)
    ('d', 2.0, None)

    >>> c_double.from_param(-2.0)
    ('d', -2.0, None)

    >>> c_double.from_param(10000000000L)
    ('d', 10000000000.0, None)

    >>> c_double.from_param(-10000000000L)
    ('d', -10000000000.0, None)

    >>> c_double.from_param(c_double(-2.0))
    c_double(-2.000000)

    >>> c_double(2.0)._as_parameter_
    ('d', 2.0, c_double(2.000000))
    
    """

def test_integer():
    # C integers are created from Python integers and longs.
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

    >>> c_int(42)._as_parameter_
    ('i', 42, c_int(42))
    """

def test_strings():
    # C char * is created from Python strings,
    # or from None to create a NULL pointer
    """
    >>> from ctypes import c_string
    >>> c_string.from_param("123")
    '123'

    >>> c_string.from_param(u"123")
    Traceback (most recent call last):
       ...
    TypeError: c_string, string, or None expected

    >>> c_string.from_param(c_string("123"))
    <c_string '123'>

    >>> c_string.from_param(None)
    0

    # this returns the addres of the internal string buffer
    >>> type(c_string("abc")._as_parameter_)
    <type 'int'>

    >>> c_string(None)
    <c_string NULL>
    
    >>> c_string(None)._as_parameter_
    0
    """

# disabled, doesn't yet work: c_wstring has no from_param classmethod.

##def test_wstrings():
##    # C wchar * is created from Python strings,
##    # or from None to create a NULL pointer
##    """
##    >>> from ctypes import c_wstring
##    >>> c_wstring.from_param("123")
##    '123'

##    >>> c_string.from_param(u"123")
##    Traceback (most recent call last):
##       ...
##    TypeError: c_string, string, or None expected

##    >>> c_string.from_param(c_string("123"))
##    <c_string '123'>

##    >>> c_string.from_param(None)
##    0
##    """

def test_char():
    """
    >>> from ctypes import c_char
    >>> c_char.from_param("x")
    120

    >>> c_char(42)
    Traceback (most recent call last):
        ...
    TypeError: one character string expected

    >>> c_char("abc")
    Traceback (most recent call last):
        ...
    TypeError: one character string expected

    >>> c_char.from_param(u"x")
    Traceback (most recent call last):
        ...
    TypeError: expected one character string instead of unicode instance

    >>> c_char.from_param(c_char("x"))
    c_char('x')

    >>> c_char("x")._as_parameter_
    ('c', 120, c_char('x'))

    """

def test_longlong():
    # currently you cannot pass c_longlong and c_ulonglong values
    # to function calls.
    """
    >>> from ctypes import c_longlong
    >>> c_longlong.from_param(42)
    Traceback (most recent call last):
       ...
    TypeError: c_longlong and c_ulonglong objects cannot be passed as function parameters
    """

def test(*args, **kw):
    import doctest, test_parameters
    doctest.testmod(test_parameters, *args, **kw)

if __name__ == '__main__':
    test()
