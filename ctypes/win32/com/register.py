import _winreg, sys, imp, os
from ctypes import byref, POINTER
from ctypes.com import GUID, CLSCTX_LOCAL_SERVER, CLSCTX_INPROC_SERVER
from ctypes.com.automation import REGKIND_REGISTER, LoadTypeLibEx, TLIBATTR, oleaut32

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
# If registration is run from a frozen executable then the _typelib_
# attribute is ignored, and a typelib resource in sys.executable is
# used instead.

def main_is_frozen():
    return (hasattr(sys, "importers") # py2exe
            or imp.is_frozen("__main__") # tools/freeze
            or hasattr(sys, "frozen") # McMillan installer
            )

class Registrar(object):
    """Registrar registers or unregisters a COM coclass in the registry.

    It can be extended by overriding the build_table method.
    """
    _reg_progid_ = None
    _reg_clsctx_ = CLSCTX_LOCAL_SERVER | CLSCTX_INPROC_SERVER
    
    def __init__(self, cls):
        self._cls = cls
        self._reg_clsid_ = cls._reg_clsid_
        if hasattr(cls, "_reg_progid_"):
            self._reg_progid_ = cls._reg_progid_
        self._reg_desc_ = getattr(cls, "_reg_desc_", self._reg_progid_)
        self._reg_clsctx_ = getattr(cls, "_reg_clsctx_", self._reg_clsctx_)

    def build_table(self):
        """Return a sequence of tuples containing registry entries.

        The tuples must be (key, subkey, name, value).
        """
        HKCR = _winreg.HKEY_CLASSES_ROOT

        # rootkey, subkey, valuename, value
        table = [(HKCR, "CLSID\\%s" % self._reg_clsid_, "", self._reg_desc_),
                 (HKCR, "CLSID\\%s\\ProgID" % self._reg_clsid_, "", self._reg_progid_),
                 (HKCR, "AppID\\%s" % self._reg_clsid_, "", self._reg_progid_),
                 (HKCR, "%s\\CLSID" % self._reg_progid_, "", self._reg_clsid_),
                 (HKCR, self._reg_progid_, "", self._reg_desc_),
                 ]

        if not main_is_frozen() and self._reg_clsctx_ & CLSCTX_INPROC_SERVER:
            import _ctypes
            modname = self._cls.__module__
            if modname == "__main__":
                modname = os.path.splitext(os.path.basename(sys.argv[0]))[0]
                path = os.path.abspath(os.path.dirname(sys.argv[0]))
            else:
                mod = sys.modules[self._cls.__module__]
                path = os.path.abspath(os.path.dirname(mod.__file__))

            classname = "%s.%s" % (modname, self._cls.__name__)
            e = [(HKCR, "CLSID\\%s\\InprocServer32" % self._reg_clsid_, "PythonClass", classname),
                 (HKCR, "CLSID\\%s\\InprocServer32" % self._reg_clsid_, "PythonPath", path),
                 (HKCR, "CLSID\\%s\\InprocServer32" % self._reg_clsid_, "", _ctypes.__file__),
##                 (HKCR, "CLSID\\%s\\InprocServer32" % self._reg_clsid_, "ThreadingModel", "Both")
                 ]
            
            table.extend(e)
            
        if self._reg_clsctx_ & CLSCTX_LOCAL_SERVER:
            if main_is_frozen():
                exe = sys.executable
            else:
                # Or pythonw.exe?
                exe = '%s "%s"' % (sys.executable, os.path.abspath(sys.argv[0]))
            table.append((HKCR, "CLSID\\%s\\LocalServer32" % self._reg_clsid_, "", exe))
                 
        return table

    def unregister(self):
        table = self.build_table()
        table.sort()
        table.reverse() # so the "deepest" entries come first
        for root, key, name, value in table:
            try:
                _winreg.DeleteKey(root, key)
            except WindowsError, detail:
                if detail.errno != 2:
                    raise
        if hasattr(self._cls, "_typelib_"):
            if main_is_frozen():
                unregister_typelib(sys.executable)
            else:
                lib = self._cls._typelib_
                unregister_typelib(lib.path)

    def register(self):
        table = self.build_table()
        table.sort() # so the "deepest" entries come last
        for root, key, name, value in table:
            if key:
                handle = _winreg.CreateKey(root, key)
            else:
                handle = root
            _winreg.SetValueEx(handle, name, None, _winreg.REG_SZ, value)
        if hasattr(self._cls, "_typelib_"):
            if main_is_frozen():
                register_typelib(sys.executable)
            else:
                lib = self._cls._typelib_
                register_typelib(lib.path)

def register_typelib(path):
    try:
        LoadTypeLibEx(path, REGKIND_REGISTER)
##        print "Registered Typelib", path
    except:
        import traceback
        traceback.print_exc()

def unregister_typelib(path):
    try:
        tlib = LoadTypeLibEx(path, REGKIND_REGISTER)
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
##        print "Unregistered Typelib", libid, (wMajorVerNum, wMinorVerNum)
    except:
        import traceback
        traceback.print_exc()

def register(*classes):
    for cls in classes:
        cls._get_registrar().register()
    
def unregister(*classes):
    for cls in classes:
        cls._get_registrar().unregister()

if __debug__:
    if __name__ == '__main__':
        sys.path.insert(0, "samples\\server")
        import sum, ctypes.com.server
        ctypes.com.server.UseCommandLine(sum.SumObject)
