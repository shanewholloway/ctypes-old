README for the ctypes.com samples

sum.py is a COM localserver sample. It implements a dual interface
described in a typelibrary. The source code is extensively commented,
please refer to it.

In short: 

   sum.idl - the idl file describing the interface and the coclass.
   sum.tlb - the idl file compiled into a type library (with MIDL)
   sum_gen.py - the python wrapper created from the sum.tlb file.
	        This must be recreated, because it contains the absolute pathname.
   sum.py - the COM object implementation itself.

sum.py accepts the '-regserver' and '-unregserver' command line flags.
This will register or unregister the COM object and the type library.
It also accepts the '/automation' command line flag, this is used to
start the localserver, the object is registered with COM to receive
this flag.

sum.py can also be 'compiled' into an exe-file with py2exe, no special
flags needed. Use the 'setup_sum.py' file to build the exe.

The exe-file can be registered or unregistered with the same flags as
above.

Note: Currently py2exe cannot embed the type library into the
exe-file, and the registration will raise an exception.

Note2: If you are using ctypes from the CVS sandbox without installing
it, py2exe will not be able to build sum.exe correctly. This is
because py2exe is not able to simulate the magic which appears in the
ctypes\.CTYPES_DEVEL file. To build it anyway, you need to build and
(temporarily) install ctypes. Best would be to build a bdist_wininst
installer and run it, since you can remove it later very easily.

