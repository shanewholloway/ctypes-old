/*
 * Copyright 1997-2001, Thomas Heller
 *
 * $Id$
 *
 */
/*
 * History: First version dated from 3/97, derived from my SCMLIB version
 * for win16.
 */
/*
 * Related Work:
 *	- calldll	http://www.nightmare.com/software.html
 *	- libffi	http://sourceware.cygnus.com/libffi/
 *	- ffcall 	http://clisp.cons.org/~haible/packages-ffcall.html
 *   and, of course, Don Beaudry's MESS package, but this is more ctypes
 *   related.
 */

#include "Python.h"

#ifdef MS_WIN32
#include <windows.h>
#else
#include <dlfcn.h>
#include <ffi.h>
#endif

#include "ctypes.h"

#ifdef _DEBUG
#define DEBUG_EXCEPTIONS /* */
#endif

#ifdef MS_WIN32
static char *FormatError(DWORD code)
{
	LPVOID lpMsgBuf;
	FormatMessage(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM,
		      NULL,
		      code,
		      MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), // Default language
		      (LPSTR) &lpMsgBuf,
		      0,
		      NULL);
	return (char *)lpMsgBuf;
}

static void SetException(DWORD code)
{
	char *lpMsgBuf;
	lpMsgBuf = FormatError(code);
	if(lpMsgBuf) {
		PyErr_SetString(PyExc_WindowsError, lpMsgBuf);
		LocalFree(lpMsgBuf);
	} else {
		switch (code) {
		case EXCEPTION_ACCESS_VIOLATION:
			/* The thread attempted to read from or write
			   to a virtual address for which it does not
			   have the appropriate access. */
			PyErr_SetString(PyExc_WindowsError,
					"exception: access violation");
			break;
		case EXCEPTION_BREAKPOINT:
			/* A breakpoint was encountered. */
			PyErr_SetString(PyExc_WindowsError,
					"exception: breakpoint encountered");
			break;
			
		case EXCEPTION_DATATYPE_MISALIGNMENT:
			/* The thread attempted to read or write data that is
			   misaligned on hardware that does not provide
			   alignment. For example, 16-bit values must be
			   aligned on 2-byte boundaries, 32-bit values on
			   4-byte boundaries, and so on. */
			PyErr_SetString(PyExc_WindowsError,
					"exception: datatype misalignment");
			break;

		case EXCEPTION_SINGLE_STEP:
			/* A trace trap or other single-instruction mechanism
			   signaled that one instruction has been executed. */
			PyErr_SetString(PyExc_WindowsError,
					"exception: single step");
			break;

		case EXCEPTION_ARRAY_BOUNDS_EXCEEDED: 
			/* The thread attempted to access an array element
			   that is out of bounds, and the underlying hardware
			   supports bounds checking. */
			PyErr_SetString(PyExc_WindowsError,
					"exception: array bounds exceeded");
			break;

		case EXCEPTION_FLT_DENORMAL_OPERAND:
			/* One of the operands in a floating-point operation
			   is denormal. A denormal value is one that is too
			   small to represent as a standard floating-point
			   value. */
			PyErr_SetString(PyExc_WindowsError,
					"exception: floating-point operand denormal");
			break;

		case EXCEPTION_FLT_DIVIDE_BY_ZERO:
			/* The thread attempted to divide a floating-point
			   value by a floating-point divisor of zero. */
			PyErr_SetString(PyExc_WindowsError,
					"exception: float divide by zero");
			break;

		case EXCEPTION_FLT_INEXACT_RESULT:
			/* The result of a floating-point operation cannot be
			   represented exactly as a decimal fraction. */
			PyErr_SetString(PyExc_WindowsError,
					"exception: float inexact");
			break;

		case EXCEPTION_FLT_INVALID_OPERATION:
			/* This exception represents any floating-point
			   exception not included in this list. */
			PyErr_SetString(PyExc_WindowsError,
					"exception: float invalid operation");
			break;

		case EXCEPTION_FLT_OVERFLOW:
			/* The exponent of a floating-point operation is
			   greater than the magnitude allowed by the
			   corresponding type. */
			PyErr_SetString(PyExc_WindowsError,
					"exception: float overflow");
			break;

		case EXCEPTION_FLT_STACK_CHECK:
			/* The stack overflowed or underflowed as the result
			   of a floating-point operation. */
			PyErr_SetString(PyExc_WindowsError,
					"exception: stack over/underflow");
			break;

		case EXCEPTION_STACK_OVERFLOW:
			/* The stack overflowed or underflowed as the result
			   of a floating-point operation. */
			PyErr_SetString(PyExc_WindowsError,
					"exception: stack overflow");
			break;

		case EXCEPTION_FLT_UNDERFLOW:
			/* The exponent of a floating-point operation is less
			   than the magnitude allowed by the corresponding
			   type. */
			PyErr_SetString(PyExc_WindowsError,
					"exception: float underflow");
			break;

		case EXCEPTION_INT_DIVIDE_BY_ZERO:
			/* The thread attempted to divide an integer value by
			   an integer divisor of zero. */
			PyErr_SetString(PyExc_WindowsError,
					"exception: integer divide by zero");
			break;

		case EXCEPTION_INT_OVERFLOW:
			/* The result of an integer operation caused a carry
			   out of the most significant bit of the result. */
			PyErr_SetString(PyExc_WindowsError,
					"exception: integer overflow");
			break;

		case EXCEPTION_PRIV_INSTRUCTION:
			/* The thread attempted to execute an instruction
			   whose operation is not allowed in the current
			   machine mode. */
			PyErr_SetString(PyExc_WindowsError,
					"exception: priviledged instruction");
			break;

		case EXCEPTION_NONCONTINUABLE_EXCEPTION:
			/* The thread attempted to continue execution after a
			   noncontinuable exception occurred. */
			PyErr_SetString(PyExc_WindowsError,
					"exception: nocontinuable");
			break;
		default:
			printf("error %d\n", code);
			PyErr_Format(PyExc_WindowsError,
				     "exception code 0x%08X",
				     code);
			break;
		}
	}
}
#endif

