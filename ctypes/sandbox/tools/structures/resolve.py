"""
Usage: gen_structs [options] files...

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

     gen_structs -D NONAMELESSUNION -D _WIN32_WINNT=0x500 -c msvc71 -o- windows.h
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
    os.write(handle, 'extern "C" {\n');
    for fname in fnames:
        os.write(handle, '#include <%s>\n' % fname)
    os.write(handle, '}');
    os.close(handle)

##    handle, xml_file = tempfile.mkstemp(suffix=".xml", text=True)
##    os.close(handle)
    xml_file = "~temp.xml"

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
        else:
            import warnings
            warnings.warn(name, Warning)
##            print "???", name

    def endElement(self, name):
        if name in self.has_values:
            self.context = self.context[:-1]

################################################################

################

ctypes_names = {
    "short int": "c_short",
    "int": "c_int",
    "long int": "c_long",
    "long long int": "c_longlong",

    "short unsigned int": "c_ushort",
    "unsigned int": "c_uint",
    "long unsigned int": "c_ulong",
    "long long unsigned int": "c_ulonglong",

    "float": "c_float",
    "double": "c_double",

    "char": "c_char",
    "signed char": "c_byte",
    "unsigned char": "c_ubyte",
    "wchar_t": "c_wchar",
    "void": "void", # ?
    }

class FundamentalType(object):
    def __init__(self, name):
        self.name = name

    def resolve(self, find_typ):
        return

    def __repr__(self):
        return "FundamentalType(%s)" % self.name

    def as_ctype(self):
        return ctypes_names[self.name]

class Enumeration(object):
    def __init__(self, name):
        self.name = name
        self.values = []

    def add_value(self, name, value):
        self.values.append((name, value))

    def resolve(self, find_typ):
        return

    def __repr__(self):
        return "Enumeration(%s)" % self.name

    def as_ctype(self):
##        return "enum(%s)" % self.name
        return "C_INT" # fixme (or not?)

class TypeContainer(object):
    typ = None

    def resolve(self, find_typ):
        if self.typ is not None:
            return
        self.typ = find_typ(self._typ)
        self.typ.resolve(find_typ)

class PointerType(TypeContainer):
    def __init__(self, typ):
        self._typ = typ

    def __repr__(self):
        return "PointerType(%s)" % self.typ

    def as_ctype(self):
        # fixme: special case POINTER(FUNCTION)
        # fixme: special case POINTER(void)
        if type(self.typ) is FunctionType:
            return self.typ.as_ctype()
        return "POINTER(%s)" % self.typ.as_ctype()

class Typedef(TypeContainer):
    def __init__(self, name, typ):
        self.name = name
        self._typ = typ

    def as_ctype(self):
        return self.name

    def __repr__(self):
        return "Typedef(%s -> %s)" % (self.name, self.typ)

class Field(TypeContainer):
    def __init__(self, name, typ, bits=None):
        self.name = name
        self._typ = typ
        self.bits = bits

    def __repr__(self):
        return "Field(%s -> %s)" % (self.name, self.typ)

class ArrayType(TypeContainer):
    def __init__(self, typ, min, max):
        self._typ = typ
        self.min = int(min)
        if max == "":
            self.max = -1
        elif max == "ffffffffffffffff":
            self.max = -99 ##0xFFFFFFFFFFFFFFFF
        else:
            self.max = int(max)

    def __repr__(self):
        return "Array(%s[%s:%s])" % (self.typ, self.min, self.max)

    def as_ctype(self):
        return "%s * %s" % (self.typ.as_ctype(), self.max+1)

class CvQualifiedType(TypeContainer):
    def __init__(self, typ, const):
        self._typ = typ
        self.const = const

    def __repr__(self):
        return "ConstQualifier(%s)" % (self.typ)

    def as_ctype(self):
        return "CONST(%s)" % self.typ.as_ctype()

class Union(object):
    members = None
    def __init__(self, name, members):
        self.name = name
        self._members = members

    def resolve(self, find_typ):
        if self.members is not None:
            return

        self.members = []
        for id in self._members:
            f = find_typ(id)
            f.resolve(find_typ)
            if type(f) in (Field, Method):
                self.members.append(f)

    def __repr__(self):
        return "Union(%s)" % self.name

    def as_ctype(self):
        name = self.name
        if name.startswith("$_"):
            name = "__internal_" + name[2:]
        return name

class Structure(Union):
    bases = None
    def __init__(self, name, members, bases):
        self.name = name
        self._members = members
        self._bases = bases

    def resolve(self, find_typ):
        super(Structure, self).resolve(find_typ)
        if self.bases is not None:
            return

        self.bases = []
        for id in self._bases.split():
            b = find_typ(id)
            b.resolve(find_typ)
            self.bases.append(b)

    def __repr__(self):
        if self.bases:
            for m in self.members:
                if isinstance(m, Method):
                    return "Class(%s)(%s)" % (self.name, self.bases)
            return "Structure(%s)(%s)" % (self.name, self.bases)
        else:
            for m in self.members:
                if isinstance(m, Method):
                    return "Class(%s)" % self.name
            return "Structure(%s)" % self.name

    def isClass(self):
        for m in self.members:
            if isinstance(m, Method):
                return True
        return False

    def __repr__(self):
        return "Structure(%s)" % self.name

    def as_ctype(self):
        name = self.name
        if name.startswith("$_"):
            name = "__internal_" + name[2:]
        return name

class Constructor(object):
    def resolve(self, find_typ):
        return

class Method(object):
    returns = None
    def __init__(self, name, returns):
        self.name = name
        self._returns = returns

    def resolve(self, find_typ):
        if self.returns is not None:
            return
        self.returns = find_typ(self._returns)
        self.returns.resolve(find_typ)

    def __repr__(self):
        return "Method(%s, %s)" % (self.name, self.returns)

class FunctionType(object):
    def __repr__(self):
        return "FUNCTYPE(fixme)"

    def resolve(self, find_typ):
        return

    def as_ctype(self):
        return "FUNCTYPE(fixme)"

class Function(object):
    returns = None
    def __init__(self, name, returns, **kw):
        self.name = name
        self._returns = returns

    def resolve(self, find_typ):
        if self.returns is None:
            r = find_typ(self._returns)
            self.returns = r
            r.resolve(find_typ)
        return

################

class Enum_Handler(GCCXML_Handler_Base):
    has_values = Set(["Enumeration"])
    typedefs = {}

    def __init__(self, *args):
        GCCXML_Handler_Base.__init__(self, *args)
        self.all = {}

    def Field(self, attrs):
        # name, type
        id = attrs["id"]
        name = attrs["name"]
        typ = attrs["type"]
        bits = attrs.get("bits", None)
        self.all[id] = Field(name, typ, bits)

    def Constructor(self, attrs):
        id = attrs["id"]
        self.all[id] = Constructor()

    def Typedef(self, attrs):
        id = attrs["id"]
        name = attrs["name"]
        typ = attrs["type"]
        td = Typedef(name, typ)
        self.typedefs[name] = td
        self.all[id] = td

    def FundamentalType(self, attrs):
        id = attrs["id"]
        name = attrs["name"]
        self.all[id] = FundamentalType(name)

    def PointerType(self, attrs):
        # id, type
        id = attrs["id"]
        typ = attrs["type"]
        self.all[id] = PointerType(typ)

    def CvQualifiedType(self, attrs):
        # id, type, [const|volatile]
        id = attrs["id"]
        typ = attrs["type"]
##        const = attrs["const"]
        self.all[id] = CvQualifiedType(typ, "xxx")

    def ArrayType(self, attrs):
        # id, type, min?, max?
        id = attrs["id"]
        typ = attrs["type"]
        min = attrs["min"]
        max = attrs["max"]
        self.all[id] = ArrayType(typ, min, max)

    def Enumeration(self, attrs):
        # id, name
        id = attrs["id"]
        name = attrs["name"]
        e = Enumeration(name)
        self.all[id] = e
        self.context[-1] = e

    def Struct(self, attrs):
        # id, name, members
        id = attrs["id"]
        name = attrs["name"]
        bases = attrs.get("bases", "")
        members = attrs.get("members", "").split()
        self.all[id] = Structure(name, members, bases)

    def Union(self, attrs):
        # id, name, members
        id = attrs["id"]
        name = attrs["name"]
        self.all[id] = Union(name, attrs.get("members", "").split())

    def Method(self, attrs):
        # id, name, virtual, pure_virtual, returns
        id = attrs["id"]
        name = attrs["name"]
        returns = attrs["returns"]
        self.all[id] = Method(name, returns)

    def FunctionType(self, attrs):
        # id, returns, attributes
        id = attrs["id"]
        self.all[id] = FunctionType()

    def Function(self, attrs):
        # id, name, returns, extern, attributes
        id = attrs["id"]
        name = attrs["name"]
        returns = attrs["returns"]
        self.all[id] = Function(name, returns)

    def Variable(self, attrs):
        # Variable   <Variable id="_652" name="IID_StdOle" type="_3925c"
        #             context="_1" location="f4:30" file="f4" line="30" extern="1"/>
        id = attrs["id"]
        name = attrs["name"]
        typ = attrs["type"]
        extern = attrs["extern"]

    def Argument(self, attrs):
        pass

    def EnumValue(self, attrs):
        name = attrs["name"]
        value = attrs["init"]
        self.context[-1].add_value(name, value)

    # OperatorFunction
    # Ellipsis
    # ReferenceType
    # File

################################################################

def dump_enums(handler):
    for t in handler.all.values():
        if type(t) is Enumeration:
            import pprint
            print t.name
            pprint.pprint(t.values)
            print

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
##    os.remove(xml_file)

    from pprint import pprint as pp
    
    def find_typ(id):
        return handler.all[id]

    for item in handler.all.values():
        item.resolve(find_typ)

    if 0:
        dump_enums(handler)
        sys.exit()
    else:
        pass

    # Structures and Unions
    compounds = {}

    for obj in handler.all.values():
        if type(obj) is Structure and not obj.isClass():
            compounds[obj.name] = obj
        elif type(obj) is Union:
            compounds[obj.name] = obj

    print "from ctypes import *"
    print

    s_names = compounds.keys()
    s_names.sort()
##    for n in s_names:
##        print "class %s(c_int):" % n
##        print "    pass"
##        print

    for n in s_names:
        s = compounds[n]
        print "class %s(c_int):" % n
        for m in s.members:
            assert type(m) is Field
##            assert not m.bits, (m.name, m.typ.name, m.bits)
            if type(m.typ) in (Structure, Union):
                if m.typ.name.startswith("$_"):
                    name = m.typ.name.replace("$_", "__internal_")
                    print "    class %s(c_int):" % name
                    print "        _fields_ = ["
                    for mi in m.typ.members:
                        print "            ('%s', %s)" % (mi.name, mi.typ.as_ctype())
##        print "%s._fields_ = [" % n
        print "    _fields_ = ["
        for m in s.members:
            print "        ('%s', %s)," % (m.name, m.typ.as_ctype())
        print "    ]"
        print

if __name__ == "__main__":
    if len(sys.argv) == 1:
##        sys.argv.extend("-D NONAMELESSUNION -I. -D _WIN32_WINNT=0x500 -c msvc71 -o- windows.h richedit.h".split())
        sys.argv.extend("-D NONAMELESSUNION -D _WIN32_WINNT=0x500 -c msvc6 -o- windows.h".split())
    main()
