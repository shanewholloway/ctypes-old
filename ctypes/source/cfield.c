#include "Python.h"
#include "structmember.h"

#include <ffi.h>
#include "ctypes.h"
#ifdef MS_WIN32
#include <windows.h>
#endif
/******************************************************************/
/*
  CField_Type
*/
static PyObject *
CField_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	CFieldObject *obj;

	obj = (CFieldObject *)type->tp_alloc(type, 0);
	return (PyObject *)obj;
}


/*
 * Expects the size, index and offset for the current field in *psize and
 * *poffset, stores the total size so far in *psize, the offset for the next
 * field in *poffset, the alignment requirements for the current field in
 * *palign, and returns a field desriptor for this field.
 */
PyObject *
CField_FromDesc(PyObject *desc, int index,
		int *psize, int *poffset, int *palign, int pack)
{
	CFieldObject *self;
	PyObject *proto;
	int size, align, length;
	SETFUNC setfunc = NULL;
	GETFUNC getfunc = NULL;
	StgDictObject *dict;

	self = (CFieldObject *)PyObject_CallObject((PyObject *)&CField_Type,
						   NULL);
	if (self == NULL)
		return NULL;

	dict = PyType_stgdict(desc);
	if (!dict) {
		PyErr_SetString(PyExc_TypeError,
				"has no _stginfo_");
		Py_DECREF(self);
		return NULL;
	}
	size = dict->size;
	if (pack)
		align = min(pack, dict->align);
	else
		align = dict->align;
	length = dict->length;
	proto = desc;

	/*  Field descriptors for 'c_char * n' are be scpecial cased to
	   return a Python string instead of an Array object instance...
	*/
	if (ArrayTypeObject_Check(proto)) {
		StgDictObject *adict = PyType_stgdict(proto);
		StgDictObject *idict;
		if (adict && adict->proto) {
			idict = PyType_stgdict(adict->proto);
			if (idict->getfunc == getentry("c")->getfunc) {
				struct fielddesc *fd = getentry("s");
				getfunc = fd->getfunc;
				setfunc = fd->setfunc;
			}
#ifdef HAVE_USABLE_WCHAR_T
			if (idict->getfunc == getentry("u")->getfunc) {
				struct fielddesc *fd = getentry("U");
				getfunc = fd->getfunc;
				setfunc = fd->setfunc;
			}
#endif
		}
	}

	self->setfunc = setfunc;
	self->getfunc = getfunc;
	self->index = index;

	Py_XINCREF(proto);
	self->proto = proto;

	if (*poffset % align) {
		int delta = align - (*poffset % align);
		*psize += delta;
		*poffset += delta;
	}

	self->size = size;
	*psize += size;

	self->offset = *poffset;
	*poffset += size;

	*palign = align;

	return (PyObject *)self;
}

static int
CField_set(CFieldObject *self, PyObject *inst, PyObject *value)
{
	CDataObject *dst;
	char *ptr;
	assert(CDataObject_Check(inst));
	dst = (CDataObject *)inst;
	ptr = dst->b_ptr + self->offset;
	return CData_set(inst, self->proto, self->setfunc, value,
			 self->index, self->size, ptr);
}

static PyObject *
CField_get(CFieldObject *self, PyObject *inst, PyTypeObject *type)
{
	CDataObject *src;
	if (inst == NULL) {
		Py_INCREF(self);
		return (PyObject *)self;
	}
	assert(CDataObject_Check(inst));
	src = (CDataObject *)inst;
	return CData_get(self->proto, self->getfunc, inst,
			 self->index, self->size, src->b_ptr + self->offset);
}

static PyMemberDef CField_members[] = {
	{ "offset", T_UINT,
	  offsetof(CFieldObject, offset), READONLY,
	  "offset in bytes of this field"},
	{ "size", T_UINT,
	  offsetof(CFieldObject, size), READONLY,
	  "size in bytes of this field"},
	{ NULL },
};

PyTypeObject CField_Type = {
	PyObject_HEAD_INIT(NULL)
	0,					/* ob_size */
	"_ctypes.CField",				/* tp_name */
	sizeof(CFieldObject),			/* tp_basicsize */
	0,					/* tp_itemsize */
	0,					/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	0,					/* tp_compare */
	0,					/* tp_repr */
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
	NULL,					/* tp_doc */
	0,					/* tp_traverse */
	0,					/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,					/* tp_iter */
	0,					/* tp_iternext */
	0,					/* tp_methods */
	CField_members,				/* tp_members */
	0,					/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	(descrgetfunc)CField_get,		/* tp_descr_get */
	(descrsetfunc)CField_set,		/* tp_descr_set */
	0,					/* tp_dictoffset */
	0,					/* tp_init */
	0,					/* tp_alloc */
	CField_new,				/* tp_new */
	0,					/* tp_free */
};


