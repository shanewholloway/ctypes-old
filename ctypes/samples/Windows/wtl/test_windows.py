from windows import *
from gdi import *

WND_CLASS_NAME = "TestWindowClass"
hInstance = GetModuleHandle(0)

def wndProc(hWnd, nMsg, wParam, lParam):
    if nMsg == WM_DESTROY:
        PostQuitMessage(0)
        return 0
    else:
        return DefWindowProc(hWnd, nMsg, wParam, lParam)
    
cls = WNDCLASSEX()
cls.cbSize = 48
cls.lpszClassName = WND_CLASS_NAME
cls.hInstance = hInstance
cls.lpfnWndProc = WndProc(wndProc)
cls.style = CS_HREDRAW | CS_VREDRAW
cls.hbrBackground = GetStockObject(WHITE_BRUSH)
cls.hIcon = LoadIcon(0, IDI_APPLICATION)
cls.hIconSm = LoadIcon(0, IDI_APPLICATION)
cls.hCursor = LoadCursor(0, IDC_ARROW)


atom = RegisterClassEx(byref(cls))
hWnd = CreateWindowEx(0,
                      WND_CLASS_NAME,
                      "Test Window",
                      WS_OVERLAPPEDWINDOW,
                      10,
                      10,
                      320,
                      200,
                      0,
                      0,
                      0,
                      0)


ShowWindow(hWnd, SW_SHOW)
UpdateWindow(hWnd)

msg = MSG()
lpmsg = byref(msg)

while GetMessage(lpmsg, 0, 0, 0):
    TranslateMessage(lpmsg)
    DispatchMessage(lpmsg)
    



                              