/**************************************************************/

PyCArgObject *
new_CArgObject(void)
{
	PyCArgObject *p;
	p = PyObject_New(PyCArgObject, &PyCArg_Type);
	if (p == NULL)
		return NULL;
	p->tag = '\0';
	p->obj = NULL;
	return p;
}

static void
PyCArg_dealloc(PyCArgObject *self)
{
	Py_XDECREF(self->obj);
	PyObject_Del(self);
}

static PyObject *
PyCArg_repr(PyCArgObject *self)
{
	char buffer[256];
	switch(self->tag) {
	case 'b':
	case 'B':
		sprintf(buffer, "<cparam '%c' (%d)>",
			self->tag, self->value.b);
		break;
	case 'h':
	case 'H':
		sprintf(buffer, "<cparam '%c' (%d)>",
			self->tag, self->value.h);
		break;
	case 'i':
	case 'I':
		sprintf(buffer, "<cparam '%c' (%d)>",
			self->tag, self->value.i);
		break;
	case 'l':
	case 'L':
		sprintf(buffer, "<cparam '%c' (%ld)>",
			self->tag, self->value.l);
		break;
		
#ifdef HAVE_LONG_LONG
	case 'q':
	case 'Q':
		sprintf(buffer,
#ifdef MS_WIN32
			"<cparam '%c' (%I64d)>",
#else
			"<cparam '%c' (%qd)>",
#endif
			self->tag, self->value.q);
		break;
#endif
	case 'd':
		sprintf(buffer, "<cparam '%c' (%f)>",
			self->tag, self->value.d);
		break;
	case 'f':
		sprintf(buffer, "<cparam '%c' (%f)>",
			self->tag, self->value.f);
		break;

	case 'c':
		sprintf(buffer, "<cparam '%c' (%c)>",
			self->tag, self->value.c);
		break;

/* Hm, are these 'z' and 'Z' codes useful at all?
   Shouldn't they be replaced by the functionality of c_string
   and c_wstring ?
*/
	case 'z':
	case 'Z':
	case 'P':
		sprintf(buffer, "<cparam '%c' (%08lx)>",
			self->tag, (long)self->value.p);
		break;

	default:
		sprintf(buffer, "<cparam '%c' at %08lx>",
			self->tag, (long)self);
		break;
	}
	return PyString_FromString(buffer);
}

