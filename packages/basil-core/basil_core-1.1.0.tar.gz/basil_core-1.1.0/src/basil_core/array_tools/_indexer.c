#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#define Py_LIMITED_API 0x030600f0

#include <Python.h>
#include <numpy/arrayobject.h>
#include <numpy/npy_math.h>
#include "dbg.h"

/* Define docstrings */
static char module_docstring[] = "an array indexer for xevra";
static char _unique_array_index64u_docstring[] = 
    "Return the index for elements of one array matching another unique array";
static char _unique_array_index32u_docstring[] = 
    "Return the index for elements of one array matching another unique array";
static char _unique_array_index16u_docstring[] = 
    "Return the index for elements of one array matching another unique array";
static char _unique_array_index64_docstring[] = 
    "Return the index for elements of one array matching another unique array";
static char _unique_array_index32_docstring[] = 
    "Return the index for elements of one array matching another unique array";
static char _unique_array_index16_docstring[] = 
    "Return the index for elements of one array matching another unique array";

/* Declare the C functions here. */
static PyObject *_unique_array_index64u(PyObject *self, PyObject *args);
static PyObject *_unique_array_index32u(PyObject *self, PyObject *args);
static PyObject *_unique_array_index16u(PyObject *self, PyObject *args);
static PyObject *_unique_array_index64(PyObject *self, PyObject *args);
static PyObject *_unique_array_index32(PyObject *self, PyObject *args);
static PyObject *_unique_array_index16(PyObject *self, PyObject *args);


/* Define the methods that will be available on the module. */
static PyMethodDef module_methods[] = {
    {"_unique_array_index64u", _unique_array_index64u, METH_VARARGS, _unique_array_index64u_docstring},
    {"_unique_array_index32u", _unique_array_index32u, METH_VARARGS, _unique_array_index32u_docstring},
    {"_unique_array_index16u", _unique_array_index16u, METH_VARARGS, _unique_array_index16u_docstring},
    {"_unique_array_index64", _unique_array_index64, METH_VARARGS, _unique_array_index64_docstring},
    {"_unique_array_index32", _unique_array_index32, METH_VARARGS, _unique_array_index32_docstring},
    {"_unique_array_index16", _unique_array_index16, METH_VARARGS, _unique_array_index16_docstring},
    {NULL, NULL, 0, NULL}
};

/* This is the function that will call on import */

#if PY_MAJOR_VERSION >= 3
    #define MOD_ERROR_VAL NULL
    #define MOD_SUCCESS_VAL(val) val
    #define MOD_INIT(name) PyMODINIT_FUNC PyInit_##name(void)
    #define MOD_DEF(ob, name, doc, methods) \
        static struct PyModuleDef moduledef = { \
          PyModuleDef_HEAD_INIT, name, doc, -1, methods, }; \
        ob = PyModule_Create(&moduledef);
#else
    #define MOD_ERROR_VAL
    #define MOD_SUCCESS_VAL(val)
    #define MOD_INIT(name) void init##name(void)
    #define MOD_DEF(ob, name, doc, methods) \
            ob = Py_InitModule3(name, methods, doc);
#endif

MOD_INIT(_indexer)
{
    PyObject *m;
    MOD_DEF(m, "_indexer", module_docstring, module_methods);
    if (m == NULL)
        return MOD_ERROR_VAL;
    import_array();
    return MOD_SUCCESS_VAL(m);
}

/* Begin the function definitions */

