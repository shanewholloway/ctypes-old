ctypes is a module allowing to create and manipulate C data types in
Python. These can then be passed to C-functions loaded from dynamic
link libraries.

This module is supposed to be a greatly enhanced and much more
complete replacement of Sam Rushing's calldll/npstruct/windll
modules. ctypes is not based on Sam's work, it has different roots.

It requires Python 2.2 or higher, since it makes intensive use of the
new type system.

For all platforms except Windows you'll need a recent version of
libffi which supports your processor.  Ronald Oussoren has kindly
assembled a snapshot of libffi taken from the GCC CVS repository which
works with this release, it is availabale for download from the ctypes
download page
http://sourceforge.net/project/showfiles.php?group_id=71702.

To install ctypes from source, unpack the distribution,
enter the ctypes-0.4.0 directory, and enter

  python setup.py install --help

to see the options available, then

  python setup.py install [options]

to install it.  If you want to run the unittests before, you should do

  python setup.py test

To install from the binary windows installer, make sure you download
the correct version depending on the Python version you use.

For Python 2.2, you need
    ctypes-0.4.0.win32-py2.2.exe

For Python 2.3, you need
    ctypes-0.4.0.win32-py2.3.exe 


----

It provides classes which can be used to create complicated C data
types, for example, those used in Windows type libraries.

Included is a facility to dynamically load DLLs, retrieve functions,
and call them. You can also call methods on COM objects.

Implemented are simple data types (int, char, string, and so on),
function pointers (callbacks), structures, unions, arrays, and
pointers.

ctypes uses win32 structured exception handling, to make it as safe as
possible, although it should be pretty clear that it's easy to crash
the Python interpreter with it.

The source distribution contains an extensive, although inclomplete,
tutorial (which you can also read online), as well as example scripts
demonstrating the use.

One of these scripts contains a dynamic Dispatch implementation, which
is used to drive MS word as an example.

----

Current version: 0.4.0

Homepage: http://starship.python.net/crew/theller/ctypes.html

License: MIT

Platforms: Windows, linux, MacOS X
