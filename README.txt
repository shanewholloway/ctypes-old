ctypes is a ffi (Foreign Function Interface) package for Python.

It allows to call functions exposed from dlls/shared libraries and has
extensive facilities to create, access and manipulate simpole and
complicated C data types transparently from Python - in other words:
wrap libraries in pure Python.

ctypes runs on Windows, MacOS X, Linux, Solaris.

On Windows, ctypes contains (the beginning of) a COM framework mainly
targetted to use and implement custom COM interfaces.

----

ctypes requires Python 2.2 or higher, since it makes intensive use of the
new type system.

For all platforms except Windows you'll need a very recent version of
libffi which supports your processor.

----

Unfortunately libffi is in a very sad state, there seem to be no
official releases recent enough to be used with ctypes (libffi-1.20 is
too old!).

Currently libffi is maintained in the GCC CVS tree. Ronald Oussoren
has kindly assembled a snapshot of libffi taken from the GCC CVS
repository which works with this release, it is available for download
from the ctypes download page
http://sourceforge.net/project/showfiles.php?group_id=71702.

----

To install ctypes from source, unpack the distribution,
enter the ctypes-0.6.x directory, and enter

  python setup.py install --help

to see the options available, then

  python setup.py install [options]

to install it.  If you want to run the unittests before, you should do

  python setup.py test

To install from the binary windows installer, make sure you download
the correct version depending on the Python version you use.

For Python 2.2, you need
    ctypes-0.6.x.win32-py2.2.exe

For Python 2.3, you need
    ctypes-0.6.x.win32-py2.3.exe 


----

On Windows, ctypes uses win32 structured exception handling, to make
it as safe as possible, although it should be pretty clear that it's
easy to crash the Python interpreter with it.

The source distribution contains an extensive, although inclomplete,
tutorial (which you can also read online), as well as example scripts
demonstrating the use.

----

Current version: 0.6.2

Homepage: http://starship.python.net/crew/theller/ctypes.html

License: MIT

Platforms: Windows, linux, MacOS X, solaris
