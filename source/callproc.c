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

   1. (in CFuncPtr_call) restype and converters are got from self or stgdict.
   2. If it's a COM method, the COM pointer is retrieved from the argument list.
   3. If converters are there, the number of arguments is checked.
   4. CallProc is called, for a COM method with a slice [1:-1] of the arg list.

   5. An array of PyCArgObject pointers is allocated to hold all the converted arguments.
   6. If converters are present, each argument is replaced by the result of passing the argument
      to the converter.
   7. Each argument is passed to ConvParam, which creates a PyCArgObject.
   8. Another PyCArgObject is allocated to hold the result of the function call.
   9. PrepareResult() is called with the restype to fill out the tag field of the PyCArgObject.

  10. _call_function_pointer is called.

  11. GetResult() is called with the 'result' PyCArgObject' to convert the C data
      into a Python object.
  12. All the PyCArgObjects are DECREF'd.

  What does PrepareResult and GetResult do?

  PrepareResult sets the 'tag' field of the PyCArgObject.

    - if no restype, assume integer, and set it to 'i'.
    - get the type's stgdict, if it has a getfunc and a string proto,
      set the tag to the format character (if it is in "bBhHiIlLqQdfP")
    - if it is a ctypes Pointer type, set it to 'P'
    - if it is callable, set it to 'i' (and later call it with the integer result)
    - otherwise assume integer, and set it to 'i'
  
  _call_function_pointer iterates over the PyCArgObject array, and pushed their values
  onto the stack, C type depending on the 'tag'.
  Depending if the result PyCArgObject's 'tag', the function is called and the result
  stored into the result's space.

  The libffi version of _call_function_pointer creates an array of ffi_type pointers,
  and fills it with ffi_type_xxx depending on the PyCArgObject's tag value.
  Same for the PyCArgObject's result tag, then calls the ffi_call function.

  ffi_call needs an array of ffi_type pointers, and an array of void* pointers
  pointing to the argument values (the value field of the PyCArgObject instances).

  GetResult doesn't use the 'tag' field, it examines restype again:

    - If it is a ctypes pointer: create an empty instance, and memcpy() thze result into it.
    - If the restype's stgdict has a getfunc, call it.
    - If the restype is callable, call it with the integer result
  
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
				     "exception code 0x%08X",
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
	p->tag = '\0';
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

struct argument {
	ffi_type *ffi_type;
	PyObject *keep;
	union {
		char c;
		char b;
		short h;
		int i;
		long l;
#ifdef HAVE_LONG_LONG
		PY_LONG_LONG q;
#endif
		double d;
		float f;
		void *p;
	} value;
};

/*
 * Convert a single Python object into a PyCArgObject and return it.
 */
static int ConvParam(PyObject *obj, int index, struct argument *pa)
{
	if (PyCArg_CheckExact(obj)) {
		PyCArgObject *carg = (PyCArgObject *)obj;
		pa->ffi_type = carg->pffi_type;
		memcpy(&pa->value, &carg->value, sizeof(pa->value));
		return 0;
	}

	/* check for None, integer, string or unicode and use directly if successful */
	if (obj == Py_None) {
		pa->ffi_type = &ffi_type_pointer;
		pa->value.p = NULL;
		return 0;
	}

	if (PyInt_Check(obj)) {
		pa->ffi_type = &ffi_type_sint;
		pa->value.l = PyInt_AS_LONG(obj);
		return 0;
	}

	if (PyLong_Check(obj)) {
		pa->ffi_type = &ffi_type_sint;
		pa->value.l = (long)PyLong_AsUnsignedLong(obj);
		if (pa->value.l == -1 && PyErr_Occurred()) {
			PyErr_Clear();
			pa->value.l = PyLong_AsLong(obj);
			if (pa->value.l == -1 && PyErr_Occurred()) {
				PyErr_SetString(PyExc_OverflowError,
						"long int too long to convert");
				return -1;
			}
		}
		return 0;
	}

	if (PyString_Check(obj)) {
		pa->ffi_type = &ffi_type_pointer;
		pa->value.p = PyString_AS_STRING(obj);
		return 0;
	}

#ifdef HAVE_USABLE_WCHAR_T
	if (PyUnicode_Check(obj)) {
		pa->ffi_type = &ffi_type_pointer;
		pa->value.p = PyUnicode_AS_UNICODE(obj);
		return 0;
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
		if (arg == 0) {
			PyErr_Format(PyExc_TypeError,
				     "Don't know how to convert parameter %d", index);
			return -1;
		}
		if (PyCArg_CheckExact(arg)) {
			PyCArgObject *carg = (PyCArgObject *)arg;
			pa->ffi_type = carg->pffi_type;
			memcpy(&pa->value, &carg->value, sizeof(pa->value));
			pa->keep = arg;
			return 0;
		}
		if (PyInt_Check(arg)) {
			pa->ffi_type = &ffi_type_sint;
			pa->value.l = PyInt_AS_LONG(arg);
			pa->keep = arg;
			return 0;
		}
#if 0
/* Does this make sense? Now that even Structure and Union types
   have an _as_parameter_ property implemented in C, which returns
   a PyCArgObject?
*/
		if (CDataObject_Check(arg)) {
			CDataObject *mem = (CDataObject *)arg;
			parm->tag = 'V';
			parm->value.p = mem->b_ptr;
			parm->size = mem->b_size;
			/* This consumes the refcount of arg */
			parm->obj = arg;
			return parm;
		}
#endif
		Py_DECREF(arg);
		PyErr_Format(PyExc_TypeError,
			     "Don't know how to convert parameter %d", index);
		return -1;
	}
}


