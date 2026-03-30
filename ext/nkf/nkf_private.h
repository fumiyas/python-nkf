/*
 * nkf_private.h - Internal definitions for NKF
 *
 * This header defines the full nkf_context struct, internal function pointer
 * types, constants, buffer types, and accessor macros.
 * Include this ONLY from nkf.c — external code should use nkf.h.
 */

#ifndef NKF_PRIVATE_H
#define NKF_PRIVATE_H

#include "nkf.h"
#include "config.h"

#include <assert.h>

/* --- Platform compatibility (from old nkf.h) --- */

#if (defined(__TURBOC__) || defined(_MSC_VER) || defined(LSI_C) || \
     (defined(__WATCOMC__) && defined(__386__) && !defined(__LINUX__)) || \
     defined(__MINGW32__) || defined(__EMX__) || defined(__MSDOS__) || \
     defined(__WINDOWS__) || defined(__DOS__) || defined(__OS2__)) && !defined(MSDOS)
#define MSDOS
#if (defined(__Win32__) || defined(_WIN32)) && !defined(__WIN32__)
#define __WIN32__
#endif
#endif

#ifdef PERL_XS
#undef OVERWRITE
#endif

#ifndef PERL_XS
#include <stdio.h>
#endif

#if defined(MSDOS) || defined(__OS2__)
#include <fcntl.h>
#include <io.h>
#if defined(_MSC_VER) || defined(__WATCOMC__)
#define mktemp _mktemp
#endif
#endif

#ifdef MSDOS
#ifdef LSI_C
#define setbinmode(fp) fsetbin(fp)
#elif defined(__DJGPP__)
#include <libc/dosio.h>
#define setbinmode(fp) /* TODO */
#else
#define setbinmode(fp) setmode(fileno(fp), O_BINARY)
#endif
#else
#define setbinmode(fp) (void)(fp)
#endif

#ifdef _IOFBF
#define setvbuffer(fp, buf, size) setvbuf(fp, buf, _IOFBF, size)
#else
#define setvbuffer(fp, buf, size) setbuffer(fp, buf, size)
#endif

#if !defined(DEFAULT_CODE_JIS) && !defined(DEFAULT_CODE_SJIS) && \
    !defined(DEFAULT_CODE_WINDOWS_31J) && !defined(DEFAULT_CODE_EUC) && \
    !defined(DEFAULT_CODE_UTF8) && !defined(DEFAULT_CODE_LOCALE)
#define DEFAULT_CODE_LOCALE
#endif

#ifdef DEFAULT_CODE_LOCALE
#if defined(__WIN32__)
# ifndef HAVE_LOCALE_H
#  define HAVE_LOCALE_H
# endif
#elif defined(__OS2__)
# undef HAVE_LANGINFO_H
# ifndef HAVE_LOCALE_H
#  define HAVE_LOCALE_H
# endif
#elif defined(MSDOS)
# ifndef HAVE_LOCALE_H
#  define HAVE_LOCALE_H
# endif
#elif defined(__BIONIC__)
#else
# ifndef HAVE_LANGINFO_H
#  define HAVE_LANGINFO_H
# endif
# ifndef HAVE_LOCALE_H
#  define HAVE_LOCALE_H
# endif
#endif
#ifdef HAVE_LANGINFO_H
#include <langinfo.h>
#endif
#ifdef HAVE_LOCALE_H
#include <locale.h>
#endif
#endif /* DEFAULT_CODE_LOCALE */

/* --- Legacy boolean aliases (for minimal diff in nkf.c) --- */

#ifndef FALSE
#define FALSE NKF_FALSE
#endif
#ifndef TRUE
#define TRUE  NKF_TRUE
#endif

/* --- Legacy constant aliases (for minimal diff in nkf.c) --- */

