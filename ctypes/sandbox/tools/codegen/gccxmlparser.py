import sys, os, tempfile
import xml.sax
from sets import Set
import nodes

# XXX
os.environ["PATH"] = r"c:\sf\buildgcc\bin\release"

################################################################

class CompilerError(Exception):
    pass

# Create a C file containing #includes to the specified filenames.
# Run GCCXML to create an XML file, and return the xml filename.
def run_gccxml(fnames, options, verbose=0, xml_file=None):
    # fnames is the sequence of include files
    # options is seuqence of strings containing command line options for GCCXML
    # verbose - integer specifying the verbosity
    #
    # returns the filename of the generated XML file

    # write a temporary C file
    handle, c_file = tempfile.mkstemp(suffix=".c", text=True)
    if verbose:
        print >> sys.stderr, "writing temporary C source file %s" % c_file
##    os.write(handle, 'extern "C" {\n');
    for fname in fnames:
        os.write(handle, '#include <%s>\n' % fname)
##    os.write(handle, '}');
    os.close(handle)

    if xml_file is None:
        handle, xml_file = tempfile.mkstemp(suffix=".xml", text=True)
        os.close(handle)

    if options:
        options = " ".join(options)
    else:
        options = ""

    try:
        if verbose:
            print >> sys.stderr, r"gccxml.exe %s %s -fxml=%s" % (options, c_file, xml_file)
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

class GCCXML_Handler(xml.sax.handler.ContentHandler):
    has_values = Set(["Enumeration", "Function", "FunctionType",
                      "OperatorFunction", "Method", "Constructor",
                      "Destructor", "OperatorMethod"])

    def __init__(self, *args):
        xml.sax.handler.ContentHandler.__init__(self, *args)
        self.context = []
        self.all = {}
        self.artificial = []

    def demangle(self, name):
        return "_py_" + name.replace("$", "_")

    def startElement(self, name, attrs):
        # find and call the handler for this element
        mth = getattr(self, name)
        result = mth(attrs)
        if result is not None:
            # record the result
            _id = attrs.get("id", None)
            if _id is not None:
                self.all[_id] = result
        # if this element has children, push onto the context
        if name in self.has_values:
            self.context.append(result)

    def endElement(self, name):
        # if this element has children, pop the context
        if name in self.has_values:
            self.context.pop()

    ################################
    # do-nothing element handlers

    def Class(self, attrs): pass
    def Destructor(self, attrs): pass
    
    def GCC_XML(self, attrs): pass
    def Namespace(self, attrs): pass

    def Variable(self, attrs): pass
    def Base(self, attrs): pass
    def Ellipsis(self, attrs): pass
    def File(self, attrs): pass
    def OperatorMethod(self, attrs): pass

    ################################
    # real element handlers

    # simple types and modifiers

    def Typedef(self, attrs):
        name = attrs["name"]
        typ = attrs["type"]
        return nodes.Typedef(name, typ)

    def _fixup_Typedef(self, t):
        t.typ = self.all[t.typ]

    def FundamentalType(self, attrs):
        name = attrs["name"]
        if name == "void":
            size = ""
        else:
            size = attrs["size"]
        align = attrs["align"]
        return nodes.FundamentalType(name, size, align)

    def _fixup_FundamentalType(self, t): pass

    def PointerType(self, attrs):
        typ = attrs["type"]
        size = attrs["size"]
        align = attrs["align"]
        return nodes.PointerType(typ, size, align)

    def _fixup_PointerType(self, p):
        p.typ = self.all[p.typ]

    ReferenceType = PointerType
    _fixup_ReferenceType = _fixup_PointerType

    def ArrayType(self, attrs):
        # type, min?, max?
        typ = attrs["type"]
        min = attrs["min"]
        max = attrs["max"]
        if max == "ffffffffffffffff":
            max = "-1"
        return nodes.ArrayType(typ, min, max)

    def _fixup_ArrayType(self, a):
        a.typ = self.all[a.typ]

    def CvQualifiedType(self, attrs):
        # id, type, [const|volatile]
        typ = attrs["type"]
