/*  
    The most important internal functions:
    ======================================

    PyObject *SETFUNC(void *ptr, PyObject *value, unsigned size, PyObject *type);
    
    'type' is a ctypes type - it has an stgdict.

    SETFUNC checks if value is 'compatible' with 'type', then stores 'value'
    into the memory block pointed to by 'ptr'. The interpretation of 'size'
    depends on the type: for array types it means the length of the array
    (could that also be accessed via the storage dict?), for integer types it
    may specify bit offset and size (in structure fields).

    Returns a Python object which must be kept alive to keep the memory block
    contents valid.

    -----

    PyObject *GETFUNC(void *ptr, unsigned size, PyObject *type, CDataObject *base, int index);
  
    Construct an instance of 'type' from the memory block 'ptr'.  'size' has
    the same meaning as in SETFUNC, if 'base' is non-NULL, the resulting
    instance uses the memory of 'base'. 'index' is used to specify which
    objects from 'base' must be kept alive.

    -----

    int ASPARAM(CDataObject *self, struct argument *pa);

    ASPARAM knows how a ctypes instance is used as parameter in a function
    call.

 */

/*
  xyz_asparam(CDataObject *self, struct argument *pa)
  
  Instance method.

  Copies the contents of self's buffer into pa's buffer,
  keeps self alive in pa->keep, sets ps'a ffi_type.
*/

/*
  xyz_from_param(PyObject *type, PyObject *value)

  Class method (instance method on the metatype to be exact).

  Adapts 'value' to the ctypes 'type', and returns something that can be used
  as a function call argument.  Should probably create a new CArgObject, the
  use the type's setfunc to store value in it.
*/

/*
  ToDo:

  Get rid of the checker (and also the converters) field in CFuncPtrObject and
  StgDictObject, and replace them by slot functions in StgDictObject.

  think about a buffer-like object (memory? bytes?)

  Should POINTER(c_char) and POINTER(c_wchar) have a .value property?
  What about c_char and c_wchar arrays then?

  Add from_mmap, from_file, from_string metaclass methods.

  Maybe we can get away with from_file (calls read) and with a from_buffer
  method?

  And what about the to_mmap, to_file, to_str(?) methods?  They would clobber
  the namespace, probably. So, functions instead? And we already have memmove...
*/

/*

Name			methods, members, getsets
==============================================================================

StructType_Type		__new__(), from_address(), __mul__(), from_param()
UnionType_Type		__new__(), from_address(), __mul__(), from_param()
PointerType_Type	__new__(), from_address(), __mul__(), from_param(), set_type()
ArrayType_Type		__new__(), from_address(), __mul__(), from_param()
SimpleType_Type		__new__(), from_address(), __mul__(), from_param()

CData_Type
  Struct_Type		__new__(), __init__()
  Pointer_Type		__new__(), __init__(), contents
  Array_Type		__new__(), __init__(), __get/setitem__(), __len__()
  Simple_Type		__new__(), __init__()

CField_Type
StgDict_Type

==============================================================================

class methods
-------------

It has some similarity to the byref() construct compared to pointer()
from_address(addr)
	- construct an instance from a given memory block (sharing this memory block)

from_param(obj)
	- typecheck and convert a Python object into a C function call parameter
	  the result may be an instance of the type, or an integer or tuple
	  (typecode, value[, obj])

instance methods/properties
---------------------------

functions
---------

sizeof(cdata)
	- return the number of bytes the buffer contains

sizeof(ctype)
	- return the number of bytes the buffer of an instance would contain

byref(cdata)

addressof(cdata)

pointer(cdata)

POINTER(ctype)

bytes(cdata)
	- return the buffer contents as a sequence of bytes (which is currently a string)

*/

/*
 * StgDict_Type
 * StructType_Type
 * UnionType_Type
 * PointerType_Type
 * ArrayType_Type
 * SimpleType_Type
 *
 * CData_Type
 * Struct_Type
 * Union_Type
 * Array_Type
 * Simple_Type
 * Pointer_Type
 * CField_Type
 *
 */

#include "Python.h"
#include "structmember.h"

#include <ffi.h>
#include "ctypes.h"

#ifdef MS_WIN32
#include <windows.h>
#else
#include <dlfcn.h>
#endif

PyObject *PyExc_ArgError;
static PyTypeObject Simple_Type;

char *conversion_mode_encoding = NULL;
char *conversion_mode_errors = NULL;

static PyObject *CData_AtAddress(PyObject *type, void *buf);

/* Some simple types */
PyObject *CTYPE_c_char_p, *CTYPE_c_char, *CTYPE_c_wchar, *CTYPE_c_wchar_p, *CTYPE_c_void_p, *CTYPE_BSTR;

static PyObject *
generic_getfunc(void *ptr, unsigned size,
		PyObject *type, CDataObject *src, int index)
{
	if (type == NULL) {
		PyErr_SetString(PyExc_SystemError,
				"ctypes bug: generic_getfunc called with NULL type");
		return NULL;
	}
	return CData_FromBaseObj(type, (PyObject *)src, 0, ptr);
}


/******************************************************************/
/*
  StructType_Type - a meta type/class.  Creating a new class using this one as
  __metaclass__ will call the contructor StructUnionType_new.  It replaces the
  tp_dict member with a new instance of StgDict, and initializes the C
  accessible fields somehow.
*/

static PyObject *
basic_setfunc(void *ptr, PyObject *value, unsigned size, PyObject *type)
{
	/* This should be common to ALL types... */
	if (PyObject_IsInstance(value, type)) {
		CDataObject *src = (CDataObject *)value;
		memmove(ptr,
			src->b_ptr,
			size);
		value = GetKeepedObjects(src);
		Py_INCREF(value);
		return value;
	}
	PyErr_Format(PyExc_TypeError,
		     "Incompatible types %s instance instead of %s instance",
		     value->ob_type->tp_name,
		     ((PyTypeObject *)type)->tp_name);
	return NULL;
}

/* derived from cfield.c::_generic_field_setfunc */
static PyObject *
StructUnion_setfunc(void *ptr, PyObject *value, unsigned size, PyObject *type)
{
	/* This only for structures and arrays...*/
	if (PyTuple_Check(value)) {
		/* If value is a tuple, we call the type with the tuple
		   and use the result */
		PyObject *ob;
		PyObject *result;
		ob = PyObject_CallObject(type, value);
		if (ob == NULL) {
			Extend_Error_Info(PyExc_RuntimeError, "(%s) ",
					  ((PyTypeObject *)type)->tp_name);
			return NULL;
		}
		result = StructUnion_setfunc(ptr, ob, size, type);
		Py_DECREF(ob);
		return result;
	}
	return basic_setfunc(ptr, value, size, type);
}

static int
StructUnion_asparam(CDataObject *self, struct argument *pa)
{
	StgDictObject *dict = PyObject_stgdict((PyObject *)self);
	pa->ffi_type = &dict->ffi_type;
	pa->value.p = self->b_ptr;
	Py_INCREF(self);
	pa->keep = (PyObject *)self;
	return 0;
}

static PyObject *
StructUnionType_new(PyTypeObject *type, PyObject *args, PyObject *kwds, int isStruct)
{
	PyTypeObject *result;
	PyObject *fields;
	StgDictObject *dict;

	/* create the new instance (which is a class,
	   since we are a metatype!) */
	result = (PyTypeObject *)PyType_Type.tp_new(type, args, kwds);
	if (!result)
		return NULL;

	/* keep this for bw compatibility */
	if (PyDict_GetItemString(result->tp_dict, "_abstract_"))
		return (PyObject *)result;

	dict = (StgDictObject *)PyObject_CallObject((PyObject *)&StgDict_Type, NULL);
	if (!dict) {
		Py_DECREF(result); /*COV*/
		return NULL; /*COV*/
	}
	/* replace the class dict by our updated stgdict, which holds info
	   about storage requirements of the instances */
	if (-1 == PyDict_Update((PyObject *)dict, result->tp_dict)) {
		Py_DECREF(result); /*COV*/
		Py_DECREF((PyObject *)dict); /*COV*/
		return NULL; /*COV*/
	}
	Py_DECREF(result->tp_dict);
	result->tp_dict = (PyObject *)dict;

	dict->setfunc = StructUnion_setfunc;
	dict->getfunc = generic_getfunc;
	dict->asparam = StructUnion_asparam;

	fields = PyDict_GetItemString((PyObject *)dict, "_fields_");
	if (!fields) {
		StgDictObject *basedict = PyType_stgdict((PyObject *)result->tp_base);

		if (basedict == NULL)
			return (PyObject *)result;
		/* copy base dict */
		if (-1 == StgDict_clone(dict, basedict)) {
			Py_DECREF(result); /*COV*/
			return NULL; /*COV*/
		}
		dict->flags &= ~DICTFLAG_FINAL; /* clear the 'final' flag in the subclass dict */
		basedict->flags |= DICTFLAG_FINAL; /* set the 'final' flag in the baseclass dict */
		return (PyObject *)result;
	}

	if (-1 == PyObject_SetAttrString((PyObject *)result, "_fields_", fields)) {
		Py_DECREF(result);
		return NULL;
	}

	return (PyObject *)result;
}

static PyObject *
StructType_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	return StructUnionType_new(type, args, kwds, 1);
}

static PyObject *
UnionType_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	return StructUnionType_new(type, args, kwds, 0);
}

static char from_address_doc[] =
"C.from_address(integer) -> C instance\naccess a C instance at the specified address";

static PyObject *
CDataType_from_address(PyObject *type, PyObject *value)
{
	void *buf;
	if (!PyInt_Check(value)) {
		PyErr_SetString(PyExc_TypeError,
				"integer expected");
		return NULL;
	}
	buf = (void *)PyInt_AS_LONG(value);
	return CData_AtAddress(type, buf);
}

static char in_dll_doc[] =
"C.in_dll(dll, name) -> C instance\naccess a C instance in a dll";

static PyObject *
CDataType_in_dll(PyObject *type, PyObject *args)
{
	PyObject *dll;
	char *name;
	PyObject *obj;
	void *handle;
	void *address;

	if (!PyArg_ParseTuple(args, "Os", &dll, &name))
		return NULL;

	obj = PyObject_GetAttrString(dll, "_handle");
	if (!obj)
		return NULL;
	if (!PyInt_Check(obj)) {
		PyErr_SetString(PyExc_TypeError,
				"the _handle attribute must be an integer");
		Py_DECREF(obj);
		return NULL;
	}
	handle = (void *)PyInt_AS_LONG(obj);
	Py_DECREF(obj);

#ifdef MS_WIN32
	address = (void *)GetProcAddress(handle, name);
	if (!address) {
		PyErr_Format(PyExc_ValueError,
			     "symbol '%s' not found",
			     name);
		return NULL;
	}
#else
	address = (void *)dlsym(handle, name);
	if (!address) {
		PyErr_Format(PyExc_ValueError,
#ifdef __CYGWIN__
/* dlerror() isn't very helpful on cygwin */
			     "symbol '%s' not found (%s) ",
			     name,
#endif
			     dlerror());
		return NULL;
	}
#endif
	return CData_AtAddress(type, address);
}

static char from_param_doc[] =
"Convert a Python object into a function call parameter.";

/* Used for Array, Structure, Union, CFuncPtr */
static PyObject *
CDataType_from_param(PyObject *type, PyObject *value)
{
	if (1 == PyObject_IsInstance(value, type)) {
		Py_INCREF(value);
		return value;
	}
	if (PyCArg_CheckExact(value)) {
		PyCArgObject *p = (PyCArgObject *)value;
		StgDictObject *dict = PyType_stgdict(type);

		/* If we got a PyCArgObject, we must check if the object packed in it
		   is an instance of the type's dict->proto */
		if(PyObject_IsInstance(p->obj, dict->itemtype)) {
			Py_INCREF(value);
			return value;
		}
		PyErr_Format(PyExc_TypeError,
			     "expected %s instance instead of pointer to %s",
			     ((PyTypeObject *)type)->tp_name,
			     p->obj->ob_type->tp_name);
		return NULL;
	}
	PyErr_Format(PyExc_TypeError,
		     "expected %s instance instead of %s",
		     ((PyTypeObject *)type)->tp_name,
		     value->ob_type->tp_name);
	return NULL;
}

static PyMethodDef CDataType_methods[] = {
	{ "from_param", CDataType_from_param, METH_O, from_param_doc },
	{ "from_address", CDataType_from_address, METH_O, from_address_doc },
	{ "in_dll", CDataType_in_dll, METH_VARARGS, in_dll_doc },
	{ NULL, NULL },
};

static PyObject *
CDataType_repeat(PyObject *self, int length)
{
	return CreateArrayType(self, length);
}

static PySequenceMethods CDataType_as_sequence = {
	0,			/* inquiry sq_length; */
	0,			/* binaryfunc sq_concat; */
	CDataType_repeat,	/* intargfunc sq_repeat; */
	0,			/* intargfunc sq_item; */
	0,			/* intintargfunc sq_slice; */
	0,			/* intobjargproc sq_ass_item; */
	0,			/* intintobjargproc sq_ass_slice; */
	0,			/* objobjproc sq_contains; */
	
	0,			/* binaryfunc sq_inplace_concat; */
	0,			/* intargfunc sq_inplace_repeat; */
};

static int
CDataType_clear(PyTypeObject *self)
{
	StgDictObject *dict = PyType_stgdict((PyObject *)self);
	if (dict)
		Py_CLEAR(dict->itemtype);
	return PyType_Type.tp_clear((PyObject *)self);
}

static int
CDataType_traverse(PyTypeObject *self, visitproc visit, void *arg)
{
	StgDictObject *dict = PyType_stgdict((PyObject *)self);
	if (dict)
		Py_VISIT(dict->itemtype);
	return PyType_Type.tp_traverse((PyObject *)self, visit, arg);
}

static int
StructType_setattro(PyObject *self, PyObject *key, PyObject *value)
{
	/* XXX Should we disallow deleting _fields_? */
	if (-1 == PyObject_GenericSetAttr(self, key, value))
		return -1;
	
	if (value && PyString_Check(key) &&
	    0 == strcmp(PyString_AS_STRING(key), "_fields_"))
		return StructUnionType_update_stgdict(self, value, 1);
	return 0;
}


