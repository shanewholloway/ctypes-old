from ctypes import windll, byref, Structure, Array
kernel32 = windll.kernel32

from ctypes import c_ushort, c_ubyte, c_ulong, c_char

BYTE = c_ubyte
WORD = c_ushort
DWORD = c_ulong

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
    _abstract_ = None
    _fields_ = None # only for pychecker
    
    def dump(self, indent="", INDENT="   "):
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

class SYSTEM_INFO(DStructure):
    _fields_ = [("wProcessorArchitecture", WORD),
                ("wReserved", WORD),
                ("dwPageSize", DWORD),
                ("lpMinimumApplicationAddress", DWORD),
                ("lpMaximumApplicationAddress", DWORD),
                ("dwActiveProcessorMask", DWORD),
                ("dwNumberOfProcessors", DWORD),
                ("dwProcessorType", DWORD),
                ("dwAllocationGranularity", DWORD),
                ("wProcessorLevel", WORD),
                ("wProcessorRevision", WORD)]


class SYSTEM_POWER_STATUS(DStructure):
    _fields_ = [("ACLineStatus", BYTE),
                ("BatteryFlag", BYTE),
                ("BatteryLifePercent", BYTE),
                ("Reserved1", BYTE),
                ("BatteryLifeTime", DWORD),
                ("BatteryFullLifeTime", DWORD)]

class SYSTEMTIME(DStructure):
    _fields_ = [("wYear", WORD),
                ("wMonth", WORD),
                ("wDayOfWeek", WORD),
                ("wDay", WORD),
                ("wHour", WORD),
                ("wMinute", WORD),
                ("wSecond", WORD),
                ("wMilliSeconds", WORD)]
    
class OSVERSIONINFO(DStructure):
    _fields_ = [("dwOSVersionInfoSize", DWORD),
                ("dwMajorVersion", DWORD),
                ("dwMinorVersion", DWORD),
                ("dwBuildNumber", DWORD),
                ("dwPlatformId", DWORD),
                ("szCSDVersion", STRING(128))]


if __name__ == '__main__':
    si = SYSTEM_INFO()
    kernel32.GetSystemInfo(byref(si))
    si.dump()

    sps = SYSTEM_POWER_STATUS()
    kernel32.GetSystemPowerStatus(byref(sps))
    sps.dump()

    st = SYSTEMTIME()
    kernel32.GetSystemTime(byref(st))
    st.dump()

    vi = OSVERSIONINFO()
##    import _ctypes
    from ctypes import sizeof
    size = sizeof(vi)
    vi.dwOSVersionInfoSize = size
    kernel32.GetVersionExA(byref(vi))
    vi.dump()