#define BS      NKF_BS
#define TAB     NKF_TAB
#define LF      NKF_LF
#define CR      NKF_CR
#define ESC     NKF_ESC
#define SP      NKF_SP
#define DEL     NKF_DEL
#define SI      NKF_SI
#define SO      NKF_SO
#define SS2     NKF_SS2
#define SS3     NKF_SS3
#define CRLF    NKF_CRLF

/* Encoding enum aliases (for minimal diff in nkf.c) */
#define ASCII           NKF_ASCII
#define ISO_8859_1      NKF_ISO_8859_1
#define ISO_2022_JP     NKF_ISO_2022_JP
#define CP50220         NKF_CP50220
#define CP50221         NKF_CP50221
#define CP50222         NKF_CP50222
#define ISO_2022_JP_1   NKF_ISO_2022_JP_1
#define ISO_2022_JP_3   NKF_ISO_2022_JP_3
#define ISO_2022_JP_2004 NKF_ISO_2022_JP_2004
#define SHIFT_JIS       NKF_SHIFT_JIS
#define WINDOWS_31J     NKF_WINDOWS_31J
#define CP10001         NKF_CP10001
#define EUC_JP          NKF_EUC_JP
#define EUCJP_NKF       NKF_EUCJP_NKF
#define CP51932         NKF_CP51932
#define EUCJP_MS        NKF_EUCJP_MS
#define EUCJP_ASCII     NKF_EUCJP_ASCII
#define SHIFT_JISX0213  NKF_SHIFT_JISX0213
#define SHIFT_JIS_2004  NKF_SHIFT_JIS_2004
#define EUC_JISX0213    NKF_EUC_JISX0213
#define EUC_JIS_2004    NKF_EUC_JIS_2004
#define UTF_8           NKF_UTF_8
#define UTF_8N          NKF_UTF_8N
#define UTF_8_BOM       NKF_UTF_8_BOM
#define UTF8_MAC        NKF_UTF8_MAC
#define UTF_16          NKF_UTF_16
#define UTF_16BE        NKF_UTF_16BE
#define UTF_16BE_BOM    NKF_UTF_16BE_BOM
#define UTF_16LE        NKF_UTF_16LE
#define UTF_16LE_BOM    NKF_UTF_16LE_BOM
#define UTF_32          NKF_UTF_32
#define UTF_32BE        NKF_UTF_32BE
#define UTF_32BE_BOM    NKF_UTF_32BE_BOM
#define UTF_32LE        NKF_UTF_32LE
#define UTF_32LE_BOM    NKF_UTF_32LE_BOM
#define BINARY          NKF_BINARY
#define NKF_ENCODING_TABLE_SIZE NKF_ENCODING_TABLE_SIZE
#define JIS_X_0201_1976_K NKF_JIS_X_0201_1976_K
#define JIS_X_0208      NKF_JIS_X_0208
#define JIS_X_0212      NKF_JIS_X_0212
#define JIS_X_0213_2    NKF_JIS_X_0213_2
#define JIS_X_0213_1    NKF_JIS_X_0213_1

/* Byte order aliases */
#define ENDIAN_BIG      NKF_ENDIAN_BIG
#define ENDIAN_LITTLE   NKF_ENDIAN_LITTLE
#define ENDIAN_2143     NKF_ENDIAN_2143
#define ENDIAN_3412     NKF_ENDIAN_3412

/* --- Internal constants --- */

#define MIME_DECODE_DEFAULT STRICT_MIME

#ifndef MIME_DECODE_DEFAULT
#define MIME_DECODE_DEFAULT STRICT_MIME
#endif
#ifndef X0201_DEFAULT
#define X0201_DEFAULT TRUE
#endif

#if DEFAULT_NEWLINE == 0x0D0A
#elif DEFAULT_NEWLINE == 0x0D
#else
#define DEFAULT_NEWLINE 0x0A
#endif

#define FIXED_MIME      7
#define STRICT_MIME     8

#define HOLD_SIZE       1024

#define IOBUF_SIZE      16384

#define DEFAULT_J       'B'
#define DEFAULT_R       'B'

