"""gccxmlparser - parse a gccxml created XML file into a sequence type descriptions"""
import xml.sax
import typedesc
import sys
try:
    set
except NameError:
    from sets import Set as set

################################################################

class GCCXML_Handler(xml.sax.handler.ContentHandler):
    has_values = set(["Enumeration", "Function", "FunctionType",
                      "OperatorFunction", "Method", "Constructor",
                      "Destructor", "OperatorMethod"])

    def __init__(self, *args):
        xml.sax.handler.ContentHandler.__init__(self, *args)
        self.context = []
        self.all = {}
        self.artificial = []
        self.cpp_data = {}

    def demangle(self, name):
        if name.startswith("__"):
            name = "_py_" + name
        if name[:0] and name[0] in "0123456789":
            name = "_%c" % name[0] + name
        name = name.replace("$", "_")
        name = name.replace(".", "_")
        return  name

    def startElement(self, name, attrs):
        # find and call the handler for this element
        mth = getattr(self, name)
        result = mth(attrs)
        if result is not None:
            location = attrs.get("location", None)
            if location is not None:
                result.location = location
            # record the result
            _id = attrs.get("id", None)
            # The '_id' attribute is used to link together all the
            # nodes, in the _fixup_ methods.
            if _id is not None:
                self.all[_id] = result
            else:
                # EnumValue, for example, has no "_id" attribute.
                # Invent our own...
                self.all[id(result)] = result
        # if this element has children, push onto the context
        if name in self.has_values:
            self.context.append(result)

    cdata = None
    def endElement(self, name):
        # if this element has children, pop the context
        if name in self.has_values:
            self.context.pop()
        self.cdata = None

    ################################
    # do-nothing element handlers

    def Class(self, attrs): pass
    def Destructor(self, attrs): pass
    
    def GCC_XML(self, attrs): pass
    def Namespace(self, attrs): pass

    def Base(self, attrs): pass
    def Ellipsis(self, attrs): pass
    def OperatorMethod(self, attrs): pass

    ################################
    # real element handlers

    def CPP_DUMP(self, attrs):
        name = attrs["name"]
        # Insert a new list for each named section into self.cpp_data,
        # and point self.cdata to it.  self.cdata will be set to None
        # again at the end of each section.
        self.cpp_data[name] = self.cdata = []

    def characters(self, content):
        if self.cdata is not None:
            self.cdata.append(content)

    def File(self, attrs):
        name = attrs["name"]
        return typedesc.File(name)

    def _fixup_File(self, f):
        if sys.platform == "win32" and " " in f.name:
            # On windows, convert to short filename if it contains blanks
            from ctypes import windll, create_unicode_buffer, sizeof
            buf = create_unicode_buffer(256)
            if windll.kernel32.GetShortPathNameW(f.name, buf, sizeof(buf)):
                f.name = buf.value
    
    # simple types and modifiers

    def Variable(self, attrs):
        name = attrs["name"]
        if name.startswith("cpp_sym_"):
            # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx fix me!
            name = name[len("cpp_sym_"):]
        init = attrs.get("init", None)
        typ = attrs["type"]
        return typedesc.Variable(name, typ, init)

    def _fixup_Variable(self, t):
        t.typ = self.all[t.typ]

    def Typedef(self, attrs):
        name = self.demangle(attrs["name"])
        typ = attrs["type"]
        return typedesc.Typedef(name, typ)

    def _fixup_Typedef(self, t):
        t.typ = self.all[t.typ]

    def FundamentalType(self, attrs):
        name = self.demangle(attrs["name"])
        if name == "void":
            size = ""
        else:
            size = attrs["size"]
        align = attrs["align"]
        return typedesc.FundamentalType(name, size, align)

    def _fixup_FundamentalType(self, t): pass

    def PointerType(self, attrs):
        typ = attrs["type"]
        size = attrs["size"]
        align = attrs["align"]
        return typedesc.PointerType(typ, size, align)

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
        return typedesc.ArrayType(typ, min, max)

    def _fixup_ArrayType(self, a):
        a.typ = self.all[a.typ]

    def CvQualifiedType(self, attrs):
        # id, type, [const|volatile]
        typ = attrs["type"]
        const = attrs.get("const", None)
        volatile = attrs.get("volatile", None)
        return typedesc.CvQualifiedType(typ, const, volatile)

    def _fixup_CvQualifiedType(self, c):
        c.typ = self.all[c.typ]

    # callables
    
    def Function(self, attrs):
        # name, returns, extern, attributes
        name = self.demangle(attrs["name"])
        returns = attrs["returns"]
        attributes = attrs.get("attributes", "").split()
        extern = attrs.get("extern")
        return typedesc.Function(name, returns, attributes, extern)

    def _fixup_Function(self, func):
        func.returns = self.all[func.returns]
        func.arguments = [self.all[a] for a in func.arguments]

    def FunctionType(self, attrs):
        # id, returns, attributes
        returns = attrs["returns"]
        attributes = attrs.get("attributes", "").split()
        return typedesc.FunctionType(returns, attributes)
    
    def _fixup_FunctionType(self, func):
        func.returns = self.all[func.returns]
        func.arguments = [self.all[a] for a in func.arguments]

    def OperatorFunction(self, attrs):
        # name, returns, extern, attributes
        name = self.demangle(attrs["name"])
        returns = attrs["returns"]
        return typedesc.OperatorFunction(name, returns)

    def _fixup_OperatorFunction(self, func):
        func.returns = self.all[func.returns]

    def Constructor(self, attrs):
        name = self.demangle(attrs["name"])
        return typedesc.Constructor(name)

    def _fixup_Constructor(self, const): pass

    def Method(self, attrs):
        # name, virtual, pure_virtual, returns
        name = self.demangle(attrs["name"])
        returns = attrs["returns"]
        return typedesc.Method(name, returns)

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
        name = self.demangle(attrs["name"])
        size = attrs["size"]
        align = attrs["align"]
        if attrs.get("artificial"):
            # enum {} ENUM_NAME;
            return typedesc.Enumeration(name, size, align)
        else:
            # enum tagENUM {};
            enum = typedesc.Enumeration(None, size, align)
            self.artificial.append(typedesc.Typedef(name, enum))
            return enum

    def _fixup_Enumeration(self, e): pass

    def EnumValue(self, attrs):
        name = self.demangle(attrs["name"])
        value = attrs["init"]
        v = typedesc.EnumValue(name, value, self.context[-1])
        self.context[-1].add_value(v)
        return v

    def _fixup_EnumValue(self, e): pass

    # structures, unions

    def Struct(self, attrs):
        # id, name, members
        name = attrs.get("name")
        bases = attrs.get("bases", "").split()
        members = attrs.get("members", "").split()
