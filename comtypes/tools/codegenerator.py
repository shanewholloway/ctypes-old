# Extended code generator able to generate code for everything
# contained in COM type libraries.

import typedesc
import ctypes.wrap.codegenerator

class Generator(ctypes.wrap.codegenerator.Generator):

    ################################################################
    # top-level typedesc generators
    #
    def CoClass(self, coclass):
        for itf, idlflags in coclass.interfaces:
            self.generate(itf)
        print >> self.stream, "class %s(CoClass):" % coclass.name
        doc = getattr(coclass, "doc", None)
        if doc:
            print >> self.stream, "    %r" % doc
        print >> self.stream, "    _clsid_ = GUID(%r)" % coclass.clsid
        print >> self.stream, "    _idlflags_ = %s" % coclass.idlflags
        implemented = [i[0].name for i in coclass.interfaces
                       if i[1] & 2 == 0]
        sources = [i[0].name for i in coclass.interfaces
                       if i[1] & 2]
        if implemented:
            print >> self.stream, "    _com_interfaces_ = [%s]" % ", ".join(implemented)
        if sources:
            print >> self.stream, "    _outgoing_interfaces_ = [%s]" % ", ".join(sources)
        print >> self.stream

    def ComInterface(self, itf):
        self.generate(itf.get_head())
        self.generate(itf.get_body())

    def ComInterfaceHead(self, head):
        self.generate(head.itf.base)
        basename = self.type_name(head.itf.base)
        print >> self.stream, "class %s(%s):" % (head.itf.name, basename)
        print >> self.stream, "    _iid_ = GUID(%r)" % head.itf.iid
        print >> self.stream, "    _idlflags_ = %s" % head.itf.idlflags

    def ComInterfaceBody(self, body):
        # make sure we can generate the body
        for m in body.itf.members:
            for a in m.arguments:
                self.generate(a[0])
            self.generate(m.returns)

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
        print >> self.stream, "class %s(%s):" % (head.itf.name, basename)
        doc = getattr(head.itf, "doc", None)
        if doc:
            print >> self.stream, "    %r" % doc
        print >> self.stream, "    _iid_ = GUID(%r)" % head.itf.iid
        print >> self.stream, "    _idlflags_ = %s" % head.itf.idlflags

        # code
        prop_map = {}
        for m in head.itf.members:
            is_property = self.make_DispMethodWrapper(m)
            if is_property is not None:
                name, kind = is_property
                prop_map.setdefault(name, []).append(kind)
        for name, kinds in prop_map.items():
            if "propget" in kinds:
                getter = "_get_%s" % name
            if "propput" in kinds:
                setter = "_set_%s" % name
            elif "propputref" in kinds:
                setter = "_putref_%s" % name
            else:
                setter = None
            print >> self.stream, "    %s = property(%s, %s)" % (name, getter, setter)
        print >> self.stream

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
                    arglist.append("( %r, '%s', %s, %r )" % (
                        idlflags,
                        name,
                        self.type_name(typ),
                        default))
                else:
                    arglist.append("( %r, '%s', %s )" % (
                        idlflags,
                        name,
                        self.type_name(typ)))
            self.stream.write(",\n              ".join(arglist))
            print >> self.stream, "),"

    def make_DispMethod(self, m):
        # typ, name, idlflags, default
        args = [self.type_name(a[0]) for a in m.arguments]
##        code = "    DISPMETHOD(%r,\n               %s, '%s'" % (
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
                    arglist.append("( %r, '%s', %s, %r )" % (
                        idlflags,
                        name,
                        self.type_name(typ),
                        default))
                else:
                    arglist.append("( %r, '%s', %s )" % (
                        idlflags,
                        name,
                        self.type_name(typ),
                        ))
            self.stream.write(",\n               ".join(arglist))
            print >> self.stream, "),"
