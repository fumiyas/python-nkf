#!/usr/bin/env python3
## -*- coding:utf-8 -*-
##
## Python: Japanese codecs by NKF
## Copyright (c) 2007-2024 SATOH Fumiyasu @ OSSTech Corp., Japan
##               <https://www.osstech.co.jp/>
##
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##
## 1. Redistributions of source code must retain the above copyright notice, this
##    list of conditions and the following disclaimer.
## 2. Redistributions in binary form must reproduce the above copyright notice,
##    this list of conditions and the following disclaimer in the documentation
##    and/or other materials provided with the distribution.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
## ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
##
## The views and conclusions contained in the software and documentation are those
## of the authors and should not be interpreted as representing official policies,
## either expressed or implied, of the author(s).

## References:
##      http://gihyo.jp/dev/serial/01/pythonhacks/0004
##      http://www.egenix.com/www2002/python/unicode-proposal.txt
##      encodings/*.py
##      JapaneseCodecs-1.4.11 (for Python 2.4)

import codecs
import encodings
import re

from nkf import NKF

## ======================================================================

_CODECS = {
    "iso2022_jp_nkf": NKF("-m0", "-x", encoding="iso-2022-jp"),
    "euc_jp_nkf": NKF("-m0", "-x", encoding="euc-jp"),
    "shift_jis_nkf": NKF("-m0", "-x", encoding="shift_jis"),
}

regentry_by_encoding = {
    name: nkf_obj.codec_info() for name, nkf_obj in _CODECS.items()
}


def nkf_codec_search_func(encoding):
    return regentry_by_encoding.get(encoding)


codecs.register(nkf_codec_search_func)


## Override Japanese codecs by *_nkf
## ----------------------------------------------------------------------

def override_encodings():
    encodings._cache["iso2022_jp"] = encodings._cache["iso2022-jp"] = (
        regentry_by_encoding["iso2022_jp_nkf"]
    )
    encodings._cache["euc_jp"] = encodings._cache["euc_jp_ms"] = (
        regentry_by_encoding["euc_jp_nkf"]
    )
    encodings._cache["shift_jis"] = regentry_by_encoding["shift_jis_nkf"]

    ## Override aliases for Japanese codecs by *_nkf
    for alias in encodings.aliases.aliases:
        encoder = None
        if re.match(r"^iso_?2022_?jp(_?(1|ext))?$", alias):
            encoder = regentry_by_encoding["iso2022_jp_nkf"]
        elif re.match(r"^(euc_?jp|u_?jis)$", alias):
            encoder = regentry_by_encoding["euc_jp_nkf"]
        elif re.match(r"^s(hift)?_?jis$", alias):
            encoder = regentry_by_encoding["shift_jis_nkf"]
        if encoder:
            encodings._cache[alias] = encoder
            alias2 = alias.replace("_", "-")
            if alias2 != alias:
                encodings._cache[alias2] = encoder

overrideEncodings = override_encodings
