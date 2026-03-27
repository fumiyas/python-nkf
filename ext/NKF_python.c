/*
 * Python Interface to NKF
 * Copyright (c) 2012-2024 SATOH Fumiyasu @ OSS Technology Corp., Japan
 * Copyright (c) 2005 Matsumoto, Tadashi <ma2@city.plala.jp>
 * All Rights Reserved.
 *
 * Everyone is permitted to do anything on this program
 * including copying, modifying, improving,
 * as long as you don't try to pretend that you wrote it.
 * i.e., the above copyright notice has to appear in all copies.
 * Binary distribution requires original version messages.
 * You don't have to ask before copying, redistribution or publishing.
 * THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE.
 */

#define PY_SSIZE_T_CLEAN

#include "Python.h"
#include "nkf/nkf_context.h"

/* Per-call I/O state (stack-allocated, no globals) */
typedef struct {
    unsigned char *in_buf;
    unsigned char *in_ptr;
    unsigned char *in_end;
    unsigned char *out_buf;
    unsigned char *out_ptr;
    unsigned char *out_end;
    Py_ssize_t out_capacity;
    int error;
} pynkf_io_t;

static nkf_char
pynkf_ext_getc(void *user_data)
{
    pynkf_io_t *io = (pynkf_io_t *)user_data;
    if (io->in_ptr >= io->in_end) return EOF;
    return (nkf_char)(*io->in_ptr++);
}

static nkf_char
pynkf_ext_ungetc(nkf_char c, void *user_data)
{
    pynkf_io_t *io = (pynkf_io_t *)user_data;
    if (io->in_ptr <= io->in_buf) return EOF;
    *(--io->in_ptr) = (unsigned char)c;
    return c;
}

static void
pynkf_ext_putc(nkf_char c, void *user_data)
{
    pynkf_io_t *io = (pynkf_io_t *)user_data;
    if (io->error) return;

    if (io->out_ptr >= io->out_end) {
        Py_ssize_t new_capacity = io->out_capacity * 2;
        Py_ssize_t used = io->out_ptr - io->out_buf;
        unsigned char *p = (unsigned char *)PyMem_Realloc(io->out_buf, new_capacity + 1);
        if (p == NULL) {
            io->error = 1;
            return;
        }
        io->out_buf = p;
        io->out_ptr = p + used;
        io->out_capacity = new_capacity;
        io->out_end = p + new_capacity;
    }
    *io->out_ptr++ = (unsigned char)c;
}

/* Discard output (used for guess mode) */
static void
pynkf_ext_putc_discard(nkf_char c, void *user_data)
{
    (void)c;
    (void)user_data;
}

static PyObject *
pynkf_convert(unsigned char *str, Py_ssize_t strlen, char *opts, Py_ssize_t optslen)
{
    nkf_context_t *ctx;
    pynkf_io_t io;
    PyObject *res;
    char *optbuf;

    /* Initialize I/O state */
    io.in_buf = str;
    io.in_ptr = str;
    io.in_end = str + strlen;
    io.out_capacity = (Py_ssize_t)(strlen * 1.5) + 256;
    io.out_buf = (unsigned char *)PyMem_Malloc(io.out_capacity + 1);
    if (io.out_buf == NULL) {
        PyErr_NoMemory();
        return NULL;
    }
    io.out_ptr = io.out_buf;
    io.out_end = io.out_buf + io.out_capacity;
    io.error = 0;

    /* NUL-terminate the options string */
    optbuf = (char *)PyMem_Malloc(optslen + 1);
    if (optbuf == NULL) {
        PyMem_Free(io.out_buf);
        PyErr_NoMemory();
        return NULL;
    }
    memcpy(optbuf, opts, optslen);
    optbuf[optslen] = '\0';

    ctx = nkf_context_new();
    if (ctx == NULL) {
        PyMem_Free(optbuf);
        PyMem_Free(io.out_buf);
        PyErr_NoMemory();
        return NULL;
    }

    nkf_context_set_input(ctx, pynkf_ext_getc, pynkf_ext_ungetc, &io);
    nkf_context_set_output(ctx, pynkf_ext_putc, &io);
    nkf_convert(ctx, optbuf);
    nkf_context_free(ctx);
    PyMem_Free(optbuf);

    if (io.error) {
        PyMem_Free(io.out_buf);
        PyErr_NoMemory();
        return NULL;
    }

    *io.out_ptr = '\0';
    res = PyBytes_FromStringAndSize((char *)io.out_buf, io.out_ptr - io.out_buf);
    PyMem_Free(io.out_buf);
    return res;
}

static PyObject *
pynkf_convert_guess(unsigned char *str, Py_ssize_t strlen)
{
    nkf_context_t *ctx;
    pynkf_io_t io;
    const char *codename;

    io.in_buf = str;
    io.in_ptr = str;
    io.in_end = str + strlen;
    io.error = 0;

    ctx = nkf_context_new();
    if (ctx == NULL) {
        PyErr_NoMemory();
        return NULL;
    }

    nkf_context_set_input(ctx, pynkf_ext_getc, pynkf_ext_ungetc, &io);
    nkf_context_set_output(ctx, pynkf_ext_putc_discard, NULL);
    nkf_convert(ctx, "-g");
    codename = nkf_get_guessed_code(ctx);

    PyObject *res = PyUnicode_FromString(codename);
    nkf_context_free(ctx);
    return res;
}

#ifndef EXTERN_NKF
static
#endif
PyObject *pynkf_nkf(PyObject *self, PyObject *args)
{
    unsigned char *str;
    Py_ssize_t strlen;
    char *opts;
    Py_ssize_t optslen;

    if (!PyArg_ParseTuple(args, "s#s#", &opts, &optslen, &str, &strlen)) {
        return NULL;
    }
    return pynkf_convert(str, strlen, opts, optslen);
}

#ifndef EXTERN_NKF
static
#endif
PyObject *pynkf_guess(PyObject *self, PyObject *args)
{
    unsigned char *str;
    Py_ssize_t strlen;

    if (!PyArg_ParseTuple(args, "s#", &str, &strlen)) {
        return NULL;
    }
    return pynkf_convert_guess(str, strlen);
}

#ifndef EXTERN_NKF
static PyMethodDef
nkfMethods[] = {
    {"nkf", pynkf_nkf, METH_VARARGS, ""},
    {"guess", pynkf_guess, METH_VARARGS, ""},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef nkfmodule = {
    PyModuleDef_HEAD_INIT,
    "nkf",
    "",
    -1,
    nkfMethods
};

/* Module initialization function */
PyMODINIT_FUNC
PyInit__nkf(void)
{
    return PyModule_Create(&nkfmodule);
}
#endif
