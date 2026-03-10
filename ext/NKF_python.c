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
pynkf_convert(const Py_buffer *src, const char *opts)
{
  PyObject * res;

  pynkf_ibufsize = src->len;
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
  pynkf_inbuf  = src->buf;
  pynkf_iptr = pynkf_inbuf;
  pynkf_guess_flag = 0;

  if (setjmp(env) == 0){

    reinit();

    options(opts);

    kanji_convert(NULL);

  }else{
    PyMem_Free(pynkf_outbuf);
    PyErr_NoMemory();
    return NULL;
  }

  *pynkf_optr = 0;
  res = PyBytes_FromString(pynkf_outbuf);
  PyMem_Free(pynkf_outbuf);

  return res;
}

static PyObject *
pynkf_convert_guess(const Py_buffer *src)
{
  const char *codename;

  pynkf_ibufsize = src->len;
  pynkf_icount = 0;
  pynkf_inbuf  = src->buf;
  pynkf_iptr = pynkf_inbuf;

  pynkf_guess_flag = 1;
  reinit();
  guess_f = 1;

  kanji_convert(NULL);

  codename = get_guessed_code();

  return PyUnicode_FromString(codename);
}

#ifndef EXTERN_NKF
static
#endif
PyObject *pynkf_nkf(PyObject *self, PyObject *args)
{
  Py_buffer src;
  const char *opts;
  PyObject *res;

  if (!PyArg_ParseTuple(args, "ss*", &opts, &src)) {
    return NULL;
  }

  res = pynkf_convert(&src, opts);
  PyBuffer_Release(&src);

  return res;
}

#ifndef EXTERN_NKF
static
#endif
PyObject *pynkf_guess(PyObject *self, PyObject *args)
{
  Py_buffer src;
  PyObject *res;

  if (!PyArg_ParseTuple(args, "s*", &src)) {
    return NULL;
  }

  res = pynkf_convert_guess(&src);
  PyBuffer_Release(&src);

  return res;
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
