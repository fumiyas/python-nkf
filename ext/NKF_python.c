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

/* ======================================================================
 * Encoding name -> NKF flags lookup table
 * ====================================================================== */

typedef struct {
  const char *normalized;  /* lowercased, hyphens/underscores stripped */
  const char *enc_flag;    /* NKF output flag for encoding (str->bytes) */
  const char *dec_flag;    /* NKF input flag for decoding (bytes->str) */
} nkf_enc_map_entry;

static const nkf_enc_map_entry nkf_enc_map[] = {
  {"iso2022jp",   "-j",     "-J"},
  {"eucjp",       "-e",     "-E"},
  {"shiftjis",    "-s",     "-S"},
  {"sjis",        "-s",     "-S"},
  {"cp932",       "-s",     "-S"},
  {"windows31j",  "-s",     "-S"},
  {"utf8",        "-w",     "-W"},
  {"utf16",       "-w16",   "-W16"},
  {"utf16be",     "-w16B0", "-W16B"},
  {"utf16le",     "-w16L0", "-W16L"},
  {"utf32",       "-w32",   "-W32"},
  {"utf32be",     "-w32B0", "-W32B"},
  {"utf32le",     "-w32L0", "-W32L"},
  {NULL, NULL, NULL}
};

static const nkf_enc_map_entry *
nkf_enc_map_lookup(const char *name)
{
  char buf[64];
  int j = 0;
  const nkf_enc_map_entry *e;

  for (int i = 0; name[i] && j < 63; i++) {
    char c = name[i];
    if (c == '-' || c == '_') continue;
    buf[j++] = (c >= 'A' && c <= 'Z') ? (char)(c + 32) : c;
  }
  buf[j] = '\0';

  for (e = nkf_enc_map; e->normalized; e++) {
    if (strcmp(buf, e->normalized) == 0) return e;
  }
  return NULL;
}

/* ======================================================================
 * NKF type — Python type wrapping nkf_context
 * ====================================================================== */

typedef struct {
  PyObject_HEAD
  nkf_context *ctx;
  PyObject *options;     /* tuple of option strings */
  PyObject *encoding;    /* str or Py_None */
  const char *enc_flag;  /* e.g. "-j", or NULL if no encoding */
  const char *dec_flag;  /* e.g. "-J", or NULL if no encoding */
} NKFObject;

static PyTypeObject NKFType;

/* Helper: run conversion using self->ctx with stored + extra options */
static PyObject *
nkfobj_do_convert(NKFObject *self, unsigned char *data, Py_ssize_t data_len,
                  const char **extra_opts, Py_ssize_t extra_opts_len)
{
  Py_ssize_t i, n;
  pynkf_io_t io;
  int ret;
  PyObject *res;

  nkf_context_init(self->ctx);

  /* Apply stored options */
  n = PyTuple_GET_SIZE(self->options);
  for (i = 0; i < n; i++) {
    const char *opt = PyUnicode_AsUTF8(PyTuple_GET_ITEM(self->options, i));
    if (opt == NULL) return NULL;
    nkf_options(self->ctx, opt);
  }

  /* Apply extra options (for encode/decode direction) */
  for (i = 0; i < extra_opts_len; i++) {
    nkf_options(self->ctx, extra_opts[i]);
  }

  /* Set up I/O */
  io.inbuf = data;
  io.inbuf_size = data_len;
  io.in_pos = 0;
  io.outbuf_size = (Py_ssize_t)(data_len * 1.5) + 256;
  io.outbuf = (unsigned char *)PyMem_Malloc(io.outbuf_size);
  if (io.outbuf == NULL) {
    PyErr_NoMemory();
    return NULL;
  }
  io.out_pos = 0;
  io.suppress_output = 0;
  io.oom = 0;

  nkf_set_io(self->ctx, pynkf_io_getc, pynkf_io_ungetc, pynkf_io_putc, &io);

  ret = nkf_convert(self->ctx);

  if (io.oom || ret != 0) {
    PyMem_Free(io.outbuf);
    PyErr_NoMemory();
    return NULL;
  }

  res = PyBytes_FromStringAndSize((const char *)io.outbuf, io.out_pos);
  PyMem_Free(io.outbuf);
  return res;
}

