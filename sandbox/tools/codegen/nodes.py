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

    def depends(self):
        result = set(self.arguments)
        result.add(self.returns)
        return result

class Constructor(_HasArgs):
    def __init__(self, name):
        self.name = name
        self.arguments = []

    def depends(self):
        return []

class OperatorFunction(_HasArgs):
    def __init__(self, name, returns):
        self.name = name
        self.returns = returns
        self.arguments = []

class FunctionType(_HasArgs):
    def __init__(self, returns):
        self.returns = returns
        self.arguments = []

    def depends(self):
        result = set(self.arguments)
        result.add(self.returns)
        return result

class Method(_HasArgs):
    def __init__(self, name, returns):
        self.name = name
        self.returns = returns
        self.arguments = []

    def depends(self):
        result = set(self.arguments)
        result.add(self.returns)
        return result

class FundamentalType(object):
    def __init__(self, name):
        self.name = name
        
    def depends(self):
        return []

    def __repr__(self):
        return "<FundamentalType(%s)>" % self.name

def get_pointed_to(p):
    # if p is a pointer, return the end of the chain pointed to.
    if isinstance(p, PointerType):
        return get_pointed_to(p.typ)
    elif isinstance(p, CvQualifiedType):
        return get_pointed_to(p.typ)
    elif isinstance(p, Typedef):
        return get_pointed_to(p.typ)
    return p

class PointerType(object):
    def __init__(self, typ):
        self.typ = typ

    def depends(self):
        # Well, if the pointer points to a structure or union,
        # we don't need the complete struct or union definition.
        # The header will suffice.
        t = get_pointed_to(self)
        if type(t) in (Structure, Union):
            return [t.get_head()]
        return [t]

    def __repr__(self):
        return "<POINTER(%s)>" % self.typ

class Typedef(object):
    def __init__(self, name, typ):
        self.name = name
        self.typ = typ

    def depends(self):
        if type(self.typ) in (Structure, Union):
            return [self.typ.get_head()]
        return [self.typ]

    def __repr__(self):
        return "<Typedef(%s) at %x>" % (self.name, id(self))

class ArrayType(object):
    def __init__(self, typ, min, max):
        self.typ = typ
        self.min = min
        self.max = max

    def depends(self):
        return [self.typ]

    def __repr__(self):
        return "<Array(%s[%s]) at %x>" % (self.typ, self.max, id(self))

# Structures (and Unions, as well) are split into three objects.
# Structure depends on StructureHead and StructureBody
# StructureHead depends on bases,
# StructureBody depends on head and members.
#
# Pointer to Structure depends on StructureHead only

class StructureHead(object):
    def __init__(self, struct):
        self.struct = struct

    def depends(self):
        # XXX Hm, does it depend on bases, or does it depends on the bases' head?
        return self.struct.bases

class StructureBody(object):
    def __init__(self, struct):
        self.struct = struct

    def depends(self):
        result = set()
        # needed, so that the head is defined before the body
        result.add(self.struct.get_head())
        for m in self.struct.members:
            if type(m) is Field:
                result.add(m.typ)
            if type(m) is Method:
                result.update(m.depends())
        return result

    def __repr__(self):
        return "<StructureBody(%s) at %x>" % (self.struct.name, id(self))

class _Struct_Union_Base(object):
    def depends(self):
        return [self.struct_head, self.struct_body]
        
    def get_body(self):
        return self.struct_body

    def get_head(self):
        return self.struct_head

    def __repr__(self):
        return "<%s(%s) at %x>" % (self.__class__.__name__, self.name, id(self))

class Structure(_Struct_Union_Base):
    def __init__(self, name, align, members, bases, size, artificial=None):
        self.name = name
        assert int(align) % 8 == 0
        self.align = int(align) / 8
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
        assert int(align) % 8 == 0
        self.align = int(align) / 8
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
        self.offset = offset

    def depends(self):
        return [self.typ]

class CvQualifiedType(object):
    def __init__(self, typ, attrib):
        self.typ = typ
        self.attrib = attrib

    def depends(self):
        return self.typ.depends()

class Enumeration(object):
    def __init__(self, name):
        self.name = name
        self.values = []

    def add_value(self, name, value):
        self.values.append((name, value))

    def depends(self):
        return []

################################################################
