#define NP_NO_DEPRECATED_API NPY_1_7_API_VERSION
#define Py_LIMITED_API 0x030600f0

#include <Python.h>
#include <numpy/arrayobject.h>
#include <numpy/npy_math.h>
#include "dbg.h"
#include "_basil_core_astro_const.h"

/* Define docstring */
static char module_docstring[] =
    "Calculate things related to DWD Roche overflow";
static char _DWD_r_of_m_docstring[] =
    "Calculate the WD radius as a function of mass";
static char _DWD_RLOF_a_of_m1_m2_r1_r2_docstring[] =
    "Calculate the DWD Roche Lobe overflow separation.";
static char _DWD_RLOF_P_of_m1_m2_r1_r2_docstring[] =
    "Calculate the DWD Roche Lobe overflow Period.";

/* Declare the C functions here */
static PyObject *_DWD_r_of_m(PyObject *self, PyObject *args);
static PyObject *_DWD_RLOF_a_of_m1_m2_r1_r2(PyObject *self, PyObject *args);
static PyObject *_DWD_RLOF_P_of_m1_m2_r1_r2(PyObject *self, PyObject *args);

/* Define the methods that will be available in the module */
static PyMethodDef module_methods[] = {
    {
    "_DWD_r_of_m",
    _DWD_r_of_m,
    METH_VARARGS,
    _DWD_r_of_m_docstring,
   },
    {
    "_DWD_RLOF_a_of_m1_m2_r1_r2",
    _DWD_RLOF_a_of_m1_m2_r1_r2,
    METH_VARARGS,
    _DWD_RLOF_a_of_m1_m2_r1_r2_docstring,
   },
    {
    "_DWD_RLOF_P_of_m1_m2_r1_r2",
    _DWD_RLOF_P_of_m1_m2_r1_r2,
    METH_VARARGS,
    _DWD_RLOF_P_of_m1_m2_r1_r2_docstring,
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

MOD_INIT(_DWD_RLOF)
{
    PyObject *m;
    MOD_DEF(m, "_DWD_RLOF", module_docstring, module_methods);
    if (m == NULL)
        return MOD_ERROR_VAL;
    import_array();
    return MOD_SUCCESS_VAL(m);
}

/* Define other functions here */

static PyObject *_DWD_r_of_m(PyObject *self, PyObject *args) {

    // npts will describe the length of our P array
    npy_intp npts = 0;
    // Loop variables
    npy_intp i = 0;
    double R_NS = 1.4e-5;
    double m_ratio = 0;
    double a = 0;
    double m_ch_m_2_3 = 0, m_m_ch_2_3 = 0;
    // Py_objects for inputs and output objects
    PyObject *m_obj = NULL;
    PyObject *out_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *m_arr = NULL;
    PyArrayObject *out_arr = NULL;
    // Get pointers for the arrays
    double *m_ptr, *out_ptr;

    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "O", &m_obj)){
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    // Fill the array pointers
    m_arr = (PyArrayObject *)PyArray_FROM_O(m_obj);
    check(m_arr, "Failed to build m_arr.");
    check(PyArray_NDIM(m_arr) == 1, "m array should have only one dimension.");

    // Check the dimensions
    npts = PyArray_DIM(m_arr, 0);
    check(npts > 0, "npts should be greater than zero.");

    // Build output array
    out_obj = PyArray_ZEROS(1, &npts, NPY_DOUBLE, 0);
    check(out_obj, "Failed to build output object.");
    out_arr = (PyArrayObject *)out_obj;
    check(out_arr, "Failed to build output array.");

    // Allow multithreading
    Py_BEGIN_ALLOW_THREADS
    for (i = 0; i < npts; i++){
        m_ptr = PyArray_GETPTR1(m_arr, i);
        out_ptr = PyArray_GETPTR1(out_arr, i);
        m_ratio = ((double) CHANDRASEKHAR_MASS) / (*m_ptr);
        m_ch_m_2_3 = pow(cbrt(m_ratio), 2);
        m_m_ch_2_3 = pow(cbrt(1/m_ratio),2);
        //log_info("m_ptr: %f, M_CH/m_ptr: %f, m_ptr/M_CH: %f", *m_ptr, (CHANDRASEKHAR_MASS/(*m_ptr)), ((*m_ptr) / CHANDRASEKHAR_MASS));
        a = 0.0115 * sqrt(m_ch_m_2_3 - m_m_ch_2_3);
        // get q
        *out_ptr = RSUN * ((R_NS > a) ? R_NS : a);
    }
    // Cut out the multithreading nonsense
    Py_END_ALLOW_THREADS
    // Free things
    if (m_arr) {Py_DECREF(m_arr);}
    // Return output array
    return out_obj;

// Error
error:
    if (m_arr) {Py_DECREF(m_arr);}
    if (out_obj) {Py_DECREF(out_obj);}
    if (out_arr) {Py_DECREF(out_arr);}
    PyErr_SetString(PyExc_RuntimeError, "C error");
    return NULL;
}
static PyObject *_DWD_RLOF_a_of_m1_m2_r1_r2(PyObject *self, PyObject *args) {

    // npts will describe the length of our P array
    npy_intp npts = 0;
    // Loop variables
    npy_intp i = 0;
    // Define constant ((64/5) * G^3 * c^{-3})
    //double beta_factor = (12.8) * pow((double) GGRAV, 3) * pow((double) CLIGHT, -5);
    double q = 0, q_1_3 = 0, q_2_3 = 0, numerator = 0, denominator = 0;
    //double period_factor = 4. * pow(NPY_PI, 2) / GGRAV;
    // Py_objects for inputs and output objects
    PyObject *m1_obj = NULL;
    PyObject *m2_obj = NULL;
    PyObject *r1_obj = NULL;
    PyObject *r2_obj = NULL;
    PyObject *out_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *m1_arr = NULL;
    PyArrayObject *m2_arr = NULL;
    PyArrayObject *r1_arr = NULL;
    PyArrayObject *r2_arr = NULL;
    PyArrayObject *out_arr = NULL;
    // Get pointers for the arrays
    double *m1_ptr, *m2_ptr, *r1_ptr, *r2_ptr, *out_ptr;

    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "OOOO", &m1_obj, &m2_obj, &r1_obj, &r2_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    // Fill the array pointers
    m1_arr = (PyArrayObject *)PyArray_FROM_O(m1_obj);
    check(m1_arr, "Failed to build m1_arr.");
    check(PyArray_NDIM(m1_arr) == 1, "m1 array should have only one dimension.");

    m2_arr = (PyArrayObject *)PyArray_FROM_O(m2_obj);
    check(m2_arr, "Failed to build m2_arr.");
    check(PyArray_NDIM(m2_arr) == 1, "m2 array should have only one dimension.");

    r1_arr = (PyArrayObject *)PyArray_FROM_O(r1_obj);
    check(r1_arr, "Failed to build r1_arr.");
    check(PyArray_NDIM(r1_arr) == 1, "r1 array should have only one dimension.");

    r2_arr = (PyArrayObject *)PyArray_FROM_O(r2_obj);
    check(r2_arr, "Failed to build r2_arr.");
    check(PyArray_NDIM(r2_arr) == 1, "r2 array should have only one dimension.");

    // Check the dimensions
    npts = PyArray_DIM(m1_arr, 0);
    check(npts > 0, "npts should be greater than zero.");
    check(PyArray_DIM(m2_arr, 0) == npts, "dimension mismatch between m1 and m2.");
    check(PyArray_DIM(r1_arr, 0) == npts, "dimension mismatch between m1 and r1.");
    check(PyArray_DIM(r2_arr, 0) == npts, "dimension mismatch between m1 and r2.");

    // Build output array
    out_obj = PyArray_ZEROS(1, &npts, NPY_DOUBLE, 0);
    check(out_obj, "Failed to build output object.");
    out_arr = (PyArrayObject *)out_obj;
    check(out_arr, "Failed to build output array.");

    // Allow multithreading
    Py_BEGIN_ALLOW_THREADS
    for (i = 0; i < npts; i++){
        m1_ptr = PyArray_GETPTR1(m1_arr, i);
        m2_ptr = PyArray_GETPTR1(m2_arr, i);
        r1_ptr = PyArray_GETPTR1(r1_arr, i);
        r2_ptr = PyArray_GETPTR1(r2_arr, i);
        out_ptr = PyArray_GETPTR1(out_arr, i);
        // get q
        q = (*m1_ptr > *m2_ptr ? *m2_ptr : *m1_ptr) / (*m1_ptr > *m2_ptr ? *m1_ptr : *m2_ptr);
        q_1_3 = cbrt(q); 
        q_2_3 = pow(q_1_3, 2);
        numerator = 0.6 * q_2_3 + log(1 + q_1_3);
        denominator = 0.49 * q_2_3;
        *out_ptr = (*m1_ptr > *m2_ptr ? *r2_ptr : *r1_ptr) * numerator / denominator;
    }
    // Cut out the multithreading nonsense
    Py_END_ALLOW_THREADS
    // Free things
    if (m1_arr) {Py_DECREF(m1_arr);}
    if (m2_arr) {Py_DECREF(m2_arr);}
    if (r1_arr) {Py_DECREF(r1_arr);}
    if (r2_arr) {Py_DECREF(r2_arr);}
    // Return output array
    return out_obj;

// Error
error:
    if (m1_arr) {Py_DECREF(m1_arr);}
    if (m2_arr) {Py_DECREF(m2_arr);}
    if (r1_arr) {Py_DECREF(r1_arr);}
    if (r2_arr) {Py_DECREF(r2_arr);}
    if (out_obj) {Py_DECREF(out_obj);}
    if (out_arr) {Py_DECREF(out_arr);}
    PyErr_SetString(PyExc_RuntimeError, "C error");
    return NULL;
}
static PyObject *_DWD_RLOF_P_of_m1_m2_r1_r2(PyObject *self, PyObject *args) {

    // npts will describe the length of our P array
    npy_intp npts = 0;
    // Loop variables
    npy_intp i = 0;
    // Define constant ((64/5) * G^3 * c^{-3})
    //double beta_factor = (12.8) * pow((double) GGRAV, 3) * pow((double) CLIGHT, -5);
    double q = 0, q_1_3 = 0, q_2_3 = 0, numerator = 0, denominator = 0;
    double period_factor = 4. * pow(NPY_PI, 2) / GGRAV;
    double a = 0;
    // Py_objects for inputs and output objects
    PyObject *m1_obj = NULL;
    PyObject *m2_obj = NULL;
    PyObject *r1_obj = NULL;
    PyObject *r2_obj = NULL;
    PyObject *out_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *m1_arr = NULL;
    PyArrayObject *m2_arr = NULL;
    PyArrayObject *r1_arr = NULL;
    PyArrayObject *r2_arr = NULL;
    PyArrayObject *out_arr = NULL;
    // Get pointers for the arrays
    double *m1_ptr, *m2_ptr, *r1_ptr, *r2_ptr, *out_ptr;

    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "OOOO", &m1_obj, &m2_obj, &r1_obj, &r2_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    // Fill the array pointers
    m1_arr = (PyArrayObject *)PyArray_FROM_O(m1_obj);
    check(m1_arr, "Failed to build m1_arr.");
    check(PyArray_NDIM(m1_arr) == 1, "m1 array should have only one dimension.");

    m2_arr = (PyArrayObject *)PyArray_FROM_O(m2_obj);
    check(m2_arr, "Failed to build m2_arr.");
    check(PyArray_NDIM(m2_arr) == 1, "m2 array should have only one dimension.");

    r1_arr = (PyArrayObject *)PyArray_FROM_O(r1_obj);
    check(r1_arr, "Failed to build r1_arr.");
    check(PyArray_NDIM(r1_arr) == 1, "r1 array should have only one dimension.");

    r2_arr = (PyArrayObject *)PyArray_FROM_O(r2_obj);
    check(r2_arr, "Failed to build r2_arr.");
    check(PyArray_NDIM(r2_arr) == 1, "r2 array should have only one dimension.");

    // Check the dimensions
    npts = PyArray_DIM(m1_arr, 0);
    check(npts > 0, "npts should be greater than zero.");
    check(PyArray_DIM(m2_arr, 0) == npts, "dimension mismatch between m1 and m2.");
    check(PyArray_DIM(r1_arr, 0) == npts, "dimension mismatch between m1 and r1.");
    check(PyArray_DIM(r2_arr, 0) == npts, "dimension mismatch between m1 and r2.");

    // Build output array
    out_obj = PyArray_ZEROS(1, &npts, NPY_DOUBLE, 0);
    check(out_obj, "Failed to build output object.");
    out_arr = (PyArrayObject *)out_obj;
    check(out_arr, "Failed to build output array.");

    // Allow multithreading
    Py_BEGIN_ALLOW_THREADS
    for (i = 0; i < npts; i++){
        m1_ptr = PyArray_GETPTR1(m1_arr, i);
        m2_ptr = PyArray_GETPTR1(m2_arr, i);
        r1_ptr = PyArray_GETPTR1(r1_arr, i);
        r2_ptr = PyArray_GETPTR1(r2_arr, i);
        out_ptr = PyArray_GETPTR1(out_arr, i);
        // get q
        q = (*m1_ptr > *m2_ptr ? *m2_ptr : *m1_ptr) / (*m1_ptr > *m2_ptr ? *m1_ptr : *m2_ptr);
        q_1_3 = cbrt(q); 
        q_2_3 = pow(q_1_3, 2);
        numerator = 0.6 * q_2_3 + log(1 + q_1_3);
        denominator = 0.49 * q_2_3;
        a = (*m1_ptr > *m2_ptr ? *r2_ptr : *r1_ptr) * numerator / denominator;
        *out_ptr = sqrt(period_factor * (a * pow(a, 2)) / (*m1_ptr + *m2_ptr));
    }
    // Cut out the multithreading nonsense
    Py_END_ALLOW_THREADS
    // Free things
    if (m1_arr) {Py_DECREF(m1_arr);}
    if (m2_arr) {Py_DECREF(m2_arr);}
    if (r1_arr) {Py_DECREF(r1_arr);}
    if (r2_arr) {Py_DECREF(r2_arr);}
    // Return output array
    return out_obj;

// Error
error:
    if (m1_arr) {Py_DECREF(m1_arr);}
    if (m2_arr) {Py_DECREF(m2_arr);}
    if (r1_arr) {Py_DECREF(r1_arr);}
    if (r2_arr) {Py_DECREF(r2_arr);}
    if (out_obj) {Py_DECREF(out_obj);}
    if (out_arr) {Py_DECREF(out_arr);}
    PyErr_SetString(PyExc_RuntimeError, "C error");
    return NULL;
}