static int
UnionType_setattro(PyObject *self, PyObject *key, PyObject *value)
{
	/* XXX Should we disallow deleting _fields_? */
	if (-1 == PyObject_GenericSetAttr(self, key, value))
		return -1;
	
	if (PyString_Check(key) &&
	    0 == strcmp(PyString_AS_STRING(key), "_fields_"))
		return StructUnionType_update_stgdict(self, value, 0);
	return 0;
}


PyTypeObject StructType_Type = {
	PyObject_HEAD_INIT(NULL)
	0,					/* ob_size */
	"_ctypes.StructType",			/* tp_name */
	0,					/* tp_basicsize */
	0,					/* tp_itemsize */
	0,					/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	0,					/* tp_compare */
	0,			       		/* tp_repr */
	0,					/* tp_as_number */
	&CDataType_as_sequence,			/* tp_as_sequence */
	0,					/* tp_as_mapping */
	0,					/* tp_hash */
	0,					/* tp_call */
	0,					/* tp_str */
	0,					/* tp_getattro */
	StructType_setattro,			/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC, /* tp_flags */
	"metatype for the CData Objects",	/* tp_doc */
	(traverseproc)CDataType_traverse,	/* tp_traverse */
	(inquiry)CDataType_clear,		/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,					/* tp_iter */
	0,					/* tp_iternext */
	CDataType_methods,			/* tp_methods */
	0,					/* tp_members */
	0,					/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	0,					/* tp_init */
	0,					/* tp_alloc */
	StructType_new,				/* tp_new */
	0,					/* tp_free */
};

static PyTypeObject UnionType_Type = {
	PyObject_HEAD_INIT(NULL)
	0,					/* ob_size */
	"_ctypes.UnionType",			/* tp_name */
	0,					/* tp_basicsize */
	0,					/* tp_itemsize */
	0,					/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	0,					/* tp_compare */
	0,			       		/* tp_repr */
	0,					/* tp_as_number */
	&CDataType_as_sequence,		/* tp_as_sequence */
	0,					/* tp_as_mapping */
	0,					/* tp_hash */
	0,					/* tp_call */
	0,					/* tp_str */
	0,					/* tp_getattro */
	UnionType_setattro,			/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC, /* tp_flags */
	"metatype for the CData Objects",	/* tp_doc */
	(traverseproc)CDataType_traverse,	/* tp_traverse */
	(inquiry)CDataType_clear,		/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,					/* tp_iter */
	0,					/* tp_iternext */
	CDataType_methods,			/* tp_methods */
	0,					/* tp_members */
	0,					/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	0,					/* tp_init */
	0,					/* tp_alloc */
	UnionType_new,				/* tp_new */
	0,					/* tp_free */
};


/******************************************************************/

/*

The PointerType_Type metaclass must ensure that the subclass of Pointer can be
created. It must check for a _type_ attribute in the class. Since are no
runtime created properties, a CField is probably *not* needed ?

class IntPointer(Pointer):
    _type_ = "i"

The Pointer_Type provides the functionality: a contents method/property, a
size property/method, and the sequence protocol.

*/

static int
PointerType_SetProto(StgDictObject *stgdict, PyObject *proto)
{
	if (proto && !PyType_Check(proto)) {
		PyErr_SetString(PyExc_TypeError,
				"_type_ must be a type");
		return -1;
	}
	if (proto && !PyType_stgdict(proto)) {
		PyErr_SetString(PyExc_TypeError,
				"_type_ must have storage info");
		return -1;
	}
	Py_INCREF(proto);
	Py_XDECREF(stgdict->itemtype);
	stgdict->itemtype = proto;
	return 0;
}

static PyObject *
Pointer_setfunc(void *ptr, PyObject *value, unsigned size, PyObject *type)
{
	StgDictObject *dict;

	if (value == Py_None) {
		*(void **)ptr = NULL;
		Py_INCREF(Py_None);
		return Py_None;
	}
	dict = PyObject_stgdict(value);
	if (dict
	    && ArrayObject_Check(value)
	    /* Should we accept subclasses here? */
	    && dict->itemtype == PyType_stgdict(type)->itemtype) {
		*(void **)ptr = ((CDataObject *)value)->b_ptr;
		/* We need to keep the array alive, not just the arrays b_objects. */
		Py_INCREF(value);
		return value;
	}
	return basic_setfunc(ptr, value, size, type);
}

static int
Pointer_asparam(CDataObject *self, struct argument *pa)
{
	pa->ffi_type = &ffi_type_pointer;
	pa->value.p = *(void **)self->b_ptr;
	Py_INCREF(self);
	pa->keep = (PyObject *)self;
	return 0;
}

static PyObject *
PointerType_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	PyTypeObject *result;
	StgDictObject *stgdict;
	PyObject *proto;
	PyObject *typedict;

	typedict = PyTuple_GetItem(args, 2);
	if (!typedict)
		return NULL;
/*
  stgdict items size, align, length contain info about pointers itself,
  stgdict->proto has info about the pointed to type!
*/
	stgdict = (StgDictObject *)PyObject_CallObject(
		(PyObject *)&StgDict_Type, NULL);
	if (!stgdict)
		return NULL;
	stgdict->size = sizeof(void *);
	stgdict->align = getentry("P")->pffi_type->alignment;
	stgdict->length = 2;
	stgdict->ffi_type = ffi_type_pointer;

	proto = PyDict_GetItemString(typedict, "_type_"); /* Borrowed ref */
	if (proto && -1 == PointerType_SetProto(stgdict, proto)) {
		Py_DECREF((PyObject *)stgdict);
		return NULL;
	}

	/* create the new instance (which is a class,
	   since we are a metatype!) */
	result = (PyTypeObject *)PyType_Type.tp_new(type, args, kwds);
	if (result == NULL)
		return NULL;

	/* replace the class dict by our updated spam dict */
	if (-1 == PyDict_Update((PyObject *)stgdict, result->tp_dict)) {
		Py_DECREF(result);
		Py_DECREF((PyObject *)stgdict);
		return NULL;
	}
	Py_DECREF(result->tp_dict);
	result->tp_dict = (PyObject *)stgdict;

	stgdict->getfunc = generic_getfunc;
	stgdict->setfunc = Pointer_setfunc;
	stgdict->asparam = Pointer_asparam;

	return (PyObject *)result;
}