PyTypeObject PyCArg_Type = {
	PyObject_HEAD_INIT(NULL)
	0,
	"CArgObject",
	sizeof(PyCArgObject),
	0,
	(destructor)PyCArg_dealloc,		/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	0,					/* tp_compare */
	(reprfunc)PyCArg_repr,			/* tp_repr */
	0,					/* tp_as_number */
	0,					/* tp_as_sequence */
	0,					/* tp_as_mapping */
	0,					/* tp_hash */
	0,					/* tp_call */
	0,					/* tp_str */
	0,					/* tp_getattro */
	0,					/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT,			/* tp_flags */
};

/****************************************************************/
/*
 * Convert a PyObject * into a parameter suitable to pass to an
 * C function call.
 *
 * 1. Python integers are converted to C int and passed by value.
 *
 * 2. 3-tuples are expected to have a format character in the first
 *    item, which must be 'i', 'f', 'd', 'q', or 'P'.
 *    The second item will have to be an integer, float, double, long long
 *    or integer (denoting an address void *), will be converted to the
 *    corresponding C data type and passed by value.
 *
 * 3. Other Python objects are tested for an '_as_parameter_' attribute.
 *    The value of this attribute must be an integer which will be passed
 *    by value, or a 2-tuple or 3-tuple which will be used according
 *    to point 2 above. The third item (if any), is ignored. It is normally
 *    used to keep the object alive where this parameter refers to.
 *    XXX This convention is dangerous - you can construct arbitrary tuples
 *    in Python and pass them. Would it be safer to use a custom container
 *    datatype instead of a tuple?
 *
 * 4. Other Python objects cannot be passed as parameters - an exception is raised.
 *
 * 5. ConvParam will store the converted result in a struct containing format
 *    and value.
 */

#define ASSERT_FORMAT(fmt) assert(strchr("ciqfdpsz", fmt))

/*
 * Convert a single Python object into a 'C object' and store it in a
 * 'struct param'.  Return -1 on error (with exception set), 0 otherwise.
 */
static PyCArgObject *ConvParam(PyObject *obj, int index)
{
	PyCArgObject *parm;

	if (PyCArg_CheckExact(obj)) {
		Py_INCREF(obj);
		return (PyCArgObject *)obj;
	}

	parm = new_CArgObject();
	if (!parm)
		return NULL;

	/* check for None, integer, string or unicode and use directly if successful */
	if (obj == Py_None) {
		parm->tag = 'P';
		parm->value.p = NULL;
		Py_INCREF(Py_None);
		parm->obj = Py_None;
		return parm;
	}

	if (PyInt_Check(obj)) {
		parm->tag = 'i';
		parm->value.i = PyInt_AS_LONG(obj);
		Py_INCREF(obj);
		parm->obj = obj;
		return parm;
	}

	if (PyString_Check(obj)) {
		parm->tag = 'P';
		parm->value.p = PyString_AS_STRING(obj);
		Py_INCREF(obj);
		parm->obj = obj;
		return parm;
	}

#ifdef HAVE_USABLE_WCHAR_T
	if (PyUnicode_Check(obj)) {
		parm->tag = 'P';
		parm->value.p = PyUnicode_AS_UNICODE(obj);
		Py_INCREF(obj);
		parm->obj = obj;
		return parm;
	}
#endif
	{
		PyObject *arg;
		arg = PyObject_GetAttrString(obj, "_as_parameter_");
		/* Which types should we exactly allow here?
		   integers are required for using Python classes
		   as parameters (they have to expose the '_as_parameter_'
		   attribute)
		*/
		if (arg == 0)
			goto error;
		if (PyCArg_CheckExact(arg)) {
			Py_DECREF(parm);
			return (PyCArgObject *)arg;
		}
		if (PyInt_Check(arg)) {
			parm->tag = 'i';
			parm->value.i = PyInt_AS_LONG(arg);
			Py_INCREF(obj);
			parm->obj = obj;
			return parm;
		}
	  error:
		Py_XDECREF(arg);
		Py_DECREF(parm);
		PyErr_Format(PyExc_TypeError,
			     "Don't know how to convert parameter %d", index);
		return NULL;
	}
}


#ifndef MS_WIN32
/*
 * libffi uses:
 *
 * ffi_status ffi_prep_cif(ffi_cif *cif, ffi_abi abi,
 *	                   unsigned int nargs,
 *                         ffi_type *rtype,
 *                         ffi_type **atypes);
 *
 * and then
 *
 * void ffi_call(ffi_cif *cif, void *fn, void *rvalue, void **avalues);
 */
