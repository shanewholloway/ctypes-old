"""
Dispatch(progid, interface, clsctx
"""
import inspect

from ctypes import *
from ctypes.com import IUnknown, GUID, CreateInstance, CLSCTX_LOCAL_SERVER, \
     CLSCTX_INPROC_SERVER, ole32, STDMETHOD, HRESULT, COMObject
from ctypes.com.hresult import *
from ctypes.com.automation import IDispatch, ITypeInfo, ITypeComp, VARIANT, DISPPARAMS, \
     IEnumVARIANT, EXCEPINFO, DISPID, ITypeLib, IProvideClassInfo2
from ctypes.com.automation import BINDPTR, DESCKIND
from ctypes.com.connectionpoints import IConnectionPointContainer, IConnectionPoint, \
     IEnumConnectionPoints


################################################################

DISPATCH_METHOD = 0x1
DISPATCH_PROPERTYGET = 0x2
DISPATCH_PROPERTYPUT = 0x4
DISPATCH_PROPERTYPUTREF = 0x8

FUNC_VIRTUAL = 0
FUNC_PUREVIRTUAL = FUNC_VIRTUAL + 1
FUNC_NONVIRTUAL = FUNC_PUREVIRTUAL + 1
FUNC_STATIC = FUNC_NONVIRTUAL + 1
FUNC_DISPATCH = FUNC_STATIC + 1

DESCKIND_FUNCDESC = 1
DESCKIND_VARDESC = 2
DESCKIND_TYPECOMP = 3

DISPID_PROPERTYPUT = -3

guid_null = GUID()

################################################################

def _wrap(variant):
    if variant.vt == 9: # VT_DISPATCH
        result = variant.value
        if result:
            return _Dispatch(result)
        return None
    return variant.value

def _unwrap(x):
    if isinstance(x, _Dispatch):
        return x._comobj
    if isinstance(x, COMObject):
        ptr = POINTER(IUnknown)()
        x.QueryInterface(None, pointer(IUnknown._iid_), byref(ptr))
        return ptr
    return x

################################################################

class _funcdesc(object):
    # FUNCDESC wrapper which will eventually release the funcdesc via
    # the supplied typeinfo interface
    def __init__(self, fd, ti):
        self.fd = fd
        self.ti = ti

    def __getattr__(self, name):
        return getattr(self.fd, name)

    def __del__(self):
        self.ti.ReleaseFuncDesc(byref(self.fd))

from ctypes.com.automation import TYPEATTR, HREFTYPE, IMPLTYPEFLAGS
from ctypes.com.automation import IMPLTYPEFLAG_FSOURCE, IMPLTYPEFLAG_FDEFAULT, TKIND_DISPATCH

################################################################
# Convenience functions, simplyfing code quite a bit

class _typeattr(object):
    # TYPEATTR wrapper which will eventually release the typeattr via
    # the supplied typeinfo interface
    def __init__(self, ta, ti):
        self.ta = ta
        self.ti = ti

    def __getattr__(self, name):
        return getattr(self.ta, name)

    def __del__(self):
        self.ti.ReleaseTypeAttr(byref(self.ta))

################
def GetTypeInfo(disp, index=0, lcid=0):
    ti = POINTER(ITypeInfo)()
    disp.GetTypeInfo(index, lcid, byref(ti))
    return ti

def GetContainingTypeLib(typeinfo):
    tlb = POINTER(ITypeLib)()
    typeinfo.GetContainingTypeLib(byref(tlb), None)
    return tlb

def GetTypeInfoOfGuid(typelib, clsid):
    ti = POINTER(ITypeInfo)()
    typelib.GetTypeInfoOfGuid(byref(clsid), byref(ti))
    return ti

def GetTypeAttr(typeinfo):
    pta = POINTER(TYPEATTR)()
    typeinfo.GetTypeAttr(byref(pta))
    return _typeattr(pta[0], typeinfo)

def GetImplTypeFlags(typeinfo, index):
    flags = IMPLTYPEFLAGS()
    typeinfo.GetImplTypeFlags(index, byref(flags))
    return flags.value

def GetRefTypeInfo(typeinfo, index):
    hr = HREFTYPE()
    typeinfo.GetRefTypeOfImplType(index, byref(hr))
    ti = POINTER(ITypeInfo)()
    typeinfo.GetRefTypeInfo(hr, byref(ti))
    return ti
    
