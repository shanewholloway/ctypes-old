from ctypes import windll, Structure, byref, GetLastError, WinError, c_uint, c_char
kernel32 = windll.kernel32

from ctypes import Array

# Not the recommended way...
# But what IS the recommended way?
def STRING(size):
    class S(Array):
        _type_ = c_char
        _length_ = size
        
        def __str__(self):
            return "".join(self).split("\0")[0]

        def __repr__(self):
            return repr(str(self))

    return S

class DStructure(Structure):
    _abstract_ = None # this is an abstract class
    _fields_ = None # only for pychecker
    
    def dump(self, indent=""):
        INDENT = "   "
        print "%s%s:" % (indent, self.__class__.__name__)
        for name, fmt in self._fields_:
            val = getattr(self, name)
            if isinstance(val, Structure):
                val.dump(indent + INDENT)
            elif isinstance(val, long) or isinstance(val, int):
                print "%s%30s: %s (0x%x)" % (indent, name, val, val)
            else:
                print "%s%30s: %r" % (indent, name, val)
        print

class FILETIME(DStructure):
    _fields_ = [("dwLowDateTime", c_uint),
                ("dwHighDateTime", c_uint)]

class WIN32_FIND_DATA(DStructure):
    _fields_ = [("dwFileAttributes", c_uint),
                ("ftCreationTime", FILETIME),
                ("ftLastAccessTime", FILETIME),
                ("ftLastWriteTime", FILETIME),
                ("nFileSizeLow", c_uint),
                ("nFileSizeHigh", c_uint),
                ("dwReserved0", c_uint),
                ("dwReserved1", c_uint),
                ("cFileName", STRING(260)), #c_char * 260), # MAX_PATH = 260
                ("cAlternateFileName", STRING(14))]


ERROR_NO_MORE_FILES = 18

def test_findfiles(mask):
    wfd = WIN32_FIND_DATA()
    handle = kernel32.FindFirstFileA(mask, byref(wfd))
    if handle == -1:
        raise WinError()
    print "HANDLE", handle
    wfd.dump()

    try:
        while 1:
            res = kernel32.FindNextFileA(handle, byref(wfd))
            if not res:
                if ERROR_NO_MORE_FILES == GetLastError():
                    break
                else:
                    raise WinError()
            wfd.dump()

    finally:
        kernel32.FindClose(handle)

if __name__ == '__main__':
    test_findfiles(r"c:\*.exe")
