from ctypes import windll, oledll
from ctypes import POINTER, c_int, byref, pointer, addressof, WinError
from ctypes import Structure, Union
from ctypes import sizeof, c_ubyte, c_wchar_p

SYS_WIN16 = 0
SYS_WIN32 = SYS_WIN16 + 1
SYS_MAC = SYS_WIN32 + 1

oleaut32 = oledll.oleaut32
ole32 = oledll.ole32
ole32.CoInitialize(0)

from _ctypes import call_commethod

def dump(obj, indent=""):
    INDENT = "   "
    print "%s%s:" % (indent, obj.__class__.__name__)
    for name, fmt in obj._fields_:
        val = getattr(obj, name)
        if isinstance(val, (Structure, Union)):
            dump(val, indent + INDENT)
        elif isinstance(val, long) or isinstance(val, int):
            print "%s%30s: %s (0x%x)" % (indent, name, val, val)
        else:
            print "%s%30s: %r" % (indent, name, val)
    print


class GUID(Structure):
    _fields_ = [("Data1", "I"),
                ("Data2", "h"),
                ("Data3", "h"),
                ("Data4", c_ubyte * 8)]

    _as_parameter_ = property(byref)

##    def _get_as_parm(self):
##        return byref(self)

##    _as_parameter_ = property(_get_as_parm)
        
    def __init__(self, name=None):
        if name is not None:
            ole32.CLSIDFromString(unicode(name), byref(self))

    def __str__(self):
        from ctypes import c_wstring
        s = c_wstring(u'\000' * 39)
        ole32.StringFromGUID2(byref(self), s, 39)
        return "<guid:%s>" % s.value

    def __cmp__(self, other):
        if isinstance(other, GUID):
            result = ole32.IsEqualGUID(byref(self), byref(other))
            return not result
        return -1

################################################################

class COMInterfaceMeta(type):
    # Make sure '_com_methods_' and '_iid_' are
    # present in the class dict
    #
    # _iid_ must be a GUID specifying the implemented interface
    # _com_mmethods_ must be a sequence of strings, naming *all* the
    # methods in vtable order
    def __new__(self, name, bases, dict):
        try:
            dict["_com_methods_"]
            dict["_iid_"]
        except KeyError:
            raise ValueError, "class must have _iid_ and _com_methods_"
        return super(COMInterfaceMeta, self).__new__(self, name, bases, dict)

class IUnknown:
    __metaclass__ = COMInterfaceMeta
    _iid_ = GUID("{00000000-0000-0000-C000-000000000046}")
    _com_methods_ = "QueryInterface AddRef Release".split()

class IClassFactory(IUnknown):
    _iid_ = GUID("{00000001-0000-0000-C000-000000000046}")
    _com_methods_ = IUnknown._com_methods_ + \
                    "CreateInstance LockServer".split()

class IEnumVARIANT(IUnknown):
    _iid_ = GUID("{00020404-0000-0000-C000-000000000046}")
    _com_methods_ = IUnknown._com_methods_ + \
                    "Next Skip Reset Clone".split()

class IDispatch(IUnknown):
    _iid_ = GUID("{00020400-0000-0000-C000-000000000046}")
    _com_methods_ = IUnknown._com_methods_ + \
                    """GetTypeInfoCount GetTypeInfo GetIDsOfNames
                    Invoke""".split()

class ICreateTypeLib(IUnknown):
    _iid_ = GUID("{00020406-0000-0000-C000-000000000046}")
    _com_methods_ = IUnknown._com_methods_ + \
                    """CreateTypeInfo SetName SetVersion
                    SetGuid SetDocString SetHelpFileName
                    SetHelpContext SetLcid SetLibFlags
                    SaveAllChanges""".split()

class ICreateTypeInfo(IUnknown):
    _iid_ = GUID("{00020405-0000-0000-C000-000000000046}")
    _com_methods_ = IUnknown._com_methods_ + \
                    """SetGuid SetTypeFlags SetDocString
                    SetHelpContext SetVersion AddRefTypeInfo
                    AddFuncDesc AddImplType SetImplTypeFlags
                    SetAlignment SetSchema AddVarDesc
                    SetFuncAndParamNames SetVarName SetTypeDescAlias
                    DefineFuncAsDllEntry SetFuncDocString
                    SetVarDocString SetFuncHelpContext
                    SetVarHelpContext SetMops SetTypeIdldesc
                    LayOut""".split()

class IOleWindow(IUnknown):
    _iid_ = GUID("{00000114-0000-0000-C000-000000000046}")
    _com_methods_ = IUnknown._com_methods_ + \
                    """GetWindow ContextSensitiveHelp""".split()