static int _call_function_pointer(int flags,
				  PPROC pProc,
				  PyCArgObject **parms,
				  PyCArgObject *res,
				  int argcount)
{
	ffi_cif cif;
	ffi_type *rtype;
	ffi_type **atypes;
	void **values;
	int i;

/*
  There's a problem with current CVS versions of libffi (2003-01-21).
  It redefines ffi_type_slong and ffi_type_ulong to
  ffi_type_sint64 and ffi_type_uint64.

  Fortunately, ctypes' unittests catch this.

	printf("SIZEOF_LONG %d\n", SIZEOF_LONG);

	printf("ffi_type_slong %p\n", &ffi_type_slong);
	printf("ffi_type_sint64 %p\n", &ffi_type_sint64);
	printf("ffi_type_sint %p\n", &ffi_type_sint);
	printf("ffi_type_sint32 %p\n", &ffi_type_sint32);
*/
#if (SIZEOF_LONG_LONG == 8 && SIZEOF_LONG == 4)
#undef ffi_type_ulong
#define ffi_type_ulong ffi_type_uint32
#define ffi_type_ulonglong ffi_type_uint64
#undef ffi_type_slong
#define ffi_type_slong ffi_type_sint32
#define ffi_type_slonglong ffi_type_sint64
#endif

	atypes = (ffi_type **)alloca(argcount * sizeof(ffi_type *));
	values = (void **)alloca(argcount * sizeof(void *));

	for (i = 0; i < argcount; ++i) {
		switch(parms[i]->tag) {
		case 'c':
			atypes[i] = &ffi_type_schar;
			break;
		case 'b':
			atypes[i] = &ffi_type_sint8;
			break;
		case 'B':
			atypes[i] = &ffi_type_uint8;
			break;
		case 'h':
			atypes[i] = &ffi_type_sshort;
			break;
		case 'H':
			atypes[i] = &ffi_type_ushort;
			break;
		case 'i':
			atypes[i] = &ffi_type_sint;
			break;
		case 'I':
			atypes[i] = &ffi_type_uint;
			break;
		case 'l':
			atypes[i] = &ffi_type_slong;
			break;
		case 'L':
			atypes[i] = &ffi_type_ulong;
			break;
		case 'q':
			atypes[i] = &ffi_type_slonglong;
			break;
		case 'Q':
			atypes[i] = &ffi_type_ulonglong;
			break;
		case 'z':
		case 'Z':
		case 'P':
			atypes[i] = &ffi_type_pointer;
			break;
		case 'd':
			atypes[i] = &ffi_type_double;
			break;
		case 'f':
			atypes[i] = &ffi_type_float;
			break;
		default:
			printf("PARM ????? %c\n", parms[i]->tag);
			atypes[i] = NULL;
			break;
		}
		values[i] = &parms[i]->value;
	}
	switch(res->tag) {
	case 'c':
		rtype = &ffi_type_schar;
		break;
	case 'b':
		rtype = &ffi_type_sint8;
		break;
	case 'B':
		rtype = &ffi_type_uint8;
		break;
	case 'h':
		rtype = &ffi_type_sshort;
		break;
	case 'H':
		rtype = &ffi_type_ushort;
		break;
	case 'i':
		rtype = &ffi_type_sint;
		break;
	case 'I':
		rtype = &ffi_type_uint;
		break;
	case 'l':
		rtype = &ffi_type_slong;
		break;
	case 'L':
		rtype = &ffi_type_ulong;
		break;
	case 'q':
		rtype = &ffi_type_slonglong;
		break;
	case 'Q':
		rtype = &ffi_type_ulonglong;
		break;
	case 'z':
	case 'Z':
	case 'P':
		rtype = &ffi_type_pointer;
		break;
	case 'd':
		rtype = &ffi_type_double;
		break;
	case 'f':
		rtype = &ffi_type_float;
		break;
	default:
		printf("RES ????? %c\n", res->tag);
		rtype = NULL;
		break;
	}
    
	if (FFI_OK != ffi_prep_cif(&cif, FFI_DEFAULT_ABI,
				   argcount,
				   rtype,
				   atypes)) {
		PyErr_SetString(PyExc_RuntimeError,
				"ffi_prep_cif failed");
		return -1;
	}

	Py_BEGIN_ALLOW_THREADS
	ffi_call(&cif, (void *)pProc, &res->value, values);
	Py_END_ALLOW_THREADS

	return 0;
}
#else
#pragma optimize ("", off)
/*
 * Can you figure out what this does? ;-)
 */
