#define NP_NO_DEPRECATED_API NPY_1_7_API_VERSION
#define Py_LIMITED_API 0x030600f0

#include <Python.h>
#include <numpy/arrayobject.h>
#include <numpy/npy_math.h>
#include "dbg.h"
#include "_basil_core_astro_const.h"

/* Define docstring */
static char module_docstring[] =
    "Gravitational wave orbital decay calculations";
static char _beta_arr_docstring[] =
    "Calculate Beta constant from page 8 of Peters(1964)";
static char _beta_sgl_docstring[] =
    "Calculate Beta constant from page 8 of Peters(1964)";
static char _peters_ecc_const_sgl_docstring[] =
    "Calculate eccentricity part of the constant of motion from Peters(1964)";
static char _peters_ecc_const_arr_docstring[] =
    "Calculate eccentricity part of the constant of motion from Peters(1964)";
static char _peters_ecc_integrand_sgl_docstring[] =
    "Calculate eccentricity integral integrand for orbital decay";
static char _peters_ecc_integrand_arr_docstring[] =
    "Calculate eccentricity integral integrand for orbital decay";
static char _merge_time_circ_sgl_docstring[] =
    "Calculate circular time for orbital decay";
static char _merge_time_circ_arr_docstring[] =
    "Calculate circular time for orbital decay";
static char _orb_sep_evol_circ_sgl_docstring[] =
    "Calculate separation of circular binary as a function of time";
static char _orb_sep_evol_circ_arr_docstring[] =
    "Calculate separation of circular binanies as a function of time";
static char _orb_sep_evol_ecc_integrand_sgl_docstring[] =
    "Calculate separation integrand of eccentric binary as a function of time";
static char _orb_sep_evol_ecc_integrand_arr_docstring[] =
    "Calculate sep integrand of eccentric binanies as a function of time";

/* Declare the C functions here */
static PyObject *_beta_arr(PyObject *self, PyObject *args);
static PyObject *_beta_sgl(PyObject *self, PyObject *args);
static PyObject *_peters_ecc_const_sgl(PyObject *self, PyObject *args);
static PyObject *_peters_ecc_const_arr(PyObject *self, PyObject *args);
static PyObject *_peters_ecc_integrand_sgl(PyObject *self, PyObject *args);
static PyObject *_peters_ecc_integrand_arr(PyObject *self, PyObject *args);
static PyObject *_merge_time_circ_sgl(PyObject *self, PyObject *args);
static PyObject *_merge_time_circ_arr(PyObject *self, PyObject *args);
static PyObject *_orb_sep_evol_circ_sgl(PyObject *self, PyObject *args);
static PyObject *_orb_sep_evol_circ_arr(PyObject *self, PyObject *args);
static PyObject *_orb_sep_evol_ecc_integrand_sgl(PyObject *self, PyObject *args);
static PyObject *_orb_sep_evol_ecc_integrand_arr(PyObject *self, PyObject *args);

