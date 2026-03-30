/*
 * nkf.h - Public API for NKF (Network Kanji Filter)
 *
 * This header defines the public interface for embedding NKF.
 * Include this file from external code (e.g., NKF_python.c).
 * Internal implementation details are in nkf_private.h.
 */

#ifndef NKF_H
#define NKF_H

#include <stdlib.h>
#include <string.h>

/* Compatibility definitions */

#ifndef nkf_char
typedef int nkf_char;
#define NKF_INT32_C(n)   (n)
#endif

#ifndef ARG_UNUSED
#if defined(__GNUC__)
#  define ARG_UNUSED  __attribute__ ((unused))
#else
#  define ARG_UNUSED
#endif
#endif

/* Boolean constants */
#define NKF_FALSE   0
#define NKF_TRUE    1

/* --- Encoding IDs --- */

enum nkf_encodings {
    NKF_ASCII,
    NKF_ISO_8859_1,
    NKF_ISO_2022_JP,
    NKF_CP50220,
    NKF_CP50221,
    NKF_CP50222,
    NKF_ISO_2022_JP_1,
    NKF_ISO_2022_JP_3,
    NKF_ISO_2022_JP_2004,
    NKF_SHIFT_JIS,
    NKF_WINDOWS_31J,
    NKF_CP10001,
    NKF_EUC_JP,
    NKF_EUCJP_NKF,
    NKF_CP51932,
    NKF_EUCJP_MS,
    NKF_EUCJP_ASCII,
    NKF_SHIFT_JISX0213,
    NKF_SHIFT_JIS_2004,
    NKF_EUC_JISX0213,
    NKF_EUC_JIS_2004,
    NKF_UTF_8,
    NKF_UTF_8N,
    NKF_UTF_8_BOM,
    NKF_UTF8_MAC,
    NKF_UTF_16,
    NKF_UTF_16BE,
    NKF_UTF_16BE_BOM,
    NKF_UTF_16LE,
    NKF_UTF_16LE_BOM,
    NKF_UTF_32,
    NKF_UTF_32BE,
    NKF_UTF_32BE_BOM,
    NKF_UTF_32LE,
    NKF_UTF_32LE_BOM,
    NKF_BINARY,
    NKF_ENCODING_TABLE_SIZE,
    NKF_JIS_X_0201_1976_K = 0x1013,
    NKF_JIS_X_0208        = 0x1168,
    NKF_JIS_X_0212        = 0x1159,
    NKF_JIS_X_0213_2      = 0x1229,
    NKF_JIS_X_0213_1      = 0x1233
};

/* --- Byte order --- */

enum nkf_byte_order {
    NKF_ENDIAN_BIG    = 1,
    NKF_ENDIAN_LITTLE = 2,
    NKF_ENDIAN_2143   = 3,
    NKF_ENDIAN_3412   = 4
};

/* --- Error codes --- */

#define NKF_OK              0
#define NKF_ERROR_OOM       1   /* Out of memory */
#define NKF_ERROR_INTERNAL  2   /* Internal error (e.g., unconnected module) */

/* --- ASCII control codes --- */

#define NKF_BS      0x08
#define NKF_TAB     0x09
#define NKF_LF      0x0a
#define NKF_CR      0x0d
#define NKF_ESC     0x1b
#define NKF_SP      0x20
#define NKF_DEL     0x7f
#define NKF_SI      0x0f
#define NKF_SO      0x0e
#define NKF_SS2     0x8e
#define NKF_SS3     0x8f
#define NKF_CRLF    0x0D0A

/* --- Opaque context type --- */

typedef struct nkf_context nkf_context;

/* --- Type declarations for encoding tables --- */

typedef struct nkf_native_encoding nkf_native_encoding;
typedef struct nkf_encoding nkf_encoding;

/* --- I/O callback typedefs for embedding --- */

/*
 * Embedders provide these callbacks to redirect NKF's I/O
 * to in-memory buffers or other destinations.
 *
 * io_getc:   Return next input byte (0-255), or EOF (-1) on end.
 * io_ungetc: Push back one byte to input. Return the byte, or EOF on error.
 * io_putc:   Write one output byte. Set ctx error_code on failure.
 */
typedef int  (*nkf_io_getc_t)(void *userdata);
typedef int  (*nkf_io_ungetc_t)(void *userdata, int c);
typedef void (*nkf_io_putc_t)(void *userdata, int c);

/* --- Public API --- */

/*
 * Allocate and initialize a new NKF context.
 * Returns NULL on allocation failure.
 */
nkf_context *nkf_context_new(void);

/*
 * Free an NKF context and all associated resources.
 */
void nkf_context_free(nkf_context *ctx);

/*
 * Reset all conversion state to defaults.
 * Called automatically by nkf_context_new(), but can be called
 * again to reuse a context for a new conversion.
 */
void nkf_context_init(nkf_context *ctx);

/*
 * Set I/O callbacks for the context.
 * Must be called before nkf_convert() or nkf_guess().
 */
void nkf_set_io(nkf_context *ctx,
                 nkf_io_getc_t getc_func,
                 nkf_io_ungetc_t ungetc_func,
                 nkf_io_putc_t putc_func,
                 void *userdata);

/*
 * Parse an option string (e.g., "-j", "-w", "--ic=UTF-8").
 * Can be called multiple times to set multiple options.
 * Returns 0 on success, nonzero on error.
 */
int nkf_options(nkf_context *ctx, const char *option);

/*
 * Perform character encoding conversion.
 * Reads input via io_getc, writes output via io_putc.
 * Returns 0 on success, or an NKF_ERROR_* code.
 */
int nkf_convert(nkf_context *ctx);

/*
 * Detect the encoding of input data.
 * Reads input via io_getc (output is suppressed).
 * After calling, use nkf_get_guessed_code() to retrieve the result.
 * Returns 0 on success.
 */
int nkf_guess(nkf_context *ctx);

/*
 * Get the name of the detected encoding after nkf_guess().
 * Returns a pointer to a static string (e.g., "UTF-8", "Shift_JIS").
 */
const char *nkf_get_guessed_code(nkf_context *ctx);

/*
 * Get the detected input end-of-line style after conversion/guess.
 * Returns NKF_CR, NKF_LF, NKF_CRLF, EOF (mixed), or 0 (undetected).
 */
int nkf_get_input_eol(nkf_context *ctx);

/*
 * Get the output encoding object (for inspecting encoding properties).
 * Returns NULL if not yet determined.
 */
nkf_encoding *nkf_get_output_encoding(nkf_context *ctx);

/*
 * Get the error code from the last operation.
 */
int nkf_get_error(nkf_context *ctx);

/* --- Encoding utility functions --- */

const char *nkf_enc_name(nkf_encoding *enc);
int nkf_enc_to_index(nkf_encoding *enc);
nkf_native_encoding *nkf_enc_to_base_encoding(nkf_encoding *enc);

/* --- Well-known encoding objects (extern, defined in nkf.c) --- */

extern nkf_native_encoding NkfEncodingASCII;
extern nkf_native_encoding NkfEncodingISO_2022_JP;
extern nkf_native_encoding NkfEncodingShift_JIS;
extern nkf_native_encoding NkfEncodingEUC_JP;
extern nkf_native_encoding NkfEncodingUTF_8;
extern nkf_native_encoding NkfEncodingUTF_16;
extern nkf_native_encoding NkfEncodingUTF_32;

#endif /* NKF_H */