/* Helper: run guess using self->ctx. Returns 0 on success, -1 on error. */
static int
nkfobj_do_guess(NKFObject *self, unsigned char *data, Py_ssize_t data_len)
{
  Py_ssize_t i, n;
  pynkf_io_t io;

  nkf_context_init(self->ctx);

  n = PyTuple_GET_SIZE(self->options);
  for (i = 0; i < n; i++) {
    const char *opt = PyUnicode_AsUTF8(PyTuple_GET_ITEM(self->options, i));
    if (opt == NULL) return -1;
    nkf_options(self->ctx, opt);
  }

  io.inbuf = data;
  io.inbuf_size = data_len;
  io.in_pos = 0;
  io.outbuf = NULL;
  io.outbuf_size = 0;
  io.out_pos = 0;
  io.suppress_output = 1;
  io.oom = 0;

  nkf_set_io(self->ctx, pynkf_io_getc, pynkf_io_ungetc, pynkf_io_putc, &io);

  nkf_guess(self->ctx);
  return 0;
}

static PyObject *
NKF_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
  NKFObject *self = (NKFObject *)type->tp_alloc(type, 0);
  if (self != NULL) {
    self->ctx = NULL;
    self->options = NULL;
    self->encoding = Py_None;
    Py_INCREF(Py_None);
    self->enc_flag = NULL;
    self->dec_flag = NULL;
  }
  return (PyObject *)self;
}

static int
NKF_init(NKFObject *self, PyObject *args, PyObject *kwargs)
{
  PyObject *encoding_obj = Py_None;
  Py_ssize_t i, n;
  PyObject *tmp;

  /* Extract "encoding" keyword argument */
  if (kwargs != NULL && PyDict_Size(kwargs) > 0) {
    PyObject *key, *value;
    Py_ssize_t pos = 0;
    while (PyDict_Next(kwargs, &pos, &key, &value)) {
      if (PyUnicode_CompareWithASCIIString(key, "encoding") == 0) {
        encoding_obj = value;
      } else {
        PyErr_Format(PyExc_TypeError,
            "NKF() got an unexpected keyword argument '%U'", key);
        return -1;
      }
    }
  }

  /* Validate all positional args are strings */
  n = PyTuple_GET_SIZE(args);
  for (i = 0; i < n; i++) {
    if (!PyUnicode_Check(PyTuple_GET_ITEM(args, i))) {
      PyErr_SetString(PyExc_TypeError, "NKF() options must be strings");
      return -1;
    }
  }

  /* Store options */
  tmp = self->options;
  Py_INCREF(args);
  self->options = args;
  Py_XDECREF(tmp);

  /* Handle encoding */
  if (encoding_obj != Py_None) {
    const char *enc_name;
    const nkf_enc_map_entry *entry;

    if (!PyUnicode_Check(encoding_obj)) {
      PyErr_SetString(PyExc_TypeError, "encoding must be a string");
      return -1;
    }
    enc_name = PyUnicode_AsUTF8(encoding_obj);
    if (enc_name == NULL) return -1;

    entry = nkf_enc_map_lookup(enc_name);
    if (entry == NULL) {
      PyErr_Format(PyExc_ValueError, "unsupported encoding: '%s'", enc_name);
      return -1;
    }

    tmp = self->encoding;
    Py_INCREF(encoding_obj);
    self->encoding = encoding_obj;
    Py_XDECREF(tmp);

    self->enc_flag = entry->enc_flag;
    self->dec_flag = entry->dec_flag;
  } else {
    tmp = self->encoding;
    Py_INCREF(Py_None);
    self->encoding = Py_None;
    Py_XDECREF(tmp);

    self->enc_flag = NULL;
    self->dec_flag = NULL;
  }

  /* Create or reinit context */
  if (self->ctx == NULL) {
    self->ctx = nkf_context_new();
    if (self->ctx == NULL) {
      PyErr_NoMemory();
      return -1;
    }
  }

  return 0;
}

