from ctypes import *

import ctypes.com
ctypes.com.DEBUG = False

from ctypes.wintypes import DWORD, HANDLE, HWND
from ctypes.com import COMObject, IUnknown, GUID, STDMETHOD, HRESULT, ole32
from ctypes.com import S_OK, S_FALSE, E_NOTIMPL
from ctypes.com.server import CLSCTX_INPROC_SERVER, CLSCTX_LOCAL_SERVER
from ctypes.com.ole import IViewObject2, IOleInPlaceObject, IOleInPlaceSite
from ctypes.com.persist import IPersistStreamInit, IPersistPropertyBag
from ctypes.com.oleobject import IOleObject, CreateOleAdviseHolder

################################################################
from ctypes.com.register import Registrar

class ControlRegistrar(Registrar):
    def build_table(self):
        """Registration for controls. There must be a subkey 'Control' (although
        this is the legacy way, the new way is to use categories.
        And set 'threadingmodel' to 'apartment'.
        """
        from _winreg import HKEY_CLASSES_ROOT
        table = super(ControlRegistrar, self).build_table()
        table.append((HKEY_CLASSES_ROOT, "CLSID\\%s\\Control" % self._reg_clsid_, None, None))
        table.append((HKEY_CLASSES_ROOT, "CLSID\\%s\\InprocServer32" % self._reg_clsid_,
                      "ThreadingModel", "Apartment"))
        return table

################################################################

E_FAIL = 0x80004005L
E_POINTER = 0x8004003L

class StopliteObject(COMObject):
    _reg_progid_ = "ctypes.Stoplite"
    _reg_desc_ = "ctypes Stoplite Object"
    _reg_clsid_ = "{36AEA23B-0DF4-45CD-8667-ED4B8DF5F73C}"

    _reg_clsctx_ = CLSCTX_INPROC_SERVER
    _com_interfaces_ = [IViewObject2, IPersistStreamInit, IPersistPropertyBag,
                        IOleObject, IOleInPlaceObject]

    def _get_registrar(cls):
        return ControlRegistrar(cls)
    _get_registrar = classmethod(_get_registrar)

    def __init__(self):
        super(StopliteObject, self).__init__()
        import common
        self.model = common.Stoplite()
        self.model.redraw = self._OnViewChange
        self._adviseholder = CreateOleAdviseHolder()

    if 0 and __debug__:
        def QueryInterface(self, this, refiid, ppiunk):
            # It is sometimes useful to see which interfaces are queried by a container...
            from ctypes.com.server import dprint
            import _winreg
            result = super(StopliteObject, self).QueryInterface(this, refiid, ppiunk)
            iid = refiid[0]
            try:
                itfname = _winreg.QueryValue(_winreg.HKEY_CLASSES_ROOT, "Interface\\%s" % iid)
            except WindowsError:
                itfname = iid
            dprint("QI(%s)" % itfname, "->", hex(result))
            return result

    ################################
    # IViewObject interface

    _view_advisesink = None

    def _OnViewChange(self, aspect=1, lindex=-1):
        # Call IAdviseSink::OnViewChange
        # DVASPECT_CONTENT = 1
        # DVASPECT_THUMBNAIL = 2
        # DVASPECT_ICON = 4
        # DVASPECT_DOCPRINT = 8
        if self._view_advisesink:
            self._view_advisesink.OnViewChange(aspect, lindex)

    def _OnClose(self):
        # Call IAdviseSink::OnClose
        if self._view_advisesink:
            self._view_advisesink.OnClose()
        
    def IViewObject_SetAdvise(self, this, dwAspect, advf, AdvSink):
        ##print "SetAdvise"
        # IViewObject::SetAdvise
        # Sets up a connection between the view object and an advise
        # sink so that the advise sink can receive notifications of
        # changes in the view object.
        if AdvSink:
            AdvSink.AddRef() # We have to take ownership of the COM pointer
            self._view_advisesink = AdvSink
        else: # got NULL pointer
            self._view_advisesink = None
        return S_OK

##    def IViewObject_GetAdvise(self, this, pdwAspect, padvf, ppAdvSink):
##        return E_NOTIMPL

    def IViewObject_Draw(self, this, dwAspect, lindex, pvAspect,
                          ptd, hicTargetDev, hdcDraw, lprcBounds,
                          lprcWBounds, pfnContinue, dwContinue):
        # IViewObject::Draw
        self.model.Draw(hdcDraw, lprcBounds[0])
        return S_OK

    def IViewObject_GetColorSet(self, this, dwAspect, lindex, pvAspect,
                                 ptd, hicTargetDev, ppColorSet):