#define GETA1   0x22
#define GETA2   0x2e

#define UCS_MAP_ASCII   0
#define UCS_MAP_MS      1
#define UCS_MAP_CP932   2
#define UCS_MAP_CP10001 3

#define NKF_UNSPECIFIED (-TRUE)

#define FOLD_MARGIN     10
#define DEFAULT_FOLD    60

#define MIME_BUF_SIZE       (1024)
#define MIME_BUF_MASK       (MIME_BUF_SIZE - 1)
#define MIMEOUT_BUF_LENGTH  74

#define STD_GC_BUFSIZE      (256)

#define MAXRECOVER  20

/* Default encoding index */
#if defined(DEFAULT_CODE_JIS)
#define DEFAULT_ENCIDX ISO_2022_JP
#elif defined(DEFAULT_CODE_SJIS)
#define DEFAULT_ENCIDX SHIFT_JIS
#elif defined(DEFAULT_CODE_WINDOWS_31J)
#define DEFAULT_ENCIDX WINDOWS_31J
#elif defined(DEFAULT_CODE_EUC)
#define DEFAULT_ENCIDX EUC_JP
#elif defined(DEFAULT_CODE_UTF8)
#define DEFAULT_ENCIDX UTF_8
#endif

/* --- Helper macros (pure, no state) --- */

#define is_alnum(c) \
    (('a'<=(c) && (c)<='z') || ('A'<=(c) && (c)<='Z') || ('0'<=(c) && (c)<='9'))

#define nkf_toupper(c) (('a'<=(c) && (c)<='z') ? ((c)-('a'-'A')) : (c))
#define nkf_isoctal(c)  ('0'<=(c) && (c)<='7')
#define nkf_isdigit(c)  ('0'<=(c) && (c)<='9')
#define nkf_isxdigit(c) (nkf_isdigit(c) || ('a'<=(c) && (c)<='f') || ('A'<=(c) && (c)<='F'))
#define nkf_isblank(c)  ((c) == SP || (c) == TAB)
#define nkf_isspace(c)  (nkf_isblank(c) || (c) == CR || (c) == LF)
#define nkf_isalpha(c)  (('a'<=(c) && (c)<='z') || ('A'<=(c) && (c)<='Z'))
#define nkf_isalnum(c)  (nkf_isdigit(c) || nkf_isalpha(c))
#define nkf_isprint(c)  (SP<=(c) && (c)<='~')
#define nkf_isgraph(c)  ('!'<=(c) && (c)<='~')
#define hex2bin(c) (('0'<=(c) && (c)<='9') ? ((c)-'0') : \
                    ('A'<=(c) && (c)<='F') ? ((c)-'A'+10) : \
                    ('a'<=(c) && (c)<='f') ? ((c)-'a'+10) : 0)
#define bin2hex(c) ("0123456789ABCDEF"[(c)&15])
#define is_eucg3(c2) (((unsigned short)(c2) >> 8) == SS3)
#define nkf_noescape_mime(c) ((c) == CR || (c) == LF || \
    ((c) > SP && (c) < DEL && (c) != '?' && (c) != '=' && (c) != '_' \
     && (c) != '(' && (c) != ')' && (c) != '.' && (c) != 0x22))

#define is_ibmext_in_sjis(c2) (CP932_TABLE_BEGIN <= (c2) && (c2) <= CP932_TABLE_END)
#define nkf_byte_jisx0201_katakana_p(c) (SP <= (c) && (c) <= 0x5F)

/* Unicode classification */
#define CLASS_MASK     NKF_INT32_C(0xFF000000)
#define CLASS_UNICODE  NKF_INT32_C(0x01000000)
#define VALUE_MASK     NKF_INT32_C(0x00FFFFFF)
#define UNICODE_BMP_MAX NKF_INT32_C(0x0000FFFF)
#define UNICODE_MAX    NKF_INT32_C(0x0010FFFF)