static PyObject *
PointerType_set_type(PyTypeObject *self, PyObject *type)
{
	StgDictObject *dict;

	dict = PyType_stgdict((PyObject *)self);
	assert(dict);

	if (-1 == PointerType_SetProto(dict, type))
		return NULL;

	if (-1 == PyDict_SetItemString((PyObject *)dict, "_type_", type))
		return NULL;

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *
PointerType_from_param(PyObject *type, PyObject *value)
{
	if (value == Py_None) {
		Py_INCREF(Py_None);
		return Py_None;
	}
	if (ArrayObject_Check(value) || PointerObject_Check(value)) {
		StgDictObject *v = PyObject_stgdict(value);
		StgDictObject *t = PyType_stgdict(type);
		if (PyObject_IsSubclass(v->itemtype, t->itemtype)) {
			Py_INCREF(value);
			return value;
		}
	}
     	return CDataType_from_param(type, value);
}

static PyMethodDef PointerType_methods[] = {
	{ "from_address", CDataType_from_address, METH_O, from_address_doc },
	{ "in_dll", CDataType_in_dll, METH_VARARGS, in_dll_doc},
	{ "from_param", (PyCFunction)PointerType_from_param, METH_O, from_param_doc},
	{ "set_type", (PyCFunction)PointerType_set_type, METH_O },
	{ NULL, NULL },
};

PyTypeObject PointerType_Type = {
	PyObject_HEAD_INIT(NULL)
	0,					/* ob_size */
	"_ctypes.PointerType",				/* tp_name */
	0,					/* tp_basicsize */
	0,					/* tp_itemsize */
	0,					/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	0,					/* tp_compare */
	0,			       		/* tp_repr */
	0,					/* tp_as_number */
	&CDataType_as_sequence,		/* tp_as_sequence */
	0,					/* tp_as_mapping */
	0,					/* tp_hash */
	0,					/* tp_call */
	0,					/* tp_str */
	0,					/* tp_getattro */
	0,					/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC, /* tp_flags */
	"metatype for the Pointer Objects",	/* tp_doc */
	(traverseproc)CDataType_traverse,	/* tp_traverse */
	(inquiry)CDataType_clear,		/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,					/* tp_iter */
	0,					/* tp_iternext */
	PointerType_methods,			/* tp_methods */
	0,					/* tp_members */
	0,					/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	0,					/* tp_init */
	0,					/* tp_alloc */
	PointerType_new,			/* tp_new */
	0,					/* tp_free */
};


/******************************************************************/
/*
  CharArray helper functions
*/
static int
CharArray_set_raw(CDataObject *self, PyObject *value)
{
	char *ptr;
	int size;
	if (PyBuffer_Check(value)) {
		size = value->ob_type->tp_as_buffer->bf_getreadbuffer(value, 0, (void *)&ptr);
		if (size < 0)
			return -1;
	} else if (-1 == PyString_AsStringAndSize(value, &ptr, &size)) {
		return -1;
	}
	if (size > self->b_size) {
		PyErr_SetString(PyExc_ValueError,
				"string too long");
		return -1;
	}

	memcpy(self->b_ptr, ptr, size);

	return 0;
}

static PyObject *
CharArray_get_raw(CDataObject *self)
{
	return PyString_FromStringAndSize(self->b_ptr, self->b_size);
}

static PyObject *
CharArray_get_value(CDataObject *self)
{
	int i;
	char *ptr = self->b_ptr;
	for (i = 0; i < self->b_size; ++i)
		if (*ptr++ == '\0')
			break;
	return PyString_FromStringAndSize(self->b_ptr, i);
}

/* Returns number of characters copied.  -1 on error, -2 when value is not a
   string or unicode object.
*/
static int
Store_EncodedString(char *ptr, PyObject *value, unsigned size)
{
	unsigned len;
	if (PyUnicode_Check(value)) {
		value = PyUnicode_AsEncodedString(value,
						  conversion_mode_encoding,
						  conversion_mode_errors);
		if (value == NULL)
			return -1;
	} else if (PyString_Check(value)) {
		Py_INCREF(value);
	} else
		return -2;
	len = PyString_GET_SIZE(value);
	if (len < size)
		++len; /* We'll copy the terminating NUL if there is space */
	else if (len > size) {
		Py_DECREF(value);
		PyErr_Format(PyExc_ValueError,
			     "string too long (%d, maximum length %d)",
			     size, len);
		return -1;
	}
	memcpy(ptr, PyString_AS_STRING(value), len);
	Py_DECREF(value);
	return len;
}

static int
CharArray_set_value(CDataObject *self, PyObject *value)
{
	int result = Store_EncodedString(self->b_ptr,
					 value,
					 self->b_size);
	if (result == -1)
		return -1;
	if (result == -2) {
		PyErr_Format(PyExc_TypeError,
			     "string expected instead of %s instance",
			     value->ob_type->tp_name);
		return -1;
	}
	return 0;
}

static PyObject *
CharArray_setfunc(void *ptr, PyObject *value, unsigned size, PyObject *type)
{
	int result = Store_EncodedString(ptr, value, size);
	if (result == -1)
		return NULL;
	if (result == -2) {
		return StructUnion_setfunc(ptr, value, size, type);
	}
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *
CharArray_getfunc(void *ptr, unsigned size,
		  PyObject *type, CDataObject *src, int index)
{
	unsigned i;
	for (i = 0; i < size; ++i)
		if (((char *)ptr)[i] == '\0')
			break;
	return PyString_FromStringAndSize(ptr, i);
}

static PyGetSetDef CharArray_getsets[] = {
	{ "raw", (getter)CharArray_get_raw, (setter)CharArray_set_raw,
	  "value", NULL },
	{ "value", (getter)CharArray_get_value, (setter)CharArray_set_value,
	  "string value"},
	{ NULL, NULL }
};

/******************************************************************/
/*
  WCharArray helper functions
*/

#ifdef CTYPES_UNICODE
static PyObject *
WCharArray_get_value(CDataObject *self)
{
	unsigned int i;
	wchar_t *ptr = (wchar_t *)self->b_ptr;
	for (i = 0; i < self->b_size/sizeof(wchar_t); ++i)
		if (*ptr++ == (wchar_t)0)
			break;
	return PyUnicode_FromWideChar((wchar_t *)self->b_ptr, i);
}

static int
WCharArray_set_value(CDataObject *self, PyObject *value)
{
	int result = 0;

	if (PyString_Check(value)) {
		value = PyUnicode_FromEncodedObject(value,
						    conversion_mode_encoding,
						    conversion_mode_errors);
		if (!value)
			return -1;
	} else if (!PyUnicode_Check(value)) {
		PyErr_Format(PyExc_TypeError,
				"unicode string expected instead of %s instance",
				value->ob_type->tp_name);
		return -1;
	} else
		Py_INCREF(value);
	if ((unsigned)PyUnicode_GET_SIZE(value) > self->b_size/sizeof(wchar_t)) {
		PyErr_SetString(PyExc_ValueError,
				"string too long");
		result = -1;
		goto done;
	}
	result = PyUnicode_AsWideChar((PyUnicodeObject *)value,
				      (wchar_t *)self->b_ptr,
				      self->b_size/sizeof(wchar_t));
	if (result >= 0 && (unsigned)result < self->b_size/sizeof(wchar_t))
		((wchar_t *)self->b_ptr)[result] = (wchar_t)0;
	if (result > 0)
		result = 0;
  done:
	Py_DECREF(value);

	return result;
}

/* merge code with WCharArray_set_value */
static PyObject *
WCharArray_setfunc(void *ptr, PyObject *value, unsigned size, PyObject *type)
{
	if (PyString_Check(value)) {
		value = PyUnicode_FromEncodedObject(value,
						    conversion_mode_encoding,
						    conversion_mode_errors);
		if (value == NULL)
			return NULL;
	} else
		Py_INCREF(value);
	if (PyUnicode_Check(value)) {
		unsigned len = (unsigned)PyUnicode_GET_SIZE(value);
		if (len > size/sizeof(wchar_t)) {
			PyErr_SetString(PyExc_ValueError,
					"string too long");
			Py_DECREF(value);
			return NULL;
		}
		len = PyUnicode_AsWideChar((PyUnicodeObject *)value,
					   (wchar_t *)ptr,
					   size/sizeof(wchar_t));
		Py_DECREF(value);
		if (len < 0)
			return NULL;
		if (len < size/sizeof(wchar_t))
			((wchar_t *)ptr)[len] = (wchar_t)0;
		Py_INCREF(Py_None);
		return Py_None;
	}
	return StructUnion_setfunc(ptr, value, size, type);
}

static PyGetSetDef WCharArray_getsets[] = {
	{ "value", (getter)WCharArray_get_value, (setter)WCharArray_set_value,
	  "string value"},
	{ NULL, NULL }
};
#endif

#ifdef CTYPES_UNICODE
static PyObject *
WCharArray_getfunc(void *ptr, unsigned size,
		   PyObject *type, CDataObject *src, int index)
{
	unsigned int i;
	for (i = 0; i < size/sizeof(wchar_t); ++i)
		if (((wchar_t *)ptr)[i] == (wchar_t)0)
			break;
	return PyUnicode_FromWideChar((wchar_t *)ptr, i);
}
#endif

/******************************************************************/
/*
  ArrayType_Type
*/
/*
  ArrayType_new ensures that the new Array subclass created has a _length_
  attribute, and a _type_ attribute.
*/


/*
  Copied from Python's typeobject.c.
 */
static int
add_getset(PyTypeObject *type, PyGetSetDef *gsp)
{
	PyObject *dict = type->tp_dict;
	for (; gsp->name != NULL; gsp++) {
		PyObject *descr;
		descr = PyDescr_NewGetSet(type, gsp);
		if (descr == NULL)
			return -1;
		if (PyDict_SetItemString(dict, gsp->name, descr) < 0)
			return -1;
		Py_DECREF(descr);
	}
	return 0;
}

static int
Array_asparam(CDataObject *self, struct argument *pa)
{
	pa->ffi_type = &ffi_type_pointer;
	pa->value.p = self->b_ptr;
	Py_INCREF(self);
	pa->keep = (PyObject *)self;
	return 0;
}

static PyObject *
ArrayType_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	PyTypeObject *result;
	StgDictObject *stgdict;
	StgDictObject *itemdict;
	PyObject *proto;
	PyObject *typedict;
	int length;

	int itemsize, itemalign, itemlen;

	typedict = PyTuple_GetItem(args, 2);
	if (!typedict)
		return NULL;

	proto = PyDict_GetItemString(typedict, "_length_"); /* Borrowed ref */
	if (!proto || !PyInt_Check(proto)) {
		PyErr_SetString(PyExc_AttributeError,
				"class must define a '_length_' attribute, "
				"which must be a positive integer");
		return NULL;
	}
	length = PyInt_AS_LONG(proto);

	proto = PyDict_GetItemString(typedict, "_type_"); /* Borrowed ref */
	if (!proto) {
		PyErr_SetString(PyExc_AttributeError,
				"class must define a '_type_' attribute");
		return NULL;
	}

	stgdict = (StgDictObject *)PyObject_CallObject(
		(PyObject *)&StgDict_Type, NULL);
	if (!stgdict)
		return NULL;

	itemdict = PyType_stgdict(proto);
	if (!itemdict) {
		PyErr_SetString(PyExc_TypeError,
				"_type_ must have storage info");
		Py_DECREF((PyObject *)stgdict);
		return NULL;
	}

	itemsize = itemdict->size;
	itemalign = itemdict->align;
	itemlen = itemdict->length;

	stgdict->size = itemsize * length;
	stgdict->align = itemalign;
	stgdict->length = length;
	Py_INCREF(proto);
	stgdict->itemtype = proto;

	/* create the new instance (which is a class,
	   since we are a metatype!) */
	result = (PyTypeObject *)PyType_Type.tp_new(type, args, kwds);
	if (result == NULL)
		return NULL;

	/* replace the class dict by our updated spam dict */
	if (-1 == PyDict_Update((PyObject *)stgdict, result->tp_dict)) {
		Py_DECREF(result);
		Py_DECREF((PyObject *)stgdict);
		return NULL;
	}
	Py_DECREF(result->tp_dict);
	result->tp_dict = (PyObject *)stgdict;

	stgdict->getfunc = generic_getfunc;
	stgdict->setfunc = StructUnion_setfunc;
	stgdict->asparam = Array_asparam;

	/* Special casing character arrays.
	   A permanent annoyance: char arrays are also strings!
	*/
	if (proto == CTYPE_c_char) {
		if (-1 == add_getset(result, CharArray_getsets))
			return NULL;
		stgdict->getfunc = CharArray_getfunc;
		stgdict->setfunc = CharArray_setfunc;
#ifdef CTYPES_UNICODE
	} else if (proto == CTYPE_c_wchar) {
		if (-1 == add_getset(result, WCharArray_getsets))
			return NULL;
		stgdict->getfunc = WCharArray_getfunc;
		stgdict->setfunc = WCharArray_setfunc;
#endif
	}

	return (PyObject *)result;
}

PyTypeObject ArrayType_Type = {
	PyObject_HEAD_INIT(NULL)
	0,					/* ob_size */
	"_ctypes.ArrayType",			/* tp_name */
	0,					/* tp_basicsize */
	0,					/* tp_itemsize */
	0,					/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	0,					/* tp_compare */
	0,			       		/* tp_repr */
	0,					/* tp_as_number */
	&CDataType_as_sequence,			/* tp_as_sequence */
	0,					/* tp_as_mapping */
	0,					/* tp_hash */
	0,					/* tp_call */
	0,					/* tp_str */
	0,					/* tp_getattro */
	0,					/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
	"metatype for the Array Objects",	/* tp_doc */
	0,					/* tp_traverse */
	0,					/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,					/* tp_iter */
	0,					/* tp_iternext */
	CDataType_methods,			/* tp_methods */
	0,					/* tp_members */
	0,					/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	0,					/* tp_init */
	0,					/* tp_alloc */
	ArrayType_new,				/* tp_new */
	0,					/* tp_free */
};


/******************************************************************/
static PyObject *
generic_from_param(PyObject *type, PyObject *value)
{
	StgDictObject *typedict = PyType_stgdict(type);
	PyCArgObject *parg = new_CArgObject();
	if (parg == NULL)
		return NULL;
	/* This makes function calls somewhat slower, imo, since a
	   PyCArgObject is allocated for each argument.  When from_param will
	   be a slot function in the stgdict, the signature can change and it
	   can be made faster again.
	*/
	parg->pffi_type = &typedict->ffi_type;
	parg->obj = typedict->setfunc(&parg->value, value, 0, type);
	if (parg->obj == NULL) {
		Py_DECREF(parg);
		return NULL;
	}
	return (PyObject *)parg;
}

/*
  SimpleType_Type
*/
/*

SimpleType_new ensures that the new Simple_Type subclass created has a valid
_type_ attribute.

*/

static char *SIMPLE_TYPE_CHARS = "cbBhHiIlLdfuzZqQPXOv";

static PyObject *
c_void_p_from_param(PyObject *type, PyObject *value)
{
	StgDictObject *stgd;

	if (value == Py_None) {
		Py_INCREF(Py_None);
		return Py_None;
	}
	if (PyString_Check(value)) {
		PyCArgObject *parg;
		struct fielddesc *fd = getentry("z");

		parg = new_CArgObject();
		parg->pffi_type = &ffi_type_pointer;
		parg->obj = fd->setfunc(&parg->value, value, 0, type);
		if (parg->obj == NULL) {
			Py_DECREF(parg);
			return NULL;
		}
		return (PyObject *)parg;
	}
	if (PyUnicode_Check(value)) {
		PyCArgObject *parg;
		struct fielddesc *fd = getentry("Z");

		parg = new_CArgObject();
		parg->pffi_type = &ffi_type_pointer;
		parg->obj = fd->setfunc(&parg->value, value, 0, type);
		if (parg->obj == NULL) {
			Py_DECREF(parg);
			return NULL;
		}
		return (PyObject *)parg;
	}
	if (PyObject_IsInstance(value, type)) {
		/* c_void_p instances */
		Py_INCREF(value);
		return value;
	}
	if (ArrayObject_Check(value) || PointerObject_Check(value)) {
		/* Any array or pointer is accepted */
		Py_INCREF(value);
		return value;
	}
	if (PyCArg_CheckExact(value)) {
		/* byref(c_xxx()) */
		PyCArgObject *a = (PyCArgObject *)value;
		if (a->pffi_type == &ffi_type_pointer) {
			Py_INCREF(value);
			return value;
		}
	}
	stgd = PyObject_stgdict(value);
	if (stgd && (stgd->itemtype == CTYPE_c_char || stgd->itemtype == CTYPE_c_wchar)) {
		PyCArgObject *parg = new_CArgObject();
		if (parg == NULL)
			return NULL;
		parg->pffi_type = &ffi_type_pointer;
		Py_INCREF(value);
		parg->obj = value;
		/* Remember: b_ptr points to where the pointer is stored! */
		parg->value.p = *(void **)(((CDataObject *)value)->b_ptr);
		return (PyObject *)parg;
	}
	/* XXX better message */
	PyErr_SetString(PyExc_TypeError,
			"wrong type");
	return NULL;
}

static PyMethodDef c_void_p_method = { "from_param", c_void_p_from_param, METH_O };

static int
Simple_asparam(CDataObject *self, struct argument *pa)
{
	StgDictObject *dict = PyObject_stgdict((PyObject *)self);
	pa->ffi_type = &dict->ffi_type;
	/* Hm, Aren't here any little/big endian issues? */
	assert(sizeof(pa->value) >= self->b_size);
	memcpy(&pa->value, self->b_ptr, self->b_size);
	Py_INCREF(self);
	pa->keep = (PyObject *)self;
	return 0;
}

static PyObject *
SimpleType_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	PyTypeObject *result;
	StgDictObject *stgdict;
	PyObject *proto;
	PyMethodDef *ml;
	struct fielddesc *fmt;

	/* create the new instance (which is a class,
	   since we are a metatype!) */
	result = (PyTypeObject *)PyType_Type.tp_new(type, args, kwds);
	if (result == NULL)
		return NULL;

	proto = PyObject_GetAttrString((PyObject *)result, "_type_"); /* new ref */
	if (!proto
	    || !PyString_Check(proto)
	    || 1 != strlen(PyString_AS_STRING(proto))
	    || !strchr(SIMPLE_TYPE_CHARS, PyString_AS_STRING(proto)[0])) {
		PyErr_Format(PyExc_AttributeError,
			     "class must define a '_type_' attribute which must be\n"
			     "a single character string containing one of '%s'.",
			     SIMPLE_TYPE_CHARS);
		Py_XDECREF(proto);
		Py_DECREF(result);
		return NULL;
	}
	stgdict = (StgDictObject *)PyObject_CallObject(
		(PyObject *)&StgDict_Type, NULL);
	if (!stgdict) {
		Py_DECREF(proto);
		return NULL;
	}

	fmt = getentry(PyString_AS_STRING(proto));

	stgdict->ffi_type = *fmt->pffi_type;
	stgdict->align = fmt->pffi_type->alignment;
	stgdict->length = 0;
	stgdict->size = fmt->pffi_type->size;
	stgdict->setfunc = fmt->setfunc;
	stgdict->getfunc = fmt->getfunc;
	stgdict->asparam = Simple_asparam;

	/* replace the class dict by the storage dict */
	if (-1 == PyDict_Update((PyObject *)stgdict, result->tp_dict)) {
		Py_DECREF(proto);
		Py_DECREF(result);
		Py_DECREF((PyObject *)stgdict);
		return NULL;
	}
	Py_DECREF(result->tp_dict);
	result->tp_dict = (PyObject *)stgdict;

	/* Install special from_param class methods in ctypes base classes.
	   Overrides the generic_from_param generic method.
	 */
	ml = NULL;
	if (result->tp_base == &Simple_Type) {
		switch (PyString_AS_STRING(proto)[0]) {
		case 'z': /* c_char_p */
			if (CTYPE_c_char == NULL) {
				PyErr_SetString(PyExc_RuntimeError,
						"Need to define c_char before c_char_p");
				return NULL; /* don't care about refcount leaks */
			}
			Py_XDECREF(stgdict->itemtype);
			Py_INCREF(CTYPE_c_char);
			stgdict->itemtype = CTYPE_c_char;
			assert(CTYPE_c_char_p == NULL);
			CTYPE_c_char_p = (PyObject *)result;
			break;
		case 'Z': /* c_wchar_p */
			if (CTYPE_c_wchar == NULL) {
				PyErr_SetString(PyExc_RuntimeError,
						"Need to define c_wchar before c_wchar_p");
				return NULL; /* don't care about refcount leaks */
			}
			Py_XDECREF(stgdict->itemtype);
			Py_INCREF(CTYPE_c_wchar);
			stgdict->itemtype = CTYPE_c_wchar;
			assert(CTYPE_c_wchar_p == NULL);
			CTYPE_c_wchar_p = (PyObject *)result;
			break;
		case 'P': /* c_void_p */
			ml = &c_void_p_method;
			assert(CTYPE_c_void_p == NULL);
			Py_INCREF(result);
			CTYPE_c_void_p = (PyObject *)result;
			break;
		case 'c': /* c_char */
			assert(CTYPE_c_char == NULL);
			CTYPE_c_char = (PyObject *)result;
			break;
		case 'X': /* BSTR */
			assert(CTYPE_BSTR == NULL);
			CTYPE_BSTR = (PyObject *)result;
			break;
		case 'u': /* c_wchar */
			assert(CTYPE_c_wchar == NULL);
			CTYPE_c_wchar = (PyObject *)result;
			break;
		}
			
		if (ml) {
			PyObject *meth;
			int x;
			meth = PyDescr_NewClassMethod(result, ml);
			if (!meth)
				return NULL;
			x = PyDict_SetItemString(result->tp_dict,
						 ml->ml_name,
						 meth);
			Py_DECREF(meth);
			if (x == -1) {
				Py_DECREF(result);
				return NULL;
			}
		}
	}
	Py_DECREF(proto);
	return (PyObject *)result;
}

