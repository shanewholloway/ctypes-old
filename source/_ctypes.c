/*
 * $Id$
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
  Pointer_Type		__new__(), __init__(), _as_parameter_, contents
  Array_Type		__new__(), __init__(), _as_parameter_, __get/setitem__(), __len__()
  Simple_Type		__new__(), __init__(), _as_parameter_

  CString_Type class	from_param()
  CString_Type		__new__(), __init__(), _as_parameter_, raw, value
  CWString_Type		_as_parameter_, raw, value

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

_as_parameter_
	- convert self into a C function call parameter
	  This is either an integer, or a 3-tuple (typecode, value, obj)

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
 * CString_Type
 * CField_Type
 *
 */

#include "Python.h"
#include "structmember.h"
#include "ctypes.h"

#ifdef MS_WIN32
#include <windows.h>
#else
#include <dlfcn.h>
#endif

#ifndef METH_CLASS
#define METH_CLASS 0x0010 /* from Python 2.3 */
#define NO_METH_CLASS
#endif



/******************************************************************/
/*
  StructType_Type - a meta type/class.  Creating a new class using this one as
  __metaclass__ will call the contructor CDataType_new.  CDataType_new
  replaces the tp_dict member with a new instance of StgDict, and initializes
  the C accessible fields somehow.
*/

static PyObject *
CDataType_new(PyTypeObject *type, PyObject *args, PyObject *kwds, int isStruct)
{
	PyTypeObject *result;
	PyObject *fields, *dict;
	PyObject *cls_dict;
	PyObject *isPacked;
	int pack = 0;

	cls_dict = PyTuple_GetItem(args, 2); /* borrowed ref */
	if (!cls_dict) {
		/* Hm. Should not be possible, but who knows. */
		PyErr_SetString(PyExc_ValueError,
				"class creation without class dict?");
		return NULL;
	}
	/* create the new instance (which is a class,
	   since we are a metatype!) */
	result = (PyTypeObject *)PyType_Type.tp_new(type, args, kwds);
	if (!result)
		return NULL;

	/* If we find an _abstract_ item in the class dict,
	   don't equip this class with a StgDict. 
	   The resulting class will not be able to create
	   instances.
	   The value of the _abstract_ item is ignored.
	*/

	if (PyDict_GetItemString(cls_dict, "_abstract_"))
		return (PyObject *)result;

	isPacked = PyDict_GetItemString(cls_dict, "_pack_");
	if (isPacked) {
		pack = PyInt_AsLong(isPacked);
		if (pack < 0 || PyErr_Occurred()) {
			PyErr_SetString(PyExc_ValueError,
					"_pack_ must be a non-negative integer");
			Py_DECREF(result);
			return NULL;
		}
	}

	fields = PyObject_GetAttrString((PyObject *)result, "_fields_");
	dict = StgDict_FromDict(fields, cls_dict, isStruct, pack);
	Py_XDECREF(fields);
	if (!dict) {
		Py_DECREF(result);
		return NULL;
	}

	/* replace the class dict by our updated stgdict, which holds info
	   about storage requirements of the instances */
	if (-1 == PyDict_Update(dict, result->tp_dict)) {
		Py_DECREF(result);
		Py_DECREF(dict);
		return NULL;
	}
	Py_DECREF(result->tp_dict);
	result->tp_dict = dict;

	return (PyObject *)result;
}

static PyObject *
StructType_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	return CDataType_new(type, args, kwds, 1);
}

static PyObject *
UnionType_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	return CDataType_new(type, args, kwds, 0);
}

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

static char from_param_doc[] =
"Convert a Python object into a function call parameter.";

static PyObject *
CDataType_from_param(PyObject *type, PyObject *value)
{
	if (1 == PyObject_IsInstance(value, type)) {
		Py_INCREF(value);
		return value;
	}
	if (PyCArg_CheckExact(value)) {
		PyCArgObject *p = (PyCArgObject *)value;
		PyObject *ob = p->obj;
		StgDictObject *dict;
		dict = PyType_stgdict(type);

		/* If we got a PyCArgObject, we must check if the object packed in it
		   is an instance of the type's dict->proto */
//		if(dict && ob && dict->proto == (PyObject *)ob->ob_type){
		if(dict && ob
		   && PyObject_IsInstance(ob, dict->proto)) {
			Py_INCREF(value);
			return value;
		}
	}
#if 1
/* XXX Remove this section ??? */
	/* tuple returned by byref: */
	/* ('i', addr, obj) */
	if (PyTuple_Check(value)) {
		PyObject *ob;
		StgDictObject *dict;

		dict = PyType_stgdict(type);
		ob = PyTuple_GetItem(value, 2);
		if (dict && ob &&
		    0 == PyObject_IsInstance(value, dict->proto)) {
			Py_INCREF(value);
			return value;
		}
	}
/* ... and leave the rest */
#endif
	PyErr_Format(PyExc_TypeError,
		     "expected %s instance instead of %s",
		     ((PyTypeObject *)type)->tp_name,
		     value->ob_type->tp_name);
	return NULL;
}

static PyMethodDef CDataType_methods[] = {
	{ "from_param", CDataType_from_param, METH_O,
	  from_param_doc },
	{ "from_address", CDataType_from_address, METH_O,
	  "create an instance from an address"},
	{ NULL, NULL },
};

/* XXX This should probably use a cache! */
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


static PyTypeObject StructType_Type = {
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
	&CDataType_as_sequence,		/* tp_as_sequence */
	0,					/* tp_as_mapping */
	0,					/* tp_hash */
	0,					/* tp_call */
	0,					/* tp_str */
	0,					/* tp_getattro */
	0,					/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
	"metatype for the CData Objects",	/* tp_doc */
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
	0,					/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
	"metatype for the CData Objects",	/* tp_doc */
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
	stgdict->proto = proto;
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
	stgdict->align = getentry("P")->align;
	stgdict->length = 1;

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
	if (value == Py_None)
		return PyInt_FromLong(0); /* NULL pointer */

	if (ArrayObject_Check(value)) {
		/* Array instances are also pointers when
		   the item types are the same.
		*/
		StgDictObject *v = PyObject_stgdict(value);
		StgDictObject *t = PyType_stgdict(type);
		if (v && t && v->proto == t->proto) {
			Py_INCREF(value);
			return value;
		}
	}
     	return CDataType_from_param(type, value);
}

