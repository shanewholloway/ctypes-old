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

#define USE_LIBFFI

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

/*
 * Convert a single Python object into a PyCArgObject and return it.
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
		parm->pffi_type = &ffi_type_pointer;
		parm->tag = 'P';
		parm->value.p = NULL;
		Py_INCREF(Py_None);
		parm->obj = Py_None;
		return parm;
	}

	if (PyInt_Check(obj)) {
		parm->pffi_type = &ffi_type_sint;
		parm->tag = 'i';
		parm->value.i = PyInt_AS_LONG(obj);
		Py_INCREF(obj);
		parm->obj = obj;
		return parm;
	}

	if (PyLong_Check(obj)) {
		parm->pffi_type = &ffi_type_sint;
		parm->tag = 'i';
		parm->value.i = (long)PyLong_AsUnsignedLong(obj);
		if (parm->value.i == -1 && PyErr_Occurred()) {
			PyErr_Clear();
			parm->value.i = PyLong_AsLong(obj);
			if (parm->value.i == -1 && PyErr_Occurred()) {
				PyErr_SetString(PyExc_OverflowError,
						"long int too long to convert");
				return NULL;
			}
		}
		Py_INCREF(obj);
		parm->obj = obj;
		return parm;
	}

	if (PyString_Check(obj)) {
		parm->pffi_type = &ffi_type_pointer;
		parm->tag = 'P';
		parm->value.p = PyString_AS_STRING(obj);
		Py_INCREF(obj);
		parm->obj = obj;
		return parm;
	}

#ifdef HAVE_USABLE_WCHAR_T
	if (PyUnicode_Check(obj)) {
		parm->pffi_type = &ffi_type_pointer;
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
		if (arg == 0) {
			Py_DECREF(parm);
			PyErr_Format(PyExc_TypeError,
				     "Don't know how to convert parameter %d", index);
			return NULL;
		}
		if (PyCArg_CheckExact(arg)) {
			Py_DECREF(parm);
			return (PyCArgObject *)arg;
		}
		if (PyInt_Check(arg)) {
			parm->pffi_type = &ffi_type_sint;
			parm->tag = 'i';
			parm->value.i = PyInt_AS_LONG(arg);
			Py_DECREF(arg);
			Py_INCREF(obj);
			parm->obj = obj;
			return parm;
		}
#if 0
/* Does this make sense? Now that even Structure and Union types
   have an _as_parameter_ property implemented in C, which returns
   a PyCArgObject?
*/
#ifdef CAN_PASS_BY_VALUE
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
#endif
		Py_DECREF(parm);
		PyErr_Format(PyExc_TypeError,
			     "Don't know how to convert parameter %d", index);
		return NULL;
	}
}


#ifdef USE_LIBFFI

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
	ffi_type **atypes;
	void **values;
	int i;
	int cc;
#ifdef MS_WIN32
	int delta;
	DWORD dwExceptionCode;
	EXCEPTION_RECORD record;
#endif
	atypes = (ffi_type **)alloca(argcount * sizeof(ffi_type *));
	values = (void **)alloca(argcount * sizeof(void *));

	for (i = 0; i < argcount; ++i) {
		ffi_type *tp = parms[i]->pffi_type;
		if (tp == NULL) {
			PyErr_SetString(PyExc_RuntimeError,
					"No ffi_type for an argument");
			return -1;
		}
		atypes[i] = tp;
		/* For structure parameters (by value), parg->value doesn't
		   contain the structure data itself, instead parg->value.p
		   *points* to the structure's data. See also _ctypes.c, function
		   Struct_as_parameter().
		*/
		if (tp->type == FFI_TYPE_STRUCT)
			values[i] = parms[i]->value.p;
		else
			values[i] = &parms[i]->value;
	}
	if (res->pffi_type == NULL) {
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
				   res->pffi_type,
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
			ffi_call(&cif, (void *)pProc, &res->value, values);
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
#else /* USE_LIBFFI */
#pragma optimize ("", off)
/*
 * Can you figure out what this does? ;-)
 */
static void __stdcall push(void)
{
}

static int _call_function_pointer(int flags,
				  PPROC pProc,
				  PyCArgObject **parms,
				  PyCArgObject *res,
				  int argcount)
{
	int i;
	DWORD dwExceptionCode;
	EXCEPTION_RECORD record;
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
		if (parms[i]->pffi_type == NULL) {
			fprintf(stderr, "NO FFI_TYPE %c\n", parms[i]->tag);
#ifdef _DEBUG
			_asm int 3;
#endif
		}
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
		case 'u':
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
			argbytes += sizeof(PY_LONG_LONG);
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
		case 'X': /* BSTR */
			push(parms[i]->value.p);
			argbytes += sizeof(void *);
			break;
#ifdef CAN_PASS_BY_VALUE
		case 'V':
		{
			int n;
			int *p;
			n = parms[i]->size;
			if (n % sizeof(int))
				n += sizeof(int);
			n /= sizeof(int);
			n -= 1;
			p = (int *)parms[i]->value.p;
			while (n >= 0) {
				push(p[n--]);
				argbytes += sizeof(int);
			}
		}
		break;
#endif
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
			res->value.q = ((PY_LONG_LONG(*)())pProc)();
			break;
#endif
		case 'z':
		case 'Z':
		case 'P':
			res->value.p = ((void *(*)())pProc)();
			break;
		case 'v':
			((void(*)())pProc)();
			break;
		default:
			/* XXX Signal bug */
			res->tag |= 0x80;
			break;
		}
#ifndef DEBUG_EXCEPTIONS
	}
	__except (HandleException(GetExceptionInformation(),
				  &dwExceptionCode, &record)) {
		;
	}