/*
  The from_param protocol should change. Suggested by Andreas Degert.

  The ctypes buildin types probably should NOT have a from_param method any
  longer.  The from_param method of other types must return something that
  ConvParam can handle: int, string, or a ctypes instance.

  When a ctypes type is used in the argtypes list:
  - argtypes[i] is the type
  - converters[i] is type.from_param or NULL

  ConvParam does:
  - if converters[i] is non-NULL: call it with the actual argument, use the result
  - if converters[i] is NULL: call argtypes[i]->setfunc with the actual argument, use the result
 */

static PyMethodDef SimpleType_methods[] = {
	{ "from_param", generic_from_param, METH_O, from_param_doc },
	{ "from_address", CDataType_from_address, METH_O, from_address_doc },
	{ "in_dll", CDataType_in_dll, METH_VARARGS, in_dll_doc},
	{ NULL, NULL },
};

PyTypeObject SimpleType_Type = {
	PyObject_HEAD_INIT(NULL)
	0,					/* ob_size */
	"_ctypes.SimpleType",				/* tp_name */
	0,					/* tp_basicsize */
	0,					/* tp_itemsize */
	0,					/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	0,					/* tp_compare */
	0,			       		/* tp_repr */
	0,					/* tp_as_number */
	&CDataType_as_sequence,		/* tp_as_sequence */
	0,					/* tp_as_mapping */
	0,					/* tp_hash */
	0,					/* tp_call */
	0,					/* tp_str */
	0,					/* tp_getattro */
	0,					/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
	"metatype for the SimpleType Objects",	/* tp_doc */
	0,					/* tp_traverse */
	0,					/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,					/* tp_iter */
	0,					/* tp_iternext */
	SimpleType_methods,			/* tp_methods */
	0,					/* tp_members */
	0,					/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	0,					/* tp_init */
	0,					/* tp_alloc */
	SimpleType_new,				/* tp_new */
	0,					/* tp_free */
};

/******************************************************************/
/*
  CFuncPtrType_Type
 */

static PyObject *
converters_from_argtypes(PyObject *ob)
{
	PyObject *converters;
	int i;
	int nArgs;

	ob = PySequence_Tuple(ob); /* new reference */
	if (!ob) {
		PyErr_SetString(PyExc_TypeError,
				"_argtypes_ must be a sequence of types");
		return NULL;
	}

	nArgs = PyTuple_GET_SIZE(ob);
	converters = PyTuple_New(nArgs);
	if (!converters)
		return NULL;
		
	/* I have to check if this is correct. Using c_char, which has a size
	   of 1, will be assumed to be pushed as only one byte!
	   Aren't these promoted to integers by the C compiler and pushed as 4 bytes?
	*/

	for (i = 0; i < nArgs; ++i) {
		PyObject *tp = PyTuple_GET_ITEM(ob, i);
		StgDictObject *dict = PyType_stgdict(tp);
		PyObject *cnv = PyObject_GetAttrString(tp, "from_param");
		if (!dict || !cnv)
			goto argtypes_error_1;
		PyTuple_SET_ITEM(converters, i, cnv);
	}
	Py_DECREF(ob);
	return converters;

  argtypes_error_1:
	Py_XDECREF(converters);
	Py_DECREF(ob);
	PyErr_Format(PyExc_TypeError,
		     "item %d in _argtypes_ is not a valid C type", i+1);
	return NULL;
}

static int
make_funcptrtype_dict(StgDictObject *stgdict)
{
	PyObject *ob;
	PyObject *converters = NULL;

	stgdict->align = getentry("P")->pffi_type->alignment;
	stgdict->length = 1;
	stgdict->size = sizeof(void *);
	stgdict->getfunc = generic_getfunc;
	stgdict->setfunc = basic_setfunc;
	stgdict->ffi_type = ffi_type_pointer;

	ob = PyDict_GetItemString((PyObject *)stgdict, "_flags_");
	if (!ob || !PyInt_Check(ob)) {
		PyErr_SetString(PyExc_TypeError,
		    "class must define _flags_ which must be an integer");
		return -1;
	}
	stgdict->flags = PyInt_AS_LONG(ob);

	/* _argtypes_ is optional... */
	ob = PyDict_GetItemString((PyObject *)stgdict, "_argtypes_");
	if (ob) {
		converters = converters_from_argtypes(ob);
		if (!converters)
			goto error;
		Py_INCREF(ob);
		stgdict->argtypes = ob;
		stgdict->converters = converters;
	}

	ob = PyDict_GetItemString((PyObject *)stgdict, "_restype_");
	if (ob) {
		if (ob != Py_None && !PyType_stgdict(ob) && !PyCallable_Check(ob)) {
			PyErr_SetString(PyExc_TypeError,
				"_restype_ must be a type, a callable, or None");
			return -1;
		}
		Py_INCREF(ob);
		stgdict->restype = ob;
		stgdict->checker = PyObject_GetAttrString(ob, "_check_retval_");
		if (stgdict->checker == NULL)
			PyErr_Clear();
	}
	return 0;

  error:
	Py_XDECREF(converters);
	return -1;

}

static int
CFuncPtr_asparam(CDataObject *self, struct argument *pa)
{
	pa->ffi_type = &ffi_type_pointer;
	pa->value.p = *(void **)self->b_ptr;
	Py_INCREF(self);
	pa->keep = (PyObject *)self;
	return 0;
}

static PyObject *
CFuncPtrType_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	PyTypeObject *result;
	StgDictObject *stgdict;

	stgdict = (StgDictObject *)PyObject_CallObject(
		(PyObject *)&StgDict_Type, NULL);
	if (!stgdict)
		return NULL;

	/* create the new instance (which is a class,
	   since we are a metatype!) */
	result = (PyTypeObject *)PyType_Type.tp_new(type, args, kwds);
	if (result == NULL) {
		Py_DECREF((PyObject *)stgdict);
		return NULL;
	}

	/* replace the class dict by our updated storage dict */
	if (-1 == PyDict_Update((PyObject *)stgdict, result->tp_dict)) {
		Py_DECREF(result);
		Py_DECREF((PyObject *)stgdict);
		return NULL;
	}
	Py_DECREF(result->tp_dict);
	result->tp_dict = (PyObject *)stgdict;

	if (-1 == make_funcptrtype_dict(stgdict)) {
		Py_DECREF(result);
		return NULL;
	}
	stgdict->asparam = CFuncPtr_asparam;
	return (PyObject *)result;
}

PyTypeObject CFuncPtrType_Type = {
	PyObject_HEAD_INIT(NULL)
	0,					/* ob_size */
	"_ctypes.CFuncPtrType",			/* tp_name */
	0,					/* tp_basicsize */
	0,					/* tp_itemsize */
	0,					/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	0,					/* tp_compare */
	0,			       		/* tp_repr */
	0,					/* tp_as_number */
	&CDataType_as_sequence,			/* tp_as_sequence */
	0,					/* tp_as_mapping */
	0,					/* tp_hash */
	0,					/* tp_call */
	0,					/* tp_str */
	0,					/* tp_getattro */
	0,					/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
	"metatype for C function pointers",	/* tp_doc */
	0,					/* tp_traverse */
	0,					/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,					/* tp_iter */
	0,					/* tp_iternext */
	CDataType_methods,			/* tp_methods */
	0,					/* tp_members */
	0,					/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	0,					/* tp_init */
	0,					/* tp_alloc */
	CFuncPtrType_new,			/* tp_new */
	0,					/* tp_free */
};


/*****************************************************************
 * Code to keep needed objects alive
 */

static CDataObject *
CData_GetContainer(CDataObject *self)
{
	while (self->b_base)
		self = self->b_base;
	if (self->b_objects == NULL) {
		if (self->b_length) {
			self->b_objects = PyDict_New();
		} else {
			Py_INCREF(Py_None);
			self->b_objects = Py_None;
		}
	}
	return self;
}

PyObject *
GetKeepedObjects(CDataObject *target)
{
	return CData_GetContainer(target)->b_objects;
}

static PyObject *
unique_key(CDataObject *target, int index)
{
	char string[256]; /* XXX is that enough? */
	char *cp = string;
	int len;
	*cp++ = index + '0';
	while (target->b_base) {
		*cp++ = target->b_index + '0';
		target = target->b_base;
	}
	len = cp - string;
	return PyString_FromStringAndSize(string, cp-string);
}
/* Keep a reference to 'keep' in the 'target', at index 'index' */
/*
 * KeepRef travels the target's b_base pointer down to the root,
 * building a sequence of indexes during the path.  The indexes, which are a
 * couple of small integers, are used to build a byte string usable as
 * key int the root object's _objects dict.
 */
int
KeepRef(CDataObject *target, int index, PyObject *keep)
{
	int result;
	CDataObject *ob;
	PyObject *key;

/* Optimization: no need to store None */
	if (keep == Py_None) {
		Py_DECREF(Py_None);
		return 0;
	}
	ob = CData_GetContainer(target);
	if (ob->b_objects == NULL || !PyDict_Check(ob->b_objects)) {
		Py_XDECREF(ob->b_objects);
		ob->b_objects = keep; /* refcount consumed */
		return 0;
	}
	key = unique_key(target, index);
	result = PyDict_SetItem(ob->b_objects, key, keep);
	Py_DECREF(key);
	Py_DECREF(keep);
	return result;
}

/******************************************************************/
/*
  CData_Type
 */
static int
CData_traverse(CDataObject *self, visitproc visit, void *arg)
{
	Py_VISIT(self->b_objects);
	Py_VISIT((PyObject *)self->b_base);
	return 0;
}

static int
CData_clear(CDataObject *self)
{
	Py_CLEAR(self->b_objects);
#ifdef MS_WIN32
	if (self->b_base == NULL) {
		/* If a BSTR instance owns the memory (b_base is NULL), we
		   have to call SysFreeString.
		*/
		if (PyObject_IsInstance((PyObject *)self, CTYPE_BSTR)) {
			if (*(BSTR *)self->b_ptr)
				SysFreeString(*(BSTR *)self->b_ptr);
		}
	}
#endif
	if (self->b_needsfree)
		PyMem_Free(self->b_ptr);
	self->b_ptr = NULL;
	Py_CLEAR(self->b_base);
	return 0;
}

static void
CData_dealloc(PyObject *self)
{
	CData_clear((CDataObject *)self);
	self->ob_type->tp_free(self);
}

static PyMemberDef CData_members[] = {
	{ "_b_base_", T_OBJECT,
	  offsetof(CDataObject, b_base), READONLY,
	  "the base object" },
	{ "_objects", T_OBJECT,
	  offsetof(CDataObject, b_objects), READONLY,
	  "internal objects tree (NEVER CHANGE THIS LIST!)"},
	{ NULL },
};

static int CData_GetBuffer(CDataObject *self, int seg, void **pptr)
{
	if (seg != 0) {
		/* Hm. Must this set an exception? */
		return -1;
	}
	*pptr = self->b_ptr;
	return self->b_size;
}

static int CData_GetSegcount(CDataObject *self, int *lenp)
{
	if (lenp)
		*lenp = 1;
	return 1;
}

static PyBufferProcs CData_as_buffer = {
	(getreadbufferproc)CData_GetBuffer,
	(getwritebufferproc)CData_GetBuffer,
	(getsegcountproc)CData_GetSegcount,
	(getcharbufferproc)NULL,
};

/*
 * CData objects are mutable, so they cannot be hashable!
 */
static long
CData_nohash(PyObject *self)
{
	PyErr_SetString(PyExc_TypeError, "unhashable type");
	return -1;
}

PyTypeObject CData_Type = {
	PyObject_HEAD_INIT(NULL)
	0,
	"_ctypes._CData",
	sizeof(CDataObject),			/* tp_basicsize */
	0,					/* tp_itemsize */
	CData_dealloc,				/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	0,					/* tp_compare */
	0,					/* tp_repr */
	0,					/* tp_as_number */
	0,					/* tp_as_sequence */
	0,					/* tp_as_mapping */
	CData_nohash,				/* tp_hash */
	0,					/* tp_call */
	0,					/* tp_str */
	0,					/* tp_getattro */
	0,					/* tp_setattro */
	&CData_as_buffer,			/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
	"XXX to be provided",			/* tp_doc */
	(traverseproc)CData_traverse,		/* tp_traverse */
	(inquiry)CData_clear,			/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,					/* tp_iter */
	0,					/* tp_iternext */
	0,					/* tp_methods */
	CData_members,				/* tp_members */
	0,					/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	0,					/* tp_init */
	0,					/* tp_alloc */
	0,					/* tp_new */
	0,					/* tp_free */
};

/* Allocate memory (or not) for a CDataObject instance */
static void CData_MallocBuffer(CDataObject *obj, StgDictObject *dict)
{
	if (dict->size <= sizeof(obj->b_value)) {
		/* No need to call malloc, can use the default buffer */
		obj->b_ptr = (char *)&obj->b_value;
		obj->b_needsfree = 0;
	} else {
		/* In python 2.4, and ctypes 0.9.6, the malloc call took about
		   33% of the creation time for c_int().
		*/
		obj->b_ptr = PyMem_Malloc(dict->size);
		obj->b_needsfree = 1;
		memset(obj->b_ptr, 0, dict->size);
	}
	obj->b_size = dict->size;
}

PyObject *
CData_FromBaseObj(PyObject *type, PyObject *base, int index, char *adr)
{
	CDataObject *cmem;

	if (base && !CDataObject_Check(base)) {
		PyErr_SetString(PyExc_TypeError,
				"expected a ctype type");
		return NULL;
	}

	cmem = (CDataObject *)PyObject_CallFunctionObjArgs(type, NULL);
	if (cmem == NULL)
		return NULL;

	if (cmem->b_needsfree)
		PyMem_Free(cmem->b_ptr);
	cmem->b_ptr = NULL;

	if (base) { /* use base's buffer */
		cmem->b_ptr = adr;
		cmem->b_needsfree = 0;
		Py_INCREF(base);
		cmem->b_base = (CDataObject *)base;
		cmem->b_index = index;
	} else { /* copy contents of adr */
		StgDictObject *dict = PyType_stgdict(type);
		CData_MallocBuffer(cmem, PyType_stgdict(type));
		memcpy(cmem->b_ptr, adr, dict->size);
		cmem->b_index = index;
	}
	return (PyObject *)cmem;
}

