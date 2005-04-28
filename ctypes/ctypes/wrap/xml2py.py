import sys, re, os, tempfile, errno
from optparse import OptionParser
import typedesc
from ctypes import CDLL, cast, c_void_p

# Hm, is it better to catch ImportError here, or should we protect this by
# if os.name == *posix" ?
try:
    from _ctypes import dlname, dladdr
except ImportError:
    # dlname and dladdr not available, hopefully also unneeded.
    pass

try:
    set
except NameError:
    from sets import Set as set

################################################################
windows_dll_names = """\
imagehlp
user32
kernel32
gdi32
advapi32
oleaut32
ole32
imm32
comdlg32
shell32
version
winmm
mpr
winscard
winspool.drv
urlmon
crypt32
cryptnet
ws2_32
opengl32
glu32
mswsock
msimg32
netapi32
rpcrt4""".split()

##msvcrt
##rpcndr
##ntdll

def fatalerror(msg):
    "Print an error message and exit the program"
    print >>sys.stderr, 'Error:', msg
    sys.exit(1)


class LibraryDescBase(object):
    """Provides symbol lookup and attributes of a shared library.

    The shared library is loaded from the supplied path.

    Public instance variables:

     name:    name of the shared library (e.g. for the linker option -l)
     version: major version of the shared library (e.g. the 2 in libA.so.2)
     key:     a unique key, created from name, which is a legal python identifier
     path:    file path as recorded by the runtime loader (this is only used
              by LibraryList for Posix systems)

    public methods:

     lookup()

    """

    def __init__(self, path):
        self.lib = CDLL(path)

    def lookup(self, symbol):
        "return a ctypes function or None"
        try:
            return getattr(self.lib, symbol)
        except AttributeError:
            return None

    def make_legal_identifier(self, name):
        name = re.sub('[^a-zA-Z0-9_]','_', name)
        if re.match('[0-9]', name):
            name = 'lib' + name
        return name


class LibraryListBase(object):
    """List of shared libraries (instances of LibraryDescBase)

    Public methods:

    which()
    """
    
    def __init__(self, names, searchpaths, verbose=False):
        """Loads the libraries

        names:       list of shared library names (as in the linker option -l)
        searchpaths: list of library search paths (linker option -L)
        verbose:     give a verbose message in case of error
        """
        pass

    def which(self, func):
        """return the dll (instance of LibraryDescBase) in which func is defined
        If func is not defined in any dll, return None.
        """
        raise NotImplementedError


