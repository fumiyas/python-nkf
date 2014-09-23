/*
 * Python Interface to NKF
 * Copyright (c) 2012-2013 SATOH Fumiyasu @ OSS Technology Copr., Japan
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

static int pynkf_ibufsize, pynkf_obufsize;
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
  size_t size;
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
#include "nkf-dist/utf8tbl.c"
#include "nkf-dist/nkf.c"

static PyObject *
pynkf_convert(unsigned char* str, int strlen, char* opts, int optslen)
{
  PyObject * res;

  pynkf_ibufsize = strlen + 1;
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

    options(opts);

    kanji_convert(NULL);

  }else{
    PyMem_Free(pynkf_outbuf);
    PyErr_NoMemory();
    return NULL;
  }

  *pynkf_optr = 0;
  #if PY_MAJOR_VERSION >= 3
    res = PyBytes_FromString(pynkf_outbuf);
  #else
    res = PyString_FromString(pynkf_outbuf);
  #endif
  PyMem_Free(pynkf_outbuf);
  return res;
}

static PyObject *
pynkf_convert_guess(unsigned char* str, int strlen)
{
  PyObject * res;
  const char *codename;

  pynkf_ibufsize = strlen + 1;
  pynkf_icount = 0;
  pynkf_inbuf  = str;
  pynkf_iptr = pynkf_inbuf;

  pynkf_guess_flag = 1;
  reinit();
  guess_f = 1;

  kanji_convert(NULL);

  codename = get_guessed_code();
  #if PY_MAJOR_VERSION >= 3
    res = PyBytes_FromString(codename);
  #else
    res = PyString_FromString(codename);
  #endif
  return res;
}

#ifndef EXTERN_NKF
static
#endif
PyObject *pynkf_nkf(PyObject *self, PyObject *args)
{
  unsigned char *str;
  int strlen;
  char *opts;
  int optslen;
  PyObject* res;

  if (!PyArg_ParseTuple(args, "s#s#", &opts, &optslen, &str, &strlen)) {
    return NULL;
  }
  res = pynkf_convert(str, strlen, opts, optslen);
  return res;
}

#ifndef EXTERN_NKF
static
#endif
PyObject *pynkf_guess(PyObject *self, PyObject *args)
{
  unsigned char *str;
  int strlen;
  PyObject* res;

  if (!PyArg_ParseTuple(args, "s#", &str, &strlen)) {
    return NULL;
  }
  res = pynkf_convert_guess(str, strlen);
  return res;
}

#ifndef EXTERN_NKF
static PyMethodDef
nkfmethods[] = {
  {"nkf", pynkf_nkf, METH_VARARGS},
  {"guess", pynkf_guess, METH_VARARGS},
  {NULL, NULL}
};

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef
moduledef = {
  PyModuleDef_HEAD_INIT,
  "nkf",
  NULL,
  NULL,
  nkfmethods,
  NULL,
  NULL,
  NULL,
  NULL
};

/* Module initialization function */
PyObject *
PyInit_nkf(void)
#else
void
initnkf(void)
#endif
{
  #if PY_MAJOR_VERSION >= 3
    PyObject *module = PyModule_Create(&moduledef);
    return module;
  #else
    Py_InitModule("nkf", nkfmethods);
  #endif
}
#endif