/******************************************************************/
/*
  Accessor functions
*/

/* Derived from Modules/structmodule.c:
   Helper routine to get a Python integer and raise the appropriate error
   if it isn't one */

static int
get_long(PyObject *v, long *p)
{
	long x;
	if (!PyInt_Check(v) && !PyLong_Check(v)) {
		PyErr_Format(PyExc_TypeError,
			     "int expected instead of %s instance",
			     v->ob_type->tp_name);
		return -1;
	}
	x = PyInt_AsLong(v);
	if (x == -1 && PyErr_Occurred()) {
		if (PyErr_ExceptionMatches(PyExc_OverflowError))
			PyErr_SetString(PyExc_ValueError,
					"Value out of range");
		return -1;
	}
	*p = x;
	return 0;
}

/* Same, but handling unsigned long */

static int
get_ulong(PyObject *v, unsigned long *p)
{
	if (PyLong_Check(v)) {
		unsigned long x = PyLong_AsUnsignedLong(v);
		if (x == (unsigned long)(-1) && PyErr_Occurred()) {
			if (PyErr_ExceptionMatches(PyExc_OverflowError))
				PyErr_SetString(PyExc_ValueError,
						"Value out of range");
			return -1;
		}
		*p = x;
		return 0;
	} else if (PyInt_Check(v)) {
		long x = PyInt_AsLong(v);
		if (x < 0) {
			PyErr_SetString(PyExc_ValueError,
					"Value out of range");
			return -1;
		}
		*p = x;
		return 0;
	} else {
		PyErr_Format(PyExc_TypeError,
			     "int expected instead of %s instance",
			     v->ob_type->tp_name);
		return -1;
	}
}

#ifdef HAVE_LONG_LONG

/* Same, but handling native long long. */

static int
get_longlong(PyObject *v, PY_LONG_LONG *p)
{
	PY_LONG_LONG x;

	if (PyLong_Check(v)) {
		x = PyLong_AsLongLong(v);
		if (x == (PY_LONG_LONG)-1 && PyErr_Occurred()) {
			if (PyErr_ExceptionMatches(PyExc_OverflowError))
				PyErr_SetString(PyExc_ValueError,
						"Value out of range");
			return -1;
		}
		*p = x;
		return 0;
	} else if (PyInt_Check(v)) {
		x = (PY_LONG_LONG)PyInt_AS_LONG(v);
		*p = x;
		return 0;
	} else {
		PyErr_Format(PyExc_TypeError,
			     "int expected instead of %s instance",
			     v->ob_type->tp_name);
		return -1;
	}
}

/* Same, but handling native unsigned long long. */

static int
get_ulonglong(PyObject *v, unsigned PY_LONG_LONG *p)
{
	if (PyLong_Check(v)) {
		unsigned PY_LONG_LONG x;
		x = PyLong_AsUnsignedLongLong(v);
		if (x == (unsigned PY_LONG_LONG)-1 && PyErr_Occurred()) {
			/* The type is OK (has been checked before),
			   so we convert OverflowError and
			   'TypeError: can't convert negative long to unsigned'
			   into ValueError
			*/
			if (PyErr_ExceptionMatches(PyExc_OverflowError)
			    || PyErr_ExceptionMatches(PyExc_TypeError))
				PyErr_SetString(PyExc_ValueError,
						"Value out of range");
			return -1;
		}
		*p = x;
		return 0;
	} else if (PyInt_Check(v)) {
		long l;
		l = PyInt_AS_LONG(v);
		if (l < 0) {
			PyErr_SetString(PyExc_ValueError,
					"Value out of range");
			return -1;
		}
		*p = (unsigned PY_LONG_LONG)l;
		return 0;
	} else {
		PyErr_Format(PyExc_TypeError,
			     "int expected instead of %s instance",
			     v->ob_type->tp_name);
		return -1;
	}
}

#endif


