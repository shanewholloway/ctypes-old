def test_cstrings():
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

    >>> type(c_string("abc")._as_parameter_)
    <type 'CArgObject'>

    >>> c_string(None)
    <c_string NULL>
    
    >>> c_string(None)._as_parameter_
    <cparam 'z' (00000000)>

    """

def test_cWIDEcstrings():
    """
    >>> from ctypes import c_wstring
    >>> c_wstring.from_param(u"123")
    u'123'

    >>> c_wstring.from_param("123")
    Traceback (most recent call last):
       ...
    TypeError: c_wstring, unicode, or None expected

    >>> c_wstring.from_param(c_wstring("123"))
    Traceback (most recent call last):
       ...
    TypeError: unicode string or None expected

    >>> c_wstring.from_param(None)
    0

    >>> type(c_wstring(u"abc")._as_parameter_)
    <type 'CArgObject'>

    >>> c_wstring(None)
    <c_wstring NULL>
    
    >>> c_wstring(None)._as_parameter_
    <cparam 'Z' (00000000)>

    """

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

def test(*args, **kw):
    return
    try:
        from ctypes import c_wstring
    except ImportError:
        # don't try to test c_wstring if it isn't available
        test_cWIDEcstrings.__doc__ = ""

    import doctest, test_parameters
    doctest.testmod(test_parameters, *args, **kw)

if __name__ == '__main__':
    test()
