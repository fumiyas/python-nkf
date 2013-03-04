#!/usr/bin/env python
## -*- coding:utf-8 -*-
##
## Python 2.x: Japanese codecs by NKF
## Copyright (c) 2007-2009 SATOH Fumiyasu @ OSS Technology, Inc.
##               <http://www.osstech.co.jp>
##
## License: GNU General Public License version 2 or later
## Date: 2009-05-20, since 2007-01-12

## References:
##      http://gihyo.jp/dev/serial/01/pythonhacks/0004
##      http://www.egenix.com/www2002/python/unicode-proposal.txt
##      encodings/*.py
##      JapaneseCodecs-1.4.11 (for Python 2.4)
##
## FIXME: All of *_IncrementalEncoder and *_incrementalDecoder classes
##        don't use NKF codec. I don't know how to implement and test it. :-X
##
## FIXME: All of *_StreamReader.read*(size) ignore the size in some cases.

__version__ = '0.3.0'

import nkf
import codecs
import _codecs_iso2022, _codecs_jp
import encodings
import sys
import re

python_version = float(re.sub(r'^(?s)(\d+\.\d+).*$', '\\1', sys.version))

## ======================================================================

if python_version >= 2.5:
    regentry_by_encoding = {}
    def nkf_codec_search_func(encoding):
        if regentry_by_encoding.has_key(encoding):
            return regentry_by_encoding[encoding]
        else:
            return None
    codecs.register(nkf_codec_search_func)
else:
    import imp

## ======================================================================

## ISO-2022-JP codecs by NKF
## ----------------------------------------------------------------------

import encodings.iso2022_jp_ext as iso2022_jp

US_ASCII          = 1
JISX0201_ROMAN    = 2
JISX0201_KATAKANA = 3
JISX0208_1978     = 4
JISX0208_1983     = 5
JISX0212_1990     = 6

CHARSETS = {
    "\033(B": US_ASCII,
    "\033(J": JISX0201_ROMAN,
    "\033(I": JISX0201_KATAKANA,
    "\033$@": JISX0208_1978,
    "\033$B": JISX0208_1983,
    "\033$(D": JISX0212_1990,
}

DESIGNATIONS = {}
for k, v in CHARSETS.items():
    DESIGNATIONS[v] = k

re_designations = re.compile("\033(\\([BIJ]|\\$[@B]|\\$\\(D)")

iso2022_jp_Codec = _codecs_iso2022.getcodec('iso2022_jp')

class iso2022_jp_nkf_Codec(codecs.Codec):
    def encode(self, input, errors='strict'):
        ret = input.encode('utf8', 'replace')
        ret = nkf.nkf('-m0 -x -W -j', ret)
        return (ret, len(input))

    def decode(self, input, errors='strict'):
        ret = nkf.nkf('-m0 -x -J -w', input)
        ret = unicode(ret, 'utf8', 'replace')
        return ret, len(input)

if python_version >= 2.5:
    class iso2022_jp_nkf_IncrementalEncoder(iso2022_jp.IncrementalEncoder):
        codec = iso2022_jp_Codec

    class iso2022_jp_nkf_IncrementalDecoder(iso2022_jp.IncrementalDecoder):
        codec = iso2022_jp_Codec

class iso2022_jp_nkf_StreamReader(iso2022_jp_nkf_Codec, codecs.StreamReader):
    def __init__(self, stream, errors='strict'):
        codecs.StreamReader.__init__(self, stream, errors)
        self.data = ''
        self.charset = US_ASCII
    def _read(self, func, size):
        if size == 0:
            return u''
        if size is None or size < 0:
            data = self.data + func()
        else:
            data = self.data + func(max(size, 8) - len(self.data))
        self.data = ''
        if self.charset != US_ASCII:
            data = DESIGNATIONS[self.charset] + data
        pos = data.rfind("\033")
        if pos >= 0 and not re_designations.match(data, pos):
            # data ends on the way of an escape sequence
            data, self.data = data[:pos], data[pos:]
            pos = data.rfind("\033")
        if pos >= 0:
            match = re_designations.match(data, pos)
            if not match:
                raise UnicodeError, "unknown designation"
            self.charset = CHARSETS[match.group()]
            if self.charset in [JISX0208_1978, JISX0208_1983, JISX0212_1990] and \
               (len(data) - match.end()) % 2 == 1:
                data, self.data = data[:-1], data[-1]
            if self.charset != US_ASCII:
                data = data + DESIGNATIONS[US_ASCII]
        return self.decode(data, self.errors)[0]
    def read(self, size=-1):
        return self._read(self.stream.read, size)
    def readline(self, size=-1):
        return self._read(self.stream.readline, size)
    def readlines(self, size=-1):
        data = self._read(self.stream.read, size)
        buffer = []
        end = 0
        while 1:
            pos = data.find(u'\n', end)
            if pos < 0:
                if end < len(data):
                    buffer.append(data[end:])
                break
            buffer.append(data[end:pos+1])
            end = pos+1
        return buffer
    def reset(self):
        self.data = ''

