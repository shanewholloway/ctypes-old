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
import comctl

class List(comctl.ListView):
    def __init__(self, *args, **kwargs):
        apply(comctl.ListView.__init__, (self,) + args, kwargs)

        
    def InsertColumns(self, colDef):
        """inserts columns into list view, based on colDef
        colDef is a list of tuples (title, width)"""
        col = comctl.LVCOLUMN()
        i = 0
        for title, width in colDef:
            col.mask = comctl.LVCF_TEXT | comctl.LVCF_WIDTH
            col.pszText = title
            col.cx = width
            self.InsertColumn(i, col)
            i += 1

    def InsertRow(self, i, row):
        """inserts a row at index i, row is a list of strings"""
        item = comctl.LVITEM()
        item.iItem = i
        item.iSubItem = 0
        item.mask = comctl.LVIF_TEXT
        item.pszText = row[0]
        self.InsertItem(item)
        
        for iSubItem in range(len(row) - 1):
            item.iSubItem = iSubItem + 1
            item.mask = comctl.LVIF_TEXT
            item.pszText = row[iSubItem + 1]
            self.SetItem(item)

