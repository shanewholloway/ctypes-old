from ctypes import Structure, c_voidp, c_int, c_ulong, oledll, c_uint, POINTER, WinError
from ctypes import pointer, Union, byref, STDAPI
from ctypes.com import GUID, REFIID
from ctypes import SetPointerType

ole32 = oledll.ole32

def HRESULT(value):
    if value & 0x80000000:
        raise WinError(value)
    return value

################

def STDMETHOD(restype, name, *argtypes):
    return name, STDAPI(restype, PIUnknown, *argtypes)

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
    
    def __new__(self, name, bases, kwds):
        # create a new COM interface class
        self.VTable_ptr = POINTER("%s_VTable" % name)
        fields = [("lpVtbl", self.VTable_ptr)]
        kwds["_fields_"] = fields
        result = type(Structure).__new__(self, name, bases, kwds)
        if kwds.has_key("_methods_"):
            result.__make_vtable()
            result.__make_methods()
        return result

    def __make_vtable(self):
        class _VTable(Structure):
            _fields_ = self._methods_
        SetPointerType(self.VTable_ptr, _VTable)

    def __setattr__(self, name, value):
        if hasattr(self, "_methods_"):
            raise TypeError, "Cannot change _methods_"
        type(Structure).__setattr__(self, name, value)
        if name == "_methods_":
            self.__make_vtable()
            self.__make_methods()

    def __make_methods(self):
        """This method attaches methods to the interface POINTER class"""
##        print "# making client methods for interface", self.__name__
        import new
        index = 0
        ptrclass = POINTER(self)
        for name, PROTO in self._fields_[0][1]._type_._fields_: # VTable._fields_
##            print "#\t%d %s" % (index, name)
            restype = PROTO.__dict__["_restype_"]
            # the first item in argtypes is the this pointer, but we don't need it
            argtypes = PROTO.__dict__["_argtypes_"][1:]
            clientPROTO = STDAPI(restype, *argtypes)
            mth = new.instancemethod(clientPROTO(index), None, ptrclass)
            setattr(ptrclass, name, mth)
            index += 1
##        print "#"

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

class IOleObject(IUnknown):
    _iid_ = GUID("{00000112-0000-0000-C000-000000000046}")
    # Most entries are wrong, and the list is incomplete - it's only a test
    _methods_ = IUnknown._methods_ + \
                [STDMETHOD(HRESULT, "SetClientSite"),
                 STDMETHOD(HRESULT, "GetClientSite"),
                 STDMETHOD(HRESULT, "SetHostNames"),
                 STDMETHOD(HRESULT, "Close", c_ulong),
                 STDMETHOD(HRESULT, "SetMoniker"),
                 STDMETHOD(HRESULT, "GetMoniker"),
                 STDMETHOD(HRESULT, "InitFromData"),
                 STDMETHOD(HRESULT, "GetClipboardData"),
                 STDMETHOD(HRESULT, "DoVerb"),
                 STDMETHOD(HRESULT, "EnumVerbs"),
                 STDMETHOD(HRESULT, "Update"),
                 STDMETHOD(HRESULT, "IsUpToDate"),
                 STDMETHOD(HRESULT, "GetUserClassID"),
                 # more...
                 ]

PIOleObject = POINTER(IOleObject)

################################################################
# implementing a COM interface pointer

E_NOTIMPL = 0x80000001

class COMObject:
    _refcnt = 1

    def _notimpl(self, *args):
##        print "notimpl", args
        return E_NOTIMPL

    def AddRef(self, this):
        self._refcnt += 1
        return self._refcnt

    def Release(self, this):
        self._refcnt -= 1
        return self._refcnt

    def _make_interface_pointer(self, itfclass):
        # Take an interface class like 'IUnknown' and create
        # an pointer to it, implementing this interface.
        itf = itfclass()
        vtbltype = itfclass._fields_[0][1]._type_
        methods = []
        for name, proto in vtbltype._fields_:
            callable = getattr(self, name, self._notimpl)
            methods.append(proto(callable))
        vtbl = vtbltype(*methods)
        itf.lpVtbl = pointer(vtbl)
        return pointer(itf)


def implement():
    from ctypes import CDLL
    import _ctypes
    dll = CDLL(_ctypes.__file__)

    ob = COMObject()

    piunk = ob._make_interface_pointer(IUnknown)

    print "From Python"

    print "A", piunk.AddRef()
    print "A", piunk.Release()

    print "From C"

    print "B", dll._testfunc_piunk(piunk)

    print "From Python2"

    print "C", piunk.AddRef()
    print "C", piunk.Release()

################################################################
# accessing a COM interface pointer

def client():
    CLSCTX_INPROC_SERVER = 0x1
    CLSCTX_LOCAL_SERVER = 0x4

    ole32.CoInitialize(None)

    clsid_stdpicture = GUID("{00000316-0000-0000-C000-000000000046}")

    piunk = PIUnknown()

    print "CoCreateInstance", \
          ole32.CoCreateInstance(byref(clsid_stdpicture),
                                 0,
                                 CLSCTX_INPROC_SERVER,
                                 byref(IUnknown._iid_),
                                 byref(piunk))

    p2 = pointer(IUnknown())
    print "QI", piunk.QueryInterface(byref(IUnknown._iid_),
                                     byref(p2))
    p2.Release()
    

    try:
        piunk.QueryInterface(byref(GUID()),
                             byref(p2))
    except WindowsError, details:
        print details

    p3 = PIOleObject()
    print "QI OLEOBJECT", piunk.QueryInterface(byref(IOleObject._iid_),
                                     pointer(p3))

    print "IsUpToDate?", p3.IsUpToDate()
    try:
        print "Update?", p3.Update()
    except WindowsError:
        pass
    print "close", p3.Close(0)

    print "AddRef/Release", piunk.AddRef(), piunk.Release()
    print "Last Release", piunk.Release()

################################################################

if __name__ == '__main__':
    implement()
    client()
