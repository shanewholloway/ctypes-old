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

from windows import *
from wtl import *
from ctypes import *

LPOFNHOOKPROC = c_voidp #TODO

class OPENFILENAME(Structure):
    _fields_ = [("lStructSize", DWORD),
                ("hwndOwner", HWND),
                ("hInstance", HINSTANCE),
                ("lpstrFilter", LPCTSTR),
                ("lpstrCustomFilter", LPTSTR),
                ("nMaxCustFilter", DWORD),
                ("nFilterIndex", DWORD),
                ("lpstrFile", LPTSTR),
                ("nMaxFile", DWORD),
                ("lpstrFileTitle", LPTSTR),
                ("nMaxFileTitle", DWORD),
                ("lpstrInitialDir", LPCTSTR),
                ("lpstrTitle", LPCTSTR),
                ("flags", DWORD),
                ("nFileOffset", WORD),
                ("nFileExtension", WORD),
                ("lpstrDefExt", LPCTSTR),
                ("lCustData", LPARAM),
                ("lpfnHook", LPOFNHOOKPROC),
                ("lpTemplateName", LPCTSTR),
                ("pvReserved", LPVOID),
                ("dwReserved", DWORD),
                ("flagsEx", DWORD)]

GetOpenFileName = windll.comdlg32.GetOpenFileNameA

class OpenFileDialog(object):
    def __init__(self, parent = None):
        self.parent = parent
        self.szPath = '\0' * 1024
        
    def DoModal(self):
        ofn = OPENFILENAME()
        ofn.lStructSize = sizeof(OPENFILENAME)
        ofn.lpstrFile = self.szPath
        ofn.nMaxFile = 1024
        ofn.hwndOwner = handle(self.parent)
        GetOpenFileName(byref(ofn))
        
    def getPath(self):
        return self.szPath[:self.szPath.find('\0')].strip()

    path = property(getPath, None, None, None)
    