#define nkf_char_euc3_new(c)       ((c) | CLASS_MASK)
#define nkf_char_unicode_new(c)    ((c) | CLASS_UNICODE)
#define nkf_char_unicode_p(c)      (((c) & CLASS_MASK) == CLASS_UNICODE)
#define nkf_char_unicode_bmp_p(c)  (((c) & VALUE_MASK) <= UNICODE_BMP_MAX)
#define nkf_char_unicode_value_p(c) (((c) & VALUE_MASK) <= UNICODE_MAX)

#define UTF16_TO_UTF32(lead, trail) \
    (((lead) << 10) + (trail) - NKF_INT32_C(0x35FDC00))

/* rot13/rot47 */
#define rot13(c) ( \
    ( c < 'A') ? c: \
    (c <= 'M')  ? (c + 13): \
    (c <= 'Z')  ? (c - 13): \
    (c < 'a')   ? (c): \
    (c <= 'm')  ? (c + 13): \
    (c <= 'z')  ? (c - 13): \
    (c) \
    )
#define rot47(c) ( \
    ( c < '!') ? c: \
    ( c <= 'O') ? (c + 47) : \
    ( c <= '~') ?  (c - 47) : \
    c \
    )

/* Memory allocation */
#define nkf_xfree(ptr)  free(ptr)

/* --- Internal type definitions --- */

/* nkf_buf_t: Fixed-capacity character buffer (embedded in context) */
typedef struct {
    long capa;
    long len;
    nkf_char *ptr;
} nkf_buf_t;

#define nkf_buf_length(buf)   ((buf)->len)
#define nkf_buf_empty_p(buf)  ((buf)->len == 0)

/* Encoding types (full definitions) */
struct nkf_native_encoding {
    const char *name;
    nkf_char (*iconv_func)(nkf_context *ctx, nkf_char c2, nkf_char c1, nkf_char c0);
    void (*oconv_func)(nkf_context *ctx, nkf_char c2, nkf_char c1);
};

struct nkf_encoding {
    const int id;
    const char *name;
    const nkf_native_encoding *base_encoding;
};

/* Input code detection state */
struct input_code {
    const char *name;
    nkf_char stat;
    nkf_char score;
    nkf_char index;
    nkf_char buf[3];
    void (*status_func)(nkf_context *ctx, struct input_code *, nkf_char);
    nkf_char (*iconv_func)(nkf_context *ctx, nkf_char c2, nkf_char c1, nkf_char c0);
    int _file_stat;
};

#define INPUT_CODE_LIST_SIZE 8  /* EUC, SJIS, UTF-8, UTF-16, UTF-32, sentinel + spare */

/* --- Internal function pointer typedefs --- */

typedef nkf_char (*nkf_getc_t)(nkf_context *ctx);
typedef nkf_char (*nkf_ungetc_t)(nkf_context *ctx, nkf_char c);
typedef void     (*nkf_putc_t)(nkf_context *ctx, nkf_char c);
typedef nkf_char (*nkf_iconv_t)(nkf_context *ctx, nkf_char c2, nkf_char c1, nkf_char c0);
typedef void     (*nkf_oconv_t)(nkf_context *ctx, nkf_char c2, nkf_char c1);
typedef void     (*nkf_fallback_t)(nkf_context *ctx, nkf_char c);

/* --- Full context struct definition --- */

struct nkf_context {
    /* === Encoding state === */
    const char *input_codename;     /* NULL: unestablished, "": BINARY */
    nkf_encoding *input_encoding;
    nkf_encoding *output_encoding;
    int output_mode;                /* ASCII, JIS_X_0208, etc. */
    int input_mode;
    int mime_decode_mode;           /* FALSE, 'B' (base64), 'Q' (quoted) */

    /* === Feature flags === */
    int ms_ucs_map_f;
    int no_cp932ext_f;
    int no_best_fit_chars_f;
    int input_endian;
    int input_bom_f;
    nkf_char unicode_subchar;
    int output_bom_f;
    int output_endian;