/*
 Box a memory block into a CData instance.

 We create an new instance, free the memory it contains, and fill in the
 memory pointer afterwards.
*/
static PyObject *
CData_AtAddress(PyObject *type, void *buf)
{
	CDataObject *pd;

	pd = (CDataObject *)PyObject_CallFunctionObjArgs(type, NULL);
	if (!pd)
		return NULL;
	if (!CDataObject_Check(pd)) {
		Py_DECREF(pd);
		PyErr_SetString(PyExc_TypeError,
				"BUG: type call did not return a CDataObject");
		return NULL;
	}
	if (pd->b_needsfree) {
		pd->b_needsfree = 0;
		PyMem_Free(pd->b_ptr);
	}
	pd->b_ptr = buf;
	return (PyObject *)pd;
}

/*
 * Set an item in object 'dst', which has the itemtype 'type', to 'value'.
 * This function has the same signature as the SETFUNC has.
 * XXX Explain differences between this function and the type's setfunc.
 * XXX See also _generic_field_setfunc...
 */
static PyObject *
_CData_set(void *ptr, PyObject *value, unsigned size, PyObject *type)
{
	CDataObject *src;

	if (!CDataObject_Check(value)) {
		StgDictObject *dict = PyType_stgdict(type);
		assert(dict);
		assert(dict->setfunc);
		return dict->setfunc(ptr, value, size, type);
	}
	src = (CDataObject *)value;

	/* Hm.  Shouldn't dict->setfunc accept this? */
	if (PyObject_IsInstance(value, type)) {
		memcpy(ptr,
		       src->b_ptr,
		       size);

		value = GetKeepedObjects(src);
		Py_INCREF(value);
		return value;
	}
	PyErr_Format(PyExc_TypeError,
		     "incompatible types, %s instance instead of %s instance",
		     value->ob_type->tp_name,
		     ((PyTypeObject *)type)->tp_name);
	return NULL;
}


/******************************************************************/
static PyObject *
GenericCData_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	CDataObject *obj;
	int size, align, length;
	StgDictObject *dict;

	dict = PyType_stgdict((PyObject *)type);
	if (!dict) {
		PyErr_SetString(PyExc_TypeError,
				"abstract class");
		return NULL;
	}
	dict->flags |= DICTFLAG_FINAL;
	size = dict->size;
	align = dict->align;
	length = dict->length;

	obj = (CDataObject *)type->tp_alloc(type, 0);
	if (!obj)
		return NULL;

	obj->b_base = NULL;
	obj->b_index = 0;
	obj->b_objects = NULL;
	obj->b_length = length;

	CData_MallocBuffer(obj, dict);
	return (PyObject *)obj;
}
/*****************************************************************/
/*
  CFuncPtr_Type
*/

static int
CFuncPtr_set_restype(CFuncPtrObject *self, PyObject *ob)
{
	PyObject *checker;
	if (ob == NULL) {
		Py_XDECREF(self->restype);
		self->restype = NULL;
		Py_XDECREF(self->checker);
		self->checker = NULL;
		return 0;
	}
	if (ob != Py_None && !PyType_stgdict(ob) && !PyCallable_Check(ob)) {
		PyErr_SetString(PyExc_TypeError,
				"restype must be a type, a callable, or None");
		return -1;
	}
	Py_XDECREF(self->restype);
	Py_INCREF(ob);
	self->restype = ob;
	checker = PyObject_GetAttrString(ob, "_check_retval_");
	if (checker == NULL) {
		PyErr_Clear();
		return 0;
	}
	self->checker = checker;
	return 0;
}

static PyObject *
CFuncPtr_get_restype(CFuncPtrObject *self)
{
	StgDictObject *dict;
	if (self->restype) {
		Py_INCREF(self->restype);
		return self->restype;
	}
	dict = PyObject_stgdict((PyObject *)self);
	assert(dict);
	if (dict->restype) {
		Py_INCREF(dict->restype);
		return dict->restype;
	} else {
		Py_INCREF(Py_None);
		return Py_None;
	}
}

static int
CFuncPtr_set_argtypes(CFuncPtrObject *self, PyObject *ob)
{
	PyObject *converters;

	if (ob == NULL || ob == Py_None) {
		Py_XDECREF(self->converters);
		self->converters = NULL;
		Py_XDECREF(self->argtypes);
		self->argtypes = NULL;
	} else {
		converters = converters_from_argtypes(ob);
		if (!converters)
			return -1;
		Py_XDECREF(self->converters);
		self->converters = converters;
		Py_XDECREF(self->argtypes);
		Py_INCREF(ob);
		self->argtypes = ob;
	}
	return 0;
}

static PyObject *
CFuncPtr_get_argtypes(CFuncPtrObject *self)
{
	StgDictObject *dict;
	if (self->argtypes) {
		Py_INCREF(self->argtypes);
		return self->argtypes;
	}
	dict = PyObject_stgdict((PyObject *)self);
	assert(dict);
	if (dict->argtypes) {
		Py_INCREF(dict->argtypes);
		return dict->argtypes;
	} else {
		Py_INCREF(Py_None);
		return Py_None;
	}
}

static PyGetSetDef CFuncPtr_getsets[] = {
	{ "restype", (getter)CFuncPtr_get_restype, (setter)CFuncPtr_set_restype,
	  "specify the result type", NULL },
	{ "argtypes", (getter)CFuncPtr_get_argtypes,
	  (setter)CFuncPtr_set_argtypes,
	  "specify the argument types", NULL },
	{ NULL, NULL }
};

#ifdef MS_WIN32
static PPROC FindAddress(void *handle, char *name, PyObject *type)
{
	PPROC address;
	char *mangled_name;
	int i;
	StgDictObject *dict = PyType_stgdict((PyObject *)type);

	address = (PPROC)GetProcAddress(handle, name);
	if (address)
		return address;
	/* It should not happen that dict is NULL, but better be safe */
	if (dict==NULL || dict->flags & FUNCFLAG_CDECL)
		return address;

	/* for stdcall, try mangled names:
	   funcname -> _funcname@<n>
	   where n is 0, 4, 8, 12, ..., 128
	 */
	mangled_name = _alloca(strlen(name) + 1 + 1 + 1 + 3); /* \0 _ @ %d */
	for (i = 0; i < 32; ++i) {
		sprintf(mangled_name, "_%s@%d", name, i*4);
		address = (PPROC)GetProcAddress(handle, mangled_name);
		if (address)
			return address;
	}
	return NULL;
}
#endif

/* Returns 1 on success, 0 on error */
static int
_validate_paramflags(PyTypeObject *type, PyObject *paramflags)
{
	int i, len;
	StgDictObject *dict = PyType_stgdict((PyObject *)type);
	PyObject *argtypes = dict->argtypes;

	if (paramflags == NULL || dict->argtypes == NULL)
		return 1;

	if (!PyTuple_Check(paramflags)) {
		PyErr_SetString(PyExc_TypeError,
				"paramflags must be a tuple or None");
		return 0;
	}

	len = PyTuple_GET_SIZE(paramflags);
	if (len != PyTuple_GET_SIZE(dict->argtypes)) {
		PyErr_SetString(PyExc_ValueError,
				"paramflags must have the same length as argtypes");
		return 0;
	}
	
	for (i = 0; i < len; ++i) {
		PyObject *item = PyTuple_GET_ITEM(paramflags, i);
		int flag;
		char *name;
		PyObject *defval;
		PyObject *typ;
		if (!PyArg_ParseTuple(item, "i|zO", &flag, &name, &defval)) {
			PyErr_SetString(PyExc_TypeError,
			       "paramflags must be a sequence of (int [,string [,value]]) tuples");
			return 0;
		}
		typ = PyTuple_GET_ITEM(argtypes, i);
		dict = PyType_stgdict(typ);
		if ((flag & 2) && (dict->ffi_type.type != FFI_TYPE_POINTER)) {
			PyErr_Format(PyExc_TypeError,
				     "output parameter %d not a pointer type: %s",
				     i+1,
				     ((PyTypeObject *)typ)->tp_name);
			return 0;
		}
		switch (flag) {
		case 0:
		case PARAMFLAG_FIN:
		case PARAMFLAG_FOUT:
		case (PARAMFLAG_FIN | PARAMFLAG_FOUT):
			break;
		default:
			PyErr_Format(PyExc_TypeError,
				     "paramflag value %d not supported",
				     flag);
			return 0;
		}
	}
	return 1;
}

static PyObject *
CFuncPtr_FromDll(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	char *name;
	int (* address)(void);
	PyObject *dll;
	PyObject *obj;
	CFuncPtrObject *self;
	void *handle;
	PyObject *paramflags = NULL;

	if (!PyArg_ParseTuple(args, "sO|O", &name, &dll, &paramflags))
		return NULL;
	if (paramflags == Py_None)
		paramflags = NULL;

	obj = PyObject_GetAttrString(dll, "_handle");
	if (!obj)
		return NULL;
	if (!PyInt_Check(obj)) {
		PyErr_SetString(PyExc_TypeError,
				"the _handle attribute of the second argument must be an integer");
		Py_DECREF(obj);
		return NULL;
	}
	handle = (void *)PyInt_AS_LONG(obj);
	Py_DECREF(obj);

#ifdef MS_WIN32
	address = FindAddress(handle, name, (PyObject *)type);
	if (!address) {
		PyErr_Format(PyExc_AttributeError,
			     "function '%s' not found",
			     name);
		return NULL;
	}
#else
	address = (PPROC)dlsym(handle, name);
	if (!address) {
		PyErr_Format(PyExc_AttributeError,
#ifdef __CYGWIN__
/* dlerror() isn't very helpful on cygwin */
			     "function '%s' not found (%s) ",
			     name,
#endif
			     dlerror());
		return NULL;
	}
#endif
	if (!_validate_paramflags(type, paramflags))
		return NULL;

	self = (CFuncPtrObject *)GenericCData_new(type, args, kwds);
	if (!self)
		return NULL;

	Py_XINCREF(paramflags);
	self->paramflags = paramflags;

	*(void **)self->b_ptr = address;

	if (-1 == KeepRef((CDataObject *)self, 0, dll)) {
		Py_DECREF((PyObject *)self);
		return NULL;
	}
	Py_INCREF((PyObject *)dll); /* for KeepRef above */

	Py_INCREF(self);
	self->callable = (PyObject *)self;
	return (PyObject *)self;
}

#ifdef MS_WIN32
static PyObject *
CFuncPtr_FromVtblIndex(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	CFuncPtrObject *self;
	int index;
	char *name = NULL;
	PyObject *paramflags = NULL;

	if (!PyArg_ParseTuple(args, "is|O", &index, &name, &paramflags))
		return NULL;
	if (paramflags == Py_None)
		paramflags = NULL;

	if (!_validate_paramflags(type, paramflags))
		return NULL;

	self = (CFuncPtrObject *)GenericCData_new(type, args, kwds);
	self->index = index + 0x1000;
	Py_XINCREF(paramflags);
	self->paramflags = paramflags;
	return (PyObject *)self;
}
#endif

/*
  CFuncPtr_new accepts different argument lists in addition to the standard
  _basespec_ keyword arg:

  one argument form
  "i" - function address
  "O" - must be a callable, creates a C callable function

  two or more argument forms (the third argument is a paramflags tuple)
  "sO|O" - function name, dll object (with an integer handle)
  "is|O" - vtable index, method name, creates callable calling COM vtbl
*/
static PyObject *
CFuncPtr_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	CFuncPtrObject *self;
	PyObject *callable;
	StgDictObject *dict;
	THUNK thunk;

	/* We're retrieved from a structure field or C result, maybe */
	if (PyTuple_GET_SIZE(args) == 0)
		return GenericCData_new(type, args, kwds);

	if (2 <= PyTuple_GET_SIZE(args)) {
#ifdef MS_WIN32
		if (PyInt_Check(PyTuple_GET_ITEM(args, 0)))
			return CFuncPtr_FromVtblIndex(type, args, kwds);
#endif
		return CFuncPtr_FromDll(type, args, kwds);
	}

	if (1 == PyTuple_GET_SIZE(args)
	    && (PyInt_Check(PyTuple_GET_ITEM(args, 0))
		|| PyLong_Check(PyTuple_GET_ITEM(args, 0)))) {
		CDataObject *ob;
		void *ptr = PyLong_AsVoidPtr(PyTuple_GET_ITEM(args, 0));
		if (ptr == NULL)
			return NULL;
		ob = (CDataObject *)GenericCData_new(type, args, kwds);
		*(void **)ob->b_ptr = ptr;
		return (PyObject *)ob;
	}

	if (!PyArg_ParseTuple(args, "O", &callable))
		return NULL;
	if (!PyCallable_Check(callable)) {
		PyErr_SetString(PyExc_TypeError,
				"argument must be callable or integer function address");
		return NULL;
	}

	/* XXX XXX This would allow to pass additional options.  For COM
	   method *implementations*, we would probably want different
	   behaviour than in 'normal' callback functions: return a HRESULT if
	   an exception occurrs in the callback, and print the traceback not
	   only on the console, but also to OutputDebugString() or something
	   like that.
	*/
