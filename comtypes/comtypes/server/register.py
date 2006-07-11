"""comtypes.server.register - register and unregister a COM object.

Exports the UseCommandLine function.  UseCommandLine is called with
the COM object classes that a module exposes.  It parses the Windows
command line and takes the appropriate actions.
These command line options are supported:

/regserver - register the classes with COM.
/unregserver - unregister the classes with COM.

/nodebug - remove all logging configuration from the registry.

/l <name>=<level> - configure the logging level for the standard Python loggind module,
this option may be used several times.

/f <formatter> - specify the formatter string.

Note: Registering and unregistering the objects does remove logging
entries.  Configuring the logging does not change other registry
entries, so it is possible to freeze a comobject with py2exe, register
it, then configure logging afterwards to debug it, and delete the
logging config afterwards.

Sample usage:

Register the COM object:

  python mycomobj.py /regserver

Configure logging info:

  python mycomobj.py /l comtypes=INFO /l comtypes.server=DEBUG /f %(message)s

Now, debug the object, and when done delete logging info:

  python mycomobj.py /nodebug
"""
import sys, os
import _winreg
import logging

import comtypes
from comtypes.typeinfo import LoadTypeLibEx, UnRegisterTypeLib, REGKIND_REGISTER
from comtypes.hresult import *
from comtypes.server import w_getopt
from ctypes import windll, c_ulong, c_wchar_p, WinError, sizeof, create_string_buffer

_debug = logging.getLogger(__name__).debug

# a SHDeleteKey function, will remove a registry key with all subkeys.
def _non_zero(retval, func, args):
    if retval:
        raise WinError(retval)
SHDeleteKey = windll.shlwapi.SHDeleteKeyW
SHDeleteKey.errcheck = _non_zero
SHDeleteKey.argtypes = c_ulong, c_wchar_p

try:
    Set = set
except NameError:
    from sets import Set #as set


_KEYS = {_winreg.HKEY_CLASSES_ROOT: "HKCR",
         _winreg.HKEY_LOCAL_MACHINE: "HKLM",
         _winreg.HKEY_CURRENT_USER: "HKCU"}

def _explain(hkey):
    return _KEYS.get(hkey, hkey)

