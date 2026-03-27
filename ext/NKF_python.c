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
#include "nkf/nkf.h"

/* Per-call I/O state, passed as userdata to NKF I/O callbacks. */
typedef struct {
  unsigned char *inbuf;
  Py_ssize_t inbuf_size;
  Py_ssize_t in_pos;
  unsigned char *outbuf;
  Py_ssize_t outbuf_size;
  Py_ssize_t out_pos;
  int suppress_output;  /* non-zero for guess mode */
  int oom;              /* set on realloc failure */
} pynkf_io_t;

static int
pynkf_io_getc(void *userdata)
{
  pynkf_io_t *io = (pynkf_io_t *)userdata;
  if (io->in_pos >= io->inbuf_size) return EOF;
  return (int)io->inbuf[io->in_pos++];
}

static int
pynkf_io_ungetc(void *userdata, int c)
{
  pynkf_io_t *io = (pynkf_io_t *)userdata;
  if (io->in_pos <= 0) return EOF;
  io->inbuf[--io->in_pos] = (unsigned char)c;
  return c;
}

static void
pynkf_io_putc(void *userdata, int c)
{
  pynkf_io_t *io = (pynkf_io_t *)userdata;

  if (io->suppress_output || io->oom) return;

  if (io->out_pos < io->outbuf_size) {
    io->outbuf[io->out_pos++] = (unsigned char)c;
  } else {
    Py_ssize_t new_size = io->outbuf_size * 2;
    unsigned char *p = (unsigned char *)PyMem_Realloc(io->outbuf, new_size + 1);
    if (p == NULL) {
      io->oom = 1;
      return;
    }
    io->outbuf = p;
    io->outbuf_size = new_size;
    io->outbuf[io->out_pos++] = (unsigned char)c;
  }
}

static PyObject *
pynkf_convert(unsigned char *str, Py_ssize_t str_len, const char **opts, Py_ssize_t opts_len)
{
  PyObject *res;
  Py_ssize_t i;
  nkf_context *ctx;
  pynkf_io_t io;
  int ret;

  ctx = nkf_context_new();
  if (ctx == NULL) {
    PyErr_NoMemory();
    return NULL;
  }

  /* Set options */
  for (i = 0; i < opts_len; i++) {
    nkf_options(ctx, opts[i]);
  }

  /* Set up I/O buffers */
  io.inbuf = str;
  io.inbuf_size = str_len;
  io.in_pos = 0;
  io.outbuf_size = (Py_ssize_t)(str_len * 1.5) + 256;
  io.outbuf = (unsigned char *)PyMem_Malloc(io.outbuf_size);
  if (io.outbuf == NULL) {
    nkf_context_free(ctx);
    PyErr_NoMemory();
    return NULL;
  }
  io.out_pos = 0;
  io.suppress_output = 0;
  io.oom = 0;

  nkf_set_io(ctx, pynkf_io_getc, pynkf_io_ungetc, pynkf_io_putc, &io);

  ret = nkf_convert(ctx);

  if (io.oom || ret != 0) {
    PyMem_Free(io.outbuf);
    nkf_context_free(ctx);
    PyErr_NoMemory();
    return NULL;
  }

  /* The new ctx-based std_putc does not output end-of-stream markers
     (EOF is filtered by std_putc), so no null stripping is needed. */
  res = PyBytes_FromStringAndSize((const char *)io.outbuf, io.out_pos);

  PyMem_Free(io.outbuf);
  nkf_context_free(ctx);
  return res;
}

static PyObject *
pynkf_convert_guess(unsigned char *str, Py_ssize_t str_len)
{
  nkf_context *ctx;
  pynkf_io_t io;
  const char *codename;
  PyObject *res;

  ctx = nkf_context_new();
  if (ctx == NULL) {
    PyErr_NoMemory();
    return NULL;
  }

  io.inbuf = str;
  io.inbuf_size = str_len;
  io.in_pos = 0;
  io.outbuf = NULL;
  io.outbuf_size = 0;
  io.out_pos = 0;
  io.suppress_output = 1;
  io.oom = 0;

  nkf_set_io(ctx, pynkf_io_getc, pynkf_io_ungetc, pynkf_io_putc, &io);

  nkf_guess(ctx);

  codename = nkf_get_guessed_code(ctx);
  res = PyUnicode_FromString(codename);

  nkf_context_free(ctx);
  return res;
}