static PyObject *
d_set(void *ptr, PyObject *value, unsigned size)
{
	double x;

	x = PyFloat_AsDouble(value);
	if (x == -1 && PyErr_Occurred()) {
		PyErr_Format(PyExc_TypeError,
			     " float expected instead of %s instance",
			     value->ob_type->tp_name);
		return NULL;
	}
	*(double *)ptr = x;
	Py_INCREF(value);
	return value;
}

static PyObject *
d_get(void *ptr, unsigned size)
{
	return PyFloat_FromDouble(*(double *)ptr);
}

static PyObject *
f_set(void *ptr, PyObject *value, unsigned size)
{
	float x;

	x = (float)PyFloat_AsDouble(value);
	if (x == -1 && PyErr_Occurred()) {
		PyErr_Format(PyExc_TypeError,
			     " float expected instead of %s instance",
			     value->ob_type->tp_name);
		return NULL;
	}
	*(float *)ptr = x;
	Py_INCREF(value);
	return value;
}

static PyObject *
f_get(void *ptr, unsigned size)
{
	return PyFloat_FromDouble(*(float *)ptr);
}

#ifdef HAVE_LONG_LONG
static PyObject *
Q_set(void *ptr, PyObject *value, unsigned size)
{
	unsigned PY_LONG_LONG x;
	if (get_ulonglong(value, &x) < 0)
		return NULL;
	*(unsigned PY_LONG_LONG *)ptr = x;
	Py_INCREF(value);
	return value;
}

static PyObject *
Q_get(void *ptr, unsigned size)
{
	return PyLong_FromUnsignedLongLong(*(unsigned PY_LONG_LONG *)ptr);
}

static PyObject *
q_set(void *ptr, PyObject *value, unsigned size)
{
	PY_LONG_LONG x;
	if (get_longlong(value, &x) < 0)
		return NULL;
	*(PY_LONG_LONG *)ptr = x;
	Py_INCREF(value);
	return value;
}

static PyObject *
q_get(void *ptr, unsigned size)
{
	return PyLong_FromLongLong(*(PY_LONG_LONG *)ptr);
}
#endif


static PyObject *
i_set(void *ptr, PyObject *value, unsigned size)
{
	long x;
	if (get_long(value, &x) < 0)
		return NULL;
	*(int *)ptr = (int)x;
	Py_INCREF(value);
	return value;
}


static PyObject *
i_get(void *ptr, unsigned size)
{
	return PyInt_FromLong(*(int *)ptr);
}

static PyObject *
I_set(void *ptr, PyObject *value, unsigned size)
{
	unsigned long val;
	if (get_ulong(value, &val) < 0)
		return  NULL;
	*(unsigned int *)ptr = (unsigned int)val;
	Py_INCREF(value);
	return value;
}


static PyObject *
I_get(void *ptr, unsigned size)
{
	return PyLong_FromUnsignedLong(*(unsigned int *)ptr);
}

static PyObject *
l_set(void *ptr, PyObject *value, unsigned size)
{
	long x;
	if (get_long(value, &x) < 0)
		return NULL;
	*(long *)ptr = x;
	Py_INCREF(value);
	return value;
}


static PyObject *
l_get(void *ptr, unsigned size)
{
	return PyInt_FromLong(*(long *)ptr);
}

static PyObject *
L_set(void *ptr, PyObject *value, unsigned size)
{
	unsigned long val;
	if (get_ulong(value, &val) < 0)
		return  NULL;
	*(unsigned long *)ptr = val;
	Py_INCREF(value);
	return value;
}


static PyObject *
L_get(void *ptr, unsigned size)
{
	return PyLong_FromUnsignedLong(*(unsigned long *)ptr);
}

static PyObject *
h_set(void *ptr, PyObject *value, unsigned size)
{
	long val;
	if (get_long(value, &val) < 0)
		return NULL;
	if ((long)(short)val != val) {
		PyErr_SetString(PyExc_ValueError,
			     "Value out of range");
		return NULL;
	}
	*(short *)ptr = (short)val;
	Py_INCREF(value);
	return value;
}


static PyObject *
h_get(void *ptr, unsigned size)
{
	return PyInt_FromLong(*(short *)ptr);
}

static PyObject *
H_set(void *ptr, PyObject *value, unsigned size)
{
	unsigned long val;
	if (get_ulong(value, &val) < 0)
		return NULL;
	if (val > 0xFFFF) {
		PyErr_SetString(PyExc_ValueError,
			     "Value out of range");
		return NULL;
	}
	*(unsigned short *)ptr = (unsigned short)val;
	Py_INCREF(value);
	return value;
}


