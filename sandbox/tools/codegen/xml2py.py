# bugs:
# packing of structures/unions with bitfields? See '##XXX FIXME'
import sys
from codegenerator import generate_code

################################################################

def main():
    from optparse import OptionParser

    parser = OptionParser("usage: %prog [options] xmlfile")
    parser.add_option("-s",
                      dest="symbols",
                      help="comma separated list of symbols to include "
                      "(if not specified, all symbols will be included)",
                      default=None)
    parser.add_option("-o",
                      dest="python_file",
                      help="output filename (if not specified, standard output will be used)",
                      default="-")
    options, files = parser.parse_args()

    if len(files) != 1:
        parser.error("Only one input file can be specified")

    if options.python_file == "-":
        stream = sys.stdout
    else:
        stream = open(options.python_file, "w")

    generate_code(files[0], stream, symbols=options.symbols)


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
##        sys.argv.append("win32.xml")
##        sys.argv.append("-sCoCreateInstance")
        sys.argv.append("win32.xml")
        sys.argv.append("-sCLSIDFromString,StringFromGUID2,IsEqualGUID")
##        sys.argv.append("-owin32.py")
    main()
