from ctypes import *
try:
    HRESULT
except NameError: # ctypes 0.92 and older
    from _ctypes import HRESULT
from comtypes.GUID import GUID

################################################################
# The metaclasses...

# would c_void_p be a better base? Conflicts with the QueryInterface signature...
_pbase = POINTER(c_void_p)
#_pbase = c_void_p

def _create_method_codestring(func, doc=None):
    # Assuming the <func> has this definition:
    #   def func(self, first, second="spam", third=42):
    #       ....
    # a string containing the following code is returned:
    #   def func(self, first, second="spam", third=42):
    #       return self.func._api_(self, first, second, third)
    import inspect
    args, varargs, varkw, defaults = inspect.getargspec(func)
    if varkw:
        raise TypeError, "%s argument list must not contain ** argument" % func.func_name
    if doc:
        return "def %s%s:\n    %r\n    return self.%s._api_%s" % \
               (func.func_name,
                inspect.formatargspec(args, varargs, varkw, defaults),
                doc,
                func.func_name,
                inspect.formatargspec(args, varargs, varkw))
    return "def %s%s:\n    return self.%s._api_%s" % \
           (func.func_name,
            inspect.formatargspec(args, varargs, varkw, defaults),
            func.func_name,
            inspect.formatargspec(args, varargs, varkw))

class _cominterface_meta(type):
    # Metaclass for COM interface classes.
    # Creates POINTER(cls) also for the newly created class.
    def __new__(self, name, bases, namespace):
        methods = namespace.pop("_methods_", None)
        cls = type.__new__(self, name, bases, namespace)
        if methods:
            setattr(cls, "_methods_", methods)
        # The interface 'cls' is used as a mixin for the
        # POINTER(interface) class:
        def __del__(s_):
            "Release the COM refcount we own."
            if s_:
                result = s_.Release()
##        def __eq__(s_, other):
##            return cast(s_, c_int).value == cast(other, c_int).value
        # POINTER(interface) looks nice as class name, but is it ok?
        p = _compointer_meta("POINTER(%s)" % cls.__name__,
                             (cls, _pbase),
                             {"__del__": __del__,
##                              "__eq__": __eq__, # XXX fixme: COM identity rules
                              "_type_": c_int # XXX fixme
                              })
        from ctypes import _pointer_type_cache
        _pointer_type_cache[cls] = p
        return cls

    def __setattr__(self, name, value):
        type.__setattr__(self, name, value)
        if name != "_methods_":
            return
        self.make_methods(value)

    def __get_method(self, name):
        # should create a method if doesn't have one.
        mth = getattr(self, name, None)
        if mth is None:
            def func(self, *args):
                return getattr(self, name)._api_(self, *args)
            setattr(self, name, func)
            # convert into unbound method
            mth = getattr(self, name)
            return mth

        func = mth.im_func
        if len(func.func_code.co_code) == 4:
            # method has no body - create one
            codestring = _create_method_codestring(func, func.func_doc)
            ns = {}
            exec codestring in ns
            func = ns[func.func_name]
            # convert into unbound method
            setattr(self, name, func)
            mth = getattr(self, name)
        return mth

    def __get_baseinterface_methodcount(self):
        "Return the number of com methods in the base interfaces"
        return sum([len(itf.__dict__.get("_methods_", ()))
                    for itf in self.__mro__[1:]])

    def make_methods(self, methods):
        if not methods:
            return
        vtbl_offset = self.__get_baseinterface_methodcount()
        for i, (restype, name, argtypes) in enumerate(methods):
            # the function prototype
            prototype = WINFUNCTYPE(restype, *argtypes)
            # the actual COM interface method object, will invoke
            # the method in the VTable of the COM interface pointer
            func = prototype(i + vtbl_offset, name)

            # the Python method implementation in the interface
            mth = self.__get_method(name)
            mth.im_func._api_ = func

# This class only to avoid a metaclass confict. No additional
# behaviour here.
class _compointer_meta(type(_pbase), _cominterface_meta):
    pass

################################################################

from comtypes.BSTR import BSTR

def STDMETHOD(restype, name, argtypes=()):
    "Defines a COM method"
    return restype, name, argtypes

class IUnknown(object):
    __metaclass__ = _cominterface_meta
    _iid_ = GUID("{00000000-0000-0000-C000-000000000046}")

    def QueryInterface(self, interface):
        "QueryInterface(klass) -> instance"
        p = POINTER(interface)()
        self.QueryInterface._api_(self, byref(interface._iid_), byref(p))
        return p

    def AddRef(self):
        "Increase the internal refcount by one"

    def Release(self):
        "Decrease the internal refcount by one"

    _methods_ = [
        STDMETHOD(HRESULT, "QueryInterface",
                  [POINTER(GUID), POINTER(_pbase)]),
        STDMETHOD(c_ulong, "AddRef"),
        STDMETHOD(c_ulong, "Release")
        ]

__all__ = "IUnknown GUID HRESULT BSTR STDMETHOD".split()

if __name__ == "__main__":
    help(POINTER(IUnknown))