static PyObject *
H_get(void *ptr, unsigned size)
{
	return PyInt_FromLong(*(unsigned short *)ptr);
}

static PyObject *
b_set(void *ptr, PyObject *value, unsigned size)
{
	long val;
	if (get_long(value, &val) < 0)
		return NULL;
	if ((long)(char)val != val) {
		PyErr_SetString(PyExc_ValueError,
			     "Value out of range");
		return NULL;
	}
	*(char *)ptr = (char)val;
	Py_INCREF(value);
	return value;
}


static PyObject *
b_get(void *ptr, unsigned size)
{
	return PyInt_FromLong(*(char *)ptr);
}

static PyObject *
B_set(void *ptr, PyObject *value, unsigned size)
{
	unsigned long val;
	if (get_ulong(value, &val) < 0)
		return NULL;
	if ((unsigned long)(unsigned char)val != val) {
		PyErr_SetString(PyExc_ValueError,
			     "Value out of range");
		return NULL;
	}
	*(unsigned char *)ptr = (unsigned char)val;
	Py_INCREF(value);
	return value;
}


static PyObject *
B_get(void *ptr, unsigned size)
{
	return PyInt_FromLong(*(unsigned char *)ptr);
}

static PyObject *
c_set(void *ptr, PyObject *value, unsigned size)
{
	if (!PyString_Check(value) || (1 != PyString_Size(value))) {
		PyErr_Format(PyExc_TypeError,
			     "one character string expected");
		return NULL;
	}
	*(char *)ptr = PyString_AS_STRING(value)[0];
	Py_INCREF(value);
	return value;
}


static PyObject *
c_get(void *ptr, unsigned size)
{
	return PyString_FromStringAndSize((char *)ptr, 1);
}

#ifdef HAVE_USABLE_WCHAR_T
/* u - a single unicode character */
static PyObject *
u_set(void *ptr, PyObject *value, unsigned size)
{
	int len;
	wchar_t *p;

	if (PyString_Check(value)) {
		value = PyUnicode_FromObject(value);
		if (!value)
			return NULL;
	} else if (!PyUnicode_Check(value)) {
		PyErr_Format(PyExc_TypeError,
				"unicode string expected instead of %s instance",
				value->ob_type->tp_name);
		return NULL;
	} else
		Py_INCREF(value);

	p = PyUnicode_AsUnicode(value);
	if (!p) {
		Py_DECREF(value);
		return NULL;
	}
	len = PyUnicode_GET_SIZE(value);
	if (len != 1) {
		Py_DECREF(value);
		PyErr_SetString(PyExc_TypeError,
				"one character unicode string expected");
		return NULL;
	}
	*(wchar_t *)ptr = p[0];
	return value;
}


static PyObject *
u_get(void *ptr, unsigned size)
{
	return PyUnicode_FromWideChar((wchar_t *)ptr, 1);
}

/* U - a unicode string */
static PyObject *
U_get(void *ptr, unsigned size)
{
	PyObject *result;
	unsigned int len;

	size /= sizeof(wchar_t); /* we count character units here, not bytes */

	result = PyUnicode_FromWideChar((wchar_t *)ptr, size);
	if (!result)
		return NULL;
	/* We need 'result' to be able to count the characters with wcslen,
	   since ptr may not be NUL terminated.  If the length is smaller (if
	   it was actually NUL terminated, we construct a new one and thorw
	   away the result.
	*/
	/* chop off at the first NUL character, if any. */
	len = wcslen(PyUnicode_AS_UNICODE(result));
	if (len < size) {
		PyObject *ob = PyUnicode_FromWideChar((wchar_t *)ptr, len);
		Py_DECREF(result);
		return ob;
	}
	return result;
}

static PyObject *
U_set(void *ptr, PyObject *value, unsigned length)
{
	unsigned int size;

	if (PyString_Check(value)) {
		value = PyUnicode_FromObject(value);
		if (!value)
			return NULL;
	} else if (!PyUnicode_Check(value)) {
		PyErr_Format(PyExc_TypeError,
				"unicode string expected instead of %s instance",
				value->ob_type->tp_name);
		return NULL;
	} else
		Py_INCREF(value);
	size = PyUnicode_GET_DATA_SIZE(value);
	if (size > length) {
		PyErr_Format(PyExc_ValueError,
			     "too long (%d instead of less than %d)",
			     size, length);
		Py_DECREF(value);
		return NULL;
	} else if (size < length-sizeof(wchar_t))
		/* copy terminating NUL character */
		size += sizeof(wchar_t);
	memcpy((wchar_t *)ptr, PyUnicode_AS_UNICODE(value), size);
	return value;
}

