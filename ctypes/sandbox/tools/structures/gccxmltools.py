"""
Usage: gccxmltools.py [options] files...

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

     gccxmltools.py -D NONAMELESSUNION -D _WIN32_WINNT=0x500 -c msvc71 -o- windows.h
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
# abstract base classes
#
class Base(object):
    def _resolve(self, find_typ):
        return

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.name)

    def depends(self):
        return []

class TypeContainer(Base):
    typ = None

    def _resolve(self, find_typ):
        if self.typ is not None:
            return
        self.typ = find_typ(self._typ)
        self.typ._resolve(find_typ)

    def depends(self):
        return [self.typ]

################################
# concrete classes

class FundamentalType(Base):
    def __init__(self, name):
        self.name = name

class Enumeration(Base):
    def __init__(self, name):
        self.name = name
        self.values = []

    def add_value(self, name, value):
        self.values.append((name, value))

class PointerType(TypeContainer):
    def __init__(self, typ):
        self._typ = typ

    def __repr__(self):
        return "PointerType(%s)" % self.typ

class Typedef(TypeContainer):
    def __init__(self, name, typ):
        self.name = name
        self._typ = typ

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

class CvQualifiedType(TypeContainer):
    def __init__(self, typ, const):
        self._typ = typ
        self.const = const

    def __repr__(self):
        return "ConstQualifier(%s)" % (self.typ)

class Union(Base):
    members = None
    def __init__(self, name, members):
        self.name = name
        self._members = members

    def _resolve(self, find_typ):
        if self.members is not None:
            return

        self.members = []
        for id in self._members:
            f = find_typ(id)
            f._resolve(find_typ)
            if type(f) in (Field, Method):
                self.members.append(f)

    def depends(self):
        return [field.typ for field in self.members]


class Structure(Union):
    bases = None
    def __init__(self, name, members, bases):
        self.name = name
        self._members = members
        self._bases = bases

    def _resolve(self, find_typ):
        super(Structure, self)._resolve(find_typ)
        if self.bases is not None:
            return

        self.bases = []
        for id in self._bases.split():
            b = find_typ(id)
            b._resolve(find_typ)
            self.bases.append(b)

    def isClass(self):
        for m in self.members:
            if type(m) is Method:
                return True
        return False

    def __repr__(self):
        return "Structure(%s)" % self.name

    def depends(self):
        return [field.typ for field in self.members if type(field) == Field]


class Constructor(Base):
    def __init__(self, name):
        self.name = name

class Method(Base):
    returns = None
    def __init__(self, name, returns):
        self.name = name
        self._returns = returns

    def _resolve(self, find_typ):
        if self.returns is not None:
            return
        self.returns = find_typ(self._returns)
        self.returns._resolve(find_typ)

    def depends(self):
        return [self.returns]


class FunctionType(Base):
    def __repr__(self):
        return "FunctionType"

class Function(Base):
    returns = None
    def __init__(self, name, returns):
        self.name = name
        self._returns = returns

    def _resolve(self, find_typ):
        if self.returns is None:
            r = find_typ(self._returns)
            self.returns = r
            r._resolve(find_typ)
        return

    def depends(self):
        return [self.returns]

################################################################

from sets import Set

def D(attrs):
    result = {}
    for name, value in attrs._attrs.items():
        result[str(name)] = value
    return result

class GCCXML_Handler(handler.ContentHandler):
    has_values = Set(["Enumeration", "Function", "FunctionType", "Method"])

    def __init__(self, *args):
        handler.ContentHandler.__init__(self, *args)
        self.context = []
        self.all = {}

    def startElement(self, name, attrs):
        result = None
        mth = getattr(self, name, None)
        if mth is not None:
            result = mth(attrs)
            _id = attrs.get("id", None)
            if _id is not None:
                self.all[_id] = result
##        else:
##            import warnings
##            warnings.warn(name, Warning)
        if name in self.has_values:
            self.context.append(result)

    def endElement(self, name):
        if name in self.has_values:
            self.context = self.context[:-1]

    def get_result(self):
        for item in self.all.values():
            item._resolve(self.all.__getitem__)
        return self.all.values()


    ################

    def Function(self, attrs):
        # name, returns, extern, attributes
        name = attrs["name"]
        returns = attrs["returns"]
        return Function(name, returns)

    def Field(self, attrs):
        # name, type
        name = attrs["name"]
        typ = attrs["type"]
        bits = attrs.get("bits", None)
        return Field(name, typ, bits)

    def Constructor(self, attrs):
        name = attrs["name"]
        return Constructor(name)

    def Typedef(self, attrs):
        name = attrs["name"]
        typ = attrs["type"]
        return Typedef(name, typ)

    def FundamentalType(self, attrs):
        name = attrs["name"]
        return FundamentalType(name)

    def PointerType(self, attrs):
        typ = attrs["type"]
        return PointerType(typ)

    def CvQualifiedType(self, attrs):
        # id, type, [const|volatile]
        typ = attrs["type"]
##        const = attrs["const"]
##        volatile = attrs["volatile"]
        return CvQualifiedType(typ, "xxx")

    def ArrayType(self, attrs):
        # type, min?, max?
        typ = attrs["type"]
        min = attrs["min"]
        max = attrs["max"]
        return ArrayType(typ, min, max)

    def Enumeration(self, attrs):
        # id, name
        name = attrs["name"]
        return Enumeration(name)

    def Struct(self, attrs):
        # id, name, members
        name = attrs["name"]
        bases = attrs.get("bases", "")
        members = attrs.get("members", "").split()
        return Structure(name, members, bases)

    def Union(self, attrs):
        name = attrs["name"]
        return Union(name, attrs.get("members", "").split())

    def Method(self, attrs):
        # name, virtual, pure_virtual, returns
        name = attrs["name"]
        returns = attrs["returns"]
        return Method(name, returns)

    def FunctionType(self, attrs):
        # id, returns, attributes
        return FunctionType()

##    def Variable(self, attrs):
##        # Variable   <Variable id="_652" name="IID_StdOle" type="_3925c"
##        #             context="_1" location="f4:30" file="f4" line="30" extern="1"/>
##        name = attrs["name"]
##        typ = attrs["type"]
##        extern = attrs["extern"]
##        return Variable(name, typ, extern)

##    def Argument(self, attrs):
##        pass

    def EnumValue(self, attrs):
        name = attrs["name"]
        value = attrs["init"]
        self.context[-1].add_value(name, value)

    # OperatorFunction
    # Ellipsis
    # ReferenceType
    # File

################################################################

class Visitor(object):
    def __init__(self, objects):
        self.__objects = objects

    def _visit(self, obj):
        mth = getattr(self, obj.__class__.__name__, None)
        if mth is not None:
            mth(obj)
##        else:
##            import warnings
##            warnings.warn(type(obj), Warning)

    def go(self):
        for o in self.__objects:
            self._visit(o)

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

    handler = GCCXML_Handler()

    parse(xml_file, handler)
##    os.remove(xml_file)

    return handler.get_result()

if __name__ == "__main__":
    if len(sys.argv) == 1:
##        sys.argv.extend("-D NONAMELESSUNION -I. -D _WIN32_WINNT=0x500 -c msvc71 -o- windows.h richedit.h".split())
        sys.argv.extend("-D NONAMELESSUNION -D _WIN32_WINNT=0x500 -c msvc6 -o- windows.h".split())
    main()