static PyMethodDef PointerType_methods[] = {
	{ "from_address", CDataType_from_address, METH_O,
	  "create an instance from an address"},
	{ "from_param", (PyCFunction)PointerType_from_param, METH_O,
	  from_param_doc},
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
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
	"metatype for the Pointer Objects",	/* tp_doc */
	0,					/* tp_traverse */
	0,					/* tp_clear */
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
  ArrayType_Type
*/
/*

ArrayType_new ensures that the new Array subclass created has a _length_
attribute, and a _type_ attribute.

class IntArray10(Array):
    _type_ = "i"
    _size_ = 10

*/

static PyObject *
ArrayType_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	PyTypeObject *result;
	StgDictObject *stgdict;
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

	if (PyType_Check(proto)) {
		StgDictObject *dict;
		dict = PyType_stgdict(proto);
		if (!dict) {
			PyErr_SetString(PyExc_TypeError,
					"invalid type ???");
			Py_DECREF((PyObject *)stgdict);
			return NULL;
		}
		itemsize = dict->size;
		itemalign = dict->align;
		itemlen = dict->length;

		stgdict->size = itemsize * length;
		stgdict->align = itemalign;
		stgdict->length = length;
		Py_INCREF(proto);
		stgdict->proto = proto;
	} else if (PyString_Check(proto)) {
		int offset = 0;
		int align = 0;
		CFieldObject *field;

		itemsize = 0;
		field = (CFieldObject *)CField_FromDesc(proto, 0,
							&itemsize, &offset, &align, 0);
		if (!field) {
			Py_DECREF((PyObject *)stgdict);
			return NULL;
		}
		stgdict->size = itemsize * length;
		stgdict->align = align;
		stgdict->length = length;
		stgdict->setfunc = field->setfunc;
		stgdict->getfunc = field->getfunc;
		stgdict->proto = NULL;
	} else {
		PyErr_SetString(PyExc_TypeError,
				"_type_ does not define storage info");
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
/*
  SimpleType_Type
*/
/*

SimpleType_new ensures that the new Simple_Type subclass created has a valid
_type_ attribute.

*/

static char *SIMPLE_TYPE_CHARS = "cbBhHiIlLdfzZqQPX";

static PyObject *
SimpleType_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	PyTypeObject *result;
	StgDictObject *stgdict;
	PyObject *proto;
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
	if (!stgdict)
		return NULL;

	fmt = getentry(PyString_AS_STRING(proto));

	stgdict->align = fmt->align;
	stgdict->length = 1;
	stgdict->size = fmt->size;
	stgdict->setfunc = fmt->setfunc;
	stgdict->getfunc = fmt->getfunc;
	/* This consumes the refcount on proto which we have */
	stgdict->proto = proto;

	/* replace the class dict by our updated spam dict */
	if (-1 == PyDict_Update((PyObject *)stgdict, result->tp_dict)) {
		Py_DECREF(result);
		Py_DECREF((PyObject *)stgdict);
		return NULL;
	}
	Py_DECREF(result->tp_dict);
	result->tp_dict = (PyObject *)stgdict;
	return (PyObject *)result;
}

/*
 * This is a *class method*.
 * Convert a parameter into something that ConvParam can handle.
 *
 * This is either an instance of the requested type, a Python integer, or a
 * 'magic' 3-tuple.
 *
 * (These are somewhat related to Martin v. Loewis 'Enhanced Argument Tuples',
 * described in PEP 286.)
 *
 * The tuple must contain
 *
 * - a format character, currently 'ifdqc' are understood
 *   which will inform ConvParam about how to push the argument on the stack.
 *
 * - a corresponding Python object: i - integer, f - float, d - float,
 *   q - longlong, c - integer
 *
 * - any object which can be used to keep the original parameter alive
 *   as long as the tuple lives.
 */
static PyObject *
SimpleType_from_param(PyObject *type, PyObject *value)
{
	StgDictObject *dict;
	char *fmt;
	PyCArgObject *parg;
	struct fielddesc *fd;

	/* If the value is already an instance of the requested type,
	   we can use it as is */
	if (1 == PyObject_IsInstance(value, type)) {
		Py_INCREF(value);
		return value;
	}

	dict = PyType_stgdict(type);
	assert(dict);

	/* I think we can rely on this being a one-character string */
	fmt = PyString_AsString(dict->proto);
	assert(fmt);
	
	fd = getentry(fmt);
	assert(fd);
	
	parg = new_CArgObject();
	if (parg == NULL)
		return NULL;

	parg->tag = fmt[0];
	parg->obj = fd->setfunc(&parg->value, value, 0);
	if (parg->obj == NULL) {
		Py_DECREF(parg);
		return NULL;
	}
	return (PyObject *)parg;
}

static PyMethodDef SimpleType_methods[] = {
	{ "from_param", SimpleType_from_param, METH_O,
	  from_param_doc },
	{ "from_address", CDataType_from_address, METH_O,
	  "create an instance from an address"},
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
converters_from_argtypes(PyObject *ob, int *psize)
{
	PyObject *converters;
	int i;
	int nArgs;
	int nArgBytes;

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

	nArgBytes = 0;
	for (i = 0; i < nArgs; ++i) {
		PyObject *tp = PyTuple_GET_ITEM(ob, i);
		StgDictObject *dict = PyType_stgdict(tp);
		PyObject *cnv = PyObject_GetAttrString(tp, "from_param");
		if (!dict || !cnv)
			goto argtypes_error_1;
		nArgBytes += dict->size;
		PyTuple_SET_ITEM(converters, i, cnv);
	}
	Py_DECREF(ob);
	if (psize)
		*psize = nArgBytes;
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

	stgdict->align = getentry("P")->align;
	stgdict->length = 1;
	stgdict->size = sizeof(void *);
	stgdict->setfunc = NULL;
	stgdict->getfunc = NULL;

	ob = PyDict_GetItemString((PyObject *)stgdict, "_flags_");
	if (!ob || !PyInt_Check(ob)) {
		PyErr_SetString(PyExc_TypeError,
		    "class must define _flags_ which must be an integer");
		return -1;
	}
	stgdict->flags = PyInt_AS_LONG(ob);

	/* _argtypes_ is optional... */
	stgdict->nArgBytes = 0;
	ob = PyDict_GetItemString((PyObject *)stgdict, "_argtypes_");
	if (ob) {
		converters = converters_from_argtypes(ob, &stgdict->nArgBytes);
		if (!converters)
			goto error;
		Py_INCREF(ob);
		stgdict->argtypes = ob;
		stgdict->converters = converters;
	}

	ob = PyDict_GetItemString((PyObject *)stgdict, "_restype_");
	if (ob) {
		StgDictObject *dict = PyType_stgdict(ob);
		if (!dict && !PyCallable_Check(ob)) {
			PyErr_SetString(PyExc_TypeError,
				"_restype_ must be a type or callable");
			return -1;
		}
		Py_INCREF(ob);
		stgdict->restype = ob;
	}
	return 0;

  error:
	Py_XDECREF(converters);
	return -1;

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

	return (PyObject *)result;
}

static PyTypeObject CFuncPtrType_Type = {
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


/******************************************************************/
/*
  CData_Type
 */
struct basespec {
	CDataObject *base;
	int index;
	char *adr;
};

static char basespec_string[] = "base specification";

/*
 * Return a list of size <size> filled with None's.
 */
static PyObject *
RepeatedList(PyObject *ob, int size)
{
	int i;
	PyObject *list;

	list = PyList_New(size);
	if (!list)
		return NULL;
	for (i = 0; i < size; ++i) {
		Py_INCREF(ob);
		PyList_SET_ITEM(list, i, ob);
	}
	return list;
}

static PyObject *
NoneList(int size)
{
	return RepeatedList(Py_None, size);
}

#define ASSERT_CDATA(x) assert(((x)->b_base == NULL) ^ ((x)->b_objects == NULL))

/*
 * Return the list(tree) entry corresponding to a memory object.
 * Borrowed reference!
 */
PyObject *
CData_GetList(CDataObject *mem)
{
	PyObject *list;
	PyObject *obj;
	ASSERT_CDATA(mem);
	if (!mem->b_base) {
		return mem->b_objects;
	} else {
//		assert(mem->b_objects == NULL);
		list = CData_GetList(mem->b_base);
		if (list == NULL)
			return NULL;
		obj = PyList_GetItem(list, mem->b_index);
		if (obj == NULL)
			return NULL;
		if (obj == Py_None) {
			obj = NoneList(mem->b_length);
			if (-1 == PyList_SetItem(list, mem->b_index, obj))
				return NULL;
		}
		return obj;
	}
}

/*
 * Make sure object <mem> has a list of length <length>
 * at index <index>. Initially all list members are None.
 */
static int
CData_EnsureList(CDataObject *mem, int index, int length)
{
	PyObject *list;
	PyObject *obj;

	list = CData_GetList(mem);
	if (!list)
		return -1;
	obj = PyList_GetItem(list, index);
	if (!obj)
		return -1;

	if (obj == Py_None) {
		obj = NoneList(length);
		if (!obj)
			return -1;
		if (-1 == PyList_SetItem(list, index, obj))
			return -1;
	}
	return 0;
}


static void
CData_dealloc(PyObject *self)
{
	CDataObject *mem = (CDataObject *)self;

	if (mem->b_needsfree)
		PyMem_Free(mem->b_ptr);
	mem->b_ptr = NULL;
	Py_XDECREF(mem->b_base);
	Py_XDECREF(mem->b_objects);
	self->ob_type->tp_free(self);
}

static PyObject *
CData_objects(CDataObject *self)
{
	PyObject *result;

	result = CData_GetList(self);
	Py_INCREF(result);
	return result;
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
	0,					/* tp_traverse */
	0,					/* tp_clear */
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

/*
 * Trick #17: Pass a PyCObject named _basespec_ to the tp_new constructor,
 * then let tp_new remove it from the keyword dict, so that tp_init doesn't
 * get confused by it.
 *
 */

/*
 * If base is NULL, index is ignored, and baseofs is cast to a pointer
 * and used as the buffer of the new instance.
 *
 * If base is not NULL, it must be a CDataObject.
 * The new instance is a kind of 'slice' of the base object.
 * It shares base's pointer at offset baseofs, and uses index
 * in the base's object list to keep its references.
 *
 * In the latter case, the new instance shares the buffer of base.
 *
 * Box a memory block into a CData instance:
 *	CData_AtAddress(PyObject *type, void *buf);
 *
 * Create a CData instance as 'slice' of a base object:
 *	CData_FromBaseObj(PyObject *type, PyObject *base, int index, int baseofs);
 *
 */

static PyObject *
CData_FromBaseObj(PyObject *type, PyObject *base, int index, char *adr)
{
	struct basespec spec;
	PyObject *cobj;
	PyObject *mem;
	PyObject *args, *kw;
	CDataObject *cd;

	if (base && !CDataObject_Check(base)) {
		PyErr_SetString(PyExc_TypeError,
				"expected a ctype type");
		return NULL;
	}

	spec.base = (CDataObject *)base;
	spec.adr = adr;
	spec.index = index;
	cobj = PyCObject_FromVoidPtrAndDesc(&spec, basespec_string, NULL);
	kw = Py_BuildValue("{s:O}", "_basespec_", cobj);
	args = PyTuple_New(0);

	mem = PyObject_Call(type, args, kw);
	Py_DECREF(kw);
	Py_DECREF(args);
	if (mem == NULL)
		return NULL;
			    
	/* XXX cobj will be invalid once we leave this function! */
	assert(cobj->ob_refcnt == 1);
	Py_DECREF(cobj);

	cd = (CDataObject *)mem;

	ASSERT_CDATA(cd);

	return mem;
}

PyObject *
CData_AtAddress(PyObject *type, void *buf)
{
	return CData_FromBaseObj(type, NULL, 0, buf);
}

PyObject *
CData_get(PyObject *type, GETFUNC getfunc, PyObject *src,
	  int index, int size, char *adr)
{
	if (type) {
		StgDictObject *dict;
		dict = PyType_stgdict(type);
		if (dict)
			assert(size == dict->size);
		if (dict && dict->getfunc)
			return dict->getfunc(adr, dict->size);
		return CData_FromBaseObj(type, src, index, adr);
	}
	return getfunc(adr, size);
}

/*
  Helper function for CData_set below.
*/
static PyObject *
_CData_set(CDataObject *dst, PyObject *type, SETFUNC setfunc, PyObject *value,
	  int index, int size, char *ptr)
{
	CDataObject *src;
	PyObject *result;

	if (!type)
		return setfunc(ptr, value, size);
	
	if (!CDataObject_Check(value)) {
		StgDictObject *dict = PyType_stgdict(type);
		if (dict && dict->setfunc)
			return dict->setfunc(ptr,
					     value, dict->size); /* Or simply size? */
		PyErr_SetString(PyExc_TypeError,
				"cannot use this type");
		return NULL;
	}
	src = (CDataObject *)value;

	if (PyObject_IsInstance(value, type)) {
		memcpy(ptr,
		       src->b_ptr,
		       size);
		result = CData_GetList(src);
		Py_INCREF(result); /* reference to keep */
		return result;
	}

	if (PointerTypeObject_Check(type)
	    && ArrayObject_Check(value)) {
		StgDictObject *p1, *p2;
		p1 = PyObject_stgdict(value);
		p2 = PyType_stgdict(type);

		if (p1->proto != p2->proto) {
			PyErr_Format(PyExc_TypeError,
				     "incompatible types, %s instance instead of %s instance",
				     value->ob_type->tp_name,
				     ((PyTypeObject *)type)->tp_name);
			return NULL;
		}
		*(void **)ptr = src->b_ptr;
		result = CData_GetList(src);
		Py_XINCREF(result); /* reference to keep */
		return result;
	}
	PyErr_Format(PyExc_TypeError,
		     "incompatible types, %s instance instead of %s instance",
		     value->ob_type->tp_name,
		     ((PyTypeObject *)type)->tp_name);
	return NULL;
}

/*
 * Set a slice in object 'dst', which has the type 'type',
 * to the value 'value'.
 */
int
CData_set(PyObject *dst, PyObject *type, SETFUNC setfunc, PyObject *value,
	  int index, int size, char *ptr)
{
	CDataObject *mem = (CDataObject *)dst;
	PyObject *objects, *result;

	if (!CDataObject_Check(dst)) {
		PyErr_SetString(PyExc_TypeError,
				"not a ctype instance");
		return -1;
	}
	objects = CData_GetList(mem);
	if (!objects)
		return -1;

	result = _CData_set(mem, type, setfunc, value,
			    index, size, ptr);
	if (result == NULL)
		return -1;

	return PyList_SetItem(objects, index, result);
}


/******************************************************************/
static PyObject *
GenericCData_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	CDataObject *obj;
	PyObject *basespec = NULL;
	int size, align, length;
	StgDictObject *dict;

	dict = PyType_stgdict((PyObject *)type);
	if (!dict) {
		PyErr_SetString(PyExc_TypeError,
				"abstract class");
		return NULL;
	}
	size = dict->size;
	align = dict->align;
	length = dict->length;

	if (kwds)
		basespec = PyDict_GetItemString(kwds, "_basespec_");

	obj = (CDataObject *)type->tp_alloc(type, 0);
	if (!obj)
		return NULL;
	/* Three different cases:
	 * - no basespec object in kwds: Allocate new memory
	 * - basespec->base is set:
	 *	This is the base object owning the buffer,
	 *	index and offset must be set
	 * - basespec->base is NULL:
	 *	index is ignored, offset contains the buffer address to use.
	 */

	if (basespec) {
		struct basespec *spec;
		void *descr;

		descr = PyCObject_GetDesc(basespec);
		if (!descr) {
			Py_DECREF(obj);
			return NULL;
		}
		if (descr != basespec_string) {
			PyErr_SetString(PyExc_TypeError, "invalid object");
			Py_DECREF(obj);
			return NULL;
		}
		spec = PyCObject_AsVoidPtr(basespec);

		if (spec->base) {
			Py_INCREF(spec->base);
			obj->b_base = spec->base;
			obj->b_index = spec->index;
			obj->b_objects = NULL;
			obj->b_length = length;
			
			obj->b_ptr = spec->adr;
			obj->b_size = size;
			obj->b_needsfree = 0;
			if (-1 == CData_EnsureList(obj->b_base,
						    spec->index, length)) {
				Py_DECREF(obj);
				return NULL;
			}
		} else {
			obj->b_base = NULL;
			obj->b_index = 0;
			obj->b_objects = NoneList(length);
			obj->b_length = length;
			
			obj->b_ptr = spec->adr;
			obj->b_size = size;
			obj->b_needsfree = 0;
		}
		/* don't pass this to tp_init! */
		if (-1 == PyDict_DelItemString(kwds, "_basespec_")) {
			Py_DECREF(obj);
			return NULL;
		}

	} else {
		obj->b_base = NULL;
		obj->b_index = 0;

		/* 1.11 us in Python 2.3 -OO, 30% of total creation time for c_int() */
		/* 2.2 us in Pyton 2.2 -OO, ~20% of total creation time */
		/* Should we use an array of objects in the CDataObject structure
		   instead of the b_objects pointer pointing to a list? */
		obj->b_objects = NoneList(length);
		obj->b_length = length;

		/* 0.7 us in Python 2.3, 20 % of total creation time for c_int() */
		/* same ABSOLUTE time, but smaller percentage in Python 2.2 */
		/* We could save this time if the buffer in this case
		   would be part of the object already */
		obj->b_ptr = PyMem_Malloc(size);
		obj->b_size = size;
		obj->b_needsfree = 1;
		memset(obj->b_ptr, 0, size);
	}
	ASSERT_CDATA(obj);
	return (PyObject *)obj;
}
/*****************************************************************/
/*
  CFuncPtr_Type
*/

static PyObject *
CFuncPtr_as_parameter(CDataObject *self)
{
	PyCArgObject *parg;
	
	parg = new_CArgObject();
	if (parg == NULL)
		return NULL;
	
	parg->tag = 'P';
	Py_INCREF(self);
	parg->obj = (PyObject *)self;
	parg->value.p = *(void **)self->b_ptr;
	return (PyObject *)parg;	
}

static int
CFuncPtr_set_restype(CFuncPtrObject *self, PyObject *ob)
{
	StgDictObject *dict = PyType_stgdict(ob);
	if (!dict && !PyCallable_Check(ob)) {
		PyErr_SetString(PyExc_TypeError,
				"restype must be a type or callable");
		return -1;
	}
	Py_XDECREF(self->restype);
	Py_INCREF(ob);
	self->restype = ob;
	return 0;
}

static int
CFuncPtr_set_argtypes(CFuncPtrObject *self, PyObject *ob)
{
	PyObject *converters = converters_from_argtypes(ob, NULL);
	if (!converters)
		return -1;
	Py_XDECREF(self->converters);
	self->converters = converters;
	Py_XDECREF(self->argtypes);
	Py_INCREF(ob);
	self->argtypes = ob;
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
	{ "restype", NULL, (setter)CFuncPtr_set_restype,
	  "specify the result type", NULL },
	{ "argtypes", (getter)CFuncPtr_get_argtypes,
	  (setter)CFuncPtr_set_argtypes,
	  "specify the argument types", NULL },
	{ "_as_parameter_", (getter)CFuncPtr_as_parameter, NULL,
	  "return a magic value so that this can be converted to a C parameter (readonly)",
	  NULL },
	{ NULL, NULL }
};

static PyObject *
CFuncPtr_FromDll(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	char *name;
	int (* address)(void);
	PyObject *dll;
	PyObject *obj;
	CFuncPtrObject *self;
	void *handle;
	PyObject *objects;

	if (!PyArg_ParseTuple(args, "sO", &name, &dll))
		return NULL;

	obj = PyObject_GetAttrString(dll, "_handle");
	if (!obj)
		return NULL;
	if (!PyInt_Check(obj)) {
		Py_DECREF(obj);
		return NULL;
	}
	handle = (void *)PyInt_AS_LONG(obj);
	Py_DECREF(obj);

#ifdef MS_WIN32
	address = (PPROC)GetProcAddress(handle, name);
	if (!address) {
		PyErr_Format(PyExc_ValueError,
			     "function '%s' not found",
			     name);
		return NULL;
	}
#else
	address = (PPROC)dlsym(handle, name);
	if (!address) {
		PyErr_Format(PyExc_ValueError,
			     dlerror());
		return NULL;
	}
#endif
	self = (CFuncPtrObject *)GenericCData_new(type, args, kwds);
	if (!self)
		return NULL;

	*(void **)self->b_ptr = address;

	objects = CData_GetList((CDataObject *)self);
	if (!objects) {
		Py_DECREF((PyObject *)self);
		return NULL;
	}

	if (-1 == PyList_SetItem(objects, 0, dll)) {
		Py_DECREF((PyObject *)self);
		return NULL;
	}
	Py_INCREF((PyObject *)dll); /* for PyList_SetItem above */

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

	if (!PyArg_ParseTuple(args, "i", &index))
		return NULL;
	
	self = (CFuncPtrObject *)GenericCData_new(type, args, kwds);

	self->index = index + 0x1000;
	return (PyObject *)self;
}
#endif

static PyObject *
CFuncPtr_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	CFuncPtrObject *self;
	PyObject *callable;
	StgDictObject *dict;
	THUNK thunk;
	PyObject *objects; 

	if (kwds && PyDict_GetItemString(kwds, "_basespec_")) {
		return GenericCData_new(type, args, kwds);
	}

	if (2 == PyTuple_GET_SIZE(args))
		return CFuncPtr_FromDll(type, args, kwds);

#ifdef MS_WIN32
	if (1 == PyTuple_GET_SIZE(args) && PyInt_Check(PyTuple_GET_ITEM(args, 0)))
		return CFuncPtr_FromVtblIndex(type, args, kwds);
#endif

	if (!PyArg_ParseTuple(args, "O", &callable))
		return NULL;
	if (!PyCallable_Check(callable)) {
		PyErr_SetString(PyExc_TypeError,
				"argument must be callable");
		return NULL;
	}
	dict = PyType_stgdict((PyObject *)type);
	/* XXXX Fails if we do: 'CFuncPtr(lambda x: x)' */
	if (!dict || !dict->argtypes) {
		PyErr_SetString(PyExc_TypeError,
		       "cannot construct instance of this class:"
			" no argtypes");
		return NULL;
	}

	/*****************************************************************/
	/*
	  Thoughts:

	  1. The thunk should keep (and later free) references to callable and
	  argtypes itself.

	  2. The thunk should probably be wrapped up in a PyCObject, and then
	  stored in the _objects list.

	  3. We absolutely need GC support.

	*/
	/* The thunk keeps unowned references to callable and dict->argtypes
	   so we have to keep them alive somewhere else: callable is kept in self,
	   dict->argtypes is in the type's stgdict.
	*/
	thunk = AllocFunctionCallback(callable,
				      dict->nArgBytes,
				      dict->argtypes,
				      dict->flags & FUNCFLAG_CDECL);
	if (!thunk)
		return NULL;

	self = (CFuncPtrObject *)GenericCData_new(type, args, kwds);

	Py_INCREF(callable);
	self->callable = callable;

	self->thunk = thunk;
	*(void **)self->b_ptr = thunk;

	objects = CData_GetList((CDataObject *)self);
	if (!objects) {
		Py_DECREF((PyObject *)self);
		return NULL;
	}

	/* We store ourself in self->b_objects[0], because the whole instance
	   must be kept alive if stored in a structure field, for example.
	   Cycle GC to the rescue! And we have a unittest proving that this works
	   correctly...
	*/

	if (-1 == PyList_SetItem(objects, 0, (PyObject *)self)) {
		Py_DECREF((PyObject *)self);
		return NULL;
	}
	Py_INCREF((PyObject *)self); /* for PyList_SetItem above */

	return (PyObject *)self;
}

static PyObject *
CFuncPtr_call(CFuncPtrObject *self, PyObject *args, PyObject *kwds)
{
	PyObject *restype;
	PyObject *converters;
	StgDictObject *dict = PyObject_stgdict((PyObject *)self);
#ifdef MS_WIN32
	IUnknown *piunk = NULL;
	void *pProc;
#endif

	assert(dict); /* if not, it's a bug */
	restype = self->restype ? self->restype : dict->restype;
	converters = self->converters ? self->converters : dict->converters;

#ifdef MS_WIN32
	if (self->index) {
		CDataObject *this;
		this = (CDataObject *)PyTuple_GetItem(args, 0);
		if (!this || !CDataObject_Check(this)) {
			PyErr_SetString(PyExc_TypeError,
					"wrong type for this arg");
			return NULL;
		}
		/* there should be more checks? No, in Python*/
		/* First arg is an pointer to an interface instance */
		if (!this->b_ptr || *(void **)this->b_ptr == NULL) {
			PyErr_SetString(PyExc_ValueError,
					"NULL pointer access");
			return NULL;
		}
		piunk = *(IUnknown **)this->b_ptr;
		pProc = ((void **)piunk->lpVtbl)[self->index - 0x1000];
	}
#endif

	if (converters) {
		int required = PyTuple_GET_SIZE(converters);
		int actual = PyTuple_GET_SIZE(args);
#ifdef MS_WIN32
		if (piunk)
			required ++;
#endif
		if (required != actual) {
			PyErr_Format(PyExc_TypeError,
			     "this function takes %d argument%s (%d given)",
				     required,
				     required == 1 ? "" : "s",
				     actual);
			return NULL;
		}
	}
#ifdef MS_WIN32
	if (piunk) {
		PyObject *a = PyTuple_GetSlice(args, 1, PyTuple_GET_SIZE(args));
		PyObject *result;
		result = _CallProc(pProc,
				   a,
				   piunk,
				   dict->flags,
				   converters,
				   restype);
		Py_DECREF(a);
		return result;
	}
#endif
	return _CallProc(*(void **)self->b_ptr,
			 args,
			 NULL,
			 dict->flags,
			 converters,
			 restype);
}

static int
CFuncPtr_traverse(CFuncPtrObject *self, visitproc visit, void *arg)
{
	int err;

#define TRAVERSE(o) if(o) {err = visit(o, arg); if(err) return err;}

	TRAVERSE(self->callable)
	TRAVERSE(self->restype)
	TRAVERSE(self->argtypes)
	TRAVERSE(self->converters)
	TRAVERSE(self->b_objects)

#undef TRAVERSE

	return 0;
}


static int
CFuncPtr_clear(CFuncPtrObject *self)
{
	Py_XDECREF(self->callable);
	self->callable = NULL;

	Py_XDECREF(self->restype);
	self->restype = NULL;

	Py_XDECREF(self->argtypes);
	self->argtypes = NULL;

	Py_XDECREF(self->converters);
	self->converters = NULL;

	self->b_ptr = NULL;
	if (self->thunk)
		FreeCallback(self->thunk);
	self->thunk = NULL;

	Py_XDECREF(self->b_objects);
	self->b_objects = NULL;

	return 0;
}

static void
CFuncPtr_dealloc(CFuncPtrObject *self)
{
	CFuncPtr_clear(self);
	CData_dealloc((PyObject *)self);
}

static PyTypeObject CFuncPtr_Type = {
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

/* Hm. This is really Structure_init... */
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
	fields = PyObject_GetAttrString(self, "_fields_");
	if (!fields)
		return IBUG("no _fields_");

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
	0,					/* tp_traverse */
	0,					/* tp_clear */
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
	GenericCData_new,				/* tp_new */
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
	0,					/* tp_traverse */
	0,					/* tp_clear */
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
	GenericCData_new,				/* tp_new */
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
	int offset, size;
	StgDictObject *stgdict;

	if (index < 0 || index >= self->b_length) {
		PyErr_SetString(PyExc_IndexError,
				"invalid index");
		return NULL;
	}

	stgdict = PyObject_stgdict((PyObject *)self);
	assert(stgdict);
	size = stgdict->size / stgdict->length;
	offset = index * size;

	return CData_get(stgdict->proto, stgdict->getfunc, (PyObject *)self,
			 index, size, self->b_ptr + offset);
}

static int
Array_ass_item(CDataObject *self, int index, PyObject *value)
{
	int size, offset;
	StgDictObject *stgdict;
	char *ptr;

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
	ptr = self->b_ptr + offset;

	return CData_set((PyObject *)self, stgdict->proto, stgdict->setfunc, value,
			 index, size, ptr);
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
	0,					/* sq_slice; */
	(intobjargproc)Array_ass_item,		/* sq_ass_item; */
	0,					/* sq_ass_slice; */
	0,					/* sq_contains; */
	
	0,					/* sq_inplace_concat; */
	0,					/* sq_inplace_repeat; */
};

static PyObject *
Array_as_parameter(CDataObject *self)
{
	PyCArgObject *p = new_CArgObject();
	if (p == NULL)
		return NULL;
	p->tag = 'P';
	p->value.p = (char *)self->b_ptr;
	Py_INCREF(self);
	p->obj = (PyObject *)self;
	return (PyObject *)p;
}

static PyGetSetDef Array_getsets[] = {
	{ "_as_parameter_", (getter)Array_as_parameter,
	  (setter)NULL, "convert to a parameter", NULL },
	{ NULL },
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
	0,					/* tp_traverse */
	0,					/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,					/* tp_iter */
	0,					/* tp_iternext */
	0,					/* tp_methods */
	0,					/* tp_members */
	Array_getsets,				/* tp_getset */
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
	char name[256];

	if (!PyType_Check(itemtype)) {
		PyErr_SetString(PyExc_TypeError,
				"Expected a type object");
		return NULL;
	}
	sprintf(name, "%.200s_Array_%d",
		((PyTypeObject *)itemtype)->tp_name, length);

	return PyObject_CallFunction((PyObject *)&ArrayType_Type,
				     "s(O){s:i,s:O}",
				     name,
				     &Array_Type,
				     "_length_",
				     length,
				     "_type_",
				     itemtype
				     );
}


/******************************************************************/
/*
  Simple_Type
*/

static int
Simple_set_value(CDataObject *self, PyObject *value)
{
	PyObject *result;
	PyObject *objects;
	StgDictObject *dict = PyObject_stgdict((PyObject *)self);

	result = dict->setfunc(self->b_ptr, value, dict->size);
	if (!result)
		return -1;

	/* Keep the object alive */
	objects = CData_GetList(self);
	if (!objects)
		return -1; /* Hm. Severe bug. What now? Undo all the above? */
	/* setfunc returns a new reference, PyList_SetItem() consumes it */
	return PyList_SetItem(objects, 0, result); /* index is always 0 */
}

static int
Simple_init(CDataObject *self, PyObject *args, PyObject *kw)
{
	PyObject *value = NULL;

	/* XXX Optimize. PyArg_ParseTuple is slow... */
	if (!PyArg_ParseTuple(args, "|O", &value))
		return -1;

	if (value)
		return Simple_set_value(self, value);
	return 0;
}

static PyObject *
Simple_get_value(CDataObject *self)
{
	StgDictObject *dict = PyObject_stgdict((PyObject *)self);
	return dict->getfunc(self->b_ptr, self->b_size);
}

static PyObject *
Simple_as_parameter(CDataObject *self)
{
	StgDictObject *dict = PyObject_stgdict((PyObject *)self);
	char *fmt = PyString_AsString(dict->proto);
	PyCArgObject *parg;
	struct fielddesc *fd;
	
	fd = getentry(fmt);
	assert(fd);
	
	parg = new_CArgObject();
	if (parg == NULL)
		return NULL;
	
	parg->tag = fmt[0];
	Py_INCREF(self);
	parg->obj = (PyObject *)self;
	memcpy(&parg->value, self->b_ptr, self->b_size);
	return (PyObject *)parg;	
}

static PyGetSetDef Simple_getsets[] = {
	{ "value", (getter)Simple_get_value, (setter)Simple_set_value,
	  "current value", NULL },
	{ "_as_parameter_", (getter)Simple_as_parameter, NULL,
	  "return a magic value so that this can be converted to a C parameter (readonly)",
	  NULL },
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
	0,					/* tp_traverse */
	0,					/* tp_clear */
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
	PyObject *base;
	PyObject *proto;

	if (*(void **)self->b_ptr == NULL) {
		PyErr_SetString(PyExc_ValueError,
				"NULL pointer access");
		return NULL;
	}

	stgdict = PyObject_stgdict((PyObject *)self);
	assert(stgdict);
	
	proto = stgdict->proto;
	itemdict = PyType_stgdict(proto);
	size = itemdict->size;
	offset = index * itemdict->size;

	/* XXX explain! */
	if (index != 0)
		base = NULL;
	else
		base = (PyObject *)self;
	return CData_get(stgdict->proto, stgdict->getfunc, base,
			 index, size, (*(char **)self->b_ptr) + offset);
}

static int
Pointer_ass_item(CDataObject *self, int index, PyObject *value)
{
	int size;
	StgDictObject *stgdict;

	if (value == NULL) {
		PyErr_SetString(PyExc_TypeError,
				"Pointer does not support item deletion");
		return -1;
	}
	
	stgdict = PyObject_stgdict((PyObject *)self);
	if (index != 0) {
		PyErr_SetString(PyExc_IndexError,
				"invalid index");
		return -1;
	}
	size = stgdict->size / stgdict->length;

	return CData_set((PyObject *)self, stgdict->proto, stgdict->setfunc, value,
			 index, size, *(void **)self->b_ptr);
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
	return CData_FromBaseObj(stgdict->proto,
				   (PyObject *)self, 0,
				   *(void **)self->b_ptr);
}

static int
Pointer_set_contents(CDataObject *self, PyObject *value, void *closure)
{
	StgDictObject *stgdict;
	CDataObject *dst;
	PyObject *objects, *keep;

	if (value == NULL) {
		PyErr_SetString(PyExc_TypeError,
				"Pointer does not support item deletion");
		return -1;
	}
	stgdict = PyObject_stgdict((PyObject *)self);
	if (!CDataObject_Check(value) 
	    || 0 == PyObject_IsInstance(value, stgdict->proto)) {
		/* XXX PyObject_IsInstance could return -1! */
		PyErr_Format(PyExc_TypeError,
			     "expected %s instead of %s",
			     ((PyTypeObject *)(stgdict->proto))->tp_name,
			     value->ob_type->tp_name);
		return -1;
	}

	dst = (CDataObject *)value;
	*(void **)self->b_ptr = dst->b_ptr;

	objects = CData_GetList(self);
	keep = RepeatedList(value, PyList_GET_SIZE(CData_GetList(dst)));
	/* We need the whole (sub)tree of the object we point to.
	   But we need the object itself, too.
	*/
	/* XXX Explain why this works (to myself, at least) */
	/* XXX Need GC support to avoid immortal objects ? */
	return PyList_SetItem(objects, 0, keep);
}

static int
Pointer_length(CDataObject *self)
{
	return 1;
}

static PyObject *
Pointer_as_parameter(CDataObject *self)
{
	PyCArgObject *parg;

	parg = new_CArgObject();
	if (parg == NULL)
		return NULL;

	parg->tag = 'P';
	Py_INCREF(self);
	parg->obj = (PyObject *)self;
	parg->value.p = *(void **)self->b_ptr;
	return (PyObject *)parg;
}

static PyGetSetDef Pointer_getsets[] = {
	{ "contents", (getter)Pointer_get_contents,
	  (setter)Pointer_set_contents,
	  "the object this pointer points to (read-write)", NULL },
	{ "_as_parameter_", (getter)Pointer_as_parameter, NULL,
	  "return a magic value so that this can be converted to a C parameter (readonly)",
	  NULL },
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

static PySequenceMethods Pointer_as_sequence = {
	(inquiry)Pointer_length,		/* inquiry sq_length; */
	0,					/* binaryfunc sq_concat; */
	0,					/* intargfunc sq_repeat; */
	(intargfunc)Pointer_item,		/* intargfunc sq_item; */
	0,					/* intintargfunc sq_slice; */
	(intobjargproc)Pointer_ass_item,	/* intobjargproc sq_ass_item; */
	0,					/* intintobjargproc sq_ass_slice; */
	0,					/* objobjproc sq_contains; */
	/* Added in release 2.0 */
	0,			/* binaryfunc sq_inplace_concat; */
	0,			/* intargfunc sq_inplace_repeat; */
};

static PyTypeObject Pointer_Type = {
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
	0,					/* tp_as_number */
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
	0,					/* tp_traverse */
	0,					/* tp_clear */
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
  CString_Type
*/
/*
 * XXX Some should be split into __init__()
 */
static PyObject *
CString_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
/* XXX Beware of UNICODE */
	CDataObject *obj;
	PyObject *init;
	int size = -1;
	char *data;
	int slen;

	if (!PyArg_ParseTuple(args, "O|i", &init, &size))
		return NULL;
	
	if (PyString_Check(init)) {
		PyString_AsStringAndSize(init, &data, &slen);
		if (size == -1)
			size = slen+1;
		if (slen > size-1)
			slen = size-1;
	} else if (PyInt_Check(init)) {
		size = PyInt_AS_LONG(init);
		data = NULL;
	} else {
		PyErr_SetString(PyExc_TypeError,
				"string or positive integer expected");
		return NULL;
	}
	if (size <= 0) {
		PyErr_SetString(PyExc_ValueError,
				"string size must be positive");
		return NULL;
	}

	obj = (CDataObject *)type->tp_alloc(type, 0);

	obj->b_base = NULL;
	obj->b_index = 0;
	/* No python objects referenced... */
	obj->b_objects = NoneList(0);
	obj->b_length = 0;

	obj->b_ptr = PyMem_Malloc(size);
	obj->b_size = size;
	obj->b_needsfree = 1;
	if (data) {
		memcpy(obj->b_ptr, data, slen);
	}
	obj->b_ptr[size-1] = '\0';
	return (PyObject *)obj;
}

static PyMemberDef CString_members[] = {
	{ "_b_size_", T_UINT,
	  offsetof(CDataObject, b_size), READONLY,
	  "the internal buffer size" },
	{ NULL },
};

static PyObject *
CString_get_value(CDataObject *self)
{
	if (self->b_ptr == NULL) {
		PyErr_SetString(PyExc_ValueError,
				"NULL pointer access");
		return NULL;
	}
	/* PyUnicode_FromWideChar */
	return PyString_FromString(self->b_ptr);
}

static PyObject *
CString_get_value_raw(CDataObject *self)
{
	if (self->b_ptr == NULL) {
		PyErr_SetString(PyExc_ValueError,
				"NULL pointer access");
		return NULL;
	}
	return PyString_FromStringAndSize(self->b_ptr, self->b_size);
}

static int
CString_set_value(CDataObject *self, PyObject *value)
{
	char *data;
	int size;

	if (self->b_ptr == NULL) {
		PyErr_SetString(PyExc_ValueError,
				"NULL pointer access");
		return -1;
	}
	data = PyString_AsString(value);
	if (!data)
		return -1;
	size = PyString_Size(value);
	if (size == -1)
		return -1;
	if (size+1 > self->b_size) {
		PyErr_SetString(PyExc_ValueError,
				"string too long");
		return -1;
	}
	/* clear old contents of buffer, just in case */
	memset(self->b_ptr, 0, self->b_size);
	/* copy new contents */
	memcpy(self->b_ptr, data, size);
	return 0;
}

static PyObject *
CString_as_parameter(CDataObject *self)
{
	PyCArgObject *p = new_CArgObject();
	if (p == NULL)
		return NULL;
	p->tag = 'z';
	p->value.p = (char *)self->b_ptr;
	Py_INCREF(self);
	p->obj = (PyObject *)self;
	return (PyObject *)p;
}

static PyGetSetDef CString_getsets[] = {
	{ "raw", (getter)CString_get_value_raw,
	  (setter)CString_set_value,
	  "the raw string contents", NULL },
	{ "value", (getter)CString_get_value,
	  (setter)CString_set_value,
	  "the string contents", NULL },
	{ "_as_parameter_", (getter)CString_as_parameter,
	  (setter)NULL, "convert to a parameter", NULL },
	{ NULL },
};

static PyObject *
CString_repr(CDataObject *self)
{
	if (self->b_ptr == NULL)
		return PyString_FromString("<c_string NULL>");
	if (self->b_size > 20)
		return PyString_FromFormat("<c_string '%20s...'>", self->b_ptr);
	else
		return PyString_FromFormat("<c_string '%20s'>", self->b_ptr);
}

/*
 * If this is a real C classmethod (Python 2.3 and later),
 * it has METH_O style. So the type is in the first argument,
 * and the arg in the second.
 *
 * We fake this in Python 2.2, where METH_CLASS is not present,
 * and 'args' is a tuple containing the type as first member.
 */
static PyObject *
CString_from_param(PyObject *cls, PyObject *args)
{
	PyObject *value;

#ifdef NO_METH_CLASS
	PyObject *ignore;

	if (!PyArg_ParseTuple(args, "OO", &ignore, &value))
		return NULL;
#else
	value = args;
#endif
	if (value == Py_None)
		return PyInt_FromLong(0);

	if (!CString_Check(value) && !PyString_Check(value)) {
		PyErr_SetString(PyExc_TypeError,
				"c_string, string, or None expected");
		return NULL;
	}
	Py_INCREF(value);
	return value;
}

static PyMethodDef CString_methods[] = {
#ifdef NO_METH_CLASS /* Python 2.2 */
	{ "from_param", CString_from_param, METH_VARARGS | METH_CLASS,
#else
	{ "from_param", CString_from_param, METH_O | METH_CLASS,
#endif
	  from_param_doc },
	{ NULL, NULL },
};

static PyTypeObject CString_Type = {
	PyObject_HEAD_INIT(NULL)
	0,
	"_ctypes.c_string",
	sizeof(CDataObject),			/* tp_basicsize */
	0,					/* tp_itemsize */
	CData_dealloc,				/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	0,					/* tp_compare */
	(reprfunc)CString_repr,			/* tp_repr */
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
	"a mutable string",			/* tp_doc */
	0,					/* tp_traverse */
	0,					/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,					/* tp_iter */
	0,					/* tp_iternext */
	CString_methods,			/* tp_methods */
	CString_members,			/* tp_members */
	CString_getsets,			/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	0,					/* tp_init */
	0,					/* tp_alloc */
	CString_new,				/* tp_new */
	0,					/* tp_free */
};


#ifdef HAVE_USABLE_WCHAR_T
/******************************************************************/
/*
  CWString_Type
*/
/*
 * XXX Some should be split into __init__()
 */
static PyObject *
CWString_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	CDataObject *obj;
	PyObject *init;
	int size = -1;
	int slen;
	wchar_t *data;

	if (!PyArg_ParseTuple(args, "O|i", &init, &size))
		return NULL;

	if (PyUnicode_Check(init)) {
		data = PyUnicode_AS_UNICODE(init);
		slen = PyUnicode_GET_SIZE(init);
		if (size == -1)
			size = slen+1;
		if (slen > size-1)
			slen = size-1;
	} else if (PyInt_Check(init)) {
		size = PyInt_AS_LONG(init);
		data = NULL;
	} else {
		PyErr_SetString(PyExc_TypeError,
				"unicode string or None expected");
		return NULL;
	}
	if (size <= 0) {
		PyErr_SetString(PyExc_ValueError,
				"string size must be positive");
		return NULL;
	}

	obj = (CDataObject *)type->tp_alloc(type, 0);

	obj->b_base = NULL;
	obj->b_index = 0;
	/* No python objects referenced... */
	obj->b_objects = NoneList(0);
	obj->b_length = 0;

	obj->b_ptr = PyMem_Malloc(size * sizeof(wchar_t));
	obj->b_size = size * sizeof(wchar_t);
	obj->b_needsfree = 1;
	if (data) {
		memcpy(obj->b_ptr, data, slen * sizeof(wchar_t));
		memset(obj->b_ptr+(slen * sizeof(wchar_t)), 0, (size-slen)*sizeof(wchar_t));
	} else
		memset(obj->b_ptr, 0, size*sizeof(wchar_t));

	return (PyObject *)obj;
}

static PyMemberDef CWString_members[] = {
	{ "_b_size_", T_UINT,
	  offsetof(CDataObject, b_size), READONLY,
	  "the internal buffer size" },
	{ NULL },
};

static PyObject *
CWString_get_value(CDataObject *self)
{
	if (self->b_ptr == NULL) {
		PyErr_SetString(PyExc_ValueError,
				"NULL pointer access");
		return NULL;
	}
	return PyUnicode_FromWideChar((wchar_t *)self->b_ptr,
				      wcslen((wchar_t *)self->b_ptr));
}

static PyObject *
CWString_get_value_raw(CDataObject *self)
{
	if (self->b_ptr == NULL) {
		PyErr_SetString(PyExc_ValueError,
				"NULL pointer access");
		return NULL;
	}
	return PyUnicode_FromWideChar((wchar_t *)self->b_ptr,
				      self->b_size/sizeof(wchar_t));
}

static int
CWString_set_value(CDataObject *self, PyObject *value)
{
	wchar_t *data;
	unsigned int size;

	if (self->b_ptr == NULL) {
		PyErr_SetString(PyExc_ValueError,
				"NULL pointer access");
		return -1;
	}

	if (PyUnicode_Check(value)) {
		data = PyUnicode_AS_UNICODE(value);
		size = PyUnicode_GET_SIZE(value);
	} else {
		PyErr_SetString(PyExc_TypeError,
				"unicode string expected");
		return -1;
	}
	size *= sizeof(wchar_t);

	if (size+sizeof(wchar_t) > (unsigned)self->b_size) {
		PyErr_SetString(PyExc_ValueError,
				"unicode string too long");
		return -1;
	}
	/* clear old contents of buffer, just in case */
	memset(self->b_ptr, 0, self->b_size);
	/* copy new contents */
	memcpy(self->b_ptr, data, size);
	return 0;
}

static PyObject *
CWString_as_parameter(CDataObject *self)
{
	PyCArgObject *p = new_CArgObject();
	if (p == NULL)
		return NULL;
	p->tag = 'Z';
	p->value.p = (char *)self->b_ptr;
	Py_INCREF(self);
	p->obj = (PyObject *)self;
	return (PyObject *)p;
}

static PyGetSetDef CWString_getsets[] = {
	{ "_as_parameter_", (getter)CWString_as_parameter,
	  (setter)NULL, "convert to a parameter", NULL },
	{ "value", (getter)CWString_get_value,
	  (setter)CWString_set_value,
	  "the string contents", NULL },
	{ "raw", (getter)CWString_get_value_raw,
	  (setter)CWString_set_value,
	  "the raw string contents", NULL },
	{ NULL },
};

static PyObject *
CWString_from_param(PyObject *cls, PyObject *args)
{
	PyObject *value;

#ifdef NO_METH_CLASS
	PyObject *ignore;

	if (!PyArg_ParseTuple(args, "OO", &ignore, &value))
		return NULL;
#else
	value = args;
#endif
	if (value == Py_None)
		return PyInt_FromLong(0);

	if (!CWString_Check(value) && !PyUnicode_Check(value)) {
		PyErr_SetString(PyExc_TypeError,
				"c_wstring, unicode, or None expected");
		return NULL;
	}
	Py_INCREF(value);
	return value;
}


static PyMethodDef CWString_methods[] = {
#ifdef NO_METH_CLASS /* Python 2.2 */
	{ "from_param", CWString_from_param, METH_VARARGS | METH_CLASS,
#else
	{ "from_param", CWString_from_param, METH_O | METH_CLASS,
#endif
	  from_param_doc },
	{ NULL, NULL },
};

static PyObject *
CWString_repr(CDataObject *self)
{
	wchar_t buffer[64];
	int size;
	if (self->b_ptr == NULL)
		return PyString_FromString("<c_wstring NULL>");

	if (self->b_size > 20)
		size = _snwprintf(buffer, 64, L"<c_wstring '%.20s...'>", self->b_ptr);
	else
		size = _snwprintf(buffer, 64, L"<c_wstring '%.20s'>", self->b_ptr);
	return PyUnicode_FromWideChar(buffer, size);
}

static PyTypeObject CWString_Type = {
	PyObject_HEAD_INIT(NULL)
	0,
	"_ctypes.c_wstring",
	sizeof(CDataObject),			/* tp_basicsize */
	0,					/* tp_itemsize */
	CData_dealloc,				/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	0,					/* tp_compare */
	(reprfunc)CWString_repr,		/* tp_repr */
	0,					/* tp_as_number */
	0,					/* tp_as_sequence */
	0,					/* tp_as_mapping */
	0,					/* tp_hash */
	0,					/* tp_call */
	0,					/* tp_str */
	0,					/* tp_getattro */
	0,					/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
	"a mutable unicode string",		/* tp_doc */
	0,					/* tp_traverse */
	0,					/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,					/* tp_iter */
	0,					/* tp_iternext */
	CWString_methods,			/* tp_methods */
	CWString_members,			/* tp_members */
	CWString_getsets,			/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	0,					/* tp_init */
	0,					/* tp_alloc */
	CWString_new,				/* tp_new */
	0,					/* tp_free */
};
#endif


/******************************************************************/
PyObject *
ToPython(void *ptr, char tag)
{
	struct fielddesc *fd = getentry(&tag);
	if (!fd) {
		PyErr_Format(PyExc_ValueError,
			     "invalid format char for restype '%c'",
			     tag);
		return NULL;
	}
	return fd->getfunc(ptr, 0);
}

/******************************************************************/
/*
 *  Module initialization.
 */

PyObject *
sizeof_func(PyObject *self, PyObject *obj)
{
	StgDictObject *dict;

	dict = PyType_stgdict(obj);
	if (dict)
		return PyInt_FromLong(dict->size);

	/* Should be able to handle CString and CWString instances? */
	if (CDataObject_Check(obj) || CString_Check(obj)
#ifdef HAVE_USABLE_WCHAR_T
	    || CWString_Check(obj)
#endif
		)
		return PyInt_FromLong(((CDataObject *)obj)->b_size);
	PyErr_SetString(PyExc_TypeError,
			"no size");
	return NULL;
}

PyObject *
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

/*
 * We must return something which can be converted to a parameter,
 * but still has a reference to self.
 */
PyObject *
byref(PyObject *self, PyObject *obj)
{
	/* Should be able to handle CString and CWString instances? */
	PyCArgObject *parg;
	if (!CDataObject_Check(obj)) {
		PyErr_SetString(PyExc_TypeError,
				"expected CData instance");
		return NULL;
	}

	parg = new_CArgObject();
	if (parg == NULL)
		return NULL;

	parg->tag = 'P';
	Py_INCREF(obj);
	parg->obj = obj;
	parg->value.p = ((CDataObject *)obj)->b_ptr;
	return (PyObject *)parg;
}

/*
 * Better to implement addressof here, than to do it in ctypes.py,
 * and have to know about the exact format returned by byref().
 */
PyObject *
addressof(PyObject *self, PyObject *obj)
{
	if (CDataObject_Check(obj) || CString_Check(obj)
#ifdef HAVE_USABLE_WCHAR_T
	    || CWString_Check(obj)
#endif
		)
		return PyInt_FromLong((long)((CDataObject *)obj)->b_ptr);
	PyErr_SetString(PyExc_TypeError,
			"expected CData instance");
	return NULL;
}

/*
static char *Structure_docs =
"An abstract base class for C struct data types\n"
"\n"
"Concrete subclasses must define a _fields_ class attribute\n"
"which must be a sequence of (name, format) tuples.\n"
"\n"
"Abstract subclasses must define an _abstract_ attribute;\n"
"the value of this is ignored.";

static char *Pointer_docs =
"An abstract base class for C pointer data types\n"
"\n"
"Subclasses must define a _type_ class attribute which must\n"
"either be a format character or a subclass of Structure.";


static char *Array_docs =
"An abstract base class for C array data types\n"
"\n"
"Subclasses must define a _type_ class attribute which must\n"
"either be a format character or a subclass of Structure.";
*/

#ifdef NO_METH_CLASS
void DoClassMethods(PyTypeObject *type)
{
	PyObject *func;
	PyObject *meth;
	PyMethodDef *ml = type->tp_methods;

	for (; ml->ml_name; ++ml) {
		if ((ml->ml_flags & METH_CLASS) == 0)
			continue;
		ml->ml_flags &= ~METH_CLASS;
		func = PyCFunction_New(ml, NULL);
		if (!func)
			return;
		meth = PyObject_CallFunctionObjArgs(
			(PyObject *)&PyClassMethod_Type,
			func, NULL);
		if (!meth)
			return;
		if (-1 == PyDict_SetItemString(type->tp_dict,
					       ml->ml_name,
					       meth))
			return;
	}
}
#endif

static char *module_docs =
"Create and manipulate C compatible data types in Python.\n"
"\n"
"format descriptors: characters similar to the struct module\n"
"XXX more";

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

	CData_Type.tp_base = &PyBaseObject_Type;
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
//	PyModule_AddObject(m, "CFieldType", (PyObject *)&CField_Type);

	/* CString_Type is *not* derived from CData_Type */
	/* XXX Should CString_Type be derived from CData_Type?
	   This would enable sizeof() and byref(). But is this correct?
	*/
//	CString_Type.tp_base = &CData_Type;
	if (PyType_Ready(&CString_Type) < 0)
		return;
	/* Hm. Better use a custom metaclass? */
#ifdef NO_METH_CLASS
	DoClassMethods(&CString_Type);
#endif
	PyModule_AddObject(m, "c_string", (PyObject *)&CString_Type);

#ifdef HAVE_USABLE_WCHAR_T
	if (PyType_Ready(&CWString_Type) < 0)
		return;
	/* Hm. Better use a custom metaclass? */
#ifdef NO_METH_CLASS
	DoClassMethods(&CWString_Type);
#endif
	PyModule_AddObject(m, "c_wstring", (PyObject *)&CWString_Type);
#endif

	/*************************************************
	 *
	 * Other stuff
	 */

#ifdef MS_WIN32
	PyModule_AddObject(m, "FUNCFLAG_HRESULT", PyInt_FromLong(FUNCFLAG_HRESULT));
	PyModule_AddObject(m, "FUNCFLAG_STDCALL", PyInt_FromLong(FUNCFLAG_STDCALL));
#endif
	PyModule_AddObject(m, "FUNCFLAG_CDECL", PyInt_FromLong(FUNCFLAG_CDECL));

	/*************************************************
	 *
	 * Others...
	 */
	init_callbacks_in_module(m);
}

PyObject *my_debug(PyObject *self, CDataObject *arg)
{
#ifdef MS_WIN32
  	DISPPARAMS *dp;
  	VARIANT *va;
 	OLECHAR FAR * FAR *p;
	FUNCDESC *f = (FUNCDESC *)(arg->b_ptr);

	ELEMDESC *pelemdesc = *(ELEMDESC **)arg->b_ptr;
 	int *pi;
 	char *cp;
 	char **cpp;
	IUnknown *pIunk = *(IUnknown **)(arg->b_ptr);
	IDispatch *pIDisp = (IDispatch *)(arg->b_ptr);
#ifdef _DEBUG
	int x;
#endif
 	dp = (DISPPARAMS *)arg->b_ptr;
 	va = (VARIANT *)arg->b_ptr;
 	p = (OLECHAR FAR * FAR *)arg->b_ptr;
 	pi = (int *)arg->b_ptr;
 	cp = arg->b_ptr;
 	cpp = (char **)arg->b_ptr;
#ifdef _DEBUG
	_asm int 3;
	Py_BEGIN_ALLOW_THREADS
	x = pIunk->lpVtbl->AddRef(pIunk);
	x = pIunk->lpVtbl->Release(pIunk);
	Py_END_ALLOW_THREADS
#endif
#endif
	Py_INCREF(Py_None);
	return Py_None;
}

#ifdef MS_WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

/* some functions handy for testing */

EXPORT int _testfunc_i_bhilfd(char b, short h, int i, long l, float f, double d)
{
//	printf("_testfunc_i_bhilfd got %d %d %d %ld %f %f\n",
//	       b, h, i, l, f, d);
	return (int)(b + h + i + l + f + d);
}

EXPORT float _testfunc_f_bhilfd(char b, short h, int i, long l, float f, double d)
{
//	printf("_testfunc_f_bhilfd got %d %d %d %ld %f %f\n",
//	       b, h, i, l, f, d);
	return (float)(b + h + i + l + f + d);
}

EXPORT double _testfunc_d_bhilfd(char b, short h, int i, long l, float f, double d)
{
//	printf("_testfunc_d_bhilfd got %d %d %d %ld %f %f\n",
//	       b, h, i, l, f, d);
	return (double)(b + h + i + l + f + d);
}

EXPORT char * _testfunc_p_p(void *s)
{
	return s;
}


#ifndef MS_WIN32
# define __stdcall /* */
#endif

typedef struct {
	int (*c)(int, int);
	int (__stdcall *s)(int, int);
} FUNCS;

EXPORT int _testfunc_callfuncp(FUNCS *fp)
{
	fp->c(1, 2);
	fp->s(3, 4);
	return 0;
}

EXPORT int _testfunc_deref_pointer(int *pi)
{
	return *pi;
}

#ifdef MS_WIN32
EXPORT int _testfunc_piunk(IUnknown FAR *piunk)
{
	piunk->lpVtbl->AddRef(piunk);
	return piunk->lpVtbl->Release(piunk);
}
#endif

#ifdef HAVE_LONG_LONG
EXPORT LONG_LONG _testfunc_q_bhilfdq(char b, short h, int i, long l, float f,
				     double d, LONG_LONG q)
{
	return (LONG_LONG)(b + h + i + l + f + d + q);
}

EXPORT LONG_LONG _testfunc_q_bhilfd(char b, short h, int i, long l, float f, double d)
{
	return (LONG_LONG)(b + h + i + l + f + d);
}

EXPORT int _testfunc_callback_i_if(int value, int (*func)(int))
{
	int sum = 0;
	while (value != 0) {
		sum += func(value);
		value /= 2;
	}
	return sum;
}

EXPORT LONG_LONG _testfunc_callback_q_qf(LONG_LONG value, int (*func)(LONG_LONG))
{
	LONG_LONG sum = 0;

	while (value != 0) {
		sum += func(value);
		value /= 2;
	}
	return sum;
}

#endif
/*
 Local Variables:
 compile-command: "cd .. && python setup.py -q build -g && python setup.py -q build install --home ~"
 End:
*/
