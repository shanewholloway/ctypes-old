from ctypes import Structure, c_voidp, c_int, c_ulong, oledll, c_uint, POINTER, WinError
from ctypes import pointer, Union, byref, STDAPI
from ctypes.com import GUID, REFIID

ole32 = oledll.ole32

from _ctypes import _SimpleCData

def HRESULT(value):
    if value & 0x80000000:
        raise WinError(value)
    return value

def STDMETHOD(restype, name, *argtypes):
    return name, STDAPI(restype, *argtypes)

################

PIUnknown = POINTER("IUnknown")

class VTable(Structure):
    _fields_ = [STDMETHOD(c_int, "QueryInterface", PIUnknown, REFIID, POINTER(PIUnknown)),
                STDMETHOD(c_int, "AddRef", PIUnknown),
                STDMETHOD(c_int, "Release", PIUnknown)]

class IUnknown(Union):
    _fields_ = [("lpVtbl", POINTER(VTable)),
                ("this", c_int)]

from ctypes import SetPointerType
SetPointerType(PIUnknown, IUnknown)

import new

name, PROTO = VTable._fields_[1]
PROTO = STDAPI(PROTO._restype_, *PROTO._argtypes_[1:])
IUnknown.my_AddRef = new.instancemethod(PROTO(1), None, IUnknown)

name, PROTO = VTable._fields_[2]
PROTO = STDAPI(PROTO._restype_, *PROTO._argtypes_[1:])
IUnknown.my_Release = new.instancemethod(PROTO(2), None, IUnknown)

################################################################
# implementing a COM interface pointer

E_NOTIMPL = 0x80000001

class COClass:
    _refcnt = 1
##    def QueryInterface(self, *args):
##        print "MyQI", args
##        return len(args)

    def _notimpl(self, *args):
##        print "notimpl", args
        return E_NOTIMPL

    def AddRef(self, *args):
        self._refcnt += 1
        return self._refcnt

##    def Release(self, *args):
##        self._refcnt -= 1
##        return self._refcnt

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

print itf.lpVtbl.contents.AddRef(byref(itf))
print "A", itf.lpVtbl.contents.Release(byref(itf))

print "From C"

print dll._testfunc_piunk(pointer(itf))

print "From Python2"

print itf.my_AddRef()
print "B", itf.my_Release()

print E_NOTIMPL