if os.name == "posix":

    class LibraryDescPosix(LibraryDescBase):

        def __init__(self, path):
            LibraryDescBase.__init__(self, path)
            self.name, self.version = self.get_name_version(path)
            self.key = self.make_legal_identifier(self.name)
            self.path = self.normalize_path(path)

        def get_soname(self, path):
            import re, os
            cmd = "objdump -p -j .dynamic " + path
            res = re.search(r'\sSONAME\s+([^\s]+)', os.popen(cmd).read())
            if not res:
                raise ValueError("no soname found for shared lib '%s'" % path)
            return res.group(1)

        def get_name_version(self, path):
            soname = self.get_soname(path)
            m = re.match(r'lib(?P<name>[^.]+)\.so(\.(?P<version>.*))?', soname)
            if not m:
                raise ValueError(
                    "soname of form lib<name>.so.<version> expected, got '%s'" % soname)
            return m.group('name'), m.group('version')

        def normalize_path(self, path):
            "return the file path of the shared library as recorded by the runtime loader"
            return dlname(self.lib._handle)


    class LibraryListPosix(LibraryListBase):

        def __init__(self, names, searchpaths, verbose=False):
            if not names:
                self.dlls = []
            else:
                paths = self.findLibraryPaths(names, searchpaths, verbose)
                self.dlls = [LibraryDescPosix(path) for path in paths]
            self.lookup_dlls = dict([(d.path, d) for d in self.dlls])

        def which(self, func):
            name = func.name
            for dll in self.dlls:
                f = dll.lookup(name)
                if f is None:
                    continue
                address = cast(f, c_void_p).value
                path = dladdr(address)
                return self.lookup_dlls.get(path)
            return None

        def findLibraryPaths(self, names, searchpaths, verbose):
            stubneeded = True # sometimes needed on platforms like IRIX to
                              # find all libraries; not needed on Linux
            exprlist = [(name, re.compile('[^\(\)\s]*lib%s\.[^\(\)\s]*' % name))
                        for name in names]
            cc=('cc','gcc')[os.system('gcc --version > /dev/null 2> /dev/null')==0]
            if stubneeded:
                stubfile = tempfile.NamedTemporaryFile(suffix='.c')
                stubfile.write('int main(void) { return 0L; }\n')
                stubfile.flush()
                stub = stubfile.name
            else:
                stub = ''
            try:
                # outfile = /dev/null works, but if someone is stupid
                # enough to start this as root he might be missing
                # /dev/null later...
                fdout, outfile =  tempfile.mkstemp()
                cmd = '%s %s -o %s -Wl,-t %s %s 2>&1' % (
                    cc, stub, outfile,
                    ' '.join(['-L%s' % path for path in searchpaths]),
                    ' '.join(['-l%s' % name for name in names]))
                fd = os.popen(cmd)
                trace = fd.read()
                err = fd.close()
            finally:
                try:
                    os.unlink(outfile)
                except OSError, e:
                    if e.errno != errno.ENOENT:
                        raise
            paths = []
            for name, expr in exprlist:
                m = expr.search(trace)
                if m:
                    names.remove(name)
                    paths.append(m.group(0))
            if err and verbose:
                if err >= 256:
                    err /= 256
                s = 'error in command (exitcode %d):\n%s' % (res, cmd)
                if trace:
                    s += '\noutput:\n' + trace
                fatalerror(s)
            if names:
                fatalerror('shared library not found: %s' % names[0])
            return paths

    LibraryList = LibraryListPosix

if os.name == "nt":

    class LibraryDescNT(LibraryDescBase):

        def __init__(self, path):
            LibraryDescBase.__init__(self, path)
            self.name, self.version = self.get_name_version(path)
            self.key = self.make_legal_identifier(self.name)

        def get_name_version(self, path):
            # There are no consistent naming conventions for dll
            # versions on windows.  Which is the reason for dllhell.
            #
            # Some patterns are:
            #
            # Append a D for the debug version (MSVCR71.DLL - MSVR71D.DLL)
            # Version number part of the filename: MFC42.DLL - MFC71.DLL
            # But: MSVCRT.DLL MSVCR71.DLL
            # U suffix for unicode? MFC42.DLL MFC42U.DLL
            # locale suffix: MFC71DEU.DLL
            #
            # Here are some more MFC71 versions from my system:
            # MFC71.DLL
            # MFC71CHS.DLL
            # MFC71CHT.DLL
            # MFC71D.DLL
            # MFC71DEU.DLL
            # MFC71ENU.DLL
            # MFC71ESP.DLL
            # MFC71FRA.DLL
            # MFC71ITA.DLL
            # MFC71JPN.DLL
            # MFC71KOR.DLL
            # MFC71U.DLL
            # MFC71UD.DLL
            dllname = self.get_soname(path)
            return dllname, ""

        def get_soname(self, path):
            # Should it strip the extension, if '.dll'?
            # Should it strip the directory part? Probably...
            return os.path.basename(path)

    class LibraryListNT(LibraryListBase):

        def __init__(self, names, searchpaths, verbose=False):
            self.dlls = [LibraryDescNT(name) for name in names]

        def which(self, func):
            name = func.name
            for dll in self.dlls:
                if dll.lookup(name) is not None:
                    return dll
            return None

    LibraryList = LibraryListNT


