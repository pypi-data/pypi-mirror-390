#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#define Py_LIMITED_API 0x030600f0

#include <Python.h>
#include <numpy/arrayobject.h>
#include <numpy/npy_math.h>

/* Define docstrings */
static char module_docstring[] = "Coordinate transformations for tides";
static char _lambda_tilde_of_eta_lambda1_lambda2_docstring[] =
    "Calculate lambda tilde from components";
static char _delta_lambda_of_eta_lambda1_lambda2_docstring[] =
    "Calculate delta lamba tilde from components";
static char _lambda1_of_eta_lambda_tilde_delta_lambda_docstring[] =
    "Calculate lambda 1 given eta, lambda tilde, and delta lambda tilde";
static char _lambda2_of_eta_lambda_tilde_delta_lambda_docstring[] =
    "Calculate lambda 2 given eta, lambda tilde, and delta lambda tilde";

/* Declare the C functions here. */
static PyObject *_lambda_tilde_of_eta_lambda1_lambda2(PyObject *self, PyObject *args);
static PyObject *_delta_lambda_of_eta_lambda1_lambda2(PyObject *self, PyObject *args);
static PyObject *_lambda1_of_eta_lambda_tilde_delta_lambda(PyObject *self, PyObject *args);
static PyObject *_lambda2_of_eta_lambda_tilde_delta_lambda(PyObject *self, PyObject *args);

