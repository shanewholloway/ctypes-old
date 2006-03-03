"""
This module implements decorators for native api function calls.

name_library(name, so_name)
cdecl(restype, dllname, argtypes)
stdcall(restype, dllname, argtypes) - windows only
"""

LOGGING = False

import os
import ctypes

def cdecl(restype, dllname, argtypes, logging=False):
    """cdecl(restype, dllname, argtypes, logging=False) -> decorator.

    The decorator, when applied to a function, attaches an '_api_'
    attribute to the function.  Calling this attribute calls the
    function exported from the dll, using the standard C calling
    convention.
   
    restype - result type
    dll - name or instance of a dll/shared library
    argtypes - list of argument types
    logging - if this is True, the result of each function call
        is printed to stderr.
    """
    def decorate(func):
        library = ctypes.cdll.find(dllname, False)
        api = ctypes.CFUNCTYPE(restype, *argtypes)(func.func_name, library)
        func._api_ = api
        # The following few lines trigger a pychecker bug, see
        # https://sourceforge.net/tracker/index.php?func=detail&aid=1114902&group_id=24686&atid=382217
        if logging or LOGGING:
            def f(*args):
                result = func(*args)
                print >> sys.stderr, "# function call: %s%s -> %s" % (func.func_name, args, result)
                return result
            return f
        return func
    return decorate

if os.name == "nt":
    def stdcall(restype, dllname, argtypes, logging=False):
        """stdcall(restype, dllname, argtypes, logging=False) -> decorator.

        The decorator, when applied to a function, attaches an '_api_'
        attribute to the function.  Calling this attribute calls the
        function exported from the dll, using the MS '__stdcall' calling
        convention.

        restype - result type
        dll - name or instance of a dll
        argtypes - list of argument types
        logging - if this is True, the result of each function call
            is printed to stderr.
        """
        def decorate(func):
            library = ctypes.windll.find(dllname, False)
            api = ctypes.WINFUNCTYPE(restype, *argtypes)(func.func_name, library)
            func._api_ = api
            # The following few lines trigger a pychecker bug, see
            # https://sourceforge.net/tracker/index.php?func=detail&aid=1114902&group_id=24686&atid=382217
            if logging or LOGGING:
                def f(*args):
                    result = func(*args)
                    print >> sys.stderr, "# function call: %s%s -> %s" % (func.func_name, args, result)
                    return result
                return f
            return func
        return decorate

################################################################

def _test():
    import os, sys
    from ctypes import c_char, c_int, c_ulong, c_double, \
         POINTER, create_string_buffer, sizeof

    if os.name == "nt":
        from ctypes import WinError

        #@ stdcall(ctypes.c_ulong, "kernel32", [c_ulong, POINTER(c_char), c_ulong])
        def GetModuleFileNameA(handle=0):
            buf = create_string_buffer(256)
            if 0 == GetModuleFileNameA._api_(handle, buf, sizeof(buf)):
                raise WinError()
            return buf.value
        GetModuleFileNameA = stdcall(ctypes.c_ulong, "kernel32",
                                     [c_ulong, POINTER(c_char), c_ulong])(GetModuleFileNameA)

        assert(sys.executable == GetModuleFileNameA())

    #@ cdecl(c_double, 'libm', [c_double])
    def sqrt(value):
        return sqrt._api_(value)
    sqrt = cdecl(c_double, 'm', [c_double])(sqrt)

    assert sqrt(4.0) == 2.0

if __name__ == "__main__":
    _test()