##        ##print "GetColorSet", bool(ptd), bool(ppColorSet)
        return E_NOTIMPL

    ################################
    # IViewObject2 interface

    def IViewObject2_GetExtent(self, this, dwAspect, lindex, ptd, lpsizel):
##        ##print "IViewObject2::GetExtent"
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
        from ctypes.com.automation import VARIANT
        var = VARIANT()
        pPropBag.Read(name, byref(var), pErrorLog)
        return var.value

    def IPersistPropertyBag_Load(self, this, pPropBag, pErrorLog):
        # We must *always* AddRef() the COM pointers we receive,
        # to match the Release() call when they go out of scope!
        if pErrorLog:
            pErrorLog.AddRef()
        if pPropBag:
            pPropBag.AddRef()
        val = self._load_property(u"digits", pPropBag, pErrorLog)
        self.model._interval = val
        return S_OK

    ################################
    # IPersistStreamInit interface

    def IPersistStreamInit_IsDirty(self, this):
        return S_FALSE

    def IPersistStreamInit_Load(self, this, pStm):
        if pStm:
            pStm.AddRef()
        return S_OK

    def IPersistStreamInit_Save(self, this, pStm, fClearDirty):
        if pStm:
            pStm.AddRef()
        return S_OK

    def IPersistStreamInit_GetSizeMax(self, this, pcbSize):
        from ctypes.com.server import dprint
        pcbSize[0] = 1234
        return S_OK

    def IPersistStreamInit_InitNew(self, this):
        return S_OK

    ################################
    # IOleObject interface
    #
    # See also: http://spec.winprog.org/captcom/journal3/page2.html

    _clientsite = None

    def IOleObject_SetClientSite(self, this, ppClientSite):
        if ppClientSite:
            ppClientSite.AddRef()
            self._clientsite = ppClientSite
        else:
            self._clientsite = None
        return S_OK

    def IOleObject_SetHostNames(self, this, szContainerApp, szContainerObject):
        return S_OK

    _himetricExtent = 0, 0

    def IOleObject_SetExtent(self, this, dwDrawAspect, psizel):
        self._himetricExtent = psizel[0].cx, psizel[0].cy
        return S_OK

    def IOleObject_GetExtent(self, this, dwDrawAspect, psizel):
        psizel[0].cx, psizel[0].cy = self._himetricExtent
        return S_OK

    def IOleObject_GetMiscStatus(self, this, dwAspect, pdwStatus):
        pdwStatus[0] = 131073
        return S_OK

    def IOleObject_GetUserType(self, this, dwFormOfUserType, pszUserType):
        return ole32.OleRegGetUserType(byref(GUID(self._reg_clsid_)), dwFormOfUserType, pszUserType)

    _adviseholder = None

    def IOleObject_Advise(self, this, pAdvSink, pdwConnection):
        # IOleObject::Advise
        if pAdvSink:
            pAdvSink.AddRef()
        return self._adviseholder.Advise(pAdvSink, pdwConnection)

    def IOleObject_Unadvise(self, this, dwConnection):
        return self._adviseholder.Unadvise(dwConnection)

    def IOleObject_EnumAdvise(self, this, ppenumAdvise):
        return self._adviseholder.EnumAdvise(ppenumAdvise)

    def IOleObject_DoVerb(self, this, iVerb, lpmsg, pActiveSite, lindex, hwndParent, lprcPosRect):
        print "LOG: DoVerb %d" % iVerb
        if pActiveSite:
            pActiveSite.AddRef()
        if iVerb == OLEIVERB_PRIMARY and hasattr(self, "_DoVerbPrimary"):
            return self._DoVerbPrimary(lprcPosRect[0], hwndParent)
        if iVerb == OLEIVERB_SHOW and hasattr(self, "_DoVerbShow"):
            return self._DoVerbShow(lprcPosRect[0], hwndParent)
        if iVerb == OLEIVERB_INPLACEACTIVATE and hasattr(self, "_DoVerbInPlaceActivate"):
            return self._DoVerbInPlaceActivate(lprcPosRect[0], hwndParent)
        if iVerb == OLEIVERB_UIACTIVATE and hasattr(self, "_DoVerbUIActivate"):
            return self._DoVerbUIActivate(lprcPosRect[0], hwndParent)
        if iVerb == OLEIVERB_HIDE and hasattr(self, "_DoVerbHide"):
            return self._DoVerbHide(lprcPosRect[0], hwndParent)
        if iVerb == OLEIVERB_OPEN and hasattr(self, "_DoVerbOpen"):
            return self._DoVerbOpen(lprcPosRect[0], hwndParent)
        if iVerb == OLEIVERB_DISCARDUNDOSTATE and hasattr(self, "_DoVerbDiscardUndoState"):
            return self._DoVerbDiscardUndoState(lprcPosRect[0], hwndParent)
        if iVerb == OLEIVERB_PROPERTIES and hasattr(self, "_DoVerbProperties"):
            return self._DoVerbProperties(lprcPosRect[0], hwndParent)
        return E_NOTIMPL

    def IOleObject_EnumVerbs(self, this, ppEnumOleVerb):
        return OLEOBJ_E_NOVERBS
