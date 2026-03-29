"""Tests for nkf.NKF class and codec integration."""

import codecs
import io

import pytest

import nkf
from nkf import NKF


# ======================================================================
# NKF class construction
# ======================================================================


class TestNKFConstruction:
    def test_basic_construction(self):
        n = NKF("-j")
        assert n.options == ("-j",)
        assert n.encoding is None

    def test_multiple_options(self):
        n = NKF("-m0", "-x", "-j")
        assert n.options == ("-m0", "-x", "-j")

    def test_no_options(self):
        n = NKF()
        assert n.options == ()
        assert n.encoding is None

    def test_encoding_keyword(self):
        n = NKF("-m0", encoding="iso-2022-jp")
        assert n.encoding == "iso-2022-jp"

    def test_encoding_aliases(self):
        """Various encoding name formats should be accepted."""
        for name in ["iso-2022-jp", "ISO-2022-JP", "iso2022_jp", "ISO2022JP"]:
            n = NKF(encoding=name)
            assert n.encoding == name

    def test_all_supported_encodings(self):
        """All documented encodings should be constructible."""
        for name in [
            "iso-2022-jp", "euc-jp", "shift_jis", "cp932",
            "utf-8", "utf-16", "utf-16be", "utf-16le",
            "utf-32", "utf-32be", "utf-32le",
        ]:
            NKF(encoding=name)

    def test_unsupported_encoding(self):
        with pytest.raises(ValueError, match="unsupported encoding"):
            NKF(encoding="nonexistent")

    def test_invalid_option_type(self):
        with pytest.raises(TypeError, match="options must be strings"):
            NKF(42)

    def test_invalid_encoding_type(self):
        with pytest.raises(TypeError, match="encoding must be a string"):
            NKF(encoding=42)

    def test_unexpected_keyword(self):
        with pytest.raises(TypeError, match="unexpected keyword"):
            NKF(foo="bar")


# ======================================================================
# NKF.convert()
# ======================================================================


class TestNKFConvert:
    def test_jis_output(self):
        n = NKF("-j")
        result = n.convert("テスト".encode("utf-8"))
        assert result == b"\x1b$B%F%9%H\x1b(B"

    def test_eucjp_output(self):
        n = NKF("-e")
        result = n.convert("テスト".encode("utf-8"))
        assert result == b"\xa5\xc6\xa5\xb9\xa5\xc8"

    def test_sjis_output(self):
        n = NKF("-s")
        result = n.convert("テスト".encode("utf-8"))
        assert result == b"\x83e\x83X\x83g"

    def test_convert_without_encoding(self):
        """convert() works without encoding parameter."""
        n = NKF("-w")
        jis = b"\x1b$B%F%9%H\x1b(B"
        result = n.convert(jis)
        assert result == "テスト".encode("utf-8")

    def test_convert_with_options(self):
        """Multiple stored options are applied."""
        n = NKF("-m0", "-x", "-j")
        result = n.convert("テスト".encode("utf-8"))
        assert result == b"\x1b$B%F%9%H\x1b(B"

    def test_convert_reusable(self):
        """Context is reusable across calls."""
        n = NKF("-j")
        r1 = n.convert("テスト".encode("utf-8"))
        r2 = n.convert("テスト".encode("utf-8"))
        assert r1 == r2

    def test_convert_empty(self):
        n = NKF("-j")
        result = n.convert(b"")
        assert result == b""


# ======================================================================
# NKF.encode() / NKF.decode()
# ======================================================================


