from ctypes import *
from ctypes.wintypes import BOOL
from ctypes.com import CreateInstance, GUID, ole32, IUnknown, \
     STDMETHOD, HRESULT, REFIID, COMObject
from ctypes.com.hresult import TYPE_E_ELEMENTNOTFOUND

class IMalloc(IUnknown):
    _iid_ = GUID("{00000002-0000-0000-C000-000000000046}")
    _methods_ = IUnknown._methods_ + [
        STDMETHOD(c_voidp, "Alloc", c_ulong),
        STDMETHOD(c_voidp, "Realloc", c_voidp, c_ulong),
        STDMETHOD(None, "Free", c_voidp),
        STDMETHOD(c_ulong, "GetSize", c_voidp),
        STDMETHOD(c_int, "DidAlloc", c_voidp),
        STDMETHOD(None, "HeapMinimize")]
        

class IMallocSpy(IUnknown):
    _iid_ = GUID("{0000001D-0000-0000-C000-000000000046}")
    _methods_ = IUnknown._methods_ + [
        STDMETHOD(c_ulong, "PreAlloc", c_ulong),
        STDMETHOD(c_voidp, "PostAlloc", c_voidp),
        STDMETHOD(c_voidp, "PreFree", c_voidp, BOOL),
        STDMETHOD(None, "PostFree", BOOL),
        STDMETHOD(c_ulong, "PreRealloc", c_voidp, c_ulong, POINTER(c_voidp), BOOL),
        STDMETHOD(c_voidp, "PostRealloc", c_voidp, BOOL),
        STDMETHOD(c_voidp, "PreGetSize", c_voidp, BOOL),
        STDMETHOD(c_ulong, "PostGetSize", c_ulong, BOOL),
        STDMETHOD(c_voidp, "PreDidAlloc", c_voidp, BOOL),
        STDMETHOD(c_int, "PostDidAlloc", c_voidp, BOOL, c_int),
        STDMETHOD(None, "PreHeapMinimize"),
        STDMETHOD(None, "PostHeapMinimize")]

class MallocSpy(COMObject):
    _com_interfaces_ = [IMallocSpy]

    def __init__(self):
        self.blocks = {}
        super(MallocSpy, self).__init__()

    def AddRef(self, this):
        self._refcnt += 1
        return self._refcnt

    def Release(self, this):
        self._refcnt -= 1
        return self._refcnt

    ################

    # keep track of allocated blocks and size
    def PreAlloc(self, this, cbRequest):
        self.cbRequest = cbRequest
        return cbRequest

    def PostAlloc(self, this, pActual):
        self.blocks[pActual] = self.cbRequest
        del self.cbRequest
        return pActual

    def PreFree(self, this, pRequest, fSpyed):
        if fSpyed:
            del self.blocks [pRequest]
        else:
            print "PreFree", pRequest, fSpyed
        return pRequest

    def PostFree(self, this, fSpyed):
        pass

    def PreGetSize(self, this, pRequest, fSpyed):
        return pRequest

    def PostGetSize(self, this, cbActual, fSpyed):
        return cbActual

    def PreRealloc(self, this, pRequest, cbRequest, ppNewRequest, fSpyed):
        return cbRequest

    def PostRealloc(self, this, pActual, fSpyed):
        return pActual

    def PreDidAlloc(self, this, pRequest, fSpyed):
        return pRequest

    def PostDidAlloc(self, this, pRequest, fSpyed, fActual):
        return fActual

    def PreHeapMinimize(self, this):
        pass

    def PostHeapMinimize(self, this):
        pass

    ################

    def active_blocks(self):
        return self.blocks

    def register(self):
        oledll.ole32.CoRegisterMallocSpy(byref(self._com_pointers_[0][1]))

    def revoke(self, warn=1):
        self.release_all(warn=warn)
        oledll.ole32.CoRevokeMallocSpy()

    def release_all(self, warn=1):
        active = self.active_blocks()
        if active:
            m = CoGetMalloc()
            if warn:
                print "%d Allocated Memory Blocks:" % len(active)
                for block, size in active.items():
                    didalloc = m.DidAlloc(c_voidp(block))
                    print "\t%d bytes at %08X" % (size, block), didalloc
            for block, size in active.items():
                m.Free(c_voidp(block))

def CoGetMalloc():
    m = POINTER(IMalloc)()
    ole32.CoGetMalloc(1, byref(m))
    return m

################################################################

if __name__ == "__main__":
    import ctypes.com
    from ctypes.com.automation import LoadTypeLib, BSTR

    def doit(n):
        tlb = LoadTypeLib(r"c:\windows\system32\shdocvw.dll")
        for i in xrange(-1, n):
            name = BSTR()
            doc = BSTR()
            help = BSTR()
            
            try:
                tlb.GetDocumentation(i, byref(name), byref(doc), None, byref(help))
            except WindowsError, detail:
                if detail.errno != TYPE_E_ELEMENTNOTFOUND:
                    raise
                break
##            print [name.value, doc.value]

    mallocspy = MallocSpy()
    mallocspy.register()

    try:
        doit(32000)
    except:
        import traceback
        traceback.print_exc()

    # Clear sys.exc_info(), in case there are COM objects left
    try: 1/0
    except: pass

    # Shutdown COM by calling CoUninitialize *now*.
    # See ctypes.com.__init__.py for details
    import ctypes.com
    ctypes.com.__cleaner = None
    
    mallocspy.revoke()