ffi_type *GetType(PyObject *obj)
{
	StgDictObject *dict = PyType_stgdict(obj);
	if (dict == NULL)
		return &ffi_type_sint;
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
				  struct argument *res,
				  int argcount)
{
	ffi_cif cif;
	int cc;
#ifdef MS_WIN32
	int delta;
	DWORD dwExceptionCode;
	EXCEPTION_RECORD record;
#endif
	/* XXX check before here */
	if (res->ffi_type == NULL) {
		PyErr_SetString(PyExc_RuntimeError,
				"No ffi_type for result");
		return -1;
	}
	
	cc = FFI_DEFAULT_ABI;
#ifdef MS_WIN32
	if ((flags & FUNCFLAG_CDECL) == 0)
		cc = FFI_STDCALL;
	dwExceptionCode = 0;
#endif
	if (FFI_OK != ffi_prep_cif(&cif,
				   cc,
				   argcount,
				   res->ffi_type,
				   atypes)) {
		PyErr_SetString(PyExc_RuntimeError,
				"ffi_prep_cif failed");
		return -1;
	}

	Py_BEGIN_ALLOW_THREADS
#ifdef MS_WIN32
#ifndef DEBUG_EXCEPTIONS
	__try {
#endif
		delta =
#endif
			ffi_call(&cif, (void *)pProc, &res->value, avalues);
#ifdef MS_WIN32
#ifndef DEBUG_EXCEPTIONS
	}
	__except (HandleException(GetExceptionInformation(),
				  &dwExceptionCode, &record)) {
		;
	}
#endif
#endif
	Py_END_ALLOW_THREADS
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
	return 0;
}

#define RESULT_PASTE_INTO 1
#define RESULT_CALL_RESTYPE 2

/*
 * Fill out the format field of 'result', depending on 'restype'.
 */
void PrepareResult(PyObject *restype, PyCArgObject *result)
{
	StgDictObject *dict;

	if (restype == NULL) {
		result->pffi_type = &ffi_type_sint;
		return;
	}

	dict = PyType_stgdict(restype);
	if (dict && dict->getfunc) {
		result->pffi_type = &dict->ffi_type;
		return;
	}

	if (PyCallable_Check(restype)) {
		result->pffi_type = &ffi_type_sint;
		return;
	}

	if (restype == Py_None) {
		result->pffi_type = &ffi_type_void;
		return;
	}
	/* should not occurr */
	result->pffi_type = &ffi_type_sint;
}

/*
 * Convert the C value in result into an instance described by restype
 */