def QueryInterface(obj, interface):
    ptr = POINTER(interface)()
    obj.QueryInterface(byref(interface._iid_), byref(ptr))
    return ptr

def EnumConnectionPoints(container):
    ecp = POINTER(IEnumConnectionPoints)()
    container.EnumConnectionPoints(byref(ecp))
    return ecp

def GetConnectionInterface(cp):
    guid = GUID()
    cp.GetConnectionInterface(byref(guid))
    return guid

def Next(enum):
    cp = POINTER(IConnectionPoint)()
    if S_OK != enum.Next(1, byref(cp), None):
        raise StopIteration # ??? make the IEnumXXX pointer classes iterators themselves?
    return cp


def GetTypeComp(tlb):
    tc = POINTER(ITypeComp)()
    tlb.GetTypeComp(byref(tc))
    return tc

################################################################

class COMError(WindowsError):
    def __init__(self, *args):
        WindowsError.__init__(self, *args)
        self.args = args

    def __str__(self):
        return str(self.args)

################################################################

class _Constants(object):
    def __init__(self, ti):
        tlb = GetContainingTypeLib(ti)
        self.__tc = GetTypeComp(tlb)
        
    def __getattr__(self, name):
        bp = BINDPTR()
        dk = DESCKIND()
        ti = POINTER(ITypeInfo)()
        self.__tc.Bind(unicode(name),
                       0,
                       0,
                       byref(ti),
                       byref(dk),
                       byref(bp))
        if dk.value != DESCKIND_VARDESC:
            raise AttributeError, name
        vd = bp.lpvardesc[0]
        result = vd.u.lpvarValue[0].value
        ti.ReleaseVarDesc(bp.lpvardesc)
        return result


# For *some* info about the usage of the ITypeComp interface,
# see Inside OLE, 2nd edition: Chapter 3

# There's also a quite useful document at
# http://aromakiki.ismyweb.net/doc/S1227.htm

class _Dispatch(object):
    # these are to silence pychecker
    _comobj = None
    _typecomp = None

##    def __del__(self):
##        if self._connection is not None:
####            print "disconnecting...", self._connection
##            self._connection()
####            print "...disconnected"

    def __init__(self, comobj, typeinfo=None):
        self.__dict__["_comobj"] = comobj

        if typeinfo is None:
            typeinfo = GetTypeInfo(comobj)
        tc = QueryInterface(typeinfo, ITypeComp)
        self.__dict__["_typecomp"] = tc
        self.__dict__["_constants_"] = _Constants(typeinfo)

    def _get_funcdesc(self, name, flags):
        bp = BINDPTR()
        dk = DESCKIND()
        ti = POINTER(ITypeInfo)()
        self._typecomp.Bind(unicode(name),
                           0,
                           flags,
                           byref(ti),
                           byref(dk),
                           byref(bp))
        if dk.value != DESCKIND_FUNCDESC:
            return None
        fd = bp.lpfuncdesc[0]
