# More type descriptions from parsed COM typelibaries.

from ctypes.wrap.typedesc import *

class ComMethod(object):
    # custom COM method, parsed from typelib
    def __init__(self, invkind, name, returns, idlflags):
        self.invkind = invkind
        self.name = name
        self.returns = returns
        self.idlflags = idlflags
        self.arguments = []

    def add_argument(self, typ, name, idlflags, default):
        self.arguments.append((typ, name, idlflags, default))

class DispMethod(object):
    # dispatchable COM method, parsed from typelib
    def __init__(self, dispid, invkind, name, returns, idlflags):
        self.dispid = dispid
        self.invkind = invkind
        self.name = name
        self.returns = returns
        self.idlflags = idlflags
        self.arguments = []

    def add_argument(self, typ, name, idlflags, default):
        self.arguments.append((typ, name, idlflags, default))

class DispProperty(object):
    # dispatchable COM property, parsed from typelib
    def __init__(self, dispid, name, typ, idlflags):
        self.dispid = dispid
        self.name = name
        self.typ = typ
        self.idlflags = idlflags

class DispInterfaceHead(object):
    def __init__(self, itf):
        self.itf = itf

class DispInterfaceBody(object):
    def __init__(self, itf):
        self.itf = itf

class DispInterface(object):
    def __init__(self, name, members, base, iid, idlflags):
        self.name = name
        self.members = members
        self.base = base
        self.iid = iid
        self.idlflags = idlflags
        self.itf_head = DispInterfaceHead(self)
        self.itf_body = DispInterfaceBody(self)
        
    def get_body(self):
        return self.itf_body

    def get_head(self):
        return self.itf_head

class ComInterfaceHead(object):
    def __init__(self, itf):
        self.itf = itf

class ComInterfaceBody(object):
    def __init__(self, itf):
        self.itf = itf

class ComInterface(object):
    def __init__(self, name, members, base, iid, idlflags):
        self.name = name
        self.members = members
        self.base = base
        self.iid = iid
        self.idlflags = idlflags
        self.itf_head = ComInterfaceHead(self)
        self.itf_body = ComInterfaceBody(self)
        
    def get_body(self):
        return self.itf_body

    def get_head(self):
        return self.itf_head

class CoClass(object):
    def __init__(self, name, clsid, idlflags):
        self.name = name
        self.clsid = clsid
        self.idlflags = idlflags
        self.interfaces = []

    def add_interface(self, itf, idlflags):
        self.interfaces.append((itf, idlflags))

