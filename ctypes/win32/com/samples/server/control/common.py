from ctypes import *
from ctypes.wintypes import DWORD, HANDLE, HWND
import random

################################################################

user32 = windll.user32
gdi32 = windll.gdi32

# fake
void = c_int

TIMERPROC = WINFUNCTYPE(void, HWND, c_uint, c_uint, DWORD)

def RGB(red, green, blue):
    return (blue << 16) + (green << 8) + red

yellow_brush = gdi32.CreateSolidBrush(RGB(255, 255, 0))
green_brush = gdi32.CreateSolidBrush(RGB(0, 255, 0))
red_brush = gdi32.CreateSolidBrush(RGB(255, 0, 0))

RED =    0x1000
YELLOW = 0x2000
GREEN =  0x4000

# State table for a simple stoplite

STATES = {RED: RED + 1,
          RED+1: RED + 2,
          RED+2: RED | YELLOW,
          RED | YELLOW: GREEN,
          GREEN: GREEN+1,
          GREEN+1: GREEN+2,
          GREEN+2: YELLOW,
          YELLOW: RED}

################################################################

class Stoplite(object):
    _state = random.choice(STATES.keys())

    def __init__(self):
        self._timerproc = TIMERPROC(self.timerproc)
        self._interval = random.choice(range(200, 1600))
        self._timerid = user32.SetTimer(0, 0, self._interval, self._timerproc)

    def timerproc(self, hwnd, uMsg, idEvent, dwTime):
        self._state = STATES[self._state]
        if hasattr(self, "redraw"):
            self.redraw()

    def Draw(self, hdc, rc):
        COLOR_BTNFACE = 15
        user32.FillRect(hdc, byref(rc), COLOR_BTNFACE + 1)
        BLACK_BRUSH = 4
        user32.FrameRect(hdc, byref(rc), gdi32.GetStockObject(BLACK_BRUSH))

        rc.left += 2
        rc.top += 2
        rc.right -= 2
        rc.bottom -= 2

        rc.bottom -= 12

        LTGRAY_BRUSH = 1
        GRAY_BRUSH = 2
        DKGRAY_BRUSH = 3

        if self._state & RED:
            gdi32.SelectObject(hdc, red_brush)
        else:
            gdi32.SelectObject(hdc, gdi32.GetStockObject(GRAY_BRUSH))
        gdi32.Ellipse(hdc, rc.left, rc.top, rc.right, rc.top + rc.height/3)

        if self._state & YELLOW:
            gdi32.SelectObject(hdc, yellow_brush)
        else:
            gdi32.SelectObject(hdc, gdi32.GetStockObject(GRAY_BRUSH))
        gdi32.Ellipse(hdc, rc.left, rc.top + rc.height/3,
                      rc.right, rc.bottom - rc.height/3)

        if self._state & GREEN:
            gdi32.SelectObject(hdc, green_brush)
        else:
            gdi32.SelectObject(hdc, gdi32.GetStockObject(GRAY_BRUSH))
        gdi32.Ellipse(hdc, rc.left, rc.bottom - rc.height/3, rc.right, rc.bottom)

        text = str(self._interval)
        gdi32.TextOutA(hdc, rc.left, rc.bottom, text, len(text))
