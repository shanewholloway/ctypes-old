import ctypes
import comtypes
import comtypes.automation
import comtypes.automation.typeinfo

################################################################

def get_type(ti, tdesc):
    # Return an (approximate) ctype for a typedesc
    if tdesc.vt == 26:
        return ctypes.POINTER(get_type(ti, tdesc._.lptdesc[0]))
    if tdesc.vt == 29:
        ta = ti.GetRefTypeInfo(tdesc._.hreftype).GetTypeAttr()
        typ = {0: ctypes.c_int, # TKIND_ENUM
               # XXX ? TKIND_RECORD, TKIND_MODULE, TKIND_COCLASS, TKIND_ALIAS, TKIND_UNION
               3: comtypes.IUnknown, # TKIND_INTERFACE
               4: comtypes.automation.IDispatch # TKIND_DISPATCH
               }[ta.typekind]
        return typ
    return comtypes.automation.VT2CTYPE[tdesc.vt]

def param_info(ti, ed):
    # Return a tuple (flags, type) or (flags, type, default)
    # from an ELEMDESC instance.
    flags = ed._.paramdesc.wParamFlags
    typ = get_type(ti, ed.tdesc)
    if flags & comtypes.automation.typeinfo.PARAMFLAG_FHASDEFAULT:
        var = ed._.paramdesc.pparamdescex[0].varDefaultValue
        return flags, typ, var.value
    return flags, typ

def method_proto(name, ti, fd):
    # return resulttype, argtypes, paramflags for a com method
    assert fd.funckind == comtypes.automation.typeinfo.FUNC_PUREVIRTUAL, fd.funckind # FUNC_PUREVIRTUAL
##    names = ti.GetNames(fd.memid, fd.cParams + 1)
    restype = param_info(ti, fd.elemdescFunc)[1] # result type of com method
    argtypes = [] # argument types of com method
    parmflags = []
    for i in range(fd.cParams):
        # flags, typ[, default]
        flags, typ = param_info(ti, fd.lprgelemdescParam[i])
        argtypes.append(typ)
        parmflags.append(flags)
    proto = comtypes.COMMETHODTYPE(restype, tuple(argtypes), tuple(parmflags))
    return proto

# XXX Merge _ComMethod and _ComProperty.
# Retrieve proto lazy in __call__, __setitem__, __getitem__
class _ComBase(object):
    def __init__(self, obj, oVft, name, proto):
        self.comobj = obj._comobj
        self.typecomp = obj._typecomp
        self.typeinfo = obj._typeinfo
        self.comcall = proto(oVft, name)
        self.name = name

    def do_call(self, comcall, *args, **kw):
        retvals = []
        for index, x in enumerate(comcall.parmflags):
            if x & 2: # PARAMFLAG_FOUT
                typ = comcall.argtypes[index]._type_
                inst = typ()
                args = args[:index] + (ctypes.byref(inst),) + args[index:]
                retvals.append(inst)
        result = comcall(self.comobj, *args, **kw)
        if retvals:
            result = tuple([x.value for x in retvals])
            if len(result) == 1:
                result = result[0]
        return result

class _ComMethod(_ComBase):
    def __call__(self, *args, **kw):
        # type 1
        return self.do_call(self.comcall, *args, **kw)

class _ComProperty(_ComBase):
    def __getitem__(self, args):
        # type 2
        if not isinstance(args, tuple):
            args = (args,)
        return self.do_call(self.comcall, *args)

    def __setitem__(self, index, value):
        # type 4
        kind, desc = self.typecomp.Bind(self.name, 4)
        assert kind == "function"
        proto = method_proto(self.name, self.typeinfo, desc)
        comcall = proto(desc.oVft/4, self.name)
        if isinstance(index, tuple):
            args = index + (value,)
        else:
            args = (index, value)
        self.do_call(comcall, *args)

    def set(self, value):
        self.comcall(self.comobj, value)

def get_custom_interface(comobj, typeinfo):
    if typeinfo is None:
        typeinfo = comobj.GetTypeInfo()
    ta = typeinfo.GetTypeAttr()
    if ta.typekind == comtypes.automation.typeinfo.TKIND_INTERFACE:
        # everything ok
        return typeinfo, comobj
    if ta.typekind == comtypes.automation.typeinfo.TKIND_DISPATCH:
        # try to get the dual interface portion from a dispatch interface
        href = typeinfo.GetRefTypeOfImplType(-1)
        typeinfo = typeinfo.GetRefTypeInfo(href)
        ta = typeinfo.GetTypeAttr()
        if ta.typekind != comtypes.automation.typeinfo.TKIND_INTERFACE:
            # it didn't work
            raise TypeError, "could not get custom interface"
        # we must QI for this interface, but using IDispatch
        iid = ta.guid
        comobj = comobj.QueryInterface(comtypes.automation.IDispatch, iid)
        return typeinfo, comobj
    raise TypeError, "could not get custom interface"

class _Dynamic(object):
    def __init__(self, comobj, typeinfo=None):
        typeinfo, comobj = get_custom_interface(comobj, typeinfo)
        self.__dict__["_typeinfo"] = typeinfo
        self.__dict__["_typecomp"] = self._typeinfo.GetTypeComp()
        self.__dict__["_comobj"] = comobj
        
    def __getattr__(self, name):
        kind, desc = self._typecomp.Bind(name, 1 + 2) # only METHOD and PROPGET
        if kind == "function":
            proto = method_proto(name, self._typeinfo, desc)
            if desc.invkind == 2:
                if not [f for f in proto.parmflags if f & 1]:
                    # does not need "in" args -> invoke it
                    mth = _ComMethod(self, desc.oVft/4, name, proto)
                    return mth()
                # We should also try to bind PROPPUT and PROPPUTREF,
                # when _ComProperty.__setitem__ is called.  For this,
                # we need self._typecomp in _ComProperty.
                prop = _ComProperty(self, desc.oVft/4, name, proto)
                return prop
            mth = _ComMethod(self, desc.oVft/4, name, proto)
            self.__dict__[name] = mth
            return mth
        raise AttributeError, name

    def __setattr__(self, name, value):
        kind, desc = self._typecomp.Bind(name, 4)
        if kind == "function":
            proto = method_proto(name, self._typeinfo, desc)
            prop = _ComProperty(self, desc.oVft/4, name, proto)
            prop.set(value)
            return
        raise "NYI"

################################################################

def ActiveXObject(progid,
                  interface=comtypes.automation.IDispatch,
                  clsctx=comtypes.CLSCTX_ALL):
    # XXX Should we also allow GUID instances for the first parameter?
    # Or strings containing guids?
    clsid = comtypes.GUID.from_progid(progid)
    p = comtypes.CoCreateInstance(clsid, interface=interface, clsctx=clsctx)
    return _Dynamic(p)
