Python Interface to NKF (Network Kanji Filter)
======================================================================

* Copyright (c) 2012-2024 SATOH Fumiyasu @ OSSTech Corp., Japan
* Copyright (c) 2005 Matsumoto, Tadashi (original author)
* License: BSD
* Development home: <https://github.com/fumiyas/python-nkf>
* Author's home: <https://fumiyas.github.io/>

How to Install
----------------------------------------------------------------------

Install from PyPI:

```console
$ sudo pip install nkf
```

Install from source tree:

```console
$ make
$ sudo make install
```

Run tests:

```console
$ make test
```

Usage
----------------------------------------------------------------------

```python
## flag is same as the flags of nkf itself
import nkf
output = nkf.nkf(flag, input)

## For example, to convert from euc-jp to utf-8
output = nkf.nkf('-Ew', 'some euc-jp string')

## Options can also be passed as a list or tuple
output = nkf.nkf(['-E', '-w'], 'some euc-jp string')
output = nkf.nkf(['--ic=euc-jp', '--oc=utf-8n'], 'some euc-jp string')

## Guess character encoding
input_encoding = nkf.guess('some string')

## Guess character encoding and newline type
encoding, newline = nkf.guess_detail('some string')
```

`guess()` function guesses an input string encoding and returns
one of next strings:

* `BINARY`
* `ASCII`
* `Shift_JIS`
* `CP932`
* `EUC-JP`
* `EUCJP-MS`
* `CP51932`
* `ISO-2022-JP`
* `CP50221`
* `CP50220`
* `UTF-8`
* `UTF-16`
* `UTF-32`

`guess_detail()` function returns a tuple of `(encoding, newline)`.
`encoding` is same as `guess()`, and `newline` is one of:

* `None` (no newline detected)
* `LF`
* `CR`
* `CRLF`
* `MIXED`
