import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
# COM success and error codes

S_OK = 0
S_FALSE = 1

E_UNEXPECTED = 0x8000FFFF

E_NOTIMPL = 0x80004001
E_NOINTERFACE = 0x80004002
E_POINTER = 0x80004003
E_FAIL = 0x80004005
E_INVALIDARG = 0x80070057

CLASS_E_NOAGGREGATION = 0x80040110
CLASS_E_CLASSNOTAVAILABLE = 0x80040111

TYPE_E_ELEMENTNOTFOUND = 0x8002802B

CO_E_CLASSSTRING = 0x800401F3
