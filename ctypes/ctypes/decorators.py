"""
This module implements decorators for native api function calls.

stdcall(restype, dllname, argtypes[, logging=False])
cdecl(restype, dllname, argtypes[, logging=False])

The decorator functions are used like this:

>>> from ctypes import *
>>> # wrap the GetModuleFileNameA function
>>> @ stdcall(c_ulong, 'kernel32', [c_ulong, POINTER(c_char), c_ulong])
... def GetModuleFileNameA(handle=0):
...     buf = create_string_buffer(256)
...     if 0 == GetModuleFileNameA._api_(handle, buf, sizeof(buf)):
...         raise WinError()
...     return buf.value
>>>
>>> sys.executable == GetModuleFileNameA()
True
>>>
>>> @ cdecl(c_char_p, 'msvcrt', [c_char_p, c_int])
... def strchr(string, c):
...     'find a character in a string'
...     return strchr._api_(string, c)
>>> print strchr('abcdef', ord('x'))
None
>>> print strchr('abcdef', ord('c'))
cdef
>>>
"""

# This doesn't work, see below.
##>>> @ cdecl(c_char_p, 'msvcrt', [c_char_p, c_int])
##... def strchr(string, c):
##...     'find a character in a string'
##...
##>>> print strchr('abcdef', ord('x'))
##None
##>>> print strchr('abcdef', ord('c'))
##cdef
##>>>

import sys
import ctypes

LOGGING = False

##def _create_func_codestring(func, doc=None):
##    # given a function object <func>, build the source code for
##    # another function, having the same argument list, and a function
##    # body which contains a call to an _api_ function.
##    #
##    # Assuming the <func> has this definition:
##    #   def func(first, second="spam", third=42):
##    #       ....
##    # a string containing the following code is returned:
##    #   def func(first, second="spam", third=42):
##    #       return _api_(first, second, third)
##    import inspect
##    args, varargs, varkw, defaults = inspect.getargspec(func)
##    if varkw:
##        raise TypeError, "function argument list cannot contain ** argument"
##    if doc:
##        return "def %s%s:\n    %r\n    return %s._api_%s" % \
##               (func.func_name,
##                inspect.formatargspec(args, varargs, varkw, defaults),
##                doc,
##                func.func_name,
##                inspect.formatargspec(args, varargs, varkw))
##    return "def %s%s:\n    return %s._api_%s" % \
##           (func.func_name,
##            inspect.formatargspec(args, varargs, varkw, defaults),
##            func.func_name,
##            inspect.formatargspec(args, varargs, varkw))

################################################################

def stdcall(restype, dll, argtypes, logging=False):
    def decorate(func):
        if isinstance(dll, basestring):
            this_dll = ctypes.CDLL(dll)
        else:
            this_dll = dll
        api = ctypes.WINFUNCTYPE(restype, *argtypes)(func.func_name, this_dll)
        # This simple way to find out an empty function body doesn't work.
##        if len(func.func_code.co_code) == 4:
##            codestring = _create_func_codestring(func, func.__doc__)
##            d = {}
##            exec codestring in d
##            func = d[func.func_name]
        func._api_ = api
        if logging or LOGGING:
            def f(*args):
                result = func(*args)
                print >> sys.stderr, "# function call: %s%s -> %s" % (func.func_name, args, result)
                return result
            return f
        else:
            return func
    return decorate

def cdecl(restype, dll, argtypes, logging=False):
    def decorate(func):
        if isinstance(dll, basestring):
            this_dll = ctypes.CDLL(dll)
        else:
            this_dll = dll
        api = ctypes.CFUNCTYPE(restype, *argtypes)(func.func_name, this_dll)
        # This simple way to find out an empty function body doesn't work.
##        if len(func.func_code.co_code) == 4:
##            codestring = _create_func_codestring(func, func.__doc__)
##            d = {}
##            exec codestring in d
##            func = d[func.func_name]
        func._api_ = api
        if logging or LOGGING:
            def f(*args):
                result = func(*args)
                print >> sys.stderr, func.func_name, args, "->", result
                return result
            return f
        else:
            return func
    return decorate

################################################################

##if __name__ == "__main__":
if 0:
    import doctest
    doctest.testmod()