def remove_dups(seq):
    "remove duplicate entries from a sequence and return a list"
    s = set()
    l = []
    for i in seq:
        if i in s:
            continue
        s.add(i)
        l.append(i)
    return l
    

def main(args=None):
    if args is None:
        args = sys.argv

    def windows_dlls(option, opt, value, parser):
        parser.values.dlls.extend(windows_dll_names)

    parser = OptionParser("usage: %prog xmlfile [options]")
    parser.add_option("-d",
                      action="store_true",
                      dest="use_decorators",
                      help="use Python 2.4 function decorators",
                      default=False)

    parser.add_option("-k",
                      action="store",
                      dest="kind",
                      help="kind of type descriptions to include: "
                      "d = #defines, "
                      "e = enumerations, "
                      "f = functions, "
                      "s = structures, "
                      "t = typedefs",
                      metavar="TYPEKIND",
                      default=None)

    parser.add_option("-l",
                      dest="dlls",
                      help="libraries to search for exported functions",
                      action="append",
                      default=[])

    parser.add_option("-L",
                      dest="searchpaths",
                      metavar="DIR",
                      help="Add directory dir to the list of"
                      " directories to be searched for -l",
                      action="append",
                      default=[])

    parser.add_option("-o",
                      dest="output",
                      help="output filename (if not specified, standard output will be used)",
                      default="-")

    parser.add_option("-r",
                      dest="expressions",
                      metavar="EXPRESSION",
                      action="append",
                      help="regular expression for symbols to include "
                      "(if neither symbols nor expressions are specified,"
                      "everything will be included)",
                      default=None)

    parser.add_option("-s",
                      dest="symbols",
                      metavar="SYMBOL",
                      action="append",
                      help="symbol to include "
                      "(if neither symbols nor expressions are specified,"
                      "everything will be included)",
                      default=None)

    parser.add_option("-v",
                      action="store_true",
                      dest="verbose",
                      help="verbose output",
                      default=False)

    parser.add_option("-w",
                      action="callback",
                      callback=windows_dlls,
                      help="add all standard windows dlls to the searched dlls list")

    parser.add_option("-m",
                      dest="modules",
                      metavar="module",
                      help="Python module(s) containing symbols which will "
                      "be imported instead of generated (ctypes is always used)",
                      action="append",
                      default=["ctypes"])

    options, files = parser.parse_args(args[1:])

    if len(files) != 1:
        parser.error("Exactly one input file must be specified")

    if options.output == "-":
        stream = sys.stdout
    else:
        stream = open(options.output, "w")

    if options.expressions:
        options.expressions = map(re.compile, options.expressions)

    ################################################################

    dlls = LibraryList(remove_dups(options.dlls), options.searchpaths)

    known_symbols = {}
    for name in options.modules:
        mod = __import__(name)
        for submodule in name.split(".")[1:]:
            mod = getattr(mod, submodule)
        for name in mod.__dict__:
            known_symbols[name] = mod.__name__

    if options.kind:
        types = []
        for char in options.kind:
            typ = {"a": [typedesc.Alias],
                   "d": [typedesc.Variable],
                   "e": [typedesc.Enumeration, typedesc.EnumValue],
                   "f": [typedesc.Function],
                   "m": [typedesc.Macro],
                   "s": [typedesc.Structure],
                   "t": [typedesc.Typedef],
                   }[char]
            types.extend(typ)
        options.kind = tuple(types)

    from gccxmlparser import parse
    items = parse(files[0])

    stream.write("# generated by 'xml2py'\n")
    stream.write("# flags '%s'\n" % " ".join(sys.argv[1:]))

    from codegenerator import Generator
    gen = Generator(stream,
                    use_decorators=options.use_decorators,
                    known_symbols=known_symbols,
                    searched_dlls=dlls)

    gen.generate_code(items,
                      verbose=options.verbose,
                      symbols=options.symbols,
                      expressions=options.expressions,
                      types=options.kind)
                    
if __name__ == "__main__":
    sys.exit(main())
