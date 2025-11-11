#define NP_NO_DEPRECATED_API NPY_1_7_API_VERSION
#define Py_LIMITED_API 0x030600f0

#include <Python.h>
#include <numpy/arrayobject.h>
#include <numpy/npy_math.h>
#include "dbg.h"

/* Define docstring */
static char module_docstring[] =
    "Probabilistic distances for statistics";
static char _bhattacharyya_distance_docstring[] =
    "Calculate the Bhattacharyya distances for some distributions.";
static char _hellinger_distance_docstring[] =
    "Calculate the Hellinger distances for some distributions.";

/* Declare the C functions here */
static PyObject *_bhattacharyya_distance(PyObject *self, PyObject *args);
static PyObject *_hellinger_distance(PyObject *self, PyObject *args);

/* Define the methods that will be available in the module */
static PyMethodDef module_methods[] = {
    {
    "_bhattacharyya_distance",
    _bhattacharyya_distance,
    METH_VARARGS,
    _bhattacharyya_distance_docstring,
   },
    {
    "_hellinger_distance",
    _hellinger_distance,
    METH_VARARGS,
    _hellinger_distance_docstring,
   },
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

MOD_INIT(_distance)
{
    PyObject *m;
    MOD_DEF(m, "_distance", module_docstring, module_methods);
    if (m == NULL)
        return MOD_ERROR_VAL;
    import_array();
    return MOD_SUCCESS_VAL(m);
}

/* Define other functions here */

/* distance functions */
static PyObject *_bhattacharyya_distance(PyObject *self, PyObject *args) {

    // npts will describe the length of our P array
    npy_intp npts = 0;
    // nQ describes the number of Q distributions to loop
    npy_intp nQ = 0;
    // store single value of Bhattacharyya distance
    double BC = 0;
    // Loop variables
    npy_intp i = 0, j = 0;
    // Py_objects for inputs and output objects
    PyObject *P_obj = NULL;
    PyObject *Q_obj = NULL;
    PyObject *out_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *P_arr = NULL;
    PyArrayObject *Q_arr = NULL;
    PyArrayObject *out_arr = NULL;
    // Get pointers for the arrays
    double *P_ptr, *Q_ptr, *out_ptr;

    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "OO", &P_obj, &Q_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    // Fill the array pointers
    P_arr = (PyArrayObject *)PyArray_FROM_O(P_obj);
    check(P_arr, "Failed to build P_arr.");
    check(PyArray_NDIM(P_arr) == 1, "P array should have only one dimension.");
    Q_arr = (PyArrayObject *)PyArray_FROM_O(Q_obj);
    check(Q_arr, "Failed to build Q_arr.");
    check(PyArray_NDIM(Q_arr) == 2, "Q array should have only one dimension.");

    // Check the dimensions
    npts = PyArray_DIM(P_arr, 0);
    check(npts > 0, "npts should be greater than zero.");
    check(PyArray_DIM(Q_arr, 1) == npts, "dimension mismatch between P and Q.");
    nQ = PyArray_DIM(Q_arr, 0);
    check(nQ > 0, "nQ should be greater than zero.");

    // Build output array
    out_obj = PyArray_ZEROS(1, &nQ, NPY_DOUBLE, 0);
    check(out_obj, "Failed to build output object.");
    out_arr = (PyArrayObject *)out_obj;
    check(out_arr, "Failed to build output array.");
    // Fill out with zeros
    PyArray_FILLWBYTE(out_arr, 0);

    // Allow multithreading
    Py_BEGIN_ALLOW_THREADS
    for (i = 0; i < nQ; i++){
        BC = 0;
        out_ptr = PyArray_GETPTR1(out_arr, i);
        for (j = 0; j < npts; j++){
            P_ptr = PyArray_GETPTR1(P_arr, j);
            Q_ptr = PyArray_GETPTR2(Q_arr, i, j);
            BC += sqrt(*P_ptr * *Q_ptr);
        }
        *out_ptr = -log(BC);
    }
    // Cut out the multithreading nonsense
    Py_END_ALLOW_THREADS
    // Free things
    if (P_arr) {Py_DECREF(P_arr);}
    if (Q_arr) {Py_DECREF(Q_arr);}
    // Return output array
    return out_obj;

// Error
error:
    if (P_arr) {Py_DECREF(P_arr);}
    if (Q_arr) {Py_DECREF(Q_arr);}
    if (out_obj) {Py_DECREF(out_obj);}
    if (out_arr) {Py_DECREF(out_arr);}
    PyErr_SetString(PyExc_RuntimeError, "C error");
    return NULL;
}
/* distance functions */
static PyObject *_hellinger_distance(PyObject *self, PyObject *args) {

    // npts will describe the length of our P array
    npy_intp npts = 0;
    // nQ describes the number of Q distributions to loop
    npy_intp nQ = 0;
    // store single value of Bhattacharyya coefficient
    double BC = 0;
    // Loop variables
    npy_intp i = 0, j = 0;
    // Py_objects for inputs and output objects
    PyObject *P_obj = NULL;
    PyObject *Q_obj = NULL;
    PyObject *out_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *P_arr = NULL;
    PyArrayObject *Q_arr = NULL;
    PyArrayObject *out_arr = NULL;
    // Get pointers for the arrays
    double *P_ptr, *Q_ptr, *out_ptr;

    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "OO", &P_obj, &Q_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    // Fill the array pointers
    P_arr = (PyArrayObject *)PyArray_FROM_O(P_obj);
    check(P_arr, "Failed to build P_arr.");
    check(PyArray_NDIM(P_arr) == 1, "P array should have only one dimension.");
    Q_arr = (PyArrayObject *)PyArray_FROM_O(Q_obj);
    check(Q_arr, "Failed to build Q_arr.");
    check(PyArray_NDIM(Q_arr) == 2, "Q array should have only one dimension.");

    // Check the dimensions
    npts = PyArray_DIM(P_arr, 0);
    check(npts > 0, "npts should be greater than zero.");
    check(PyArray_DIM(Q_arr, 1) == npts, "dimension mismatch between P and Q.");
    nQ = PyArray_DIM(Q_arr, 0);
    check(nQ > 0, "nQ should be greater than zero.");

    // Build output array
    out_obj = PyArray_ZEROS(1, &nQ, NPY_DOUBLE, 0);
    check(out_obj, "Failed to build output object.");
    out_arr = (PyArrayObject *)out_obj;
    check(out_arr, "Failed to build output array.");
    // Fill out with zeros
    PyArray_FILLWBYTE(out_arr, 0);

    // Allow multithreading
    Py_BEGIN_ALLOW_THREADS
    for (i = 0; i < nQ; i++){
        BC = 0;
        out_ptr = PyArray_GETPTR1(out_arr, i);
        for (j = 0; j < npts; j++){
            P_ptr = PyArray_GETPTR1(P_arr, j);
            Q_ptr = PyArray_GETPTR2(Q_arr, i, j);
            BC += sqrt(*P_ptr * *Q_ptr);
        }
        *out_ptr = sqrt(1 - BC);
    }
    // Cut out the multithreading nonsense
    Py_END_ALLOW_THREADS
    // Free things
    if (P_arr) {Py_DECREF(P_arr);}
    if (Q_arr) {Py_DECREF(Q_arr);}
    // Return output array
    return out_obj;

// Error
error:
    if (P_arr) {Py_DECREF(P_arr);}
    if (Q_arr) {Py_DECREF(Q_arr);}
    if (out_obj) {Py_DECREF(out_obj);}
    if (out_arr) {Py_DECREF(out_arr);}
    PyErr_SetString(PyExc_RuntimeError, "C error");
    return NULL;
}
