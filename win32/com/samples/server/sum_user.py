# ctypes client code, using the CSum COM object
from ctypes import *
from ctypes.com import CreateInstance
from ctypes.com.automation import IDispatch
from sum_gen import CSum

sum = CreateInstance(CSum)
result = c_double()
sum.Add(3.14, 3.14, byref(result))
print "Added 3.14 and 3.14, result", result.value

idisp = pointer(IDispatch())

sum.QueryInterface(byref(IDispatch._iid_), byref(idisp))

count = c_uint()
idisp.GetTypeInfoCount(byref(count))
print "Has Typeinfo?", count.value