static void __stdcall push(void)
{
}

typedef struct {
	int format;	// 'i', 'q', 'f', 'd', 'p'
	union {
		char c;
		int i;
		LONG_LONG l;
		float f;
		double d;
		void *p;
	} val;
	PyObject *keepref;
	int flags;	/* only used for results, not for parameters */
} param;

static int _call_function_pointer(int flags,
				  PPROC pProc,
				  PyCArgObject **parms,
				  PyCArgObject *res,
				  int argcount)
{
	int i;
	DWORD dwExceptionCode;
	int new_esp, save_esp;
	int argbytes = 0;
	
	/*
	  The idea was to do this in C, without assembler. But how can we
	  guard against passing the wrong number of arguments? How do we
	  save and restore the stack pointer?

	  Apparently MSVC does not use ESP addressing but EBP addressing,
	  so we can use local variables (on the stack) for saving and
	  restoring the value of ESP!
	*/

	_asm mov save_esp, esp;
	new_esp = save_esp;

#pragma warning (disable: 4087)
	/* Both __stdcall and __cdecl calling conventions pass the arguments
	   'right to left'. The difference is in the stack cleaning: __stdcall
	   __stdcall functions pop their arguments off the stack themselves,
	   __cdecl functions leave this to the caller.
	*/
	for (i = argcount-1; i >= 0; --i) {
		float f;

		switch(parms[i]->tag) {
		case 'c':
			push(parms[i]->value.c);
			argbytes += sizeof(int);
			break;
		
			/* This works, although it doesn't look correct! */
		case 'b':
		case 'h':
		case 'i':
		case 'B':
		case 'H':
		case 'I':
			push(parms[i]->value.i);
			argbytes += sizeof(int);
			break;
		case 'l':
		case 'L':
			push(parms[i]->value.l);
			argbytes += sizeof(long);
			break;
#ifdef HAVE_LONG_LONG
		case 'q':
		case 'Q':
			push(parms[i]->value.q);
			argbytes += sizeof(LONG_LONG);
			break;
#endif
		case 'f':
			/* Cannot use push(parms[i]->value.f) here, because
			   the C compiler would promote it to a double
			*/
			f = parms[i]->value.f;
			_asm push f;
			argbytes += sizeof(float);
			break;
		case 'd':
			push(parms[i]->value.d);
			argbytes += sizeof(double);
			break;
		case 'z':
		case 'Z':
		case 'P':
			push(parms[i]->value.p);
			argbytes += sizeof(void *);
			break;
		default:
			PyErr_Format(PyExc_ValueError,
				     "BUG: Invalid format tag '%c' for argument",
				     parms[i]->tag);
			/* try to clean the stack */
			_asm mov esp, save_esp;
			return -1;
		}
	}

#pragma warning (default: 4087)
	Py_BEGIN_ALLOW_THREADS
	dwExceptionCode = 0;
#ifndef DEBUG_EXCEPTIONS
	__try {
#endif
		switch(res->tag) {
		case 'c':
			res->value.c = ((char(*)())pProc)();
			break;
		case 'B':
		case 'b':
			res->value.b = ((char(*)())pProc)();
			break;
		case 'H':
		case 'h':
			res->value.h = ((short(*)())pProc)();
			break;
		case 'I':
		case 'i':
			res->value.i = ((int(*)())pProc)();
			break;
		case 'l':
		case 'L':
			res->value.l = ((long(*)())pProc)();
			break;
		case 'd':
			res->value.d = ((double(*)())pProc)();
			break;
		case 'f':
			res->value.f = ((float(*)())pProc)();
			break;
#ifdef HAVE_LONG_LONG
		case 'q':
		case 'Q':
			res->value.q = ((LONG_LONG(*)())pProc)();
			break;
#endif
		case 'z':
		case 'Z':
		case 'P':
			res->value.p = ((void *(*)())pProc)();
			break;
		default:
			/* XXX Signal bug */
			res->tag |= 0x80;
			break;
		}
#ifndef DEBUG_EXCEPTIONS
	}
	__except (dwExceptionCode = GetExceptionCode(), EXCEPTION_EXECUTE_HANDLER) {
		;
	}
#endif
	_asm sub new_esp, esp;
	_asm mov esp, save_esp;

	Py_END_ALLOW_THREADS

	if (dwExceptionCode) {
		SetException(dwExceptionCode);
		return -1;
	}
	if (res->tag & 0x80) {
		PyErr_Format(PyExc_ValueError,
			     "BUG: Invalid format tag for restype '%c'",
			     res->tag & ~0x80);
		return -1;
	}

	if (flags & FUNCFLAG_CDECL) /* Clean up stack if needed */
		new_esp -= argbytes;
	if (new_esp < 0) {
		PyErr_Format(PyExc_ValueError,
			     "Procedure probably called with not enough "
			     "arguments (%d bytes missing)",
			     -new_esp);
		return -1;
	}
	if (new_esp > 0) {
		PyErr_Format(PyExc_ValueError,
			     "Procedure probably called with too many "
			     "arguments (%d bytes in excess)",
			     new_esp);
		return -1;
	}
	return 0;
}
#pragma optimize ("", on)