/*
	if (kwds && PyDict_GetItemString(kwds, "options")) {
		...
	}
*/

	dict = PyType_stgdict((PyObject *)type);
	/* XXXX Fails if we do: 'CFuncPtr(lambda x: x)' */
	if (!dict || !dict->argtypes) {
		PyErr_SetString(PyExc_TypeError,
		       "cannot construct instance of this class:"
			" no argtypes");
		return NULL;
	}

	/*****************************************************************/
	/* The thunk keeps unowned references to callable and dict->argtypes
	   so we have to keep them alive somewhere else: callable is kept in self,
	   dict->argtypes is in the type's stgdict.
	*/
	thunk = AllocFunctionCallback(callable,
				      dict->argtypes,
				      dict->restype,
				      dict->flags & FUNCFLAG_CDECL);
	if (!thunk)
		return NULL;

	self = (CFuncPtrObject *)GenericCData_new(type, args, kwds);

	Py_INCREF(callable);
	self->callable = callable;

	self->thunk = thunk;
	*(void **)self->b_ptr = *(void **)thunk;

	/* We store ourself in self->b_objects[0], because the whole instance
	   must be kept alive if stored in a structure field, for example.
	   Cycle GC to the rescue! And we have a unittest proving that this works
	   correctly...
	*/

	if (-1 == KeepRef((CDataObject *)self, 0, (PyObject *)self)) {
		Py_DECREF((PyObject *)self);
		return NULL;
	}
	Py_INCREF((PyObject *)self); /* for KeepRef above */

	return (PyObject *)self;
}


/*
  _byref consumes a refcount to its argument
*/
static PyObject *
_byref(PyObject *obj)
{
	PyCArgObject *parg;
	if (!CDataObject_Check(obj)) {
		PyErr_SetString(PyExc_TypeError,
				"expected CData instance");
		return NULL;
	}

	parg = new_CArgObject();
	if (parg == NULL) {
		Py_DECREF(obj);
		return NULL;
	}

	parg->pffi_type = &ffi_type_pointer;
	parg->obj = obj;
	parg->value.p = ((CDataObject *)obj)->b_ptr;
	return (PyObject *)parg;
}

static PyObject *
_get_arg(int *pindex, char *name, PyObject *defval, PyObject *inargs, PyObject *kwds)
{
	PyObject *v;

	if (*pindex < PyTuple_GET_SIZE(inargs)) {
		v = PyTuple_GET_ITEM(inargs, *pindex);
		++*pindex;
		Py_INCREF(v);
		return v;
	}
	if (kwds && (v = PyDict_GetItemString(kwds, name))) {
		++*pindex;
		Py_INCREF(v);
		return v;
	}
	if (defval) {
		Py_INCREF(defval);
		return defval;
	}
	PyErr_Format(PyExc_TypeError,
		     "required argument '%s' missing", name);
	return NULL;
}

/*
 This function implements higher level functionality plus the ability to call
 functions with keyword arguments by looking at parameter flags.  parameter
 flags is a tuple of 1, 2 or 3-tuples.  The first entry in each is an integer
 specifying the direction of the data transfer for this parameter - 'in',
 'out' or 'inout' (zero means the same as 'in').  The second entry is the
 parameter name, and the third is the default value if the parameter is
 missing in the function call.

 Note: keyword args not yet implemented!

 This function builds a new tuple 'callargs' which contains the parameters to
 use in the call.  Items on this tuple are copied from the 'inargs' tuple for
 'in' parameters, and constructed from the 'argtypes' tuple for 'out'
 parameters.

*/
static PyObject *
_build_callargs(CFuncPtrObject *self, PyObject *argtypes,
		PyObject *inargs, PyObject *kwds,
		PyObject **pretval)
{
	PyObject *paramflags = self->paramflags;
	PyObject *callargs;
	StgDictObject *dict;
	int i, len;
	int inargs_index = 0;
	int outmask = 0;
	/* It's a little bit difficult to determine how many arguments the
	function call requires/accepts.  For simplicity, we count the consumed
	args and compare this to the number of supplied args. */
	int actual_args;

	*pretval = NULL;
	/* Trivial cases, where we either return inargs itself, or a slice of it. */
	if (argtypes == NULL || paramflags == NULL || PyTuple_GET_SIZE(argtypes) == 0) {
#ifdef MS_WIN32
		if (self->index)
			return PyTuple_GetSlice(inargs, 1, PyTuple_GET_SIZE(inargs));
#endif
		Py_INCREF(inargs);
		return inargs;
	}

	len = PyTuple_GET_SIZE(argtypes);
	callargs = PyTuple_New(len); /* the argument tuple we build */
	if (callargs == NULL)
		return NULL;

#ifdef MS_WIN32
	/* For a COM method, skip the first arg */
	if (self->index) {
		inargs_index = 1;
	}
#endif
	
	for (i = 0; i < len; ++i) {
		PyObject *item = PyTuple_GET_ITEM(paramflags, i);
		PyObject *ob, *v;
		int flag;
		char *name = NULL;
		PyObject *defval = NULL;
		if (!PyArg_ParseTuple(item, "i|zO", &flag, &name, &defval)) {
			/* Hm. Either we should raise a more specific error
			   here, or we should validate the paramflags tuple
			   when it is set */
			_AddTraceback("_build_callargs", __FILE__, __LINE__-4);
			goto error;
		}
		switch (flag) {
		case 0:
		case PARAMFLAG_FIN:
			/* 'in' parameter.  Copy it from inargs. */
			ob =_get_arg(&inargs_index, name, defval, inargs, kwds);
			if (ob == NULL)
				goto error;
			PyTuple_SET_ITEM(callargs, i, ob);
			break;
		case PARAMFLAG_FOUT:
			/* 'out' parameter.
			   argtypes[i] must be a POINTER to a c type.
			*/
			ob = PyTuple_GET_ITEM(argtypes, i);
			dict = PyType_stgdict(ob);
			/* Create an instance of the pointed-to type */
			ob = PyObject_CallObject(dict->itemtype, NULL);
			if (ob == NULL)
				goto error;
			/* Insert as byref parameter */
			ob = _byref(ob);
			if (ob == NULL)
				goto error;
			PyTuple_SET_ITEM(callargs, i, ob);
			outmask |= (1 << i);
			break;
		case (PARAMFLAG_FIN | PARAMFLAG_FOUT):
			/* for [in, out] parameters, we should probably
			   - call _get_arg to get the [in] value
			   - create an object with the [in] value as parameter
			   - and then proceed in the same way as for an [out] parameter
			*/
			ob = PyTuple_GET_ITEM(argtypes, i);
			dict = PyType_stgdict(ob);
			/* Create an instance of the pointed-to type */
			v = _get_arg(&inargs_index, name, defval, inargs, kwds);
			if (v == 0)
				goto error;
			ob = PyObject_CallFunctionObjArgs(dict->itemtype,
							  v,
							  NULL);
			Py_DECREF(v);
			if (ob == 0)
				goto error;
			ob = _byref(ob);
			if (ob == NULL)
				goto error;
			PyTuple_SET_ITEM(callargs, i, ob);
			outmask |= (1 << i);
			break;
		default:
			PyErr_Format(PyExc_ValueError,
				     "paramflag %d not yet implemented", flag);
			goto error;
			break;
		}
	}

	/* We have counted the arguments we have consumed in 'inargs_index'.  This
	   must be the same as len(inargs) + len(kwds), otherwise we have
	   either too much or not enough arguments. */

	actual_args = PyTuple_GET_SIZE(inargs) + (kwds ? PyDict_Size(kwds) : 0);
	if (actual_args != inargs_index) {
		/* When we have default values or named parameters, this error
		   message is misleading.  See unittests/test_paramflags.py
		 */
		PyErr_Format(PyExc_TypeError,
			     "call takes exactly %d arguments (%d given)",
			     inargs_index, actual_args);
		goto error;
	}

	/* outmask is a bitmask containing indexes into callargs.  Items at
	   these indexes contain values to return.
	 */

	len = 0;
	for (i = 0; i < 32; ++i) {
		if (outmask & (1 << i))
			++len;
	}

	switch (len) {
		int j;
	case 0:
		*pretval = NULL;
		break;
	case 1:
		for (i = 0; i < 32; ++i) {
			if (outmask & (1 << i)) {
				*pretval = PyTuple_GET_ITEM(callargs, i);
				Py_INCREF(*pretval);
				break;
			}
		}
		break;
	default:
		*pretval = PyTuple_New(len);
		j = 0;
		for (i = 0; i < 32; ++i) {
			PyObject *ob;
			if (outmask & (1 << i)) {
				ob = PyTuple_GET_ITEM(callargs, i);
				Py_INCREF(ob);
				PyTuple_SET_ITEM(*pretval, j, ob);
				++j;
			}
		}
	}

	return callargs;
  error:
	Py_DECREF(callargs);
	return NULL;
}

static PyObject *
_get_one(PyObject *obj)
{
	PyCArgObject *arg = (PyCArgObject *)obj;
	PyObject *result = arg->obj;
	StgDictObject *dict = PyObject_stgdict(result);

/*
  XXX See comments in comtypes::COMMETHOD2.  Urgent need to clean this up:
  replace with a _from_outparam_ slot call.
*/
	/* XXX XXX This needs to be fixed. dict->itemtype is NEVER a string any more. */
	if (dict->itemtype && PyString_CheckExact(dict->itemtype)) {
		char *fmt = PyString_AS_STRING(dict->itemtype);
		/* simple data type, but no pointer */
		if (fmt[0] == 'P') {
			Py_INCREF(result);
			return result;
		}
	}
	if (dict->getfunc) {
		CDataObject *c = (CDataObject *)result;
		return dict->getfunc(c->b_ptr, c->b_size,
				     (PyObject *)result->ob_type, c, 0);
	}
	Py_INCREF(result);
	return result;
}

static PyObject *
_build_result(PyObject *result, PyObject *retval)
{
	int i, len;

	if (retval == NULL)
		return result;
	if (result == NULL) {
		Py_DECREF(retval);
		return NULL;
	}
	Py_DECREF(result);

	if (!PyTuple_CheckExact(retval)) {
		PyObject *v = _get_one(retval);
		Py_DECREF(retval);
		return v;
	}
	assert (retval->ob_refcnt == 1);
	/* We know we are sole owner of the retval tuple.  So, we can replace
	   the values in it instead of allocating a new one.
	*/
	len = PyTuple_GET_SIZE(retval);
	for (i = 0; i < len; ++i) {
		PyObject *ob = _get_one(PyTuple_GET_ITEM(retval, i));
		PyTuple_SetItem(retval, i, ob);
	}
	return retval;
}

static PyObject *
CFuncPtr_call(CFuncPtrObject *self, PyObject *inargs, PyObject *kwds)
{
	PyObject *restype;
	PyObject *converters;
	PyObject *checker;
	PyObject *argtypes;
	StgDictObject *dict = PyObject_stgdict((PyObject *)self);
	PyObject *result;
	PyObject *callargs;
	PyObject *retval;
#ifdef MS_WIN32
	IUnknown *piunk = NULL;
#endif
	void *pProc = NULL;

	assert(dict); /* if not, it's a bug */
	restype = self->restype ? self->restype : dict->restype;
	converters = self->converters ? self->converters : dict->converters;
	checker = self->checker ? self->checker : dict->checker;
	argtypes = self->argtypes ? self->argtypes : dict->argtypes;


	pProc = *(void **)self->b_ptr;
#ifdef MS_WIN32
	if (self->index) {
		/* It's a COM method */
		CDataObject *this;
		this = (CDataObject *)PyTuple_GetItem(inargs, 0); /* borrowed ref! */
		if (!this) {
			PyErr_SetString(PyExc_ValueError,
					"native com method call without 'this' parameter");
			return NULL;
		}
		if (!CDataObject_Check(this)) {
			PyErr_SetString(PyExc_TypeError,
					"Expected a COM this pointer as first argument");
			return NULL;
		}
		/* there should be more checks? No, in Python */
		/* First arg is an pointer to an interface instance */
		if (!this->b_ptr || *(void **)this->b_ptr == NULL) {
			PyErr_SetString(PyExc_ValueError,
					"NULL COM pointer access");
			return NULL;
		}
		piunk = *(IUnknown **)this->b_ptr;
		if (NULL == piunk->lpVtbl) {
			PyErr_SetString(PyExc_ValueError,
					"COM method call without VTable");
			return NULL;
		}
		pProc = ((void **)piunk->lpVtbl)[self->index - 0x1000];
	}
#endif
	callargs = _build_callargs(self, argtypes, inargs, kwds, &retval);
	if (callargs == NULL)
		return NULL;

	if (converters) {
		int required = PyTuple_GET_SIZE(converters);
		int actual = PyTuple_GET_SIZE(callargs);

		if ((dict->flags & FUNCFLAG_CDECL) == FUNCFLAG_CDECL) {
			/* For cdecl functions, we allow more actual arguments
			   than the length of the argtypes tuple.
			*/
			if (required > actual) {
				Py_DECREF(callargs);
				PyErr_Format(PyExc_TypeError,
			  "this function takes at least %d argument%s (%d given)",
					     required,
					     required == 1 ? "" : "s",
					     actual);
				return NULL;
			}
		} else if (required != actual) {
			Py_DECREF(callargs);
			PyErr_Format(PyExc_TypeError,
			     "this function takes %d argument%s (%d given)",
				     required,
				     required == 1 ? "" : "s",
				     actual);
			return NULL;
		}
	}

	result = _CallProc(pProc,
			   callargs,
#ifdef MS_WIN32
			   piunk,
#else
			   NULL,
#endif
			   dict->flags,
			   converters,
			   restype,
			   checker);
	Py_DECREF(callargs);
	return _build_result(result, retval);
}

static int
CFuncPtr_traverse(CFuncPtrObject *self, visitproc visit, void *arg)
{
	Py_VISIT(self->callable);
	Py_VISIT(self->restype);
	Py_VISIT(self->checker);
	Py_VISIT(self->argtypes);
	Py_VISIT(self->converters);
	Py_VISIT(self->b_objects);
	Py_VISIT(self->paramflags);
	return 0;
}

static int
CFuncPtr_clear(CFuncPtrObject *self)
{
	Py_CLEAR(self->callable);
	Py_CLEAR(self->restype);
	Py_CLEAR(self->checker);
	Py_CLEAR(self->argtypes);
	Py_CLEAR(self->converters);
	Py_CLEAR(self->b_objects);
	Py_CLEAR(self->paramflags);

	if (self->b_needsfree)
		PyMem_Free(self->b_ptr);
	self->b_ptr = NULL;

	if (self->thunk)
		FreeCallback(self->thunk);
	self->thunk = NULL;

	return 0;
}

