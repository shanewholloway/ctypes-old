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
    <cparam 'f' (2.000000)>

    >>> c_float.from_param(-2.0)
    <cparam 'f' (-2.000000)>

    >>> c_float.from_param(10000000000L)
    <cparam 'f' (10000000000.000000)>

    >>> c_float.from_param(-10000000000L)
    <cparam 'f' (-10000000000.000000)>

    >>> c_float.from_param(c_float(-2.0))
    c_float(-2.000000)
    
    >>> c_float(2.0)._as_parameter_
    <cparam 'f' (2.000000)>

    >>> c_float(2.0)._as_parameter_ = None
    Traceback (most recent call last):
    TypeError: attribute '_as_parameter_' of '_ctypes._SimpleCData' objects is not writable
    
    """


def test_double():
    # C doubles are created from Python integers, longs, and floats.
    """
    >>> from ctypes import c_double

    >>> c_double.from_param(2)
    <cparam 'd' (2.000000)>

    >>> c_double.from_param(-2.0)
    <cparam 'd' (-2.000000)>

    >>> c_double.from_param(10000000000L)
    <cparam 'd' (10000000000.000000)>

    >>> c_double.from_param(-10000000000L)
    <cparam 'd' (-10000000000.000000)>

    >>> c_double.from_param(c_double(-2.0))
    c_double(-2.000000)

    >>> c_double(2.0)._as_parameter_
    <cparam 'd' (2.000000)>
    
    """

def test_integer():
    # C integers are created from Python integers and longs.
    """
    >>> from ctypes import c_byte, c_ubyte, c_short, c_ushort
    >>> from ctypes import c_int, c_uint, c_long, c_ulong
    >>> signed_types = [c_byte, c_short, c_int, c_long]
    >>> unsigned_types = [c_ubyte, c_ushort, c_uint, c_ulong]

    >>> [t.from_param(10) for t in signed_types]
    [<cparam 'b' (10)>, <cparam 'h' (10)>, <cparam 'i' (10)>, <cparam 'l' (10)>]

    >>> [t.from_param(10) for t in unsigned_types]
    [<cparam 'B' (10)>, <cparam 'H' (10)>, <cparam 'I' (10)>, <cparam 'L' (10)>]

    >>> [t.from_param(-10) for t in signed_types]
    [<cparam 'b' (-10)>, <cparam 'h' (-10)>, <cparam 'i' (-10)>, <cparam 'l' (-10)>]

    >>> [t.from_param(t(10)) for t in signed_types]
    [c_byte(10), c_short(10), c_int(10), c_long(10)]

    >>> [t.from_param(t(10)) for t in unsigned_types]
    [c_ubyte(10), c_ushort(10), c_uint(10), c_ulong(10)]

    >>> c_int(42)._as_parameter_
    <cparam 'i' (42)>

    """

def test_strings():
    # C char * is created from Python strings,
    # or from None to create a NULL pointer
    #
    # XXX How is this related to the c_char_p data type?
    # c_string is a mutable string, and c_char_p is only a pointer?
    # In this case, c_string.from_param should allocate a new buffer, probably.
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
    <type 'CArgObject'>

    >>> c_string(None)
    <c_string NULL>
    
    >>> c_string(None)._as_parameter_
    <cparam 'z' (00000000)>

    """

### disabled, doesn't yet work: c_wstring has no from_param classmethod.

####def test_wstrings():
####    # C wchar * is created from Python strings,
####    # or from None to create a NULL pointer
####    """
####    >>> from ctypes import c_wstring
####    >>> c_wstring.from_param("123")
####    '123'

####    >>> c_string.from_param(u"123")
####    Traceback (most recent call last):
####       ...
####    TypeError: c_string, string, or None expected

####    >>> c_string.from_param(c_string("123"))
####    <c_string '123'>

####    >>> c_string.from_param(None)
####    0
####    """

def test_char():
    """
    >>> from ctypes import c_char
    >>> c_char.from_param("x")
    <cparam 'c' (x)>

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
    TypeError: one character string expected

    >>> c_char.from_param(c_char("x"))
    c_char('x')

    >>> c_char("x")._as_parameter_
    <cparam 'c' (x)>

    """

def test_longlong():
    # currently you cannot pass c_longlong and c_ulonglong values
    # to function calls.
    """
    >>> from ctypes import c_longlong, c_ulonglong
    >>> c_longlong.from_param(42)
    <cparam 'q' (42)>

    >>> c_ulonglong.from_param(42)
    <cparam 'Q' (42)>
    
    """

def test_byref():
    """
    >>> from ctypes import byref, c_int, addressof
    >>> ci = c_int(42)
    >>> "<cparam 'P' (%x)>" % addressof(ci) == repr(byref(ci))
    1
    
    >>> from ctypes import pointer
    >>> p = pointer(ci)
    >>> a = addressof(p.contents)
    >>> b = p._as_parameter_
    >>> "<cparam 'P' (%x)>" % a == repr(p._as_parameter_)
    1

    """

def test(*args, **kw):
    import doctest, test_parameters
    doctest.testmod(test_parameters, *args, **kw)

if __name__ == '__main__':
    test()