##        abstract = attrs.get("abstract", "")
        align = attrs["align"]
        size = attrs.get("size")
        artificial = attrs.get("artificial")
        if name is None:
            name = self.demangle(attrs["mangled"]) # for debug only
##        if abstract:
##            return typedesc.Class(name, members, bases)
##        else:
        if artificial:
            return typedesc.Structure(name, align, members, bases, size)
        else:
##            struct = typedesc.Structure(name, align, members, bases, size)
            struct = typedesc.Structure(name, align, members, bases, size)
            self.artificial.append(typedesc.Typedef(name, struct))
            return struct

    def _fixup_Structure(self, s):
        s.members = [self.all[m] for m in s.members]
        s.bases = [self.all[b] for b in s.bases]
    _fixup_Union = _fixup_Structure

    def Union(self, attrs):
        name = attrs.get("name")
        bases = attrs.get("bases", "").split()
        members = attrs.get("members", "").split()
##        abstract = attrs.get("abstract", "")
        align = attrs["align"]
        size = attrs.get("size")
##        artificial = attrs.get("artificial")
        if name is None:
            name = self.demangle(attrs["mangled"]) # for debug only
        return typedesc.Union(name, align, members, bases, size)

    def Field(self, attrs):
        # name, type
        name = self.demangle(attrs["name"])
        typ = attrs["type"]
        bits = attrs.get("bits", None)
        offset = attrs.get("offset")
        return typedesc.Field(name, typ, bits, offset)

    def _fixup_Field(self, f):
        f.typ = self.all[f.typ]

    ################

    def _fixup_Macro(self, m):
        pass

    def get_macros(self, text):
        text = "".join(text)
        # preprocessor definitions that look like macros with one or more arguments
        for m in text.splitlines():
            name, body = m.split(None, 1)
            name, args = name.split("(", 1)
            args = "(%s" % args
            self.all[name] = typedesc.Macro(name, args, body)

    def get_aliases(self, text, namespace):
        # preprocessor definitions that look like aliases:
        #  #define A B
        text = "".join(text)
        aliases = {}
        for a in text.splitlines():
            name, value = a.split(None, 1)
            a = typedesc.Alias(name, value)
            aliases[name] = a
            self.all[name] = a

        for name, a in aliases.items():
            # the value should be either in namespace...
            value = a.alias
            if value in namespace:
                # set the type
                a.typ = namespace[value]
            # or in aliases...
            elif value in aliases:
                a.typ = aliases[value]
            # or unknown.
            else:
                # not known
                print "skip %s = %s" % (name, value)

    def get_result(self):
        interesting = (typedesc.Typedef, typedesc.Enumeration, typedesc.EnumValue,
                       typedesc.Function, typedesc.Structure, typedesc.Union,
                       typedesc.Variable, typedesc.Macro, typedesc.Alias)

        self.get_macros(self.cpp_data.get("functions"))

        remove = []
        for n, i in self.all.items():
            # link together all the nodes (the XML that gccxml generates uses this).
            mth = getattr(self, "_fixup_" + type(i).__name__)
            try:
                mth(i)
            except KeyError: # XXX better exception catching
                remove.append(n)
            else:
                location = getattr(i, "location", None)
                if location:
                    fil, line = location.split(":")
                    i.location = self.all[fil].name, line

        for n in remove:
            del self.all[n]

        # Now we can build the namespace.
        namespace = {}
        for i in self.all.values():
            if not isinstance(i, interesting):
                continue  # we don't want these
            name = getattr(i, "name", None)
            if name is not None:
                namespace[name] = i

        self.get_aliases(self.cpp_data.get("aliases"), namespace)

        result = []
        for i in self.artificial + self.all.values():
            if isinstance(i, interesting):
                result.append(i)


        # todo: get cpp_data, and convert it into typedesc nodes.
        # functions = self.cpp_data.get("functions")
        # aliases = self.cpp_data.get("aliases")

        return result

################################################################

def parse(xmlfile):
    # parse an XML file into a sequence of type descriptions
    handler = GCCXML_Handler()
    xml.sax.parse(xmlfile, handler)
    return handler.get_result()
