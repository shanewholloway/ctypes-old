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

