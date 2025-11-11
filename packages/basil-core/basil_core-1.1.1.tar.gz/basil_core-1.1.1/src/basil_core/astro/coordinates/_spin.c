#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#define Py_LIMITED_API 0x030600f0

#include <Python.h>
#include <numpy/arrayobject.h>
#include <numpy/npy_math.h>

/* Define docstrings */
static char module_docstring[] = "Coordinate transformations for spin";
static char _chieff_of_m1_m2_chi1z_chi2z_docstring[] = 
    "Calculate chi effective from components";
static char _chiMinus_of_m1_m2_chi1z_chi2z_docstring[] =
    "Calculate chiMinus from components";
static char _chi1z_of_m1_m2_chieff_chiMinus_docstring[] =
    "Calculate chi1z from m1, m2, chieff, chiMinus";
static char _chi2z_of_m1_m2_chieff_chiMinus_docstring[] =
    "Calculate chi2z from m1, m2, chieff, chiMinus";

/* Declare the C functions here. */
static PyObject *_chieff_of_m1_m2_chi1z_chi2z(PyObject *self, PyObject *args);
static PyObject *_chiMinus_of_m1_m2_chi1z_chi2z(PyObject *self, PyObject *args);
static PyObject *_chi1z_of_m1_m2_chieff_chiMinus(PyObject *self, PyObject *args);
static PyObject *_chi2z_of_m1_m2_chieff_chiMinus(PyObject *self, PyObject *args);


