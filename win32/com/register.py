from ctypes.com.server import CLSCTX_LOCAL_SERVER, CLSCTX_INPROC_SERVER
import _winreg, sys, imp

################################################################
# Registration
#
# COMObject attributes for registration:
#
# _reg_clsid_ - required string
# _reg_progid_ - optional (?) string
# _reg_desc_ - optional string
# _reg_clsctx_ - optional REGCLS_CTX* constants
#
# _typelib_ - optional object, which must have a 'path' attribute
#
# If registration is run from a frozen executable (imp.is_frozen("__main__") is true),
# then the _typelib_ attribute is ignored, and a typelib resource in sys.executable
# is used instead.

def is_frozen():
    return hasattr(sys, "importers") or imp.is_frozen("__main__")

def _register(cls):
    h = _winreg.CreateKey(_winreg.HKEY_CLASSES_ROOT, "CLSID\\%s" % cls._reg_clsid_)
    name = "CLSID\\%s" % cls._reg_clsid_

    if not hasattr(cls, "_reg_clsctx_") or cls._reg_clsctx_ & CLSCTX_LOCAL_SERVER:
        if is_frozen():
            value = sys.executable
        else:
            import os
            value = "%s %s" % \
                    (sys.executable, os.path.abspath(sys.argv[0]))
        print "LocalServer32", value
        _winreg.SetValue(h, "LocalServer32", _winreg.REG_SZ, value)

    if hasattr(cls, "_reg_progid_"):

        _winreg.SetValue(_winreg.HKEY_CLASSES_ROOT, "AppID\\%s" % cls._reg_clsid_,
                         _winreg.REG_SZ,
                         cls._reg_progid_)

        _winreg.SetValue(h, "ProgID",
                         _winreg.REG_SZ,
                         cls._reg_progid_)
        
        desc = getattr(cls, "_reg_desc_", cls._reg_progid_)
        _winreg.SetValue(_winreg.HKEY_CLASSES_ROOT, cls._reg_progid_,
                         _winreg.REG_SZ,
                         desc)

        _winreg.SetValue(h, "",
                         _winreg.REG_SZ,
                         desc)

        _winreg.SetValue(_winreg.HKEY_CLASSES_ROOT, "%s\\CLSID" % cls._reg_progid_,
                         _winreg.REG_SZ,
                         cls._reg_clsid_)

    if hasattr(cls, "_typelib_") and not is_frozen():
        from ctypes.com.automation import REGKIND_REGISTER, LoadTypeLibEx
        import os
        path = os.path.abspath(cls._typelib_.path)
        try:
            LoadTypeLibEx(path, REGKIND_REGISTER)
            print "Registered Typelib", path
        except:
            import traceback
            traceback.print_exc()
        
    print "Registered COM class", cls


def register(*classes):
    for cls in classes:
        _register(cls)
    register_typelib()
    
def register_typelib():
    if is_frozen():
        from ctypes.com.automation import REGKIND_REGISTER, LoadTypeLibEx
        try:
            LoadTypeLibEx(sys.executable, REGKIND_REGISTER)
            print "Registered Typelib", sys.executable
        except:
            import traceback
            traceback.print_exc()

def unregister_typelib():
    if is_frozen():
        from ctypes.com.automation import REGKIND_REGISTER, LoadTypeLibEx, TLIBATTR, oleaut32
        from ctypes.com import GUID
        from ctypes import byref, POINTER
        try:
            tlib = LoadTypeLibEx(sys.executable, REGKIND_REGISTER)
            pta = POINTER(TLIBATTR)()
            tlib.GetLibAttr(byref(pta))
            ta = pta.contents
            libid = str(ta.guid)
            lcid = ta.lcid
            syskind = ta.syskind
            wMajorVerNum = ta.wMajorVerNum
            wMinorVerNum = ta.wMinorVerNum
            tlib.ReleaseTLibAttr(pta)

            oleaut32.UnRegisterTypeLib(byref(GUID(libid)), wMajorVerNum,
                                       wMinorVerNum, lcid, syskind)
            print "Unregistered Typelib", libid, (wMajorVerNum, wMinorVerNum)
        except:
            import traceback
            traceback.print_exc()

REG_KEYS = "LocalServer32 InprocServer32 PythonClass PythonPath Control MiscStatus ProgID".split()

def _unregister(cls):
    unregister_typelib()

    if hasattr(cls, "_typelib_") and not is_frozen():
        from ctypes import byref
        from ctypes.com.automation import oleaut32
        SYS_WIN32 = 1
        tlib = cls._typelib_
        oleaut32.UnRegisterTypeLib(byref(tlib.guid),
                                   tlib.version[0],
                                   tlib.version[1],
                                   0, # XXX lcid
                                   SYS_WIN32)
    try:
        h = _winreg.OpenKey(_winreg.HKEY_CLASSES_ROOT, "CLSID\\%s" % cls._reg_clsid_)
    except WindowsError, detail:
        if detail.errno == 2:
            return

    for name in REG_KEYS:
        try:
            _winreg.DeleteKey(h, name)
            print "deleted", name
        except WindowsError, detail:
            if detail.errno != 2:
                raise

    _winreg.DeleteKey(h, "")

    h = _winreg.OpenKey(_winreg.HKEY_CLASSES_ROOT, "AppID")
    _winreg.DeleteKey(h, cls._reg_clsid_)

##    h = _winreg.OpenKey(_winreg.HKEY_CLASSES_ROOT, "%s\\CLSID" % cls._reg_progid_)
##    _winreg.DeleteKey(h, cls._reg_clsid_)

def unregister(*classes):
    for cls in classes:
        _unregister(cls)
