from ctypes import Structure, POINTER, c_voidp, c_ubyte, c_byte, c_int, \
     c_ushort, c_short, c_uint, c_long, c_ulong, c_wchar_p, c_wstring
from ctypes import oledll, byref, sizeof
ole32 = oledll.ole32

from windows import *

################################################################
# COM data types
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
        s = c_wstring(u'\000' * 39)
        ole32.StringFromGUID2(byref(self), s, 39)
        return "<guid:%s>" % s.value

    def __str__(self):
        s = c_wstring(u'\000' * 39)
        ole32.StringFromGUID2(byref(self), s, 39)
        return s.value

    def __cmp__(self, other):
        if isinstance(other, GUID):
            return not ole32.IsEqualGUID(byref(self), byref(other))
        return -1

    def __eq__(self, other, IsEqualGUID=ole32.IsEqualGUID):
        return isinstance(other, GUID) and \
               IsEqualGUID(byref(self), byref(other))               

assert(sizeof(GUID) == 16)

REFCLSID = REFGUID = REFIID = POINTER(GUID)

LCID = c_ulong
DWORD = c_ulong
WORD = c_ushort

################################################################
# COM interface and pointer meta and baseclasses
#
class _COMInterfaceMeta(type(Structure)):
    def __new__(self, name, bases, dict):
        # Hm, if we want a real type for the lpvtbl field, we should
        # probably use an imcomplete pointer, and SetPointerType later.
        dict["_fields_"] = [("lpvtbl", c_voidp)]
        return type(Structure).__new__(self, name, bases, dict)

class COMInterface(Structure):
    """Base class for COM interfaces.

    In practice, all actual COM interfaces are derived from IUnknown
    or it's subclasses.

    A _methods_ class variable is required, which is a sequence of
    (methodname, argtypes) pairs.  This sequence must be in VTable
    order, and methods of the baseclass must ot be repeated in derived
    classes.

    The _methods_ variable may be set later, after to class is
    created, to help out when some methods' argument types contain
    references to interface pointers defined later.

    An _iid_ class variable is also required, it must be a GUID
    instance containing the CLSID of this interface.
    """
    __metaclass__ = _COMInterfaceMeta
    def _get_methods(self):
        # classmethod which returns the total sequence of (methodname,
        # argument_types) pairs of COM methods in VTable order.
        result = []
        for cls in self.__mro__[:-4]:
            result[0:0] = list(cls.__dict__["_methods_"])
        return result
    _get_methods = classmethod(_get_methods)

################

class _COMPointerMeta(type(Structure)):
    # This metaclass sets the required _fields_ attribute, which is
    # the same for all subclasses, and sets a flag that the Python
    # methods have not yet been created, they are lazily created
    # when the first instance is created.
    def __new__(cls, name, bases, dict):
        dict["_fields_"] = [("this", c_voidp)]
        dict["_has_methods_"] = 0
        return type(Structure).__new__(cls, name, bases, dict)

def _make_commethod(index, argtypes, name):
    # XXX move this to C code (subclass of DynFunction)
    from _ctypes import call_commethod
##    print "# make commethod %i (%s)" % (index, name), argtypes
    argtypes = tuple([a.from_param for a in argtypes])
    def func(self, *args):
        return call_commethod(self, index, args, argtypes)
    return func

################

class COMPointer(Structure):
    """
    COMPointer instances point to actual COM interface instances.

    An _interface_ class variable must contain a COMInterface class.
    Methods are automatically created from the _interface_'s _methods_
    table.  The COM reference count is handled automatically, Python
    decrements the COM refcount with Release() in the __del__ method
    of IUnknown.
    """
    __metaclass__ = _COMPointerMeta

    def __new__(cls, *args, **kw):
        if cls._has_methods_:
            return Structure.__new__(cls, *args, **kw)
##        print "# creating methods for", cls
        index = 0
        for name, argtypes in cls._interface_._get_methods():
            mth = _make_commethod(index, argtypes, name)
            setattr(cls, name, mth)
            index += 1
        cls._has_methods_ = 1
        return Structure.__new__(cls, *args, **kw)

################################################################
# This is not exported by ctypes:
_PyCArgType = type(byref(c_int()))

from _ctypes import _Pointer

