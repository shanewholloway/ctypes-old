from ctypes import Structure, POINTER, c_voidp, c_ubyte, c_byte, c_int, \
     c_ushort, c_short, c_uint, c_long, c_ulong, c_wchar_p, c_wchar, \
     oledll, byref, sizeof, WINFUNCTYPE, SetPointerType, WinError, pointer

from _ctypes import HRESULT

ole32 = oledll.ole32

from ctypes.wintypes import DWORD, WORD, BYTE

################################################################
# Basic COM data types
#

class GUID(Structure):
    _fields_ = [("Data1", DWORD),
                ("Data2", WORD),
                ("Data3", WORD),
                ("Data4", BYTE * 8)]

    def __init__(self, name=None):
        if name is not None:
            ole32.CLSIDFromString(unicode(name), byref(self))

    def __repr__(self):
        s = (c_wchar * 39)()
        ole32.StringFromGUID2(byref(self), s, 39)
        return "<guid:%s>" % s.value

    def __str__(self):
        s = (c_wchar * 39)()
        ole32.StringFromGUID2(byref(self), s, 39)
        return s.value

    def __cmp__(self, other):
        if isinstance(other, GUID):
            return not ole32.IsEqualGUID(byref(self), byref(other))
        return -1

    def __nonzero__(self):
        result = str(buffer(self)) != "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"
        print "__nonzero__", self, result
        return result

    def __eq__(self, other, IsEqualGUID=ole32.IsEqualGUID):
        return isinstance(other, GUID) and \
               IsEqualGUID(byref(self), byref(other))               
assert(sizeof(GUID) == 16), sizeof(GUID)

REFCLSID = REFGUID = REFIID = POINTER(GUID)

################################################################
# COM interface and pointer meta and baseclasses
#

def STDMETHOD(restype, name, *argtypes):
    # First argument (this) for COM method implementation is really an
    # IUnknown pointer, but we don't want this to be built all the time,
    # since we probably don't use it, so use c_voidp
    return name, WINFUNCTYPE(restype, c_voidp, *argtypes)

def COMPointer__del__(self):
    if self.contents.lpVtbl:
        self.Release()


class _interface_meta(type(Structure)):
    """Metaclass for COM interface classes.

    These classes require a _methods_ list, which must be a sequence
    of (name, prototype) pairs. 'name' is the name of the COM method,
    'prototype' is the function class containing return type and
    argument types. These pairs are usually created by the STDMETHOD()
    function.

    The list must be a VTable order, and it must include all methods
    of all base interfaces.

    The method list is used to create a VTable instance and populating
    it with C function pointers if the interface is *implemented* in
    Python.

    It is also used to automatically create Python methods for the
    POINTER class for an interface, which forward the call to the COM
    object which implements this interface.

    The list *may* be set after the class is created, but it must be
    available when the class is first used.
    """
    
    def __new__(cls, name, bases, kwds):
        # create a new COM interface class
        VTable_ptr = POINTER("%s_VTable" % name)
        fields = [("lpVtbl", VTable_ptr)]
        kwds["_fields_"] = fields
        result = type(Structure).__new__(cls, name, bases, kwds)
        result.VTable_ptr = VTable_ptr
        if kwds.has_key("_methods_"):
            result._init_class()
        return result

    def __make_vtable(self):
        # Now that self._methods_ is available, create the VTable
        _VTable = type(Structure)("%s_VTable" % self.__name__,
                                  (Structure,),
                                  {"_fields_": self._methods_})
        SetPointerType(self.VTable_ptr, _VTable)

    def _init_class(self):
        self.__make_vtable()
        self.__make_methods()
        POINTER(self).__del__ = COMPointer__del__

    def __setattr__(self, name, value):
        if name == "_methods_" and self.__dict__.has_key("_methods_"):
            raise TypeError, "Cannot change _methods_"
        type(Structure).__setattr__(self, name, value)
        if name == "_methods_":
            self._init_class()

    def __make_methods(self):
        """This method attaches methods to the interface POINTER class"""
