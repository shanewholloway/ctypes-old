import new

def STDMETHOD(*args): pass # fake
def const(x): return x # fake
from ctypes import *

class _com_interface(Structure):
    _fields_ = [('lpVtbl', c_void_p)]

def _create_func_codestring(func, name):
    # given a function <func>, build the source code for another
    # function, having the same argument list, and a function body
    # which contains a call to an _api_ function.
    # Assuming the <func> has this definition:
    #   def func(first, second="spam", third=42):
    #       ....
    # a string containing the following code is returned:
    #   def <name>(first, second="spam", third=42):
    #       return _api_(first, second, third)
    import inspect
    # inspect.getargspec() returns: (args, varargs, varkw, defaults)
    args = inspect.getargspec(func)
    if args[2]:
        raise TypeError, "function argument list cannot contain ** argument"

    argnames = args[0]
    defaults = args[-1]

    if not defaults:
        if args[1]:
            argnames.append("*%s" % args[1])
        argnames = ", ".join(argnames)
        return "def %s(%s): return _api_(%s)" % (name, argnames, argnames)

    first_list = ", ".join(argnames)

    args = argnames[:-len(defaults)]
    args.extend( ["%s=%r" % t for t in zip(argnames[-len(defaults):], defaults)] )
    args = ", ".join(args)

    return """def %s(%s): return _api_(%s)""" % (name, args, first_list)

def _decorate_with_api_global(func, call_api):
    # return a new function derived from <func>, inserting an '_api_'
    # symbol into the function globals, which is bound to the
    # <call_api> object.
    #
    # If the body of <func> is empty, a new function body is created,
    # which simply calls the _api_ object with all parameters passed to <func>.
    if len(func.func_code.co_code) == 4:
        code_string = _create_func_codestring(func, func.func_name)
        d = {}
        exec code_string in d
        func = d[func.func_name]
    func_globals = {"_api_": call_api}
    func_globals.update(func.func_globals)
    return new.function(func.func_code,
                        func_globals,
                        func.func_name,
                        func.func_defaults)

def STDCALL(dllname, restype, funcname, argtypes):
    # a decorator which loads the specified dll, retrieves the
    # function with the specified name, set its restype and argtypes,
    # and exposes it as an '_api_' global in the namespace of the
    # decorated function.
    def decorate(func):
        api = getattr(WinDLL(dllname), funcname)
        api.restype = restype
        api.argtypes = argtypes
        return _decorate_with_api_global(func, api)
    return decorate

def CDECL(dllname, restype, funcname, argtypes):
    # a decorator which loads the specified dll, retrieves the
    # function with the specified name, set its restype and argtypes,
    # and exposes it as an '_api_' global in the namespace of the
    # decorated function.
    def decorate(func):
        api = getattr(CDLL(dllname), funcname)
        api.restype = restype
        api.argtypes = argtypes
        return _decorate_with_api_global(func, api)
    return decorate

################################################################

if __name__ == "__main__":
    decorator = STDCALL("kernel32", c_int, "GetModuleHandleA", (c_char_p,))

    def GetModuleHandle(name=None):
        result = _api_(name)
        print "GetModuleHandle(%s) -> %x" % (name, result)
        return result

    print _create_func_codestring(GetModuleHandle, "GetModuleHandle")

    GetModuleHandle = decorator(GetModuleHandle)

    GetModuleHandle()
    GetModuleHandle("python.exe")
    GetModuleHandle("python23.dll")
    import zlib
    GetModuleHandle(zlib.__file__)
