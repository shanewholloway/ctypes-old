## 	   Copyright (c) 2003 Henk Punt

## Permission is hereby granted, free of charge, to any person obtaining
## a copy of this software and associated documentation files (the
## "Software"), to deal in the Software without restriction, including
## without limitation the rights to use, copy, modify, merge, publish,
## distribute, sublicense, and/or sell copies of the Software, and to
## permit persons to whom the Software is furnished to do so, subject to
## the following conditions:

## The above copyright notice and this permission notice shall be
## included in all copies or substantial portions of the Software.

## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
## EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
## MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
## NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
## LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
## OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
## WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE

from ctypes import *
from windows import *

class BITMAP(Structure):
    _fields_ = [("bmType", LONG),
    		("bmWidth", LONG),
    		("bmHeight", LONG),
    		("bmWidthBytes", LONG),
    		("bmPlanes", WORD),
    		("bmBitsPixel", WORD),
    		("bmBits", LPVOID)]

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
CLR_NONE = 0xffffffff

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