    int unbuf_f;
    int estab_f;
    int nop_f;
    int binmode_f;
    int rot_f;
    int hira_f;
    int alpha_f;
    int mime_f;
    int mime_decode_f;
    int mimebuf_f;
    int broken_f;
    int iso8859_f;
    int mimeout_f;
    int x0201_f;
    int iso2022jp_f;

    int nfc_f;
    int cap_f;
    int url_f;
    int numchar_f;
    int noout_f;
    int debug_f;
    int guess_f;            /* 0: OFF, 1: ON, 2: VERBOSE */
    int exec_f;

    int cp51932_f;
    int cp932inv_f;
    int x0212_f;
    int x0213_f;

    /* Fold/format options */
    int fold_f;
    int fold_preserve_f;
    int fold_len;
    int fold_margin;
    int f_line;             /* chars in line */
    int f_prev;
    unsigned char kanji_intro;
    unsigned char ascii_intro;

    /* File/option state */
    int option_mode;
    int file_out_f;
    int overwrite_f;
    int preserve_time_f;
    int backup_f;
    char *backup_suffix;
    int eolmode_f;          /* CR, LF, CRLF */
    int input_eol;          /* 0: unestablished, EOF: MIXED */
    nkf_char prev_cr;
    int end_check;

    unsigned char prefix_table[256];

    /* === I/O function pointer chain (conversion pipeline) === */
    nkf_iconv_t    iconv;
    nkf_oconv_t    oconv;
    nkf_oconv_t    o_zconv;
    nkf_oconv_t    o_fconv;
    nkf_oconv_t    o_eol_conv;
    nkf_oconv_t    o_rot_conv;
    nkf_oconv_t    o_hira_conv;
    nkf_oconv_t    o_base64conv;
    nkf_oconv_t    o_iso2022jp_check_conv;
    nkf_putc_t     o_putc;

    nkf_getc_t     i_getc;
    nkf_ungetc_t   i_ungetc;
    nkf_getc_t     i_bgetc;
    nkf_ungetc_t   i_bungetc;

    nkf_putc_t     o_mputc;
    nkf_getc_t     i_mgetc;
    nkf_ungetc_t   i_mungetc;
    nkf_getc_t     i_mgetc_buf;
    nkf_ungetc_t   i_mungetc_buf;

    nkf_getc_t     i_nfc_getc;
    nkf_ungetc_t   i_nfc_ungetc;
    nkf_getc_t     i_cgetc;
    nkf_ungetc_t   i_cungetc;
    nkf_getc_t     i_ugetc;
    nkf_ungetc_t   i_uungetc;
    nkf_getc_t     i_ngetc;
    nkf_ungetc_t   i_nungetc;

    nkf_iconv_t    iconv_for_check;
    nkf_iconv_t    mime_iconv_back;
    nkf_fallback_t encode_fallback;

    /* === Buffers & runtime conversion state === */
    int mimeout_mode;       /* 0, -1, 'Q', 'B', 1, 2 */
    int base64_count;

    nkf_char hold_buf[HOLD_SIZE * 2];
    int hold_count;

    nkf_char z_prev2;
    nkf_char z_prev1;

    /* Encoding detection state (per-context copy) */
    struct input_code input_code_list[INPUT_CODE_LIST_SIZE];

    /*
     * Formerly nkf_state_t fields (flattened into context).
     * In original code these were accessed as nkf_state->field.
     * After refactoring, access directly as ctx->field.
     * No accessor macros for these — the 31 uses in nkf.c
     * are changed to ctx->field in Phase 2.
     */
    nkf_buf_t *std_gc_buf;
    nkf_char broken_state;
    nkf_buf_t *broken_buf;
    nkf_char mimeout_b64_state;  /* was nkf_state->mimeout_state */
    nkf_buf_t *nfc_buf;

