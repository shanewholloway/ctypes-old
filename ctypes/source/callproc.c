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


/*
  How are functions called, and how are parameters converted to C ?

  1. _ctypes.c::CFuncPtr_call receives an argument tuple 'inargs' and a
  keyword dictionary 'kwds'.

  2. After several checks, _build_callargs() is called which returns another
  tuple 'callargs'.  This may be the same tuple as 'inargs', a slice of
  'inargs', or a completely fresh tuple, depending on several things (is is a
  COM method, are 'paramflags' available).

  3. If [out] parameters are present in paramflags, _build_callargs also
  creates and returns another object, which is either a single object or a
  tuple, whcih will later be used to build the function return value.

  4. _CallProc is then called with the 'callargs' tuple.  _CallProc first
  allocates two arrays.  The first is an array of 'struct argument' items, the
  second array has 'void *' entried.

  5. If 'converters' are present (converters is a sequence of argtypes'
  from_param methods), for each item in 'callargs' converter is called and the
  result passed to PyObject_asparam.  If 'converters' are not present, each argument
  is directly passed to ConvParm.

  6. For each arg, PyObject_asparam stores the contained C data (or a pointer to it,
  for structures) into the 'struct argument' array.

  7. Finally, a loop fills the 'void *' array so that each item points to the
  data contained in or pointed to by the 'struct argument' array.

  8. The 'void *' argument array is what _call_function_pointer
  expects. _call_function_pointer then has very little to do - only some
  libffi specific stuff, then it calls ffi_call.

  So, there are 4 data structures holding processed arguments:
  - the inargs tuple (in CFuncPtr_call)
  - the callargs tuple (in CFuncPtr_call)
  - the 'struct argguments' array
  - the 'void *' array

 */

#include "Python.h"
#include "structmember.h"

#ifdef MS_WIN32
#include <windows.h>
#else
#include <dlfcn.h>
#endif

#ifdef MS_WIN32
#define alloca _alloca
#endif

#include <ffi.h>
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

void SetException(DWORD code, EXCEPTION_RECORD *pr)
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
			if (pr->ExceptionInformation[0] == 0)
				PyErr_Format(PyExc_WindowsError,
					     "exception: access violation reading %p",
					     pr->ExceptionInformation[1]);
			else
				PyErr_Format(PyExc_WindowsError,
					     "exception: access violation writing %p",
					     pr->ExceptionInformation[1]);
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
				     "exception code 0x%08x",
				     code);
			break;
		}
	}
}

static DWORD HandleException(EXCEPTION_POINTERS *ptrs,
			     DWORD *pdw, EXCEPTION_RECORD *record)
{
	*pdw = ptrs->ExceptionRecord->ExceptionCode;
	*record = *ptrs->ExceptionRecord;
	return EXCEPTION_EXECUTE_HANDLER;
}

static PyObject *
check_hresult(PyObject *self, PyObject *args)
{
	HRESULT hr;
	if (!PyArg_ParseTuple(args, "i", &hr))
		return NULL;
	if (FAILED(hr))
		return PyErr_SetFromWindowsErr(hr);
	return PyInt_FromLong(hr);
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
	p->pffi_type = NULL;
	p->obj = NULL;
	memset(&p->value, 0, sizeof(p->value));
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

	if (self->pffi_type == &ffi_type_pointer) {
		sprintf(buffer, "<cparam 'P' (%08lx)>", (long)self->value.p);
	} else

		switch(self->pffi_type->type) {
		case FFI_TYPE_SINT8:
			sprintf(buffer, "<cparam 'b' (%d)>", self->value.b);
			break;
		case FFI_TYPE_UINT8:
			sprintf(buffer, "<cparam 'B' (%d)>", self->value.b);
			break;
		case FFI_TYPE_SINT16:
			sprintf(buffer, "<cparam 'h' (%d)>", self->value.h);
			break;
		case FFI_TYPE_UINT16:
			sprintf(buffer, "<cparam 'H' (%d)>", self->value.h);
			break;
		case FFI_TYPE_SINT32:
			sprintf(buffer, "<cparam 'l' (%d)>", self->value.i);
			break;
		case FFI_TYPE_UINT32:
			sprintf(buffer, "<cparam 'L' (%d)>", self->value.i);
			break;
#ifdef HAVE_LONG_LONG
		case FFI_TYPE_SINT64:
			sprintf(buffer,
#ifdef MS_WIN32
				"<cparam 'q' (%I64d)>",
#else
				"<cparam 'q' (%qd)>",
#endif
				self->value.q);
			break;
		case FFI_TYPE_UINT64:
			sprintf(buffer,
#ifdef MS_WIN32
				"<cparam 'Q' (%I64d)>",
#else
				"<cparam 'Q' (%qd)>",
#endif
				self->value.q);
			break;
#endif
		case FFI_TYPE_DOUBLE:
			sprintf(buffer, "<cparam 'd' (%f)>", self->value.d);
			break;
		case FFI_TYPE_FLOAT:
			sprintf(buffer, "<cparam 'f' (%f)>", self->value.f);
			break;
		default:
			sprintf(buffer, "<cparam '?' at %08lx>", (long)self);
			break;
		}
	return PyString_FromString(buffer);
}