class TestNKFEncodeDecode:
    @pytest.fixture(
        params=[
            ("iso-2022-jp", "テスト", b"\x1b$B%F%9%H\x1b(B"),
            ("euc-jp", "テスト", b"\xa5\xc6\xa5\xb9\xa5\xc8"),
            ("shift_jis", "テスト", b"\x83e\x83X\x83g"),
        ],
        ids=["jis", "eucjp", "sjis"],
    )
    def enc_data(self, request):
        return request.param

    def test_encode(self, enc_data):
        enc_name, text, expected = enc_data
        n = NKF("-m0", "-x", encoding=enc_name)
        result, consumed = n.encode(text)
        assert result == expected
        assert consumed == len(text)

    def test_decode(self, enc_data):
        enc_name, text, encoded = enc_data
        n = NKF("-m0", "-x", encoding=enc_name)
        result, consumed = n.decode(encoded)
        assert result == text
        assert consumed == len(encoded)

    def test_roundtrip(self, enc_data):
        enc_name, text, _ = enc_data
        n = NKF("-m0", "-x", encoding=enc_name)
        encoded, _ = n.encode(text)
        decoded, _ = n.decode(encoded)
        assert decoded == text

    def test_encode_requires_encoding(self):
        n = NKF("-j")
        with pytest.raises(TypeError, match="requires 'encoding'"):
            n.encode("test")

    def test_decode_requires_encoding(self):
        n = NKF("-j")
        with pytest.raises(TypeError, match="requires 'encoding'"):
            n.decode(b"test")

    def test_encode_empty(self):
        n = NKF(encoding="utf-8")
        result, consumed = n.encode("")
        assert result == b""
        assert consumed == 0

    def test_decode_empty(self):
        n = NKF(encoding="utf-8")
        result, consumed = n.decode(b"")
        assert result == ""
        assert consumed == 0

    def test_encode_ascii(self):
        n = NKF("-m0", "-x", encoding="iso-2022-jp")
        result, consumed = n.encode("hello")
        assert result == b"hello"
        assert consumed == 5

    @pytest.mark.parametrize(
        "enc_name",
        ["utf-16", "utf-16be", "utf-16le", "utf-32", "utf-32be", "utf-32le"],
    )
    def test_unicode_roundtrip(self, enc_name):
        n = NKF("-m0", "-x", encoding=enc_name)
        text = "テスト日本語ABC"
        encoded, _ = n.encode(text)
        decoded, _ = n.decode(encoded)
        assert decoded == text

    def test_decode_memoryview(self):
        n = NKF("-m0", "-x", encoding="euc-jp")
        data = b"\xa5\xc6\xa5\xb9\xa5\xc8"
        result, _ = n.decode(memoryview(data))
        assert result == "テスト"

    def test_decode_bytearray(self):
        n = NKF("-m0", "-x", encoding="euc-jp")
        data = bytearray(b"\xa5\xc6\xa5\xb9\xa5\xc8")
        result, _ = n.decode(data)
        assert result == "テスト"


# ======================================================================
# NKF.guess() / NKF.guess_detail()
# ======================================================================


class TestNKFGuess:
    def test_guess_jis(self):
        n = NKF()
        assert n.guess(b"\x1b$B%F%9%H\x1b(B") == "ISO-2022-JP"

    def test_guess_eucjp(self):
        n = NKF()
        assert n.guess(b"\xa5\xc6\xa5\xb9\xa5\xc8") == "EUC-JP"

    def test_guess_sjis(self):
        n = NKF()
        assert n.guess(b"\x83e\x83X\x83g") == "Shift_JIS"

    def test_guess_utf8(self):
        n = NKF()
        assert n.guess("テスト".encode("utf-8")) == "UTF-8"

    def test_guess_detail_with_lf(self):
        n = NKF()
        enc, eol = n.guess_detail("テスト\n".encode("utf-8"))
        assert enc == "UTF-8"
        assert eol == "LF"

    def test_guess_detail_no_eol(self):
        n = NKF()
        enc, eol = n.guess_detail("テスト".encode("utf-8"))
        assert enc == "UTF-8"
        assert eol is None


# ======================================================================
# NKF.codec_info()
# ======================================================================


class TestNKFCodecInfo:
    def test_codec_info_type(self):
        n = NKF("-m0", "-x", encoding="iso-2022-jp")
        ci = n.codec_info()
        assert isinstance(ci, codecs.CodecInfo)

    def test_codec_info_name(self):
        n = NKF("-m0", "-x", encoding="iso-2022-jp")
        ci = n.codec_info()
        assert ci.name == "iso-2022-jp"

    def test_codec_info_encode_decode(self):
        n = NKF("-m0", "-x", encoding="euc-jp")
        ci = n.codec_info()
        enc, _ = ci.encode("テスト")
        dec, _ = ci.decode(enc)
        assert dec == "テスト"

    def test_codec_info_requires_encoding(self):
        n = NKF("-j")
        with pytest.raises(TypeError, match="requires 'encoding'"):
            n.codec_info()