##        assert fd.funckind == FUNC_DISPATCH
        return _funcdesc(fd, ti)

    def __prop_get(self, memid):
        result = VARIANT()
        self._comobj.Invoke(memid,
                           byref(guid_null),
                           0, # LCID
                           DISPATCH_PROPERTYGET,
                           byref(DISPPARAMS()),
                           byref(result),
                           None, # pExcepInfo
                           None) # puArgError
        return _wrap(result)

    def __prop_put(self, memid, value):
        parms = DISPPARAMS()
        parms.cArgs = 1
        parms.rgvarg = pointer(VARIANT(value))
        parms.cNamedArgs = 1
        parms.rgdispidNamedArgs = pointer(DISPID(DISPID_PROPERTYPUT))
        self._comobj.Invoke(memid,
                           byref(guid_null),
                           0, # LCID
                           DISPATCH_PROPERTYPUT,
                           byref(parms),
                           None, # pVarResult
                           None, # pExcepInfo
                           None) # puArgError

    def __setattr__(self, name, value):
        fd = self._get_funcdesc(name, DISPATCH_PROPERTYPUT) # | DISPATCH_PROPERTYPUTREF)
        if fd is None:
            raise AttributeError, name
        assert fd.cParams == 1
        self.__prop_put(fd.memid, _unwrap(value))

    def __getattr__(self, name):
        fd = self._get_funcdesc(name, DISPATCH_METHOD + DISPATCH_PROPERTYGET)
        if fd is None:
            raise AttributeError, name
        if fd.invkind == DISPATCH_PROPERTYGET:
            if fd.cParams == 0:
                return self.__prop_get(fd.memid)
            return _DispMethod(name, self._comobj, fd)
        elif fd.invkind == DISPATCH_METHOD:
            return _DispMethod(name, self._comobj, fd)
        else:
            raise "What's this", fd.invkind

    def __call__(self):
        return self.__prop_get(0)

    def __nonzero__(self):
        # XXX needs more...
        return True

    # What if there isn't a Count or _NewEnum method? Shouldn't we raise another
    def __len__(self):
        # XXX Should raise TypeError: len() of unsized object
        return self.Count

    def __getitem__(self, index):
        # XXX Should raise TypeError: unindexable object
        enum = POINTER(IEnumVARIANT)()
        self._NewEnum.QueryInterface(byref(IEnumVARIANT._iid_),
                                     byref(enum))
        if index:
            enum.Skip(index)
        result = VARIANT()
        enum.Next(1, byref(result), None)
        return _wrap(result)

    def __iter__(self):
        enum = POINTER(IEnumVARIANT)()
        self._NewEnum.QueryInterface(byref(IEnumVARIANT._iid_),
                                     byref(enum))
        return _NewEnum(enum)

class _NewEnum(object):
    def __init__(self, enum):
        self.enum = enum

    def __iter__(self):
        return self

    def next(self):
        result = VARIANT()
        if S_FALSE == self.enum.Next(1, byref(result), None):
            raise StopIteration
        return _wrap(result)

class _DispMethod(object):
    def __init__(self, name, comobj, fd):
        self.name = name
        self._comobj = comobj
        self.fd = fd

    def _get_dispid_dict(self, names):
        # returns a dictionary mapping parameter names to dispids.
        # The function name itself is also included, but does no harm imo.
        # XXX Is there a way to do this more efficiently, with ITypeComp?
        names = [self.name] + names
        name_array = (c_wchar_p * len(names))()
        for i, n in enumerate(names):
            name_array[i] = c_wchar_p(unicode(n))
        memids = (DISPID * len(names))()
        self._comobj.GetIDsOfNames(byref(guid_null),
                                  name_array,
                                  len(names),
                                  0,
                                  memids)
        return dict(zip(names, memids))

    def _build_parms(self, *args, **kw):
        parms = DISPPARAMS()
        parms.cArgs = len(args) + len(kw)
        parms.cNamedArgs = len(kw)
        parms.rgvarg = rgvarg = (VARIANT * parms.cArgs)()

        i = 0
        if kw:
            parms.rgdispidNamedArgs = rgdispids = (DISPID * parms.cNamedArgs)()
            d = self._get_dispid_dict(kw.keys())
            for name, value in kw.items():
                rgvarg[i].value = value
                rgdispids[i] = d[name]
                i += 1

        arguments = [_unwrap(a) for a in args]
        arguments.reverse() # that's the required ordering
        for a in arguments:
            rgvarg[i].value = a
            i += 1

        return parms

    # To support [out] parameters, it seems the following is needed:
    # build an rgvarg array containing as long as funcdesc.cParams
    # For the actual parameters passed, set the VARIANT to their value.
    # For [out] parameters (as specified in PARAMDESC.wPARAMFlags, set the VAIRANT
    # vt field to VT_BYREF (otherwise the parameter is considered read only),
    # together with the VT_XXX code as specified in TYPEDESC.vt.
    # After the call, retrieve the [out] parameters value and return
    # a tuple of them.
    def __call__(self, *args, **kw):
        parms = self._build_parms(*args, **kw)
        result = VARIANT()
        excepinfo = EXCEPINFO()
        uArgError = c_uint()
        try:
            self._comobj.Invoke(self.fd.memid,
                                byref(guid_null),
                                0, # LCID
                                self.fd.invkind,
                                byref(parms),
                                byref(result), # pVarResult
                                byref(excepinfo), # pExcepInfo
                                byref(uArgError)) # puArgError
        except WindowsError, (errno, strerror):
            assert excepinfo.pfnDeferredFillIn == 0
            raise COMError(errno, strerror, excepinfo.as_tuple(), uArgError.value)
        return _wrap(result)

    # XXX Note to self: There's a DispGetParam oleaut32 api, is this useful somewhere?

