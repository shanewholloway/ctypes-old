# from Paul Moore via comp.lang.python
from ctypes import windll, c_string, c_int, STDAPI
user32 = windll.user32

EnumWindowsProc = STDAPI(c_int, c_int, c_int)

def DisplayWindow(hwnd, lparam):
    title = c_string('\000' * 256)
    user32.GetWindowTextA(hwnd, title, 255)
    if title.value:
        print "%08x" % hwnd, repr(title.value)

enumproc = EnumWindowsProc(DisplayWindow)

if __name__ == '__main__':
    user32.EnumWindows(enumproc, 0)
