from ctypes import windll, Structure, byref, GetLastError, WinError
kernel32 = windll.kernel32

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
    _fields_ = [("dwLowDateTime", "I"),
                ("dwHighDateTime", "I")]

class WIN32_FIND_DATA(DStructure):
    _fields_ = [("dwFileAttributes", "I"),
                ("ftCreationTime", FILETIME),
                ("ftLastAccessTime", FILETIME),
                ("ftLastWriteTime", FILETIME),
                ("nFileSizeLow", "I"),
                ("nFileSizeHigh", "I"),
                ("dwReserved0", "I"),
                ("dwReserved1", "I"),
                ("cFileName", "260s"), # MAX_PATH = 260
                ("cAlternateFileName", "14s")]


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