static PyObject *
pynkf_convert_guess_detail(unsigned char *str, Py_ssize_t str_len)
{
  nkf_context *ctx;
  pynkf_io_t io;
  const char *codename;
  const char *eol_name;
  int eol;
  PyObject *res;

  ctx = nkf_context_new();
  if (ctx == NULL) {
    PyErr_NoMemory();
    return NULL;
  }

  io.inbuf = str;
  io.inbuf_size = str_len;
  io.in_pos = 0;
  io.outbuf = NULL;
  io.outbuf_size = 0;
  io.out_pos = 0;
  io.suppress_output = 1;
  io.oom = 0;

  nkf_set_io(ctx, pynkf_io_getc, pynkf_io_ungetc, pynkf_io_putc, &io);

  nkf_guess(ctx);

  codename = nkf_get_guessed_code(ctx);
  eol = nkf_get_input_eol(ctx);

  if (eol == NKF_CR)        eol_name = "CR";
  else if (eol == NKF_LF)   eol_name = "LF";
  else if (eol == NKF_CRLF) eol_name = "CRLF";
  else if (eol == EOF)       eol_name = "MIXED";
  else                       eol_name = NULL;

  res = Py_BuildValue("(sz)", codename, eol_name);

  nkf_context_free(ctx);
  return res;
}

#define PYNKF_OPTS_STACK_SIZE 8

#ifndef EXTERN_NKF
static
#endif
PyObject *pynkf_nkf(PyObject *self, PyObject *args)
{
  PyObject *opts_obj;
  unsigned char *str;
  Py_ssize_t str_len;
  const char *opts_stack[PYNKF_OPTS_STACK_SIZE];
  const char **opts = opts_stack;
  Py_ssize_t opts_len;
  Py_ssize_t i;
  PyObject *res;

  if (!PyArg_ParseTuple(args, "Os#", &opts_obj, &str, &str_len)) {
    return NULL;
  }

  if (PyUnicode_Check(opts_obj)) {
    const char *opt = PyUnicode_AsUTF8(opts_obj);
    if (opt == NULL) {
      return NULL;
    }
    opts[0] = opt;
    opts_len = 1;
  } else if (PyList_Check(opts_obj) || PyTuple_Check(opts_obj)) {
    int is_tuple = PyTuple_Check(opts_obj);
    opts_len = is_tuple ? PyTuple_GET_SIZE(opts_obj) : PyList_GET_SIZE(opts_obj);

    if (opts_len > PYNKF_OPTS_STACK_SIZE) {
      opts = (const char **)PyMem_Malloc(sizeof(const char *) * opts_len);
      if (opts == NULL) {
        PyErr_NoMemory();
        return NULL;
      }
    }

    for (i = 0; i < opts_len; i++) {
      PyObject *item = is_tuple ? PyTuple_GET_ITEM(opts_obj, i) : PyList_GET_ITEM(opts_obj, i);
      if (!PyUnicode_Check(item)) {
        if (opts != opts_stack) PyMem_Free(opts);
        PyErr_SetString(PyExc_TypeError, "options must be strings");
        return NULL;
      }
      const char *opt = PyUnicode_AsUTF8(item);
      if (opt == NULL) {
        if (opts != opts_stack) PyMem_Free(opts);
        return NULL;
      }
      opts[i] = opt;
    }
  } else {
    PyErr_SetString(PyExc_TypeError, "first argument must be a string, list, or tuple");
    return NULL;
  }

  res = pynkf_convert(str, str_len, opts, opts_len);
  if (opts != opts_stack) PyMem_Free(opts);
  return res;
}

#ifndef EXTERN_NKF
static
#endif
PyObject *pynkf_guess(PyObject *self, PyObject *args)
{
  unsigned char *str;
  Py_ssize_t str_len;
  PyObject *res;

  if (!PyArg_ParseTuple(args, "s#", &str, &str_len)) {
    return NULL;
  }
  res = pynkf_convert_guess(str, str_len);
  return res;
}

#ifndef EXTERN_NKF
static
#endif
PyObject *pynkf_guess_detail(PyObject *self, PyObject *args)
{
  unsigned char *str;
  Py_ssize_t str_len;
  PyObject *res;

  if (!PyArg_ParseTuple(args, "s#", &str, &str_len)) {
    return NULL;
  }
  res = pynkf_convert_guess_detail(str, str_len);
  return res;
}

#ifndef EXTERN_NKF
static PyMethodDef
nkfMethods[] = {
  {"nkf", pynkf_nkf, METH_VARARGS, ""},
  {"guess", pynkf_guess, METH_VARARGS, ""},
  {"guess_detail", pynkf_guess_detail, METH_VARARGS, ""},
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