#endif

#define RESULT_PASTE_INTO 1
#define RESULT_CALL_RESTYPE 2

/*
 * Fill out the format field of 'result', depending on 'restype'.
 */
static void PrepareResult(PyObject *restype, PyCArgObject *result)
{
	if (restype == NULL) {
		result->tag = 'i';
		return;
	}

	if (PyString_Check(restype)) {
		/* XXX Is it single letter? */
		result->tag = PyString_AS_STRING(restype)[0];
		return;
	}

	if (PointerTypeObject_Check(restype)) {
		result->tag = 'P';
		return;
	}

#if 0
	if (SimpleTypeObject_Check(restype)) {
		/* Simple data types as return value don't make too much sense
		 * (why would you prefer a c_int instance over a plain Python integer?)
		 * but subclasses DO make sense. Think 'class HRESULT(c_int): pass'.
		 */
		/*
		 * If this would be enabled, it would start with this code:
		 */
		StgDictObject *dict;

		dict = PyType_stgdict(restype);
		if (!dict || !PyString_Check(dict->proto)) {
			PyErr_SetString(PyExc_TypeError,
					"invalid restype: has no stgdict or proto invalid");
			goto error;
		}
		format = PyString_AS_STRING(dict->proto)[0];
	}
#endif
	if (PyCallable_Check(restype)) {
		result->tag = 'i'; /* call with integer result */
		return;
	}

	/* XXX This should not occur... */
	result->tag = 'i';
}

/*
 * Convert the C value in result into an instance described by restype
 */
static PyObject *GetResult(PyObject *restype, PyCArgObject *result)
{
	PyObject *retval = ToPython(&result->value, result->tag);

	if (restype == NULL || PyString_Check(restype)) {
		Py_INCREF(retval);
		return retval;
	}

	if (PointerTypeObject_Check(restype)) {
		CDataObject *pd;
		/* There is no Python api to set the pointer value, so we
		   create an empty (NULL) pointer, and modify it afterwards.
		*/
		pd = (CDataObject *)PyObject_CallFunctionObjArgs(restype, NULL);
		if (!pd)
			return NULL;
		if (!CDataObject_Check(pd)) {
			Py_DECREF(pd);
			PyErr_SetString(PyExc_TypeError,
					"BUG: restype call did not return a CDataObject");
			return NULL;
		}
		/* Even better would be to use the buffer interface */
		memcpy(pd->b_ptr, &result->value, pd->b_size);
		return (PyObject *)pd;
	}
	if (PyCallable_Check(restype))
		return PyObject_CallFunction(restype, "i",
					     result->value.i);
	/* Should be unreached */
	assert(FALSE);
	return NULL; /* to silence the compiler */
}

/*
 * Requirements, must be ensured by the caller:
 * - argtuple is tuple of arguments
 * - argtypes is either NULL, or a tuple of the same size as argtuple
 *
 * - XXX various requirements for restype, not yet collected
 */
