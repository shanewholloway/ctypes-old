# A sample COM server, implementing a dual interface.
#
# The interface is described in sum.idl, which must be compiled into
# the type libary sum.tlb with the MIDL compiler command 'midl /tlb
# sum.tlb sum.idl'.
#
# Next, the type library should be used to create the Python wrapper
# sum_gen.py. This can be done with the readtlb.py tool, with the
# command '..\..\tools\readtlb.py sum.tlb >sum_gen.py'.

# Then, we can import what we need from the sum_gen module:

# interface, coclass, typelib
from sum_gen import IDualSum, CSum, SumLib

# special code for this sample, to make sure sum_gen contains
# a valid path to the type library:
from ctypes.com.register import main_is_frozen
if not main_is_frozen():
    import os
    if not os.path.isfile(SumLib.path):
        raise RuntimeError, \
              "please recreate the sum_gen file or adjust the .tlb pathname"

# This object implements a dual interface described in a type library,
# and ctypes.com provides a handy bas class we can use:
from ctypes.com.automation import DualObjImpl
from ctypes.com.server import CLSCTX_LOCAL_SERVER, CLSCTX_INPROC_SERVER

class SumObject(DualObjImpl):
    # A sequence of COM interfaces this object implements
    _com_interfaces_ = [IDualSum]
    # The type library we need, SumLib has the correct attributes
    _typelib_ = SumLib
    # The progid for the registry
    _reg_progid_ = "ctypes.SumObject"
    # The name for the registry
    _reg_desc_ = "Sum Object"
    # and the clsid. We could use the one in the typelib, if the
    # typelib contains a CoClass. The typelib could as well only
    # describe an interface.
    _reg_clsid_ = CSum._reg_clsid_

    _reg_clsctx_ = CLSCTX_LOCAL_SERVER | CLSCTX_INPROC_SERVER

    # It is absolutely essential that you call the base class __init__
    # method if you override it here. The best way to do it is
    # probably with super():
    def __init__(self):
        super(SumObject, self).__init__()

    # We *should* implement the methods described in the typelib.  COM
    # servers receive an additional 'this' parameter, which is the COM
    # 'this' pointer (an integer), although we don't need it.
    #
    # The name of the COM method must either be
    # <interface_name>-<method_name> or simply <method_name>, but the
    # former is preferred to avoid name clashes if the object
    # implements a lot of interfaces.
    def IDualSum_Add(self, this, a, b, presult):
        # See the typelib, a and b are c_doubles converted to Python
        # floats, and presult is the result pointer which also points
        # to a c_double.
        presult[0] = a + b
        # The method must return a HRESULT, 0 is the same as S_OK
        return 0

def main():
    # Running this script with "-regserver" registers this object as a
    # LocalServer32 together with the type library, "-unregserver"
    # deletes the registry entries again.
    #
    # Note that the object will be registered to run with python.exe,
    # *not* pythonw.exe, so a console will be created when the object
    # is run. At least it is nice to see tracebacks if they occurr.
    #
    # You can start the object from Oleview for example, look under
    # Object Classes->All Objects->Sum Object to locate it.
    #
    # You can also (since it implements a dual interface) use it from win32com:
    #
    # from win32com.client import Dispatch
    # d = Dispatch("ctypes.SumObject")
    # print d.Add(3.14, 3.14)
    #
    # This script prints '6.28'.
    #
    from ctypes.com.server import UseCommandLine
    UseCommandLine(SumObject)

    
if __name__ == '__main__':
    main()
