from ctypes import *
from ctypes.wintypes import DWORD, HANDLE, HWND
from ctypes.com import COMObject, IUnknown, GUID, STDMETHOD, HRESULT
from ctypes.com.server import CLSCTX_INPROC_SERVER, CLSCTX_LOCAL_SERVER

################################################################

class RECTL(Structure):
    _fields_ = [("left", c_long),
                ("top", c_long),
                ("right", c_long),
                ("bottom", c_long)]

    def _get_height(self):
        return self.bottom - self.top
    height = property(_get_height)

class SIZEL(Structure):
    _fields_ = [("cx", c_long),
                ("cy", c_long)]

HDC = HANDLE

################################################################

# Fakes:
void = c_int
FORMATETC = c_int
STGMEDIUM = c_int
IMoniker = c_int
DVTARGETDEVICE = c_int
LOGPALETTE = c_int

class IAdviseSink(IUnknown):
    _iid_ = GUID("{0000010F-0000-0000-C000-000000000046}")
    _methods_ = IUnknown._methods_ + [
        STDMETHOD(void, "OnDataChange", POINTER(FORMATETC), POINTER(STGMEDIUM)),
        STDMETHOD(void, "OnViewChange", DWORD, c_long),
        STDMETHOD(void, "OnRename", POINTER(IMoniker)),
        STDMETHOD(void, "OnSave"),
        STDMETHOD(void, "OnClose")]

class IViewObject(IUnknown):
    _iid_ = GUID("{0000010D-0000-0000-C000-000000000046}")
    _methods_ = IUnknown._methods_ + [
        STDMETHOD(HRESULT, "Draw", DWORD, c_long, c_void_p,
                  POINTER(DVTARGETDEVICE), HDC, HDC, POINTER(RECTL),
                  POINTER(RECTL), c_void_p, DWORD),
        STDMETHOD(HRESULT, "GetColorSet", DWORD, c_long, c_void_p,
                  POINTER(DVTARGETDEVICE), HDC, POINTER(POINTER(LOGPALETTE))),
        STDMETHOD(HRESULT, "Freeze", DWORD, c_long, c_void_p, POINTER(DWORD)),
        STDMETHOD(HRESULT, "Unfreeze", DWORD),
        STDMETHOD(HRESULT, "SetAdvise", DWORD, DWORD, POINTER(IAdviseSink)),
        STDMETHOD(HRESULT, "GetAdvise", POINTER(DWORD), POINTER(DWORD),
                  POINTER(POINTER(IAdviseSink)))]

class IViewObject2(IViewObject):
    _iid_ = GUID("{00000127-0000-0000-C000-000000000046}")
    _methods_ = IViewObject._methods_ + [
        STDMETHOD(HRESULT, "GetExtent", DWORD, c_long,
                  POINTER(DVTARGETDEVICE), POINTER(SIZEL))]

################################################################
from ctypes.com.register import Registrar

class ControlRegistrar(Registrar):
    def build_table(self):
        """Registration for controls. There must be a subkey 'Control' (although
        this is the legacy way, the new way is to use categories.
        """
        from _winreg import HKEY_CLASSES_ROOT
        table = super(ControlRegistrar, self).build_table()
        table.append((HKEY_CLASSES_ROOT, "CLSID\\%s\\Control" % self._reg_clsid_, None, None))
        return table

################################################################

E_NOTIMPL = 0x80004001
S_OK = 0

class StopliteObject(COMObject):
    _reg_progid_ = "ctypes.Stoplite"
    _reg_desc_ = "ctypes Stoplite Object"
    _reg_clsid_ = "{36AEA23B-0DF4-45CD-8667-ED4B8DF5F73C}"

    _reg_clsctx_ = CLSCTX_INPROC_SERVER
    _com_interfaces_ = [IViewObject2]

    def _get_registrar(self):
        return ControlRegistrar(self)
    _get_registrar = classmethod(_get_registrar)

    def __init__(self):
        super(StopliteObject, self).__init__()
        self._advisesink = None
        import common
        self.model = common.Stoplite()
        self.model.redraw = self._OnViewChange

    def _OnViewChange(self, aspect=1, lindex=-1):
        # Call IAdviseSink::OnViewChange
        # DVASPECT_CONTENT = 1
        # DVASPECT_THUMBNAIL = 2
        # DVASPECT_ICON = 4
        # DVASPECT_DOCPRINT = 8
        if self._advisesink:
            self._advisesink.OnViewChange(aspect, lindex)

    def _OnClose(self):
        # Call IAdviseSink::OnClose
        if self._advisesink:
            self._advisesink.OnClose()
        
    # IViewObject interface

    def IViewObject2_SetAdvise(self, this, dwAspect, advf, AdvSink):
        # IViewObject::SetAdvise
        # Sets up a connection between the view object and an advise
        # sink so that the advise sink can receive notifications of
        # changes in the view object.
        if AdvSink:
            AdvSink.AddRef() # We have to take ownership of the COM pointer
            self._advisesink = AdvSink
        else: # got NULL pointer
            self._advisesink = None
        return S_OK

    def IViewObject2_GetAdvise(self, this, pdwAspect, padvf, ppAdvSink):
        return E_NOTIMPL

    def IViewObject2_Draw(self, this, dwAspect, lindex, pvAspect,
                          ptd, hicTargetDev, hdcDraw, lprcBounds,
                          lprcWBounds, pfnContinue, dwContinue):
        # IViewObject::Draw
        self.model.Draw(hdcDraw, lprcBounds[0])
        return S_OK

    def IViewObject2_GetColorSet(self, this, dwAspect, lindex, pvAspect,
                                 ptd, hicTargetDev, ppColorSet):
##        print "GetColorSet", bool(ptd), bool(ppColorSet)
        return E_NOTIMPL

    # IViewObject2 interface

    def IViewObject2_GetExtent(self, this, dwAspect, lindex, ptd, lpsizel):
##        print "IViewObject2::GetExtent"
        return E_NOTIMPL

if __name__ == '__main__':
    from ctypes.com.server import UseCommandLine
    UseCommandLine(StopliteObject)
