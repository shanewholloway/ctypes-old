from ctypes import Structure, c_voidp, c_int, c_ulong, oledll, c_uint, POINTER, WinError
from ctypes import pointer, Union, byref, STDAPI
from ctypes.com import GUID, REFIID
from ctypes import SetPointerType

ole32 = oledll.ole32

def HRESULT(value):
    if value & 0x80000000:
        raise WinError(value)
    return value

HRESULT = c_ulong

################

def STDMETHOD(restype, name, *argtypes):
    return name, STDAPI(restype, PIUnknown, *argtypes)

class _interface_meta(type(Structure)):
    def __new__(self, name, bases, kwds):
        self.VTable_ptr = POINTER("%s_VTable" % name)
        fields = [("lpVtbl", self.VTable_ptr)]
        kwds["_fields_"] = fields
        return type(Structure).__new__(self, name, bases, kwds)

    def make_vtable(self):
        class _VTable(Structure):
            _fields_ = self._methods_
        SetPointerType(self.VTable_ptr, _VTable)

    def __call__(self, *args):
##        print "__call__"
        result = type(Structure).__call__(self, *args)
        if not hasattr(self, "AddRef"):
            self.make_vtable()
            self.make_methods()
        return result

    def make_methods(self):
##        print "make client methods for interface", self.__name__
        import new
        index = 0
        for name, PROTO in self._fields_[0][1]._type_._fields_: # VTable._fields_
##            print "\t%d %s" % (index, name)
            clientPROTO = STDAPI(PROTO._restype_, *PROTO._argtypes_[1:])
            mth = new.instancemethod(clientPROTO(index), None, self)
            setattr(self, name, mth)
            index += 1

class IUnknown(Structure):
    __metaclass__ = _interface_meta

PIUnknown = POINTER(IUnknown)

IUnknown._methods_ = [STDMETHOD(c_int, "QueryInterface", REFIID, POINTER(PIUnknown)),
                      STDMETHOD(c_ulong, "AddRef"),
                      STDMETHOD(c_ulong, "Release")]

################################################################
# implementing a COM interface pointer

E_NOTIMPL = 0x80000001

class COClass:
    _refcnt = 1

    def _notimpl(self, *args):
##        print "notimpl", args
        return E_NOTIMPL

    def AddRef(self, *args):
        self._refcnt += 1
        return self._refcnt

    def Release(self, *args):
        self._refcnt -= 1
        return self._refcnt

    def make_interface_pointer(self, itfclass):
        itf = itfclass()
        vtbltype = itfclass._fields_[0][1]._type_
        methods = []
        for name, proto in vtbltype._fields_:
            callable = getattr(self, name, self._notimpl)
            methods.append(proto(callable))
        vtbl = vtbltype(*methods)
        itf.lpVtbl = pointer(vtbl)
        return itf


from ctypes import CDLL
import _ctypes
dll = CDLL(_ctypes.__file__)

ob = COClass()

itf = ob.make_interface_pointer(IUnknown)

itf = ob.make_interface_pointer(IUnknown)

print "From Python"

print "A", itf.lpVtbl.contents.AddRef(byref(itf))
print "A", itf.lpVtbl.contents.Release(byref(itf))

print "From C"

print "B", dll._testfunc_piunk(pointer(itf))

print "From Python2"

print "C", itf.AddRef()
print "C", itf.Release()