/* Define the methods that will be available on the module. */
static PyMethodDef module_methods[] = {
    {
     "_chieff_of_m1_m2_chi1z_chi2z",
     _chieff_of_m1_m2_chi1z_chi2z,
     METH_VARARGS,
     _chieff_of_m1_m2_chi1z_chi2z_docstring
    },
    {
     "_chiMinus_of_m1_m2_chi1z_chi2z",
     _chiMinus_of_m1_m2_chi1z_chi2z,
     METH_VARARGS,
     _chiMinus_of_m1_m2_chi1z_chi2z_docstring
    },
    {
     "_chi1z_of_m1_m2_chieff_chiMinus",
     _chi1z_of_m1_m2_chieff_chiMinus,
     METH_VARARGS,
     _chi1z_of_m1_m2_chieff_chiMinus_docstring,
    },
    {
     "_chi2z_of_m1_m2_chieff_chiMinus",
     _chi2z_of_m1_m2_chieff_chiMinus,
     METH_VARARGS,
     _chi2z_of_m1_m2_chieff_chiMinus_docstring,
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

MOD_INIT(_spin)
{
    PyObject *m;
    MOD_DEF(m, "_spin", module_docstring, module_methods);
    if (m == NULL)
        return MOD_ERROR_VAL;
    import_array();
    return MOD_SUCCESS_VAL(m);
}

/* Begin the function definitions */
/* Chi effective from m1, m2, chi1z, chi2z */

static PyObject *_chieff_of_m1_m2_chi1z_chi2z(PyObject *self, PyObject *args) {

    long n;
    size_t i = 0;
    double tm1, tm2, tchi1z, tchi2z;
    PyObject *m1_obj, *m2_obj, *chi1z_obj, *chi2z_obj, *result_obj;
    PyArrayObject *m1_array, *m2_array, *chi1z_array, *chi2z_array, *result_array, *arrays[4];
    npy_intp dims[1];
    double *result;
    NpyIter *iter;
    NpyIter_IterNextFunc *iternext;
    char **dataptr;
    npy_intp *strideptr, *innersizeptr;
    PyArray_Descr *dtypes[] = {
                               PyArray_DescrFromType(NPY_DOUBLE),
                               PyArray_DescrFromType(NPY_DOUBLE),
                               PyArray_DescrFromType(NPY_DOUBLE),
                               PyArray_DescrFromType(NPY_DOUBLE)
                              };
    npy_uint32 op_flags[] = {
                             NPY_ITER_READONLY,
                             NPY_ITER_READONLY,
                             NPY_ITER_READONLY,
                             NPY_ITER_READONLY
                            };

    /* Parse the input tuple */
    if (!PyArg_ParseTuple(args, "OOOO", &m1_obj, &m2_obj, &chi1z_obj, &chi2z_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    /* Interpret the input objects as `numpy` arrays */
    m1_array =      (PyArrayObject *)PyArray_FROM_O(m1_obj);
    m2_array =      (PyArrayObject *)PyArray_FROM_O(m2_obj);
    chi1z_array =   (PyArrayObject *)PyArray_FROM_O(chi1z_obj);
    chi2z_array =   (PyArrayObject *)PyArray_FROM_O(chi2z_obj);

    /* If that didn't work, throw an `Exception`. */
    if ((m1_array == NULL) || (m2_array == NULL) || (chi1z_array == NULL) || (chi2z_array == NULL)) {
        PyErr_SetString(PyExc_TypeError, "Couldn't parse the input arrays.");
        Py_XDECREF(m1_array);
        Py_XDECREF(m2_array);
        Py_XDECREF(chi1z_array);
        Py_XDECREF(chi2z_array);
        return NULL;
    }

    /* How many data points are there? */
    n = (long)PyArray_DIM(m1_array, 0);

    /* Check the dimensions. */
    if (
        (n != (long)PyArray_DIM(m2_array, 0)) || 
        (n != (long)PyArray_DIM(chi1z_array, 0)) || 
        (n != (long)PyArray_DIM(chi2z_array, 0))
       ) {
        PyErr_SetString(PyExc_RuntimeError, "Dimension mismatch between x and y");
        Py_DECREF(m1_array);
        Py_DECREF(m2_array);
        Py_DECREF(chi1z_array);
        Py_DECREF(chi2z_array);
    }

    /* Build the output arrays */
    dims[0] = n;
    result_obj = PyArray_ZEROS(1, dims, NPY_DOUBLE, 0);
    if (result_obj == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Couldn't build output array");
        Py_DECREF(m1_array);
        Py_DECREF(m2_array);
        Py_DECREF(chi1z_array);
        Py_DECREF(chi2z_array);
        Py_XDECREF(result_obj);

        return NULL;
    }

    result_array = (PyArrayObject *)result_obj;

    //PyArray_FILLWBYTE(result_array, 0);

    if (n == 0) {
        Py_DECREF(m1_array);
        Py_DECREF(m2_array);
        Py_DECREF(chi1z_array);
        Py_DECREF(chi2z_array);
        return result_obj;
    }

    /* Array Magic */
    arrays[0] = m1_array;
    arrays[1] = m2_array;
    arrays[2] = chi1z_array;
    arrays[3] = chi2z_array;
    iter = NpyIter_AdvancedNew(4, arrays,
                               NPY_ITER_EXTERNAL_LOOP | NPY_ITER_BUFFERED,
                               NPY_KEEPORDER, NPY_SAFE_CASTING, op_flags, dtypes,
                               -1, NULL, NULL, 0);
    if (iter == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Couldn't set up iterator");
        Py_DECREF(m1_array);
        Py_DECREF(m2_array);
        Py_DECREF(chi1z_array);
        Py_DECREF(chi2z_array);
        Py_DECREF(result_obj);
        Py_DECREF(result_array);
        return NULL;
    }
    
    /*
     * The iternext function gets stored in a local variable
     * so it can be called repeatedly in an efficient manner.
     */
    iternext = NpyIter_GetIterNext(iter, NULL);
    if (iternext == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Couldn't set up iterator");
        NpyIter_Deallocate(iter);
        Py_DECREF(m1_array);
        Py_DECREF(m2_array);
        Py_DECREF(chi1z_array);
        Py_DECREF(chi2z_array);
        Py_DECREF(result_obj);
        Py_DECREF(result_array);
        return NULL;
    }
    
    /* The location of the data pointer which the interpolator may update */
    dataptr = NpyIter_GetDataPtrArray(iter);

    /*The location of the stride which the iterator may update */
    strideptr = NpyIter_GetInnerStrideArray(iter);

    /* The location of the inner loop size which the interpolator may update */
    innersizeptr = NpyIter_GetInnerLoopSizePtr(iter);

    /* Pre-compute variables for efficiency in the calculation */
    //

    /* Get C array for output array */
    result = (double *)PyArray_DATA(result_array);

    Py_BEGIN_ALLOW_THREADS

    do {
    
        /* Get the inner loop data/stride/count values */
        npy_intp stride0 = strideptr[0];
        npy_intp stride1 = strideptr[1];
        npy_intp stride2 = strideptr[2];
        npy_intp stride3 = strideptr[3];
        npy_intp size = *innersizeptr;

        /* This is a typical inner loop for NPY_ITER_EXTERNAL_LOOP */
        while (size--) {
            tm1 =       *(double *)dataptr[0];
            tm2 =       *(double *)dataptr[1];
            tchi1z =    *(double *)dataptr[2];
            tchi2z =    *(double *)dataptr[3];
            //mc[i] = ((tm1 * tm2) ** (0.6)) *(tm1 + tm2) ** (-0.2);
            result[i] = ((tm1 * tchi1z) + (tm2 * tchi2z)) / (tm1 + tm2);

            dataptr[0] += stride0;
            dataptr[1] += stride1;
            dataptr[2] += stride2;
            dataptr[3] += stride3;
            i++;
        }

    } while (iternext(iter));

    Py_END_ALLOW_THREADS

    NpyIter_Deallocate(iter);

    /* Clean up. */
    Py_DECREF(m1_array);
    Py_DECREF(m2_array);
    Py_DECREF(chi1z_array);
    Py_DECREF(chi2z_array);

    return result_obj;
}

/* ChiMinus from m1, m2, chi1z, chi2z */

static PyObject *_chiMinus_of_m1_m2_chi1z_chi2z(PyObject *self, PyObject *args) {

    long n;
    size_t i = 0;
    double tm1, tm2, tchi1z, tchi2z;
    PyObject *m1_obj, *m2_obj, *chi1z_obj, *chi2z_obj, *result_obj;
    PyArrayObject *m1_array, *m2_array, *chi1z_array, *chi2z_array, *result_array, *arrays[4];
    npy_intp dims[1];
    double *result;
    NpyIter *iter;
    NpyIter_IterNextFunc *iternext;
    char **dataptr;
    npy_intp *strideptr, *innersizeptr;
    PyArray_Descr *dtypes[] = {
                               PyArray_DescrFromType(NPY_DOUBLE),
                               PyArray_DescrFromType(NPY_DOUBLE),
                               PyArray_DescrFromType(NPY_DOUBLE),
                               PyArray_DescrFromType(NPY_DOUBLE)
                              };
    npy_uint32 op_flags[] = {
                             NPY_ITER_READONLY,
                             NPY_ITER_READONLY,
                             NPY_ITER_READONLY,
                             NPY_ITER_READONLY
                            };

    /* Parse the input tuple */
    if (!PyArg_ParseTuple(args, "OOOO", &m1_obj, &m2_obj, &chi1z_obj, &chi2z_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    /* Interpret the input objects as `numpy` arrays */
    m1_array =      (PyArrayObject *)PyArray_FROM_O(m1_obj);
    m2_array =      (PyArrayObject *)PyArray_FROM_O(m2_obj);
    chi1z_array =   (PyArrayObject *)PyArray_FROM_O(chi1z_obj);
    chi2z_array =   (PyArrayObject *)PyArray_FROM_O(chi2z_obj);

    /* If that didn't work, throw an `Exception`. */
    if ((m1_array == NULL) || (m2_array == NULL) || (chi1z_array == NULL) || (chi2z_array == NULL)) {
        PyErr_SetString(PyExc_TypeError, "Couldn't parse the input arrays.");
        Py_XDECREF(m1_array);
        Py_XDECREF(m2_array);
        Py_XDECREF(chi1z_array);
        Py_XDECREF(chi2z_array);
        return NULL;
    }

    /* How many data points are there? */
    n = (long)PyArray_DIM(m1_array, 0);

    /* Check the dimensions. */
    if (
        (n != (long)PyArray_DIM(m2_array, 0)) || 
        (n != (long)PyArray_DIM(chi1z_array, 0)) || 
        (n != (long)PyArray_DIM(chi2z_array, 0))
       ) {
        PyErr_SetString(PyExc_RuntimeError, "Dimension mismatch between x and y");
        Py_DECREF(m1_array);
        Py_DECREF(m2_array);
        Py_DECREF(chi1z_array);
        Py_DECREF(chi2z_array);
    }

    /* Build the output arrays */
    dims[0] = n;
    result_obj = PyArray_ZEROS(1, dims, NPY_DOUBLE, 0);
    if (result_obj == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Couldn't build output array");
        Py_DECREF(m1_array);
        Py_DECREF(m2_array);
        Py_DECREF(chi1z_array);
        Py_DECREF(chi2z_array);
        Py_XDECREF(result_obj);

        return NULL;
    }

    result_array = (PyArrayObject *)result_obj;

    //PyArray_FILLWBYTE(result_array, 0);

    if (n == 0) {
        Py_DECREF(m1_array);
        Py_DECREF(m2_array);
        Py_DECREF(chi1z_array);
        Py_DECREF(chi2z_array);
        return result_obj;
    }

    /* Array Magic */
    arrays[0] = m1_array;
    arrays[1] = m2_array;
    arrays[2] = chi1z_array;
    arrays[3] = chi2z_array;
    iter = NpyIter_AdvancedNew(4, arrays,
                               NPY_ITER_EXTERNAL_LOOP | NPY_ITER_BUFFERED,
                               NPY_KEEPORDER, NPY_SAFE_CASTING, op_flags, dtypes,
                               -1, NULL, NULL, 0);
    if (iter == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Couldn't set up iterator");
        Py_DECREF(m1_array);
        Py_DECREF(m2_array);
        Py_DECREF(chi1z_array);
        Py_DECREF(chi2z_array);
        Py_DECREF(result_obj);
        Py_DECREF(result_array);
        return NULL;
    }
    
    /*
     * The iternext function gets stored in a local variable
     * so it can be called repeatedly in an efficient manner.
     */
    iternext = NpyIter_GetIterNext(iter, NULL);
    if (iternext == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Couldn't set up iterator");
        NpyIter_Deallocate(iter);
        Py_DECREF(m1_array);
        Py_DECREF(m2_array);
        Py_DECREF(chi1z_array);
        Py_DECREF(chi2z_array);
        Py_DECREF(result_obj);
        Py_DECREF(result_array);
        return NULL;
    }
    
    /* The location of the data pointer which the interpolator may update */
    dataptr = NpyIter_GetDataPtrArray(iter);

    /*The location of the stride which the iterator may update */
    strideptr = NpyIter_GetInnerStrideArray(iter);

    /* The location of the inner loop size which the interpolator may update */
    innersizeptr = NpyIter_GetInnerLoopSizePtr(iter);

    /* Pre-compute variables for efficiency in the calculation */
    //

    /* Get C array for output array */
    result = (double *)PyArray_DATA(result_array);

    Py_BEGIN_ALLOW_THREADS

    do {
    
        /* Get the inner loop data/stride/count values */
        npy_intp stride0 = strideptr[0];
        npy_intp stride1 = strideptr[1];
        npy_intp stride2 = strideptr[2];
        npy_intp stride3 = strideptr[3];
        npy_intp size = *innersizeptr;

        /* This is a typical inner loop for NPY_ITER_EXTERNAL_LOOP */
        while (size--) {
            tm1 =       *(double *)dataptr[0];
            tm2 =       *(double *)dataptr[1];
            tchi1z =    *(double *)dataptr[2];
            tchi2z =    *(double *)dataptr[3];
            //mc[i] = ((tm1 * tm2) ** (0.6)) *(tm1 + tm2) ** (-0.2);
            result[i] = ((tm1 * tchi1z) - (tm2 * tchi2z)) / (tm1 + tm2);

            dataptr[0] += stride0;
            dataptr[1] += stride1;
            dataptr[2] += stride2;
            dataptr[3] += stride3;
            i++;
        }

    } while (iternext(iter));

    Py_END_ALLOW_THREADS

    NpyIter_Deallocate(iter);

    /* Clean up. */
    Py_DECREF(m1_array);
    Py_DECREF(m2_array);
    Py_DECREF(chi1z_array);
    Py_DECREF(chi2z_array);

    return result_obj;
}

/* Chi1z from m1, m2, chi1z, chi2z, chieff, chiMinus */

static PyObject *_chi1z_of_m1_m2_chieff_chiMinus(PyObject *self, PyObject *args) {

    long n;
    size_t i = 0;
    double tm1, tm2, tchieff, tchiMinus;
    PyObject *m1_obj, *m2_obj, *chieff_obj, *chiMinus_obj, *result_obj;
    PyArrayObject *m1_array, *m2_array, *chieff_array, *chiMinus_array, *result_array, *arrays[4];
    npy_intp dims[1];
    double *result;
    NpyIter *iter;
    NpyIter_IterNextFunc *iternext;
    char **dataptr;
    npy_intp *strideptr, *innersizeptr;
    PyArray_Descr *dtypes[] = {
                               PyArray_DescrFromType(NPY_DOUBLE),
                               PyArray_DescrFromType(NPY_DOUBLE),
                               PyArray_DescrFromType(NPY_DOUBLE),
                               PyArray_DescrFromType(NPY_DOUBLE)
                              };
    npy_uint32 op_flags[] = {
                             NPY_ITER_READONLY,
                             NPY_ITER_READONLY,
                             NPY_ITER_READONLY,
                             NPY_ITER_READONLY
                            };

    /* Parse the input tuple */
    if (!PyArg_ParseTuple(args, "OOOO", &m1_obj, &m2_obj, &chieff_obj, &chiMinus_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    /* Interpret the input objects as `numpy` arrays */
    m1_array =      (PyArrayObject *)PyArray_FROM_O(m1_obj);
    m2_array =      (PyArrayObject *)PyArray_FROM_O(m2_obj);
    chieff_array =   (PyArrayObject *)PyArray_FROM_O(chieff_obj);
    chiMinus_array =   (PyArrayObject *)PyArray_FROM_O(chiMinus_obj);

    /* If that didn't work, throw an `Exception`. */
    if ((m1_array == NULL) || (m2_array == NULL) || (chieff_array == NULL) || (chiMinus_array == NULL)) {
        PyErr_SetString(PyExc_TypeError, "Couldn't parse the input arrays.");
        Py_XDECREF(m1_array);
        Py_XDECREF(m2_array);
        Py_XDECREF(chieff_array);
        Py_XDECREF(chiMinus_array);
        return NULL;
    }

    /* How many data points are there? */
    n = (long)PyArray_DIM(m1_array, 0);

    /* Check the dimensions. */
    if (
        (n != (long)PyArray_DIM(m2_array, 0)) || 
        (n != (long)PyArray_DIM(chieff_array, 0)) || 
        (n != (long)PyArray_DIM(chiMinus_array, 0))
       ) {
        PyErr_SetString(PyExc_RuntimeError, "Dimension mismatch between x and y");
        Py_DECREF(m1_array);
        Py_DECREF(m2_array);
        Py_DECREF(chieff_array);
        Py_DECREF(chiMinus_array);
    }

    /* Build the output arrays */
    dims[0] = n;
    result_obj = PyArray_ZEROS(1, dims, NPY_DOUBLE, 0);
    if (result_obj == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Couldn't build output array");
        Py_DECREF(m1_array);
        Py_DECREF(m2_array);
        Py_DECREF(chieff_array);
        Py_DECREF(chiMinus_array);
        Py_XDECREF(result_obj);

        return NULL;
    }

    result_array = (PyArrayObject *)result_obj;

    //PyArray_FILLWBYTE(result_array, 0);

    if (n == 0) {
        Py_DECREF(m1_array);
        Py_DECREF(m2_array);
        Py_DECREF(chieff_array);
        Py_DECREF(chiMinus_array);
        return result_obj;
    }

    /* Array Magic */
    arrays[0] = m1_array;
    arrays[1] = m2_array;
    arrays[2] = chieff_array;
    arrays[3] = chiMinus_array;
    iter = NpyIter_AdvancedNew(4, arrays,
                               NPY_ITER_EXTERNAL_LOOP | NPY_ITER_BUFFERED,
                               NPY_KEEPORDER, NPY_SAFE_CASTING, op_flags, dtypes,
                               -1, NULL, NULL, 0);
    if (iter == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Couldn't set up iterator");
        Py_DECREF(m1_array);
        Py_DECREF(m2_array);
        Py_DECREF(chieff_array);
        Py_DECREF(chiMinus_array);
        Py_DECREF(result_obj);
        Py_DECREF(result_array);
        return NULL;
    }
    
    /*
     * The iternext function gets stored in a local variable
     * so it can be called repeatedly in an efficient manner.
     */
    iternext = NpyIter_GetIterNext(iter, NULL);
    if (iternext == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Couldn't set up iterator");
        NpyIter_Deallocate(iter);
        Py_DECREF(m1_array);
        Py_DECREF(m2_array);
        Py_DECREF(chieff_array);
        Py_DECREF(chiMinus_array);
        Py_DECREF(result_obj);
        Py_DECREF(result_array);
        return NULL;
    }
    
    /* The location of the data pointer which the interpolator may update */
    dataptr = NpyIter_GetDataPtrArray(iter);

    /*The location of the stride which the iterator may update */
    strideptr = NpyIter_GetInnerStrideArray(iter);

    /* The location of the inner loop size which the interpolator may update */
    innersizeptr = NpyIter_GetInnerLoopSizePtr(iter);

    /* Pre-compute variables for efficiency in the calculation */
    //

    /* Get C array for output array */
    result = (double *)PyArray_DATA(result_array);

    Py_BEGIN_ALLOW_THREADS

    do {
    
        /* Get the inner loop data/stride/count values */
        npy_intp stride0 = strideptr[0];
        npy_intp stride1 = strideptr[1];
        npy_intp stride2 = strideptr[2];
        npy_intp stride3 = strideptr[3];
        npy_intp size = *innersizeptr;

        /* This is a typical inner loop for NPY_ITER_EXTERNAL_LOOP */
        while (size--) {
            tm1 =       *(double *)dataptr[0];
            tm2 =       *(double *)dataptr[1];
            tchieff =    *(double *)dataptr[2];
            tchiMinus =    *(double *)dataptr[3];
            //mc[i] = ((tm1 * tm2) ** (0.6)) *(tm1 + tm2) ** (-0.2);
            result[i] = (tm1 + tm2) * (tchieff + tchiMinus) / (2*tm1);
            //result[i] = (tm1 + tm2) * (tchieff - tchiMinus) / (2*tm2);

            dataptr[0] += stride0;
            dataptr[1] += stride1;
            dataptr[2] += stride2;
            dataptr[3] += stride3;
            i++;
        }

    } while (iternext(iter));

    Py_END_ALLOW_THREADS

    NpyIter_Deallocate(iter);

    /* Clean up. */
    Py_DECREF(m1_array);
    Py_DECREF(m2_array);
    Py_DECREF(chieff_array);
    Py_DECREF(chiMinus_array);

    return result_obj;
}

/* Chi2z from m1, m2, chi1z, chi2z, chieff, chiMinus */

static PyObject *_chi2z_of_m1_m2_chieff_chiMinus(PyObject *self, PyObject *args) {

    long n;
    size_t i = 0;
    double tm1, tm2, tchieff, tchiMinus;
    PyObject *m1_obj, *m2_obj, *chieff_obj, *chiMinus_obj, *result_obj;
    PyArrayObject *m1_array, *m2_array, *chieff_array, *chiMinus_array, *result_array, *arrays[4];
    npy_intp dims[1];
    double *result;
    NpyIter *iter;
    NpyIter_IterNextFunc *iternext;
    char **dataptr;
    npy_intp *strideptr, *innersizeptr;
    PyArray_Descr *dtypes[] = {
                               PyArray_DescrFromType(NPY_DOUBLE),
                               PyArray_DescrFromType(NPY_DOUBLE),
                               PyArray_DescrFromType(NPY_DOUBLE),
                               PyArray_DescrFromType(NPY_DOUBLE)
                              };
    npy_uint32 op_flags[] = {
                             NPY_ITER_READONLY,
                             NPY_ITER_READONLY,
                             NPY_ITER_READONLY,
                             NPY_ITER_READONLY
                            };

    /* Parse the input tuple */
    if (!PyArg_ParseTuple(args, "OOOO", &m1_obj, &m2_obj, &chieff_obj, &chiMinus_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    /* Interpret the input objects as `numpy` arrays */
    m1_array =      (PyArrayObject *)PyArray_FROM_O(m1_obj);
    m2_array =      (PyArrayObject *)PyArray_FROM_O(m2_obj);
    chieff_array =   (PyArrayObject *)PyArray_FROM_O(chieff_obj);
    chiMinus_array =   (PyArrayObject *)PyArray_FROM_O(chiMinus_obj);

    /* If that didn't work, throw an `Exception`. */
    if ((m1_array == NULL) || (m2_array == NULL) || (chieff_array == NULL) || (chiMinus_array == NULL)) {
        PyErr_SetString(PyExc_TypeError, "Couldn't parse the input arrays.");
        Py_XDECREF(m1_array);
        Py_XDECREF(m2_array);
        Py_XDECREF(chieff_array);
        Py_XDECREF(chiMinus_array);
        return NULL;
    }

    /* How many data points are there? */
    n = (long)PyArray_DIM(m1_array, 0);

    /* Check the dimensions. */
    if (
        (n != (long)PyArray_DIM(m2_array, 0)) || 
        (n != (long)PyArray_DIM(chieff_array, 0)) || 
        (n != (long)PyArray_DIM(chiMinus_array, 0))
       ) {
        PyErr_SetString(PyExc_RuntimeError, "Dimension mismatch between x and y");
        Py_DECREF(m1_array);
        Py_DECREF(m2_array);
        Py_DECREF(chieff_array);
        Py_DECREF(chiMinus_array);
    }

    /* Build the output arrays */
    dims[0] = n;
    result_obj = PyArray_ZEROS(1, dims, NPY_DOUBLE, 0);
    if (result_obj == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Couldn't build output array");
        Py_DECREF(m1_array);
        Py_DECREF(m2_array);
        Py_DECREF(chieff_array);
        Py_DECREF(chiMinus_array);
        Py_XDECREF(result_obj);

        return NULL;
    }

    result_array = (PyArrayObject *)result_obj;

    //PyArray_FILLWBYTE(result_array, 0);

    if (n == 0) {
        Py_DECREF(m1_array);
        Py_DECREF(m2_array);
        Py_DECREF(chieff_array);
        Py_DECREF(chiMinus_array);
        return result_obj;
    }

    /* Array Magic */
    arrays[0] = m1_array;
    arrays[1] = m2_array;
    arrays[2] = chieff_array;
    arrays[3] = chiMinus_array;
    iter = NpyIter_AdvancedNew(4, arrays,
                               NPY_ITER_EXTERNAL_LOOP | NPY_ITER_BUFFERED,
                               NPY_KEEPORDER, NPY_SAFE_CASTING, op_flags, dtypes,
                               -1, NULL, NULL, 0);
    if (iter == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Couldn't set up iterator");
        Py_DECREF(m1_array);
        Py_DECREF(m2_array);
        Py_DECREF(chieff_array);
        Py_DECREF(chiMinus_array);
        Py_DECREF(result_obj);
        Py_DECREF(result_array);
        return NULL;
    }
    
    /*
     * The iternext function gets stored in a local variable
     * so it can be called repeatedly in an efficient manner.
     */
    iternext = NpyIter_GetIterNext(iter, NULL);
    if (iternext == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Couldn't set up iterator");
        NpyIter_Deallocate(iter);
        Py_DECREF(m1_array);
        Py_DECREF(m2_array);
        Py_DECREF(chieff_array);
        Py_DECREF(chiMinus_array);
        Py_DECREF(result_obj);
        Py_DECREF(result_array);
        return NULL;
    }
    
    /* The location of the data pointer which the interpolator may update */
    dataptr = NpyIter_GetDataPtrArray(iter);

    /*The location of the stride which the iterator may update */
    strideptr = NpyIter_GetInnerStrideArray(iter);

    /* The location of the inner loop size which the interpolator may update */
    innersizeptr = NpyIter_GetInnerLoopSizePtr(iter);

    /* Pre-compute variables for efficiency in the calculation */
    //

    /* Get C array for output array */
    result = (double *)PyArray_DATA(result_array);

    Py_BEGIN_ALLOW_THREADS

    do {
    
        /* Get the inner loop data/stride/count values */
        npy_intp stride0 = strideptr[0];
        npy_intp stride1 = strideptr[1];
        npy_intp stride2 = strideptr[2];
        npy_intp stride3 = strideptr[3];
        npy_intp size = *innersizeptr;

        /* This is a typical inner loop for NPY_ITER_EXTERNAL_LOOP */
        while (size--) {
            tm1 =       *(double *)dataptr[0];
            tm2 =       *(double *)dataptr[1];
            tchieff =    *(double *)dataptr[2];
            tchiMinus =    *(double *)dataptr[3];
            //mc[i] = ((tm1 * tm2) ** (0.6)) *(tm1 + tm2) ** (-0.2);
            //result[i] = (tm1 + tm2) * (tchieff + tchiMinus) / (2*tm1);
            result[i] = (tm1 + tm2) * (tchieff - tchiMinus) / (2*tm2);

            dataptr[0] += stride0;
            dataptr[1] += stride1;
            dataptr[2] += stride2;
            dataptr[3] += stride3;
            i++;
        }

    } while (iternext(iter));

    Py_END_ALLOW_THREADS

    NpyIter_Deallocate(iter);

    /* Clean up. */
    Py_DECREF(m1_array);
    Py_DECREF(m2_array);
    Py_DECREF(chieff_array);
    Py_DECREF(chiMinus_array);

    return result_obj;
}

