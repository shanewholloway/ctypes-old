from ctypes import Structure, c_voidp, c_int, c_ulong, oledll, c_uint, POINTER, WinError
from ctypes import pointer, Union, byref, STDAPI
from ctypes.com import GUID, REFIID

ole32 = oledll.ole32

def HRESULT(value):
    if value & 0x80000000:
        raise WinError(value)
    return value

HRESULT = c_ulong

################

PIUnknown = POINTER("IUnknown")

def STDMETHOD(restype, name, *argtypes):
    return name, STDAPI(restype, PIUnknown, *argtypes)

class _interface_meta(type(Structure)):
    def __new__(self, name, bases, kwds):
        class _VTable(Structure):
            _fields_ = kwds["_methods_"]
        fields = [("lpVtbl", POINTER(_VTable))]
        kwds["_fields_"] = fields
        return type(Structure).__new__(self, name, bases, kwds)

class IUnknown(Structure):
    __metaclass__ = _interface_meta
    _methods_ = [STDMETHOD(c_int, "QueryInterface", REFIID, POINTER(PIUnknown)),
                 STDMETHOD(c_ulong, "AddRef"),
                 STDMETHOD(c_ulong, "Release")]
    
from ctypes import SetPointerType
SetPointerType(PIUnknown, IUnknown)

import new

index = 0
for name, PROTO in IUnknown._fields_[0][1]._type_._fields_: # VTable._fields_
    clientPROTO = STDAPI(PROTO._restype_, *PROTO._argtypes_[1:])
    mth = new.instancemethod(clientPROTO(index), None, IUnknown)
    setattr(IUnknown, name, mth)
    index += 1

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
        vtbltype = itfclass._fields_[0][1]._type_
        methods = []
        for name, proto in vtbltype._fields_:
            callable = getattr(self, name, self._notimpl)
            methods.append(proto(callable))
        vtbl = vtbltype(*methods)
        itf = itfclass()
        itf.lpVtbl = pointer(vtbl)
        return itf


from ctypes import CDLL
import _ctypes
dll = CDLL(_ctypes.__file__)

ob = COClass()

itf = ob.make_interface_pointer(IUnknown)

print "From Python"

print "A", itf.lpVtbl.contents.AddRef(byref(itf))
print "A", itf.lpVtbl.contents.Release(byref(itf))

print "From C"

print "B", dll._testfunc_piunk(pointer(itf))

print "From Python2"

print "C", itf.AddRef()
print "C", itf.Release()