static PyMemberDef PyCArgType_members[] = {
	{ "_obj", T_OBJECT,
	  offsetof(PyCArgObject, obj), READONLY,
	  "the wrapped object" },
	{ NULL },
};

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
	0,					/* tp_doc */
	0,					/* tp_traverse */
	0,					/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,					/* tp_iter */
	0,					/* tp_iternext */
	0,					/* tp_methods */
	PyCArgType_members,			/* tp_members */
};

/****************************************************************/
static int PyObject_asparam(PyObject *obj, struct argument *pa, int index)
{
	StgDictObject *stgdict = PyObject_stgdict(obj);
	PyObject *arg;

	pa->keep = NULL; /* so we cannot forget it later */

	/* ctypes instances know themselves how to pass as argument */
	if (stgdict)
		return stgdict->asparam((CDataObject *)obj, pa);
	if (obj == Py_None) {
		pa->ffi_type = &ffi_type_pointer;
		pa->pdata = &pa->value.p;
		pa->value.p = NULL;
		return 0;
	}
	if (PyInt_Check(obj)) {
		pa->ffi_type = &ffi_type_sint;
		pa->pdata = &pa->value.i;
		pa->value.i = PyInt_AS_LONG(obj);
		return 0;
	}
	if (PyLong_Check(obj)) {
		pa->ffi_type = &ffi_type_sint;
		pa->pdata = &pa->value.i;
		pa->value.i = (int)PyLong_AsUnsignedLongMask(obj);
		return 0;
	}
	if (PyString_Check(obj)) {
		pa->ffi_type = &ffi_type_pointer;
		pa->pdata = &pa->value.p;
		pa->value.p = PyString_AS_STRING(obj);
		Py_INCREF(obj);
		pa->keep = obj;
		return 0;
	}
#ifdef CTYPES_UNICODE
	/* XXX See Z_set. */
	/* XXX PyUnicode_AsWideChar(), */
	/* Pass as pointer by calling Z_set() */
	if (PyUnicode_Check(obj)) {
		pa->ffi_type = &ffi_type_pointer;
		pa->pdata = &pa->value.p;
		pa->keep = getentry("Z")->setfunc(&pa->value.p, obj, 0, NULL); /* CTYPE_c_wchar_p? */
		if (pa->keep == NULL)
			return -1;
		return 0;
	}
#endif
	if (PyCArg_CheckExact(obj)) {
		PyCArgObject *carg = (PyCArgObject *)obj;
		pa->ffi_type = carg->pffi_type;
		Py_INCREF(obj);
		pa->keep = obj;
		pa->pdata = &carg->value;
		return 0;
	}

	arg = PyObject_GetAttrString(obj, "_as_parameter_");
	/* Which types should we exactly allow here?
	   integers are required for using Python classes
	   as parameters (they have to expose the '_as_parameter_'
	   attribute)
	*/
	if (arg == 0) {
		PyErr_Format(PyExc_TypeError,
			     "Don't know how to convert parameter %d", index);
		return -1;
	}
	if (PyCArg_CheckExact(arg)) {
		PyCArgObject *carg = (PyCArgObject *)arg;
		pa->ffi_type = carg->pffi_type;
		pa->pdata = &carg->value;
		/* consumes the refcount: */
		pa->keep = arg;
		return 0;
	}
	if (PyInt_Check(arg)) {
		pa->ffi_type = &ffi_type_sint;
		pa->pdata = &pa->value.i;
		pa->value.i = PyInt_AS_LONG(arg);
		/* consumes the refcount: */
		pa->keep = arg;
		return 0;
	}
	Py_DECREF(arg);
	PyErr_Format(PyExc_TypeError,
		     "Don't know how to convert parameter %d", index);
	return -1;
}


