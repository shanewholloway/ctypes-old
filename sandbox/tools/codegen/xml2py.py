# bugs:
# packing of structures/unions with bitfields? See '##XXX FIXME'
import sys, re
from optparse import OptionParser
from codegenerator import generate_code

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
##glut32

##rpcndr
##ntdll

def main(args=None):
    if args is None:
        args = sys.argv

    def windows_dlls(option, opt, value, parser):
        parser.values.dlls.extend(windows_dll_names)

    parser = OptionParser("usage: %prog [options] xmlfile")
    parser.add_option("-w",
                      action="callback",
                      callback=windows_dlls,
                      help="add all standard windows dlls to the searched dlls list")

    parser.add_option("-l",
                      dest="dlls",
                      help="libraries to search for exported functions",
                      action="append",
                      default=[])

    parser.add_option("-s",
                      dest="symbols",
                      metavar="SYMBOL",
                      action="append",
                      help="symbol to include "
                      "(if neither symbols nor expressions are specified, everything will be included)",
                      default=None)

    parser.add_option("-r",
                      dest="expressions",
                      metavar="EXPRESSION",
                      action="append",
                      help="regular expression for symbol to include "
                      "(if neither symbols nor expressions are specified, everything will be included)",
                      default=None)

    parser.add_option("-o",
                      dest="output",
                      help="output filename (if not specified, standard output will be used)",
                      default="-")

    parser.add_option("-v",
                      action="store_true",
                      dest="verbose",
                      help="verbose output",
                      default=False)

    parser.add_option("-d",
                      action="store_true",
                      dest="use_decorators",
                      help="use Python 2.4 function decorators",
                      default=False)

##    try:
##        import comtypes
##    except ImportError:
##        default_modules = ["ctypes", "ctypes.com"]
##    else:
##        default_modules = ["ctypes", "comtypes"]
    default_modules = ["ctypes"]
        
    parser.add_option("-m",
                      dest="modules",
                      metavar="module",
                      help="Python module(s) containing symbols which will be imported instead of generated",
                      action="append",
                      default=default_modules)

    options, files = parser.parse_args(args[1:])

    if len(files) != 1:
        parser.error("Exactly one input file must be specified")

    if options.output == "-":
        stream = sys.stdout
    else:
        stream = open(options.output, "w")

    if options.expressions:
        options.expressions = map(re.compile, options.expressions)

    stream.write("# generated by 'xml2py'\n")
    stream.write("# flags '%s'\n" % " ".join(sys.argv[1:]))

    known_symbols = {}

    from ctypes import CDLL
    dlls = [CDLL(name) for name in options.dlls]

    for name in options.modules:
        mod = __import__(name)
        for submodule in name.split(".")[1:]:
            mod = getattr(mod, submodule)
        known_symbols.update(mod.__dict__)

    generate_code(files[0], stream,
                  symbols=options.symbols,
                  expressions=options.expressions,
                  verbose=options.verbose,
                  use_decorators=options.use_decorators,
                  known_symbols=known_symbols,
                  searched_dlls=dlls)


if __name__ == "__main__":
    sys.exit(main())