##            print >> self.stream, "\n               ),"

    def make_DispProperty(self, prop):
        print >> self.stream, "    DISPPROPERTY(%r, %s, '%s')," % (
            [prop.dispid] + prop.idlflags,
            self.type_name(prop.typ),
            prop.name)

    ################################################################
    # Python method implementation generators.
    #
    def make_DispPropertyWrapper(self, p):
        type_name = self.type_name(p.typ)
        print >> self.stream, "    def _get_%s(self):" % p.name
        print >> self.stream, "        _result_ = %s()" % type_name
        print >> self.stream, "        self.__com_get_%s(byref(_result))" % p.name
        print >> self.stream, "        return _result_.value"
        getter = "_get_%s" % p.name

        if "readonly" in p.idlflags:
            setter = None
        else:
            setter = "_set_%s" % p.name
            print >> self.stream, "    def _set_%s(self, rhs):" % p.name
            print >> self.stream, "        self.__com_set_%s(rhs)" % p.name
        
        doc = getattr(p, "doc", None)
        print >> self.stream, "    %s = property(%s, %s, doc=%r)" % \
              (p.name, getter, setter, doc)
        print >> self.stream
        return None

    def make_DispMethodWrapper(self, m):
        if isinstance(m, typedesc.DispProperty):
            return self.DispPropertyWrapper(m)
        funcname = m.name
        if "propget" in m.idlflags:
            funcname = "_get_%s" % funcname
        elif "propput" in m.idlflags:
            funcname = "_set_%s" % funcname
        elif "propputref" in m.idlflags:
            funcname = "_putref_%s" % funcname
        else:
            pass
        args = m.arguments[:]
        if self.type_name(m.returns) != 'None': # return type != void
            typ = typedesc.PointerType(m.returns, 32, 32)
            args.append((typ, "_result_", ["out"], None)) # add with paramflag_fout

        inargs = []
        for typ, name, idlflags, default in args:
            if "in" in idlflags:
                if default is not None:
                    inargs.append("%s=%r" % (name, default))
                elif "optional" in idlflags:
                    inargs.append("%s=%s" % (name, "MISSING"))
                else:
                    inargs.append(name)

        allargs = []
        flocals = []
        for typ, name, idlflags, default in args:
            # XXX What about [in, out] parameters?
            if "out" in idlflags:
                assert isinstance(typ, typedesc.PointerType)
                flocals.append((name, self.type_name(typ.typ)))
                allargs.append("byref(%s)" % name)
            else:
                allargs.append(name)

        # Now that POINTER(<com_interface>) instances have a .value property
        # which returns the com pointer itself, we can do this FOR ALL types:
        outargs = ["%s.value" % name for (typ, name, idlflags, default) in args
                   if "out" in idlflags]

        print >> self.stream, "    def %s(%s):" % (funcname, ", ".join(["self"] + inargs))
        doc = getattr(m, "doc", None)
        if doc:
            print >> self.stream, "        %r" % doc
        for n, t in flocals:
            print >> self.stream, "        %s = %s()" % (n, t)
        if outargs:
            print >> self.stream, "        self.__com_%s(%s)" % (funcname, ", ".join(allargs))
            print >> self.stream, "        return %s" % ", ".join(outargs)
        else:
            print >> self.stream, "        return self.__com_%s(%s)" % (funcname, ", ".join(allargs))

        is_property = None
        # check if this could be a Python property
        if "propget" in m.idlflags:
            if len(inargs) == 0:
                # 'propget' can only be a Python property if it has no args
                is_property = m.name, "propget"
            else:
                print >> self.stream, "    %s = %s" % (m.name, funcname)
        elif "propput" in m.idlflags:
            if len(inargs) == 1:
                # 'propput' can only be a Python property if it has no args
                is_property = m.name, "propput"
            else:
                print >> self.stream, "    %s = %s" % (m.name, funcname)
        elif "propputref" in m.idlflags:
            if len(inargs) == 1:
                # 'propputref' can only be a Python property if it has no args
                # XXX 
                is_property = m.name, "propputref"
            else:
                print >> self.stream, "    %s = %s" % (m.name, funcname)

        print >> self.stream
        return is_property

# shortcut for development
if __name__ == "__main__":
    import tlbparser
    tlbparser.main()
    