PyObject *_CallProc(PPROC pProc,
		    PyObject *argtuple,
		    void *pIunk,
		    int flags,
		    PyObject *argtypes,
		    PyObject *restype)
{
	int i, n, argcount;
	PyCArgObject *result = NULL;
	PyCArgObject **pargs, **pp;
	PyObject *retval = NULL;

	n = argcount = PyTuple_GET_SIZE(argtuple);

	/* a COM object this pointer */
	if (pIunk)
		++argcount;

#ifdef MS_WIN32
#define alloca _alloca
#endif
	pargs = (PyCArgObject **)alloca(sizeof(PyCArgObject *) * argcount);
	memset(pargs, 0, sizeof(pargs) * argcount);

	if (pIunk) {
		pargs[0] = new_CArgObject();
		if (pargs[0] == NULL)
			return NULL;
		pargs[0]->tag = 'P';
		pargs[0]->value.p = pIunk;
		pp = &pargs[1];
	} else {
		pp = &pargs[0];
	}

	/* Convert the arguments */
	for (i = 0; i < n; ++i, ++pp) {
		PyObject *converter;
		PyObject *arg;

		arg = PyTuple_GET_ITEM(argtuple, i);	/* borrowed ref */
		if (argtypes) {
			converter = PyTuple_GET_ITEM(argtypes, i);
			arg = PyObject_CallFunctionObjArgs(converter,
							   arg,
							   NULL);
			if (arg == NULL)
				goto error;

			*pp = ConvParam(arg, i+1);
			if (!*pp)
				goto error; /* leaking somewhat */
			Py_DECREF(arg);
		} else {
			*pp = ConvParam(arg, i+1);
			if (!*pp)
				goto error; /* leaking somewhat */
		}
	}

	/* This should better be static... */
	result = new_CArgObject();
	if (result == NULL)
		goto error;
	PrepareResult(restype, result);

	if (-1 == _call_function_pointer(flags, pProc, pargs, result, argcount))
		goto error;

#ifdef MS_WIN32
	if (flags & FUNCFLAG_HRESULT) {
		if (result->value.i & 0x80000000)
			retval = PyErr_SetFromWindowsErr(result->value.i);
		else
			retval = PyInt_FromLong(result->value.i);
	} else
#endif
		retval = GetResult(restype, result);
  error:
	for (i = 0; i < argcount; ++i) {
		Py_XDECREF(pargs[i]);
	}
	Py_XDECREF(result);
	return retval;
}

#ifdef MS_WIN32
static char format_error_doc[] =
"FormatError([integer]) -> string\n\
\n\
Convert a win32 error code into a string. If the error code is not\n\
given, the return value of a call to GetLastError() is used.\n";
static PyObject *format_error(PyObject *self, PyObject *args)
{
	PyObject *result;
	char *lpMsgBuf;
	DWORD code = 0;
	if (!PyArg_ParseTuple(args, "|i:FormatError", &code))
		return NULL;
	if (code == 0)
		code = GetLastError();
	lpMsgBuf = FormatError(code);
	if (lpMsgBuf) {
		result = Py_BuildValue("s", lpMsgBuf);
		LocalFree(lpMsgBuf);
	} else {
		result = Py_BuildValue("s", "<no description>");
	}
	return result;
}

static char load_library_doc[] =
"LoadLibrary(name) -> handle\n\
\n\
Load an executable (usually a DLL), and return a handle to it.\n\
The handle may be used to locate exported functions in this\n\
module.\n";
static PyObject *load_library(PyObject *self, PyObject *args)
{
	char *name;
	HMODULE hMod;
	if (!PyArg_ParseTuple(args, "s:LoadLibrary", &name))
		return NULL;
	hMod = LoadLibrary(name);
	if (!hMod)
		return PyErr_SetFromWindowsErr(GetLastError());
	return Py_BuildValue("i", hMod);
}