/* Define the methods that will be available in the module */
static PyMethodDef module_methods[] = {
    {
    "_beta_arr",
    _beta_arr,
    METH_VARARGS,
    _beta_arr_docstring,
   },
    {
    "_beta_sgl",
    _beta_sgl,
    METH_VARARGS,
    _beta_sgl_docstring,
   },
    {
    "_peters_ecc_const_sgl",
    _peters_ecc_const_sgl,
    METH_VARARGS,
    _peters_ecc_const_sgl_docstring,
   },
    {
    "_peters_ecc_const_arr",
    _peters_ecc_const_arr,
    METH_VARARGS,
    _peters_ecc_const_arr_docstring,
   },
    {
    "_peters_ecc_integrand_sgl",
    _peters_ecc_integrand_sgl,
    METH_VARARGS,
    _peters_ecc_integrand_sgl_docstring,
   },
    {
    "_peters_ecc_integrand_arr",
    _peters_ecc_integrand_arr,
    METH_VARARGS,
    _peters_ecc_integrand_arr_docstring,
   },
    {
    "_merge_time_circ_sgl",
    _merge_time_circ_sgl,
    METH_VARARGS,
    _merge_time_circ_sgl_docstring,
   },
    {
    "_merge_time_circ_arr",
    _merge_time_circ_arr,
    METH_VARARGS,
    _merge_time_circ_arr_docstring,
   },
   {
   "_orb_sep_evol_circ_sgl",
    _orb_sep_evol_circ_sgl,
    METH_VARARGS,
    _orb_sep_evol_circ_sgl_docstring,
   },
   {
   "_orb_sep_evol_circ_arr",
    _orb_sep_evol_circ_arr,
    METH_VARARGS,
    _orb_sep_evol_circ_arr_docstring,
   },
   {
   "_orb_sep_evol_ecc_integrand_sgl",
    _orb_sep_evol_ecc_integrand_sgl,
    METH_VARARGS,
    _orb_sep_evol_ecc_integrand_sgl_docstring,
   },
   {
   "_orb_sep_evol_ecc_integrand_arr",
    _orb_sep_evol_ecc_integrand_arr,
    METH_VARARGS,
    _orb_sep_evol_ecc_integrand_arr_docstring,
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

MOD_INIT(_decay)
{
    PyObject *m;
    MOD_DEF(m, "_decay", module_docstring, module_methods);
    if (m == NULL)
        return MOD_ERROR_VAL;
    import_array();
    return MOD_SUCCESS_VAL(m);
}

/* Define other functions here */

/* Beta array */
static PyObject *_beta_arr(PyObject *self, PyObject *args) {

    // npts will describe the length of our P array
    npy_intp npts = 0;
    // Loop variables
    npy_intp i = 0;
    // Define constant ((64/5) * G^3 * c^{-3})
    double factor = (12.8) * pow((double) GGRAV, 3) * pow((double) CLIGHT, -5);
    // Py_objects for inputs and output objects
    PyObject *m1_obj = NULL;
    PyObject *m2_obj = NULL;
    PyObject *out_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *m1_arr = NULL;
    PyArrayObject *m2_arr = NULL;
    PyArrayObject *out_arr = NULL;
    // Get pointers for the arrays
    double *m1_ptr, *m2_ptr, *out_ptr;

    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "OO", &m1_obj, &m2_obj)) {
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

    // Check the dimensions
    npts = PyArray_DIM(m1_arr, 0);
    check(npts > 0, "npts should be greater than zero.");
    check(PyArray_DIM(m2_arr, 0) == npts, "dimension mismatch between P and Q.");

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
        out_ptr = PyArray_GETPTR1(out_arr, i);
        *out_ptr = factor * (*m1_ptr) * (*m2_ptr) * (*m1_ptr + *m2_ptr);
    }
    // Cut out the multithreading nonsense
    Py_END_ALLOW_THREADS
    // Free things
    if (m1_arr) {Py_DECREF(m1_arr);}
    if (m2_arr) {Py_DECREF(m2_arr);}
    // Return output array
    return out_obj;

// Error
error:
    if (m1_arr) {Py_DECREF(m1_arr);}
    if (m2_arr) {Py_DECREF(m2_arr);}
    if (out_obj) {Py_DECREF(out_obj);}
    if (out_arr) {Py_DECREF(out_arr);}
    PyErr_SetString(PyExc_RuntimeError, "C error");
    return NULL;
}

/* Beta single */
static PyObject *_beta_sgl(PyObject *self, PyObject *args) {

    // Define constant ((64/5) * G^3 * c^{-3})
    double factor = (12.8) * pow((double) GGRAV, 3) * pow((double) CLIGHT, -5);
    // Define inputs
    double m1 = 0.;
    double m2 = 0.;
    // Define output
    PyObject *out_obj = NULL;
    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "dd", &m1, &m2)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }
    // Compute the output
    out_obj = Py_BuildValue("d",factor * m1 * m2 * (m1 + m2));
    return out_obj;
}
/* Peters' eccentricity Pure C */
double peters_ecc_const_c(double ecc) {
    return (1. - pow(ecc,2)) / (pow(ecc,12./19.) * pow(1. + (121./304.) * pow(ecc,2), 870./2299.));
}

