'''
This module implements decorators for native api function calls.

stdcall(restype, dllname, argtypes[, logging=False])
cdecl(restype, dllname, argtypes[, logging=False])

The decorator functions are used like this:

>>> from ctypes import *
>>> # wrap the GetModuleFileNameA function
>>> @ stdcall(c_ulong, "kernel32", [c_ulong, POINTER(c_char), c_ulong])
... def GetModuleFileNameA(handle=0):
...     buf = create_string_buffer(256)
...     if 0 == _api_(handle, buf, sizeof(buf)):
...         raise WinError()
...     return buf.value
>>>
>>> sys.executable == GetModuleFileNameA()
True
>>>
'''
import sys
from opcode import opmap, HAVE_ARGUMENT, EXTENDED_ARG
LOAD_GLOBAL = opmap["LOAD_GLOBAL"]
LOAD_CONST = opmap["LOAD_CONST"]

import ctypes

LOGGING = False

def _create_func_codestring(func, doc=None):
    # given a function object <func>, build the source code for
    # another function, having the same argument list, and a function
    # body which contains a call to an _api_ function.
    #
    # Assuming the <func> has this definition:
    #   def func(first, second="spam", third=42):
    #       ....
    # a string containing the following code is returned:
    #   def func(first, second="spam", third=42):
    #       return _api_(first, second, third)
    import inspect
    args, varargs, varkw, defaults = inspect.getargspec(func)
    if varkw:
        raise TypeError, "function argument list cannot contain ** argument"
    if doc:
        return "def %s%s:\n    %r\n    return _api_%s" % \
               (func.func_name,
                inspect.formatargspec(args, varargs, varkw, defaults),
                doc,
                inspect.formatargspec(args, varargs, varkw))
    return "def %s%s:\n    return _api_%s" % \
           (func.func_name,
            inspect.formatargspec(args, varargs, varkw, defaults),
            inspect.formatargspec(args, varargs, varkw))

VERBOSE = False # print opcodes replaced

def _make_constants(f, **env):
    # Replace 'LOAD_GLOBAL <name>' opcodes with 'LOAD_CONST <const>'
    # opcodes, where <const> comes from the 'name' stored in env.
    #
    # based on Raymond Hettinger's recipe 'binding constants at compile time'
    # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/277940
    if len(f.func_code.co_code) == 4:
        # Hacky way to detect an empty function body.
        codestring = _create_func_codestring(f, f.__doc__)
        d = {}
        exec codestring in d
        #print codestring
        f = d[f.func_name]

    co = f.func_code
    newcode = map(ord, co.co_code)
    newconsts = list(co.co_consts)
    names = co.co_names
    codelen = len(newcode)

    i = 0
    while i < codelen:
        opcode = newcode[i]

        if opcode == LOAD_GLOBAL:
            oparg = newcode[i+1] + (newcode[i+2] << 8)
            name = names[oparg]
            if name in env:
                value = env[name]
                for pos, v in enumerate(newconsts):
                    if v is value:
                        break
                else:
                    pos = len(newconsts)
                    newconsts.append(value)
                newcode[i] = LOAD_CONST
                newcode[i+1] = pos & 0xFF
                newcode[i+2] = pos >> 8
                if VERBOSE:
                    print >> sys.stderr, "# _make_constants: %s --> %s" % (name, value)
                
        if opcode >= HAVE_ARGUMENT:
            i += 3
        else:
            i += 1

    codestr = ''.join(map(chr, newcode))
    codeobj = type(co)(co.co_argcount, co.co_nlocals, co.co_stacksize,
                       co.co_flags, codestr, tuple(newconsts), names,
                       co.co_varnames, co.co_filename, co.co_name,
                       co.co_firstlineno, co.co_lnotab, co.co_freevars,
                       co.co_cellvars)

    func = type(f)(codeobj, f.func_globals, f.func_name, f.func_defaults,
                   f.func_closure)

# for introspection?
##    func._api_ = env["_api_"]
    return func

################################################################

def stdcall(restype, dllname, argtypes, logging=LOGGING):
    def decorate(func):
        dll = getattr(ctypes.windll, dllname)
        api = getattr(dll, func.func_name)
        api.restype = restype
        api.argtypes = argtypes
        func = _make_constants(func, _api_=api)
        if logging:
            def f(*args):
                result = func(*args)
                print >> sys.stderr, "# function call: %s%s -> %s" % (func.func_name, args, result)
                return result
            return f
        else:
            return func
    return decorate

def cdecl(restype, dllname, argtypes, logging=LOGGING):
    def decorate(func):
        dll = getattr(ctypes.cdll, dllname)
        api = getattr(dll, func.func_name)
        api.restype = restype
        api.argtypes = argtypes
        func = _make_constants(func, _api_=api)
        if logging:
            def f(*args):
                result = func(*args)
                print >> sys.stderr, func.func_name, args, "->", result
                return result
            return f
        else:
            return func
    return decorate

################################################################

if __name__ == "__main__":
    import doctest
    doctest.testmod()
