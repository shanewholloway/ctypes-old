# Extended code generator able to generate code for everything
# contained in COM type libraries.

import typedesc
import ctypes.wrap.codegenerator

class Generator(ctypes.wrap.codegenerator.Generator):

    ################################################################
    # top-level typedesc generators
    #
    def CoClass(self, coclass):
        self.need_GUID()
        print >> self.stream, "class %s(CoClass):" % coclass.name
        doc = getattr(coclass, "doc", None)
        if doc:
            print >> self.stream, "    %r" % doc
        print >> self.stream, "    _clsid_ = GUID(%r)" % coclass.clsid
        print >> self.stream, "    _idlflags_ = %s" % coclass.idlflags
        for itf, idlflags in coclass.interfaces:
            self.generate(itf)
        implemented = [i[0].name for i in coclass.interfaces
                       if i[1] & 2 == 0]
        sources = [i[0].name for i in coclass.interfaces
                       if i[1] & 2]
        if implemented:
            print >> self.stream, "%s._com_interfaces_ = [%s]" % (coclass.name, ", ".join(implemented))
        if sources:
            print >> self.stream, "%s._outgoing_interfaces_ = [%s]" % (coclass.name, ", ".join(sources))
        print >> self.stream

    def ComInterface(self, itf):
        self.generate(itf.get_head())
        self.generate(itf.get_body())

    def ComInterfaceHead(self, head):
        self.generate(head.itf.base)
        basename = self.type_name(head.itf.base)

        self.need_GUID()
        print >> self.stream, "class %s(%s):" % (head.itf.name, basename)
        print >> self.stream, "    _iid_ = GUID(%r)" % head.itf.iid
        print >> self.stream, "    _idlflags_ = %s" % head.itf.idlflags

    def ComInterfaceBody(self, body):
        # make sure we can generate the body
        for m in body.itf.members:
            for a in m.arguments:
                self.generate(a[0])
            self.generate(m.returns)

        self.need_COMMETHOD()
        print >> self.stream, "%s._methods_ = [" % body.itf.name
        for m in body.itf.members:
            if isinstance(m, typedesc.ComMethod):
                self.make_ComMethod(m)
            else:
                raise TypeError, "what's this?"
        print >> self.stream, "]"

    def DispInterface(self, itf):
        self.generate(itf.get_head())
        self.generate(itf.get_body())

    def DispInterfaceHead(self, head):
        self.generate(head.itf.base)
        basename = self.type_name(head.itf.base)

        self.need_GUID()
        print >> self.stream, "class %s(%s):" % (head.itf.name, basename)
        doc = getattr(head.itf, "doc", None)
        if doc:
            print >> self.stream, "    %r" % doc
        print >> self.stream, "    _iid_ = GUID(%r)" % head.itf.iid
        print >> self.stream, "    _idlflags_ = %s" % head.itf.idlflags

    def DispInterfaceBody(self, body):
        # make sure we can generate the body
        for m in body.itf.members:
            if isinstance(m, typedesc.DispMethod):
                for a in m.arguments:
                    self.generate(a[0])
                self.generate(m.returns)
            elif isinstance(m, typedesc.DispProperty):
                self.generate(m.typ)
            else:
                raise TypeError, m

        print >> self.stream, "%s._methods_ = [" % body.itf.name
        for m in body.itf.members:
            if isinstance(m, typedesc.DispMethod):
                self.make_DispMethod(m)
            elif isinstance(m, typedesc.DispProperty):
                self.make_DispProperty(m)
            else:
                raise TypeError, m
        print >> self.stream, "]"

    ################################################################
    # non-toplevel method generators
    #
    def make_ComMethod(self, m):
        # typ, name, idlflags, default
        args = [self.type_name(a[0]) for a in m.arguments]
        code = "    COMMETHOD(%r, %s, '%s'" % (
            m.idlflags,
            self.type_name(m.returns),
            m.name)
        
        if not m.arguments:
            print >> self.stream, "%s)," % code
        else:
            print >> self.stream, "%s," % code
            self.stream.write("              ")
            arglist = []
            for typ, name, idlflags, default in m.arguments:
                if default is not None:
                    arglist.append("( %r, '%s', %r )" % (
                        idlflags,
                        self.type_name(typ),
                        name,
                        default))
                else:
                    arglist.append("( %r, %s, '%s' )" % (
                        idlflags,
                        self.type_name(typ),
                        name))
            self.stream.write(",\n              ".join(arglist))
            print >> self.stream, "),"

    def make_DispMethod(self, m):
        # typ, name, idlflags, default
        args = [self.type_name(a[0]) for a in m.arguments]
        code = "    DISPMETHOD(%r, %s, '%s'" % (
            [m.dispid] + m.idlflags,
            self.type_name(m.returns),
            m.name)

        if not m.arguments:
            print >> self.stream, "%s)," % code
        else:
            print >> self.stream, "%s," % code
            self.stream.write("               ")
            arglist = []
            for typ, name, idlflags, default in m.arguments:
                if default is not None:
                    arglist.append("( %r, %s, '%s', %r )" % (
                        idlflags,
                        self.type_name(typ),
                        name,
                        default))
                else:
                    arglist.append("( %r, %s, '%s' )" % (
                        idlflags,
                        self.type_name(typ),
                        name,
                        ))
            self.stream.write(",\n               ".join(arglist))
            print >> self.stream, "),"

    def make_DispProperty(self, prop):
        print >> self.stream, "    DISPPROPERTY(%r, %s, '%s')," % (
            [prop.dispid] + prop.idlflags,
            self.type_name(prop.typ),
            prop.name)

# shortcut for development
if __name__ == "__main__":
    import tlbparser
    tlbparser.main()