static void
CFuncPtr_dealloc(CFuncPtrObject *self)
{
	CFuncPtr_clear(self);
	self->ob_type->tp_free((PyObject *)self);
}

PyTypeObject CFuncPtr_Type = {
	PyObject_HEAD_INIT(NULL)
	0,
	"_ctypes.CFuncPtr",
	sizeof(CFuncPtrObject),			/* tp_basicsize */
	0,					/* tp_itemsize */
	(destructor)CFuncPtr_dealloc,		/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	0,					/* tp_compare */
	0,					/* tp_repr */
	0,					/* tp_as_number */
	0,					/* tp_as_sequence */
	0,					/* tp_as_mapping */
	0,					/* tp_hash */
	(ternaryfunc)CFuncPtr_call,		/* tp_call */
	0,					/* tp_str */
	0,					/* tp_getattro */
	0,					/* tp_setattro */
	&CData_as_buffer,			/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
	"Function Pointer",			/* tp_doc */
	(traverseproc)CFuncPtr_traverse,	/* tp_traverse */
	(inquiry)CFuncPtr_clear,		/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,					/* tp_iter */
	0,					/* tp_iternext */
	0,					/* tp_methods */
	0,					/* tp_members */
	CFuncPtr_getsets,			/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	0,					/* tp_init */
	0,					/* tp_alloc */
        CFuncPtr_new,				/* tp_new */
	0,					/* tp_free */
};

/*****************************************************************/
/*
  Struct_Type
*/
static int
IBUG(char *msg)
{
	PyErr_Format(PyExc_RuntimeError,
			"inconsistent state in CDataObject (%s)", msg);
	return -1;
}

static int
Struct_init(PyObject *self, PyObject *args, PyObject *kwds)
{
	int i;
	PyObject *fields;

/* Optimization possible: Store the attribute names _fields_[x][0]
 * in C accessible fields somewhere ?
 */

/* Check this code again for correctness! */

	if (!PyTuple_Check(args)) {
		PyErr_SetString(PyExc_TypeError,
				"args not a tuple?");
		return -1;
	}
	if (PyTuple_GET_SIZE(args)) {
		fields = PyObject_GetAttrString(self, "_fields_");
		if (!fields) {
			PyErr_Clear();
			fields = PyTuple_New(0);
		}

		if (PyTuple_GET_SIZE(args) > PySequence_Length(fields)) {
			Py_DECREF(fields);
			PyErr_SetString(PyExc_ValueError,
					"too many initializers");
			return -1;
		}

		for (i = 0; i < PyTuple_GET_SIZE(args); ++i) {
			PyObject *pair = PySequence_GetItem(fields, i);
			PyObject *name;
			PyObject *val;
			if (!pair) {
				Py_DECREF(fields);
				return IBUG("_fields_[i] failed");
			}

			name = PySequence_GetItem(pair, 0);
			if (!name) {
				Py_DECREF(fields);
				return IBUG("_fields_[i][0] failed");
			}

			val = PyTuple_GET_ITEM(args, i);
			if (-1 == PyObject_SetAttr(self, name, val)) {
				Py_DECREF(fields);
				return -1;
			}

			Py_DECREF(name);
			Py_DECREF(pair);
		}
		Py_DECREF(fields);
	}

	if (kwds) {
		PyObject *key, *value;
		int pos = 0;
		while(PyDict_Next(kwds, &pos, &key, &value)) {
			if (-1 == PyObject_SetAttr(self, key, value))
				return -1;
		}
	}
	return 0;
}

static PyTypeObject Struct_Type = {
	PyObject_HEAD_INIT(NULL)
	0,
	"_ctypes.Structure",
	0,					/* tp_basicsize */
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
	&CData_as_buffer,			/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
	"Structure base class",			/* tp_doc */
	(traverseproc)CData_traverse,		/* tp_traverse */
	(inquiry)CData_clear,			/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,					/* tp_iter */
	0,					/* tp_iternext */
	0,					/* tp_methods */
	0,					/* tp_members */
	0,					/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	Struct_init,				/* tp_init */
	0,					/* tp_alloc */
	GenericCData_new,			/* tp_new */
	0,					/* tp_free */
};

static PyTypeObject Union_Type = {
	PyObject_HEAD_INIT(NULL)
	0,
	"_ctypes.Union",
	0,					/* tp_basicsize */
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
	&CData_as_buffer,			/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
	"Union base class",			/* tp_doc */
	(traverseproc)CData_traverse,		/* tp_traverse */
	(inquiry)CData_clear,			/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,					/* tp_iter */
	0,					/* tp_iternext */
	0,					/* tp_methods */
	0,					/* tp_members */
	0,					/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	Struct_init,				/* tp_init */
	0,					/* tp_alloc */
	GenericCData_new,			/* tp_new */
	0,					/* tp_free */
};


/******************************************************************/
/*
  Array_Type
*/
static int
Array_init(CDataObject *self, PyObject *args, PyObject *kw)
{
	int i;
	int n;

	if (!PyTuple_Check(args)) {
		PyErr_SetString(PyExc_TypeError,
				"args not a tuple?");
		return -1;
	}
	n = PyTuple_GET_SIZE(args);
	for (i = 0; i < n; ++i) {
		PyObject *v;
		v = PyTuple_GET_ITEM(args, i);
		if (-1 == PySequence_SetItem((PyObject *)self, i, v))
			return -1;
	}
	return 0;
}

static PyObject *
Array_item(CDataObject *self, int index)
{
	PyObject *itemtype;
	StgDictObject *stgdict;

	if (index < 0 || index >= self->b_length) {
		PyErr_SetString(PyExc_IndexError,
				"invalid index");
		return NULL;
	}

	stgdict = PyObject_stgdict((PyObject *)self);
	itemtype = stgdict->itemtype;
	stgdict = PyType_stgdict(itemtype);

	return stgdict->getfunc(self->b_ptr + stgdict->size * index, stgdict->size,
				itemtype, self, index);
}

static PyObject *
Array_slice(CDataObject *self, int ilow, int ihigh)
{
	StgDictObject *stgdict;
	PyListObject *np;
	int i, len;

	if (ilow < 0)
		ilow = 0;
	else if (ilow > self->b_length)
		ilow = self->b_length;
	if (ihigh < ilow)
		ihigh = ilow;
	else if (ihigh > self->b_length)
		ihigh = self->b_length;
	len = ihigh - ilow;

	stgdict = PyObject_stgdict((PyObject *)self);
	if (stgdict->itemtype == CTYPE_c_char) {
		char *ptr = (char *)self->b_ptr;
		return PyString_FromStringAndSize(ptr + ilow, len);
#ifdef CTYPES_UNICODE
	} else if (stgdict->itemtype == CTYPE_c_wchar) {
		wchar_t *ptr = (wchar_t *)self->b_ptr;
		return PyUnicode_FromWideChar(ptr + ilow, len);
#endif
	}

	np = (PyListObject *) PyList_New(len);
	if (np == NULL)
		return NULL;

	for (i = 0; i < len; i++) {
		PyObject *v = Array_item(self, i+ilow);
		PyList_SET_ITEM(np, i, v);
	}
	return (PyObject *)np;
}

static int
Array_ass_item(CDataObject *self, int index, PyObject *value)
{
	int size, offset;
	StgDictObject *stgdict;
	PyObject *keep;

	if (value == NULL) {
		PyErr_SetString(PyExc_TypeError,
				"Array does not support item deletion");
		return -1;
	}
	
	stgdict = PyObject_stgdict((PyObject *)self);
	if (index < 0 || index >= stgdict->length) {
		PyErr_SetString(PyExc_IndexError,
				"invalid index");
		return -1;
	}
	size = stgdict->size / stgdict->length;
	offset = index * size;

	keep = _CData_set(self->b_ptr + offset, value, size, stgdict->itemtype);
	if (keep == NULL)
		return -1;
	return KeepRef(self, index, keep);
}

static int
Array_ass_slice(CDataObject *self, int ilow, int ihigh, PyObject *value)
{
	int i, len;

	if (value == NULL) {
		PyErr_SetString(PyExc_TypeError,
				"Array does not support item deletion");
		return -1;
	}

	if (ilow < 0)
		ilow = 0;
	else if (ilow > self->b_length)
		ilow = self->b_length;
	if (ihigh < 0)
		ihigh = 0;
	if (ihigh < ilow)
		ihigh = ilow;
	else if (ihigh > self->b_length)
		ihigh = self->b_length;

	len = PySequence_Length(value);
	if (len != ihigh - ilow) {
		PyErr_SetString(PyExc_ValueError,
				"Can only assign sequence of same size");
		return -1;
	}
	for (i = 0; i < len; i++) {
		PyObject *item = PySequence_GetItem(value, i);
		int result;
		if (item == NULL)
			return -1;
		result = Array_ass_item(self, i+ilow, item);
		Py_DECREF(item);
		if (result == -1)
			return -1;
	}
	return 0;
}

static int
Array_length(CDataObject *self)
{
	return self->b_length;
}

static PySequenceMethods Array_as_sequence = {
	(inquiry)Array_length,			/* sq_length; */
	0,					/* sq_concat; */
	0,					/* sq_repeat; */
	(intargfunc)Array_item,			/* sq_item; */
	(intintargfunc)Array_slice,		/* sq_slice; */
	(intobjargproc)Array_ass_item,		/* sq_ass_item; */
	(intintobjargproc)Array_ass_slice,	/* sq_ass_slice; */
	0,					/* sq_contains; */
	
	0,					/* sq_inplace_concat; */
	0,					/* sq_inplace_repeat; */
};

PyTypeObject Array_Type = {
	PyObject_HEAD_INIT(NULL)
	0,
	"_ctypes.Array",
	sizeof(CDataObject),			/* tp_basicsize */
	0,					/* tp_itemsize */
	0,					/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	0,					/* tp_compare */
	0,					/* tp_repr */
	0,					/* tp_as_number */
	&Array_as_sequence,			/* tp_as_sequence */
	0,					/* tp_as_mapping */
	0,					/* tp_hash */
	0,					/* tp_call */
	0,					/* tp_str */
	0,					/* tp_getattro */
	0,					/* tp_setattro */
	&CData_as_buffer,			/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
	"XXX to be provided",			/* tp_doc */
	(traverseproc)CData_traverse,		/* tp_traverse */
	(inquiry)CData_clear,			/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,					/* tp_iter */
	0,					/* tp_iternext */
	0,					/* tp_methods */
	0,					/* tp_members */
	0,					/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	(initproc)Array_init,			/* tp_init */
	0,					/* tp_alloc */
        GenericCData_new,			/* tp_new */
	0,					/* tp_free */
};

PyObject *
CreateArrayType(PyObject *itemtype, int length)
{
	static PyObject *cache;
	PyObject *key;
	PyObject *result;
	char name[256];

	if (cache == NULL) {
		cache = PyDict_New();
		if (cache == NULL)
			return NULL;
	}
	key = Py_BuildValue("(Oi)", itemtype, length);
	if (!key)
		return NULL;
	result = PyDict_GetItem(cache, key);
	if (result) {
		Py_INCREF(result);
		Py_DECREF(key);
		return result;
	}

	if (!PyType_Check(itemtype)) {
		PyErr_SetString(PyExc_TypeError,
				"Expected a type object");
		return NULL;
	}
	sprintf(name, "%.200s_Array_%d",
		((PyTypeObject *)itemtype)->tp_name, length);

	result = PyObject_CallFunction((PyObject *)&ArrayType_Type,
				       "s(O){s:i,s:O}",
				       name,
				       &Array_Type,
				       "_length_",
				       length,
				       "_type_",
				       itemtype
		);
	if (!result)
		return NULL;
	PyDict_SetItem(cache, key, result);
	Py_DECREF(key);
	return result;
}


/******************************************************************/
/*
  Simple_Type
*/

static int
Simple_set_value(CDataObject *self, PyObject *value)
{
	PyObject *result;
	StgDictObject *dict = PyObject_stgdict((PyObject *)self);

	result = dict->setfunc(self->b_ptr, value, dict->size, (PyObject *)self->ob_type);
	if (!result)
		return -1;

	/* consumes the refcount the setfunc returns */
	return KeepRef(self, 0, result);
}

static int
Simple_init(CDataObject *self, PyObject *args, PyObject *kw)
{
	switch (PyTuple_Size(args)) {
	case 0:
		return 0;
	case 1:
		return Simple_set_value(self, PyTuple_GET_ITEM(args, 0));
	default:
		PyErr_SetString(PyExc_TypeError,
				"function takes at most 1 argument");
		return -1;
	}
}

static PyObject *
Simple_get_value(CDataObject *self)
{
	StgDictObject *dict = PyObject_stgdict((PyObject *)self);
	return dict->getfunc(self->b_ptr, self->b_size,
			     (PyObject *)self->ob_type, self, 0);
}

static PyGetSetDef Simple_getsets[] = {
	{ "value", (getter)Simple_get_value, (setter)Simple_set_value,
	  "current value", NULL },
	{ NULL, NULL }
};

static PyTypeObject Simple_Type = {
	PyObject_HEAD_INIT(NULL)
	0,
	"_ctypes._SimpleCData",
	sizeof(CDataObject),			/* tp_basicsize */
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
	&CData_as_buffer,			/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
	"XXX to be provided",			/* tp_doc */
	(traverseproc)CData_traverse,		/* tp_traverse */
	(inquiry)CData_clear,			/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,					/* tp_iter */
	0,					/* tp_iternext */
	0,					/* tp_methods */
	0,					/* tp_members */
	Simple_getsets,				/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	(initproc)Simple_init,			/* tp_init */
	0,					/* tp_alloc */
        GenericCData_new,			/* tp_new */
	0,					/* tp_free */
};

