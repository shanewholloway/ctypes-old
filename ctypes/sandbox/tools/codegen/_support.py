def STDMETHOD(*args): pass # fake
def const(x): return x # fake
from ctypes import *

class _com_interface(Structure):
    _fields_ = [('lpVtbl', c_void_p)]

def STDCALL(dllname, restype, funcname, argtypes):
    # a decorator which loads the specified dll, retrieves the
    # function with the specified name, set its restype and argtypes,
    # and exposes it as an '_call_' global in the namespace of the
    # decorated function.
    def decorate(func):
        import new
        api = getattr(WinDLL(dllname), funcname)
        api.restype = restype
        api.argtypes = argtypes
        f_globals = dict(func.func_globals)
        f_globals["_call_"] = api
        f = new.function(func.func_code,
                         f_globals,
                         func.func_name,
                         func.func_defaults)
        return f
    return decorate

def CDECL(dllname, restype, funcname, argtypes):
    # a decorator which loads the specified dll, retrieves the
    # function with the specified name, set its restype and argtypes,
    # and exposes it as an '_call_' global in the namespace of the
    # decorated function.
    def decorate(func):
        import new
        api = getattr(CDLL(dllname), funcname)
        api.restype = restype
        api.argtypes = argtypes
        f_globals = dict(func.func_globals)
        f_globals["_call_"] = api
        f = new.function(func.func_code,
                         f_globals,
                         func.func_name,
                         func.func_defaults)
        return f
    return decorate