class iso2022_jp_nkf_StreamWriter(iso2022_jp_nkf_Codec, codecs.StreamWriter):
    codec = iso2022_jp_Codec

if python_version >= 2.5:
    def iso2022_jp_nkf_getregentry():
        return codecs.CodecInfo(
            name =                  'iso2022_jp_nkf',
            encode =                iso2022_jp_nkf_Codec().encode,
            decode =                iso2022_jp_nkf_Codec().decode,
            incrementalencoder =    iso2022_jp_nkf_IncrementalEncoder,
            incrementaldecoder =    iso2022_jp_nkf_IncrementalDecoder,
            streamreader =          iso2022_jp_nkf_StreamReader,
            streamwriter =          iso2022_jp_nkf_StreamWriter,
        )
    regentry_by_encoding['iso2022_jp_nkf'] = iso2022_jp_nkf_getregentry()
else:
    m = imp.new_module('iso2022_jp_nkf')
    m.getregentry = lambda : (
        iso2022_jp_nkf_Codec().encode,
        iso2022_jp_nkf_Codec().decode,
        iso2022_jp_nkf_StreamReader,
        iso2022_jp_nkf_StreamWriter,
    )
    sys.modules['iso2022_jp_nkf'] = m

## EUC-JP codecs by NKF
## ----------------------------------------------------------------------

import encodings.euc_jp as euc_jp

euc_jp_Codec = _codecs_jp.getcodec('euc_jp')

class euc_jp_nkf_Codec(codecs.Codec):
    def encode(self, input, errors='strict'):
        ret = input.encode('utf8', 'replace')
        ret = nkf.nkf('-m0 -x -W -e', ret)
        return (ret, len(input))

    def decode(self, input, errors='strict'):
        ret = nkf.nkf('-m0 -x -E -w', input)
        ret = unicode(ret, 'utf8', 'replace')
        return ret, len(input)

if python_version >= 2.5:
    class euc_jp_nkf_IncrementalEncoder(euc_jp.IncrementalEncoder):
        codec = euc_jp_Codec

    class euc_jp_nkf_IncrementalDecoder(euc_jp.IncrementalDecoder):
        codec = euc_jp_Codec

class euc_jp_nkf_StreamReader(euc_jp_nkf_Codec, codecs.StreamReader):
    def __init__(self, stream, errors='strict'):
        codecs.StreamReader.__init__(self, stream, errors)
        self.data = ''
    def _read(self, func, size):
        if size == 0:
            return u''
        if size is None or size < 0:
            data = self.data + func()
            self.data = ''
        else:
            data = self.data + func(max(size, 2) - len(self.data))
            size = len(data)
            p = 0
            while p < size:
                if data[p] < "\x80":
                    p = p + 1
                elif p + 2 <= size:
                    p = p + 2
                else:
                    break
            data, self.data = data[:p], data[p:]
        return self.decode(data, self.errors)[0]
    def read(self, size=-1):
        return self._read(self.stream.read, size)
    def readline(self, size=-1):
        return self._read(self.stream.readline, size)
    def readlines(self, size=-1):
        data = self._read(self.stream.read, size)
        buffer = []
        end = 0
        while 1:
            pos = data.find(u'\n', end)
            if pos < 0:
                if end < len(data):
                    buffer.append(data[end:])
                break
            buffer.append(data[end:pos+1])
            end = pos+1
        return buffer
    def reset(self):
        self.data = ''

class euc_jp_nkf_StreamWriter(euc_jp_nkf_Codec, codecs.StreamWriter):
    codec = euc_jp_Codec

