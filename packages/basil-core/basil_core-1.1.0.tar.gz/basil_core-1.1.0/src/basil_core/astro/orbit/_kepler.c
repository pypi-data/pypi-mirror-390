#define NP_NO_DEPRECATED_API NPY_1_7_API_VERSION
#define Py_LIMITED_API 0x030600f0

#include <Python.h>
#include <numpy/arrayobject.h>
#include <numpy/npy_math.h>
#include "dbg.h"
#include "_basil_core_astro_const.h"

/* Define docstring */
static char module_docstring[] =
    "Kepler coordinates and calculations";
static char _orbital_period_of_m1_m2_a_sgl_docstring[] =
    "Calculate the orbital period using Kepler's equations.";
static char _orbital_period_of_m1_m2_a_arr_docstring[] =
    "Calculate the orbital period using Kepler's equations.";

/* Declare the C functions here */
static PyObject *_orbital_period_of_m1_m2_a_sgl(PyObject *self, PyObject *args);
static PyObject *_orbital_period_of_m1_m2_a_arr(PyObject *self, PyObject *args);

/* Define the methods that will be available in the module */
static PyMethodDef module_methods[] = {
    {
    "_orbital_period_of_m1_m2_a_sgl",
    _orbital_period_of_m1_m2_a_sgl,
    METH_VARARGS,
    _orbital_period_of_m1_m2_a_sgl_docstring,
   },
    {
    "_orbital_period_of_m1_m2_a_arr",
    _orbital_period_of_m1_m2_a_arr,
    METH_VARARGS,
    _orbital_period_of_m1_m2_a_arr_docstring,
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

MOD_INIT(_kepler)
{
    PyObject *m;
    MOD_DEF(m, "_kepler", module_docstring, module_methods);
    if (m == NULL)
        return MOD_ERROR_VAL;
    import_array();
    return MOD_SUCCESS_VAL(m);
}

/* Define other functions here */

static PyObject *_orbital_period_of_m1_m2_a_sgl(PyObject *self, PyObject *args) {
    // Constant
    double period_factor = 4. * pow(NPY_PI, 2) / GGRAV;
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
        sqrt(period_factor * (a0 * pow(a0, 2)) / (m1 + m2))
    );
    return out_obj;
}

static PyObject *_orbital_period_of_m1_m2_a_arr(PyObject *self, PyObject *args) {

    // npts will describe the length of our P array
    npy_intp npts = 0;
    // Loop variables
    npy_intp i = 0;
    // Define constant ((64/5) * G^3 * c^{-3})
    //double beta_factor = (12.8) * pow((double) GGRAV, 3) * pow((double) CLIGHT, -5);
    double period_factor = 4. * pow(NPY_PI, 2) / GGRAV;
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
        //beta = beta_factor * (*m1_ptr) * (*m2_ptr) * (*m1_ptr + *m2_ptr);
        //*out_ptr = sqrt(sqrt(pow(*a0_ptr, 4) - (4 * beta * (*t_ptr))));
        *out_ptr = sqrt(period_factor * (*a0_ptr * pow(*a0_ptr, 2)) / (*m1_ptr + *m2_ptr));
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