#endif

static PyObject *
s_get(void *ptr, unsigned size)
{
	PyObject *result;

	result = PyString_FromString((char *)ptr);
	if (!result)
		return NULL;
	/* chop off at the first NUL character, if any.
	 * On error, result will be deallocated and set to NULL.
	 */
	size = min(size, strlen(PyString_AS_STRING(result)));
	if (result->ob_refcnt == 1) {
		/* shorten the result */
		_PyString_Resize(&result, size);
		return result;
	} else
		/* cannot shorten the result */
		return PyString_FromStringAndSize(ptr, size);
}

static PyObject *
s_set(void *ptr, PyObject *value, unsigned length)
{
	char *data;
	unsigned size;

	data = PyString_AsString(value);
	if (!data)
		return NULL;
	size = strlen(data);
	if (size < length) {
		/* This will copy the leading NUL character
		 * if there is space for it.
		 */
		++size;
	} else if (size >= length) {
		PyErr_Format(PyExc_ValueError,
			     "string too long (%d instead of less than %d)",
			     size, length);
		return NULL;
	}
	/* Also copy the terminating NUL character */
	memcpy((char *)ptr, data, size);
	Py_INCREF(value);
	return value;
}


/* XXX Seems the S format is no longer used anywhere, remove after 0.6.0 release */
#if 1
static PyObject *
S_get(void *ptr, unsigned length)
{
	return PyString_FromStringAndSize((char *)ptr, length);
}

static PyObject *
S_set(void *ptr, PyObject *value, unsigned length)
{
	char *data;
	unsigned size;

	if (-1 == PyString_AsStringAndSize(value, &data, &size)) {
		return NULL;
	}
	if (size > length) {
		PyErr_Format(PyExc_ValueError,
			     "string too long (%d instead of at most than %d)",
			     size, length);
		return NULL;
	}
	/* No terminating NUL character */
	memcpy((char *)ptr, data, size);
	Py_INCREF(value);
	return value;
}
#endif

static PyObject *
z_set(void *ptr, PyObject *value, unsigned size)
{
	if (value == Py_None) {
		*(char **)ptr = NULL;
		Py_INCREF(value);
		return value;
	}
	if (!PyString_Check(value)) {
		PyErr_Format(PyExc_TypeError,
				"string expected instead of %s instance",
				value->ob_type->tp_name);
		return NULL;
	}
	*(char **)ptr = PyString_AS_STRING(value);
	Py_INCREF(value);
	return value;
}

static PyObject *
z_get(void *ptr, unsigned size)
{
	if (*(void **)ptr)
		return PyString_FromString(*(char **)ptr);
	else {
		Py_INCREF(Py_None);
		return Py_None;
	}
}

#ifdef HAVE_USABLE_WCHAR_T
static PyObject *
Z_set(void *ptr, PyObject *value, unsigned size)
{
	if (value == Py_None) {
		*(wchar_t **)ptr = NULL;
		Py_INCREF(value);
		return value;
	}
	if (PyString_Check(value)) {
		value = PyUnicode_FromObject(value);
		if (!value)
			return NULL;
	} else if (!PyUnicode_Check(value)) {
		PyErr_Format(PyExc_TypeError,
				"unicode string expected instead of %s instance",
				value->ob_type->tp_name);
		return NULL;
	} else
		Py_INCREF(value);
	*(wchar_t **)ptr = PyUnicode_AS_UNICODE(value);
	return value;
}

static PyObject *
Z_get(void *ptr, unsigned size)
{
	wchar_t *p;
	p = *(wchar_t **)ptr;
	if (p)
		return PyUnicode_FromWideChar(p, wcslen(p));
	else {
		Py_INCREF(Py_None);
		return Py_None;
	}
}
#endif