    /* MIME input ring buffer */
    struct {
        unsigned char buf[MIME_BUF_SIZE];
        unsigned int top;
        unsigned int last;
        unsigned int input;
    } mime_input_state;

    /* MIME output buffer */
    struct {
        unsigned char buf[MIMEOUT_BUF_LENGTH + 1];
        int count;
    } mimeout_state;

    /* Encoding name buffer (replaces function-local static buf[16]) */
    char enc_name_buf[16];
    char enc_name_buf2[16];

    /* === Embedder-provided I/O callbacks === */
    void *io_userdata;
    nkf_io_getc_t   io_getc;
    nkf_io_ungetc_t  io_ungetc;
    nkf_io_putc_t    io_putc;

    /* === Error state === */
    int error_code;         /* NKF_OK, NKF_ERROR_OOM, etc. */
};

/* --- Accessor macros --- */
/*
 * These macros allow nkf.c function bodies to refer to context fields
 * using their original global variable names, provided every function
 * has `nkf_context *ctx` as a parameter.
 *
 * This dramatically reduces the diff in nkf.c function bodies.
 */

/* Encoding state */
#define input_codename      (ctx->input_codename)
#define input_encoding      (ctx->input_encoding)
#define output_encoding     (ctx->output_encoding)
#define output_mode         (ctx->output_mode)
#define input_mode          (ctx->input_mode)
#define mime_decode_mode    (ctx->mime_decode_mode)

/* Feature flags */
#define ms_ucs_map_f        (ctx->ms_ucs_map_f)
#define no_cp932ext_f       (ctx->no_cp932ext_f)
#define no_best_fit_chars_f (ctx->no_best_fit_chars_f)
#define input_endian        (ctx->input_endian)
#define input_bom_f         (ctx->input_bom_f)
#define unicode_subchar     (ctx->unicode_subchar)
#define output_bom_f        (ctx->output_bom_f)
#define output_endian       (ctx->output_endian)
#define unbuf_f             (ctx->unbuf_f)
#define estab_f             (ctx->estab_f)
#define nop_f               (ctx->nop_f)
#define binmode_f           (ctx->binmode_f)
#define rot_f               (ctx->rot_f)
#define hira_f              (ctx->hira_f)
#define alpha_f             (ctx->alpha_f)
#define mime_f              (ctx->mime_f)
#define mime_decode_f       (ctx->mime_decode_f)
#define mimebuf_f           (ctx->mimebuf_f)
#define broken_f            (ctx->broken_f)
#define iso8859_f           (ctx->iso8859_f)
#define mimeout_f           (ctx->mimeout_f)
#define x0201_f             (ctx->x0201_f)
#define iso2022jp_f         (ctx->iso2022jp_f)
#define nfc_f               (ctx->nfc_f)
#define cap_f               (ctx->cap_f)
#define url_f               (ctx->url_f)
#define numchar_f           (ctx->numchar_f)
#define noout_f             (ctx->noout_f)
#define debug_f             (ctx->debug_f)
#define guess_f             (ctx->guess_f)
#define exec_f              (ctx->exec_f)
#define cp51932_f           (ctx->cp51932_f)
#define cp932inv_f          (ctx->cp932inv_f)
#define x0212_f             (ctx->x0212_f)
#define x0213_f             (ctx->x0213_f)
#define fold_f              (ctx->fold_f)
#define fold_preserve_f     (ctx->fold_preserve_f)
#define fold_len            (ctx->fold_len)
#define fold_margin         (ctx->fold_margin)
#define f_line              (ctx->f_line)
#define f_prev              (ctx->f_prev)
#define kanji_intro         (ctx->kanji_intro)
#define ascii_intro         (ctx->ascii_intro)
#define option_mode         (ctx->option_mode)
#define file_out_f          (ctx->file_out_f)
#define overwrite_f         (ctx->overwrite_f)
#define preserve_time_f     (ctx->preserve_time_f)
#define backup_f            (ctx->backup_f)
#define backup_suffix       (ctx->backup_suffix)
#define eolmode_f           (ctx->eolmode_f)
#define input_eol           (ctx->input_eol)
#define prev_cr             (ctx->prev_cr)
#define end_check           (ctx->end_check)
#define prefix_table        (ctx->prefix_table)

