/*
 * nkf.h - NKF public API
 *
 * This header defines the public API for using NKF in a reentrant manner.
 * All mutable state is encapsulated in nkf_context_t.
 */

#ifndef NKF_H
#define NKF_H

#include "nkf_internal.h"

/* Forward declaration (opaque) */
typedef struct nkf_context nkf_context_t;

/* External I/O callback types */
typedef nkf_char (*nkf_ext_getc_fn)(void *user_data);
typedef nkf_char (*nkf_ext_ungetc_fn)(nkf_char c, void *user_data);
typedef void     (*nkf_ext_putc_fn)(nkf_char c, void *user_data);

/* Lifecycle */
nkf_context_t *nkf_context_new(void);
void nkf_context_free(nkf_context_t *ctx);

/* I/O setup */
void nkf_context_set_input(nkf_context_t *ctx, nkf_ext_getc_fn getc_fn, nkf_ext_ungetc_fn ungetc_fn, void *user_data);
void nkf_context_set_output(nkf_context_t *ctx, nkf_ext_putc_fn putc_fn, void *user_data);

/* Conversion */
int nkf_convert(nkf_context_t *ctx, const char *options);
const char *nkf_get_guessed_code(nkf_context_t *ctx);

#endif /* NKF_H */
