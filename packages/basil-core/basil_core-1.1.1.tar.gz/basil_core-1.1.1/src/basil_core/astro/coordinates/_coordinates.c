#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#define Py_LIMITED_API 0x030600f0

#include <Python.h>
#include <numpy/arrayobject.h>
#include <numpy/npy_math.h>
#include "dbg.h"

/* Define docstrings */
static char module_docstring[] = "Coordinate transformations for xevra";
static char _mc_of_m1_m2_docstring[] = "Convert m1 and m2 to mc";
static char _eta_of_m1_m2_docstring[] = "Convert m1 and m2 to eta";
static char _M_of_mc_eta_docstring[] = "Convert mc and eta to M";
static char _m1_of_M_eta_docstring[] = "Convert M and eta to m1";
static char _m2_of_M_eta_docstring[] = "Convert M and eta to m2";
static char _detector_of_source_docstring[] = 
    "Convert source frame mass to detector frame";
static char _source_of_detector_docstring[] =
    "Convert detector frame mass to source frame";

/* Declare the C functions here. */
static PyObject *_mc_of_m1_m2(PyObject *self, PyObject *args);
static PyObject *_eta_of_m1_m2(PyObject *self, PyObject *args);
static PyObject *_M_of_mc_eta(PyObject *self, PyObject *args);
static PyObject *_m1_of_M_eta(PyObject *self, PyObject *args);
static PyObject *_m2_of_M_eta(PyObject *self, PyObject *args);
static PyObject *_detector_of_source(PyObject *self, PyObject *args);
static PyObject *_source_of_detector(PyObject *self, PyObject *args);