static PyObject *GetResult(PyObject *restype, struct argument *result)
{
	StgDictObject *dict;

	assert(restype);

	if (restype == Py_None) {
		Py_INCREF(Py_None);
		return Py_None;
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

	dict = PyType_stgdict(restype);
	if (dict && dict->getfunc) {
		/* ffi.h defines the endianness:
		   1234 = LIL_ENDIAN, 4321 = BIGENDIAN */
#if (BYTEORDER == 4321)
		/* This hack is needed for big endian machines.
		   Is there another way?
		 */
		char c;
		short s;
		int i;
		long l;
		switch (dict->size) {
		case 1:
			c = (char)result->value.l;
			return dict->getfunc(&c, dict->size);
		case SIZEOF_SHORT:
			s = (short)result->value.l;
			return dict->getfunc(&s, dict->size);
		case SIZEOF_INT:
			i = (int)result->value.l;
			return dict->getfunc(&i, dict->size);
#if (SIZEOF_LONG != SIZEOF_INT)
		case SIZEOF_LONG:
			l = (long)result->value.l;
			return dict->getfunc(&l, dict->size);
#endif
		}
#endif
		return dict->getfunc(&result->value, dict->size);
	}
	if (PyCallable_Check(restype))
		return PyObject_CallFunction(restype, "i",
					     result->value.i);
	PyErr_SetString(PyExc_TypeError,
			"Bug: cannot convert result");
	return NULL; /* to silence the compiler */
}

void Extend_Error_Info(char *fmt, ...)
{
	va_list vargs;
	PyObject *tp, *v, *tb, *s, *msg;

	va_start(vargs, fmt);
	s = PyString_FromFormatV(fmt, vargs);
	va_end(vargs);
	if (!s)
		return;

	PyErr_Fetch(&tp, &v, &tb);
	PyErr_NormalizeException(&tp, &v, &tb);
	msg = PyObject_Str(v);
	if (msg) {
		PyString_ConcatAndDel(&s, msg);
		Py_DECREF(v);
		PyErr_Restore(tp, s, tb);
	} else {
		PyErr_Clear();
		PyErr_Restore(tp, v, tb);
	}
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
		    PyObject *argtypes, /* misleading name: This is a method,
					   not a type (the .from_param class
					   nethod) */
		    PyObject *restype)
{
	int i, n, argcount;
	struct argument result;
	struct argument *args, *pa;
	ffi_type **atypes;
	void **avalues;
	PyObject *retval = NULL;

	n = argcount = PyTuple_GET_SIZE(argtuple);
	/* an optional COM object this pointer */
	if (pIunk)
		++argcount;

	args = (struct argument *)alloca(sizeof(struct argument) * argcount);
	memset(args, 0, sizeof(struct argument) * argcount);

	if (pIunk) {
		args[0].ffi_type = &ffi_type_pointer;
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
		if (argtypes) {
			PyObject *v;
			converter = PyTuple_GET_ITEM(argtypes, i);
			v = PyObject_CallFunctionObjArgs(converter,
							   arg,
							   NULL);
			if (v == NULL) {
				Extend_Error_Info("while constructing argument %d:\n", i+1);
				goto cleanup;
			}

			err = ConvParam(v, i+1, pa);
			Py_DECREF(v);
			if (-1 == err) {
				Extend_Error_Info("while constructing argument %d:\n", i+1);
				goto cleanup;
			}
		} else {
			err = ConvParam(arg, i+1, pa);
			if (-1 == err) {
				Extend_Error_Info("while constructing argument %d:\n", i+1);
				goto cleanup; /* leaking ? */
			}
		}
	}

	result.ffi_type = GetType(restype);

	avalues = (void **)alloca(sizeof(void *) * argcount);
	atypes = (ffi_type **)alloca(sizeof(ffi_type *) * argcount);
	for (i = 0; i < argcount; ++i) {
		atypes[i] = args[i].ffi_type;
		if (atypes[i]->type == FFI_TYPE_STRUCT)
			avalues[i] = (void *)args[i].value.p;
		else
			avalues[i] = (void *)&args[i].value;
	}

	if (-1 == _call_function_pointer(flags, pProc, avalues, atypes, &result, argcount))
		goto cleanup;

#ifdef MS_WIN32
	if (flags & FUNCFLAG_HRESULT) {
		if (result.value.i & 0x80000000)
			retval = PyErr_SetFromWindowsErr(result.value.i);
		else
			retval = PyInt_FromLong(result.value.i);
	} else
#endif
		retval = GetResult(restype, &result);
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

/* obsolete, should be removed */
/* Only used by sample code (in samples\Windows\COM.py) */
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
#ifdef RTLD_LOCAL	
	int mode = RTLD_NOW | RTLD_LOCAL;
#else
	/* cygwin doesn't define RTLD_LOCAL */
	int mode = RTLD_NOW;
#endif
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

PyMethodDef module_methods[] = {
#ifdef MS_WIN32
	{"FormatError", format_error, METH_VARARGS, format_error_doc},
	{"LoadLibrary", load_library, METH_VARARGS, load_library_doc},
	{"FreeLibrary", free_library, METH_VARARGS, free_library_doc},
	{"call_commethod", call_commethod, METH_VARARGS },
	{"HRESULT", check_hresult, METH_VARARGS},
#else
	{"dlopen", py_dl_open, METH_VARARGS, "dlopen a library"},
	{"dlclose", py_dl_close, METH_VARARGS, "dlclose a library"},
	{"dlsym", py_dl_sym, METH_VARARGS, "find symbol in shared library"},
#endif
	{"alignment", align_func, METH_O},
	{"sizeof", sizeof_func, METH_O},
	{"byref", byref, METH_O},
	{"addressof", addressof, METH_O},
	{NULL,      NULL}        /* Sentinel */
};

/*
 Local Variables:
 compile-command: "cd .. && python setup.py -q build -g && python setup.py -q build install --home ~"
 End:
*/