ffi_type *GetType(PyObject *obj)
{
	StgDictObject *dict;
	if (obj == NULL)
		return &ffi_type_sint;
	dict = PyType_stgdict(obj);
	if (dict == NULL)
		return &ffi_type_sint;
#ifdef MS_WIN32
	/* This little trick works correctly with MSVC.
	   It returns small structures in registers
	*/
	if (dict->ffi_type.type == FFI_TYPE_STRUCT) {
		if (dict->ffi_type.size <= 4)
			return &ffi_type_sint32;
		else if (dict->ffi_type.size <= 8)
			return &ffi_type_sint64;
	}
#endif
	return &dict->ffi_type;
}


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
				  void **avalues,
				  ffi_type **atypes,
				  ffi_type *restype,
				  void *resmem,
				  int argcount)
{
	PyThreadState *_save = NULL; /* For Py_BLOCK_THREADS and Py_UNBLOCK_THREADS */
	ffi_cif cif;
	int cc;
#ifdef MS_WIN32
	int delta;
	DWORD dwExceptionCode;
	EXCEPTION_RECORD record;
#endif
	cc = FFI_DEFAULT_ABI;
#ifdef MS_WIN32
	if ((flags & FUNCFLAG_CDECL) == 0)
		cc = FFI_STDCALL;
	dwExceptionCode = 0;
#endif
	if (FFI_OK != ffi_prep_cif(&cif,
				   cc,
				   argcount,
				   restype,
				   atypes)) {
		PyErr_SetString(PyExc_RuntimeError,
				"ffi_prep_cif failed");
		return -1;
	}

	if ((flags & FUNCFLAG_PYTHONAPI) == 0)
		Py_UNBLOCK_THREADS
#ifdef MS_WIN32
#ifndef DEBUG_EXCEPTIONS
	__try {
#endif
		delta =
#endif
			ffi_call(&cif, (void *)pProc, resmem, avalues);
#ifdef MS_WIN32
#ifndef DEBUG_EXCEPTIONS
	}
	__except (HandleException(GetExceptionInformation(),
				  &dwExceptionCode, &record)) {
		;
	}
#endif
#endif
	if ((flags & FUNCFLAG_PYTHONAPI) == 0)
		Py_BLOCK_THREADS
#ifdef MS_WIN32
	if (dwExceptionCode) {
		SetException(dwExceptionCode, &record);
		return -1;
	}
	if (delta < 0) {
		if (flags & FUNCFLAG_CDECL)
			PyErr_Format(PyExc_ValueError,
				     "Procedure called with not enough "
				     "arguments (%d bytes missing) "
				     "or wrong calling convention",
				     -delta);
		else
			PyErr_Format(PyExc_ValueError,
				     "Procedure probably called with not enough "
				     "arguments (%d bytes missing)",
				     -delta);
		return -1;
	} else if (delta > 0) {
		PyErr_Format(PyExc_ValueError,
			     "Procedure probably called with too many "
			     "arguments (%d bytes in excess)",
			     delta);
		return -1;
	}
#endif
	if ((flags & FUNCFLAG_PYTHONAPI) && PyErr_Occurred())
		return -1;
	return 0;
}

#define RESULT_PASTE_INTO 1
#define RESULT_CALL_RESTYPE 2

/*
 * Convert the C value in result into an instance described by restype
 */