/* Peters' eccentricity constant (single) */
static PyObject *_peters_ecc_const_sgl(PyObject *self, PyObject *args) {
    // Define inputs
    double ecc = 0;
    // Define outputs
    PyObject *out_obj = NULL;
    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "d", &ecc)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }
    // Compute the output
    out_obj = Py_BuildValue("d",
        (1. - pow(ecc,2)) / (pow(ecc,12./19.) * pow(1. + (121./304.) * pow(ecc,2), 870./2299.))
    );
    return out_obj;
}

/* Peters' eccentricity constant (array) */
static PyObject *_peters_ecc_const_arr(PyObject *self, PyObject *args) {
    // npts will describe the length of our P array
    npy_intp npts = 0;
    // Loop variables
    npy_intp i = 0;
    // Define constant ((64/5) * G^3 * c^{-3})
    //double factor = (12.8) * pow((double) GGRAV, 3) * pow((double) CLIGHT, -5);
    // Py_objects for inputs and output objects
    PyObject *ecc_obj = NULL;
    PyObject *out_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *ecc_arr = NULL;
    PyArrayObject *out_arr = NULL;
    // Get pointers for the arrays
    double *ecc_ptr, *out_ptr;
    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "O", &ecc_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }
    // Fill the array pointers
    ecc_arr = (PyArrayObject *)PyArray_FROM_O(ecc_obj);
    check(ecc_arr, "Failed to build ecc_arr.");
    check(PyArray_NDIM(ecc_arr) == 1, "ecc array should have only one dimension.");

    // Check the dimensions
    npts = PyArray_DIM(ecc_arr, 0);
    check(npts > 0, "npts should be greater than zero.");
    check(PyArray_DIM(ecc_arr, 0) == npts, "dimension mismatch between P and Q.");

    // Build output array
    out_obj = PyArray_ZEROS(1, &npts, NPY_DOUBLE, 0);
    check(out_obj, "Failed to build output object.");
    out_arr = (PyArrayObject *)out_obj;
    check(out_arr, "Failed to build output array.");

    // Allow multithreading
    Py_BEGIN_ALLOW_THREADS
    for (i = 0; i < npts; i++){
        ecc_ptr = PyArray_GETPTR1(ecc_arr, i);
        out_ptr = PyArray_GETPTR1(out_arr, i);
        *out_ptr = (1. - pow(*ecc_ptr,2)) / (pow(*ecc_ptr,12./19.) * pow(1. + (121./304.) * pow(*ecc_ptr,2), 870./2299.));
    }

    // Cut out the multithreading nonsense
    Py_END_ALLOW_THREADS
    // Free things
    if (ecc_arr) {Py_DECREF(ecc_arr);}
    // Return output array
    return out_obj;

// Error
error:
    if (ecc_arr) {Py_DECREF(ecc_arr);}
    if (out_obj) {Py_DECREF(out_obj);}
    if (out_arr) {Py_DECREF(out_arr);}
    PyErr_SetString(PyExc_RuntimeError, "C error");
    return NULL;
}

/* Peters' eccentricity integrand */
static PyObject *_peters_ecc_integrand_sgl(PyObject *self, PyObject *args) {
    // Define inputs
    double ecc = 0;
    // Define outputs
    PyObject *out_obj = NULL;
    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "d", &ecc)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }
    // Compute the output
    out_obj = Py_BuildValue("d",
        pow(ecc,29./19.) * pow(1 + (121./304.) * pow(ecc,2),1181./2299.) * pow(1 - pow(ecc,2), -3./2.)
    );
    return out_obj;
}