/* Function pointer chain */
#define iconv               (ctx->iconv)
#define oconv               (ctx->oconv)
#define o_zconv             (ctx->o_zconv)
#define o_fconv             (ctx->o_fconv)
#define o_eol_conv          (ctx->o_eol_conv)
#define o_rot_conv          (ctx->o_rot_conv)
#define o_hira_conv         (ctx->o_hira_conv)
#define o_base64conv        (ctx->o_base64conv)
#define o_iso2022jp_check_conv (ctx->o_iso2022jp_check_conv)
#define o_putc              (ctx->o_putc)
#define i_getc              (ctx->i_getc)
#define i_ungetc            (ctx->i_ungetc)
#define i_bgetc             (ctx->i_bgetc)
#define i_bungetc           (ctx->i_bungetc)
#define o_mputc             (ctx->o_mputc)
#define i_mgetc             (ctx->i_mgetc)
#define i_mungetc           (ctx->i_mungetc)
#define i_mgetc_buf         (ctx->i_mgetc_buf)
#define i_mungetc_buf       (ctx->i_mungetc_buf)
#define i_nfc_getc          (ctx->i_nfc_getc)
#define i_nfc_ungetc        (ctx->i_nfc_ungetc)
#define i_cgetc             (ctx->i_cgetc)
#define i_cungetc           (ctx->i_cungetc)
#define i_ugetc             (ctx->i_ugetc)
#define i_uungetc           (ctx->i_uungetc)
#define i_ngetc             (ctx->i_ngetc)
#define i_nungetc           (ctx->i_nungetc)
#define iconv_for_check     (ctx->iconv_for_check)
#define mime_iconv_back     (ctx->mime_iconv_back)
#define encode_fallback     (ctx->encode_fallback)

/* Buffers & state */
#define mimeout_mode        (ctx->mimeout_mode)
#define base64_count        (ctx->base64_count)
#define hold_buf            (ctx->hold_buf)
#define hold_count          (ctx->hold_count)
#define z_prev2             (ctx->z_prev2)
#define z_prev1             (ctx->z_prev1)
#define input_code_list     (ctx->input_code_list)
/*
 * nkf_state fields: NO accessor macros.
 * Original code uses nkf_state->std_gc_buf, nkf_state->broken_state, etc.
 * After refactoring, these become ctx->std_gc_buf, ctx->broken_state, etc.
 * nkf_state->mimeout_state becomes ctx->mimeout_b64_state.
 */
/*
 * NOTE: No accessor macro for mime_input_state or mimeout_state.
 * Use ctx->mime_input_state and ctx->mimeout_state directly.
 * Having them as macros would conflict with the mime_input_buf macro
 * and nkf_state->mimeout_state (now ctx->mimeout_b64_state) patterns.
 */

/* MIME input buffer access */
#define mime_input_buf(n)   (ctx->mime_input_state.buf[(n) & MIME_BUF_MASK])

/* --- nkf_buf_t operations --- */

static inline nkf_char
nkf_buf_at(nkf_buf_t *buf, int index)
{
    assert(index <= buf->len);
    return buf->ptr[index];
}

static inline void
nkf_buf_clear(nkf_buf_t *buf)
{
    buf->len = 0;
}

static inline void
nkf_buf_push(nkf_buf_t *buf, nkf_char c)
{
    assert(buf->len < buf->capa);
    buf->ptr[buf->len++] = c;
}

static inline nkf_char
nkf_buf_pop(nkf_buf_t *buf)
{
    assert(buf->len > 0);
    return buf->ptr[--buf->len];
}

#endif /* NKF_PRIVATE_H */
