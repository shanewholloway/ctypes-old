from ctypes import HRESULT, POINTER
from comtypes import BSTR

# COMMETHOD and DISPMETHOD return what's required to create
# WINFUNCTYPE templates and instances: (restype, name, argtypes)
#
# Calling WINFUNCTYPE with (restype, *argtypes) returns the template.
#
# Calling the template with (vtbl_index, name, class) returns an unbound method
# usable for client COM method class.
#
# Calling the template with (callable) returns a C callable usable as
# COM method implementation.

def COMMETHOD(idlflags, restype, name, *argtypes):
    # where do the idlflags go?
    if "propget" in idlflags:
        name = "_get_%s" % name
    elif "propput" in idlflags:
        name = "_set_%s" % name
    return restype, name, [a[2] for a in argtypes]

def DISPMETHOD(idlflags, restype, name, *argtypes):
    # where do the idlflags go?
    assert isinstance(idlflags[0], int)
    if restype is not None:
        argtypes = argtypes + ((["out"], "_result_", POINTER(restype)),)
    if "propget" in idlflags:
        name = "_get_%s" % name
    elif "propput" in idlflags:
        name = "_set_%s" % name
    argtypes = [a[2] for a in argtypes]
    return HRESULT, name, argtypes

def DISPPROPERTY(idlflags, typ, name):
    # fake
    return typ, name, []