/* Peters' eccentricity integrand (array) */
static PyObject *_peters_ecc_integrand_arr(PyObject *self, PyObject *args) {
    // npts will describe the length of our P array
    npy_intp npts = 0;
    // Loop variables
    npy_intp i = 0;
    // Define constant ((64/5) * G^3 * c^{-3})
    //double factor = (12.8) * pow((double) GGRAV, 3) * pow((double) CLIGHT, -5);
    // Py_objects for inputs and output objects
    PyObject *ecc_obj = NULL;
    PyObject *out_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *ecc_arr = NULL;
    PyArrayObject *out_arr = NULL;
    // Get pointers for the arrays
    double *ecc_ptr, *out_ptr;
    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "O", &ecc_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }
    // Fill the array pointers
    ecc_arr = (PyArrayObject *)PyArray_FROM_O(ecc_obj);
    check(ecc_arr, "Failed to build ecc_arr.");
    check(PyArray_NDIM(ecc_arr) == 1, "ecc array should have only one dimension.");

    // Check the dimensions
    npts = PyArray_DIM(ecc_arr, 0);
    check(npts > 0, "npts should be greater than zero.");
    check(PyArray_DIM(ecc_arr, 0) == npts, "dimension mismatch between P and Q.");

    // Build output array
    out_obj = PyArray_ZEROS(1, &npts, NPY_DOUBLE, 0);
    check(out_obj, "Failed to build output object.");
    out_arr = (PyArrayObject *)out_obj;
    check(out_arr, "Failed to build output array.");

    // Allow multithreading
    Py_BEGIN_ALLOW_THREADS
    for (i = 0; i < npts; i++){
        ecc_ptr = PyArray_GETPTR1(ecc_arr, i);
        out_ptr = PyArray_GETPTR1(out_arr, i);
        *out_ptr = pow(*ecc_ptr,29./19.) * pow(1 + (121./304.) * pow(*ecc_ptr,2),1181./2299.) * pow(1 - pow(*ecc_ptr,2), -3./2.);
    }

    // Cut out the multithreading nonsense
    Py_END_ALLOW_THREADS
    // Free things
    if (ecc_arr) {Py_DECREF(ecc_arr);}
    // Return output array
    return out_obj;

// Error
error:
    if (ecc_arr) {Py_DECREF(ecc_arr);}
    if (out_obj) {Py_DECREF(out_obj);}
    if (out_arr) {Py_DECREF(out_arr);}
    PyErr_SetString(PyExc_RuntimeError, "C error");
    return NULL;
}

static PyObject *_merge_time_circ_arr(PyObject *self, PyObject *args) {

    // npts will describe the length of our P array
    npy_intp npts = 0;
    // Loop variables
    npy_intp i = 0;
    // Define constant ((64/5) * G^3 * c^{-3})
    double beta_factor = (12.8) * pow((double) GGRAV, 3) * pow((double) CLIGHT, -5);
    double beta = 0;
    //double period_factor = 4. * pow(NPY_PI, 2) / GGRAV;
    // Py_objects for inputs and output objects
    PyObject *m1_obj = NULL;
    PyObject *m2_obj = NULL;
    PyObject *a0_obj = NULL;
    PyObject *out_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *m1_arr = NULL;
    PyArrayObject *m2_arr = NULL;
    PyArrayObject *a0_arr = NULL;
    PyArrayObject *out_arr = NULL;
    // Get pointers for the arrays
    double *m1_ptr, *m2_ptr, *a0_ptr, *out_ptr;

    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "OOO", &m1_obj, &m2_obj, &a0_obj)) {
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

    a0_arr = (PyArrayObject *)PyArray_FROM_O(a0_obj);
    check(a0_arr, "Failed to build a0_arr.");
    check(PyArray_NDIM(a0_arr) == 1, "a0 array should have only one dimension.");

    // Check the dimensions
    npts = PyArray_DIM(m1_arr, 0);
    check(npts > 0, "npts should be greater than zero.");
    check(PyArray_DIM(m2_arr, 0) == npts, "dimension mismatch between m1 and m2.");
    check(PyArray_DIM(a0_arr, 0) == npts, "dimension mismatch between m1 and a0.");

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
        a0_ptr = PyArray_GETPTR1(a0_arr, i);
        out_ptr = PyArray_GETPTR1(out_arr, i);
        // estimate beta
        beta = beta_factor * (*m1_ptr) * (*m2_ptr) * (*m1_ptr + *m2_ptr);
        // calculate result
        *out_ptr = pow(pow(*a0_ptr, 2),2) / (4 * beta);
    }
    // Cut out the multithreading nonsense
    Py_END_ALLOW_THREADS
    // Free things
    if (m1_arr) {Py_DECREF(m1_arr);}
    if (m2_arr) {Py_DECREF(m2_arr);}
    if (a0_arr) {Py_DECREF(a0_arr);}
    // Return output array
    return out_obj;