#endif
	_asm sub new_esp, esp;
	_asm mov esp, save_esp;

	Py_END_ALLOW_THREADS

	if (dwExceptionCode) {
		SetException(dwExceptionCode, &record);
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
		/* Try to give a better error message */
		if (flags & FUNCFLAG_CDECL)
			PyErr_Format(PyExc_ValueError,
				     "Procedure called with not enough "
				     "arguments (%d bytes missing) "
				     "or wrong calling convention",
				     -new_esp);
		else
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

#endif /* USE_LIBFFI */

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
		result->tag = 'i';
		return;
	}

	/* XXX Wouldn't it be better to store the 'fmt' directly
	   in the stgdict? And for the libffi version, store the ffi_type
	   pointer there?
	*/
	dict = PyType_stgdict(restype);
	if (dict && dict->getfunc && dict->proto && PyString_Check(dict->proto)) {
		char *fmt = PyString_AS_STRING(dict->proto);
		/* XXX This should probably be checked when assigning the restype
		   attribute
		*/
		if (strchr("zcbBhHiIlLqQdfP", fmt[0])) {
			result->tag = fmt[0];
			result->pffi_type = &dict->ffi_type;
			return;
		}
	}

/* Remove later */
	if (PyString_Check(restype)) {
		assert(0);
		/* XXX Is it single letter? */
		result->tag = PyString_AS_STRING(restype)[0];
		return;
	}

	if (PointerTypeObject_Check(restype)) {
		result->pffi_type = &ffi_type_pointer;
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
		result->pffi_type = &ffi_type_sint;
		return;
	}

	if (restype == Py_None) {
		result->tag = 'v'; /* call with void result */
		result->pffi_type = &ffi_type_void;
		return;
	}

	/* XXX This should not occur... */
	result->tag = 'i';
	result->pffi_type = &ffi_type_sint;
}

/*
 * Convert the C value in result into an instance described by restype
 */
static PyObject *GetResult(PyObject *restype, PyCArgObject *result)
{
	StgDictObject *dict;

	if (restype == Py_None) {
		Py_INCREF(Py_None);
		return Py_None;
	}

	if (restype == NULL)
		return ToPython(&result->value, result->tag);

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
	if (dict && dict->getfunc)
		/* We don't do size-checking, we assume PrepareResult
		   has already done it. */
		return dict->getfunc(&result->value, dict->size);

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
		pargs[0]->pffi_type = &ffi_type_pointer;
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
			/* new ref */
			arg = PyObject_CallFunctionObjArgs(converter,
							   arg,
							   NULL);
			if (arg == NULL) {
				Extend_Error_Info("while constructing argument %d:\n", i+1);
				goto error;
			}

			*pp = ConvParam(arg, i+1);
			Py_DECREF(arg);
			if (!*pp) {
				Extend_Error_Info("while constructing argument %d:\n", i+1);
				goto error;
			}
		} else {
			*pp = ConvParam(arg, i+1);
			if (!*pp) {
				Extend_Error_Info("while constructing argument %d:\n", i+1);
				goto error; /* leaking ? */
			}
		}
	}

	/* Is it possible to allocate Python objects on the stack
	   instead of on the heap? */
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
