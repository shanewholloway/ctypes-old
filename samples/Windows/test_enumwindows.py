# from Paul Moore via comp.lang.python
from ctypes import windll, CFunction, CFuncPtr, c_string, c_int
user32 = windll.user32

class EnumWindowsProc(CFunction):
    _types_ = c_int, c_int
    _stdcall_ = 1

class EnumWindowsProc(CFuncPtr):
    _argtypes_ = c_int, c_int
    _flags_ = 0

def DisplayWindow(hwnd, lparam):
    title = c_string('\000' * 256)
    user32.GetWindowTextA(hwnd, title, 255)
    if title.value:
        print "%08x" % hwnd, repr(title.value)

enumproc = EnumWindowsProc(DisplayWindow)

if __name__ == '__main__':
    user32.EnumWindows(enumproc, 0)
