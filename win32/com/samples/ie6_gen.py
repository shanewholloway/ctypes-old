# -*- python -*-
# Generated from C:\sf\ctypes_head\win32\com\samples\server\sum.tlb

###############################################################
# NOTE: This is a GENERATED file. Please do not make changes, #
# they will be overwritten next time it is regenerated.       #
###############################################################

from ctypes.com import IUnknown, GUID, STDMETHOD, HRESULT
from ctypes.com.automation import IDispatch, BSTR, VARIANT

from ctypes import POINTER, c_voidp, c_byte, c_ubyte, \
     c_short, c_ushort, c_int, c_uint, c_long, c_ulong, \
     c_float, c_double, Structure, byref, sizeof

class COMObject:
    # later this class will be used to create COM objects.
    pass

class enum(c_int):
    pass

OLECMDID = enum
OLECMDEXECOPT = enum

class dispinterface(IDispatch):
    class __metaclass__(type(IDispatch)):
        def __setattr__(self, name, value):
            if name == '_dispmethods_':
##                protos = []
                dispmap = {}
                for dispid, mthname, proto in value:
##                    protos.append(proto)
                    dispmap[dispid] = mthname
##                setattr(self, '_methods_', IDispatch._methods_ + protos)
                setattr(self, '_methods_', IDispatch._methods_)
                type(IDispatch).__setattr__(self, '_dispmap_', dispmap)
            type(IDispatch).__setattr__(self, name, value)

def DISPMETHOD(dispid, restype, name, *argtypes):
    return dispid, name, STDMETHOD(HRESULT, name, *argtypes)

##############################################################################

# The Type Library
class SumLib:
    'Sum 1.0 Type Library'
    guid = GUID('{90810CB9-D427-48B6-81FF-92D4A2098B45}')
    version = (1, 0)
    flags = 0x8
    path = 'C:\\sf\\ctypes_head\\win32\\com\\samples\\server\\sum.tlb'

##############################################################################

class IDualSum(IDispatch):
    """IDualSum Interface"""
    _iid_ = GUID('{6EDC65BF-0CB7-4B0D-9E43-11C655E51AE9}')


IDualSum._methods_ = IDispatch._methods_ + [
    (STDMETHOD(HRESULT, "Add", c_double, c_double, POINTER(c_double))),
]

##############################################################################

class CSum(COMObject):
    """CSum Class"""
    _reg_clsid_ = '{2E0504A1-1A23-443F-939D-869A6C731521}'
    _com_interfaces_ = [IDualSum]

