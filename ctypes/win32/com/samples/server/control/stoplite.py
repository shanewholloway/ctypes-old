from ctypes import *
from ctypes.wintypes import DWORD, HANDLE, HWND
from ctypes.com import COMObject, IUnknown, GUID, STDMETHOD, HRESULT, ole32
from ctypes.com.server import CLSCTX_INPROC_SERVER, CLSCTX_LOCAL_SERVER
from ctypes.com.ole import IViewObject2
from ctypes.com.persist import IPersist, IPersistPropertyBag

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
    _com_interfaces_ = [IViewObject2, IPersistPropertyBag]

    def _get_registrar(self):
        return ControlRegistrar(self)
    _get_registrar = classmethod(_get_registrar)

    def __init__(self):
        super(StopliteObject, self).__init__()
        self._advisesink = None
        import common
        self.model = common.Stoplite()
        self.model.redraw = self._OnViewChange

    if 0:
        def QueryInterface(self, this, refiid, ppiunk):
            # It is sometimes useful to see which interfaces are queried by a container...
            from ctypes.com.server import dprint
            result = super(StopliteObject, self).QueryInterface(this, refiid, ppiunk)
            iid = refiid[0]
            import _winreg
            try:
                itfname = _winreg.QueryValue(_winreg.HKEY_CLASSES_ROOT, "Interface\\%s" % iid)
            except WindowsError:
                itfname = iid
            dprint("QI(%s)" % itfname, "->", hex(result))
            return result

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
        
    ################################
    # IViewObject interface

    def IViewObject_SetAdvise(self, this, dwAspect, advf, AdvSink):
        ##print "SetAdvise"
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

    def IViewObject_GetAdvise(self, this, pdwAspect, padvf, ppAdvSink):
        ##print "GetAdvise"
        return E_NOTIMPL

    def IViewObject_Draw(self, this, dwAspect, lindex, pvAspect,
                          ptd, hicTargetDev, hdcDraw, lprcBounds,
                          lprcWBounds, pfnContinue, dwContinue):
        # IViewObject::Draw
        self.model.Draw(hdcDraw, lprcBounds[0])
        return S_OK

    def IViewObject_GetColorSet(self, this, dwAspect, lindex, pvAspect,
                                 ptd, hicTargetDev, ppColorSet):
        ##print "GetColorSet", bool(ptd), bool(ppColorSet)
        return E_NOTIMPL

    ################################
    # IViewObject2 interface

    def IViewObject2_GetExtent(self, this, dwAspect, lindex, ptd, lpsizel):
        ##print "IViewObject2::GetExtent"
        return E_NOTIMPL

    ################################
    # IPersist interface

    def IPersist_GetClassID(self, this, pClassID):
        # IPersist::GetClassID
        ole32.CLSIDFromString(unicode(self._reg_clsid_), pClassID)
        return S_OK

    ################################
    # IPersistPropertyBag interface

    def IPersistPropertyBag_InitNew(self, this):
        return S_OK

    def _load_property(self, name, pPropBag, pErrorLog):
        from ctypes.com.server import dprint
        from ctypes.com.automation import VARIANT
        var = VARIANT()
        try:
            pPropBag.Read(name, byref(var), pErrorLog)
        except Exception, details:
            dprint("ERROR", details)
        return var.get_value()

    def IPersistPropertyBag_Load(self, this, pPropBag, pErrorLog):
        from ctypes.com.server import dprint
        pPropBag.AddRef()
        val = self._load_property("digits", pPropBag, pErrorLog)
        self.model._interval = val
        dprint("IPersistPropertyBag Loaded digits", val)
        return S_OK

if __name__ == '__main__':
    from ctypes.com.server import UseCommandLine
    UseCommandLine(StopliteObject)
