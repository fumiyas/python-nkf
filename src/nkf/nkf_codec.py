## -*- coding: utf-8 -*- vim:shiftwidth=4:expandtab:
"""
NKF codec helper classes for codecs.CodecInfo integration.

Provides IncrementalEncoder, IncrementalDecoder, StreamReader,
StreamWriter bound to an NKF instance, and a factory function
make_codec_info() used by NKF.codec_info().
"""

import codecs


class NKFIncrementalEncoder(codecs.IncrementalEncoder):
    """Incremental encoder that buffers input until final=True."""

    def __init__(self, nkf_instance, errors="strict"):
        super().__init__(errors)
        self._nkf = nkf_instance
        self._buffer = ""

    def encode(self, input, final=False):
        self._buffer += input
        if final:
            result = self._nkf.encode(self._buffer, self.errors)[0]
            self._buffer = ""
            return result
        return b""

    def reset(self):
        super().reset()
        self._buffer = ""

    def getstate(self):
        return len(self._buffer)

    def setstate(self, state):
        # Cannot restore buffered text from an integer; just reset
        self._buffer = ""


class NKFIncrementalDecoder(codecs.IncrementalDecoder):
    """Incremental decoder that buffers input until final=True."""

    def __init__(self, nkf_instance, errors="strict"):
        super().__init__(errors)
        self._nkf = nkf_instance
        self._buffer = b""

    def decode(self, input, final=False):
        self._buffer += bytes(input)
        if final:
            result = self._nkf.decode(self._buffer, self.errors)[0]
            self._buffer = b""
            return result
        return ""

    def reset(self):
        super().reset()
        self._buffer = b""

    def getstate(self):
        return (self._buffer, 0)

    def setstate(self, state):
        self._buffer = state[0] if state[0] else b""


class NKFStreamWriter(codecs.StreamWriter):
    """Stream writer using NKF for encoding."""

    def __init__(self, nkf_instance, stream, errors="strict"):
        self._nkf = nkf_instance
        super().__init__(stream, errors)

    def encode(self, input, errors="strict"):
        return self._nkf.encode(input, errors)


class NKFStreamReader(codecs.StreamReader):
    """Stream reader using NKF for decoding.

    NKF is a whole-buffer converter, so we read all available data
    from the underlying stream, decode it, and buffer the result.
    Subsequent read/readline calls return from the decoded buffer.
    """

    def __init__(self, nkf_instance, stream, errors="strict"):
        self._nkf = nkf_instance
        self._charbuffer = ""
        super().__init__(stream, errors)

    def decode(self, input, errors="strict"):
        return self._nkf.decode(input, errors)

    def _ensure_decoded(self):
        if not self._charbuffer:
            data = self.stream.read()
            if data:
                self._charbuffer = self.decode(data, self.errors)[0]

    def read(self, size=-1, chars=-1, firstline=False):
        self._ensure_decoded()
        if size is None or size < 0:
            result = self._charbuffer
            self._charbuffer = ""
            return result
        result = self._charbuffer[:size]
        self._charbuffer = self._charbuffer[size:]
        return result

    def readline(self, size=None, keepends=True):
        self._ensure_decoded()
        if size is None:
            size = -1
        pos = self._charbuffer.find("\n")
        if pos >= 0:
            end = pos + 1
            line = self._charbuffer[:end]
            self._charbuffer = self._charbuffer[end:]
            if not keepends:
                line = line.rstrip("\n")
            return line
        result = self._charbuffer
        self._charbuffer = ""
        return result

    def readlines(self, sizehint=None, keepends=True):
        self._ensure_decoded()
        text = self._charbuffer
        self._charbuffer = ""
        return text.splitlines(keepends)

    def reset(self):
        self._charbuffer = ""
        super().reset()


def make_codec_info(nkf_instance):
    """Create a codecs.CodecInfo bound to an NKF instance.

    Called from NKF.codec_info() (C level).
    """
    nkf_ref = nkf_instance

    class BoundIncrementalEncoder(NKFIncrementalEncoder):
        def __init__(self, errors="strict"):
            super().__init__(nkf_ref, errors)

    class BoundIncrementalDecoder(NKFIncrementalDecoder):
        def __init__(self, errors="strict"):
            super().__init__(nkf_ref, errors)

    class BoundStreamReader(NKFStreamReader):
        def __init__(self, stream, errors="strict"):
            super().__init__(nkf_ref, stream, errors)

    class BoundStreamWriter(NKFStreamWriter):
        def __init__(self, stream, errors="strict"):
            super().__init__(nkf_ref, stream, errors)

    return codecs.CodecInfo(
        name=nkf_instance.encoding,
        encode=nkf_instance.encode,
        decode=nkf_instance.decode,
        incrementalencoder=BoundIncrementalEncoder,
        incrementaldecoder=BoundIncrementalDecoder,
        streamreader=BoundStreamReader,
        streamwriter=BoundStreamWriter,
    )
