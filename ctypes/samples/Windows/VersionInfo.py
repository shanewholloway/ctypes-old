# modeled after ASPN recipe by Dan Rolander (?), which uses calldll

from ctypes import c_string, c_int, windll, sizeof, WinError, byref, c_char_p
from ctypes import pointer, POINTER
from ctypes import Structure

from ctypes import c_ushort, c_ubyte, c_ulong, c_char

BYTE = c_ubyte
WORD = c_ushort
DWORD = c_ulong

def dump(data, indent=""):
    INDENT = "   " + indent
    print "%s%s:" % (indent, data.__class__.__name__)
    for name, fmt in data._fields_:
        val = getattr(data, name)
        if isinstance(val, Structure):
            val.dump(INDENT)
        elif isinstance(val, long) or isinstance(val, int):
            print "%s%30s: %s (0x%x)" % (indent, name, val, val)
        else:
            print "%s%30s: %r" % (indent, name, val)
    print

class VS_FIXEDFILEINFO(Structure):
    _fields_ = [("dwSignature", DWORD), # will be 0xFEEF04BD
                ("dwStrucVersion", DWORD),
                ("dwFileVersionMS", DWORD),
                ("dwFileVersionLS", DWORD),
                ("dwProductVersionMS", DWORD),
                ("dwProductVersionLS", DWORD),
                ("dwFileFlagsMask", DWORD),
                ("dwFileFlags", DWORD),
                ("dwFileOS", DWORD),
                ("dwFileType", DWORD),
                ("dwFileSubtype", DWORD),
                ("dwFileDateMS", DWORD),
                ("dwFileDateLS", DWORD)]

def get_file_version(filename):
    verinfosize = windll.version.GetFileVersionInfoSizeA(filename, 0)
    if not verinfosize:
        raise WinError()

    buffer = c_string("\000"*verinfosize)
    windll.version.GetFileVersionInfoA(filename, 0, buffer._b_size_, buffer)

    ffi = VS_FIXEDFILEINFO()
    uLen = c_int()

    lpffi = POINTER(VS_FIXEDFILEINFO) ()
##    windll.version.VerQueryValueA.argtypes = [c_string,
##                                              c_char_p,
##                                              POINTER(POINTER(VS_FIXEDFILEINFO)),
##                                              POINTER(c_int)]
    res = windll.version.VerQueryValueA(buffer,
                                 "\\",
                                 pointer(lpffi),
                                 pointer(uLen))
    if not res:
        raise WinError()

    ffi = lpffi.contents
    # ffi shares memory from buffer, so we must keep a reference to it:
    ffi._buffer = buffer
        
    return ffi

if __name__ == '__main__':
    import os.path
    path = c_string(256)
    windll.kernel32.GetSystemDirectoryA(path, sizeof(path))
    file = os.path.join(path.value, "notepad.exe")

    vsfileinfo = get_file_version(file)
    dump(vsfileinfo)
