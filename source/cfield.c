#include "Python.h"
#include "structmember.h"

#include "ctypes.h"

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


static char *var_field_codes = "sS";

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

	self = (CFieldObject *)PyObject_CallObject((PyObject *)&CField_Type,
						   NULL);
	if (self == NULL)
		return NULL;
	if (PyString_Check(desc)) {
		struct fielddesc *fmt;
		char *name = PyString_AS_STRING(desc);
		int fieldsize = 0;
		
		while (isdigit(*name)) {
		        fieldsize = fieldsize * 10 + *name - '0';
			++name;
		}

		if (name[1] != '\0') {
			PyErr_Format(PyExc_ValueError,
				     "format must be single char, not '%s'",
				     name);
			return NULL;
		}

		if (fieldsize && !strchr(var_field_codes, name[0])) {
			PyErr_Format(PyExc_ValueError,
				     "field size not allowed for '%s' format",
				     name);
			return NULL;
		}

		fmt = getentry(name);
		if (!fmt) {
			PyErr_Format(PyExc_ValueError,
				     "invalid format '%s'", name);
			return NULL;
		}
		size = fieldsize ? fieldsize * fmt->size : fmt->size;
		if (pack)
			align = min(pack, fmt->align);
		else
			align = fmt->align;
		setfunc = fmt->setfunc;
		getfunc = fmt->getfunc;
		length = 1;
		proto = NULL;
	} else {
		StgDictObject *dict;
		dict = PyType_stgdict(desc);
		if (!dict) {
			PyErr_SetString(PyExc_TypeError,
					"has no _stginfo_");
			Py_DECREF(self);
			return NULL;
		}
		size = dict->size;
		align = dict->align;
		length = dict->length;
		proto = desc;
#if 0
		/* XXX This is the place where field descriptors like
		   'c_char * n' should be scpecial cased to return a Python
		   string instead of an Array object instance...
		*/
		if (ArrayTypeObject_Check(proto)) {
			StgDictObject *adict = PyType_stgdict(proto);
			StgDictObject *idict;
			if (adict && adict->proto) {
				struct fielddesc *fd;
				idict = PyType_stgdict(adict->proto);
				fd = getentry("c");
				if (idict->getfunc == fd->getfunc) {
					fd = getentry("s");
					getfunc = fd->getfunc;
					setfunc = fd->setfunc;
				}
			}
			
		}
#endif
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
	PyObject *objects;

	if (!CDataObject_Check(inst)) {
		PyErr_SetString(PyExc_TypeError,
				"Not a CData Object");
		return -1;
	}
	dst = (CDataObject *)inst;

	/* Hm.
	 * If self->proto is NULL, we require setfunc to do it's work.
	 *
	 * If self->proto is not NULL, we currently:
	 *
	 * - require that value is a CDataObject.
	 *
	 * - If isinstance(value, self->proto) is true, we simply
	 *   copy the buffer contents of value into dst's buffer
	 *   at the correct offset.
	 *
	 * - If self->proto is a PointerType and value is an Array,
	 *   we require that the value type's stgdict is identical to
	 *   self->proto's stgdict - this means that Array's items
	 *   have the same type as the Pointer's contents. So we can
	 *   copy the Array's buffer address into dst's buffer at the
	 *   correct offset.
	 *   (In C, an array can always (automatically) be cast to a pointer.)
	 *
	 * What would be a nice protocol to replace or extend the above
	 * algorithm?
	 */
	if (self->proto) {
		CDataObject *src = (CDataObject *)value;
		if (!CDataObject_Check(value)) {
			if (CFunctionObject_Check(value)) {
				CFunctionObject *func;
				func = (CFunctionObject *)value;
				assert(self->size == sizeof(void *));
				*(void **)(dst->b_ptr + self->offset) = func->callback;
				Py_INCREF(value); /* reference to keep */
			} else {
				/* Hm. We can arrive here when self->proto is an ArrayType_Type,
				   and value is a sequence. */
				/* Should we call (self->proto).from_param(PySequence_GetItem())? */
				PyErr_SetString(PyExc_TypeError,
						"CDataObject expected");
				return -1;
			}
		} else if (PyObject_IsInstance(value, self->proto)) {
			memcpy(dst->b_ptr + self->offset,
			       src->b_ptr,
			       self->size);
			value = CData_GetList(src);
			Py_INCREF(value); /* reference to keep */
		} else if (PointerTypeObject_Check(self->proto)
			   && ArrayObject_Check(src)) {
			StgDictObject *p1, *p2;

			p1 = PyObject_stgdict(value);
			p2 = PyType_stgdict(self->proto);

			if (p1->proto != p2->proto) {
				PyErr_Format(PyExc_TypeError,
				     "incompatible types, %s instance instead of %s instance",
					     value->ob_type->tp_name,
					     ((PyTypeObject *)self->proto)->tp_name);
				return -1;
			}
			assert(self->size == sizeof(void *));
			*(void **)(dst->b_ptr + self->offset) = src->b_ptr;
			value = CData_GetList(src);
			Py_INCREF(value); /* reference to keep */
		} else {
			PyErr_Format(PyExc_TypeError,
				     "incompatible types, %s instance instead of %s instance",
				     value->ob_type->tp_name,
				     ((PyTypeObject *)self->proto)->tp_name);
			return -1;
		}
	} else {
		value = self->setfunc(dst->b_ptr + self->offset,
				      value, self->size);
		if (!value)
			return -1;
		/* No Py_INCREF(), setfunc already returns a new reference. */
	}
	/* Keep the object alive */
	objects = CData_GetList(dst);
	if (!objects)
		return -1; /* Hm. Severe bug. What now? Undo all the above? */
	return PyList_SetItem(objects, self->index, value);
}