class Registrar(object):

    def nodebug(self, cls):
        """Delete logging entries from the registry."""
        clsid = cls._reg_clsid_
        try:
            _debug('DeleteKey( %s\\CLSID\\%s\\Logging"' % \
                    (_explain(_winreg.HKEY_CLASSES_ROOT), clsid))
            hkey = _winreg.OpenKey(_winreg.HKEY_CLASSES_ROOT, r"CLSID\%s" % clsid)
            _winreg.DeleteKey(hkey, "Logging")
        except WindowsError, detail:
            if detail.errno != 2:
                raise

    def debug(self, cls, levels, format):
        """Write entries in the registry to setup logging for this clsid."""
        # handlers
        # format
        clsid = cls._reg_clsid_
        _debug('CreateKey( %s\\CLSID\\%s\\Logging"' % \
                (_explain(_winreg.HKEY_CLASSES_ROOT), clsid))
        hkey = _winreg.CreateKey(_winreg.HKEY_CLASSES_ROOT, r"CLSID\%s\Logging" % clsid)
        for item in levels:
            name, value = item.split("=")
            v = getattr(logging, value)
            assert isinstance(v, int)
        _debug('SetValueEx(levels, %s)' % levels)
        _winreg.SetValueEx(hkey, "levels", None, _winreg.REG_MULTI_SZ, levels)
        if format:
            _debug('SetValueEx(format, %s)' % format)
            _winreg.SetValueEx(hkey, "format", None, _winreg.REG_SZ, format)
        else:
            _debug('DeleteValue(format)')
            try:
                _winreg.DeleteValue(hkey, "format")
            except WindowsError, detail:
                if detail.errno != 2:
                    raise

    def register(self, cls):
        """Register the COM server class."""
        # First, we unregister the object with force=True, to force removal
        # of all registry entries, even if we would not write them.
        # Second, we create new entries.
        # It seems ATL does the same.
        self.unregister(cls, force=True)
        table = self._registry_entries(cls)
        table.sort()
        _debug("Registering %s", cls)
        for hkey, subkey, valuename, value in table:
            _debug ('[%s\\%s]', _explain(hkey), subkey)
            _debug('%s="%s"', valuename or "@", value)
            k = _winreg.CreateKey(hkey, subkey)
            _winreg.SetValueEx(k, valuename, None, _winreg.REG_SZ, str(value))

        tlib = getattr(cls, "_reg_typelib_", None)
        if tlib is not None:
            if hasattr(sys, "frozendllhandle"):
                dll = self._get_serverdll()
                _debug("LoadTypeLibEx(%s, REGKIND_REGISTER)", dll)
                LoadTypeLibEx(dll, REGKIND_REGISTER)
            else:
                path = cls._typelib_path_
                _debug("LoadTypeLibEx(%s, REGKIND_REGISTER)", path)
                LoadTypeLibEx(path, REGKIND_REGISTER)
        _debug("Done")

    def unregister(self, cls, force=False):
        """Unregister the COM server class."""
        # If force==False, we only remove those entries that we
        # actually would have written.  It seems ATL does the same.
        table = [t[:2] for t in self._registry_entries(cls)]
        # only unique entries
        table = list(set(table))
        table.sort()
        table.reverse()
        _debug("Unregister %s", cls)
        for hkey, subkey in table:
            try:
                if force:
                    _debug("SHDeleteKey %s\\%s", _explain(hkey), subkey)
                    SHDeleteKey(hkey, subkey)
                else:
                    _debug("DeleteKey %s\\%s", _explain(hkey), subkey)
                    _winreg.DeleteKey(hkey, subkey)
            except WindowsError, detail:
                if detail.errno != 2:
                    raise
        tlib = getattr(cls, "_reg_typelib_", None)
        if tlib is not None:
            try:
                _debug("UnRegisterTypeLib(%s, %s, %s)", *tlib)
                UnRegisterTypeLib(*tlib)
            except WindowsError, detail:
                if not detail.errno in (TYPE_E_REGISTRYACCESS, TYPE_E_CANTLOADLIBRARY):
                    raise
        _debug("Done")

    def _get_serverdll(self):
        """Return the pathname of the dll hosting the COM object."""
        handle = getattr(sys, "frozendllhandle", None)
        if handle is not None:
            buf = create_string_buffer(260)
            windll.kernel32.GetModuleFileNameA(handle, buf, sizeof(buf))
            return buf[:]
        import _ctypes
        return _ctypes.__file__

    def _get_full_classname(self, cls):
        """Return <modulename>.<classname> for 'cls'."""
        modname = cls.__module__
        if modname == "__main__":
            modname = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        return "%s.%s" % (modname, cls.__name__)

    def _get_pythonpath(self, cls):
        """Return the filesystem path of the module containing 'cls'."""
        modname = cls.__module__
        dirname = os.path.dirname(sys.modules[modname].__file__)
        return os.path.abspath(dirname)

    def _registry_entries(self, cls):
        """Return a sequence of tuples containing registry entries.

        The tuples must be (key, subkey, name, value).

        Required entries:
        =================
        _reg_clsid_ - a string or GUID instance
        _reg_clsctx_ - server type(s) to register

        Optional entries:
        =================
        _reg_desc_ - a string
        _reg_progid_ - a string naming the progid, typically 'MyServer.MyObject.1'
        _reg_novers_progid_ - version independend progid, typically 'MyServer.MyObject'
        _reg_typelib_ - an tuple (libid, majorversion, minorversion) specifying a typelib.
        _reg_threading_ - a string specifying the threading model

        Note that the first part of the progid string is typically the
        IDL library name of the type library containing the coclass.
        """
        HKCR = _winreg.HKEY_CLASSES_ROOT

        # table format: rootkey, subkey, valuename, value
        table = []
        append = lambda *args: table.append(args)

        # basic entry - names the comobject
        reg_clsid = str(cls._reg_clsid_) # that's the only required attribute for registration
        reg_desc = getattr(cls, "_reg_desc_", "")
        append(HKCR, "CLSID\\%s" % reg_clsid, "", reg_desc)

        reg_progid = getattr(cls, "_reg_progid_", None)
        if reg_progid:
            # for ProgIDFromCLSID:
            append(HKCR, "CLSID\\%s\\ProgID" % reg_clsid, "", reg_progid) # 1

            # for CLSIDFromProgID
            if reg_desc:
                append(HKCR, reg_progid, "", reg_desc) # 2
            append(HKCR, "%s\\CLSID" % reg_progid, "", reg_clsid) # 3

            reg_novers_progid = getattr(cls, "_reg_novers_progid_", None)
            if reg_novers_progid:
                append(HKCR, "CLSID\\%s\\VersionIndependendProgID" % reg_clsid, # 1a
                       "", reg_novers_progid)
                if reg_desc:
                    append(HKCR, reg_novers_progid, "", reg_desc) # 2a
                append(HKCR, "%s\\CurVer" % reg_novers_progid, "", reg_progid) #
                append(HKCR, "%s\\CLSID" % reg_novers_progid, "", reg_clsid) # 3a

        clsctx = getattr(cls, "_reg_clsctx_", 0)

        if clsctx & comtypes.CLSCTX_LOCAL_SERVER and not hasattr(sys, "frozendllhandle"):
            exe = sys.executable
            script = __import__(cls.__module__).__file__
            if " " in exe:
                exe = '"%s"' % exe
            if " " in script:
                script = '"%s"' % script
            append(HKCR, "CLSID\\%s\\LocalServer32" % reg_clsid, "", "%s %s" % (exe, script))

        if clsctx & comtypes.CLSCTX_INPROC_SERVER:
            append(HKCR, "CLSID\\%s\\InprocServer32" % reg_clsid,
                   "", self._get_serverdll())
            # only for inproc servers
            append(HKCR, "CLSID\\%s\\InprocServer32" % reg_clsid,
                   "PythonClass", self._get_full_classname(cls))
            # only for non-frozen inproc servers the PythonPath is needed.
            if not hasattr(sys, "frozendllhandle"):
                append(HKCR, "CLSID\\%s\\InprocServer32" % reg_clsid,
                       "PythonPath", self._get_pythonpath(cls))

            reg_threading = getattr(cls, "_reg_threading_", None)
            if reg_threading is not None:
                append(HKCR, "CLSID\\%s\\InprocServer32" % reg_clsid,
                       "ThreadingModel", reg_threading)

        reg_tlib = getattr(cls, "_reg_typelib_", None)
        if reg_tlib is not None:
            append(HKCR, "CLSID\\%s\\Typelib" % reg_clsid, "", reg_tlib[0])

        return table

################################################################

def register(cls):
    Registrar().register(cls)

def unregister(cls):
    Registrar().unregister(cls)

def UseCommandLine(*classes):
    usage = """Usage: %s [-regserver] [-unregserver] [-nodebug] [-f logformat] [-l loggername=level]""" % sys.argv[0]
    opts, args = w_getopt.w_getopt(sys.argv[1:],
                                   "regserver unregserver embedding l: f: nodebug")
    if not opts:
        sys.stderr.write(usage)
        return 0 # nothing for us to do

    levels = []
    format = None
    nodebug = False
    runit = False
    for option, value in opts:
        if option == "regserver":
            for cls in classes:
                register(cls)
        elif option == "unregserver":
            for cls in classes:
                unregister(cls)
        elif option == "embedding":
            runit = True
        elif option == "f":
            format = value
        elif option == "l":
            levels.append(value)
        elif option == "nodebug":
            nodebug = True

    if levels or format is not None:
        for cls in classes:
            Registrar().debug(cls, levels, format)
    if nodebug:
        for cls in classes:
            Registrar().nodebug(cls)

    if runit:
        import comtypes.server.localserver
        comtypes.server.localserver.run(classes)

    return 1 # we have done something

if __name__ == "__main__":
    UseCommandLine()