if python_version >= 2.5:
    def euc_jp_nkf_getregentry():
        return codecs.CodecInfo(
            name =                  'euc_jp_nkf',
            encode =                euc_jp_nkf_Codec().encode,
            decode =                euc_jp_nkf_Codec().decode,
            incrementalencoder =    euc_jp_nkf_IncrementalEncoder,
            incrementaldecoder =    euc_jp_nkf_IncrementalDecoder,
            streamreader =          euc_jp_nkf_StreamReader,
            streamwriter =          euc_jp_nkf_StreamWriter,
        )
    regentry_by_encoding['euc_jp_nkf'] = euc_jp_nkf_getregentry()
else:
    m = imp.new_module('euc_jp_nkf')
    m.getregentry = lambda : (
        euc_jp_nkf_Codec().encode,
        euc_jp_nkf_Codec().decode,
        euc_jp_nkf_StreamReader,
        euc_jp_nkf_StreamWriter,
    )
    sys.modules['euc_jp_nkf'] = m

## Shift_JIS codecs by NKF
## ----------------------------------------------------------------------

import encodings.shift_jis as shift_jis

shift_jis_Codec = _codecs_jp.getcodec('shift_jis')

class shift_jis_nkf_Codec(codecs.Codec):
    def encode(self, input, errors='strict'):
        ret = input.encode('utf8', 'replace')
        ret = nkf.nkf('-m0 -x -W -s', ret)
        return (ret, len(input))

    def decode(self, input, errors='strict'):
        ret = nkf.nkf('-m0 -x -S -w', input)
        ret = unicode(ret, 'utf8', 'replace')
        return ret, len(input)

if python_version >= 2.5:
    class shift_jis_nkf_IncrementalEncoder(shift_jis.IncrementalEncoder):
        codec = shift_jis_Codec

    class shift_jis_nkf_IncrementalDecoder(shift_jis.IncrementalDecoder):
        codec = shift_jis_Codec

class shift_jis_nkf_StreamReader(shift_jis_nkf_Codec, codecs.StreamReader):
    def __init__(self, stream, errors='strict'):
        codecs.StreamReader.__init__(self, stream, errors)
        self.data = ''
    def _read(self, func, size):
        if size == 0:
            return u''
        if size is None or size < 0:
            data = self.data + func()
            self.data = ''
        else:
            data = self.data + func(max(size, 2) - len(self.data))
            size = len(data)
            p = 0
            while p < size:
                if data[p] < "\x80" or data[p] >= "\xa1" and data[p] <= "\xdf":
                    p = p + 1
                elif p + 2 <= size:
                    p = p + 2
                else:
                    break
            data, self.data = data[:p], data[p:]
        return self.decode(data, self.errors)[0]
    def read(self, size=-1):
        return self._read(self.stream.read, size)
    def readline(self, size=-1):
        return self._read(self.stream.readline, size)
    def readlines(self, size=-1):
        data = self._read(self.stream.read, size)
        buffer = []
        end = 0
        while 1:
            pos = data.find(u'\n', end)
            if pos < 0:
                if end < len(data):
                    buffer.append(data[end:])
                break
            buffer.append(data[end:pos+1])
            end = pos+1
        return buffer
    def reset(self):
        self.data = ''

class shift_jis_nkf_StreamWriter(shift_jis_nkf_Codec, codecs.StreamWriter):
    codec = shift_jis_Codec

if python_version >= 2.5:
    def shift_jis_nkf_getregentry():
        return codecs.CodecInfo(
            name =                  'shift_jis_nkf',
            encode =                shift_jis_nkf_Codec().encode,
            decode =                shift_jis_nkf_Codec().decode,
            incrementalencoder =    shift_jis_nkf_IncrementalEncoder,
            incrementaldecoder =    shift_jis_nkf_IncrementalDecoder,
            streamreader =          shift_jis_nkf_StreamReader,
            streamwriter =          shift_jis_nkf_StreamWriter,
        )
    regentry_by_encoding['shift_jis_nkf'] = shift_jis_nkf_getregentry()
else:
    m = imp.new_module('shift_jis_nkf')
    m.getregentry = lambda : (
        shift_jis_nkf_Codec().encode,
        shift_jis_nkf_Codec().decode,
        shift_jis_nkf_StreamReader,
        shift_jis_nkf_StreamWriter,
    )
    sys.modules['shift_jis_nkf'] = m

## ----------------------------------------------------------------------

## Override Japanese codecs by *_nkf