// Error
error:
    if (m1_arr) {Py_DECREF(m1_arr);}
    if (m2_arr) {Py_DECREF(m2_arr);}
    if (a0_arr) {Py_DECREF(a0_arr);}
    if (out_obj) {Py_DECREF(out_obj);}
    if (out_arr) {Py_DECREF(out_arr);}
    PyErr_SetString(PyExc_RuntimeError, "C error");
    return NULL;
}
static PyObject *_merge_time_circ_sgl(PyObject *self, PyObject *args) {
    // Beta constant
    double beta_factor = (12.8) * pow((double) GGRAV, 3) * pow((double) CLIGHT, -5);
    // Define inputs
    double m1 = 0;
    double m2 = 0;
    double a0 = 0;
    // Define outputs
    PyObject *out_obj = NULL;
    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "ddd", &m1, &m2, &a0)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }
    // Compute the output
    out_obj = Py_BuildValue("d",
        pow(pow(a0, 2),2) / (4 * beta_factor * m1 * m2 * (m1+m2))
    );
    return out_obj;
}

static PyObject *_orb_sep_evol_circ_arr(PyObject *self, PyObject *args) {

    // npts will describe the length of our P array
    npy_intp npts = 0;
    // Loop variables
    npy_intp i = 0;
    // Define constant ((64/5) * G^3 * c^{-3})
    double beta_factor = (12.8) * pow((double) GGRAV, 3) * pow((double) CLIGHT, -5);
    double beta = 0;
    // Py_objects for inputs and output objects
    PyObject *m1_obj = NULL;
    PyObject *m2_obj = NULL;
    PyObject *a0_obj = NULL;
    PyObject *t_obj = NULL;
    PyObject *out_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *m1_arr = NULL;
    PyArrayObject *m2_arr = NULL;
    PyArrayObject *a0_arr = NULL;
    PyArrayObject *t_arr = NULL;
    PyArrayObject *out_arr = NULL;
    // Get pointers for the arrays
    double *m1_ptr, *m2_ptr, *a0_ptr, *t_ptr,  *out_ptr;

    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "OOOO", &m1_obj, &m2_obj, &a0_obj, &t_obj)) {
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

    a0_arr = (PyArrayObject *)PyArray_FROM_O(a0_obj);
    check(a0_arr, "Failed to build a0_arr.");
    check(PyArray_NDIM(a0_arr) == 1, "a0 array should have only one dimension.");

    t_arr = (PyArrayObject *)PyArray_FROM_O(t_obj);
    check(t_arr, "Failed to build t_arr.");
    check(PyArray_NDIM(t_arr) == 1, "t array should have only one dimension.");

    // Check the dimensions
    npts = PyArray_DIM(m1_arr, 0);
    check(npts > 0, "npts should be greater than zero.");
    check(PyArray_DIM(m2_arr, 0) == npts, "dimension mismatch between m1 and m2.");
    check(PyArray_DIM(a0_arr, 0) == npts, "dimension mismatch between m1 and a0.");
    check(PyArray_DIM(t_arr, 0) == npts, "dimension mismatch between m1 and t.");

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
        a0_ptr = PyArray_GETPTR1(a0_arr, i);
        t_ptr = PyArray_GETPTR1(t_arr, i);
        out_ptr = PyArray_GETPTR1(out_arr, i);
        beta = beta_factor * (*m1_ptr) * (*m2_ptr) * (*m1_ptr + *m2_ptr);
        *out_ptr = sqrt(sqrt(pow(pow(*a0_ptr, 2),2) - (4 * beta * (*t_ptr))));
    }
    // Cut out the multithreading nonsense
    Py_END_ALLOW_THREADS
    // Free things
    if (m1_arr) {Py_DECREF(m1_arr);}
    if (m2_arr) {Py_DECREF(m2_arr);}
    if (a0_arr) {Py_DECREF(a0_arr);}
    if (t_arr) {Py_DECREF(t_arr);}
    // Return output array
    return out_obj;