static PyObject *GetResult(PyObject *restype, void *result, PyObject *checker)
{
	StgDictObject *dict;

	if (restype == NULL) {
		return getentry("i")->getfunc(result, sizeof(int),
					      NULL, NULL, 0);
	}

	if (restype == Py_None) {
		Py_INCREF(Py_None);
		return Py_None;
	}

	dict = PyType_stgdict(restype);

	/* THIS code should probably move into CallProc, where GetResult is
	   called. But doesn't matter too much. */
#if IS_BIG_ENDIAN
	if (dict && dict->size < sizeof(ffi_arg)) {
		/* libffi returns the result in a buffer of
		   sizeof(ffi_arg).  This causes problems on big
		   endian machines, since the result buffer cannot
		   simply be casted to the actual result type.
		   Instead, we must adjust the pointer:
		*/
		char *ptr = result;
		ptr += sizeof(ffi_arg) - dict->size;
		result = ptr;
	}
#endif

	if (dict && dict->getfunc) {
		PyObject *retval = dict->getfunc(result, dict->size,
						 restype, NULL, 0);
		if (retval == NULL)
			return NULL;
		if (checker == NULL)
			return retval;
		{
			PyObject *v;
			v = PyObject_CallFunctionObjArgs(checker, retval, NULL);
			if (v == NULL)
				_AddTraceback("GetResult", __FILE__, __LINE__-2);
			Py_DECREF(retval);
			return v;
		}
	}

	if (PyCallable_Check(restype))
		return PyObject_CallFunction(restype, "i",
					     *(int *)result);
	PyErr_SetString(PyExc_TypeError,
			"Bug: cannot convert result");
	return NULL;
}

/*
 * Raise a new exception 'exc_class', adding additional text to the original
 * exception string.
 */
/*
  We should probably get rid of this function, and instead add a stack frame
  with _AddTraceback.
*/
void Extend_Error_Info(PyObject *exc_class, char *fmt, ...)
{
	va_list vargs;
	PyObject *tp, *v, *tb, *s, *cls_str, *msg_str;

	va_start(vargs, fmt);
	s = PyString_FromFormatV(fmt, vargs);
	va_end(vargs);
	if (!s)
		return;

	PyErr_Fetch(&tp, &v, &tb);
	PyErr_NormalizeException(&tp, &v, &tb);
	cls_str = PyObject_Str(tp);
	if (cls_str) {
		PyString_ConcatAndDel(&s, cls_str);
		PyString_ConcatAndDel(&s, PyString_FromString(": "));
	} else
		PyErr_Clear();
	msg_str = PyObject_Str(v);
	if (msg_str)
		PyString_ConcatAndDel(&s, msg_str);
	else {
		PyErr_Clear();
		PyString_ConcatAndDel(&s, PyString_FromString("???"));
	}
	PyErr_SetObject(exc_class, s);
	Py_XDECREF(tp);
	Py_XDECREF(v);
	Py_XDECREF(tb);
	Py_DECREF(s);
}


