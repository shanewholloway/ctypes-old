# ctypes client code, using the CSum COM object
from sum_gen import CSum
from ctypes.com import CreateInstance
from ctypes import c_double, byref

sum = CreateInstance(CSum)

result = c_double()
sum.Add(3.14, 3.14, byref(result))
print result