// Error
error:
    if (m1_arr) {Py_DECREF(m1_arr);}
    if (m2_arr) {Py_DECREF(m2_arr);}
    if (a0_arr) {Py_DECREF(a0_arr);}
    if (t_arr) {Py_DECREF(t_arr);}
    if (out_obj) {Py_DECREF(out_obj);}
    if (out_arr) {Py_DECREF(out_arr);}
    PyErr_SetString(PyExc_RuntimeError, "C error");
    return NULL;
}
static PyObject *_orb_sep_evol_circ_sgl(PyObject *self, PyObject *args) {
    // Beta constant
    double beta_factor = (12.8) * pow((double) GGRAV, 3) * pow((double) CLIGHT, -5);
    // Define inputs
    double m1 = 0;
    double m2 = 0;
    double a0 = 0;
    double t = 0;
    // Define outputs
    PyObject *out_obj = NULL;
    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "dddd", &m1, &m2, &a0, &t)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }
    // Calculate beta. That's a neat trick
    double beta = beta_factor * m1 * m2 * (m1 + m2);
    // Compute the output
    out_obj = Py_BuildValue("d",
        sqrt(sqrt(pow(pow(a0,2),2) - (4 * beta * t)))
    );
    return out_obj;
}

static PyObject *_orb_sep_evol_ecc_integrand_arr(PyObject *self, PyObject *args) {

    // npts will describe the length of our P array
    npy_intp npts = 0;
    // Loop variables
    npy_intp i = 0;
    // Py_objects for inputs and output objects
    PyObject *ecc = NULL;
    double preamble = 0;
    double c0 = 0;
    PyObject *ecc_obj = NULL;
    PyObject *out_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *ecc_arr = NULL;
    PyArrayObject *out_arr = NULL;
    // Get pointers for the arrays
    double *ecc_ptr,*out_ptr;

    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "ddO", &preamble, &c0, &ecc_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    // Fill the array pointers
    ecc_arr = (PyArrayObject *)PyArray_FROM_O(ecc_obj);
    check(ecc_arr, "Failed to build ecc_arr.");
    check(PyArray_NDIM(ecc_arr) == 1, "ecc array should have only one dimension.");

    // Check the dimensions
    npts = PyArray_DIM(ecc_arr, 0);
    check(npts > 0, "npts should be greater than zero.");

    // Build output array
    out_obj = PyArray_ZEROS(1, &npts, NPY_DOUBLE, 0);
    check(out_obj, "Failed to build output object.");
    out_arr = (PyArrayObject *)out_obj;
    check(out_arr, "Failed to build output array.");

    // Allow multithreading
    Py_BEGIN_ALLOW_THREADS
    for (i = 0; i < npts; i++){
        ecc_ptr = PyArray_GETPTR1(ecc_arr, i);
        out_ptr = PyArray_GETPTR1(out_arr, i);
        double sep = c0 / peters_ecc_const_c(*ecc_ptr);
        *out_ptr = preamble * (*ecc_ptr/pow(sep,4)) * (1. + (121./304.)*pow(*ecc_ptr,2)) / pow(1. - pow(*ecc_ptr,2),5./2.);
    }
    // Cut out the multithreading nonsense
    Py_END_ALLOW_THREADS
    // Free things
    if (ecc_arr) {Py_DECREF(ecc_arr);}
    // Return output array
    return out_obj;

// Error
error:
    if (ecc_arr) {Py_DECREF(ecc_arr);}
    if (out_obj) {Py_DECREF(out_obj);}
    if (out_arr) {Py_DECREF(out_arr);}
    PyErr_SetString(PyExc_RuntimeError, "C error");
    return NULL;
}
static PyObject *_orb_sep_evol_ecc_integrand_sgl(PyObject *self, PyObject *args) {
    // Beta constant
    //double beta_factor = (12.8) * pow((double) GGRAV, 3) * pow((double) CLIGHT, -5);
    // Define inputs
    double c0 = 0;
    double preamble = 0;
    double ecc = 0;
    // Define intermitten steps
    double sep = 0;
    // Define outputs
    PyObject *out_obj = NULL;
    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "ddd", &preamble, &c0, &ecc)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }
    // Calculate separation
    sep = c0 / peters_ecc_const_c(ecc);
    // Compute the output
    out_obj = Py_BuildValue("d",
        preamble * (ecc/pow(sep,4)) * (1. + (121./304.)*pow(ecc,2)) / pow(1. - pow(ecc,2),5./2.)
    );
    return out_obj;
}