static char free_library_doc[] =
"FreeLibrary(handle) -> void\n\
\n\
Free the handle of an executable previously loaded by LoadLibrary.\n";
static PyObject *free_library(PyObject *self, PyObject *args)
{
	HMODULE hMod;
	if (!PyArg_ParseTuple(args, "i:FreeLibrary", &hMod))
		return NULL;
	if (!FreeLibrary(hMod))
		return PyErr_SetFromWindowsErr(GetLastError());
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *
call_commethod(PyObject *self, PyObject *args)
{
	IUnknown *pIunk;
	int index;
	PyObject *arguments;
	PPROC *lpVtbl;
	PyObject *result;
	CDataObject *pcom;
	PyObject *argtypes = NULL;

	if (!PyArg_ParseTuple(args,
			      "OiO!|O!",
			      &pcom, &index,
			      &PyTuple_Type, &arguments,
			      &PyTuple_Type, &argtypes))
		return NULL;

	if (argtypes && (PyTuple_GET_SIZE(arguments) != PyTuple_GET_SIZE(argtypes))) {
		PyErr_Format(PyExc_TypeError,
			     "Method takes %d arguments (%d given)",
			     PyTuple_GET_SIZE(argtypes), PyTuple_GET_SIZE(arguments));
		return NULL;
	}

	if (!CDataObject_Check(pcom) || (pcom->b_size != sizeof(void *))) {
		PyErr_Format(PyExc_TypeError,
			     "COM Pointer expected instead of %s instance",
			     pcom->ob_type->tp_name);
		return NULL;
	}

	if ((*(void **)(pcom->b_ptr)) == NULL) {
		PyErr_SetString(PyExc_ValueError,
				"The COM 'this' pointer is NULL");
		return NULL;
	}

	pIunk = (IUnknown *)(*(void **)(pcom->b_ptr));
	lpVtbl = (PPROC *)(pIunk->lpVtbl);

	result =  _CallProc(lpVtbl[index],
			    arguments,
			    pIunk,
			    FUNCFLAG_HRESULT, /* flags */
			    argtypes, /* self->argtypes */
			    NULL); /* self->restype */
	return result;
}

#else

static PyObject *py_dl_open(PyObject *self, PyObject *args)
{
	char *name;
	void * handle;
	int mode = RTLD_NOW | RTLD_LOCAL;
	if (!PyArg_ParseTuple(args, "s:dlopen", &name))
		return NULL;
	handle = dlopen(name, mode);
	if (!handle) {
		PyErr_SetString(PyExc_OSError,
				       dlerror());
		return NULL;
	}
	return Py_BuildValue("i", handle);
}

static PyObject *py_dl_close(PyObject *self, PyObject *args)
{
	void * handle;

	if (!PyArg_ParseTuple(args, "i:dlclose", &handle))
		return NULL;
	if (dlclose(handle)) {
		PyErr_SetString(PyExc_OSError,
				       dlerror());
		return NULL;
	}
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *py_dl_sym(PyObject *self, PyObject *args)
{
	char *name;
	void *handle;
	void *ptr;

	if (!PyArg_ParseTuple(args, "is:dlsym", &handle, &name))
		return NULL;
	ptr = dlsym(handle, name);
	if (!ptr) {
		PyErr_SetString(PyExc_OSError,
				       dlerror());
		return NULL;
	}
	return Py_BuildValue("i", ptr);
}
#endif

/*
 * Only for debugging so far: So that we cann call CFunction instances
 *
 * XXX Needs to accept more arguments: flags, argtypes, restype
 */
static PyObject *
call_function(PyObject *self, PyObject *args)
{
	PPROC func;
	PyObject *arguments;
	PyObject *result;

	if (!PyArg_ParseTuple(args,
			      "iO!",
			      &func,
			      &PyTuple_Type, &arguments))
		return NULL;

	result =  _CallProc(func,
			    arguments,
			    NULL,
			    0, /* flags */
			    NULL, /* self->argtypes */
			    NULL); /* self->restype */
	return result;
}

#ifdef _DEBUG
extern PyObject *
my_debug(PyObject *, PyObject *);
#endif

PyMethodDef module_methods[] = {
#ifdef MS_WIN32
	{"FormatError", format_error, METH_VARARGS, format_error_doc},
	{"LoadLibrary", load_library, METH_VARARGS, load_library_doc},
	{"FreeLibrary", free_library, METH_VARARGS, free_library_doc},
	{"call_commethod", call_commethod, METH_VARARGS },
#else
	{"dlopen", py_dl_open, METH_VARARGS, "dlopen a library"},
	{"dlclose", py_dl_close, METH_VARARGS, "dlclose a library"},
	{"dlsym", py_dl_sym, METH_VARARGS, "find symbol in shared library"},
#endif
	{"alignment", align_func, METH_O},
	{"sizeof", sizeof_func, METH_O},
	{"byref", byref, METH_O},
	{"addressof", addressof, METH_O},
	{"call_function", call_function, METH_VARARGS },
#ifdef _DEBUG
	{"my_debug", my_debug, METH_O},
#endif
	{NULL,      NULL}        /* Sentinel */
};

/*
 Local Variables:
 compile-command: "python setup.py install --home ~"
 End:
*/
