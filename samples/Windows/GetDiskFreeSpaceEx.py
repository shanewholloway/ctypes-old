from ctypes import Structure, windll, WinError, byref
kernel32 = windll.kernel32

class ULARGE_INTEGER(Structure):
    _fields_ = [("value", "Q")]

    def __long__(self):
        return self.value

def test_ansi(drive):
    avail = ULARGE_INTEGER()
    total = ULARGE_INTEGER()
    totalfree = ULARGE_INTEGER()

    drive = str(drive)
    result = kernel32.GetDiskFreeSpaceExA(drive,
                                          byref(avail),
                                          byref(total),
                                          byref(totalfree)
                                          )
    if not result:
        raise WinError()
    return [avail.value, total.value, totalfree.value]
    
def test_unicode(drive):
    avail = ULARGE_INTEGER()
    total = ULARGE_INTEGER()
    totalfree = ULARGE_INTEGER()

    drive = unicode(drive)
    result = kernel32.GetDiskFreeSpaceExW(unicode(drive),
                                          byref(avail),
                                          byref(total),
                                          byref(totalfree))
    
    if not result:
        raise WinError()

##    return [long(avail), long(total), long(totalfree)]
    return [avail.value, total.value, totalfree.value]

try:
    from win32file import GetDiskFreeSpaceEx
except ImportError:
    GetDiskFreeSpaceEx = None

def test_win32file(drive):
    return GetDiskFreeSpaceEx(drive)

if __name__ == '__main__':
    drive = ""
    drive = "c:\\"
##    drive = "x:\\"
##    drive = r"\\server\setup\xx"
    print "ANSI"
    print test_ansi(drive)
    print

    print "UNICODE"
    print test_unicode(drive)
    print

    if GetDiskFreeSpaceEx is not None:
        print "win32file"
        print GetDiskFreeSpaceEx(drive)