static void
NKF_dealloc(NKFObject *self)
{
  if (self->ctx != NULL) {
    nkf_context_free(self->ctx);
  }
  Py_XDECREF(self->options);
  Py_XDECREF(self->encoding);
  Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *
NKF_convert(NKFObject *self, PyObject *args)
{
  unsigned char *data;
  Py_ssize_t data_len;

  if (!PyArg_ParseTuple(args, "s#", &data, &data_len))
    return NULL;

  return nkfobj_do_convert(self, data, data_len, NULL, 0);
}

static PyObject *
NKF_encode(NKFObject *self, PyObject *args, PyObject *kwargs)
{
  static char *kwlist[] = {"input", "errors", NULL};
  PyObject *input;
  const char *errors = "strict";
  const char *utf8;
  Py_ssize_t utf8_len, input_len;
  const char *extra_opts[2];
  PyObject *result;

  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "U|s", kwlist, &input, &errors))
    return NULL;

  if (self->enc_flag == NULL) {
    PyErr_SetString(PyExc_TypeError,
        "encode() requires 'encoding' parameter in NKF() constructor");
    return NULL;
  }

  utf8 = PyUnicode_AsUTF8AndSize(input, &utf8_len);
  if (utf8 == NULL) return NULL;

  extra_opts[0] = "-W";
  extra_opts[1] = self->enc_flag;
  result = nkfobj_do_convert(self, (unsigned char *)utf8, utf8_len, extra_opts, 2);
  if (result == NULL) return NULL;

  input_len = PyUnicode_GET_LENGTH(input);
  return Py_BuildValue("(Nn)", result, input_len);
}

static PyObject *
NKF_decode(NKFObject *self, PyObject *args, PyObject *kwargs)
{
  static char *kwlist[] = {"input", "errors", NULL};
  Py_buffer buf;
  const char *errors = "strict";
  const char *extra_opts[2];
  PyObject *result, *str;
  Py_ssize_t input_len;

  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "y*|s", kwlist, &buf, &errors))
    return NULL;

  if (self->dec_flag == NULL) {
    PyBuffer_Release(&buf);
    PyErr_SetString(PyExc_TypeError,
        "decode() requires 'encoding' parameter in NKF() constructor");
    return NULL;
  }

  extra_opts[0] = self->dec_flag;
  extra_opts[1] = "-w";
  result = nkfobj_do_convert(self, (unsigned char *)buf.buf, buf.len, extra_opts, 2);
  input_len = buf.len;
  PyBuffer_Release(&buf);
  if (result == NULL) return NULL;

  str = PyUnicode_DecodeUTF8(PyBytes_AS_STRING(result), PyBytes_GET_SIZE(result), errors);
  Py_DECREF(result);
  if (str == NULL) return NULL;

  return Py_BuildValue("(Nn)", str, input_len);
}

static PyObject *
NKF_guess(NKFObject *self, PyObject *args)
{
  unsigned char *data;
  Py_ssize_t data_len;

  if (!PyArg_ParseTuple(args, "s#", &data, &data_len))
    return NULL;

  if (nkfobj_do_guess(self, data, data_len) < 0)
    return NULL;

  return PyUnicode_FromString(nkf_get_guessed_code(self->ctx));
}

static PyObject *
NKF_guess_detail(NKFObject *self, PyObject *args)
{
  unsigned char *data;
  Py_ssize_t data_len;
  const char *eol_name;
  int eol;

  if (!PyArg_ParseTuple(args, "s#", &data, &data_len))
    return NULL;

  if (nkfobj_do_guess(self, data, data_len) < 0)
    return NULL;

  eol = nkf_get_input_eol(self->ctx);

  if (eol == NKF_CR)        eol_name = "CR";
  else if (eol == NKF_LF)   eol_name = "LF";
  else if (eol == NKF_CRLF) eol_name = "CRLF";
  else if (eol == EOF)       eol_name = "MIXED";
  else                       eol_name = NULL;

  return Py_BuildValue("(sz)", nkf_get_guessed_code(self->ctx), eol_name);
}

