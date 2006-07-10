import sys, re, os
from optparse import OptionParser
from ctypes_codegen.codegenerator import generate_code
from ctypes_codegen import typedesc

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
msvcrt
msimg32
netapi32
rpcrt4""".split()

##rpcndr
##ntdll

def main(argv=None):
    if argv is None:
        argv = sys.argv

    def windows_dlls(option, opt, value, parser):
        parser.values.dlls.extend(windows_dll_names)

    parser = OptionParser("usage: %prog xmlfile [options]")
    parser.add_option("-c",
                      action="store_true",
                      dest="generate_comments",
                      help="include source file location in comments",
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

    if os.name in ("ce", "win32"):
        default_modules = ["ctypes.wintypes", "ctypes" ]
    else:
        default_modules = ["ctypes" ]

    parser.add_option("-m",
                      dest="modules",
                      metavar="module",
                      help="Python module(s) containing symbols which will "
                      "be imported instead of generated",
                      action="append",
                      default=default_modules)

    options, files = parser.parse_args(argv[1:])

    if len(files) != 1:
        parser.error("Exactly one input file must be specified")

    if options.output == "-":
        stream = sys.stdout
    else:
        stream = open(options.output, "w")

    if options.expressions:
        options.expressions = map(re.compile, options.expressions)

    if options.generate_comments:
        stream.write("# generated by 'xml2py'\n")
        stream.write("# flags '%s'\n" % " ".join(argv[1:]))

    known_symbols = {}

    from ctypes import CDLL
    from ctypes.util import find_library

    def load_library(name):
        path = find_library(name)
        if path is None:
            raise RuntimeError("Library '%s' not found" % name)
        return CDLL(path)

    dlls = [load_library(name) for name in options.dlls]

    for name in options.modules:
        mod = __import__(name)
        for submodule in name.split(".")[1:]:
            mod = getattr(mod, submodule)
        for name, item in mod.__dict__.iteritems():
            if isinstance(item, type):
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

    generate_code(files[0], stream,
                  symbols=options.symbols,
                  expressions=options.expressions,
                  verbose=options.verbose,
                  generate_comments=options.generate_comments,
                  known_symbols=known_symbols,
                  searched_dlls=dlls,
                  types=options.kind)


if __name__ == "__main__":
    sys.exit(main())
