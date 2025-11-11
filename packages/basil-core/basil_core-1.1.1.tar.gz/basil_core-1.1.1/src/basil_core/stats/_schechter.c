#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#define Py_LIMITED_API 0x030600f0

#include <Python.h>
#include <numpy/arrayobject.h>
#include <numpy/npy_math.h>
#include "dbg.h"

/* Define docstrings */
static char module_docstring[] = "Schechter functions in C";
static char _schechter_fixed_redshift64_docstring[] = 
    "Return the schecter function pdf for fixed redshift";
static char _schechter_varied_redshift64_docstring[] = 
    "Return the schecter function pdf for varied redshift";

/* Declare the C functions here. */
static PyObject *_schechter_fixed_redshift64(PyObject *self, PyObject *args);
static PyObject *_schechter_varied_redshift64(PyObject *self, PyObject *args);

/* Define the methods that will be available on the module. */
static PyMethodDef module_methods[] = {
    {"_schechter_fixed_redshift64", _schechter_fixed_redshift64, METH_VARARGS, _schechter_fixed_redshift64_docstring},
    {"_schechter_varied_redshift64", _schechter_varied_redshift64, METH_VARARGS, _schechter_varied_redshift64_docstring},
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

MOD_INIT(_schechter)
{
    PyObject *m;
    MOD_DEF(m, "_schechter", module_docstring, module_methods);
    if (m == NULL)
        return MOD_ERROR_VAL;
    import_array();
    return MOD_SUCCESS_VAL(m);
}

/* Begin the function definitions */

static PyObject *_schechter_fixed_redshift64(PyObject *self, PyObject *args) {

    // n will be used to describe the length of the
    // input 'gsm' and output 'psi' arrays
    npy_intp npts = 0;
    // Py_objects for input and output objects
    PyObject *gsm_obj, *psi_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *gsm_array, *psi_array  = NULL;
    // Loop variables
    npy_intp i = 0;
    // Initialize pointers
    double *gsm_ptr, *psi_ptr;
    
    //Initialize the rest of the inputs
    double redshift = 0.;
    double phi0 = 0.;
    double phi1 = 0.;
    double alpha0 = 0.;
    double alpha1 = 0.;
    double M0 = 0.;
    double M1 = 0.;
    double M2 = 0.;
    double gsm_min = 0.;
    double gsm_max = 0.;

    // Initialize other variables we may need
    double phi_scale = 0.;
    double alpha_z = 0.;
    double gsm_scale = 0.;
    double log_const = 0.;
    double gsm_factor = 0;

    /* Parse the input tuple */
    // Python and Numpy interfaces for C have some pretty heavy-handed macros
    // This block parses the input tuple that python will try to pass to C
    // O is just a PyObject
    // see \url{https://docs.python.org/3/c-api/arg.html} for more details
    if (!PyArg_ParseTuple(args, "Oddddddddddi", &gsm_obj, &redshift,
            &phi0, &phi1, &alpha0, &alpha1, &M0, &M1, &M2,
            &gsm_min, &gsm_max, &npts)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    /* Interpret the input objects as `numpy` arrays */
    gsm_array = (PyArrayObject *)PyArray_FROM_O(gsm_obj);

    /* If that didn't work, throw an error. */
    check((gsm_array != NULL),
        "Couldn't parse the input arrays");

    /* How many data points are there? */
    npts = (long)PyArray_DIM(gsm_array, 0);

    /* Build the output arrays */
    psi_obj = PyArray_ZEROS(1, &npts, NPY_FLOAT64, 0);
    check(psi_obj != NULL, "Couldn't build output array");
    psi_array = (PyArrayObject *)psi_obj;

    // Fill output array with zeros
    PyArray_FILLWBYTE(psi_array, -1);

    // Begin math
    phi_scale = phi0 * pow((1. + redshift), phi1);
    alpha_z = 1. + alpha0 + (alpha1 * redshift);
    gsm_scale = M0 + (M1 * redshift) + (M2 * pow(redshift, 2));
    gsm_scale = pow(10, -1. * (gsm_scale));
    // Get natural log of 10
    log_const = log(10);

    // Check if length is zero
    check(npts != 0, "Length of array is zero");

    // Prepare for loop
    Py_BEGIN_ALLOW_THREADS

    // Loop the unique values
    for (i = 0; i < npts; i++){
        // Get unique pointer
        gsm_ptr = PyArray_GETPTR1(gsm_array, i);
        // Get psi pointer
        psi_ptr = PyArray_GETPTR1(psi_array, i);
        // Check mass limits
        if ((*gsm_ptr < gsm_min) | (*gsm_ptr > gsm_max)) {
            continue;
        }
        // Calculate gsm factor
        gsm_factor = (*gsm_ptr) * gsm_scale;
        // Calculate psi
        *psi_ptr = phi_scale * log_const * pow(gsm_factor, alpha_z) * exp(-1. * gsm_factor);
    }
    Py_END_ALLOW_THREADS

    /* Clean up. */
    Py_DECREF(gsm_array);

    return psi_obj;

error:
    if (gsm_array) {Py_DECREF(gsm_array);}
    if (psi_obj) {Py_DECREF(psi_obj);}
    if (psi_array) {Py_DECREF(psi_array);}
    return NULL;
}


static PyObject *_schechter_varied_redshift64(PyObject *self, PyObject *args) {

    // n will be used to describe the length of the
    // input 'gsm' and output 'psi' arrays
    npy_intp npts = 0;
    npy_intp npts_redshift = 0;
    // Py_objects for input and output objects
    PyObject *gsm_obj, *redshift_obj, *psi_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *gsm_array, *redshift_array, *psi_array  = NULL;
    // Loop variables
    npy_intp i = 0;
    // Initialize pointers
    double *gsm_ptr, *redshift_ptr, *psi_ptr;
    
    //Initialize the rest of the inputs
    double phi0 = 0.;
    double phi1 = 0.;
    double alpha0 = 0.;
    double alpha1 = 0.;
    double M0 = 0.;
    double M1 = 0.;
    double M2 = 0.;
    double gsm_min = 0.;
    double gsm_max = 0.;

    // Initialize other variables we may need
    double phi_scale = 0.;
    double alpha_z = 0.;
    double gsm_scale = 0.;
    double log_const = 0.;
    double gsm_factor = 0;

    /* Parse the input tuple */
    // Python and Numpy interfaces for C have some pretty heavy-handed macros
    // This block parses the input tuple that python will try to pass to C
    // O is just a PyObject
    // see \url{https://docs.python.org/3/c-api/arg.html} for more details
    if (!PyArg_ParseTuple(args, "OOdddddddddi", &gsm_obj, &redshift_obj,
            &phi0, &phi1, &alpha0, &alpha1, &M0, &M1, &M2,
            &gsm_min, &gsm_max, &npts)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    /* Interpret the input objects as `numpy` arrays */
    gsm_array = (PyArrayObject *)PyArray_FROM_O(gsm_obj);
    redshift_array = (PyArrayObject *)PyArray_FROM_O(redshift_obj);

    /* If that didn't work, throw an error. */
    check((gsm_array != NULL),
        "Couldn't parse the input arrays");
    check((redshift_array != NULL),
        "Couldn't parse the input arrays");

    /* How many data points are there? */
    npts = (long)PyArray_DIM(gsm_array, 0);
    npts_redshift = (long)PyArray_DIM(gsm_array, 0);
    check(npts == npts_redshift, "gsm and redshift arrays have different lengths");

    /* Build the output arrays */
    psi_obj = PyArray_ZEROS(1, &npts, NPY_FLOAT64, 0);
    check(psi_obj != NULL, "Couldn't build output array");
    psi_array = (PyArrayObject *)psi_obj;

    // Fill output array with zeros
    PyArray_FILLWBYTE(psi_array, -1);

    // Get natural log of 10
    log_const = log(10);

    // Check if length is zero
    check(npts != 0, "Length of array is zero");

    // Prepare for loop
    Py_BEGIN_ALLOW_THREADS

    // Loop the unique values
    for (i = 0; i < npts; i++){
        // Get unique pointer
        gsm_ptr = PyArray_GETPTR1(gsm_array, i);
        // Get unique pointer
        redshift_ptr = PyArray_GETPTR1(redshift_array, i);
        // Get psi pointer
        psi_ptr = PyArray_GETPTR1(psi_array, i);
        // Check mass limits
        if ((*gsm_ptr < gsm_min) | (*gsm_ptr > gsm_max)) {
            continue;
        }
        // Begin math
        phi_scale = phi0 * pow((1. + (*redshift_ptr)), phi1);
        alpha_z = 1. + alpha0 + (alpha1 * (*redshift_ptr));
        gsm_scale = M0 + (M1 * (*redshift_ptr)) + (M2 * pow((*redshift_ptr), 2));
        gsm_scale = pow(10, -1. * (gsm_scale));
        // Calculate gsm factor
        gsm_factor = (*gsm_ptr) * gsm_scale;
        // Calculate psi
        *psi_ptr = phi_scale * log_const * pow(gsm_factor, alpha_z) * exp(-1. * gsm_factor);
    }
    Py_END_ALLOW_THREADS

    /* Clean up. */
    Py_DECREF(gsm_array);
    Py_DECREF(redshift_array);

    return psi_obj;

error:
    if (gsm_array) {Py_DECREF(gsm_array);}
    if (redshift_array) {Py_DECREF(redshift_array);}
    if (psi_obj) {Py_DECREF(psi_obj);}
    if (psi_array) {Py_DECREF(psi_array);}
    return NULL;
}


