# requires ctypes 0.9.3 or later
import new
from ctypes import *
from comtypes.GUID import GUID

################################################################
# The metaclasses...

class _cominterface_meta(type):
    # Metaclass for COM interface classes.
    # Creates POINTER(cls) also for the newly created class.
    def __new__(self, name, bases, namespace):
        methods = namespace.pop("_methods_", None)
        cls = type.__new__(self, name, bases, namespace)
        # XXX ??? First assign the _methods_, or first create the POINTER class?
        # or does it not matter?
        if methods:
            setattr(cls, "_methods_", methods)
        # The interface 'cls' is used as a mixin.
        # XXX "POINTER(<interface>)" looks nice as class name, but is it ok?
        p = type(_compointer_base)("POINTER(%s)" % cls.__name__,
                                   (cls, _compointer_base),
                                   {})
        from ctypes import _pointer_type_cache
        _pointer_type_cache[cls] = p
        return cls

    def __setattr__(self, name, value):
        type.__setattr__(self, name, value)
        if name != "_methods_":
            return
        self._make_methods(value)

    def __get_baseinterface_methodcount(self):
        "Return the number of com methods in the base interfaces"
        return sum([len(itf.__dict__.get("_methods_", ()))
                    for itf in self.__mro__[1:]])

    def _make_methods(self, methods):
        vtbl_offset = self.__get_baseinterface_methodcount()
        for i, (restype, name, argtypes) in enumerate(methods):
            # the function prototype
            prototype = WINFUNCTYPE(restype, *argtypes)
            # create a bound method, which will call into the COM vtbl
            # the three-argument call requires ctypes 0.9.3
            mth = prototype(i + vtbl_offset, name, self)
            impl = getattr(self, name, None)
            if impl is None:
                setattr(self, name, mth)
            else:
                mthname = "_%s__com_%s" % (self.__name__, name)
                # attach it with a private name (__com_AddRef, for example)
                setattr(self, mthname, mth)

# metaclass for COM interface pointers
class _compointer_meta(type(c_void_p), _cominterface_meta):
    pass

# base class for COM interface pointers
class _compointer_base(c_void_p):
    __metaclass__ = _compointer_meta
    def __del__(self):
        "Release the COM refcount we own."
        if self.value:
            self.Release()
    def __eq__(self, other):
        if not isinstance(other, _compointer_base):
            return False
        return self.value == other.value

################################################################

from comtypes.BSTR import BSTR

def STDMETHOD(restype, name, argtypes=()):
    "Specifies a COM method slot"
    return restype, name, argtypes

class _com_interface(object):
    __metaclass__ = _cominterface_meta

class IUnknown(_com_interface):
    _iid_ = GUID("{00000000-0000-0000-C000-000000000046}")

    _methods_ = [
        STDMETHOD(HRESULT, "QueryInterface",
                  [POINTER(GUID), POINTER(c_void_p)]),
        STDMETHOD(c_ulong, "AddRef"),
        STDMETHOD(c_ulong, "Release")
        ]

    def QueryInterface(self, interface):
        "QueryInterface(klass) -> instance"
        p = POINTER(interface)()
        self.__com_QueryInterface(byref(interface._iid_), byref(p))
        return p

    def AddRef(self):
        "Increase the internal refcount by one"
        return self.__com_AddRef()

    def Release(self):
        "Decrease the internal refcount by one"
        return self.__com_Release()

__all__ = "IUnknown GUID HRESULT BSTR STDMETHOD".split()

if __name__ == "__main__":
    POINTER(IUnknown)()

    p = POINTER(IUnknown)()

##    assert bool(p) is True
##    assert bool(p) is False

    windll.oleaut32.CreateTypeLib(1, u"blabla", byref(p))
    assert (2, 1) == (p.AddRef(), p.Release())

    p1 = p.QueryInterface(IUnknown)
    assert (3, 2) == (p1.AddRef(), p1.Release())
    p2 = p1.QueryInterface(IUnknown)

    assert p1 == p2

    del p2
    del p
    assert (2, 1) == (p1.AddRef(), p1.Release())

##    help(POINTER(IUnknown))

    del p1