def Dispatch(progid, interface=IDispatch, clsctx=CLSCTX_INPROC_SERVER|CLSCTX_LOCAL_SERVER):
    # XXX Should we also allow GUID instances for the first parameter?
    guid = GUID.from_progid(unicode(progid))
    p = POINTER(interface)()
    ole32.CoCreateInstance(byref(guid),
                           None,
                           clsctx,
                           byref(interface._iid_),
                           byref(p))
    return _Dispatch(p)

################################################################

################################################################

def _GetOutgoingInterfaceGuid(comobj, clsid):
    try:
        pci = QueryInterface(comobj, IProvideClassInfo2)
        GUIDKIND_DEFAULT_SOURCE_DISP_IID = 1
        iid = GUID()
        pci.GetGUID(GUIDKIND_DEFAULT_SOURCE_DISP_IID, byref(iid))
        return iid
    except WindowsError:
        pass

    try:
        tlb = GetContainingTypeLib(GetTypeInfo(comobj))
    except WindowsError:
        try:
            cpc = QueryInterface(comobj, IConnectionPointContainer)
        except WindowsError:
            raise TypeError, "this COM object doesn't support events"


        cp = Next(ecp)
        guid = GetConnectionInterface(cp)
        return guid

    ti = GetTypeInfoOfGuid(tlb, clsid)
    cImplTypes = GetTypeAttr(ti).cImplTypes

    for i in range(cImplTypes):
        if GetImplTypeFlags(ti, i) != IMPLTYPEFLAG_FDEFAULT | IMPLTYPEFLAG_FSOURCE:
            continue
        iti = GetRefTypeInfo(ti, i)
        ta = GetTypeAttr(iti)
        if ta.typekind != TKIND_DISPATCH:
            continue
        iid = ta.guid.copy()
        return iid
    raise TypeError, "no usable outgoing interface found"

def _CreateOutgoingInterface(comobj, clsid):
    guid = _GetOutgoingInterfaceGuid(comobj, clsid)
    tlb = GetContainingTypeLib(GetTypeInfo(comobj))
    typeinfo = GetTypeInfoOfGuid(tlb, guid)
    typecomp = QueryInterface(typeinfo, ITypeComp)

    class MyInterface(IDispatch):
        _methods_ = IDispatch._methods_
        _iid_ = guid
        _typecomp = typecomp
        
    return MyInterface

################################################################

class _EventReceiver(COMObject):
    _com_interfaces_ = None # for pychecker
    def __init__(self, handler_class):
        super(_EventReceiver, self).__init__()
        self._handler = handler_class()
        disp_map = self.disp_map = {}
        for name, _ in inspect.getmembers(handler_class, inspect.ismethod):
            if name.startswith("_") and name.endswith("_"):
                continue
            ti = POINTER(ITypeInfo)()
            dk = DESCKIND()
            bp = BINDPTR()
            self._com_interfaces_[0]._typecomp.Bind(c_wchar_p(name),
                                                    0, # hashval
                                                    DISPATCH_METHOD | DISPATCH_PROPERTYGET,
                                                    byref(ti),
                                                    byref(dk),
                                                    byref(bp))
            if dk.value == DESCKIND_FUNCDESC:
##                print "FOUND", name
                disp_map[bp.lpfuncdesc[0].memid] = name
                ti.ReleaseFuncDesc(bp.lpfuncdesc)
            elif dk.value == DESCKIND_VARDESC:
                ti.ReleaseVarDesc(bp.lpvardesc)
            elif dk.value == DESCKIND_TYPECOMP:
                bp.lptcomp.Release()
            elif dk.value == 0:
