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

        # If we sublass a COM interface, for example:
        # class IDispatch(IUnknown):
        #     ....
        # then we want (need?) that
        # POINTER(IDispatch) is a subclass of POINTER(IUnknown).
        if bases == (object,):
            _ptr_bases = (cls, _compointer_base)
        else:
            _ptr_bases = (cls, POINTER(bases[0]))
        # The interface 'cls' is used as a mixin.
        # XXX "POINTER(<interface>)" looks nice as class name, but is it ok?
        p = type(_compointer_base)("POINTER(%s)" % cls.__name__,
                                   _ptr_bases,
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
                # don't overwrite a custom implementation
                setattr(self, name, mth)
            # attach it with a private name (__com_AddRef, for example)
            mthname = "_%s__com_%s" % (self.__name__, name)
            setattr(self, mthname, mth)

# metaclass for COM interface pointer classes
class _compointer_meta(type(c_void_p), _cominterface_meta):
    pass

# base class for COM interface pointer classes
class _compointer_base(c_void_p):
    __metaclass__ = _compointer_meta
    def __del__(self):
        "Release the COM refcount we own."
        if self: # calls __nonzero__
            self.Release()

    # Hm, shouldn't this be in c_void_p ?
    def __nonzero__(self):
        # get the value property of the baseclass, this is the pointer value
        # both variants below do the same, and both are equally unreadable ;-)
        return bool(super(_compointer_base, self).value)
##        return bool(c_void_p.value.__get__(self))

    def __eq__(self, other):
        # COM identity rule
        if not isinstance(other, _compointer_base):
            return False
        # get the value property of the c_void_p baseclass, this is the pointer value
        return super(_compointer_base, self).value == super(_compointer_base, other).value

    # override the .value property of c_void_p
    #
    # for symmetry with other ctypes types
    # XXX explain
    def __get_value(self):
        return self
    value = property(__get_value)

    def __repr__(self):
        return "<%s instance at %x>" % (self.__class__.__name__, id(self))
################################################################

from comtypes.BSTR import BSTR

def STDMETHOD(restype, name, argtypes=()):
    "Specifies a COM method slot"
    return restype, name, argtypes

################################################################

class IUnknown(object):
    __metaclass__ = _cominterface_meta
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

class CoClass(object):
    # creation, and so on

    def create_instance(self):
        oledll.ole32.CoInitialize(None)
        p = POINTER(self._com_interfaces_[0])()
        oledll.ole32.CoCreateInstance(byref(self._clsid_),
                                      None,
                                      7, # CLSCTX
                                      byref(p._iid_),
                                      byref(p))
        return p

__all__ = ["CoClass", "IUnknown", "GUID", "HRESULT", "BSTR", "STDMETHOD"]

if __name__ == "__main__":

##    help(POINTER(IUnknown))

    class IMyInterface(IUnknown):
        pass

    assert issubclass(IMyInterface, IUnknown)
    assert issubclass(POINTER(IMyInterface), POINTER(IUnknown))

    POINTER(IUnknown)()

    p = POINTER(IUnknown)()

##    assert bool(p) is True
##    assert bool(p) is False

    windll.oleaut32.CreateTypeLib(1, u"blabla", byref(p))

    print p

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
