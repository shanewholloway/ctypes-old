"""xml2py - create ctypes module from XML file"""
import sys
import xml.sax
from sets import Set
import nodes

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

def parse(xmlfile, options=None, verbose=0):
    handler = GCCXML_Handler()
    xml.sax.parse(xmlfile, handler)
    return handler.get_result()

