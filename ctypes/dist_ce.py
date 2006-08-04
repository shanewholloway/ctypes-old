#
# This script creates dist/ctypes-2.4-arm.zip.
#

import os, fnmatch, zipfile, tempfile

README = """\
This is ctypes for Python CE 2.4, for ARM based Pocket PC.

To install ctypes on the Pocket PC, copy the files in this archive
into the \Program Files\Python24 directory on the mobile device.

Files:
    _ctypes.pyd - the ctypes extension module
    ctypes.zip - the ctypes Python modules (.py files)
    ctypes.pth - puts ctypes.zip on sys.path
    README - this file
"""

# the ctypes python modules
handle, pathname = tempfile.mkstemp()
os.close(handle)

pyarc = zipfile.ZipFile(pathname, "w")
for dirpath, dirnames, files in os.walk("ctypes"):
    files = fnmatch.filter(files, "*.py")
    for f in files:
        pyarc.write(os.path.join(dirpath, f))
pyarc.close()

arc = zipfile.ZipFile(r"dist\ctypes-2.4-arm.zip", "w")
arc.write(pathname, "ctypes.zip")
os.remove(pathname)

arc.writestr("ctypes.pth", "ctypes.zip")
arc.write(r"wince\ARMV4Rel\_ctypes.pyd", "_ctypes.pyd")
arc.write(r"wince\_ctypes_test\ARMV4Rel\_ctypes_test.pyd", "_ctypes_test.pyd")
arc.writestr("README", README.replace("\n", "\r\n"))
arc.close()