##        return ole32.OleRegEnumVerbs(byref(GUID(self._reg_clsid_)),
##                                     ppEnumOleVerb)

    def IOleObject_Update(self, this):
        return S_OK

    def IOleObject_IsUpToDate(self, this):
        return S_OK

    def IOleObject_Close(self, this, dwSaveOptions):
        if dwSaveOptions == OLECLOSE_SAVEIFDIRTY \
           or dwSaveOptions == OLECLOSE_PROMPTSAVE and self._dirty:
            print "CLOSE %s" % bool(self._clientsite)
            self._clientsite.SaveObject()
        if self._view_advisesink:
            self._view_advisesink.OnClose()
        self._adviseholder.SendOnClose()
        self._clientsite = None
        return S_OK

    def IOleObject_GetUserClassID(self, this, pClsid):
        # IOleObject::GetClassID
        return ole32.CLSIDFromString(unicode(self._reg_clsid_), pClsid)
    
    ################################
    # IOleWindow interface

    _hwnd = 0

##    def IOleWindow_GetWindow(self, this, phwnd):
    def IOleWindow_GetWindow(self, this, phwnd):
        phwnd[0] = self._hwnd
        return S_OK

    ################################
    # IOleInPlaceObject(IOleWindow) interface

    # The following has been helpful in creating this code:
    #
    # - stepping with a debugger through the ATL sources in the context
    #   of a MSVC6 atl wizard created control
    # - reading the ATL source code.
    #
    # - Kraig Brockschmidt's Inside OLE 2
    #   I still have the first edition on paper, but the second is more useful.
    #   It is on some old MSDN library CDs.
    #
    _inplace_active = False

    def IOleInPlaceObject_InPlaceDeactivate(self, this):
        # c:/vc98/ATL/include/ATLCTL.H 979
        print "InPlaceDeActivate"
        if not self._inplace_active:
            print "  ...not active"
            return S_OK
        # call UIDeactivate() ? 
        self._inplace_active = False
        if self._hwnd:
            print "Have Window Handle"
            if windll.user32.IsWindow(self._hwnd):
                print "DestroyWindow"
                windll.user32.DestroyWindow(self._hwnd)
                self._hwnd = 0
            else:
                print "IsWindow false"
        else:
            print "Have no Window"

        ips = POINTER(IOleInPlaceSite)()
        self._clientsite.QueryInterface(byref(IOleInPlaceSite._iid_), byref(ips))
        print "GOT InPlaceSite"
        ips.OnInPlaceDeactivate()

        return S_OK

    def IOleInPlaceObject_SetObjectRects(self, this, lprcPosRect, lprcClipRect):
        if not lprcPosRect or not lprcClipRect:
            return E_POINTER
        # From MSDN:

        # The coordinates are in pixels - this is different from other
        # stuff, where it is mostly in HIMETRIC.

        # The object must size its in-place window to match the
        # intersection of lprcPosRect and lprcClipRect. The object
        # must also draw its contents into the object's in-place
        # window so that proper clipping takes place.

        # The object should compare its width and height with those
        # provided by its container (conveyed through lprcPosRect). If
        # the comparison does not result in a match, the container is
        # applying scaling to the object. The object must then decide
        # whether it should continue the in-place editing in the
        # scale/zoom mode or deactivate.
        # <end quote>

        if self._hwnd:
            from ctypes.wintypes import RECT
            rcIXect = RECT()
            b = windll.user32.IntersectRect(byref(rcIXect), lprcPosRect, lprcClipRect)
            if b and not windll.user32.EqualRect(byref(rcIXect), lprcPosRect):
                raise "NOT YET IMPLEMENTED"
            windll.user32.SetWindowRgn(self._hwnd, None, True)
            SWP_NOZORDER        = 0x0004
            SWP_NOACTIVATE      = 0x0010