class IOleInPlaceActiveObject(IOleWindow):
    _iid_ = GUID("{00000117-0000-0000-C000-000000000046}")
    _com_methods_ = IOleWindow._com_methods_ + \
                    """TranslateAccelerator OnFrameWindowActivate OnDocWindowActivate
                    ResizeBorders EnableModeless""".split()
    
    
################################################################

def _make_commethod(index):
    def func(self, *args):
        return call_commethod(self, index, args)
    return func

class COMPointerMeta(type(Structure)):
    # A metaclass for COMPointer classes, automatically creates COM methods
    #
    # All this should be extended to allow the argtypes
    # of COM methods to be specified.
    def __new__(self, name, bases, dict):
        result = super(COMPointerMeta, self).__new__(self, name, bases, dict)
        
        # iterate over the _com_methods_ sequence, and build python
        # methods from them. 'AddRef', which is always the second
        # method, will be defined like this: def AddRef(self, *args):
        # call_commethod(self, 1, args) #
        
        # If the method is already present in the class, it will not
        # be overwritten. This can be the case because subclasses have
        # their methods already, or because the programmer has already
        # implemented them.
        
        index = 0
        for mthname in dict['_interface_']._com_methods_:
            if not hasattr(result, mthname):
                mth = _make_commethod(index)
                mth.name = mthname
                setattr(result, mthname, mth)
            index += 1
        return result

class IUnknownPointer(Structure):
    _fields_ = [("this", "i")]
    _interface_ = IUnknown
    __metaclass__ = COMPointerMeta
    
    def __del__(self):
        if self.this:
            self.Release()

class IEnumVARIANTPointer(IUnknownPointer):
    _interface_ = IEnumVARIANT

class IDispatchPointer(IUnknownPointer):
    _interface_ = IDispatch


class ICreateTypeLibPointer(IUnknownPointer):
    _interface_ = ICreateTypeLib

##    def SetGuid(self, guid):
##        return call_commethod(self, 6, (byref(guid),))
##    def SetGuid(self, *args):
##        return call_commethod(self, 6, args)

class ICreateTypeInfoPointer(IUnknownPointer):
    _interface_ = ICreateTypeInfo

##    def SetGuid(self, guid):
##        return call_commethod(self, 3, (byref(guid),))
##    def SetGuid(self, *args):
##        return call_commethod(self, 3, args)

class IOleWindowPointer(IUnknownPointer):
    _interface_ = IOleWindow

class IOleInPlaceActiveObjectPointer(IOleWindowPointer):
    _interface_ = IOleInPlaceActiveObject

################################################################

def CLSIDFromProgID(progid):
    clsid = GUID()
    ole32.CLSIDFromProgID(unicode(progid), byref(clsid))
    return clsid

guid_null = GUID()

def CoCreateGuid():
    guid = GUID()
    ole32.CoCreateGuid.argtypes = [POINTER(GUID)]
    ole32.CoCreateGuid(byref(guid))
    return guid

################################################################

DISPATCH_METHOD = 0x1
DISPATCH_PROPERTYGET = 0x2
DISPATCH_PROPERTYPUT = 0x4
DISPATCH_PROPERTYPUTREF = 0x8


VT_EMPTY    = 0
VT_NULL = 1
VT_I2   = 2
VT_I4   = 3
VT_R4   = 4
VT_R8   = 5
VT_CY   = 6
VT_DATE = 7
VT_BSTR = 8
VT_DISPATCH = 9
VT_ERROR    = 10
VT_BOOL = 11
VT_VARIANT  = 12
VT_UNKNOWN  = 13
VT_DECIMAL  = 14
VT_I1   = 16
VT_UI1  = 17
VT_UI2  = 18
VT_UI4  = 19
VT_I8   = 20
VT_UI8  = 21
VT_INT  = 22
VT_UINT = 23
VT_VOID = 24
VT_HRESULT  = 25
VT_PTR  = 26
VT_SAFEARRAY    = 27
VT_CARRAY   = 28
VT_USERDEFINED  = 29
VT_LPSTR    = 30
VT_LPWSTR   = 31
VT_RECORD   = 36
VT_FILETIME = 64
VT_BLOB = 65
VT_STREAM   = 66
VT_STORAGE  = 67
VT_STREAMED_OBJECT  = 68
VT_STORED_OBJECT    = 69
VT_BLOB_OBJECT  = 70
VT_CF   = 71
VT_CLSID    = 72
VT_BSTR_BLOB    = 0xfff
VT_VECTOR   = 0x1000
VT_ARRAY    = 0x2000
VT_BYREF    = 0x4000
VT_RESERVED = 0x8000
VT_ILLEGAL  = 0xffff
VT_ILLEGALMASKED    = 0xfff
VT_TYPEMASK = 0xfff

