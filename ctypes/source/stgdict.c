#include "Python.h"
#include <ffi.h>
#include "ctypes.h"

/******************************************************************/
/*
  StdDict - a dictionary subclass, containing additional C accessible fields

  XXX blabla more
*/

/* Seems we need this, otherwise we get problems when calling
 * PyDict_SetItem() (ma_lookup is NULL)
 */
static int
StgDict_init(StgDictObject *self, PyObject *args, PyObject *kwds)
{
	if (PyDict_Type.tp_init((PyObject *)self, args, kwds) < 0)
		return -1;
	return 0;
}

static void
StgDict_dealloc(StgDictObject *self)
{
	Py_XDECREF(self->proto);
	PyMem_Free(self->ffi_type.elements);
	((PyObject *)self)->ob_type->tp_free((PyObject *)self);
}


PyTypeObject StgDict_Type = {
	PyObject_HEAD_INIT(NULL)
	0,
	"StgDict",
	sizeof(StgDictObject),
	0,
	(destructor)StgDict_dealloc,		/* tp_dealloc */
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
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
	0,					/* tp_doc */
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
	(initproc)StgDict_init,			/* tp_init */
	0,					/* tp_alloc */
	0,					/* tp_new */
	0,					/* tp_free */
};

/* May return NULL, but does not set an exception! */
StgDictObject *
PyType_stgdict(PyObject *obj)
{
	PyTypeObject *type;

	if (!PyType_Check(obj))
		return NULL;
	type = (PyTypeObject *)obj;
	if (!PyType_HasFeature(type, Py_TPFLAGS_HAVE_CLASS))
		return NULL;
	if (!type->tp_dict || !StgDict_Check(type->tp_dict))
		return NULL;
	return (StgDictObject *)type->tp_dict;
}

/* May return NULL, but does not set an exception! */
StgDictObject *
PyObject_stgdict(PyObject *self)
{
	return PyType_stgdict((PyObject *)self->ob_type);
}

#if 0
/* work in progress: anonymous structure fields */
int
GetFields(PyObject *desc, int *pindex, int *psize, int *poffset, int *palign, int pack);

{
	int i;
	PyObject *tuples = PyObject_GetAttrString(desc, "_fields_");
	if (tuples == NULL)
		return -1;
	if (!PyTuple_Check(tuples))
		return -1; /* leak */
	for (i = 0; i < PyTuple_GET_SIZE(tuples); ++i) {
		char *fname;
		PyObject *dummy;
		CFieldObject *field;
		PyObject *pair = PyTuple_GET_ITEM(tuples, i);
		if (!PyArg_ParseTuple(pair, "sO", &fname, &dummy))
			return -1; /* leak */
		field = PyObject_GetAttrString(desc, fname);
		Py_DECREF(field);
	}
}
#endif

/*
  This is a helper function for the StructType_Type object.
  Hm, actually only for Structure types, since it requires the
  _fields_ attribute.
*/

PyObject *
StgDict_FromDict(PyObject *fields, PyObject *typedict, int isStruct)
{
	StgDictObject *stgdict;
	int len, offset, size, align, i;
	int union_size, total_align;
	PyObject *prev_desc = NULL;
	int bitofs;
	PyObject *isPacked;
	int pack = 0;

	if (!typedict)
		return NULL;

	isPacked = PyDict_GetItemString(typedict, "_pack_");
	if (isPacked) {
		pack = PyInt_AsLong(isPacked);
		if (pack < 0 || PyErr_Occurred()) {
			PyErr_SetString(PyExc_ValueError,
					"_pack_ must be a non-negative integer");
			return NULL;
		}
	}

	if (!fields) {
		PyErr_SetString(PyExc_AttributeError,
				"class must define a '_fields_' attribute");
		return NULL;
	}

	len = PySequence_Length(fields);
	if (len == -1) {
		PyErr_SetString(PyExc_AttributeError,
				"'_fields_' must be a sequence of pairs");
		return NULL;
	}

	stgdict = (StgDictObject *)PyObject_CallObject(
		(PyObject *)&StgDict_Type, NULL);
	if (!stgdict)
		return NULL;

	offset = 0;
	size = 0;
	align = 0;
	union_size = 0;
	total_align = 1;

	stgdict->ffi_type.type = FFI_TYPE_STRUCT;
	stgdict->ffi_type.elements = PyMem_Malloc(sizeof(ffi_type *) * (len + 1));
	memset(stgdict->ffi_type.elements, 0, sizeof(ffi_type *) * (len + 1));

#define realdict ((PyObject *)&stgdict->dict)
	for (i = 0; i < len; ++i) {
		PyObject *name = NULL, *desc = NULL;
		PyObject *pair = PySequence_GetItem(fields, i);
		PyObject *prop;
		StgDictObject *dict;
		int bitsize = 0;

		if (!pair  || !PyArg_ParseTuple(pair, "OO|i", &name, &desc, &bitsize)) {
			PyErr_SetString(PyExc_AttributeError,
					"'_fields_' must be a sequence of pairs");
			Py_XDECREF(pair);
			return NULL;
		}
		dict = PyType_stgdict(desc);
		if (dict)
			stgdict->ffi_type.elements[i] = &dict->ffi_type;
		if (PyTuple_Size(pair) == 3) { /* bits specified */
			switch(dict->ffi_type.type) {
			case FFI_TYPE_UINT8:
			case FFI_TYPE_UINT16:
			case FFI_TYPE_UINT32:
			case FFI_TYPE_SINT64:
			case FFI_TYPE_UINT64:
				break;

			case FFI_TYPE_SINT8:
			case FFI_TYPE_SINT16:
			case FFI_TYPE_SINT32:
				if (dict->getfunc != getentry("c")->getfunc
#ifdef Py_USING_UNICODE
				    && dict->getfunc != getentry("u")->getfunc
#endif
					)
					break;
				/* else fall through */
			default:
				PyErr_Format(PyExc_TypeError,
					     "bit fields not allowed for type %s",
					     ((PyTypeObject *)desc)->tp_name);
				Py_DECREF(pair);
				return NULL;
			}
			if (bitsize <= 0 || bitsize > dict->size * 8) {
				PyErr_SetString(PyExc_ValueError,
						"number of bits invalid for bit field");
				Py_DECREF(pair);
				return NULL;
			}
		} else
			bitsize = 0;
		if (isStruct) {
			prop = CField_FromDesc(desc, i,
					       prev_desc, bitsize, &bitofs,
					       &size, &offset, &align, pack);
		} else /* union */ {
			size = 0;
			offset = 0;
			align = 0;
			prop = CField_FromDesc(desc, i,
					       prev_desc, bitsize, &bitofs,
					       &size, &offset, &align, pack);
			union_size = max(size, union_size);
		}
		total_align = max(align, total_align);

		if (!prop) {
			Py_DECREF(pair);
			Py_DECREF((PyObject *)stgdict);
			return NULL;
		}
		if (-1 == PyDict_SetItem(realdict, name, prop)) {
			Py_DECREF(prop);
			Py_DECREF(pair);
			Py_DECREF((PyObject *)stgdict);
			return NULL;
		}
		Py_DECREF(pair);
		Py_DECREF(prop);
		prev_desc = desc; /* store, in case of continued bitfield */
	}
#undef realdict

	if (!isStruct)
		size = union_size;

	/* Adjust the size according to the alignment requirements */
	size = ((size + total_align - 1) / total_align) * total_align;

	stgdict->ffi_type.alignment = total_align;
	stgdict->ffi_type.size = size;

	stgdict->size = size;
	stgdict->align = total_align;
	stgdict->length = len;
	return (PyObject *)stgdict;
}