#ifdef MS_WIN32
#define alloca _alloca
#endif
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
		    PyObject *argcnv, /* tuple a converter objects */
		    PyObject *argtypes,
		    PyObject *restype,
		    PyObject *checker)
{
	int i, n, argcount, argcnv_count;
	struct argument *pa;

	struct argument *args;		/* array of temp storage for arguments */

	ffi_type **atypes;		/* array of argument ffi_types */
	void **avalues;			/* array of pointers to libffi argument values */
	ffi_type *rtype;		/* return value ffi_type */
	void *rvalue;			/* pointer to libffi return value */

	PyObject *retval = NULL;

	n = argcount = PyTuple_GET_SIZE(argtuple);
	/* an optional COM object this pointer */
	if (pIunk)
		++argcount;
	argcnv_count = argcnv ? PyTuple_GET_SIZE(argcnv) : 0;
	rtype = GetType(restype);

	args = (struct argument *)alloca(sizeof(struct argument) * argcount);
	memset(args, 0, sizeof(struct argument) * argcount);
	rvalue = alloca(max(rtype->size, sizeof(ffi_arg)));

	if (pIunk) {
		args[0].ffi_type = &ffi_type_pointer;
		args[0].pdata = &args[0].value.p;
		args[0].value.p = pIunk;
		pa = &args[1];
	} else {
		pa = &args[0];
	}

	/* Convert the arguments */
	for (i = 0; i < n; ++i, ++pa) {
		PyObject *converter;
		PyObject *arg;
		int err;

		arg = PyTuple_GET_ITEM(argtuple, i);	/* borrowed ref */
		/* For cdecl functions, we allow more actual arguments
		   than the length of the argcnv tuple.
		   This is checked in _ctypes::CFuncPtr_Call
		*/
		if (argcnv && argcnv_count > i) {
			PyObject *v;
			converter = PyTuple_GET_ITEM(argcnv, i);
			v = PyObject_CallFunctionObjArgs(converter,
							   arg,
							   NULL);
			if (v == NULL) {
				Extend_Error_Info(PyExc_ArgError, "argument %d: ", i+1);
				goto cleanup;
			}

			err = PyObject_asparam(v, pa, i+1);
			Py_DECREF(v);
			if (-1 == err) {
				Extend_Error_Info(PyExc_ArgError, "argument %d: ", i+1);
				goto cleanup;
			}
		} else {
			err = PyObject_asparam(arg, pa, i+1);
			if (-1 == err) {
				Extend_Error_Info(PyExc_ArgError, "argument %d: ", i+1);
				goto cleanup; /* leaking ? */
			}
		}
	}

	avalues = (void **)alloca(sizeof(void *) * argcount);
	atypes = (ffi_type **)alloca(sizeof(ffi_type *) * argcount);
	for (i = 0; i < argcount; ++i) {
		atypes[i] = args[i].ffi_type;
		avalues[i] = args[i].pdata;
/*
		if (atypes[i]->type == FFI_TYPE_STRUCT)
			avalues[i] = (void *)args[i].value.p;
		else
			avalues[i] = (void *)&args[i].value;
*/
	}

	if (-1 == _call_function_pointer(flags, pProc, avalues, atypes,
					 rtype, rvalue, argcount))
		goto cleanup;

#ifdef MS_WIN32
	if (flags & FUNCFLAG_HRESULT) {
		if (*(int *)rvalue & 0x80000000)
			retval = PyErr_SetFromWindowsErr(*(int *)rvalue);
		else
			retval = PyInt_FromLong(*(int *)rvalue);
	} else
#endif
		retval = GetResult(restype, rvalue, checker);
	/* Overwrite result memory, to catch bugs. */
	memset(rvalue, 0x55, max(rtype->size, sizeof(ffi_arg)));
  cleanup:
	for (i = 0; i < argcount; ++i)
		Py_XDECREF(args[i].keep);
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

static char copy_com_pointer_doc[] =
"CopyComPointer(a, b) -> integer\n";

static PyObject *
copy_com_pointer(PyObject *self, PyObject *args)
{
	PyObject *p1, *p2, *r = NULL;
	struct argument a, b;
	IUnknown *src, **pdst;
	if (!PyArg_ParseTuple(args, "OO:CopyComPointer", &p1, &p2))
		return NULL;
	a.keep = b.keep = NULL;

	if (-1 == PyObject_asparam(p1, &a, 0) || -1 == PyObject_asparam(p2, &b, 1))
		goto done;
	assert(a.pdata != NULL);
	assert(b.pdata != NULL);
	src = (IUnknown *)*(void **)a.pdata;
	pdst = (IUnknown **)*(void **)b.pdata;

	if (pdst == NULL)
		r = PyInt_FromLong(E_POINTER);
	else {
		if (src)
			src->lpVtbl->AddRef(src);
		*pdst = src;
		r = PyInt_FromLong(S_OK);
	}
  done:
	Py_XDECREF(a.keep);
	Py_XDECREF(b.keep);
	return r;
}
#else

static PyObject *py_dl_open(PyObject *self, PyObject *args)
{
	char *name;
	void * handle;
#ifdef RTLD_LOCAL	
	int mode = RTLD_NOW | RTLD_LOCAL;
#else
	/* cygwin doesn't define RTLD_LOCAL */
	int mode = RTLD_NOW;
#endif
	if (!PyArg_ParseTuple(args, "z:dlopen", &name))
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
 * Only for debugging so far: So that we can call CFunction instances
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
			    NULL,
			    NULL,
			    NULL,
			    NULL);
	return result;
}

/*
 * Only for debugging so far: So that we can call CFunction instances
 *
 * XXX Needs to accept more arguments: flags, argtypes, restype
 */
static PyObject *
call_cdeclfunction(PyObject *self, PyObject *args)
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
			    FUNCFLAG_CDECL,
			    NULL,
			    NULL,
			    NULL,
			    NULL);
	return result;
}

/*****************************************************************
 * functions
 */
static char sizeof_doc[] =
"sizeof(C type) -> integer\n"
"sizeof(C instance) -> integer\n"
"Return the size in bytes of a C instance";

static PyObject *
sizeof_func(PyObject *self, PyObject *obj)
{
	StgDictObject *dict;

	dict = PyType_stgdict(obj);
	if (dict)
		return PyInt_FromLong(dict->size);

	if (CDataObject_Check(obj))
		return PyInt_FromLong(((CDataObject *)obj)->b_size);
	PyErr_SetString(PyExc_TypeError,
			"this type has no size");
	return NULL;
}