class PPUNK(_Pointer):
    # Class to represent pointers to COM interface pointers.
    # Useful as argtype for methods which expect pointers to
    # COM interface pointers such as QueryInterface (VOID FAR * FAR *)
    def from_param(self, obj):
        # We accept two types of arguments here:
        # - pointers to instances of a COMPointer (sub)class
        # - PyCArgObjects containing instances of a COMPointer (sub)class
        # The first would have been created by a pointer(xxx) call,
        # the second one by byref(xxx)
        if type(obj) == _PyCArgType:
            if not isinstance(obj._obj, COMPointer):
                raise TypeError, "expected a reference to a COMPointer"
            return obj
        if not isinstance(obj, _Pointer) or \
               not issubclass(obj._type_, COMPointer):
            raise TypeError, "expected a reference to a COMPointer"
        return obj
    from_param = classmethod(from_param)

class PUNK(_Pointer):
    # Useful as argtype for methods which expect COM interface
    # pointers such as ? (VOID FAR *)
    def from_param(self, obj):
        if not isinstance(obj, COMPointer):
            raise TypeError, "expected a COMPointer"
        return obj
    from_param = classmethod(from_param)

################################################################
# actual COM insterface and pointer classes
#
class IUnknown(COMInterface):
    _iid_ = GUID("{00000000-0000-0000-C000-000000000046}")

class IUnknownPointer(COMPointer):
    _interface_ = IUnknown

    def __del__(self):
        # This code handles all the COM refcounting...
        if self.this:
            self.Release()

##IUnknown._methods_ = [("QueryInterface", [REFIID, POINTER(IUnknownPointer)]),
IUnknown._methods_ = [("QueryInterface", [REFIID, PPUNK]),
                      ("AddRef", []),
                      ("Release", [])]

################################################################

# Test code
#
CLSCTX_INPROC_SERVER = 0x1
CLSCTX_LOCAL_SERVER = 0x4

if 0:
    class IMyInterface(IUnknown):
        _iid_ = GUID("{1738f9ad-482c-402a-8c6c-578c43ed5624}")
        _methods_ = []
        
    class IMyInterfacePointer(COMPointer):
        _interface_ = IMyInterface


def test(runperf=0):

    def getrefcount(p):
        p.AddRef()
        return p.Release()

    ole32.CoInitialize(None)
    ole32.CoCreateInstance.argtypes = REFCLSID, c_voidp, DWORD, REFIID, PPUNK

    p = IUnknownPointer()
    clsid_stdpicture = GUID("{00000316-0000-0000-C000-000000000046}")

    ole32.CoCreateInstance(byref(clsid_stdpicture),
                           0,
                           CLSCTX_INPROC_SERVER,
                           byref(p._interface_._iid_),
                           byref(p))

    assert getrefcount(p) == 1

    def run_test(rep, msg, func, arg=None):
        items = range(rep)
        from time import clock
        if arg is not None:
            start = clock()
            for i in items:
                func(arg); func(arg); func(arg); func(arg); func(arg)
            stop = clock()
        else:
            start = clock()
            for i in items:
                func(); func(); func(); func(); func()
            stop = clock()
        print "%15s: %.2f us" % (msg, ((stop-start)*1e6/5/rep))

    if runperf:
        REP = 500000

        def do_nothing():
            pass

        run_test(REP, "p.AddRef()", p.AddRef) # 3.15 us
        run_test(REP, "p.Release()", p.Release) # 3.15 us
        run_test(REP, "do_nothing()", do_nothing) # 0.70 us

    assert getrefcount(p) == 1

    p2 = IUnknownPointer()
    p.QueryInterface(byref(IUnknownPointer._interface_._iid_),
                     byref(p2))

    assert getrefcount(p) == 2
    assert getrefcount(p2) == 2

    del p

    assert getrefcount(p2) == 1

    class IOleObject(IUnknown):
        _iid_ = GUID("{00000112-0000-0000-C000-000000000046}")
        _methods_ = [] # not true

    class IOleObjectPointer(COMPointer):
        _interface_ = IOleObject

    pic = IOleObjectPointer()
    p2.QueryInterface(byref(pic._interface_._iid_),
                      byref(pic))

    assert getrefcount(pic) == 2
    del p2
    assert getrefcount(pic) == 1

if __name__ == '__main__':
    test()