static PyObject *
NKF_codec_info(NKFObject *self, PyObject *Py_UNUSED(ignored))
{
  PyObject *mod, *func, *result;

  if (self->encoding == Py_None) {
    PyErr_SetString(PyExc_TypeError,
        "codec_info() requires 'encoding' parameter in NKF() constructor");
    return NULL;
  }

  mod = PyImport_ImportModule("nkf.nkf_codec");
  if (mod == NULL) return NULL;

  func = PyObject_GetAttrString(mod, "make_codec_info");
  Py_DECREF(mod);
  if (func == NULL) return NULL;

  result = PyObject_CallOneArg(func, (PyObject *)self);
  Py_DECREF(func);
  return result;
}

static PyObject *
NKF_get_encoding(NKFObject *self, void *closure)
{
  Py_INCREF(self->encoding);
  return self->encoding;
}

static PyObject *
NKF_get_options(NKFObject *self, void *closure)
{
  Py_INCREF(self->options);
  return self->options;
}

static PyMethodDef NKF_methods[] = {
  {"convert", (PyCFunction)NKF_convert, METH_VARARGS,
   "convert(data)\n--\n\n"
   "Convert bytes using stored NKF options.\n"},
  {"encode", (PyCFunction)(void(*)(void))NKF_encode, METH_VARARGS | METH_KEYWORDS,
   "encode(input, errors='strict')\n--\n\n"
   "Encode str to bytes in the target encoding.\n"
   "Returns (bytes, characters_consumed).\n"},
  {"decode", (PyCFunction)(void(*)(void))NKF_decode, METH_VARARGS | METH_KEYWORDS,
   "decode(input, errors='strict')\n--\n\n"
   "Decode bytes from the target encoding to str.\n"
   "Returns (str, bytes_consumed).\n"},
  {"guess", (PyCFunction)NKF_guess, METH_VARARGS,
   "guess(data)\n--\n\n"
   "Detect encoding of byte data.\n"},
  {"guess_detail", (PyCFunction)NKF_guess_detail, METH_VARARGS,
   "guess_detail(data)\n--\n\n"
   "Detect encoding and EOL of byte data.\n"
   "Returns (encoding_name, eol_name_or_None).\n"},
  {"codec_info", (PyCFunction)NKF_codec_info, METH_NOARGS,
   "codec_info()\n--\n\n"
   "Create codecs.CodecInfo for this NKF encoding.\n"},
  {NULL}
};

static PyGetSetDef NKF_getsetters[] = {
  {"encoding", (getter)NKF_get_encoding, NULL, "Encoding name (str or None)", NULL},
  {"options", (getter)NKF_get_options, NULL, "NKF option strings (tuple)", NULL},
  {NULL}
};

static PyTypeObject NKFType = {
  PyVarObject_HEAD_INIT(NULL, 0)
  .tp_name = "_nkf.NKF",
  .tp_doc = PyDoc_STR(
      "NKF(*options, encoding=None)\n\n"
      "NKF codec instance wrapping an nkf_context.\n\n"
      "Parameters:\n"
      "    *options: NKF option strings (e.g., '-m0', '-x', '-j')\n"
      "    encoding: Target encoding name (e.g., 'iso-2022-jp')\n\n"
      "When encoding is specified, encode()/decode() are available.\n"
      "convert() is always available for raw byte conversion.\n"),
  .tp_basicsize = sizeof(NKFObject),
  .tp_itemsize = 0,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_new = NKF_new,
  .tp_init = (initproc)NKF_init,
  .tp_dealloc = (destructor)NKF_dealloc,
  .tp_methods = NKF_methods,
  .tp_getset = NKF_getsetters,
};

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
  PyObject *m;

  if (PyType_Ready(&NKFType) < 0)
    return NULL;

  m = PyModule_Create(&nkfmodule);
  if (m == NULL)
    return NULL;

  if (PyModule_AddObjectRef(m, "NKF", (PyObject *)&NKFType) < 0) {
    Py_DECREF(m);
    return NULL;
  }

  return m;
}
#endif