static char alignment_doc[] =
"alignment(C type) -> integer\n"
"alignment(C instance) -> integer\n"
"Return the alignment requirements of a C instance";

static PyObject *
align_func(PyObject *self, PyObject *obj)
{
	StgDictObject *dict;

	dict = PyType_stgdict(obj);
	if (dict)
		return PyInt_FromLong(dict->align);

	dict = PyObject_stgdict(obj);
	if (dict)
		return PyInt_FromLong(dict->align);

	PyErr_SetString(PyExc_TypeError,
			"no alignment info");
	return NULL;
}

static char byref_doc[] =
"byref(C instance) -> byref-object\n"
"Return a pointer lookalike to a C instance, only usable\n"
"as function argument";

/*
 * We must return something which can be converted to a parameter,
 * but still has a reference to self.
 */
static PyObject *
byref(PyObject *self, PyObject *obj)
{
	PyCArgObject *parg;
	if (!CDataObject_Check(obj)) {
		PyErr_SetString(PyExc_TypeError,
				"expected CData instance");
		return NULL;
	}

	parg = new_CArgObject();
	if (parg == NULL)
		return NULL;

	parg->pffi_type = &ffi_type_pointer;
	Py_INCREF(obj);
	parg->obj = obj;
	parg->value.p = ((CDataObject *)obj)->b_ptr;
	return (PyObject *)parg;
}

static char addressof_doc[] =
"addressof(C instance) -> integer\n"
"Return the address of the C instance internal buffer";

static PyObject *
addressof(PyObject *self, PyObject *obj)
{
	if (CDataObject_Check(obj))
		return PyInt_FromLong((long)((CDataObject *)obj)->b_ptr);
	PyErr_SetString(PyExc_TypeError,
			"invalid type");
	return NULL;
}

static PyObject *
My_PyObj_FromPtr(PyObject *self, PyObject *args)
{
	int i;
	PyObject *ob;
	if (!PyArg_ParseTuple(args, "i", &i))
		return NULL;
	ob = (PyObject *)i;
	Py_INCREF(ob);
	return ob;
}

static PyObject *
My_Py_INCREF(PyObject *self, PyObject *arg)
{
	Py_INCREF(arg); /* that's what this function is for */
	Py_INCREF(arg); /* that for returning it */
	return arg;
}

static PyObject *
My_Py_DECREF(PyObject *self, PyObject *arg)
{
	Py_DECREF(arg); /* that's what this function is for */
	Py_INCREF(arg); /* that's for returning it */
	return arg;
}

#ifdef CTYPES_UNICODE

static char set_conversion_mode_doc[] =
"FormatError(encoding, errors) -> (previous-encoding, previous-errors)\n\
\n\
Set the encoding and error handling ctypes uses when converting\n\
between unicode and strings.  Returns the previous values.\n";

static PyObject *
set_conversion_mode(PyObject *self, PyObject *args)
{
	char *coding, *mode;
	PyObject *result;

	if (!PyArg_ParseTuple(args, "zs", &coding, &mode))
		return NULL;
	result = Py_BuildValue("(zz)", conversion_mode_encoding, conversion_mode_errors);
	if (coding) {
		PyMem_Free(conversion_mode_encoding);
		conversion_mode_encoding = PyMem_Malloc(strlen(coding) + 1);
		strcpy(conversion_mode_encoding, coding);
	} else {
		conversion_mode_encoding = NULL;
	}
	PyMem_Free(conversion_mode_errors);
	conversion_mode_errors = PyMem_Malloc(strlen(mode) + 1);
	strcpy(conversion_mode_errors, mode);
	return result;
}
#endif

static char cast_doc[] =
"cast(cobject, ctype) -> ctype-instance\n\
\n\
Create an instance of ctype, and copy the internal memory buffer\n\
of cobject to the new instance.  Should be used to cast one type\n\
of pointer to another type of pointer.\n\
Doesn't work correctly with ctypes integers.\n";

