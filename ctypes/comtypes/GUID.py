from ctypes import *
from ctypes.wintypes import DWORD, WORD, BYTE

_ole32 = oledll.ole32

class GUID(Structure):
    _fields_ = [("Data1", DWORD),
                ("Data2", WORD),
                ("Data3", WORD),
                ("Data4", BYTE * 8)]

    def __init__(self, name=None):
        if name is not None:
            _ole32.CLSIDFromString(unicode(name), byref(self))

    def __repr__(self):
        s = (c_wchar * 39)()
        _ole32.StringFromGUID2(byref(self), s, 39)
        return 'GUID("%s")' % s.value

    def __str__(self):
        s = (c_wchar * 39)()
        _ole32.StringFromGUID2(byref(self), s, 39)
        return s.value

    def __cmp__(self, other):
        if isinstance(other, GUID):
            return not _ole32.IsEqualGUID(byref(self), byref(other))
        return -1

    def __nonzero__(self):
        result = str(buffer(self)) != "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"
        return result

    def __eq__(self, other):
        return isinstance(other, GUID) and \
               _ole32.IsEqualGUID(byref(self), byref(other))

##    def __hash__(self):
##        return hash(repr(self))

    def copy(self):
        return GUID(str(self))

    def from_progid(cls, progid):
        inst = cls()
        _ole32.CLSIDFromProgID(unicode(progid), byref(inst))
        return inst
    from_progid = classmethod(from_progid)

    def progid(self):
        progid = c_wchar_p()
        _ole32.ProgIDFromCLSID(byref(self), byref(progid))
        return progid.value

assert(sizeof(GUID) == 16), sizeof(GUID)

__all__ = ["GUID"]
