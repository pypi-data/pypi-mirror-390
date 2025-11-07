#define PY_SSIZE_T_CLEAN
#include "Python.h"

PyDoc_STRVAR(minmax_doc,
"minmax(iterable, *[, default=obj, key=func]) -> (minitem, maxitem)\n\
minmax(arg1, arg2, *args, *[, key=func]) -> (minitem, maxitem)\n\n\
With a single iterable argument, return its smallest and largest item as a \n\
pair. The default keyword-only argument specifies an object to return if the\n\
provided iterable is empty.\n\n\
With two or more arguments, return the smallest and largest argument.");

static PyObject *
_pyminmax_minmax(PyObject *self, PyObject *args, PyObject *kwds)
{
    PyObject *v, *it, *item, *val, *minitem, *maxitem, *emptytuple;
    PyObject *defaultval = NULL, *keyfunc = NULL;
    static char *kwlist[] = {"key", "default", NULL};
    const char *name = "minmax";
    const int positional = PyTuple_Size(args) > 1;
    int ret;

    if (positional) {
        v = args;
    }
    else if (!PyArg_UnpackTuple(args, name, 1, 1, &v)) {
        if (PyExceptionClass_Check(PyExc_TypeError)) {
            PyErr_Format(PyExc_TypeError,
                         "%s expected at least 1 argument, got 0", name);
        }
        return NULL;
    }

    emptytuple = PyTuple_New(0);
    if (emptytuple == NULL) {
        return NULL;
    }
    ret = PyArg_ParseTupleAndKeywords(emptytuple, kwds, "|$OO:minmax", kwlist,
                                      &keyfunc, &defaultval);
    Py_DECREF(emptytuple);
    if (!ret) {
        return NULL;
    }

    if (positional && defaultval != NULL) {
        PyErr_Format(PyExc_TypeError,
                     "Cannot specify a default for %s() with multiple "
                     "positional arguments", name);
        return NULL;
    }

    /* it = iter(v) */
    it = PyObject_GetIter(v);
    if (it == NULL) {
        return NULL;
    }

    /* Get the first value from the iterator it. If there are no remaining
     * values, returns NULL with no exception set. If an error occurs while
     * retrieving the item, returns NULL and passes along the exception. */
    item = PyIter_Next(it);
    if (item == NULL) {
        if (PyErr_Occurred()) {
            Py_DECREF(it);
            return NULL;
        }
        else if (defaultval != NULL) {
            Py_DECREF(it);
            return Py_NewRef(defaultval);
        }
        else {
            PyErr_Format(PyExc_ValueError,
                         "%s() iterable argument is empty", name);
            Py_DECREF(it);
            return NULL;
        }
    }

    /* OWN: item, it */
    if (keyfunc == NULL || keyfunc == Py_None) {
        minitem = item;
        maxitem = Py_NewRef(item);

        /* OWN: minitem, maxitem, it */
        while (( item = PyIter_Next(it) )) {
            /* OWN: item, minitem, maxitem, it */
            int cmp_mx = PyObject_RichCompareBool(item, maxitem, Py_GT);
            int cmp_mn = PyObject_RichCompareBool(item, minitem, Py_LT);

            if (cmp_mx < 0 || cmp_mn < 0) {
                Py_DECREF(item);
                Py_DECREF(minitem);
                Py_DECREF(maxitem);
                Py_DECREF(it);
                return NULL;
            }
            else if (cmp_mx > 0) {
                Py_DECREF(maxitem);
                maxitem = item;
            }
            else if (cmp_mn > 0) {
                Py_DECREF(minitem);
                minitem = item;
            }
            else {
                Py_DECREF(item);
            }
        }
        if (PyErr_Occurred()) {
            Py_DECREF(minitem);
            Py_DECREF(maxitem);
            Py_DECREF(it);
            return NULL;
        }

        /* 'N' same as 'O', except that corresponding argument's refcount is
         * not incremented in the former case. If an error occurs in
         * Py_BuildValue(), Py_BuildValue() decrements minitem, maxitem for us,
         * so no need to test return value.
         */
        Py_DECREF(it);
        return Py_BuildValue("(NN)", minitem, maxitem);
    }
    else {
        PyObject *minval, *maxval;

        /* Call a callable Python object, keyfunc, with exactly 1 positional
         * argument, item, and no keyword arguments. Return the result of the
         * call on success, or raise an exception and return NULL on failure. */
        val = PyObject_CallOneArg(keyfunc, item);
        if (val == NULL) {
            Py_DECREF(item);
            Py_DECREF(it);
            return NULL;
        }

        minitem = item;
        minval = val;
        maxitem = Py_NewRef(item);
        maxval = Py_NewRef(val);

        /* OWN: minitem, minval, maxitem, maxval, it */
        while (( item = PyIter_Next(it) )) {
            /* OWN: item, minitem, minval, maxitem, maxval, it */
            val = PyObject_CallOneArg(keyfunc, item);
            if (val == NULL) {
                Py_DECREF(item);
                Py_DECREF(minitem);
                Py_DECREF(maxitem);
                Py_DECREF(minval);
                Py_DECREF(maxval);
                Py_DECREF(it);
                return NULL;
            }
            /* OWN: item, val, minitem, minval, maxitem, maxval, it */
            int cmp_mx = PyObject_RichCompareBool(val, maxval, Py_GT);
            int cmp_mn = PyObject_RichCompareBool(val, minval, Py_LT);

            if (cmp_mx < 0 || cmp_mn < 0) {
                Py_DECREF(val);
                Py_DECREF(item);
                Py_DECREF(minitem);
                Py_DECREF(maxitem);
                Py_DECREF(minval);
                Py_DECREF(maxval);
                Py_DECREF(it);
                return NULL;
            }
            else if (cmp_mx > 0) {
                Py_DECREF(maxval);
                Py_DECREF(maxitem);
                maxval = val;
                maxitem = item;
            }
            else if (cmp_mn > 0) {
                Py_DECREF(minval);
                Py_DECREF(minitem);
                minval = val;
                minitem = item;
            }
            else {
                Py_DECREF(item);
                Py_DECREF(val);
            }
        }
        if (PyErr_Occurred()) {
            Py_DECREF(minval);
            Py_DECREF(minitem);
            Py_DECREF(maxval);
            Py_DECREF(maxitem);
            Py_DECREF(it);
            return NULL;
        }

        Py_DECREF(minval);
        Py_DECREF(maxval);
        Py_DECREF(it);
        return Py_BuildValue("(NN)", minitem, maxitem);
    }
}

static PyMethodDef _pyminmax_methods[] = {
    {"minmax", (PyCFunction)(void(*)(void))_pyminmax_minmax, METH_VARARGS |
                                                             METH_KEYWORDS,
                                                             minmax_doc},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef _pyminmaxmodule = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "_pyminmax",
    .m_doc = NULL,
    .m_size = -1,
    .m_methods = _pyminmax_methods
};

PyMODINIT_FUNC
PyInit__pyminmax(void)
{
    return PyModule_Create(&_pyminmaxmodule);
}
