# simple C data unit tests for integers of different lengths
#
# byte, ubyte, short, ushort, int, uint, long, ulong,
# longlong, ulonglong

def test_ubyte():
    # c_ubyte is an unsigned character, valid range is 0 .. 255
    """
    >>> from ctypes import c_ubyte
    >>> c_ubyte(3.14)
    Traceback (most recent call last):
        ...
    TypeError: int expected instead of float instance

    >>> c_ubyte(256)
    Traceback (most recent call last):
        ...
    ValueError: Value out of range

    >>> c_ubyte(255)
    c_ubyte(255)

    >>> c_ubyte(1L)
    c_ubyte(1)

    >>> c_ubyte(0)
    c_ubyte(0)

    >>> c_ubyte(-1)
    Traceback (most recent call last):
    ...
    ValueError: Value out of range
    """

def test_byte():
    # c_byte is a signed character, valid range is -128 .. 127
    """
    >>> from ctypes import c_byte
    >>> c_byte(3.14)
    Traceback (most recent call last):
        ...
    TypeError: int expected instead of float instance

    >>> c_byte(128)
    Traceback (most recent call last):
        ...
    ValueError: Value out of range

    >>> c_byte(127)
    c_byte(127)

    >>> c_byte(1L)
    c_byte(1)

    >>> c_byte(-128)
    c_byte(-128)

    >>> c_byte(-129)
    Traceback (most recent call last):
    ...
    ValueError: Value out of range
    """

def test_ushort():
    # c_ushort is an unsigned short, valid range is 0 .. 65535
    """
    >>> from ctypes import c_ushort
    >>> c_ushort(3.14)
    Traceback (most recent call last):
        ...
    TypeError: int expected instead of float instance

    >>> c_ushort(65536)
    Traceback (most recent call last):
        ...
    ValueError: Value out of range

    >>> c_ushort(65535)
    c_ushort(65535)

    >>> c_ushort(3L)
    c_ushort(3)

    >>> c_ushort(-1)
    Traceback (most recent call last):
    ...
    ValueError: Value out of range
    """

def test_short():
    # c_short is a signed short, valid range is -32768 .. 32767
    """
    >>> from ctypes import c_short
    >>> c_short(3.14)
    Traceback (most recent call last):
        ...
    TypeError: int expected instead of float instance

    >>> c_short(32768)
    Traceback (most recent call last):
        ...
    ValueError: Value out of range

    >>> c_short(32767)
    c_short(32767)

    >>> c_short(-32768)
    c_short(-32768)

    >>> c_short(-32769)
    Traceback (most recent call last):
    ...
    ValueError: Value out of range
    """

def test_int():
    # c_int is a signed int,
    # valid range is -sys.maxint-1 .. sys.maxint

    # Note: We have to write int(a == b)
    # instead of a == b because it will be 1 or 0 in Python 2.2,
    # and True or False in Python 2.3!

    """
    >>> from ctypes import c_int; from sys import maxint
    >>> c_int(3.14)
    Traceback (most recent call last):
        ...
    TypeError: int expected instead of float instance

    >>> c_int(maxint+1)
    Traceback (most recent call last):
        ...
    ValueError: Value out of range

    >>> int(c_int(maxint).value == maxint)
    1

    >>> c_int(3L)
    c_int(3)

    >>> int(c_int(-maxint-1).value == -maxint-1)
    1

    >>> c_int(-maxint-2)
    Traceback (most recent call last):
    ...
    ValueError: Value out of range
    """

def test_uint():
    # c_uint is an unsigned int,
    # valid range is 0 .. sys.maxint*2+1
    """
    >>> from ctypes import c_uint; from sys import maxint
    >>> c_uint(3.14)
    Traceback (most recent call last):
        ...
    TypeError: int expected instead of float instance

    >>> c_uint(maxint*2+2)
    Traceback (most recent call last):
        ...
    ValueError: Value out of range

    >>> int(c_uint(maxint*2+1).value == maxint*2+1)
    1

    >>> c_uint(3L)
    c_uint(3)

    >>> c_uint(0)
    c_uint(0)

    >>> c_uint(-1)
    Traceback (most recent call last):
    ...
    ValueError: Value out of range
    """