/* Define the methods that will be available on the module. */
static PyMethodDef module_methods[] = {
    {"_mc_of_m1_m2", _mc_of_m1_m2, METH_VARARGS, _mc_of_m1_m2_docstring},
    {"_eta_of_m1_m2", _eta_of_m1_m2, METH_VARARGS, _eta_of_m1_m2_docstring},
    {"_M_of_mc_eta", _M_of_mc_eta, METH_VARARGS, _M_of_mc_eta_docstring},
    {"_m1_of_M_eta", _m1_of_M_eta, METH_VARARGS, _m1_of_M_eta_docstring},
    {"_m2_of_M_eta", _m2_of_M_eta, METH_VARARGS, _m2_of_M_eta_docstring},
    {"_detector_of_source", _detector_of_source, METH_VARARGS,
        _detector_of_source_docstring},
    {"_source_of_detector", _source_of_detector, METH_VARARGS,
        _source_of_detector_docstring},
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

MOD_INIT(_coordinates)
{
    PyObject *m;
    MOD_DEF(m, "_coordinates", module_docstring, module_methods);
    if (m == NULL)
        return MOD_ERROR_VAL;
    import_array();
    return MOD_SUCCESS_VAL(m);
}

/* Begin the function definitions */

static PyObject *_mc_of_m1_m2(PyObject *self, PyObject *args) {

    // n will be used to describe the length of the input and output arrays
    npy_intp n = 0;
    // Loop variable
    size_t i = 0;
    // Variables for math inside the loop
    double tm1, tm2;
    // Pyo_bjects for input and output objects
    PyObject *m1_obj, *m2_obj, *mc_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *m1_array, *m2_array, *mc_array  = NULL;
    // List of PyObjects to hold arrays (for iter)
    PyArrayObject *arrays[2];
    // Numpy intp??? holds dimensions
    npy_intp dims[1];
    // Point to mc???
    double *mc;
    // Initialize numpy iterator
    NpyIter *iter = NULL;
    // Initialize numpy next iteration pointer
    NpyIter_IterNextFunc *iternext;
    // Initialize pointer to data
    char **dataptr;
    // Initialize more numpy objects ???
    npy_intp *strideptr, *innersizeptr;
    // Initialize list of dtypes, and assign numpy double precision numbers
    // Matches dims of arrays
    PyArray_Descr *dtypes[] = {PyArray_DescrFromType(NPY_DOUBLE), PyArray_DescrFromType(NPY_DOUBLE)};
    // Assign flags for numpy array operations 
    // Matches dims of arrays
    npy_uint32 op_flags[] = {NPY_ITER_READONLY, NPY_ITER_READONLY};

    /* Parse the input tuple */
    // Python and Numpy interfaces for C have some pretty heavy-handed macros
    // This block parses the input tuple that python will try to pass to C
    // O is just a PyObject
    // see \url{https://docs.python.org/3/c-api/arg.html} for more details
    if (!PyArg_ParseTuple(args, "OO", &m1_obj, &m2_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    /* Interpret the input objects as `numpy` arrays */
    m1_array = (PyArrayObject *)PyArray_FROM_O(m1_obj);
    m2_array = (PyArrayObject *)PyArray_FROM_O(m2_obj);

    /* If that didn't work, throw an error. */
    check((m1_array != NULL && m2_array != NULL),
        "Couldn't parse the input arrays");

    /* How many data points are there? */
    n = (long)PyArray_DIM(m1_array, 0);

    /* Check the dimensions. */
    check((n == (long)PyArray_DIM(m2_array, 0)),
        "Dimension mismatch between x and y");

    /* Build the output arrays */
    dims[0] = n;
    //mc_obj = PyArray_SimpleNew(1, dims, NPY_DOUBLE);
    mc_obj = PyArray_ZEROS(1, dims, NPY_DOUBLE, 0);
    check(mc_obj != NULL, "Couldn't build output array");
    mc_array = (PyArrayObject *)mc_obj;

    //PyArray_FILLWBYTE(mc_array, 0);
    
    // Check if length is zero
    check(n != 0, "Length of array is zero");

    /* Array Magic */
    // arrays is a list of pointers. 
    // We are giving it the address for both of our input arrays
    arrays[0] = m1_array;
    arrays[1] = m2_array;
    // We are generating a new Numpy Iterator
    // Most of these are just flags
    /*
     * NpyIter *NpyIter_AdvancedNew(
     *      npy_intp nop, // Number of arrays
     *      PyArrayObject **op, // Your list of arrays
     *      npy_uint32 flags, //Oter f;ags
     *      NPY_ORDER order, // order flags
     *      NPY_CASTING casting, // Use safe casting
     *      npy_uint32 *op_flags, // More flags
     *      PyArray_Descr **op_dtypes, // Specifies dtype of each array
     *      int oa_ndim, // specifies the number of dimensions that will
     *                   //     be iterated with customized broadcasting
     *      int **op_axes, // used with positive values of oa_ndim
     *      npy_intp const *itershape, // used with positive values of oa_ndim
     *      npy_intp buffersize // zero -> default buffersize
     * )
     */
    iter = NpyIter_AdvancedNew(2, arrays,
                               NPY_ITER_EXTERNAL_LOOP | NPY_ITER_BUFFERED,
                               NPY_KEEPORDER, NPY_SAFE_CASTING, op_flags, dtypes,
                               -1, NULL, NULL, 0);
    check(iter != NULL, "Couldn't set up iterator");
    
    /*
     * The iternext function gets stored in a local variable
     * so it can be called repeatedly in an efficient manner.
     * NpyIter_IterNextFunc* NpyIter_GetIterNext(NpyIter* iter, char ** errmsg)
     */
    iternext = NpyIter_GetIterNext(iter, NULL);
    check(iternext != NULL, "Couldn't set up iterator");
    
    /* The location of the data pointer which the interator may update */
    dataptr = NpyIter_GetDataPtrArray(iter);

    /*The location of the stride which the iterator may update */
    strideptr = NpyIter_GetInnerStrideArray(iter);

    /* The location of the inner loop size which the interator may update */
    innersizeptr = NpyIter_GetInnerLoopSizePtr(iter);

    /* Pre-compute variables for efficiency in the calculation */
    //

    /* Get C array for output array */
    mc = (double *)PyArray_DATA(mc_array);

    Py_BEGIN_ALLOW_THREADS

    do {
    
        /* Get the inner loop data/stride/count values */
        npy_intp stride0 = strideptr[0];
        npy_intp stride1 = strideptr[1];
        npy_intp size = *innersizeptr;

        /* This is a typical inner loop for NPY_ITER_EXTERNAL_LOOP */
        while (size--) {
            tm1 = *(double *)dataptr[0];
            tm2 = *(double *)dataptr[1];
            //mc[i] = ((tm1 * tm2) ** (0.6)) *(tm1 + tm2) ** (-0.2);
            mc[i] = pow(tm1 * tm2, 0.6) * pow(tm1 + tm2, -0.2);

            dataptr[0] += stride0;
            dataptr[1] += stride1;
            i++;
        }

    } while (iternext(iter));

    Py_END_ALLOW_THREADS

    NpyIter_Deallocate(iter);

    /* Clean up. */
    Py_DECREF(m1_array);
    Py_DECREF(m2_array);

    return mc_obj;

error:
    if (iter) {NpyIter_Deallocate(iter);}
    if (m1_array) {Py_DECREF(m1_array);}
    if (m2_array) {Py_DECREF(m2_array);}
    if (mc_obj) {Py_DECREF(mc_obj);}
    if (mc_array) {Py_DECREF(mc_array);}
    return NULL;
}


/* eta of m1 and m2 */

static PyObject *_eta_of_m1_m2(PyObject *self, PyObject *args) {

    npy_intp n = 0;
    size_t i = 0;
    double tm1, tm2;
    PyObject *m1_obj, *m2_obj, *eta_obj = NULL;
    PyArrayObject *m1_array, *m2_array, *eta_array = NULL;
    PyArrayObject *arrays[2];
    npy_intp dims[1];
    double *eta;
    NpyIter *iter = NULL;
    NpyIter_IterNextFunc *iternext;
    char **dataptr;
    npy_intp *strideptr, *innersizeptr;
    PyArray_Descr *dtypes[] = {PyArray_DescrFromType(NPY_DOUBLE), PyArray_DescrFromType(NPY_DOUBLE)};
    npy_uint32 op_flags[] = {NPY_ITER_READONLY, NPY_ITER_READONLY};

    /* Parse the input tuple */
    if (!PyArg_ParseTuple(args, "OO", &m1_obj, &m2_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    /* Interpret the input objects as `numpy` arrays */
    m1_array = (PyArrayObject *)PyArray_FROM_O(m1_obj);
    m2_array = (PyArrayObject *)PyArray_FROM_O(m2_obj);

    /* If that didn't work, throw an `Exception`. */
    check((m1_array != NULL && m2_array != NULL),
        "Couldn't parse the input arrays");

    /* How many data points are there? */
    n = (long)PyArray_DIM(m1_array, 0);

    /* Check the dimensions. */
    check(n == (long)PyArray_DIM(m2_array, 0),
        "Dimension mismatch between x and y");

    /* Build the output arrays */
    dims[0] = n;
    eta_obj = PyArray_ZEROS(1, dims, NPY_DOUBLE, 0);
    check(eta_obj != NULL,
        "Couldn't build output array.");
    eta_array = (PyArrayObject *)eta_obj;

    //PyArray_FILLWBYTE(eta_array, 0);

    // Check if length is zero
    check(n != 0, "Length of array is zero.");

    /* Array Magic */
    arrays[0] = m1_array;
    arrays[1] = m2_array;
    iter = NpyIter_AdvancedNew(2, arrays,
                               NPY_ITER_EXTERNAL_LOOP | NPY_ITER_BUFFERED,
                               NPY_KEEPORDER, NPY_SAFE_CASTING, op_flags, dtypes,
                               -1, NULL, NULL, 0);
    check(iter != NULL, "Couldn't set up the iterator.");
    
    /*
     * The iternext function gets stored in a local variable
     * so it can be called repeatedly in an efficient manner.
     */
    iternext = NpyIter_GetIterNext(iter, NULL);
    check(iternext != NULL, "Couldn't set up the iterator.");
    
    /* The location of the data pointer which the iterator may update */
    dataptr = NpyIter_GetDataPtrArray(iter);

    /*The location of the stride which the iterator may update */
    strideptr = NpyIter_GetInnerStrideArray(iter);

    /* The location of the inner loop size which the iterator may update */
    innersizeptr = NpyIter_GetInnerLoopSizePtr(iter);

    /* Pre-compute variables for efficiency in the calculation */
    //

    /* Get C array for output array */
    eta = (double *)PyArray_DATA(eta_array);

    Py_BEGIN_ALLOW_THREADS

    do {
    
        /* Get the inner loop data/stride/count values */
        npy_intp stride0 = strideptr[0];
        npy_intp stride1 = strideptr[1];
        npy_intp size = *innersizeptr;

        /* This is a typical inner loop for NPY_ITER_EXTERNAL_LOOP */
        while (size--) {
            tm1 = *(double *)dataptr[0];
            tm2 = *(double *)dataptr[1];
            //mc[i] = ((tm1 * tm2) ** (0.6)) *(tm1 + tm2) ** (-0.2);
            eta[i] = (tm1*tm2) / ((tm1 + tm2) * (tm1 + tm2));

            dataptr[0] += stride0;
            dataptr[1] += stride1;
            i++;
        }

    } while (iternext(iter));

    Py_END_ALLOW_THREADS

    NpyIter_Deallocate(iter);

    /* Clean up. */
    Py_DECREF(m1_array);
    Py_DECREF(m2_array);

    return eta_obj;
error:
    if (iter) {NpyIter_Deallocate(iter);}
    if (m1_array) {Py_DECREF(m1_array);}
    if (m2_array) {Py_DECREF(m2_array);}
    if (eta_obj) {Py_DECREF(eta_obj);}
    if (eta_array) {Py_DECREF(eta_array);}
    return NULL;
}



/* M of mc and eta */

static PyObject *_M_of_mc_eta(PyObject *self, PyObject *args) {

    npy_intp n = 0;
    size_t i = 0;
    double tmc, teta;
    PyObject *mc_obj, *eta_obj, *M_obj = NULL;
    PyArrayObject *mc_array, *eta_array, *M_array = NULL;
    PyArrayObject *arrays[2];
    npy_intp dims[1];
    double *M;
    NpyIter *iter = NULL;
    NpyIter_IterNextFunc *iternext;
    char **dataptr;
    npy_intp *strideptr, *innersizeptr;
    PyArray_Descr *dtypes[] = {PyArray_DescrFromType(NPY_DOUBLE), PyArray_DescrFromType(NPY_DOUBLE)};
    npy_uint32 op_flags[] = {NPY_ITER_READONLY, NPY_ITER_READONLY};

    /* Parse the input tuple */
    if (!PyArg_ParseTuple(args, "OO", &mc_obj, &eta_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    /* Interpret the input objects as `numpy` arrays */
    mc_array = (PyArrayObject *)PyArray_FROM_O(mc_obj);
    eta_array = (PyArrayObject *)PyArray_FROM_O(eta_obj);

    /* If that didn't work, throw an `Exception`. */
    check((mc_array != NULL && eta_array != NULL),
        "Couldn't parse the input arrays");

    /* How many data points are there? */
    n = (long)PyArray_DIM(mc_array, 0);

    /* Check the dimensions. */
    if (n != (long)PyArray_DIM(eta_array, 0)) {
        PyErr_SetString(PyExc_RuntimeError, "Dimension mismatch between x and y");
        Py_DECREF(mc_array);
        Py_DECREF(eta_array);
    }

    /* Build the output arrays */
    dims[0] = n;
    M_obj = PyArray_ZEROS(1, dims, NPY_DOUBLE, 0);
    check(M_obj != NULL, "Couldn't build output array.");

    M_array = (PyArrayObject *)M_obj;

    //PyArray_FILLWBYTE(M_array, 0);

    check(n != 0, "Length of array is zero");

    /* Array Magic */
    arrays[0] = mc_array;
    arrays[1] = eta_array;
    iter = NpyIter_AdvancedNew(2, arrays,
                               NPY_ITER_EXTERNAL_LOOP | NPY_ITER_BUFFERED,
                               NPY_KEEPORDER, NPY_SAFE_CASTING, op_flags, dtypes,
                               -1, NULL, NULL, 0);
    check(iter != NULL, "Couldn't set up iterator.");
    
    /*
     * The iternext function gets stored in a local variable
     * so it can be called repeatedly in an efficient manner.
     */
    iternext = NpyIter_GetIterNext(iter, NULL);
    check(iternext != NULL, "Couldn't set up iterator");
    
    /* The location of the data pointer which the iterator may update */
    dataptr = NpyIter_GetDataPtrArray(iter);

    /*The location of the stride which the iterator may update */
    strideptr = NpyIter_GetInnerStrideArray(iter);

    /* The location of the inner loop size which the iterator may update */
    innersizeptr = NpyIter_GetInnerLoopSizePtr(iter);

    /* Pre-compute variables for efficiency in the calculation */
    //

    /* Get C array for output array */
    M = (double *)PyArray_DATA(M_array);

    Py_BEGIN_ALLOW_THREADS

    do {
    
        /* Get the inner loop data/stride/count values */
        npy_intp stride0 = strideptr[0];
        npy_intp stride1 = strideptr[1];
        npy_intp size = *innersizeptr;

        /* This is a typical inner loop for NPY_ITER_EXTERNAL_LOOP */
        while (size--) {
            tmc = *(double *)dataptr[0];
            teta = *(double *)dataptr[1];
            //mc[i] = ((tm1 * tm2) ** (0.6)) *(tm1 + tm2) ** (-0.2);
            //eta[i] = (tm1*tm2) / ((tm1 + tm2) * (tm1 + tm2));
            M[i] = tmc * pow(teta,-0.6);

            dataptr[0] += stride0;
            dataptr[1] += stride1;
            i++;
        }

    } while (iternext(iter));

    Py_END_ALLOW_THREADS

    NpyIter_Deallocate(iter);

    /* Clean up. */
    Py_DECREF(mc_array);
    Py_DECREF(eta_array);

    return M_obj;
error:
    if (iter) {NpyIter_Deallocate(iter);}
    if (mc_array) {Py_DECREF(mc_array);}
    if (eta_array) {Py_DECREF(eta_array);}
    if (M_obj) {Py_DECREF(M_obj);}
    if (M_array) {Py_DECREF(M_array);}
    return NULL;
}

/* m1 of M and eta */

static PyObject *_m1_of_M_eta(PyObject *self, PyObject *args) {

    npy_intp n = 0;
    size_t i = 0;
    double tM, teta;
    PyObject *M_obj, *eta_obj, *m1_obj = NULL;
    PyArrayObject *M_array, *eta_array, *m1_array = NULL;
    PyArrayObject *arrays[2];
    npy_intp dims[1];
    double *m1;
    NpyIter *iter = NULL;
    NpyIter_IterNextFunc *iternext;
    char **dataptr;
    npy_intp *strideptr, *innersizeptr;
    PyArray_Descr *dtypes[] = {PyArray_DescrFromType(NPY_DOUBLE), PyArray_DescrFromType(NPY_DOUBLE)};
    npy_uint32 op_flags[] = {NPY_ITER_READONLY, NPY_ITER_READONLY};

    /* Parse the input tuple */
    if (!PyArg_ParseTuple(args, "OO", &M_obj, &eta_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    /* Interpret the input objects as `numpy` arrays */
    M_array = (PyArrayObject *)PyArray_FROM_O(M_obj);
    eta_array = (PyArrayObject *)PyArray_FROM_O(eta_obj);

    /* If that didn't work, throw an `Exception`. */
    check((M_array != NULL && eta_array != NULL),
        "Couldn't parse the input arrays");

    /* How many data points are there? */
    n = (long)PyArray_DIM(M_array, 0);

    /* Check the dimensions. */
    if (n != (long)PyArray_DIM(eta_array, 0)) {
        PyErr_SetString(PyExc_RuntimeError, "Dimension mismatch between x and y");
        Py_DECREF(M_array);
        Py_DECREF(eta_array);
    }

    /* Build the output arrays */
    dims[0] = n;
    m1_obj = PyArray_ZEROS(1, dims, NPY_DOUBLE, 0);
    check(m1_obj != NULL, "Couldn't build output array.");

    m1_array = (PyArrayObject *)m1_obj;

    //PyArray_FILLWBYTE(m1_array, 0);

    check(n != 0, "Length of array is zero");

    /* Array Magic */
    arrays[0] = M_array;
    arrays[1] = eta_array;
    iter = NpyIter_AdvancedNew(2, arrays,
                               NPY_ITER_EXTERNAL_LOOP | NPY_ITER_BUFFERED,
                               NPY_KEEPORDER, NPY_SAFE_CASTING, op_flags, dtypes,
                               -1, NULL, NULL, 0);
    check(iter != NULL, "Couldn't set up iterator.");
    
    /*
     * The iternext function gets stored in a local variable
     * so it can be called repeatedly in an efficient manner.
     */
    iternext = NpyIter_GetIterNext(iter, NULL);
    check(iternext != NULL, "Couldn't set up iterator");
    
    /* The location of the data pointer which the iterator may update */
    dataptr = NpyIter_GetDataPtrArray(iter);

    /*The location of the stride which the iterator may update */
    strideptr = NpyIter_GetInnerStrideArray(iter);

    /* The location of the inner loop size which the iterator may update */
    innersizeptr = NpyIter_GetInnerLoopSizePtr(iter);

    /* Pre-compute variables for efficiency in the calculation */
    //

    /* Get C array for output array */
    m1 = (double *)PyArray_DATA(m1_array);

    Py_BEGIN_ALLOW_THREADS

    do {
    
        /* Get the inner loop data/stride/count values */
        npy_intp stride0 = strideptr[0];
        npy_intp stride1 = strideptr[1];
        npy_intp size = *innersizeptr;

        /* This is a typical inner loop for NPY_ITER_EXTERNAL_LOOP */
        while (size--) {
            tM = *(double *)dataptr[0];
            teta = *(double *)dataptr[1];
            //mc[i] = ((tm1 * tm2) ** (0.6)) *(tm1 + tm2) ** (-0.2);
            //eta[i] = (tm1*tm2) / ((tm1 + tm2) * (tm1 + tm2));
            //M[i] = tmc * pow(teta,-0.6);
            m1[i] = (tM/2.)*(1. + sqrt(1. - 4.*teta));
            //m2[i] = (tM/2.)*(1. - sqrt(1. - 4.*teta));

            dataptr[0] += stride0;
            dataptr[1] += stride1;
            i++;
        }

    } while (iternext(iter));

    Py_END_ALLOW_THREADS

    NpyIter_Deallocate(iter);

    /* Clean up. */
    Py_DECREF(M_array);
    Py_DECREF(eta_array);

    return m1_obj;
error:
    if (iter) {NpyIter_Deallocate(iter);}
    if (M_array) {Py_DECREF(M_array);}
    if (eta_array) {Py_DECREF(eta_array);}
    if (m1_obj) {Py_DECREF(m1_obj);}
    if (m1_array) {Py_DECREF(m1_array);}
    return NULL;
}

/* m2 of M and eta */

static PyObject *_m2_of_M_eta(PyObject *self, PyObject *args) {

    npy_intp n = 0;
    size_t i = 0;
    double tM, teta;
    PyObject *M_obj, *eta_obj, *m2_obj = NULL;
    PyArrayObject *M_array, *eta_array, *m2_array = NULL;
    PyArrayObject *arrays[2];
    npy_intp dims[1];
    double *m2;
    NpyIter *iter = NULL;
    NpyIter_IterNextFunc *iternext;
    char **dataptr;
    npy_intp *strideptr, *innersizeptr;
    PyArray_Descr *dtypes[] = {PyArray_DescrFromType(NPY_DOUBLE), PyArray_DescrFromType(NPY_DOUBLE)};
    npy_uint32 op_flags[] = {NPY_ITER_READONLY, NPY_ITER_READONLY};

    /* Parse the input tuple */
    if (!PyArg_ParseTuple(args, "OO", &M_obj, &eta_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    /* Interpret the input objects as `numpy` arrays */
    M_array = (PyArrayObject *)PyArray_FROM_O(M_obj);
    eta_array = (PyArrayObject *)PyArray_FROM_O(eta_obj);

    /* If that didn't work, throw an `Exception`. */
    check((M_array != NULL && eta_array != NULL),
        "Couldn't parse the input arrays");

    /* How many data points are there? */
    n = (long)PyArray_DIM(M_array, 0);

    /* Check the dimensions. */
    if (n != (long)PyArray_DIM(eta_array, 0)) {
        PyErr_SetString(PyExc_RuntimeError, "Dimension mismatch between x and y");
        Py_DECREF(M_array);
        Py_DECREF(eta_array);
    }

    /* Build the output arrays */
    dims[0] = n;
    m2_obj = PyArray_ZEROS(1, dims, NPY_DOUBLE, 0);
    check(m2_obj != NULL, "Couldn't build output array.");

    m2_array = (PyArrayObject *)m2_obj;

    //PyArray_FILLWBYTE(m2_array, 0);

    check(n != 0, "Length of array is zero");

    /* Array Magic */
    arrays[0] = M_array;
    arrays[1] = eta_array;
    iter = NpyIter_AdvancedNew(2, arrays,
                               NPY_ITER_EXTERNAL_LOOP | NPY_ITER_BUFFERED,
                               NPY_KEEPORDER, NPY_SAFE_CASTING, op_flags, dtypes,
                               -1, NULL, NULL, 0);
    check(iter != NULL, "Couldn't set up iterator.");
    
    /*
     * The iternext function gets stored in a local variable
     * so it can be called repeatedly in an efficient manner.
     */
    iternext = NpyIter_GetIterNext(iter, NULL);
    check(iternext != NULL, "Couldn't set up iterator");
    
    /* The location of the data pointer which the iterator may update */
    dataptr = NpyIter_GetDataPtrArray(iter);

    /*The location of the stride which the iterator may update */
    strideptr = NpyIter_GetInnerStrideArray(iter);

    /* The location of the inner loop size which the iterator may update */
    innersizeptr = NpyIter_GetInnerLoopSizePtr(iter);

    /* Pre-compute variables for efficiency in the calculation */
    //

    /* Get C array for output array */
    m2 = (double *)PyArray_DATA(m2_array);

    Py_BEGIN_ALLOW_THREADS

    do {
    
        /* Get the inner loop data/stride/count values */
        npy_intp stride0 = strideptr[0];
        npy_intp stride1 = strideptr[1];
        npy_intp size = *innersizeptr;

        /* This is a typical inner loop for NPY_ITER_EXTERNAL_LOOP */
        while (size--) {
            tM = *(double *)dataptr[0];
            teta = *(double *)dataptr[1];
            //mc[i] = ((tm1 * tm2) ** (0.6)) *(tm1 + tm2) ** (-0.2);
            //eta[i] = (tm1*tm2) / ((tm1 + tm2) * (tm1 + tm2));
            //M[i] = tmc * pow(teta,-0.6);
            //m1[i] = (tM/2.)*(1. + sqrt(1. - 4.*teta));
            m2[i] = (tM/2.)*(1. - sqrt(1. - 4.*teta));

            dataptr[0] += stride0;
            dataptr[1] += stride1;
            i++;
        }

    } while (iternext(iter));

    Py_END_ALLOW_THREADS

    NpyIter_Deallocate(iter);

    /* Clean up. */
    Py_DECREF(M_array);
    Py_DECREF(eta_array);

    return m2_obj;
error:
    if (iter) {NpyIter_Deallocate(iter);}
    if (M_array) {Py_DECREF(M_array);}
    if (eta_array) {Py_DECREF(eta_array);}
    if (m2_obj) {Py_DECREF(m2_obj);}
    if (m2_array) {Py_DECREF(m2_array);}
    return NULL;
}

/* detector frame mass from source frame mass and z */

static PyObject *_detector_of_source(PyObject *self, PyObject *args) {

    npy_intp n = 0;
    size_t i = 0;
    double tm, tz;
    PyObject *m_obj, *z_obj, *result_obj = NULL;
    PyArrayObject *m_array, *z_array, *result_array = NULL;
    PyArrayObject *arrays[2];
    npy_intp dims[1];
    double *result;
    NpyIter *iter = NULL;
    NpyIter_IterNextFunc *iternext;
    char **dataptr;
    npy_intp *strideptr, *innersizeptr;
    PyArray_Descr *dtypes[] = {PyArray_DescrFromType(NPY_DOUBLE), PyArray_DescrFromType(NPY_DOUBLE)};
    npy_uint32 op_flags[] = {NPY_ITER_READONLY, NPY_ITER_READONLY};

    /* Parse the input tuple */
    if (!PyArg_ParseTuple(args, "OO", &m_obj, &z_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    /* Interpret the input objects as `numpy` arrays */
    m_array = (PyArrayObject *)PyArray_FROM_O(m_obj);
    z_array = (PyArrayObject *)PyArray_FROM_O(z_obj);

    /* If that didn't work, throw an `Exception`. */
    check((m_array != NULL && z_array != NULL),
        "Couldn't parse the input arrays");

    /* How many data points are there? */
    n = (long)PyArray_DIM(m_array, 0);

    /* Check the dimensions. */
    if (n != (long)PyArray_DIM(z_array, 0)) {
        PyErr_SetString(PyExc_RuntimeError, "Dimension mismatch between x and y");
        Py_DECREF(m_array);
        Py_DECREF(z_array);
    }

    /* Build the output arrays */
    dims[0] = n;
    result_obj = PyArray_ZEROS(1, dims, NPY_DOUBLE, 0);
    check(result_obj != NULL, "Couldn't build output array.");

    result_array = (PyArrayObject *)result_obj;

    //PyArray_FILLWBYTE(result_array, 0);

    check(n != 0, "Length of array is zero");

    /* Array Magic */
    arrays[0] = m_array;
    arrays[1] = z_array;
    iter = NpyIter_AdvancedNew(2, arrays,
                               NPY_ITER_EXTERNAL_LOOP | NPY_ITER_BUFFERED,
                               NPY_KEEPORDER, NPY_SAFE_CASTING, op_flags, dtypes,
                               -1, NULL, NULL, 0);
    check(iter != NULL, "Couldn't set up iterator.");
    
    /*
     * The iternext function gets stored in a local variable
     * so it can be called repeatedly in an efficient manner.
     */
    iternext = NpyIter_GetIterNext(iter, NULL);
    check(iternext != NULL, "Couldn't set up iterator");
    
    /* The location of the data pointer which the iterator may update */
    dataptr = NpyIter_GetDataPtrArray(iter);

    /*The location of the stride which the iterator may update */
    strideptr = NpyIter_GetInnerStrideArray(iter);

    /* The location of the inner loop size which the iterator may update */
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
        npy_intp size = *innersizeptr;

        /* This is a typical inner loop for NPY_ITER_EXTERNAL_LOOP */
        while (size--) {
            tm = *(double *)dataptr[0];
            tz = *(double *)dataptr[1];
            //mc[i] = ((tm1 * tm2) ** (0.6)) *(tm1 + tm2) ** (-0.2);
            result[i] = tm*(tz + 1.);

            dataptr[0] += stride0;
            dataptr[1] += stride1;
            i++;
        }

    } while (iternext(iter));

    Py_END_ALLOW_THREADS

    NpyIter_Deallocate(iter);

    /* Clean up. */
    Py_DECREF(m_array);
    Py_DECREF(z_array);

    return result_obj;
error:
    if (iter) {NpyIter_Deallocate(iter);}
    if (m_array) {Py_DECREF(m_array);}
    if (z_array) {Py_DECREF(z_array);}
    if (result_obj) {Py_DECREF(result_obj);}
    if (result_array) {Py_DECREF(result_array);}
    return NULL;
}

/* source frame mass from detector frame mass and z */

static PyObject *_source_of_detector(PyObject *self, PyObject *args) {

    npy_intp n = 0;
    size_t i = 0;
    double tm, tz;
    PyObject *m_obj, *z_obj, *result_obj = NULL;
    PyArrayObject *m_array, *z_array, *result_array = NULL;
    PyArrayObject *arrays[2];
    npy_intp dims[1];
    double *result;
    NpyIter *iter = NULL;
    NpyIter_IterNextFunc *iternext;
    char **dataptr;
    npy_intp *strideptr, *innersizeptr;
    PyArray_Descr *dtypes[] = {PyArray_DescrFromType(NPY_DOUBLE), PyArray_DescrFromType(NPY_DOUBLE)};
    npy_uint32 op_flags[] = {NPY_ITER_READONLY, NPY_ITER_READONLY};

    /* Parse the input tuple */
    if (!PyArg_ParseTuple(args, "OO", &m_obj, &z_obj)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    /* Interpret the input objects as `numpy` arrays */
    m_array = (PyArrayObject *)PyArray_FROM_O(m_obj);
    z_array = (PyArrayObject *)PyArray_FROM_O(z_obj);

    /* If that didn't work, throw an `Exception`. */
    check((m_array != NULL && z_array != NULL),
        "Couldn't parse the input arrays");

    /* How many data points are there? */
    n = (long)PyArray_DIM(m_array, 0);

    /* Check the dimensions. */
    if (n != (long)PyArray_DIM(z_array, 0)) {
        PyErr_SetString(PyExc_RuntimeError, "Dimension mismatch between x and y");
        Py_DECREF(m_array);
        Py_DECREF(z_array);
    }

    /* Build the output arrays */
    dims[0] = n;
    result_obj = PyArray_ZEROS(1, dims, NPY_DOUBLE, 0);
    check(result_obj != NULL, "Couldn't build output array.");

    result_array = (PyArrayObject *)result_obj;

    //PyArray_FILLWBYTE(result_array, 0);

    check(n != 0, "Length of array is zero");

    /* Array Magic */
    arrays[0] = m_array;
    arrays[1] = z_array;
    iter = NpyIter_AdvancedNew(2, arrays,
                               NPY_ITER_EXTERNAL_LOOP | NPY_ITER_BUFFERED,
                               NPY_KEEPORDER, NPY_SAFE_CASTING, op_flags, dtypes,
                               -1, NULL, NULL, 0);
    check(iter != NULL, "Couldn't set up iterator.");
    
    /*
     * The iternext function gets stored in a local variable
     * so it can be called repeatedly in an efficient manner.
     */
    iternext = NpyIter_GetIterNext(iter, NULL);
    check(iternext != NULL, "Couldn't set up iterator");
    
    /* The location of the data pointer which the iterator may update */
    dataptr = NpyIter_GetDataPtrArray(iter);

    /*The location of the stride which the iterator may update */
    strideptr = NpyIter_GetInnerStrideArray(iter);

    /* The location of the inner loop size which the iterator may update */
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
        npy_intp size = *innersizeptr;

        /* This is a typical inner loop for NPY_ITER_EXTERNAL_LOOP */
        while (size--) {
            tm = *(double *)dataptr[0];
            tz = *(double *)dataptr[1];
            //mc[i] = ((tm1 * tm2) ** (0.6)) *(tm1 + tm2) ** (-0.2);
            result[i] = tm/(tz + 1.);

            dataptr[0] += stride0;
            dataptr[1] += stride1;
            i++;
        }

    } while (iternext(iter));

    Py_END_ALLOW_THREADS

    NpyIter_Deallocate(iter);

    /* Clean up. */
    Py_DECREF(m_array);
    Py_DECREF(z_array);

    return result_obj;
error:
    if (iter) {NpyIter_Deallocate(iter);}
    if (m_array) {Py_DECREF(m_array);}
    if (z_array) {Py_DECREF(z_array);}
    if (result_obj) {Py_DECREF(result_obj);}
    if (result_array) {Py_DECREF(result_array);}
    return NULL;
}


