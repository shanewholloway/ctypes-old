# win32com client code to use the CSum COM object

from win32com.client import Dispatch
d = Dispatch("ctypes.SumObject")
print d.Add(3.14, 3.14)
