# connect.py - ConnectionPoint support
from ctypes import POINTER, c_ulong, Structure, c_voidp, pointer, byref
from ctypes.com import IUnknown, GUID, REFIID, STDMETHOD, HRESULT

################

from ctypes.wintypes import DWORD

################

class CONNECTDATA(Structure):
    _fields_ = [("pUnk", POINTER(IUnknown)),
                ("dwCookie", DWORD)]

class IEnumConnections(IUnknown):
    _iid_ = GUID("{B196B287-BAB4-101A-B69C-00AA00341D07}")
PIEnumConnections = POINTER(IEnumConnections)

class IEnumConnectionPoints(IUnknown):
    _iid_ = GUID("{B196B285-BAB4-101A-B69C-00AA00341D07}")
PIEnumConnectionPoints = POINTER(IEnumConnectionPoints)

class IConnectionPointContainer(IUnknown):
    _iid_ = GUID("{B196B284-BAB4-101A-B69C-00AA00341D07}")
PIConnectionPointContainer = POINTER(IConnectionPointContainer)

class IConnectionPoint(IUnknown):
    _iid_ = GUID("{B196B286-BAB4-101A-B69C-00AA00341D07}")
PIConnectionPoint = POINTER(IConnectionPoint)

################

IEnumConnections._methods_ = IUnknown._methods_ + [
    STDMETHOD(HRESULT, "Next", c_ulong, POINTER(CONNECTDATA), POINTER(c_ulong)),
    STDMETHOD(HRESULT, "Skip", c_ulong),
    STDMETHOD(HRESULT, "Reset"),
    STDMETHOD(HRESULT, "Clone", POINTER(PIEnumConnections))]

IEnumConnectionPoints._methods_ = IUnknown._methods_ + [
    STDMETHOD(HRESULT, "Next", c_ulong, POINTER(IConnectionPoint), POINTER(c_ulong)),
    STDMETHOD(HRESULT, "Skip", c_ulong),
    STDMETHOD(HRESULT, "Reset"),
    STDMETHOD(HRESULT, "Clone", POINTER(PIEnumConnectionPoints))]

IConnectionPoint._methods_ = IUnknown._methods_ + [
    STDMETHOD(HRESULT, "GetConnectionInterface", POINTER(GUID)),
    STDMETHOD(HRESULT, "GetConnectionPointContainer", POINTER(PIConnectionPointContainer)),
    STDMETHOD(HRESULT, "Advise", POINTER(IUnknown), POINTER(DWORD)),
    STDMETHOD(HRESULT, "Unadvise", DWORD),
    STDMETHOD(HRESULT, "EnumConnections", POINTER(PIEnumConnections))]

IConnectionPointContainer._methods_ = IUnknown._methods_ + [
    STDMETHOD(HRESULT, "EnumConnectionPoints", POINTER(PIEnumConnectionPoints)),
    STDMETHOD(HRESULT, "FindConnectionPoint", REFIID, POINTER(PIConnectionPoint))]

def GetConnectionPoint(comptr, event_interface):
    # query for IConnectionPointContainer
    cpc = POINTER(IConnectionPointContainer)()
    comptr.QueryInterface(byref(IConnectionPointContainer._iid_), byref(cpc))

    # Find the connection point
    cp = POINTER(IConnectionPoint)()
    cpc.FindConnectionPoint(byref(event_interface._iid_), byref(cp))
    return cp

################################################################
# A Base class for events delivered to a dispinterface
#
from ctypes.com import COMObject

class dispinterface_EventReceiver(COMObject):
    # We fake the reference counts...
    def AddRef(self, this):
        return 2

    def Release(self, this):
        return 1

    def _get_args(self, dp):
        args = []
        for i in range(dp.cArgs-1, -1, -1):
            args.append(dp.rgvarg[i].value)
        return tuple(args)

    def Invoke(self,
               this,      dispid,    refiid,    lcid,
               wFlags, pDispParams, pVarResult, pExcepInfo,
               puArgErr):
        # It seems we don't have any alternative to implement Invoke
        # in Python.  Although DispInvoke does work for dual
        # interfaces, it doesn't work for dispinterfaces.  I have
        # tried this and failed with DispInvoke, and I assume its the
        # same with CreateStdDispatch.
        mthname = self._com_interfaces_[0]._dispmap_[dispid]
        mth = getattr(self, mthname, None)
        if mth is not None:
            # For symmetry with other code we also pass the this pointer
            args = self._get_args(pDispParams[0])
            mth(this, *args)
        elif __debug__:
            args = self._get_args(pDispParams[0])
            print "# Unimplemented (%s %s)" % (mthname, args)
        return 0

    def connect(self, source):
        # connect with a source.
        # returns data which must be passed to disconnect later.
        cp = GetConnectionPoint(source, self._com_interfaces_[0])
        pevents = self._com_pointers_[0][1]
        cookie = DWORD()
        cp.Advise(byref(pevents), byref(cookie))
        return cp, cookie

    def disconnect(self, (cp, cookie)):
        # disconnect. Call this with the data returned by connect()
        cp.Unadvise(cookie)