static PyObject *_unique_array_index64(PyObject *self, PyObject *args) {

    // n will be used to describe the length of the
    // input 'samples' and output 'indices' arrays
    npy_intp n = 0;
    // n_unique will be used to describe the length of the unique array
    npy_intp n_unique=0;
    // Py_objects for input and output objects
    PyObject *unique_obj, *sample_obj, *indices_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *unique_array, *sample_array, *indices_array  = NULL;
    // Loop variables
    npy_intp i = 0;
    npy_intp j = 0;
    // Initialize pointers
    npy_int64 *unique_ptr, *sample_ptr, *indices_ptr;

    /* Parse the input tuple */
    // Python and Numpy interfaces for C have some pretty heavy-handed macros
    // This block parses the input tuple that python will try to pass to C
    // O is just a PyObject
    // see \url{https://docs.python.org/3/c-api/arg.html} for more details
    if (!PyArg_ParseTuple(args, "OO", &unique_obj, &sample_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    /* Interpret the input objects as `numpy` arrays */
    unique_array = (PyArrayObject *)PyArray_FROM_O(unique_obj);
    sample_array = (PyArrayObject *)PyArray_FROM_O(sample_obj);

    /* If that didn't work, throw an error. */
    check((unique_array != NULL && sample_array != NULL),
        "Couldn't parse the input arrays");

    /* How many data points are there? */
    n_unique = (long)PyArray_DIM(unique_array, 0);
    n = (long)PyArray_DIM(sample_array, 0);

    /* Build the output arrays */
    indices_obj = PyArray_ZEROS(1, &n, NPY_INT64, 0);
    check(indices_obj != NULL, "Couldn't build output array");
    indices_array = (PyArrayObject *)indices_obj;

    PyArray_FILLWBYTE(indices_array, -1);
    
    // Check if length is zero
    check(n != 0, "Length of array is zero");

    Py_BEGIN_ALLOW_THREADS

    // Loop the unique values
    for (i = 0; i < n_unique; i++){
        // Get unique pointer
        unique_ptr = PyArray_GETPTR1(unique_array, i);
        // Loop the samples
        for (j = 0; j < n; j++){
            // Get the sample pointer
            sample_ptr = PyArray_GETPTR1(sample_array, j);
            // Check if they have the same value
            if (*sample_ptr == *unique_ptr){
                // Get indices ptr
                indices_ptr = PyArray_GETPTR1(indices_array, j);
                // Assign value
                *indices_ptr = i;
            }
        }
    }
    Py_END_ALLOW_THREADS

    /* Clean up. */
    Py_DECREF(unique_array);
    Py_DECREF(sample_array);

    return indices_obj;

error:
    if (unique_array) {Py_DECREF(unique_array);}
    if (sample_array) {Py_DECREF(sample_array);}
    if (indices_obj) {Py_DECREF(indices_obj);}
    if (indices_array) {Py_DECREF(indices_array);}
    return NULL;
}


static PyObject *_unique_array_index32(PyObject *self, PyObject *args) {

    // n will be used to describe the length of the
    // input 'samples' and output 'indices' arrays
    npy_intp n = 0;
    // n_unique will be used to describe the length of the unique array
    npy_intp n_unique=0;
    // Py_objects for input and output objects
    PyObject *unique_obj, *sample_obj, *indices_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *unique_array, *sample_array, *indices_array  = NULL;
    // Loop variables
    npy_intp i = 0;
    npy_intp j = 0;
    // Initialize pointers
    npy_int32 *unique_ptr, *sample_ptr, *indices_ptr;

    /* Parse the input tuple */
    // Python and Numpy interfaces for C have some pretty heavy-handed macros
    // This block parses the input tuple that python will try to pass to C
    // O is just a PyObject
    // see \url{https://docs.python.org/3/c-api/arg.html} for more details
    if (!PyArg_ParseTuple(args, "OO", &unique_obj, &sample_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    /* Interpret the input objects as `numpy` arrays */
    unique_array = (PyArrayObject *)PyArray_FROM_O(unique_obj);
    sample_array = (PyArrayObject *)PyArray_FROM_O(sample_obj);

    /* If that didn't work, throw an error. */
    check((unique_array != NULL && sample_array != NULL),
        "Couldn't parse the input arrays");

    /* How many data points are there? */
    n_unique = (long)PyArray_DIM(unique_array, 0);
    n = (long)PyArray_DIM(sample_array, 0);

    /* Build the output arrays */
    indices_obj = PyArray_ZEROS(1, &n, NPY_INT32, 0);
    check(indices_obj != NULL, "Couldn't build output array");
    indices_array = (PyArrayObject *)indices_obj;

    PyArray_FILLWBYTE(indices_array, -1);
    
    // Check if length is zero
    check(n != 0, "Length of array is zero");

    Py_BEGIN_ALLOW_THREADS

    // Loop the unique values
    for (i = 0; i < n_unique; i++){
        // Get unique pointer
        unique_ptr = PyArray_GETPTR1(unique_array, i);
        // Loop the samples
        for (j = 0; j < n; j++){
            // Get the sample pointer
            sample_ptr = PyArray_GETPTR1(sample_array, j);
            // Check if they have the same value
            if (*sample_ptr == *unique_ptr){
                // Get indices ptr
                indices_ptr = PyArray_GETPTR1(indices_array, j);
                // Assign value
                *indices_ptr = i;
            }
        }
    }
    Py_END_ALLOW_THREADS

    /* Clean up. */
    Py_DECREF(unique_array);
    Py_DECREF(sample_array);

    return indices_obj;

error:
    if (unique_array) {Py_DECREF(unique_array);}
    if (sample_array) {Py_DECREF(sample_array);}
    if (indices_obj) {Py_DECREF(indices_obj);}
    if (indices_array) {Py_DECREF(indices_array);}
    return NULL;
}


static PyObject *_unique_array_index16(PyObject *self, PyObject *args) {

    // n will be used to describe the length of the
    // input 'samples' and output 'indices' arrays
    npy_intp n = 0;
    // n_unique will be used to describe the length of the unique array
    npy_intp n_unique=0;
    // Py_objects for input and output objects
    PyObject *unique_obj, *sample_obj, *indices_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *unique_array, *sample_array, *indices_array  = NULL;
    // Loop variables
    npy_intp i = 0;
    npy_intp j = 0;
    // Initialize pointers
    npy_int16 *unique_ptr, *sample_ptr, *indices_ptr;

    /* Parse the input tuple */
    // Python and Numpy interfaces for C have some pretty heavy-handed macros
    // This block parses the input tuple that python will try to pass to C
    // O is just a PyObject
    // see \url{https://docs.python.org/3/c-api/arg.html} for more details
    if (!PyArg_ParseTuple(args, "OO", &unique_obj, &sample_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    /* Interpret the input objects as `numpy` arrays */
    unique_array = (PyArrayObject *)PyArray_FROM_O(unique_obj);
    sample_array = (PyArrayObject *)PyArray_FROM_O(sample_obj);

    /* If that didn't work, throw an error. */
    check((unique_array != NULL && sample_array != NULL),
        "Couldn't parse the input arrays");

    /* How many data points are there? */
    n_unique = (long)PyArray_DIM(unique_array, 0);
    n = (long)PyArray_DIM(sample_array, 0);

    /* Build the output arrays */
    indices_obj = PyArray_ZEROS(1, &n, NPY_INT16, 0);
    check(indices_obj != NULL, "Couldn't build output array");
    indices_array = (PyArrayObject *)indices_obj;

    PyArray_FILLWBYTE(indices_array, -1);
    
    // Check if length is zero
    check(n != 0, "Length of array is zero");

    Py_BEGIN_ALLOW_THREADS

    // Loop the unique values
    for (i = 0; i < n_unique; i++){
        // Get unique pointer
        unique_ptr = PyArray_GETPTR1(unique_array, i);
        // Loop the samples
        for (j = 0; j < n; j++){
            // Get the sample pointer
            sample_ptr = PyArray_GETPTR1(sample_array, j);
            // Check if they have the same value
            if (*sample_ptr == *unique_ptr){
                // Get indices ptr
                indices_ptr = PyArray_GETPTR1(indices_array, j);
                // Assign value
                *indices_ptr = i;
            }
        }
    }
    Py_END_ALLOW_THREADS

    /* Clean up. */
    Py_DECREF(unique_array);
    Py_DECREF(sample_array);

    return indices_obj;

error:
    if (unique_array) {Py_DECREF(unique_array);}
    if (sample_array) {Py_DECREF(sample_array);}
    if (indices_obj) {Py_DECREF(indices_obj);}
    if (indices_array) {Py_DECREF(indices_array);}
    return NULL;
}

static PyObject *_unique_array_index64u(PyObject *self, PyObject *args) {

    // n will be used to describe the length of the
    // input 'samples' and output 'indices' arrays
    npy_intp n = 0;
    // n_unique will be used to describe the length of the unique array
    npy_intp n_unique=0;
    // Py_objects for input and output objects
    PyObject *unique_obj, *sample_obj, *indices_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *unique_array, *sample_array, *indices_array  = NULL;
    // Loop variables
    npy_intp i = 0;
    npy_intp j = 0;
    // Initialize pointers
    npy_uint64 *unique_ptr, *sample_ptr, *indices_ptr;

    /* Parse the input tuple */
    // Python and Numpy interfaces for C have some pretty heavy-handed macros
    // This block parses the input tuple that python will try to pass to C
    // O is just a PyObject
    // see \url{https://docs.python.org/3/c-api/arg.html} for more details
    if (!PyArg_ParseTuple(args, "OO", &unique_obj, &sample_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    /* Interpret the input objects as `numpy` arrays */
    unique_array = (PyArrayObject *)PyArray_FROM_O(unique_obj);
    sample_array = (PyArrayObject *)PyArray_FROM_O(sample_obj);

    /* If that didn't work, throw an error. */
    check((unique_array != NULL && sample_array != NULL),
        "Couldn't parse the input arrays");

    /* How many data points are there? */
    n_unique = (long)PyArray_DIM(unique_array, 0);
    n = (long)PyArray_DIM(sample_array, 0);

    /* Build the output arrays */
    indices_obj = PyArray_ZEROS(1, &n, NPY_UINT64, 0);
    check(indices_obj != NULL, "Couldn't build output array");
    indices_array = (PyArrayObject *)indices_obj;

    //PyArray_FILLWBYTE(indices_array, -1);
    
    // Check if length is zero
    check(n != 0, "Length of array is zero");

    Py_BEGIN_ALLOW_THREADS

    // Loop the unique values
    for (i = 0; i < n_unique; i++){
        // Get unique pointer
        unique_ptr = PyArray_GETPTR1(unique_array, i);
        // Loop the samples
        for (j = 0; j < n; j++){
            // Get the sample pointer
            sample_ptr = PyArray_GETPTR1(sample_array, j);
            // Check if they have the same value
            if (*sample_ptr == *unique_ptr){
                // Get indices ptr
                indices_ptr = PyArray_GETPTR1(indices_array, j);
                // Assign value
                *indices_ptr = i;
            }
        }
    }
    Py_END_ALLOW_THREADS

    /* Clean up. */
    Py_DECREF(unique_array);
    Py_DECREF(sample_array);

    return indices_obj;

error:
    if (unique_array) {Py_DECREF(unique_array);}
    if (sample_array) {Py_DECREF(sample_array);}
    if (indices_obj) {Py_DECREF(indices_obj);}
    if (indices_array) {Py_DECREF(indices_array);}
    return NULL;
}


static PyObject *_unique_array_index32u(PyObject *self, PyObject *args) {

    // n will be used to describe the length of the
    // input 'samples' and output 'indices' arrays
    npy_intp n = 0;
    // n_unique will be used to describe the length of the unique array
    npy_intp n_unique=0;
    // Py_objects for input and output objects
    PyObject *unique_obj, *sample_obj, *indices_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *unique_array, *sample_array, *indices_array  = NULL;
    // Loop variables
    npy_intp i = 0;
    npy_intp j = 0;
    // Initialize pointers
    npy_uint32 *unique_ptr, *sample_ptr, *indices_ptr;

    /* Parse the input tuple */
    // Python and Numpy interfaces for C have some pretty heavy-handed macros
    // This block parses the input tuple that python will try to pass to C
    // O is just a PyObject
    // see \url{https://docs.python.org/3/c-api/arg.html} for more details
    if (!PyArg_ParseTuple(args, "OO", &unique_obj, &sample_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    /* Interpret the input objects as `numpy` arrays */
    unique_array = (PyArrayObject *)PyArray_FROM_O(unique_obj);
    sample_array = (PyArrayObject *)PyArray_FROM_O(sample_obj);

    /* If that didn't work, throw an error. */
    check((unique_array != NULL && sample_array != NULL),
        "Couldn't parse the input arrays");

    /* How many data points are there? */
    n_unique = (long)PyArray_DIM(unique_array, 0);
    n = (long)PyArray_DIM(sample_array, 0);

    /* Build the output arrays */
    indices_obj = PyArray_ZEROS(1, &n, NPY_UINT32, 0);
    check(indices_obj != NULL, "Couldn't build output array");
    indices_array = (PyArrayObject *)indices_obj;

    //PyArray_FILLWBYTE(indices_array, -1);
    
    // Check if length is zero
    check(n != 0, "Length of array is zero");

    Py_BEGIN_ALLOW_THREADS

    // Loop the unique values
    for (i = 0; i < n_unique; i++){
        // Get unique pointer
        unique_ptr = PyArray_GETPTR1(unique_array, i);
        // Loop the samples
        for (j = 0; j < n; j++){
            // Get the sample pointer
            sample_ptr = PyArray_GETPTR1(sample_array, j);
            // Check if they have the same value
            if (*sample_ptr == *unique_ptr){
                // Get indices ptr
                indices_ptr = PyArray_GETPTR1(indices_array, j);
                // Assign value
                *indices_ptr = i;
            }
        }
    }
    Py_END_ALLOW_THREADS

    /* Clean up. */
    Py_DECREF(unique_array);
    Py_DECREF(sample_array);

    return indices_obj;

error:
    if (unique_array) {Py_DECREF(unique_array);}
    if (sample_array) {Py_DECREF(sample_array);}
    if (indices_obj) {Py_DECREF(indices_obj);}
    if (indices_array) {Py_DECREF(indices_array);}
    return NULL;
}


static PyObject *_unique_array_index16u(PyObject *self, PyObject *args) {

    // n will be used to describe the length of the
    // input 'samples' and output 'indices' arrays
    npy_intp n = 0;
    // n_unique will be used to describe the length of the unique array
    npy_intp n_unique=0;
    // Py_objects for input and output objects
    PyObject *unique_obj, *sample_obj, *indices_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *unique_array, *sample_array, *indices_array  = NULL;
    // Loop variables
    npy_intp i = 0;
    npy_intp j = 0;
    // Initialize pointers
    npy_uint16 *unique_ptr, *sample_ptr, *indices_ptr;

    /* Parse the input tuple */
    // Python and Numpy interfaces for C have some pretty heavy-handed macros
    // This block parses the input tuple that python will try to pass to C
    // O is just a PyObject
    // see \url{https://docs.python.org/3/c-api/arg.html} for more details
    if (!PyArg_ParseTuple(args, "OO", &unique_obj, &sample_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    /* Interpret the input objects as `numpy` arrays */
    unique_array = (PyArrayObject *)PyArray_FROM_O(unique_obj);
    sample_array = (PyArrayObject *)PyArray_FROM_O(sample_obj);

    /* If that didn't work, throw an error. */
    check((unique_array != NULL && sample_array != NULL),
        "Couldn't parse the input arrays");

    /* How many data points are there? */
    n_unique = (long)PyArray_DIM(unique_array, 0);
    n = (long)PyArray_DIM(sample_array, 0);

    /* Build the output arrays */
    indices_obj = PyArray_ZEROS(1, &n, NPY_UINT16, 0);
    check(indices_obj != NULL, "Couldn't build output array");
    indices_array = (PyArrayObject *)indices_obj;


    //PyArray_FILLWBYTE(indices_array, -1);
    
    // Check if length is zero
    check(n != 0, "Length of array is zero");

    Py_BEGIN_ALLOW_THREADS

    // Loop the unique values
    for (i = 0; i < n_unique; i++){
        // Get unique pointer
        unique_ptr = PyArray_GETPTR1(unique_array, i);
        // Loop the samples
        for (j = 0; j < n; j++){
            // Get the sample pointer
            sample_ptr = PyArray_GETPTR1(sample_array, j);
            // Check if they have the same value
            if (*sample_ptr == *unique_ptr){
                // Get indices ptr
                indices_ptr = PyArray_GETPTR1(indices_array, j);
                // Assign value
                *indices_ptr = i;
            }
        }
    }
    Py_END_ALLOW_THREADS

    /* Clean up. */
    Py_DECREF(unique_array);
    Py_DECREF(sample_array);

    return indices_obj;

error:
    if (unique_array) {Py_DECREF(unique_array);}
    if (sample_array) {Py_DECREF(sample_array);}
    if (indices_obj) {Py_DECREF(indices_obj);}
    if (indices_array) {Py_DECREF(indices_array);}
    return NULL;
}

