# from Paul Moore via comp.lang.python
from ctypes import windll, c_int, WinFuncType, c_char
user32 = windll.user32

EnumWindowsProc = WinFuncType(c_int, c_int, c_int)

def c_string(init, size=None):
    """c_string(aString) -> character array
    c_string(anInteger) -> character array
    c_string(aString, anInteger) -> character array
    """
    if isinstance(init, str):
        if size is None:
            size = len(init)+1
        buftype = c_char * size
        buf = buftype()
        buf.value = init
        return buf
    elif isinstance(init, int):
        buftype = c_char * init
        buf = buftype()
        return buf
    raise TypeError, init

def DisplayWindow(hwnd, lparam):
    title = c_string('\000' * 256)
    user32.GetWindowTextA(hwnd, title, 255)
    if title.value:
        print "%08x" % hwnd, repr(title.value)

enumproc = EnumWindowsProc(DisplayWindow)

if __name__ == '__main__':
    user32.EnumWindows(enumproc, 0)
