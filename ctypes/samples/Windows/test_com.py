def test2():
    from COM import CreateTypeLib, CoCreateGuid, ICreateTypeInfoPointer, SYS_WIN32
    from ctypes import byref
    ctl = CreateTypeLib(SYS_WIN32, "mylib.tlb")

    ctl.AddRef()
    ctl.Release()

    ctl.SetName(u"MyFirstTypeLib")
    ctl.SetDocString(u"Some silly docstring")
    ctl.SetVersion(0, 1)
    ctl.SetHelpFileName(u"myhelpfile.chm")
    ctl.SetHelpContext(12345678)
    ctl.SetLibFlags(1)
    ctl.SetGuid(byref(CoCreateGuid()))

    pcti = ICreateTypeInfoPointer()

    TKIND_COCLASS = 5

    ctl.CreateTypeInfo(u"MyTypeInfo", TKIND_COCLASS, byref(pcti))
    pcti.SetGuid(byref(CoCreateGuid()))
    pcti.LayOut()

    ctl.SaveAllChanges()

    print "typelib %s created" % "mylib.tlb"

if __name__ == '__main__':
    test2()