##        print "# making client methods for interface", self.__name__
        import new
        index = 0
        ptrclass = POINTER(self)
        for name, PROTO in self._fields_[0][1]._type_._fields_: # VTable._fields_
            # PROTO is already a subclass of CFuncPtr. It is the type of a
            # function which can be used as the COM method implementation.
            # We read the restype and the argtypes from it, and construct
            # another function type, which can be used as the COM method *client*.
            # For this we don't want the first argument - the 'this' pointer.
            restype = PROTO.__dict__["_restype_"]
            argtypes = PROTO.__dict__["_argtypes_"][1:]
            clientPROTO = WINFUNCTYPE(restype, *argtypes)
            mth = new.instancemethod(clientPROTO(index), None, ptrclass)
            setattr(ptrclass, name, mth)
            index += 1

################################################################
# IUnknown, the root of all evil...

class IUnknown(Structure):
    __metaclass__ = _interface_meta
    _iid_ = GUID("{00000000-0000-0000-C000-000000000046}")

PIUnknown = POINTER(IUnknown)

################################################################
# Custom argument checking function for POINTER(PIUnknown)
_PyCArgType = type(byref(c_int()))
from ctypes import _Pointer
def from_param(self, obj):
    # We accept two types of arguments here:
    # - pointer to pointer to an instance of an IUnknown (sub)class
    # - PyCArgObjects containing pointer to an instance of an IUnknown (sub)class
    if type(obj) == _PyCArgType and \
           issubclass(obj._obj._type_, IUnknown):
        return obj
    if isinstance(obj, _Pointer) and \
           issubclass(obj._type_._type_, IUnknown):
        return obj
    raise TypeError, "expected a reference to a IUnknown"

# This must be set before it is first used in an argument list
# XXX explain reason
POINTER(PIUnknown).from_param = classmethod(from_param)

IUnknown._methods_ = [STDMETHOD(HRESULT, "QueryInterface", REFIID, POINTER(PIUnknown)),
                      STDMETHOD(c_ulong, "AddRef"),
                      STDMETHOD(c_ulong, "Release")]

################################################################

S_OK = 0
E_NOTIMPL = 0x80004001
E_NOINTERFACE = 0x80004002

class COMObject:
    _refcnt = 0
    _factory = None

    def __init__(self):
        # actually this contains (iid, interface) pairs, where iid is
        # a GUID instance, and interface is an IUnknown or subclass instance.
        # The address of this instance is the actual COM interface pointer!
        self._com_pointers_ = []
        for itf in self._com_interfaces_:
            self._make_interface_pointer(itf)

    def _make_interface_pointer(self, itfclass):
        # Take an interface class like 'IUnknown' and create
        # an pointer to it, implementing this interface.
        itf = itfclass()
        itfname = itfclass.__name__
        vtbltype = itfclass._fields_[0][1]._type_
        methods = []
        for name, proto in vtbltype._fields_:
            callable = getattr(self, "%s_%s" % (itfname, name), None)
            if callable is None:
                callable = getattr(self, name, self._notimpl)
            if callable == self._notimpl:
                print "# unimplemented %s for interface %s" % (name, itfname)
            methods.append(proto(callable))
        vtbl = vtbltype(*methods)
        itf.lpVtbl = pointer(vtbl)
        for iid in [cls._iid_ for cls in itfclass.mro()[:-3]]:
            self._com_pointers_.append((iid, itf))
        # If we would return pointer(itf) instead of byref(itf),
        # we would have to call AddRef first!
        return byref(itf)

    def _notimpl(self, *args):
        print "notimpl", args
        return E_NOTIMPL

    def QueryInterface(self, this, refiid, ppiunk):
        iid = refiid[0]
        for i, itf in self._com_pointers_:
            if i == iid:
                # *ppiunk = &itf
                from ctypes import addressof
                addr = c_voidp.from_address(addressof(ppiunk)).value
                comptr = addressof(itf)
                c_voidp.from_address(addr).value = comptr
                self.AddRef(this)
                return S_OK
        return E_NOINTERFACE

    # IUnknown methods

    def AddRef(self, this):
        self._refcnt += 1
        self._factory.LockServer(None, 1)
        return self._refcnt

    def Release(self, this):
        self._refcnt -= 1
        self._factory.LockServer(None, 0)
        return self._refcnt