#ifdef MS_WIN32
static PyObject *
BSTR_set(void *ptr, PyObject *value, unsigned size)
{
	BSTR bstr;

	/* convert value into a PyUnicodeObject or NULL */
	if (Py_None == value) {
		value = NULL;
	} else if (PyString_Check(value)) {
		value = PyUnicode_FromObject(value);
		if (!value)
			return NULL;
	} else if (PyUnicode_Check(value)) {
		Py_INCREF(value); /* for the descref below */
	} else {
		PyErr_Format(PyExc_TypeError,
				"unicode string expected instead of %s instance",
				value->ob_type->tp_name);
		return NULL;
	}

	/* create a BSTR from value */
	if (value) {
		bstr = SysAllocStringLen(PyUnicode_AS_UNICODE(value),
					 PyUnicode_GET_SIZE(value));
		Py_DECREF(value);
	} else
		bstr = NULL;

	/* free the previous contents, if any */
	if (*(BSTR *)ptr)
		SysFreeString(*(BSTR *)ptr);
	
	/* and store it */
	*(BSTR *)ptr = bstr;

	/* We don't need to keep any other object */
	Py_INCREF(Py_None);
	return Py_None;
}


static PyObject *
BSTR_get(void *ptr, unsigned size)
{
	BSTR p;
	p = *(BSTR *)ptr;
	if (p)
		return PyUnicode_FromWideChar(p, SysStringLen(p));
	else {
		/* Hm, it seems NULL pointer and zero length string are the
		   same in BSTR, see Don Box, p 81
		*/
		Py_INCREF(Py_None);
		return Py_None;
	}
}
#endif

static PyObject *
P_set(void *ptr, PyObject *value, unsigned size)
{
	void *v;
	if (value == Py_None) {
		*(void **)ptr = NULL;
		Py_INCREF(Py_None);
		return Py_None;
	}
	
	v = PyLong_AsVoidPtr(value);
	if (PyErr_Occurred()) {
		/* prevent the SystemError: bad argument to internal function */
		if (!PyInt_Check(value) && !PyLong_Check(value)) {
			PyErr_SetString(PyExc_TypeError,
					"cannot be converted to pointer");
		}
		return NULL;
	}
	*(void **)ptr = v;
	Py_INCREF(value);
	return value;
}

static PyObject *
P_get(void *ptr, unsigned size)
{
	if (*(void **)ptr == NULL) {
		Py_INCREF(Py_None);
		return Py_None;
	}
	return PyLong_FromVoidPtr(*(void **)ptr);
}

static struct fielddesc formattable[] = {
	{ 's', s_set, s_get, &ffi_type_pointer},
#if 1
/* XXX This one seems unused */
	/* See comment above S_get() */
	{ 'S', S_set, S_get, &ffi_type_schar},
#endif
	{ 'b', b_set, b_get, &ffi_type_schar},
	{ 'B', B_set, B_get, &ffi_type_uchar},
	{ 'c', c_set, c_get, &ffi_type_schar},
	{ 'd', d_set, d_get, &ffi_type_double},
	{ 'f', f_set, f_get, &ffi_type_float},
	{ 'h', h_set, h_get, &ffi_type_sshort},
	{ 'H', H_set, H_get, &ffi_type_ushort},
	{ 'i', i_set, i_get, &ffi_type_sint},
	{ 'I', I_set, I_get, &ffi_type_uint},
/* XXX Hm, sizeof(int) == sizeof(long) doesn't hold on every platform */
/* As soon as we can get rid of the type codes, this is no longer a problem */
	{ 'l', l_set, l_get, &ffi_type_sint},
	{ 'L', L_set, L_get, &ffi_type_uint},
#ifdef HAVE_LONG_LONG
	{ 'q', q_set, q_get, &ffi_type_slong},
	{ 'Q', Q_set, Q_get, &ffi_type_ulong},
#endif
	{ 'P', P_set, P_get, &ffi_type_pointer},
	{ 'z', z_set, z_get, &ffi_type_pointer},
#ifdef HAVE_USABLE_WCHAR_T
/* Correct or not? */
	{ 'u', u_set, u_get, &ffi_type_sshort},
	{ 'U', U_set, U_get, &ffi_type_pointer},
	{ 'Z', Z_set, Z_get, &ffi_type_pointer},
#endif
#ifdef MS_WIN32
	{ 'X', BSTR_set, BSTR_get, &ffi_type_pointer},
#endif
	{ 0, NULL, NULL, NULL},
};

struct fielddesc *
getentry(char *fmt)
{
	struct fielddesc *table = formattable;

	for (; table->code; ++table) {
		if (table->code == fmt[0])
			return table;
	}
	return NULL;
}

/*---------------- EOF ----------------*/