VARIANT_GET = { VT_INT: "intVal",
                VT_I4: "intVal",
                VT_BOOL: "boolVal",
                VT_R4: "fltVal",
                VT_R8: "dblVal",
                VT_DISPATCH: "pdispVal",
                VT_UNKNOWN: "punkVal",
                VT_BSTR: "myBstrVal",
                VT_EMPTY: "intVal",
                VT_NULL: "intVal"}

VARIANT_SET = { int: ("intVal", VT_I4),
                float: ("dblVal", VT_R8),
                }

class VARIANT(Structure):
    class U(Union):
        _fields_ = [("bVal", "b"),      # VT_UI1
                    ("iVal", "h"),      # VT_I2
                    ("lVal", "l"),      # VT_I4
                    ("fltVal", "f"),    # VT_R4
                    ("dblVal", "d"),    # VT_R8
                    ("boolVal", "i"),   # VT_BOOL
                    ("scode", "i"),     # VT_ERROR
                    ("pdispVal", IDispatchPointer), # VT_DISPATCH
                    ("punkVal", IUnknownPointer), # VT_UNKNOWN

                    ("bstrVal", "i"),
                    ("myBstrVal", "Z"),
##???                    ("cVal", "c"),      # VT_I1
                    ("uiVal", "H"),     # VT_UI2
                    ("ulVal", "L"),     # VT_UI4
                    ("intVal", "i"),    # VT_INT
                    ("uintVal", "I"),   # VT_UINT
                    ]


    _fields_ = [("vt", "h"),
                ("wReserved1", "h"),
                ("wReserved2", "h"),
                ("wReserved3", "h"),
                ("u", U)]
    __slots__ = []

    def __init__(self, val=None):
        if val is not None:
            self.set_value(val)

    def set_value(self, val):
        oleaut32.VariantClear(byref(self))
        if isinstance(val, (str, unicode)):
            val = oleaut32.SysAllocString(unicode(val))
            self.vt = VT_BSTR
            self.u.bstrVal = val
            return
        field, vt = VARIANT_SET[type(val)]
        setattr(self.u, field, val)
        self.vt = vt

    def get_value(self):
        if self.vt == VT_EMPTY:
            return None
        result = getattr(self.u, VARIANT_GET[self.vt])
        if self.vt == VT_DISPATCH:
            result.AddRef()
            return Dispatch(disp=result)
        if self.vt == VT_UNKNOWN:
            result.AddRef()
        return result

class DISPPARAMS(Structure):
    _fields_ = [("rgvarg", POINTER(VARIANT)),
                ("rgdispidNamedArgs", POINTER(c_int)),
                ("cArgs", "I"),
                ("cNamedArgs", "I")]


DISPID_PROPERTYPUT = -3

class EXCEPINFO(Structure):
    _fields_ = [("wCode", "H"),
                ("wReserved", "H"),
                ("bstrSource", "Z"),
                ("bstrDescription", "Z"),
                ("bstrHelpFile", "Z"),
                ("dwHelpContext", "I"),
                ("pvReserved", "i"),
                ("pfnDeferredFillIn", "i"),
                ("scode", "i")]

################################################################

class Dispatch:
    _dispatch_ = None
    def __init__(self, progid=None, disp=None):
        if progid:
            if progid[0] == "{":
                clsid = GUID(progid)
            else:
                clsid = CLSIDFromProgID(progid)
            pdisp = IDispatchPointer()
## The following line doesn't work any longer after 0.4.0 for the 5th parameter
##            ole32.CoCreateInstance.argtypes = [POINTER(GUID), c_int, c_int,
##                                               POINTER(GUID),
##                                               POINTER(IUnknownPointer)]
            ole32.CoCreateInstance(byref(clsid),
                                   0,
                                   1 | 4, # CLSCTX_INPROC_SERVER | CLSCTX_LOCAL_SERVER
                                   byref(pdisp._interface_._iid_),
                                   byref(pdisp)
                                   )
            self.__dict__['_dispatch_'] = pdisp
        if disp:
            self.__dict__['_dispatch_'] = disp
        