##                print "UNFOUND", name
                pass

    def AddRef(self, this): return 2
    def Release(self, this): return 1

    def Invoke(self, this, dispid, riid, lcid, wFlags, pDispParams,
               pVarResult, pExcepInfo, puArgError):
        mth_name = self.disp_map.get(dispid)
        if mth_name is None:
            return 0
        cArgs = pDispParams[0].cArgs
        rgvarg = pDispParams[0].rgvarg
        args = [rgvarg[i].value for i in range(cArgs-1, -1, -1)]
        result = getattr(self._handler, mth_name)(*args)
        # Hm, if some of the arguments are BYREF, we should fill in
        # the return values of the method calls.  Or not?
        # No, we should only do this for out parameters.
        return 0

    def connect(self, source):
        from ctypes.com.connectionpoints import GetConnectionPoint
        cp = GetConnectionPoint(source, self._com_interfaces_[0])
        pevents = self._com_pointers_[0][1]
        from ctypes.wintypes import DWORD
        cookie = DWORD()
        cp.Advise(byref(pevents), byref(cookie))
        return cp, cookie

    def disconnect(self, (cp, cookie)):
        # disconnect. Call this with the data returned by connect()
        cp.Unadvise(cookie)

_objects = []

def DispatchWithEvents(progid, user_class, interface=IDispatch,
                       clsctx=CLSCTX_INPROC_SERVER|CLSCTX_LOCAL_SERVER):
    p = POINTER(interface)()
    clsid = GUID.from_progid(progid)
    ole32.CoCreateInstance(byref(clsid),
                           None,
                           clsctx,
                           byref(interface._iid_),
                           byref(p))

    class EventReceiver(_EventReceiver):
        _com_interfaces_ = [_CreateOutgoingInterface(p, clsid)]

    rcv = EventReceiver(user_class)
    _objects.append(rcv)
    info = rcv.connect(p)

##    def disconnect():
##        rcv.disconnect(info)

    result = _Dispatch(p)#, disconnect)
    result.__dict__["_event_handler"] = rcv._handler
    return result

def GetObject(displayName):
    # see also: c:/python23/lib/site-packages/win32com/client/__init__.py 47
    # win32com is more flexible
    from ctypes.com.moniker import MkParseDisplayName
    moniker, i, bindCtx = MkParseDisplayName("winmgmts:")
    pdisp = POINTER(IDispatch)()
    moniker.BindToObject(bindCtx, None, byref(IDispatch._iid_), byref(pdisp))
    return _Dispatch(pdisp)


if __name__ == "__main__":

    # win32com code:
    #  moniker, i, bindCtx = pythoncom.MkParseDisplayName(Pathname)
    #  dispatch = moniker.BindToObject(bindCtx, None, pythoncom.IID_IDispatch)

    d = GetObject("winmgmts:")
    result = d.ExecQuery("SELECT * FROM Win32_NTLogEvent WHERE LogFile = 'Application'")
    print len(result)
    print result.Count

    raise SystemExit


################################################################

if __name__ == "__main__":

    def test1():
##        from ctypes.com.client import Dispatch

        ag = Dispatch("Agent.Control")
        ag.Connected = 1
        ag.ShowDefaultCharacterProperties()
        ag.Characters.Load("Merlin")
        c1 = ag.Characters.Item("Merlin")
        #ch = ag.Characters("Merlin")
        c1.Show()
        c1.Speak("Python is cool!")
        c1.GestureAt(500, 20)
        c1.Think("Although you need ctypes as well ;-)")
        import time
        time.sleep(10)
        c1.Hide()
        ag.Connected = 0
        ##ag.Unload()
##    test1()

    def test3():
##        from win32com.client import DispatchWithEvents

        class Receiver:

            def OnQuit(self, *args):
                print "OnQuit", args
                windll.user32.PostQuitMessage(0)

            def BeforeNavigate2(self, disp, URL, Flags, TargetFrameName, PostData, Headers, Cancel):
                print "BeforeNavigate2", (disp, URL, Flags, TargetFrameName, PostData, Headers, Cancel)
##                return disp, URL, Flags, TargetFrameName, PostData, Headers, Cancel
##                return 1

            def NewWindow2(self, *args):
                print "NewWindow2", args

            def NavigateComplete2(self, *args):
                print "NavigateComplete2", args

            def StatusTextChange(self, *args):
                print "StatusTextChange", args

        m = DispatchWithEvents("InternetExplorer.Application", Receiver)
        m.Visible = True
        m.Navigate("http://www.python.org")

        from ctypes.com.server import pump_messages
        pump_messages()
        
    test3()