static PyObject *
CField_get(CFieldObject *self, PyObject *inst, PyTypeObject *type)
{
	CDataObject *mem;

	if (inst == NULL) {
		Py_INCREF(self);
		return (PyObject *)self;
	}

	if (!CDataObject_Check(inst)) {
		PyErr_SetString(PyExc_TypeError,
				"Not a CData Object");
		return NULL;
	}
	mem = (CDataObject *)inst;

	/* XXX Do we need to check the size here, or do we trust in 'self'? */
	if (self->proto) {
		/* We should probably special case here if self->proto->ob_type
		   is CFunctionType_Type */
/*
		if (self->proto->ob_type == &CFunctionType_Type)
			....
*/
		return CData_FromBaseObj(self->proto,
					 inst,
					 self->index,
					 self->offset);
	}

	return self->getfunc(mem->b_ptr + self->offset, self->size);
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
get_longlong(PyObject *v, LONG_LONG *p)
{
	LONG_LONG x;

	if (PyLong_Check(v)) {
		x = PyLong_AsLongLong(v);
		if (x == (LONG_LONG)-1 && PyErr_Occurred()) {
			if (PyErr_ExceptionMatches(PyExc_OverflowError))
				PyErr_SetString(PyExc_ValueError,
						"Value out of range");
			return -1;
		}
		*p = x;
		return 0;
	} else if (PyInt_Check(v)) {
		x = (LONG_LONG)PyInt_AS_LONG(v);
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
get_ulonglong(PyObject *v, unsigned LONG_LONG *p)
{
	if (PyLong_Check(v)) {
		unsigned LONG_LONG x;
		x = PyLong_AsUnsignedLongLong(v);
		if (x == (unsigned LONG_LONG)-1 && PyErr_Occurred()) {
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
		*p = (unsigned LONG_LONG)l;
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
	unsigned LONG_LONG x;
	if (get_ulonglong(value, &x) < 0)
		return NULL;
	*(unsigned LONG_LONG *)ptr = x;
	Py_INCREF(value);
	return value;
}

static PyObject *
Q_get(void *ptr, unsigned size)
{
	return PyLong_FromUnsignedLongLong(*(unsigned LONG_LONG *)ptr);
}

static PyObject *
q_set(void *ptr, PyObject *value, unsigned size)
{
	LONG_LONG x;
	if (get_longlong(value, &x) < 0)
		return NULL;
	*(LONG_LONG *)ptr = x;
	Py_INCREF(value);
	return value;
}

static PyObject *
q_get(void *ptr, unsigned size)
{
	return PyLong_FromLongLong(*(LONG_LONG *)ptr);
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

typedef struct { char c; char x; } s_char;
typedef struct { char c; short x; } s_short;
typedef struct { char c; int x; } s_int;
typedef struct { char c; long x; } s_long;
typedef struct { char c; float x; } s_float;
typedef struct { char c; double x; } s_double;
typedef struct { char c; char *x; } s_char_p;
typedef struct { char c; void *x; } s_void_p;

#define CHAR_ALIGN (sizeof(s_char) - sizeof(char))
#define SHORT_ALIGN (sizeof(s_short) - sizeof(short))
#define INT_ALIGN (sizeof(s_int) - sizeof(int))
#define LONG_ALIGN (sizeof(s_long) - sizeof(long))
#define FLOAT_ALIGN (sizeof(s_float) - sizeof(float))
#define DOUBLE_ALIGN (sizeof(s_double) - sizeof(double))
#define CHAR_P_ALIGN (sizeof(s_char_p) - sizeof(char*))
#define VOID_P_ALIGN (sizeof(s_void_p) - sizeof(void*))

#ifdef HAVE_USABLE_WCHAR_T
typedef struct { char c; wchar_t x; } s_wchar;
typedef struct { char c; wchar_t *x; } s_wchar_p;

#define WCHAR_ALIGN (sizeof(s_wchar) - sizeof(wchar_t))
#define WCHAR_P_ALIGN (sizeof(s_wchar_p) - sizeof(wchar_t*))
#endif

#ifdef HAVE_LONG_LONG
typedef struct { char c; LONG_LONG x; } s_long_long;
#define LONG_LONG_ALIGN (sizeof(s_long_long) - sizeof(LONG_LONG))
#endif


static struct fielddesc formattable[] = {
	{ 's', sizeof(char),		CHAR_ALIGN,		s_set, s_get},
	{ 'S', sizeof(char),		CHAR_ALIGN,		S_set, S_get},
	{ 'B', sizeof(char),		CHAR_ALIGN,		B_set, B_get},
	{ 'b', sizeof(char),		CHAR_ALIGN,		b_set, b_get},
	{ 'c', sizeof(char),		CHAR_ALIGN,		c_set, c_get},
	{ 'd', sizeof(double),		DOUBLE_ALIGN,		d_set, d_get},
	{ 'f', sizeof(float),		FLOAT_ALIGN,		f_set, f_get},
	{ 'h', sizeof(short),		SHORT_ALIGN,		h_set, h_get},
	{ 'H', sizeof(short),		SHORT_ALIGN,		H_set, H_get},
	{ 'i', sizeof(int),		INT_ALIGN,		i_set, i_get},
	{ 'I', sizeof(int),		INT_ALIGN,		I_set, I_get},
	{ 'l', sizeof(long),		LONG_ALIGN,		l_set, l_get},
	{ 'L', sizeof(long),		LONG_ALIGN,		L_set, L_get},
#ifdef HAVE_LONG_LONG
	{ 'q', sizeof(LONG_LONG),	LONG_LONG_ALIGN,	q_set, q_get},
	{ 'Q', sizeof(LONG_LONG),	LONG_LONG_ALIGN,	Q_set, Q_get},
#endif
	{ 'P', sizeof(void *),		VOID_P_ALIGN,		P_set, P_get},
	{ 'z', sizeof(char *),		CHAR_P_ALIGN,		z_set, z_get},
#ifdef HAVE_USABLE_WCHAR_T
/*	{ 'u', sizeof(wchar_t),		WCHAR_ALIGN,		u_set, u_get}, */
	{ 'Z', sizeof(wchar_t *),	WCHAR_P_ALIGN,		Z_set, Z_get},
#endif
	{ 0,   0,			0,			NULL,  NULL},
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
