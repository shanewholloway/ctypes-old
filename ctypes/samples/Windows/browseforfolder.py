from ctypes import *
from ctypes.wintypes import HWND

BIF_RETURNONLYFSDIRS   = 0x0001  # For finding a folder to start document searching
BIF_DONTGOBELOWDOMAIN  = 0x0002  # For starting the Find Computer
BIF_STATUSTEXT         = 0x0004
BIF_RETURNFSANCESTORS  = 0x0008
BIF_EDITBOX            = 0x0010
BIF_VALIDATE           = 0x0020  # insist on valid result (or CANCEL)
BIF_BROWSEFORCOMPUTER  = 0x1000  # Browsing for Computers.
BIF_BROWSEFORPRINTER   = 0x2000  # Browsing for Printers
BIF_BROWSEINCLUDEFILES = 0x4000  # Browsing for Everything

class BROWSEINFO(Structure):
    _fields_ = [("hwndOwner", HWND),
                ("pidlRoot", c_int),
                ("pszDisplayName", POINTER(c_char)),
                ("lpszTitle", c_char_p),
                ("ulFlags", c_uint),
                ("lpfn", c_int), # POINTER(BFFCALLBACK)
                ("lParam", c_ulong),
                ("iImage", c_int)]

oledll.ole32.CoInitialize(None)

bi = BROWSEINFO()
buffer = c_buffer(260)
bi.hwndOwner = windll.user32.GetDesktopWindow()
bi.pszDisplayName = buffer
bi.lpszTitle = "Please select a folder:"
bi.ulFlags = BIF_RETURNONLYFSDIRS
##bi.ulFlags = BIF_BROWSEFORCOMPUTER | BIF_EDITBOX

print windll.shell32.SHBrowseForFolder(byref(bi))

print c_char_p.from_address(addressof(bi.pszDisplayName))

# XXX We must free the thing returned from SHBrowseForFolder
# XXX Should use the UNICODE version?