static PyObject *cast(PyObject *self, PyObject *args)
{
	PyObject *obj, *ctype;
	struct argument a;
	CDataObject *result;

	if (!PyArg_ParseTuple(args, "OO", &obj, &ctype))
		return NULL;
	memset(&a, 0, sizeof(struct argument));
	if (-1 == PyObject_asparam(obj, &a, 1))
		return NULL;
	assert(a.pdata != NULL);
	result = (CDataObject *)PyObject_CallFunctionObjArgs(ctype, NULL);
	if (result == NULL) {
		Py_XDECREF(a.keep);
		return NULL;
	}
	// result->b_size
	// a.ffi_type->size
	memcpy(result->b_ptr, a.pdata,
	       min(result->b_size, a.ffi_type->size));
	Py_XDECREF(a.keep);
	return (PyObject *)result;
}

static char string_at_doc[] =
"string_at(addr[, size]) -> string\n\
\n\
Return the string at addr.\n";

static PyObject *
string_at(PyObject *self, PyObject *args)
{
	PyObject *result = NULL;
	PyObject *src;
	struct argument a_arg;
	int size;

	if (!PyArg_ParseTuple(args, "O|i", &src, &size))
		return NULL;
	memset(&a_arg, 0, sizeof(struct argument));
	if (-1 == PyObject_asparam(src, &a_arg, 1))
		return NULL;
	if (PyTuple_GET_SIZE(args) == 1)
		result = PyString_FromString(*(void **)a_arg.pdata);
	else
		result = PyString_FromStringAndSize(*(void **)a_arg.pdata, size);
	Py_XDECREF(a_arg.keep);
	return result;
}

#ifdef CTYPES_UNICODE
static char wstring_at_doc[] =
"wstring_at(addr[, size]) -> unicode string\n\
\n\
Return the wide string at addr.\n";

static PyObject *
wstring_at(PyObject *self, PyObject *args)
{
	PyObject *result = NULL;
	PyObject *src;
	struct argument a_arg;
	int size;

	if (!PyArg_ParseTuple(args, "O|i", &src, &size))
		return NULL;
	memset(&a_arg, 0, sizeof(struct argument));
	if (-1 == PyObject_asparam(src, &a_arg, 1))
		return NULL;
	if (PyTuple_GET_SIZE(args) == 1)
		result = PyUnicode_FromWideChar(*(void **)a_arg.pdata, wcslen(*(void **)a_arg.pdata));
	else
		result = PyUnicode_FromWideChar(*(void **)a_arg.pdata, size);
	Py_XDECREF(a_arg.keep);
	return result;
}
#endif


PyMethodDef module_methods[] = {
	{"string_at", string_at, METH_VARARGS, string_at_doc},
	{"cast", cast, METH_VARARGS, cast_doc},
#ifdef CTYPES_UNICODE
	{"wstring_at", wstring_at, METH_VARARGS, wstring_at_doc},
	{"set_conversion_mode", set_conversion_mode, METH_VARARGS, set_conversion_mode_doc},
#endif
#ifdef MS_WIN32
	{"CopyComPointer", copy_com_pointer, METH_VARARGS, copy_com_pointer_doc},
	{"FormatError", format_error, METH_VARARGS, format_error_doc},
	{"LoadLibrary", load_library, METH_VARARGS, load_library_doc},
	{"FreeLibrary", free_library, METH_VARARGS, free_library_doc},
	{"_check_HRESULT", check_hresult, METH_VARARGS},
#else
	{"dlopen", py_dl_open, METH_VARARGS, "dlopen a library"},
	{"dlclose", py_dl_close, METH_VARARGS, "dlclose a library"},
	{"dlsym", py_dl_sym, METH_VARARGS, "find symbol in shared library"},
#endif
	{"alignment", align_func, METH_O, alignment_doc},
	{"sizeof", sizeof_func, METH_O, sizeof_doc},
	{"byref", byref, METH_O, byref_doc},
	{"addressof", addressof, METH_O, addressof_doc},
	{"call_function", call_function, METH_VARARGS },
	{"call_cdeclfunction", call_cdeclfunction, METH_VARARGS },
	{"PyObj_FromPtr", My_PyObj_FromPtr, METH_VARARGS },
	{"Py_INCREF", My_Py_INCREF, METH_O },
	{"Py_DECREF", My_Py_DECREF, METH_O },
	{NULL,      NULL}        /* Sentinel */
};

/*
 Local Variables:
 compile-command: "cd .. && python setup.py -q build -g && python setup.py -q build install --home ~"
 End:
*/
