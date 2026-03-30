"""pynkf — Python implementation of nkf (Network Kanji Filter) command."""

import os
import sys

import nkf

NKF_VERSION = "2.1.5"
NKF_RELEASE_DATE = "2018-12-15"

USAGE = """\
Usage:  pynkf -[flags] [--] [in file] ..
 j/s/e/w  Specify output encoding ISO-2022-JP, Shift_JIS, EUC-JP
          UTF options is -w[8[0],{16,32}[{B,L}[0]]]
 J/S/E/W  Specify input encoding ISO-2022-JP, Shift_JIS, EUC-JP
          UTF option is -W[8,[16,32][B,L]]
 m[BQSN0] MIME decode [B:base64,Q:quoted,S:strict,N:nonstrict,0:no decode]
 M[BQ]    MIME encode [B:base64 Q:quoted]
 f/F      Folding: -f60 or -f or -f60-10 (fold margin 10) F preserve nl
 Z[0-4]   Default/0: Convert JISX0208 Alphabet to ASCII
          1: Kankaku to one space  2: to two spaces  3: HTML Entity
          4: JISX0208 Katakana to JISX0201 Katakana
 X,x      Convert Halfwidth Katakana to Fullwidth or preserve it
 L[uwm]   Line mode u:LF w:CRLF m:CR (DEFAULT noconversion)
 --ic=<encoding>        Specify the input encoding
 --oc=<encoding>        Specify the output encoding
 --hiragana --katakana  Hiragana/Katakana Conversion
 --katakana-hiragana    Converts each other
 --cap-input            Convert hex after ':'
 --url-input            Convert hex after '%%'
 --numchar-input        Convert Unicode Character Reference
 --fb-{skip, html, xml, perl, java, subchar}
                        Specify unassigned character's replacement
 -g --guess             Guess the input code
 -v --version           Print the version
 --help/-V              Print this help / configuration\
"""


def _version():
    sys.stderr.write(
        f"Network Kanji Filter Version {NKF_VERSION}"
        f" ({NKF_RELEASE_DATE})\n"
        f"Copyright (C) 1987, FUJITSU LTD. (I.Ichikawa).\n"
        f"Copyright (C) 1996-2018, The nkf Project.\n"
        f"pynkf {nkf.__version__}\n"
    )


def _usage():
    sys.stderr.write(USAGE + "\n")
    _version()


def _print_guessed_code(data, guess_level, filename=None):
    """Print guessed encoding, mimicking nkf's print_guessed_code()."""
    prefix = f"{filename}: " if filename is not None else ""

    if guess_level >= 2:
        enc, eol = nkf.guess_detail(data)
        eol_str = f" ({eol})" if eol else ""
        sys.stdout.write(f"{prefix}{enc}{eol_str}\n")
    else:
        enc = nkf.guess(data)
        sys.stdout.write(f"{prefix}{enc}\n")


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    nkf_opts = []
    files = []
    guess_f = 0
    end_of_opts = False

    i = 0
    while i < len(argv):
        arg = argv[i]

        if end_of_opts or not arg.startswith("-") or arg == "-":
            files.append(arg)
            i += 1
            continue

        if arg == "--":
            end_of_opts = True
            i += 1
            continue

        # Long options handled in Python
        if arg.startswith("--"):
            if arg == "--help":
                _usage()
                return 0
            elif arg == "--version":
                _version()
                return 0
            elif arg == "--guess":
                guess_f = 2
                i += 1
                continue
            elif arg.startswith("--guess="):
                val = arg[len("--guess="):]
                guess_f = 1 if val in ("0", "1") else 2
                i += 1
                continue
            else:
                # Pass through to nkf_options
                nkf_opts.append(arg)
                i += 1
                continue

        # Short options handled in Python
        # Check for -v, -V, -g at the START of the option string
        flag = arg[1] if len(arg) > 1 else ""

        if flag == "v":
            _version()
            return 0
        elif flag == "V":
            _usage()
            return 0
        elif flag == "g":
            rest = arg[2:]
            if rest and rest[0] in "01":
                guess_f = 1
            elif rest and "2" <= rest[0] <= "9":
                guess_f = 2
            else:
                guess_f = 1
            i += 1
            continue
        else:
            nkf_opts.append(arg)
            i += 1
            continue

    # Process input
    has_error = False

    if guess_f:
        _process_guess(nkf_opts, files, guess_f)
    else:
        has_error = _process_convert(nkf_opts, files)

    return 1 if has_error else 0


def _process_guess(nkf_opts, files, guess_f):
    """Guess mode: detect encoding and print."""
    if not files:
        data = sys.stdin.buffer.read()
        _print_guessed_code(data, guess_f)
    else:
        show_filename = len(files) > 1
        for filepath in files:
            if filepath == "-":
                data = sys.stdin.buffer.read()
                filename = None
            else:
                try:
                    with open(filepath, "rb") as f:
                        data = f.read()
                except OSError as e:
                    print(f"{filepath}: {e.strerror}", file=sys.stderr)
                    continue
                filename = filepath if show_filename else None
            _print_guessed_code(data, guess_f, filename)


def _process_convert(nkf_opts, files):
    """Normal mode: convert and output."""
    has_error = False
    stdout = sys.stdout.buffer

    if not files:
        data = sys.stdin.buffer.read()
        result = nkf.nkf(nkf_opts, data) if nkf_opts else data
        stdout.write(result)
    else:
        for filepath in files:
            if filepath == "-":
                data = sys.stdin.buffer.read()
            else:
                try:
                    with open(filepath, "rb") as f:
                        data = f.read()
                except OSError as e:
                    print(f"{filepath}: {e.strerror}", file=sys.stderr)
                    has_error = True
                    continue
            result = nkf.nkf(nkf_opts, data) if nkf_opts else data
            stdout.write(result)

    try:
        stdout.flush()
    except BrokenPipeError:
        pass

    return has_error


if __name__ == "__main__":
    sys.exit(main())
