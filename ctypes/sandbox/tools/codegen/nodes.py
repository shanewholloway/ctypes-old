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
    return p

class PointerType(object):
    def __init__(self, typ):
        self.typ = typ

    def depends(self):
        return [get_pointed_to(self)]

    def __repr__(self):
        return "<POINTER(%s)>" % self.typ

class Typedef(object):
    def __init__(self, name, typ):
        self.name = name
        self.typ = typ

    def depends(self):
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

class Structure(object):
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

    def depends(self):
        result = set()
        if self.bases:
            result.update(self.bases)
        for m in self.members:
            result.update(m.depends())
        return result
        
    def __repr__(self):
        return "<Structure(%s) at %x>" % (self.name, id(self))

class Union(object):
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

    def depends(self):
        result = set()
        if self.bases:
            result.update(self.bases)
        for m in self.members:
            result.update(m.depends())
        return result

##class Class(object):
##    def __init__(self, name, members, bases):
##        self.name = name
##        self.members = members
##        self.bases = bases

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
