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
#include <setjmp.h>

#undef getc
#undef ungetc
#define getc(f)         pynkf_getc(f)
#define ungetc(c,f)     pynkf_ungetc(c,f)

#undef putchar
#undef TRUE
#undef FALSE
#define putchar(c)      pynkf_putchar(c)

static Py_ssize_t pynkf_ibufsize, pynkf_obufsize;
static unsigned char *pynkf_inbuf, *pynkf_outbuf;
static int pynkf_icount,pynkf_ocount;
static unsigned char *pynkf_iptr, *pynkf_optr;
static jmp_buf env;
static int pynkf_guess_flag;

static int
pynkf_getc(FILE *f)
{
  unsigned char c;
  if (pynkf_icount >= pynkf_ibufsize) return EOF;
  c = *pynkf_iptr++;
  pynkf_icount++;
  return (int)c;
}

static int
pynkf_ungetc(int c, FILE *f)
{
  if (pynkf_icount--){
    *(--pynkf_iptr) = c;
    return c;
  }else{ return EOF; }
}

static void
pynkf_putchar(int c)
{
  Py_ssize_t size;
  unsigned char *p;

  if (pynkf_guess_flag) {
    return;
  }

  if (pynkf_ocount--){
    *pynkf_optr++ = c;
  }else{
    size = pynkf_obufsize + pynkf_obufsize;
    p = (unsigned char *)PyMem_Realloc(pynkf_outbuf, size + 1);
    if (pynkf_outbuf == NULL){ longjmp(env, 1); }
    pynkf_outbuf = p;
    pynkf_optr = pynkf_outbuf + pynkf_obufsize;
    pynkf_ocount = pynkf_obufsize;
    pynkf_obufsize = size;
    *pynkf_optr++ = c;
    pynkf_ocount--;
  }
}

#define PERL_XS 1
#include "nkf/utf8tbl.c"
#include "nkf/nkf.c"

static PyObject *
pynkf_convert(unsigned char *str, Py_ssize_t str_len, const char **opts, Py_ssize_t opts_len)
{
  PyObject *res;
  Py_ssize_t i;

  pynkf_ibufsize = str_len + 1;
  pynkf_obufsize = pynkf_ibufsize * 1.5 + 256;
  pynkf_outbuf = (unsigned char *)PyMem_Malloc(pynkf_obufsize);
  if (pynkf_outbuf == NULL){
    PyErr_NoMemory();
    return NULL;
  }
  pynkf_outbuf[0] = '\0';
  pynkf_ocount = pynkf_obufsize;
  pynkf_optr = pynkf_outbuf;
  pynkf_icount = 0;
  pynkf_inbuf  = str;
  pynkf_iptr = pynkf_inbuf;
  pynkf_guess_flag = 0;

  if (setjmp(env) == 0){

    reinit();

    for (i = 0; i < opts_len; i++) {
      options((char *)opts[i]);
    }

    kanji_convert(NULL);

  }else{
    PyMem_Free(pynkf_outbuf);
    PyErr_NoMemory();
    return NULL;
  }

  /* NKF writes U+0000 as end-of-stream marker in the output encoding.
     Determine the marker size and strip it from the output. */
  {
    Py_ssize_t output_len = pynkf_optr - pynkf_outbuf;
    Py_ssize_t null_size = 1;
    if (output_encoding) {
      nkf_native_encoding *base = nkf_enc_to_base_encoding(output_encoding);
      if (base == &NkfEncodingUTF_32) null_size = 4;
      else if (base == &NkfEncodingUTF_16) null_size = 2;
    }
    if (output_len >= null_size) output_len -= null_size;
    res = PyBytes_FromStringAndSize((const char *)pynkf_outbuf, output_len);
  }
  PyMem_Free(pynkf_outbuf);
  return res;
}

static PyObject *
pynkf_convert_guess(unsigned char* str, Py_ssize_t str_len)
{
  PyObject * res;
  const char *codename;

  pynkf_ibufsize = str_len + 1;
  pynkf_icount = 0;
  pynkf_inbuf  = str;
  pynkf_iptr = pynkf_inbuf;

  pynkf_guess_flag = 1;
  reinit();
  guess_f = 1;

  kanji_convert(NULL);

  codename = get_guessed_code();

  res = PyUnicode_FromString(codename);
  return res;
}

static PyObject *
pynkf_convert_guess_detail(unsigned char* str, Py_ssize_t str_len)
{
  const char *codename;
  const char *eol_name;

  pynkf_ibufsize = str_len + 1;
  pynkf_icount = 0;
  pynkf_inbuf  = str;
  pynkf_iptr = pynkf_inbuf;

  pynkf_guess_flag = 1;
  reinit();
  guess_f = 1;

  kanji_convert(NULL);

  codename = get_guessed_code();

  if (input_eol == CR)        eol_name = "CR";
  else if (input_eol == LF)   eol_name = "LF";
  else if (input_eol == CRLF) eol_name = "CRLF";
  else if (input_eol == EOF)  eol_name = "MIXED";
  else                        eol_name = NULL;

  return Py_BuildValue("(sz)", codename, eol_name);
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
  PyObject* res;

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
