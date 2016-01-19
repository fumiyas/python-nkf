Python Interface to NKF
======================================================================

  * Copyright (c) 2012-2016 SATOH Fumiyasu @ OSS Technology Corp., Japan
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

Usage
----------------------------------------------------------------------

```python
## flag is same as the flags of nkf itself
import nkf
output = nkf.nkf(flag, input)

## For example, to convert from euc-jp to utf-8
output = nkf.nkf('-Ew', 'some euc-jp string')

## Guess character encoding
input_encoding = nkf.guess('some string')
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

