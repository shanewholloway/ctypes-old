from ctypes import windll, cdll, Structure, pointer, WinError, CFunction, sizeof
from windows import ValidHandle

class BITMAP(Structure):
    _fields_ = [("bmType", "l"),
    		("bmWidth", "l"),
    		("bmHeight", "l"),
    		("bmWidthBytes", "l"),
    		("bmPlanes", "h"),
    		("bmBitsPixel", "h"),
    		("bmBits", "z")]

MONO_FONT = 8
OBJ_FONT = 6
ANSI_FIXED_FONT  = 11
ANSI_VAR_FONT = 12
DEVICE_DEFAULT_FONT= 14
DEFAULT_GUI_FONT= 17
OEM_FIXED_FONT= 10
SYSTEM_FONT= 13
SYSTEM_FIXED_FONT= 16

COLOR_ACTIVEBORDER = 10

HS_BDIAGONAL   =3
HS_CROSS       =4
HS_DIAGCROSS   =5
HS_FDIAGONAL   =2
HS_HORIZONTAL  =0
HS_VERTICAL    =1

PATINVERT     =  0x5A0049
 
GetStockObject = windll.gdi32.GetStockObject
LineTo = windll.gdi32.LineTo
FillRect = windll.user32.FillRect
DrawEdge = windll.user32.DrawEdge
CreateCompatibleDC = windll.gdi32.CreateCompatibleDC
CreateCompatibleDC.restype = ValidHandle
SelectObject = windll.gdi32.SelectObject
GetObject = windll.gdi32.GetObjectA
DeleteObject = windll.gdi32.DeleteObject
BitBlt = windll.gdi32.BitBlt
StretchBlt = windll.gdi32.StretchBlt
GetSysColorBrush = windll.user32.GetSysColorBrush
CreateHatchBrush = windll.gdi32.CreateHatchBrush
CreatePatternBrush = windll.gdi32.CreatePatternBrush
CreateBitmap = windll.gdi32.CreateBitmap
PatBlt = windll.gdi32.PatBlt
