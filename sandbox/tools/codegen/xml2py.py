# bugs:
# packing of structures/unions with bitfields? See '##XXX FIXME'
import sys
from codegenerator import generate_code

################################################################

def main(args=None):
    if args is None:
        args = sys.argv
    from optparse import OptionParser

    def windows_dlls(option, opt, value, parser):
        parser.values.dlls.extend("kernel32 gdi32 user32".split())

    parser = OptionParser("usage: %prog [options] xmlfile")
    parser.add_option("--windows-dlls",
                      action="callback",
                      callback=windows_dlls,
                      help="add all standard windows dlls")
    parser.add_option("--dll",
                      dest="dlls",
                      action="append",
                      default=[])
    parser.add_option("-s",
                      dest="symbols",
                      help="comma separated list of symbols to include "
                      "(if not specified, all symbols will be included)",
                      default=None)
    parser.add_option("-o",
                      dest="output",
                      help="output filename (if not specified, standard output will be used)",
                      default="-")
    options, files = parser.parse_args(args[1:])

    if len(files) != 1:
        parser.error("Exactly one input file must be specified")

    if options.output == "-":
        stream = sys.stdout
    else:
        stream = open(options.output, "w")

    generate_code(files[0], stream, symbols=options.symbols)


if __name__ == "__main__":
    sys.exit(main())