##            SWP_NOSIZE          = 0x0001
##            SWP_NOMOVE          = 0x0002
##            SWP_NOREDRAW        = 0x0008
##            SWP_FRAMECHANGED    = 0x0020
##            SWP_SHOWWINDOW      = 0x0040
##            SWP_HIDEWINDOW      = 0x0080
##            SWP_NOCOPYBITS      = 0x0100
##            SWP_NOOWNERZORDER   = 0x0200
##            SWP_NOSENDCHANGING  = 0x0400
##            SWP_DRAWFRAME       = SWP_FRAMECHANGED
##            SWP_NOREPOSITION    = SWP_NOOWNERZORDER
##            SWP_DEFERERASE      = 0x2000
##            SWP_ASYNCWINDOWPOS  = 0x4000
            windll.user32.SetWindowPos(self._hwnd, None,
                                       lprcPosRect[0].left,
                                       lprcPosRect[0].top,
                                       lprcPosRect[0].right - lprcPosRect[0].left,
                                       lprcPosRect[0].bottom - lprcPosRect[0].top,
                                       SWP_NOZORDER | SWP_NOACTIVATE)
        return S_OK

    def _DoVerbInPlaceActivate(self, rect, hwndParent):
        # c:/vc98/ATL/include/ATLCTL.H 1726
        if not self._clientsite:
            return S_OK

        ips = POINTER(IOleInPlaceSite)()
        self._clientsite.QueryInterface(byref(IOleInPlaceSite._iid_), byref(ips))
##        print "Got IOleInPlaceSite pointer"
        # c:/vc98/ATL/include/ATLCTL.H 798
        if not self._inplace_active:
            if S_OK != ips.CanInPlaceActivate():
                return E_FAIL
            ips.OnInPlaceActivate()

        self._inplace_active = True

        if self._hwnd:
            SW_SHOW = 5
            windll.user32.ShowWindow(self._hwnd, SW_SHOW)
            if windll.user32.IsChild(self._hwnd, windll.user32.GetFocus()):
                windll.user32.SetFocus(self._hwnd)
        else:
            self._CreateControlWindow(hwndParent, rect)

        # GetWindowContext() ?
        # SetObjectsRect() ?

        # gone active by now, take care of UIACTIVATE

        self._clientsite.ShowObject()

        return S_OK

    def _CreateControlWindow(self, hwndParent, rect):
        WS_CHILD   = 0x40000000
        WS_VISIBLE = 0x10000000
        win_id = 0
        self._hwnd = windll.user32.CreateWindowExA(
            0,
            "SCROLLBAR",
            "",
            WS_CHILD | WS_VISIBLE,
            rect.left,
            rect.top,
            rect.right - rect.left,
            rect.bottom - rect.top,
            hwndParent,
            win_id,
            None,
            0
            )
##        print "Window created %x %x" % (self._hwnd, hwndParent)
##        print "Rect is %d %d %d %d" % (rect.left, rect.top, rect.right, rect.bottom)

OLEIVERB_PRIMARY            = 0
OLEIVERB_SHOW               = -1
OLEIVERB_OPEN               = -2
OLEIVERB_HIDE               = -3
OLEIVERB_UIACTIVATE         = -4
OLEIVERB_INPLACEACTIVATE    = -5
OLEIVERB_DISCARDUNDOSTATE   = -6
OLEIVERB_PROPERTIES         = -7

OLEOBJ_E_NOVERBS = 0x80040180

OLECLOSE_SAVEIFDIRTY = 0
OLECLOSE_NOSAVE = 1
OLECLOSE_PROMPTSAVE = 2

"""
[3240] # unimplemented Freeze for interface IViewObject2 
[3240] # unimplemented Unfreeze for interface IViewObject2 

[3240] # unimplemented Save for interface IPersistPropertyBag 

[3240] # unimplemented GetClientSite for interface IOleObject 
[3240] # unimplemented SetMoniker for interface IOleObject 
[3240] # unimplemented GetMoniker for interface IOleObject 
[3240] # unimplemented InitFromData for interface IOleObject 
[3240] # unimplemented GetClipboardData for interface IOleObject 
[3240] # unimplemented SetColorScheme for interface IOleObject 

[3240] # unimplemented ContextSensitiveHelp for interface IOleInPlaceObject 
[3240] # unimplemented InPlaceDeactivate for interface IOleInPlaceObject 
[3240] # unimplemented UIDeactivate for interface IOleInPlaceObject 
[3240] # unimplemented ReactivateAndUndo for interface IOleInPlaceObject 
"""

if __name__ == '__main__':
    from ctypes.com.server import UseCommandLine
    UseCommandLine(StopliteObject)