# Hrm. Do we want this? better be explicit?
##    def __str__(self):
##        try:
##            return str(self())
##        except WindowsError:
##            return repr(self)

    def _GetDispID(self, name):
        Name = c_wchar_p(unicode(name))
        Dispid = c_int()

        self._dispatch_.GetIDsOfNames(byref(guid_null),
                                      byref(Name),
                                      1,
                                      0,
                                      byref(Dispid))
        return Dispid.value

    def _GetDispIDs(self, *names):
        n = len(names)
        rgNames = (c_wchar_p * n)()
        rgDispIDs = (c_int * n)()

        for i in range(len(names)):
            rgNames[i].value = unicode(names[i])

        self._dispatch_.GetIDsOfNames(byref(guid_null),
                                      rgNames,
                                      len(names),
                                      0,
                                      rgDispIDs)
        return [x.value for x in rgDispIDs]

    def __len__(self):
        return self.Count

    def __getitem__(self, index):
        _newenum = self._NewEnum

        # get a pointer to the IEnumVARIANT interface
        enum = IEnumVARIANTPointer()
        _newenum.QueryInterface(byref(enum._interface_._iid_),
                                byref(enum))

        var = VARIANT()
        fetched = c_int(1)

        enum.Reset()
        enum.Skip(index)
        enum.Next(1, byref(var), byref(fetched))
        if fetched.value != 1:
            raise IndexError, index
        return var.get_value()

    def __call__(self):
        DISPID_VALUE = 0
        params = DISPPARAMS()
        result = VARIANT()
        excepinfo = EXCEPINFO()
        try:
            self._dispatch_.Invoke(DISPID_VALUE,
                                   byref(guid_null),
                                   0, # lcid
                                   DISPATCH_METHOD | DISPATCH_PROPERTYGET,
                                   byref(params),
                                   byref(result),
                                   byref(excepinfo),
                                   0)
        except WindowsError, detail:
##            dump(excepinfo)
            raise
        return result.get_value()


    def __setattr__(self, name, value):
        if name.startswith("_"):
            self.__dict__[name] = value
            return

        params = DISPPARAMS()
        params.rgvarg = pointer(VARIANT(value))
        params.rgdispidNamedArgs = pointer(c_int(DISPID_PROPERTYPUT))
        params.cArgs = 1
        params.cNamedArgs = 1

        self._dispatch_.Invoke(self._GetDispID(name),
                               byref(guid_null),
                               0, # lcid
                               DISPATCH_PROPERTYPUT,
                               byref(params),
                               0,
                               0,
                               0)


    def __getattr__(self, name):
        if name.startswith("_") and name.endswith("_"):
            raise AttributeError, name

        try:
            dispid = self._GetDispID(name)
        except WindowsError, detail:
            raise AttributeError, name

        excepinfo=EXCEPINFO()
        result=VARIANT()
        try:
            self._dispatch_.Invoke(dispid,
                                   byref(guid_null),
                                   0, # lcid
                                   DISPATCH_PROPERTYGET,
                                   byref(DISPPARAMS()),
                                   byref(result),
                                   byref(excepinfo),
                                   0)
        except WindowsError, detail:
            pass
        else:
##            print "__getattr__", name, result.vt
            return result.get_value()
        return _DispMethod(self, dispid, name)


class _DispMethod:
    def __init__(self, owner, dispid, name):
        self.owner = owner
        self.dispid = dispid
        self.name = name

    def __repr__(self):
        return "<DispMethod at %x (dispid %d, owner %s)>" % \
               (id(self), self.dispid, self.owner)

    def __call__(self, *args, **kw):
        keys = kw.keys()
        if kw:
            dispids = self.owner._GetDispIDs(self.name, *keys)
            pairs = zip(dispids[1:], keys)
        else:
            pairs = []

        rgvArgs = (VARIANT * (len(keys) + len(args)))()
        rgdispids = (c_int * len(keys))()
        i = 0
        for disp, name in pairs:
            val = kw[name]
            rgvArgs[i].set_value(val)
            rgdispids[i].value = disp
##            print "   ", name, rgdispids[i].value, val
            i += 1

        arglist = list(args)
        arglist.reverse()

        for val in arglist:
            rgvArgs[i].set_value(val)
##            print "   ", "(%d)" % i, val
            i += 1

        params = DISPPARAMS()
        params.rgvarg = rgvArgs
        params.rgdispidNamedArgs = rgdispids
        params.cArgs = len(keys) + len(args)
        params.cNamedArgs = len(keys)

##        dump(params)

        excepinfo = EXCEPINFO()
        result = VARIANT()
##        print
        try:
            self.owner._dispatch_.Invoke(self.dispid,
                                         byref(guid_null),
                                         0, # lcid
                                         DISPATCH_METHOD,
                                         byref(params),
                                         byref(result),
                                         byref(excepinfo),
                                         0)
        except WindowsError, detail:
            print str(detail)
            print dir(detail)
            dump(excepinfo)
            raise
        return result.get_value()


def CreateTypeLib(syskind, name):
    ctl = ICreateTypeLibPointer()
    
    oleaut32.CreateTypeLib.argtypes = [c_int, c_wchar_p, POINTER(ICreateTypeLibPointer)]
    # Using the prototype above will allow us to use a normal string
    # as second parameter: It will be passed as unicode.
    oleaut32.CreateTypeLib(syskind,
##                           unicode(name),
                           name,
                           byref(ctl))
    return ctl

if __name__ == '__main__':
    cls = ICreateTypeLibPointer
    print dir(cls)
    print
    print cls.__dict__
    for name in cls.__dict__.keys():
        print name, getattr(cls, name)
