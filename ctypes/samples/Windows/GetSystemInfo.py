from ctypes import windll, byref, Structure
kernel32 = windll.kernel32

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
    _fields_ = [("wProcessorArchitecture", "h"),
                ("wReserved", "h"),
                ("dwPageSize", "i"),
                ("lpMinimumApplicationAddress", "i"),
                ("lpMaximumApplicationAddress", "i"),
                ("dwActiveProcessorMask", "i"),
                ("dwNumberOfProcessors", "i"),
                ("dwProcessorType", "i"),
                ("dwAllocationGranularity", "i"),
                ("wProcessorLevel", "h"),
                ("wProcessorRevision", "h")]


class SYSTEM_POWER_STATUS(DStructure):
    _fields_ = [("ACLineStatus", "b"),
                ("BatteryFlag", "b"),
                ("BatteryLifePercent", "b"),
                ("Reserved1", "b"),
                ("BatteryLifeTime", "i"),
                ("BatteryFullLifeTime", "i")]

class SYSTEMTIME(DStructure):
    _fields_ = [("wYear", "h"),
                ("wMonth", "h"),
                ("wDayOfWeek", "h"),
                ("wDay", "h"),
                ("wHour", "h"),
                ("wMinute", "h"),
                ("wSecond", "h"),
                ("wMilliSeconds", "h")]
    
class OSVERSIONINFO(DStructure):
    _fields_ = [("dwOSVersionInfoSize", "L"),
                ("dwMajorVersion", "L"),
                ("dwMinorVersion", "L"),
                ("dwBuildNumber", "L"),
                ("dwPlatformId", "L"),
                ("szCSDVersion", "128s")]


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