# ======================================================================
# IncrementalEncoder / IncrementalDecoder
# ======================================================================


class TestIncrementalCodec:
    def test_incremental_encoder_buffering(self):
        n = NKF("-m0", "-x", encoding="iso-2022-jp")
        ci = n.codec_info()
        enc = ci.incrementalencoder()

        # Non-final calls buffer input
        assert enc.encode("テ") == b""
        assert enc.encode("ス") == b""

        # Final call flushes
        result = enc.encode("ト", final=True)
        assert result == b"\x1b$B%F%9%H\x1b(B"

    def test_incremental_encoder_reset(self):
        n = NKF("-m0", "-x", encoding="iso-2022-jp")
        ci = n.codec_info()
        enc = ci.incrementalencoder()

        enc.encode("テスト")
        enc.reset()
        result = enc.encode("A", final=True)
        assert result == b"A"

    def test_incremental_decoder_buffering(self):
        n = NKF("-m0", "-x", encoding="iso-2022-jp")
        ci = n.codec_info()
        dec = ci.incrementaldecoder()

        # Non-final calls buffer input
        jis = b"\x1b$B%F%9%H\x1b(B"
        assert dec.decode(jis[:4]) == ""
        assert dec.decode(jis[4:8]) == ""

        # Final call flushes
        result = dec.decode(jis[8:], final=True)
        assert result == "テスト"

    def test_incremental_decoder_reset(self):
        n = NKF("-m0", "-x", encoding="iso-2022-jp")
        ci = n.codec_info()
        dec = ci.incrementaldecoder()

        dec.decode(b"\x1b$B%F")
        dec.reset()
        result = dec.decode(b"hello", final=True)
        assert result == "hello"


# ======================================================================
# StreamReader / StreamWriter
# ======================================================================


class TestStreamCodec:
    def test_stream_writer(self):
        n = NKF("-m0", "-x", encoding="euc-jp")
        ci = n.codec_info()

        buf = io.BytesIO()
        writer = ci.streamwriter(buf)
        writer.write("テスト")
        assert buf.getvalue() == b"\xa5\xc6\xa5\xb9\xa5\xc8"

    def test_stream_reader(self):
        n = NKF("-m0", "-x", encoding="euc-jp")
        ci = n.codec_info()

        buf = io.BytesIO(b"\xa5\xc6\xa5\xb9\xa5\xc8")
        reader = ci.streamreader(buf)
        result = reader.read()
        assert result == "テスト"

    def test_stream_writer_jis(self):
        n = NKF("-m0", "-x", encoding="iso-2022-jp")
        ci = n.codec_info()

        buf = io.BytesIO()
        writer = ci.streamwriter(buf)
        writer.write("日本語")
        assert len(buf.getvalue()) > 0

        # Verify round-trip
        buf2 = io.BytesIO(buf.getvalue())
        reader = ci.streamreader(buf2)
        assert reader.read() == "日本語"


# ======================================================================
# codecs.py integration
# ======================================================================


class TestCodecsRegistration:
    def test_iso2022_jp_nkf_lookup(self):
        import nkf.codecs

        ci = codecs.lookup("iso2022_jp_nkf")
        assert ci is not None
        enc, _ = ci.encode("テスト")
        dec, _ = ci.decode(enc)
        assert dec == "テスト"

    def test_euc_jp_nkf_lookup(self):
        import nkf.codecs

        ci = codecs.lookup("euc_jp_nkf")
        assert ci is not None
        enc, _ = ci.encode("テスト")
        dec, _ = ci.decode(enc)
        assert dec == "テスト"

    def test_shift_jis_nkf_lookup(self):
        import nkf.codecs

        ci = codecs.lookup("shift_jis_nkf")
        assert ci is not None
        enc, _ = ci.encode("テスト")
        dec, _ = ci.decode(enc)
        assert dec == "テスト"
