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
        def __del__(cls):
            "Release the COM refcount we own."
            if cls:
                result = cls.Release()
        # POINTER(interface) looks nice as class name, but is it ok?
        p = _compointer_meta("POINTER(%s)" % cls.__name__,
                             (cls, _pbase),
                             {"__del__": __del__})
        from ctypes import _pointer_type_cache
        _pointer_type_cache[cls] = p
        return cls

    def __setattr__(self, name, value):
        type.__setattr__(self, name, value)
        if name != "_methods_":
            return
        self.make_methods(value)

    def make_methods(self, methods):
        from deco import _make_constants
        basemethods = getattr(self.__bases__[0], "_nummethods_", 0)
        if methods:
            for i, (restype, name, argtypes) in enumerate(methods):
                #print i + basemethods, name
                # the function prototype
                prototype = WINFUNCTYPE(restype, *argtypes)
                # the actual COM interface method object, will invoke
                # the method in the VTable of the COM interface pointer
                func = prototype(i + basemethods, name)

                # the Python method implementation in te interface
                mth = getattr(self, name, None)
                if mth is None:
                    mth = _default_implementation
                else:
                    mth = mth.im_func
                # replace the _api_ global by the COM method callable
                mth = _make_constants(mth, _api_=func)
                # replace the Python implementation by our 'decorated' function
                setattr(self, name, mth)
            self._nummethods_ = basemethods + i + 1
        else:
            self._nummethods_ = basemethods

# This class only to avoid a metaclass confict. No additional
# behaviour here.
class _compointer_meta(type(_pbase), _cominterface_meta):
    pass

def _default_implementation(self, *args):
    # Default COM client method
    return _api_(self, *args)

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
        _api_(self, byref(interface._iid_), byref(p))
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

if __name__ == "__main__":
    print help(POINTER(IUnknown))
