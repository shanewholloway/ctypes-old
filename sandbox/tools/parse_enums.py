"""
Usage: parse_enums [options] files...

Command line flags:

   -c <value>, --compiler <value>
      Specifies the compiler that GCCXML should emulate.  For Windows,
      typically use msvc6 or msvc71.

   -D <symbol>
   -D <symbol=value>
   -U <symbol>
   -I <directory>
      These flags are passed to GCCXML.

   -o <filename>
      Write the parsing results to <filename>.  Using '-' as filename
      will write the results to standard output.

   -v
      Increases the verbosity.  Verbosity 1 prints out what the
      program is doing, verbosity 2 additionally prints lines it could
      not parse.

   -h
      Display help, then quit.

   Sample command line (depends on the MSVC compiler you have):

     parse_enums -D _WIN32_WINNT=0x500 -c msvc71 -o- windows.h
"""
import sys, os, tempfile
from xml.sax import make_parser, parse, handler

################################################################

class CompilerError(Exception):
    pass

# Create a C file containing #includes to the specified filenames.
# Parse it with GCCXML into a XML file, and return the xml filename.
def run_gccxml(options, verbose, *fnames):
    # options is a sequence of command line options for GCCXML
    # fnames is the sequence of include files
    # verbose - integer specifying the verbosity

    # returns the filename of the generated XML file

    compiler = ""
    for o in options:
        if o.startswith("--gccxml-compiler"):
            compiler = o
    options = " ".join(options)

    def read_stderr(fd):
        import threading

        def get_errout(fd):
            errs = fd.read()
            if errs:
                sys.stderr.write(errs)
            retval = fd.close()
            if retval:
                raise ParserError, "gccxml returned error %s" % retval

        thread = threading.Thread(target=get_errout, args=(fd,))
        thread.start()
        return thread

    # write a temporary C file
    handle, c_file = tempfile.mkstemp(suffix=".c", text=True)
    for fname in fnames:
        os.write(handle, '#include <%s>\n' % fname)
    os.close(handle)

    handle, xml_file = tempfile.mkstemp(suffix=".xml", text=True)
    os.close(handle)

    try:
        if verbose:
            print >> sys.stderr, r"run gccxml.exe %s --preprocess -dM" % compiler
        i, o = os.popen4(r"gccxml.exe %s %s -fxml=%s" % (options, c_file, xml_file))
        i.close()
        sys.stderr.write(o.read())
        retval = o.close()
        if retval:
            raise CompilerError, "gccxml returned error %s" % retval
        return xml_file
    finally:
        if verbose:
            print >> sys.stderr, "Deleting temporary file %s" % c_file
        os.remove(c_file)

################################################################

##ELEMENTS = ['Function',
##            'Typedef',
##            'Struct',
##            'Field',
##            'Union',
##            'CvQualifiedType',
##            'FundamentalType',
##            'Namespace',
##            'Argument',
##            'Enumeration',
##            'EnumValue',
##            'GCC_XML',
##            'Variable',
##            'ArrayType',
##            'File',
##            'Constructor',
##            'PointerType',
##            'Ellipsis',
##            'ReferenceType',
##            'FunctionType']

from sets import Set

class GCCXML_Handler_Base(handler.ContentHandler):
    has_values = Set()

    def __init__(self, *args):
        handler.ContentHandler.__init__(self, *args)
        self.context = []

    def startElement(self, name, attrs):
        if name in self.has_values:
            self.context.append(name)
        mth = getattr(self, name, None)
        if mth is not None:
            mth(attrs)

    def endElement(self, name):
        if name in self.has_values:
            self.context = self.context[:-1]

################################################################

class Enum(object):
    # represents an enumeration
    def __init__(self, attrs):
        self.name = attrs["name"]
        self.values = []

    def add_value(self, attrs):
        self.values.append((attrs["name"], int(attrs["init"])))

    def dump_as_class(self, stream):
        print >> stream, "class %s(object):" % self.name
        for name, value in self.values:
            print >> stream, "    %s = %r" % (name, value)
        print >> stream

    def dump_as_constants(self, stream):
        for name, value in self.values:
            print >> stream, "%s = %r" % (name, value)

################

class Enum_Handler(GCCXML_Handler_Base):
    has_values = Set("Enumeration".split())

    def __init__(self, *args):
        GCCXML_Handler_Base.__init__(self, *args)
        self.enums = {}
        self.typedefs = {}

    def Enumeration(self, attrs):
        e = Enum(attrs)
        self.context[-1] = e
        self.enums[attrs["id"]] = e

    def EnumValue(self, attrs):
        e = self.context[-1]
        e.add_value(attrs)

    def Typedef(self, attrs):
        self.typedefs[attrs["name"]] = attrs["type"]

################################################################

def main(args=None):
    if args is None:
        args = sys.argv[1:]
    import getopt

    gccxml_options = []
    verbose = 0
    try:
        opts, files = getopt.getopt(args, "hvc:D:U:I:o:", ["compiler="])
    except (getopt.GetoptError, ValueError):
        print >> sys.stderr, __doc__
        return 1
    py_file = None
    for o, a in opts:
        if o in ("-c", "--compiler"):
            gccxml_options.append("--gccxml-compiler %s" % a)
        elif o in ("-D", "-U", "-I"):
            gccxml_options.append("%s %s" % (o, a))
        elif o == "-v":
            verbose += 1
        elif o == "-h":
            print >> sys.stderr, __doc__
            return 0
        elif o == "-o":
            py_file = a

    if not files:
        print "Error: no files to process"
        print >> sys.stderr, __doc__
        return 1

    xml_file = run_gccxml(gccxml_options, verbose, *files)

    handler = Enum_Handler()

    parse(xml_file, handler)
    os.remove(xml_file)

    if py_file is None:
        return 0
    if py_file == "-":
        ofi = sys.stdout
    else:
        ofi = open(py_file, "w")

    for enum in handler.enums.values():
##        enum.dump_as_class()
        enum.dump_as_constants(ofi)

    return 0

    # do we have a use for typedefs? Not yet...
    for name, typ in handler.typedefs.items():
        try:
            e = handler.enums[typ]
        except KeyError:
            pass
        else:
            print "%s = %s" % (name, e.name)
            print "del %s" % e.name
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