def overrideEncodings():
    if python_version >= 2.5:
        encodings._cache['iso2022_jp'] = iso2022_jp_nkf_getregentry()
        encodings._cache['euc_jp'] = euc_jp_nkf_getregentry()
        encodings._cache['shift_jis'] = shift_jis_nkf_getregentry()

        ## 'iso2022_jp' and 'iso2022-jp' are not in aliases
        encodings._cache['iso2022-jp'] = iso2022_jp_nkf_getregentry()
        ## 'euc_jp' and 'euc-jp' are not in aliases
        encodings._cache['euc-jp'] = euc_jp_nkf_getregentry()
        ## 'euc_jp' and 'euc-jp' are not in aliases
        encodings._cache['shift-jis'] = shift_jis_nkf_getregentry()

        ## Override aliases for Japanese codecs by *_nkf
        for alias in encodings.aliases.aliases:
            encoder = None
            if re.match(r'^iso_?2022_?jp(_?(1|ext))?$', alias):
                encoder = iso2022_jp_nkf_getregentry()
            elif re.match(r'^(euc_?jp|u_?jis)$', alias):
                encoder = euc_jp_nkf_getregentry()
            elif re.match(r'^s(hift)?_?jis$', alias):
                encoder = shift_jis_nkf_getregentry()
            if encoder:
                encodings._cache[alias] = encoder
                alias2 = re.sub('_', '-', alias)
                if alias2 != alias:
                    encodings._cache[alias2] = encoder
    else:
        encodings.aliases.aliases.update({
            'iso2022_jp':	'iso2022_jp_nkf',
            'euc_jp':		'euc_jp_nkf',
            'shift_jis':	'shift_jis_nkf',
        })

        encodings.aliases.aliases.update({'iso2022jp': 'iso2022_jp_nkf'})

        ## Override aliases for Japanese codecs by *_nkf
        for alias in encodings.aliases.aliases:
            encoding = None
            if re.match(r'^iso_?2022_?jp(_?(1|ext))?$', alias):
                encoding = 'iso2022_jp_nkf'
            elif re.match(r'^(euc_?jp|u_?jis)$', alias):
                encoding = 'euc_jp_nkf'
            elif re.match(r'^s(hift)?_?jis$', alias):
                encoding = 'shift_jis_nkf'
            if encoding:
                encodings.aliases.aliases.update({alias: encoding})

        encodings._cache.clear()

## Test
## ======================================================================

if __name__ == '__main__':
    import StringIO

    unicoded =  u'abc ABC'
    unicoded += u' 阿異雨あいう'
    unicoded += u' アイウｱｲｳ'
    unicoded += u' ①ⅰⅠ㈱〜'
    unicoded += u' =?ISO-2022-JP?B?GyRCJCIbKEI=?='

    encoding_list = [
        'iso2022_jp',
        'iso2022-jp',
        'iso2022jp',
        'iso_2022_jp',
        'iso-2022-jp',
        'euc_jp',
        'euc-jp',
        'eucjp',
        'ujis',
        'u_jis',
        'u-jis',
        'shift_jis',
        'shift-jis',
        'shiftjis',
        'sjis',
        's-jis',
    ]

    overrideEncodings()

    for encoding in encoding_list:
        print '%s: encode(), decode()' % encoding
        encoded = unicoded.encode(encoding)
        assert encoded.decode(encoding) == unicoded

        text = (encoded + "\n") * 17
        text_unicoded = text.decode(encoding)
        encoder, decoder, reader, writer = codecs.lookup(encoding)
        for func_name in ['read', 'readline', 'readlines']:
            for size in [None, -1] + range(1, 33) + [64, 128, 256, 512, 1024]:
                print '%s: %s(%s)' % (encoding, func_name, str(size))

                istream = reader(StringIO.StringIO(text))
                ostream = writer(StringIO.StringIO())
                func = getattr(istream, func_name)

                while 1:
                    text_chunk = func(size)
                    if not text_chunk:
                        break
                    ## FIXME: Fix *_StreamReader classes
                    #if size != None and size > 0:
                    #    assert len(text_chunk) <= size
                    if func_name == 'readlines':
                        ostream.writelines(text_chunk)
                    else:
                        ostream.write(text_chunk)
                assert ostream.getvalue().decode(encoding) == text_unicoded

        ## FIXME: Add test for *_Incremental* classes