def test_long():
    # c_long is a signed long,
    # valid range is -sys.maxint-1 .. sys.maxint
    """
    >>> from ctypes import c_long; from sys import maxint
    >>> c_long(3.14)
    Traceback (most recent call last):
        ...
    TypeError: int expected instead of float instance

    >>> c_long(maxint+1)
    Traceback (most recent call last):
        ...
    ValueError: Value out of range

    >>> int(c_long(maxint).value == maxint)
    1

    >>> c_long(3L)
    c_long(3)

    >>> int(c_long(-maxint-1).value == -maxint-1)
    1

    >>> c_long(-maxint-2)
    Traceback (most recent call last):
    ...
    ValueError: Value out of range
    """

def test_ulong():
    # c_ulong is an unsigned long,
    # valid range is 0 .. sys.maxint*2+1
    """
    >>> from ctypes import c_ulong; from sys import maxint
    >>> c_ulong(3.14)
    Traceback (most recent call last):
        ...
    TypeError: int expected instead of float instance

    >>> c_ulong(maxint*2+2)
    Traceback (most recent call last):
        ...
    ValueError: Value out of range

    >>> int(c_ulong(maxint*2+1).value == maxint*2+1)
    1

    >>> c_ulong(3L)
    c_ulong(3)

    >>> c_ulong(0)
    c_ulong(0)

    >>> c_ulong(-1)
    Traceback (most recent call last):
    ...
    ValueError: Value out of range
    """

def test_longlong():
    # c_longlong is a signed long long,
    # valid range is -sys.maxint-1 .. sys.maxint
    """
    >>> from ctypes import c_longlong; from sys import maxint
    >>> c_longlong(3.14)
    Traceback (most recent call last):
        ...
    TypeError: int expected instead of float instance

    >>> c_longlong(0x8000000000000000)
    Traceback (most recent call last):
        ...
    ValueError: Value out of range

    >>> int(c_longlong(0x7FFFFFFFFFFFFFFF).value == 0x7FFFFFFFFFFFFFFF)
    1

    >>> c_longlong(3L)
    c_longlong(3)

    >>> int(c_longlong(-0x8000000000000000).value == -0x8000000000000000)
    1

    >>> c_longlong(-0x8000000000000001)
    Traceback (most recent call last):
    ...
    ValueError: Value out of range
    """

def test_ulonglong():
    # c_ulonglong is a signed long long,
    # valid range is -sys.maxint-1 .. sys.maxint
    """
    >>> from ctypes import c_ulonglong; from sys import maxint
    >>> c_ulonglong(3.14)
    Traceback (most recent call last):
        ...
    TypeError: int expected instead of float instance

    >>> c_ulonglong(0xFFFFFFFFFFFFFFFF+1)
    Traceback (most recent call last):
        ...
    ValueError: Value out of range

    >>> int(c_ulonglong(0xFFFFFFFFFFFFFFFF).value == 0xFFFFFFFFFFFFFFFF)
    1

    >>> c_ulonglong(3L)
    c_ulonglong(3)

    >>> c_ulonglong(0)
    c_ulonglong(0)

    >>> c_ulonglong(-1)
    Traceback (most recent call last):
    ...
    ValueError: Value out of range
    """

def test_defaults():
    # All types (except c_string and c_wstring) can be created with an empty
    # constructor, and are then initialized to sensible default values
    """
    >>> from ctypes import c_byte, c_ubyte, c_short, c_ushort, c_ulonglong
    >>> from ctypes import c_int, c_uint, c_long, c_ulong, c_longlong
    >>> from ctypes import c_double, c_float, c_char
    >>> signed_types = [c_byte, c_short, c_int, c_long]
    >>> unsigned_types = [c_ubyte, c_ushort, c_uint, c_ulong]
    >>> other_types = [c_double, c_float, c_char]

    >>> [t() for t in signed_types]
    [c_byte(0), c_short(0), c_int(0), c_long(0)]

    >>> [t() for t in unsigned_types]
    [c_ubyte(0), c_ushort(0), c_uint(0), c_ulong(0)]

    >>> # for doctest, we have to escape the escape sign:
    >>> [t() for t in other_types]
    [c_double(0.000000), c_float(0.000000), c_char('\\x00')]

    """

def test(*args, **kw):
    import doctest, test_integers
    doctest.testmod(test_integers, *args, **kw)

if __name__ == '__main__':
    test()
