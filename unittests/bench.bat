@echo off
echo ****************************************************************
echo ***                 a simple ctypes benchmark                ***
echo *** normal extension functions are first, then the dll calls ***
echo ****************************************************************
echo.
echo *** func('abc', 3):
timeit %* -s "import ctypes" -s "from _ctypes_test import func_si" "func_si('abc', 3)"
timeit %* -s "from ctypes import cdll; import _ctypes_test; func=cdll[_ctypes_test.__file__]._py_func_si" "func('abc', 3)"
echo.

echo *** func():
timeit %* -s "import ctypes; from _ctypes_test import func" "func()"
timeit %* -s "from ctypes import cdll; import _ctypes_test; func=cdll[_ctypes_test.__file__]._py_func" "func('abc', 3)"
