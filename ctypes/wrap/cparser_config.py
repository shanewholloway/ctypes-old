# cparser_config.py - configuration items for cparser.py
#
# XXX should be made platform specific!
import re, sys, os

# C keywords, according to MSDN, plus some additional
# names like __forceinline, near, far.

# Skip all definitions where the rhs is a keyword
# Example: #define CALLBACK __stdcall
#
# Hm, should types be handled differently?
# Example: #define VOID void
C_KEYWORDS = """__asm else main struct __assume enum
__multiple_inheritance switch auto __except __single_inheritance
template __based explicit __virtual_inheritance this bool extern
mutable thread break false naked throw case __fastcall namespace true
catch __finally new try __cdecl float noreturn __try char for operator
typedef class friend private typeid const goto protected typename
const_cast if public union continue inline register unsigned
__declspec __inline default int return uuid delete __int8 short
__uuidof dllexport __int16 signed virtual dllimport __int32 sizeof
void do __int64 static volatile double __leave static_cast wmain
dynamic_cast long __stdcall while far near __forceinline __w64
__noop""".split()
C_KEYWORDS.append("long long")

# defines we know that won't work
# for windows.h
EXCLUDED_win32 = """
TTTOOLINFOA_V3_SIZE
TTTOOLINFOW_V3_SIZE
NMLVCUSTOMDRAW_V3_SIZE
NOTIFYICONDATAA_V1_SIZE
NOTIFYICONDATAA_V2_SIZE
PROPSHEETHEADERA_V1_SIZE
PROPSHEETHEADERA_V2_SIZE
PROPSHEETHEADERW_V2_SIZE
NOTIFYICONDATAW_V2_SIZE
s_imp
s_host
s_lh
s_net
s_addr
h_addr
s_impno
_VARIANT_BOOL
MIDL_uhyper
WINSCARDDATA
__MIDL_DECLSPEC_DLLIMPORT
__MIDL_DECLSPEC_DLLEXPORT
NCB_POST
STDAPI
STDAPIV
WINAPI
SHDOCAPI
WINOLEAUTAPI
WINOLEAPI
APIENTRY
EXTERN_C
FIRMWARE_PTR
STDMETHODIMPV
STDMETHODIMP
DEFAULT_UNREACHABLE
MAXLONGLONG
IMAGE_ORDINAL_FLAG64
SECURITY_NT_AUTHORITY
_I8_MIN
_I8_MAX
_UI8_MAX
_I16_MIN
_I16_MAX
_UI16_MAX
_I32_MIN
_I32_MAX
_UI32_MAX
_I64_MIN
_I64_MAX
_UI64_MAX
""".strip().split()

# The _I8_MIN symbols and friends are in limits.h, they have constanrs
# with i8 i16 i32 i64 suffixes which gccxml refuses to compile.

EXCLUDED_linux = """
_IOT_termios
""".strip().split()

if sys.platform == "win32":
    EXCLUDED = EXCLUDED_win32
elif sys.platform.startswith("linux"):
    EXCLUDED = EXCLUDED_linux
else:
    EXCLUDED = []

EXCLUDED = [text for text in EXCLUDED
            if not text.startswith("#")]

EXCLUDED_RE_win32 = r"""
^DECLSPEC\w*$
""".strip().split()

EXCLUDED_RE_linux = r"""
^__\w*$
^__attribute_\w*_$
^_G_HAVE_ST_BLKSIZE$
""".strip().split()

if sys.platform == "win32":
    EXCLUDED_RE = EXCLUDED_RE_win32
elif sys.platform.startswith("linux"):
    EXCLUDED_RE = EXCLUDED_RE_linux
else:
    EXCLUDED_RE = []

EXCLUDED_RE = [re.compile(pat) for pat in EXCLUDED_RE
               if not pat.startswith("#")]
