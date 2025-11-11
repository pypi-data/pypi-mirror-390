#define NP_NO_DEPRECATED_API NPY_1_7_API_VERSION
#define Py_LIMITED_API 0x030600f0

#include <Python.h>
#include <numpy/arrayobject.h>
#include <numpy/npy_math.h>
#include "dbg.h"

/* Define docstring */
static char module_docstring[] =
    "Probabilistic entropy for statistics";
static char _rel_entr_docstring[] =
    "Calculate the relative entropy for some distributions.";
static char _log_rel_entr_docstring[] =
    "Calculate the relative entropy with log information.";
static char _log_norm_rel_entr_docstring[] =
    "Calculate the relative entropy with log information, normalizing Q.";

/* Declare the C functions here */
static PyObject *_rel_entr(PyObject *self, PyObject *args);
static PyObject *_log_rel_entr(PyObject *self, PyObject *args);
static PyObject *_log_norm_rel_entr(PyObject *self, PyObject *args);

/* Define the methods that will be available in the module */
static PyMethodDef module_methods[] = {
    {
    "_rel_entr",
    _rel_entr,
    METH_VARARGS,
    _rel_entr_docstring,
   },
    {
    "_log_rel_entr",
    _log_rel_entr,
    METH_VARARGS,
    _log_rel_entr_docstring,
   },
    {
    "_log_norm_rel_entr",
    _log_norm_rel_entr,
    METH_VARARGS,
    _log_norm_rel_entr_docstring,
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

MOD_INIT(_relative_entropy)
{
    PyObject *m;
    MOD_DEF(m, "_relative_entropy", module_docstring, module_methods);
    if (m == NULL)
        return MOD_ERROR_VAL;
    import_array();
    return MOD_SUCCESS_VAL(m);
}

/* Define other functions here */

/* entropy functions */
static PyObject *_rel_entr(PyObject *self, PyObject *args) {

    // npts will describe the length of our P array
    npy_intp npts = 0;
    // nQ describes the number of Q distributions to loop
    npy_intp nQ = 0;
    // store single value of distance
    double r = 0, max_value = 0;

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
    if (!PyArg_ParseTuple(args, "OOd", &P_obj, &Q_obj, &max_value)) {
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
        r = 0;
        out_ptr = PyArray_GETPTR1(out_arr, i);
        for (j = 0; j < npts; j++){
            P_ptr = PyArray_GETPTR1(P_arr, j);
            Q_ptr = PyArray_GETPTR2(Q_arr, i, j);
            if ((P_ptr > 0) && (Q_ptr > 0)) {
                r += *P_ptr * log(*P_ptr / *Q_ptr);
            } else if (*P_ptr < 0) {
                r = max_value;
                break;
            }

        }
        *out_ptr = r;
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

static PyObject *_log_rel_entr(PyObject *self, PyObject *args) {

    // npts will describe the length of our P array
    npy_intp npts = 0;
    // nQ describes the number of Q distributions to loop
    npy_intp nQ = 0;
    // store single value of distance
    double r = 0 ;

    // Loop variables
    npy_intp i = 0, j = 0;
    // Py_objects for inputs and output objects
    PyObject *P_obj = NULL;
    PyObject *lnP_obj = NULL;
    PyObject *lnQ_obj = NULL;
    PyObject *out_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *P_arr = NULL;
    PyArrayObject *lnP_arr = NULL;
    PyArrayObject *lnQ_arr = NULL;
    PyArrayObject *out_arr = NULL;
    // Get pointers for the arrays
    double *P_ptr, *lnP_ptr, *lnQ_ptr, *out_ptr;

    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "OOO", &P_obj, &lnP_obj, &lnQ_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    // Fill the array pointers
    P_arr = (PyArrayObject *)PyArray_FROM_O(P_obj);
    check(P_arr, "Failed to build P_arr.");
    check(PyArray_NDIM(P_arr) == 1, "P array should have only one dimension.");
    lnP_arr = (PyArrayObject *)PyArray_FROM_O(lnP_obj);
    check(lnP_arr, "Failed to build lnP_arr.");
    check(PyArray_NDIM(lnP_arr) == 1, "lnP array should have only one dimension.");
    lnQ_arr = (PyArrayObject *)PyArray_FROM_O(lnQ_obj);
    check(lnQ_arr, "Failed to build lnQ_arr.");
    check(PyArray_NDIM(lnQ_arr) == 2, "lnQ array should have only one dimension.");

    // Check the dimensions
    npts = PyArray_DIM(P_arr, 0);
    check(npts > 0, "npts should be greater than zero.");
    check(PyArray_DIM(lnP_arr, 0) == npts, "dimension mismatch between P and lnP");
    check(PyArray_DIM(lnQ_arr, 1) == npts, "dimension mismatch between P and lnQ.");
    nQ = PyArray_DIM(lnQ_arr, 0);
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
        r = 0;
        out_ptr = PyArray_GETPTR1(out_arr, i);
        for (j = 0; j < npts; j++){
            P_ptr = PyArray_GETPTR1(P_arr, j);
            lnP_ptr = PyArray_GETPTR1(lnP_arr, j);
            lnQ_ptr = PyArray_GETPTR2(lnQ_arr, i, j);
            r += *P_ptr * (*lnP_ptr - *lnQ_ptr);
        }
        *out_ptr = r;
    }
    // Cut out the multithreading nonsense
    Py_END_ALLOW_THREADS
    // Free things
    if (P_arr) {Py_DECREF(P_arr);}
    if (lnP_arr) {Py_DECREF(lnP_arr);}
    if (lnQ_arr) {Py_DECREF(lnQ_arr);}
    // Return output array
    return out_obj;

// Error
error:
    if (P_arr) {Py_DECREF(P_arr);}
    if (lnP_arr) {Py_DECREF(lnP_arr);}
    if (lnQ_arr) {Py_DECREF(lnQ_arr);}
    if (out_obj) {Py_DECREF(out_obj);}
    if (out_arr) {Py_DECREF(out_arr);}
    PyErr_SetString(PyExc_RuntimeError, "C error");
    return NULL;
}

static PyObject *_log_norm_rel_entr(PyObject *self, PyObject *args) {

    // npts will describe the length of our P array
    npy_intp npts = 0;
    // nQ describes the number of Q distributions to loop
    npy_intp nQ = 0;
    // store single value of distance
    double r = 0;
    // Store value for normalizing Q
    double Qc = 0;

    // Loop variables
    npy_intp i = 0, j = 0;
    // Py_objects for inputs and output objects
    PyObject *P_obj = NULL;
    PyObject *lnP_obj = NULL;
    PyObject *lnQ_obj = NULL;
    PyObject *out_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *P_arr = NULL;
    PyArrayObject *lnP_arr = NULL;
    PyArrayObject *lnQ_arr = NULL;
    PyArrayObject *out_arr = NULL;
    // Get pointers for the arrays
    double *P_ptr, *lnP_ptr, *lnQ_ptr, *out_ptr;

    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "OOO", &P_obj, &lnP_obj, &lnQ_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    // Fill the array pointers
    P_arr = (PyArrayObject *)PyArray_FROM_O(P_obj);
    check(P_arr, "Failed to build P_arr.");
    check(PyArray_NDIM(P_arr) == 1, "P array should have only one dimension.");
    lnP_arr = (PyArrayObject *)PyArray_FROM_O(lnP_obj);
    check(lnP_arr, "Failed to build lnP_arr.");
    check(PyArray_NDIM(lnP_arr) == 1, "lnP array should have only one dimension.");
    lnQ_arr = (PyArrayObject *)PyArray_FROM_O(lnQ_obj);
    check(lnQ_arr, "Failed to build lnQ_arr.");
    check(PyArray_NDIM(lnQ_arr) == 2, "lnQ array should have only one dimension.");

    // Check the dimensions
    npts = PyArray_DIM(P_arr, 0);
    check(npts > 0, "npts should be greater than zero.");
    check(PyArray_DIM(lnP_arr, 0) == npts, "dimension mismatch between P and lnP");
    check(PyArray_DIM(lnQ_arr, 1) == npts, "dimension mismatch between P and lnQ.");
    nQ = PyArray_DIM(lnQ_arr, 0);
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
        r = 0;
        Qc = 0;
        // Point at output array
        out_ptr = PyArray_GETPTR1(out_arr, i);
        // Loop to estimate normalization
        for (j = 0; j < npts; j++) {
            lnQ_ptr = PyArray_GETPTR2(lnQ_arr, i, j);
            Qc += exp(*lnQ_ptr);
        }
        // Calculate normalization
        Qc = log(Qc);
        // Loop npts
        for (j = 0; j < npts; j++){
            // Point at input arrays
            P_ptr = PyArray_GETPTR1(P_arr, j);
            lnP_ptr = PyArray_GETPTR1(lnP_arr, j);
            lnQ_ptr = PyArray_GETPTR2(lnQ_arr, i, j);
            // Do calculation
            r += *P_ptr * (*lnP_ptr - (*lnQ_ptr - Qc));
        }
        *out_ptr = r;
    }
    // Cut out the multithreading nonsense
    Py_END_ALLOW_THREADS
    // Free things
    if (P_arr) {Py_DECREF(P_arr);}
    if (lnP_arr) {Py_DECREF(lnP_arr);}
    if (lnQ_arr) {Py_DECREF(lnQ_arr);}
    // Return output array
    return out_obj;

// Error
error:
    if (P_arr) {Py_DECREF(P_arr);}
    if (lnP_arr) {Py_DECREF(lnP_arr);}
    if (lnQ_arr) {Py_DECREF(lnQ_arr);}
    if (out_obj) {Py_DECREF(out_obj);}
    if (out_arr) {Py_DECREF(out_arr);}
    PyErr_SetString(PyExc_RuntimeError, "C error");
    return NULL;
}
