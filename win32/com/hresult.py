import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
# COM success and error codes

S_OK = 0
S_FALSE = 1

E_UNEXPECTED = 0x8000FFFFL

E_NOTIMPL = 0x80004001L
E_NOINTERFACE = 0x80004002L
E_POINTER = 0x80004003L
E_FAIL = 0x80004005L
E_INVALIDARG = 0x80070057L

CLASS_E_NOAGGREGATION = 0x80040110L
CLASS_E_CLASSNOTAVAILABLE = 0x80040111L

TYPE_E_ELEMENTNOTFOUND = 0x8002802BL

CO_E_CLASSSTRING = 0x800401F3L