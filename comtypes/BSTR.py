################################################################
# Memory mamagement of BSTR is broken.
#
# The way we do them here, it is not possible to transfer the
# ownership of a BSTR instance.  ctypes allocates the memory with
# SysAllocString if we call the constructor with a string, and the
# instance calls SysFreeString when it is destroyed.
# So BSTR's received from dll function calls will never be freed,
# and BSTR's we pass to functions are freed too often ;-(

from ctypes import sizeof, _SimpleCData

class BSTR(_SimpleCData):
    _type_ = "X"
    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.value)

assert(sizeof(BSTR) == 4)