##        const = attrs["const"]
##        volatile = attrs["volatile"]
        return nodes.CvQualifiedType(typ, "xxx")

    def _fixup_CvQualifiedType(self, c):
        c.typ = self.all[c.typ]

    # callables
    
    def Function(self, attrs):
        # name, returns, extern, attributes
        name = attrs["name"]
        returns = attrs["returns"]
        attributes = attrs.get("attributes", "").split()
        extern = attrs.get("extern")
        return nodes.Function(name, returns, attributes, extern)

    def _fixup_Function(self, func):
        func.returns = self.all[func.returns]
        func.arguments = [self.all[a] for a in func.arguments]

    def FunctionType(self, attrs):
        # id, returns, attributes
        returns = attrs["returns"]
        return nodes.FunctionType(returns)
    
    def _fixup_FunctionType(self, func):
        func.returns = self.all[func.returns]
        func.arguments = [self.all[a] for a in func.arguments]

    def OperatorFunction(self, attrs):
        # name, returns, extern, attributes
        name = attrs["name"]
        returns = attrs["returns"]
        return nodes.OperatorFunction(name, returns)

    def _fixup_OperatorFunction(self, func):
        func.returns = self.all[func.returns]

    def Constructor(self, attrs):
        name = attrs["name"]
        return nodes.Constructor(name)

    def _fixup_Constructor(self, const): pass

    def Method(self, attrs):
        # name, virtual, pure_virtual, returns
        name = attrs["name"]
        returns = attrs["returns"]
        return nodes.Method(name, returns)

    def _fixup_Method(self, m):
        m.returns = self.all[m.returns]
        m.arguments = [self.all[a] for a in m.arguments]

    def Argument(self, attrs):
        typ = attrs["type"]
        parent = self.context[-1]
        if parent is not None:
            parent.add_argument(typ) # name?

    # enumerations

    def Enumeration(self, attrs):
        # id, name
        name = attrs["name"]
        size = attrs["size"]
        align = attrs["align"]
        if attrs.get("artificial"):
            # enum {} ENUM_NAME;
            return nodes.Enumeration(name, size, align)
        else:
            # enum tagENUM {};
            enum = nodes.Enumeration(None, size, align)
            self.artificial.append(nodes.Typedef(name, enum))
            return enum

    def _fixup_Enumeration(self, e): pass

    def EnumValue(self, attrs):
        name = attrs["name"]
        value = attrs["init"]
        self.context[-1].add_value(name, value)

    def _fixup_EnumValue(self, e): pass

    # structures, unions

    def Struct(self, attrs):
        # id, name, members
        name = attrs.get("name")
        bases = attrs.get("bases", "").split()
        members = attrs.get("members", "").split()
        abstract = attrs.get("abstract", "")
        align = attrs["align"]
        size = attrs.get("size")
        artificial = attrs.get("artificial")
        if name is None:
            name = self.demangle(attrs["mangled"]) # for debug only
##        if abstract:
##            return nodes.Class(name, members, bases)
##        else:
        if artificial:
            return nodes.Structure(name, align, members, bases, size)
        else:
##            struct = nodes.Structure(name, align, members, bases, size)
            struct = nodes.Structure(name, align, members, bases, size)
            self.artificial.append(nodes.Typedef(name, struct))
            return struct

    def _fixup_Structure(self, s):
        s.members = [self.all[m] for m in s.members]
        s.bases = [self.all[b] for b in s.bases]
    _fixup_Union = _fixup_Structure

    def Union(self, attrs):
        name = attrs.get("name")
        bases = attrs.get("bases", "").split()
        members = attrs.get("members", "").split()
        abstract = attrs.get("abstract", "")
        align = attrs["align"]
        size = attrs.get("size")
        artificial = attrs.get("artificial")
        if name is None:
            name = self.demangle(attrs["mangled"]) # for debug only
        return nodes.Union(name, align, members, bases, size)

    def Field(self, attrs):
        # name, type
        name = attrs["name"]
        typ = attrs["type"]
        bits = attrs.get("bits", None)
        offset = attrs.get("offset")
        return nodes.Field(name, typ, bits, offset)

    def _fixup_Field(self, f):
        f.typ = self.all[f.typ]

    ################

    def get_result(self):
        interesting = (
            nodes.Typedef, nodes.Enumeration, nodes.Function, nodes.Structure, nodes.Union)
        result = []
        remove = []
        for n, i in self.all.items():
            mth = getattr(self, "_fixup_" + type(i).__name__)
            try:
                mth(i)
            except KeyError: # XXX better exception catching
                remove.append(n)
        for n in remove:
            del self.all[n]
        for i in self.artificial + self.all.values():
            if isinstance(i, interesting):
                result.append(i)
        return result

################################################################

def parse(files, options=None, verbose=0, xmlfile=None):
    # run C files through gccxml, parse the xml output,
    # and return a sequence of items found.
    xml_file = run_gccxml(files, options, verbose, xmlfile)
    handler = GCCXML_Handler()
    if verbose:
        print "Parsing...",
    xml.sax.parse(xml_file, handler)
    if verbose:
        print "done"
    return handler.get_result()

################################################################

def main(args=None):
    if args is None:
        args = sys.argv[1:]
    import getopt

    gccxml_options = []
    verbose = 0
    try:
        opts, files = getopt.getopt(args, "hvc:D:U:I:", ["compiler="])
    except (getopt.GetoptError, ValueError):
        print >> sys.stderr, __doc__
        return 1
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

    if not files:
        print "Error: no files to process"
        print >> sys.stderr, __doc__
        return 1

    items = parse(files, options=gccxml_options, verbose=verbose)

    interesting = (nodes.FunctionType, nodes.Function,
                   nodes.Method, nodes.ArrayType)

    interesting = (nodes.Structure, nodes.ArrayType)

    done = 0
    for i in range(len(items)):

        if not isinstance(items[i], interesting):
            continue
##        if isinstance(items[i], (nodes.Field, nodes.Constructor, type(None))):
##            continue
        if done > 60:
            return 1
        print items[i]
        done += 1
    return 0

if __name__ == "__main__":
    if len(sys.argv) == 1:
##        sys.argv.extend("-v -I. test.h".split())
        sys.argv.extend("-v windows.h".split())
    sys.exit(main())