/******************************************************************/
/*
  Pointer_Type
*/
static PyObject *
Pointer_item(CDataObject *self, int index)
{
	int size, offset;
	StgDictObject *stgdict, *itemdict;
	CDataObject *base;
	PyObject *proto;

	if (*(void **)self->b_ptr == NULL) {
		PyErr_SetString(PyExc_ValueError,
				"NULL pointer access");
		return NULL;
	}


	stgdict = PyObject_stgdict((PyObject *)self);
	assert(stgdict);
	
	proto = stgdict->itemtype;
	itemdict = PyType_stgdict(proto);
	size = itemdict->size;
	offset = index * itemdict->size;

	/* XXX explain! */
	if (index != 0)
		base = NULL;
	else
		base = self;

	/* XXX There MUST be some types which doen't have a getfunc, so this
	   cannot be correct.
	   Was calling CData_get before...
	*/
	return itemdict->getfunc((*(char **)self->b_ptr) + offset, size,
				 proto, base, index);
}

static int
Pointer_ass_item(CDataObject *self, int index, PyObject *value)
{
	int size;
	StgDictObject *stgdict;
	PyObject *keep;

	if (value == NULL) {
		PyErr_SetString(PyExc_TypeError,
				"Pointer does not support item deletion");
		return -1;
	}

	if (*(void **)self->b_ptr == NULL) {
		PyErr_SetString(PyExc_ValueError,
				"NULL pointer access");
		return -1;
	}
	
	stgdict = PyObject_stgdict((PyObject *)self);
	if (index != 0) {
		PyErr_SetString(PyExc_IndexError,
				"invalid index");
		return -1;
	}
	size = stgdict->size / stgdict->length;

	keep = _CData_set(*(void **)self->b_ptr, value, size, stgdict->itemtype);
	if (keep == NULL)
		return -1;
	return KeepRef(self, index, keep);
}

static PyObject *
Pointer_get_contents(CDataObject *self, void *closure)
{
	StgDictObject *stgdict;

	if (*(void **)self->b_ptr == NULL) {
		PyErr_SetString(PyExc_ValueError,
				"NULL pointer access");
		return NULL;
	}

	stgdict = PyObject_stgdict((PyObject *)self);
	assert(stgdict);
	return CData_FromBaseObj(stgdict->itemtype,
				   (PyObject *)self, 0,
				   *(void **)self->b_ptr);
}

static int
Pointer_set_contents(CDataObject *self, PyObject *value, void *closure)
{
	StgDictObject *stgdict;
	CDataObject *dst;
	PyObject *keep;

	if (value == NULL) {
		PyErr_SetString(PyExc_TypeError,
				"Pointer does not support item deletion");
		return -1;
	}
	stgdict = PyObject_stgdict((PyObject *)self);
	if (!CDataObject_Check(value) 
	    || 0 == PyObject_IsInstance(value, stgdict->itemtype)) {
		/* XXX PyObject_IsInstance could return -1! */
		PyErr_Format(PyExc_TypeError,
			     "expected %s instead of %s",
			     ((PyTypeObject *)(stgdict->itemtype))->tp_name,
			     value->ob_type->tp_name);
		return -1;
	}

	dst = (CDataObject *)value;
	*(void **)self->b_ptr = dst->b_ptr;

	/* 
	   A Pointer instance must keep a the value it points to alive.  So, a
	   pointer instance has b_length set to 2 instead of 1, and we set
	   'value' itself as the second item of the b_objects list, additionally.
	*/
	Py_INCREF(value);
	if (-1 == KeepRef(self, 1, value))
		return -1;

	keep = GetKeepedObjects(dst);
	Py_INCREF(keep);
	return KeepRef(self, 0, keep);
}

static PyGetSetDef Pointer_getsets[] = {
	{ "contents", (getter)Pointer_get_contents,
	  (setter)Pointer_set_contents,
	  "the object this pointer points to (read-write)", NULL },
	{ NULL, NULL }
};

static int
Pointer_init(CDataObject *self, PyObject *args, PyObject *kw)
{
	PyObject *value = NULL;

	if (!PyArg_ParseTuple(args, "|O", &value))
		return -1;
	if (value == NULL)
		return 0;
	return Pointer_set_contents(self, value, NULL);
}

static PyObject *
Pointer_new(PyTypeObject *type, PyObject *args, PyObject *kw)
{
	if (!PyType_stgdict((PyObject *)type)) {
		PyErr_SetString(PyExc_RuntimeError,
				"Cannot create instances: has no _type_");
		return NULL;
	}
	return GenericCData_new(type, args, kw);
}

static PyObject *
Pointer_slice(CDataObject *self, int ilow, int ihigh)
{
	PyListObject *np;
	StgDictObject *stgdict;
	int i, len;

	if (ilow < 0)
		ilow = 0;
	if (ihigh < ilow)
		ihigh = ilow;
	len = ihigh - ilow;

	stgdict = PyObject_stgdict((PyObject *)self);
	if (stgdict->itemtype == CTYPE_c_char) {
		char *ptr = *(char **)self->b_ptr;
		return PyString_FromStringAndSize(ptr + ilow, len);
#ifdef CTYPES_UNICODE
	} else if (stgdict->itemtype == CTYPE_c_wchar) {
		wchar_t *ptr = *(wchar_t **)self->b_ptr;
		return PyUnicode_FromWideChar(ptr + ilow, len);
#endif
	}

	np = (PyListObject *) PyList_New(len);
	if (np == NULL)
		return NULL;

	for (i = 0; i < len; i++) {
		PyObject *v = Pointer_item(self, i+ilow);
		PyList_SET_ITEM(np, i, v);
	}
	return (PyObject *)np;
}

static PySequenceMethods Pointer_as_sequence = {
	0,					/* inquiry sq_length; */
	0,					/* binaryfunc sq_concat; */
	0,					/* intargfunc sq_repeat; */
	(intargfunc)Pointer_item,		/* intargfunc sq_item; */
	(intintargfunc)Pointer_slice,		/* intintargfunc sq_slice; */
	(intobjargproc)Pointer_ass_item,	/* intobjargproc sq_ass_item; */
	0,					/* intintobjargproc sq_ass_slice; */
	0,					/* objobjproc sq_contains; */
	/* Added in release 2.0 */
	0,					/* binaryfunc sq_inplace_concat; */
	0,					/* intargfunc sq_inplace_repeat; */
};

static int
Pointer_nonzero(CDataObject *self)
{
	return *(void **)self->b_ptr != NULL;
}

static PyNumberMethods Pointer_as_number = {
	0, /* nb_add */
	0, /* nb_subtract */
	0, /* nb_multiply */
	0, /* nb_divide */
	0, /* nb_remainder */
	0, /* nb_divmod */
	0, /* nb_power */
	0, /* nb_negative */
	0, /* nb_positive */
	0, /* nb_absolute */
	(inquiry)Pointer_nonzero, /* nb_nonzero */
};

PyTypeObject Pointer_Type = {
	PyObject_HEAD_INIT(NULL)
	0,
	"_ctypes._Pointer",
	sizeof(CDataObject),			/* tp_basicsize */
	0,					/* tp_itemsize */
	0,					/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	0,					/* tp_compare */
	0,					/* tp_repr */
	&Pointer_as_number,			/* tp_as_number */
	&Pointer_as_sequence,			/* tp_as_sequence */
	0,					/* tp_as_mapping */
	0,					/* tp_hash */
	0,					/* tp_call */
	0,					/* tp_str */
	0,					/* tp_getattro */
	0,					/* tp_setattro */
	&CData_as_buffer,			/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
	"XXX to be provided",			/* tp_doc */
	(traverseproc)CData_traverse,		/* tp_traverse */
	(inquiry)CData_clear,			/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,					/* tp_iter */
	0,					/* tp_iternext */
	0,					/* tp_methods */
	0,					/* tp_members */
	Pointer_getsets,			/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	(initproc)Pointer_init,			/* tp_init */
	0,					/* tp_alloc */
	Pointer_new,				/* tp_new */
	0,					/* tp_free */
};


/******************************************************************/
/*
 *  Module initialization.
 */

static char *module_docs =
"Create and manipulate C compatible data types in Python.";

DL_EXPORT(void)
init_ctypes(void)
{
	PyObject *m;

/* Note:
   ob_type is the metatype (the 'type'), defaults to PyType_Type,
   tp_base is the base type, defaults to 'object' aka PyBaseObject_Type.
*/
	PyEval_InitThreads();
	m = Py_InitModule3("_ctypes", module_methods, module_docs);
	if (!m)
		return;

	if (PyType_Ready(&PyCArg_Type) < 0)
		return;

	/* StgDict is derived from PyDict_Type */
	StgDict_Type.tp_base = &PyDict_Type;
	if (PyType_Ready(&StgDict_Type) < 0)
		return;

	/*************************************************
	 *
	 * Metaclasses
	 */

	StructType_Type.tp_base = &PyType_Type;
	if (PyType_Ready(&StructType_Type) < 0)
		return;

	UnionType_Type.tp_base = &PyType_Type;
	if (PyType_Ready(&UnionType_Type) < 0)
		return;

	PointerType_Type.tp_base = &PyType_Type;
	if (PyType_Ready(&PointerType_Type) < 0)
		return;

	ArrayType_Type.tp_base = &PyType_Type;
	if (PyType_Ready(&ArrayType_Type) < 0)
		return;

	SimpleType_Type.tp_base = &PyType_Type;
	if (PyType_Ready(&SimpleType_Type) < 0)
		return;

	CFuncPtrType_Type.tp_base = &PyType_Type;
	if (PyType_Ready(&CFuncPtrType_Type) < 0)
		return;

	/*************************************************
	 *
	 * Classes using a custom metaclass
	 */

	if (PyType_Ready(&CData_Type) < 0)
		return;

	Struct_Type.ob_type = &StructType_Type;
	Struct_Type.tp_base = &CData_Type;
	if (PyType_Ready(&Struct_Type) < 0)
		return;
	PyModule_AddObject(m, "Structure", (PyObject *)&Struct_Type);

	Union_Type.ob_type = &UnionType_Type;
	Union_Type.tp_base = &CData_Type;
	if (PyType_Ready(&Union_Type) < 0)
		return;
	PyModule_AddObject(m, "Union", (PyObject *)&Union_Type);

	Pointer_Type.ob_type = &PointerType_Type;
	Pointer_Type.tp_base = &CData_Type;
	if (PyType_Ready(&Pointer_Type) < 0)
		return;
	PyModule_AddObject(m, "_Pointer", (PyObject *)&Pointer_Type);

	Array_Type.ob_type = &ArrayType_Type;
	Array_Type.tp_base = &CData_Type;
	if (PyType_Ready(&Array_Type) < 0)
		return;
	PyModule_AddObject(m, "Array", (PyObject *)&Array_Type);

	Simple_Type.ob_type = &SimpleType_Type;
	Simple_Type.tp_base = &CData_Type;
	if (PyType_Ready(&Simple_Type) < 0)
		return;
	PyModule_AddObject(m, "_SimpleCData", (PyObject *)&Simple_Type);

	CFuncPtr_Type.ob_type = &CFuncPtrType_Type;
	CFuncPtr_Type.tp_base = &CData_Type;
	if (PyType_Ready(&CFuncPtr_Type) < 0)
		return;
	PyModule_AddObject(m, "CFuncPtr", (PyObject *)&CFuncPtr_Type);

	/*************************************************
	 *
	 * Simple classes
	 */

	/* CField_Type is derived from PyBaseObject_Type */
	if (PyType_Ready(&CField_Type) < 0)
		return;

	/*************************************************
	 *
	 * Other stuff
	 */

#ifdef MS_WIN32
	PyModule_AddObject(m, "FUNCFLAG_HRESULT", PyInt_FromLong(FUNCFLAG_HRESULT));
	PyModule_AddObject(m, "FUNCFLAG_STDCALL", PyInt_FromLong(FUNCFLAG_STDCALL));
#endif
	PyModule_AddObject(m, "FUNCFLAG_CDECL", PyInt_FromLong(FUNCFLAG_CDECL));
	PyModule_AddObject(m, "FUNCFLAG_PYTHONAPI", PyInt_FromLong(FUNCFLAG_PYTHONAPI));
	PyModule_AddStringConstant(m, "__version__", "2.0.0.0cvs");
	
	PyExc_ArgError = PyErr_NewException("ctypes.ArgumentError", NULL, NULL);
	if (PyExc_ArgError) {
		Py_INCREF(PyExc_ArgError);
		PyModule_AddObject(m, "ArgumentError", PyExc_ArgError);
	}
	/*************************************************
	 *
	 * Others...
	 */
	init_callbacks_in_module(m);
}

/*****************************************************************
 * replacements for broken Python api functions
 */

#ifdef HAVE_WCHAR_H

PyObject *My_PyUnicode_FromWideChar(register const wchar_t *w,
				    int size)
{
    PyUnicodeObject *unicode;

    if (w == NULL) {
	PyErr_BadInternalCall();
	return NULL;
    }

    unicode = (PyUnicodeObject *)PyUnicode_FromUnicode(NULL, size);
    if (!unicode)
        return NULL;

    /* Copy the wchar_t data into the new object */
#ifdef HAVE_USABLE_WCHAR_T
    memcpy(unicode->str, w, size * sizeof(wchar_t));
#else
    {
	register Py_UNICODE *u;
	register int i;
	u = PyUnicode_AS_UNICODE(unicode);
	/* In Python, the following line has a one-off error */
	for (i = size; i > 0; i--)
	    *u++ = *w++;
    }
#endif

    return (PyObject *)unicode;
}

int My_PyUnicode_AsWideChar(PyUnicodeObject *unicode,
			    register wchar_t *w,
			    int size)
{
    if (unicode == NULL) {
	PyErr_BadInternalCall();
	return -1;
    }
    if (size > PyUnicode_GET_SIZE(unicode))
	size = PyUnicode_GET_SIZE(unicode);
#ifdef HAVE_USABLE_WCHAR_T
    memcpy(w, unicode->str, size * sizeof(wchar_t));
#else
    {
	register Py_UNICODE *u;
	register int i;
	u = PyUnicode_AS_UNICODE(unicode);
	/* In Python, the following line has a one-off error */
	for (i = size; i > 0; i--)
	    *w++ = *u++;
    }
#endif

    return size;
}

#endif

/*
 Local Variables:
 compile-command: "cd .. && python setup.py -q build -g && python setup.py -q build install --home ~"
 End:
*/
