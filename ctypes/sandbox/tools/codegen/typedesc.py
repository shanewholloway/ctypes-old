# typedesc.py - classes representing C type descriptions
try:
    set
except NameError:
    from sets import Set as set

class _HasArgs(object):
    def add_argument(self, arg):
        self.arguments.append(arg)

################

class Function(_HasArgs):
    def __init__(self, name, returns, attributes, extern):
        self.name = name
        self.returns = returns
        self.attributes = attributes # dllimport, __stdcall__, __cdecl__
        self.arguments = []
        self.extern = extern

class Constructor(_HasArgs):
    def __init__(self, name):
        self.name = name
        self.arguments = []

class OperatorFunction(_HasArgs):
    def __init__(self, name, returns):
        self.name = name
        self.returns = returns
        self.arguments = []

class FunctionType(_HasArgs):
    def __init__(self, returns, attributes):
        self.returns = returns
        self.attributes = attributes
        self.arguments = []

class Method(_HasArgs):
    def __init__(self, name, returns):
        self.name = name
        self.returns = returns
        self.arguments = []

class FundamentalType(object):
    def __init__(self, name, size, align):
        self.name = name
        if name != "void":
            self.size = int(size)
            self.align = int(align)
        
class PointerType(object):
    def __init__(self, typ, size, align):
        self.typ = typ
        self.size = int(size)
        self.align = int(align)

class Typedef(object):
    def __init__(self, name, typ):
        self.name = name
        self.typ = typ

class ArrayType(object):
    def __init__(self, typ, min, max):
        self.typ = typ
        self.min = min
        self.max = max

class StructureHead(object):
    def __init__(self, struct):
        self.struct = struct

class StructureBody(object):
    def __init__(self, struct):
        self.struct = struct

class _Struct_Union_Base(object):
    def get_body(self):
        return self.struct_body

    def get_head(self):
        return self.struct_head

class Structure(_Struct_Union_Base):
    def __init__(self, name, align, members, bases, size, artificial=None):
        self.name = name
        self.align = int(align)
        self.members = members
        self.bases = bases
        self.artificial = artificial
        if size is not None:
            self.size = int(size)
        else:
            self.size = None
        self.struct_body = StructureBody(self)
        self.struct_head = StructureHead(self)

class Union(_Struct_Union_Base):
    def __init__(self, name, align, members, bases, size, artificial=None):
        self.name = name
        self.align = int(align)
        self.members = members
        self.bases = bases
        self.artificial = artificial
        if size is not None:
            self.size = int(size)
        else:
            self.size = None
        self.struct_body = StructureBody(self)
        self.struct_head = StructureHead(self)

class Field(object):
    def __init__(self, name, typ, bits, offset):
        self.name = name
        self.typ = typ
        self.bits = bits
        self.offset = int(offset)

class CvQualifiedType(object):
    def __init__(self, typ, const, volatile):
        self.typ = typ
        self.const = const
        self.volatile = volatile

class Enumeration(object):
    def __init__(self, name, size, align):
        self.name = name
        self.size = int(size)
        self.align = int(align)
        self.values = []

    def add_value(self, v):
        self.values.append(v)

class EnumValue(object):
    def __init__(self, name, value, enumeration):
        self.name = name
        self.value = value
        self.enumeration = enumeration

################################################################