/* Define the methods that will be available on the module. */
static PyMethodDef module_methods[] = {
    {
     "_lambda_tilde_of_eta_lambda1_lambda2",
     _lambda_tilde_of_eta_lambda1_lambda2,
     METH_VARARGS,
     _lambda_tilde_of_eta_lambda1_lambda2_docstring
    },
    {
     "_delta_lambda_of_eta_lambda1_lambda2",
     _delta_lambda_of_eta_lambda1_lambda2,
     METH_VARARGS,
     _delta_lambda_of_eta_lambda1_lambda2_docstring
    },
    {
     "_lambda1_of_eta_lambda_tilde_delta_lambda",
     _lambda1_of_eta_lambda_tilde_delta_lambda,
     METH_VARARGS,
     _lambda1_of_eta_lambda_tilde_delta_lambda_docstring,
    },
    {
     "_lambda2_of_eta_lambda_tilde_delta_lambda",
     _lambda2_of_eta_lambda_tilde_delta_lambda,
     METH_VARARGS,
     _lambda2_of_eta_lambda_tilde_delta_lambda_docstring,
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

MOD_INIT(_tides)
{
    PyObject *m;
    MOD_DEF(m, "_tides", module_docstring, module_methods);
    if (m == NULL)
        return MOD_ERROR_VAL;
    import_array();
    return MOD_SUCCESS_VAL(m);
}

/* Begin the function definitions */
/* Chi effective from m1, m2, chi1z, chi2z */

static PyObject *_lambda_tilde_of_eta_lambda1_lambda2(PyObject *self, PyObject *args) {

    long n;
    size_t i = 0;
    double teta, tlambda1, tlambda2;
    double teta2;
    PyObject *eta_obj, *lambda1_obj, *lambda2_obj, *result_obj;
    PyArrayObject *eta_array, *lambda1_array, *lambda2_array, *result_array, *arrays[3];
    npy_intp dims[1];
    double *result;
    NpyIter *iter;
    NpyIter_IterNextFunc *iternext;
    char **dataptr;
    npy_intp *strideptr, *innersizeptr;
    PyArray_Descr *dtypes[] = {
                               PyArray_DescrFromType(NPY_DOUBLE),
                               PyArray_DescrFromType(NPY_DOUBLE),
                               PyArray_DescrFromType(NPY_DOUBLE)
                              };
    npy_uint32 op_flags[] = {
                             NPY_ITER_READONLY,
                             NPY_ITER_READONLY,
                             NPY_ITER_READONLY
                            };

    /* Parse the input tuple */
    if (!PyArg_ParseTuple(args, "OOO", &eta_obj, &lambda1_obj, &lambda2_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    /* Interpret the input objects as `numpy` arrays */
    eta_array =     (PyArrayObject *)PyArray_FROM_O(eta_obj);
    lambda1_array = (PyArrayObject *)PyArray_FROM_O(lambda1_obj);
    lambda2_array = (PyArrayObject *)PyArray_FROM_O(lambda2_obj);

    /* If that didn't work, throw an `Exception`. */
    if ((eta_array == NULL) || (lambda1_array == NULL) || (lambda2_array == NULL)) {
        PyErr_SetString(PyExc_TypeError, "Couldn't parse the input arrays.");
        Py_XDECREF(eta_array);
        Py_XDECREF(lambda1_array);
        Py_XDECREF(lambda2_array);
        return NULL;
    }

    /* How many data points are there? */
    n = (long)PyArray_DIM(eta_array, 0);

    /* Check the dimensions. */
    if (
        (n != (long)PyArray_DIM(lambda1_array, 0)) || 
        (n != (long)PyArray_DIM(lambda2_array, 0))
       ) {
        PyErr_SetString(PyExc_RuntimeError, "Dimension mismatch between x and y");
        Py_DECREF(eta_array);
        Py_DECREF(lambda1_array);
        Py_DECREF(lambda2_array);
    }

    /* Build the output arrays */
    dims[0] = n;
    result_obj = PyArray_ZEROS(1, dims, NPY_DOUBLE, 0);
    if (result_obj == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Couldn't build output array");
        Py_DECREF(eta_array);
        Py_DECREF(lambda1_array);
        Py_DECREF(lambda2_array);
        Py_XDECREF(result_obj);

        return NULL;
    }

    result_array = (PyArrayObject *)result_obj;

    //PyArray_FILLWBYTE(result_array, 0);

    if (n == 0) {
        Py_DECREF(eta_array);
        Py_DECREF(lambda1_array);
        Py_DECREF(lambda2_array);
        return result_obj;
    }

    /* Array Magic */
    arrays[0] = eta_array;
    arrays[1] = lambda1_array;
    arrays[2] = lambda2_array;
    iter = NpyIter_AdvancedNew(3, arrays,
                               NPY_ITER_EXTERNAL_LOOP | NPY_ITER_BUFFERED,
                               NPY_KEEPORDER, NPY_SAFE_CASTING, op_flags, dtypes,
                               -1, NULL, NULL, 0);
    if (iter == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Couldn't set up iterator");
        Py_DECREF(eta_array);
        Py_DECREF(lambda1_array);
        Py_DECREF(lambda2_array);
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
        Py_DECREF(eta_array);
        Py_DECREF(lambda1_array);
        Py_DECREF(lambda2_array);
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
        npy_intp size = *innersizeptr;

        /* This is a typical inner loop for NPY_ITER_EXTERNAL_LOOP */
        while (size--) {
            teta =      *(double *)dataptr[0];
            tlambda1 =  *(double *)dataptr[1];
            tlambda2 =  *(double *)dataptr[2];
            //mc[i] = ((tm1 * tm2) ** (0.6)) *(tm1 + tm2) ** (-0.2);
            //result[i] = ((tm1 * tchi1z) + (tm2 * tchi2z)) / (tm1 + tm2);
            teta2 = teta*teta;
            result[i] = (8./13.)*(((1. + (7.*teta) - (31.*teta2))*(tlambda1 + tlambda2)) +
                (sqrt(1. - (4.*teta)) * (1. + (9.*teta) - (11.0*teta2))*(tlambda1-tlambda2)));

            dataptr[0] += stride0;
            dataptr[1] += stride1;
            dataptr[2] += stride2;
            i++;
        }

    } while (iternext(iter));

    Py_END_ALLOW_THREADS

    NpyIter_Deallocate(iter);

    /* Clean up. */
    Py_DECREF(eta_array);
    Py_DECREF(lambda1_array);
    Py_DECREF(lambda2_array);

    return result_obj;
}

/* Delta lambda tilde */

static PyObject *_delta_lambda_of_eta_lambda1_lambda2(PyObject *self, PyObject *args) {

    long n;
    size_t i = 0;
    double teta, tlambda1, tlambda2;
    double teta2, teta3;
    PyObject *eta_obj, *lambda1_obj, *lambda2_obj, *result_obj;
    PyArrayObject *eta_array, *lambda1_array, *lambda2_array, *result_array, *arrays[3];
    npy_intp dims[1];
    double *result;
    NpyIter *iter;
    NpyIter_IterNextFunc *iternext;
    char **dataptr;
    npy_intp *strideptr, *innersizeptr;
    PyArray_Descr *dtypes[] = {
                               PyArray_DescrFromType(NPY_DOUBLE),
                               PyArray_DescrFromType(NPY_DOUBLE),
                               PyArray_DescrFromType(NPY_DOUBLE)
                              };
    npy_uint32 op_flags[] = {
                             NPY_ITER_READONLY,
                             NPY_ITER_READONLY,
                             NPY_ITER_READONLY
                            };

    /* Parse the input tuple */
    if (!PyArg_ParseTuple(args, "OOO", &eta_obj, &lambda1_obj, &lambda2_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    /* Interpret the input objects as `numpy` arrays */
    eta_array =     (PyArrayObject *)PyArray_FROM_O(eta_obj);
    lambda1_array = (PyArrayObject *)PyArray_FROM_O(lambda1_obj);
    lambda2_array = (PyArrayObject *)PyArray_FROM_O(lambda2_obj);

    /* If that didn't work, throw an `Exception`. */
    if ((eta_array == NULL) || (lambda1_array == NULL) || (lambda2_array == NULL)) {
        PyErr_SetString(PyExc_TypeError, "Couldn't parse the input arrays.");
        Py_XDECREF(eta_array);
        Py_XDECREF(lambda1_array);
        Py_XDECREF(lambda2_array);
        return NULL;
    }

    /* How many data points are there? */
    n = (long)PyArray_DIM(eta_array, 0);

    /* Check the dimensions. */
    if (
        (n != (long)PyArray_DIM(lambda1_array, 0)) || 
        (n != (long)PyArray_DIM(lambda2_array, 0))
       ) {
        PyErr_SetString(PyExc_RuntimeError, "Dimension mismatch between x and y");
        Py_DECREF(eta_array);
        Py_DECREF(lambda1_array);
        Py_DECREF(lambda2_array);
    }

    /* Build the output arrays */
    dims[0] = n;
    result_obj = PyArray_ZEROS(1, dims, NPY_DOUBLE, 0);
    if (result_obj == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Couldn't build output array");
        Py_DECREF(eta_array);
        Py_DECREF(lambda1_array);
        Py_DECREF(lambda2_array);
        Py_XDECREF(result_obj);

        return NULL;
    }

    result_array = (PyArrayObject *)result_obj;

    //PyArray_FILLWBYTE(result_array, 0);

    if (n == 0) {
        Py_DECREF(eta_array);
        Py_DECREF(lambda1_array);
        Py_DECREF(lambda2_array);
        return result_obj;
    }

    /* Array Magic */
    arrays[0] = eta_array;
    arrays[1] = lambda1_array;
    arrays[2] = lambda2_array;
    iter = NpyIter_AdvancedNew(3, arrays,
                               NPY_ITER_EXTERNAL_LOOP | NPY_ITER_BUFFERED,
                               NPY_KEEPORDER, NPY_SAFE_CASTING, op_flags, dtypes,
                               -1, NULL, NULL, 0);
    if (iter == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Couldn't set up iterator");
        Py_DECREF(eta_array);
        Py_DECREF(lambda1_array);
        Py_DECREF(lambda2_array);
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
        Py_DECREF(eta_array);
        Py_DECREF(lambda1_array);
        Py_DECREF(lambda2_array);
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
        npy_intp size = *innersizeptr;

        /* This is a typical inner loop for NPY_ITER_EXTERNAL_LOOP */
        while (size--) {
            teta =      *(double *)dataptr[0];
            tlambda1 =  *(double *)dataptr[1];
            tlambda2 =  *(double *)dataptr[2];
            //mc[i] = ((tm1 * tm2) ** (0.6)) *(tm1 + tm2) ** (-0.2);
            //result[i] = ((tm1 * tchi1z) + (tm2 * tchi2z)) / (tm1 + tm2);
            teta2 = teta*teta;
            teta3 = teta2*teta;
            /*
             *result[i] = 0.5 * (
             *    (sqrt(1.-4.*teta)*(1.0 - 13272.0*teta/1319.0 + 8944.0*teta2/1319.0)*(tlambda1 + tlambda2)) +
             *    (1.0 - 15910.0*teta/1319.0 + 32850.0*teta2/1319.0 + 3380.*teta3/1319.0)*(tlambda1 - tlambda2)
             *                  );
             */

            result[i] = 0.5 * (
                sqrt(1.-4.*teta) * 
                    ((1.0 + ((-13272.0 * teta + 8944.0 * teta2)/1319.0))*(tlambda1 + tlambda2)
                                    ) +
                (1.0 + (-15910.0*teta + 32850.0*teta2 + 3380.*teta3)/1319.0)*(tlambda1 - tlambda2)
                              );

            dataptr[0] += stride0;
            dataptr[1] += stride1;
            dataptr[2] += stride2;
            i++;
        }

    } while (iternext(iter));

    Py_END_ALLOW_THREADS

    NpyIter_Deallocate(iter);

    /* Clean up. */
    Py_DECREF(eta_array);
    Py_DECREF(lambda1_array);
    Py_DECREF(lambda2_array);

    return result_obj;
}

/* Lambda1 from lambda tilde and delta lambda tilde */

static PyObject *_lambda1_of_eta_lambda_tilde_delta_lambda(PyObject *self, PyObject *args) {

    long n;
    size_t i = 0;
    double teta, tlambda_tilde, tdelta_lambda;
    double teta2, teta3;
    double ta, tb, tc, td, den, tdeterminant;
    PyObject *eta_obj, *lambda_tilde_obj, *delta_lambda_obj, *result_obj;
    PyArrayObject *eta_array, *lambda_tilde_array, *delta_lambda_array, *result_array, *arrays[3];
    npy_intp dims[1];
    double *result;
    NpyIter *iter;
    NpyIter_IterNextFunc *iternext;
    char **dataptr;
    npy_intp *strideptr, *innersizeptr;
    PyArray_Descr *dtypes[] = {
                               PyArray_DescrFromType(NPY_DOUBLE),
                               PyArray_DescrFromType(NPY_DOUBLE),
                               PyArray_DescrFromType(NPY_DOUBLE)
                              };
    npy_uint32 op_flags[] = {
                             NPY_ITER_READONLY,
                             NPY_ITER_READONLY,
                             NPY_ITER_READONLY
                            };

    /* Parse the input tuple */
    if (!PyArg_ParseTuple(args, "OOO", &eta_obj, &lambda_tilde_obj, &delta_lambda_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    /* Interpret the input objects as `numpy` arrays */
    eta_array =     (PyArrayObject *)PyArray_FROM_O(eta_obj);
    lambda_tilde_array = (PyArrayObject *)PyArray_FROM_O(lambda_tilde_obj);
    delta_lambda_array = (PyArrayObject *)PyArray_FROM_O(delta_lambda_obj);

    /* If that didn't work, throw an `Exception`. */
    if ((eta_array == NULL) || (lambda_tilde_array == NULL) || (delta_lambda_array == NULL)) {
        PyErr_SetString(PyExc_TypeError, "Couldn't parse the input arrays.");
        Py_XDECREF(eta_array);
        Py_XDECREF(lambda_tilde_array);
        Py_XDECREF(delta_lambda_array);
        return NULL;
    }

    /* How many data points are there? */
    n = (long)PyArray_DIM(eta_array, 0);

    /* Check the dimensions. */
    if (
        (n != (long)PyArray_DIM(lambda_tilde_array, 0)) || 
        (n != (long)PyArray_DIM(delta_lambda_array, 0))
       ) {
        PyErr_SetString(PyExc_RuntimeError, "Dimension mismatch between x and y");
        Py_DECREF(eta_array);
        Py_DECREF(lambda_tilde_array);
        Py_DECREF(delta_lambda_array);
    }

    /* Build the output arrays */
    dims[0] = n;
    result_obj = PyArray_ZEROS(1, dims, NPY_DOUBLE, 0);
    if (result_obj == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Couldn't build output array");
        Py_DECREF(eta_array);
        Py_DECREF(lambda_tilde_array);
        Py_DECREF(delta_lambda_array);
        Py_XDECREF(result_obj);

        return NULL;
    }

    result_array = (PyArrayObject *)result_obj;

    //PyArray_FILLWBYTE(result_array, 0);

    if (n == 0) {
        Py_DECREF(eta_array);
        Py_DECREF(lambda_tilde_array);
        Py_DECREF(delta_lambda_array);
        return result_obj;
    }

    /* Array Magic */
    arrays[0] = eta_array;
    arrays[1] = lambda_tilde_array;
    arrays[2] = delta_lambda_array;
    iter = NpyIter_AdvancedNew(3, arrays,
                               NPY_ITER_EXTERNAL_LOOP | NPY_ITER_BUFFERED,
                               NPY_KEEPORDER, NPY_SAFE_CASTING, op_flags, dtypes,
                               -1, NULL, NULL, 0);
    if (iter == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Couldn't set up iterator");
        Py_DECREF(eta_array);
        Py_DECREF(lambda_tilde_array);
        Py_DECREF(delta_lambda_array);
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
        Py_DECREF(eta_array);
        Py_DECREF(lambda_tilde_array);
        Py_DECREF(delta_lambda_array);
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
        npy_intp size = *innersizeptr;

        /* This is a typical inner loop for NPY_ITER_EXTERNAL_LOOP */
        while (size--) {
            teta =      *(double *)dataptr[0];
            tlambda_tilde =  *(double *)dataptr[1];
            tdelta_lambda =  *(double *)dataptr[2];
            //result[i] = ((tm1 * tchi1z) + (tm2 * tchi2z)) / (tm1 + tm2);
            teta2 = teta*teta;
            teta3 = teta2*teta;
            tdeterminant = sqrt(1. - 4*teta);
            ta = (8./13.)*(1. + 7.*teta - 31.*teta2);
            tb = (8./13.)*tdeterminant*(1. + 9.*teta - 11.*teta2);
            tc = 0.5*tdeterminant*(1. + (-13272.*teta + 8944.0*teta2)/1319.0);
            td = 0.5*(1. + (-15910.*teta + 32850.*teta2 + 3380.*teta3)/1319.0);
            den = ((ta+tb)*(tc-td)) - ((ta-tb)*(tc+td));
            //lambda1
            result[i] = ( (tc-td)*tlambda_tilde - (ta-tb)*tdelta_lambda )/den;
            // lambda2
            //result[i] = (-(tc+td)*tlambda_tilde + (ta+tb)*tdelta_lambda )/den;


            dataptr[0] += stride0;
            dataptr[1] += stride1;
            dataptr[2] += stride2;
            i++;
        }

    } while (iternext(iter));

    Py_END_ALLOW_THREADS

    NpyIter_Deallocate(iter);

    /* Clean up. */
    Py_DECREF(eta_array);
    Py_DECREF(lambda_tilde_array);
    Py_DECREF(delta_lambda_array);

    return result_obj;
}

/* Lambda2 from lambda tilde and delta lambda tilde */

static PyObject *_lambda2_of_eta_lambda_tilde_delta_lambda(PyObject *self, PyObject *args) {

    long n;
    size_t i = 0;
    double teta, tlambda_tilde, tdelta_lambda;
    double teta2, teta3;
    double ta, tb, tc, td, den, tdeterminant;
    PyObject *eta_obj, *lambda_tilde_obj, *delta_lambda_obj, *result_obj;
    PyArrayObject *eta_array, *lambda_tilde_array, *delta_lambda_array, *result_array, *arrays[3];
    npy_intp dims[1];
    double *result;
    NpyIter *iter;
    NpyIter_IterNextFunc *iternext;
    char **dataptr;
    npy_intp *strideptr, *innersizeptr;
    PyArray_Descr *dtypes[] = {
                               PyArray_DescrFromType(NPY_DOUBLE),
                               PyArray_DescrFromType(NPY_DOUBLE),
                               PyArray_DescrFromType(NPY_DOUBLE)
                              };
    npy_uint32 op_flags[] = {
                             NPY_ITER_READONLY,
                             NPY_ITER_READONLY,
                             NPY_ITER_READONLY
                            };

    /* Parse the input tuple */
    if (!PyArg_ParseTuple(args, "OOO", &eta_obj, &lambda_tilde_obj, &delta_lambda_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    /* Interpret the input objects as `numpy` arrays */
    eta_array =     (PyArrayObject *)PyArray_FROM_O(eta_obj);
    lambda_tilde_array = (PyArrayObject *)PyArray_FROM_O(lambda_tilde_obj);
    delta_lambda_array = (PyArrayObject *)PyArray_FROM_O(delta_lambda_obj);

    /* If that didn't work, throw an `Exception`. */
    if ((eta_array == NULL) || (lambda_tilde_array == NULL) || (delta_lambda_array == NULL)) {
        PyErr_SetString(PyExc_TypeError, "Couldn't parse the input arrays.");
        Py_XDECREF(eta_array);
        Py_XDECREF(lambda_tilde_array);
        Py_XDECREF(delta_lambda_array);
        return NULL;
    }

    /* How many data points are there? */
    n = (long)PyArray_DIM(eta_array, 0);

    /* Check the dimensions. */
    if (
        (n != (long)PyArray_DIM(lambda_tilde_array, 0)) || 
        (n != (long)PyArray_DIM(delta_lambda_array, 0))
       ) {
        PyErr_SetString(PyExc_RuntimeError, "Dimension mismatch between x and y");
        Py_DECREF(eta_array);
        Py_DECREF(lambda_tilde_array);
        Py_DECREF(delta_lambda_array);
    }

    /* Build the output arrays */
    dims[0] = n;
    result_obj = PyArray_ZEROS(1, dims, NPY_DOUBLE, 0);
    if (result_obj == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Couldn't build output array");
        Py_DECREF(eta_array);
        Py_DECREF(lambda_tilde_array);
        Py_DECREF(delta_lambda_array);
        Py_XDECREF(result_obj);

        return NULL;
    }

    result_array = (PyArrayObject *)result_obj;

    //PyArray_FILLWBYTE(result_array, 0);

    if (n == 0) {
        Py_DECREF(eta_array);
        Py_DECREF(lambda_tilde_array);
        Py_DECREF(delta_lambda_array);
        return result_obj;
    }

    /* Array Magic */
    arrays[0] = eta_array;
    arrays[1] = lambda_tilde_array;
    arrays[2] = delta_lambda_array;
    iter = NpyIter_AdvancedNew(3, arrays,
                               NPY_ITER_EXTERNAL_LOOP | NPY_ITER_BUFFERED,
                               NPY_KEEPORDER, NPY_SAFE_CASTING, op_flags, dtypes,
                               -1, NULL, NULL, 0);
    if (iter == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Couldn't set up iterator");
        Py_DECREF(eta_array);
        Py_DECREF(lambda_tilde_array);
        Py_DECREF(delta_lambda_array);
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
        Py_DECREF(eta_array);
        Py_DECREF(lambda_tilde_array);
        Py_DECREF(delta_lambda_array);
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
        npy_intp size = *innersizeptr;

        /* This is a typical inner loop for NPY_ITER_EXTERNAL_LOOP */
        while (size--) {
            teta =      *(double *)dataptr[0];
            tlambda_tilde =  *(double *)dataptr[1];
            tdelta_lambda =  *(double *)dataptr[2];
            //result[i] = ((tm1 * tchi1z) + (tm2 * tchi2z)) / (tm1 + tm2);
            teta2 = teta*teta;
            teta3 = teta2*teta;
            tdeterminant = sqrt(1. - 4*teta);
            ta = (8./13.)*(1. + 7.*teta - 31.*teta2);
            tb = (8./13.)*tdeterminant*(1. + 9.*teta - 11.*teta2);
            tc = 0.5*tdeterminant*(1. + (-13272.*teta + 8944.0*teta2)/1319.0);
            td = 0.5*(1. + (-15910.*teta + 32850.*teta2 + 3380.*teta3)/1319.0);
            den = ((ta+tb)*(tc-td)) - ((ta-tb)*(tc+td));
            //lambda1
            //result[i] = ( (tc-td)*tlambda_tilde - (ta-tb)*tdelta_lambda )/den;
            // lambda2
            result[i] = (-(tc+td)*tlambda_tilde + (ta+tb)*tdelta_lambda )/den;


            dataptr[0] += stride0;
            dataptr[1] += stride1;
            dataptr[2] += stride2;
            i++;
        }

    } while (iternext(iter));

    Py_END_ALLOW_THREADS

    NpyIter_Deallocate(iter);

    /* Clean up. */
    Py_DECREF(eta_array);
    Py_DECREF(lambda_tilde_array);
    Py_DECREF(delta_lambda_array);

    return result_obj;
}

