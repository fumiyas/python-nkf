"""Tests for pynkf CLI command."""

import os
import subprocess
import sys
import tempfile

import pytest


def run_pynkf(*args, input=None):
    """Run pynkf and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        [sys.executable, "-m", "nkf", *args],
        input=input,
        capture_output=True,
    )
    return result.stdout, result.stderr, result.returncode


# ======================================================================
# Version and help
# ======================================================================


class TestVersionHelp:
    def test_version(self):
        out, err, rc = run_pynkf("-v")
        assert rc == 0
        assert b"Network Kanji Filter Version" in err
        assert b"pynkf" in err

    def test_version_long(self):
        out, err, rc = run_pynkf("--version")
        assert rc == 0
        assert b"Network Kanji Filter Version" in err

    def test_help(self):
        out, err, rc = run_pynkf("--help")
        assert rc == 0
        assert b"Usage:" in err
        assert b"pynkf" in err

    def test_help_V(self):
        out, err, rc = run_pynkf("-V")
        assert rc == 0
        assert b"Usage:" in err


# ======================================================================
# Encoding conversion
# ======================================================================


class TestConvert:
    def test_utf8_to_jis_stdin(self):
        out, err, rc = run_pynkf("-j", input="テスト".encode("utf-8"))
        assert rc == 0
        assert out == b"\x1b$B%F%9%H\x1b(B"

    def test_utf8_to_eucjp_stdin(self):
        out, err, rc = run_pynkf("-e", input="テスト".encode("utf-8"))
        assert rc == 0
        assert out == b"\xa5\xc6\xa5\xb9\xa5\xc8"

    def test_utf8_to_sjis_stdin(self):
        out, err, rc = run_pynkf("-s", input="テスト".encode("utf-8"))
        assert rc == 0
        assert out == b"\x83e\x83X\x83g"

    def test_jis_to_utf8_stdin(self):
        jis = b"\x1b$B%F%9%H\x1b(B"
        out, err, rc = run_pynkf("-w", input=jis)
        assert rc == 0
        assert out == "テスト".encode("utf-8")

    def test_combined_options(self):
        out, err, rc = run_pynkf("-m0", "-x", "-j", input="テスト".encode("utf-8"))
        assert rc == 0
        assert out == b"\x1b$B%F%9%H\x1b(B"

    def test_ic_oc_options(self):
        out, err, rc = run_pynkf(
            "--ic=UTF-8", "--oc=EUC-JP", input="テスト".encode("utf-8")
        )
        assert rc == 0
        assert out == b"\xa5\xc6\xa5\xb9\xa5\xc8"

    def test_passthrough_no_options(self):
        data = b"hello world"
        out, err, rc = run_pynkf(input=data)
        assert rc == 0
        assert out == data


# ======================================================================
# File processing
# ======================================================================


class TestFileProcessing:
    def test_single_file(self, tmp_path):
        f = tmp_path / "input.txt"
        f.write_bytes("テスト".encode("utf-8"))

        out, err, rc = run_pynkf("-j", str(f))
        assert rc == 0
        assert out == b"\x1b$B%F%9%H\x1b(B"

    def test_multiple_files(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_bytes("あ".encode("utf-8"))
        f2.write_bytes("い".encode("utf-8"))

        out, err, rc = run_pynkf("-e", str(f1), str(f2))
        assert rc == 0
        # EUC-JP: あ=0xa4a2, い=0xa4a4
        assert out == b"\xa4\xa2\xa4\xa4"

    def test_nonexistent_file(self, tmp_path):
        bad = str(tmp_path / "nonexistent.txt")
        out, err, rc = run_pynkf("-j", bad)
        assert rc == 1
        assert b"No such file" in err

    def test_nonexistent_with_valid_file(self, tmp_path):
        good = tmp_path / "good.txt"
        good.write_bytes("テスト".encode("utf-8"))
        bad = str(tmp_path / "bad.txt")

        out, err, rc = run_pynkf("-e", bad, str(good))
        assert rc == 1
        assert b"No such file" in err
        # Good file should still be processed
        assert out == b"\xa5\xc6\xa5\xb9\xa5\xc8"

    def test_stdin_dash(self):
        out, err, rc = run_pynkf("-j", "-", input="テスト".encode("utf-8"))
        assert rc == 0
        assert out == b"\x1b$B%F%9%H\x1b(B"

    def test_end_of_options(self, tmp_path):
        """-- stops option parsing; next args are files."""
        f = tmp_path / "input.txt"
        f.write_bytes("テスト".encode("utf-8"))

        out, err, rc = run_pynkf("-j", "--", str(f))
        assert rc == 0
        assert out == b"\x1b$B%F%9%H\x1b(B"


# ======================================================================
# Guess mode
# ======================================================================


class TestGuessMode:
    def test_guess_stdin(self):
        out, err, rc = run_pynkf("-g", input="テスト".encode("utf-8"))
        assert rc == 0
        assert out.strip() == b"UTF-8"

    def test_guess_g1(self):
        out, err, rc = run_pynkf("-g1", input="テスト".encode("utf-8"))
        assert rc == 0
        assert out.strip() == b"UTF-8"

    def test_guess_g2_detail(self):
        out, err, rc = run_pynkf("-g2", input="テスト\n".encode("utf-8"))
        assert rc == 0
        assert b"UTF-8" in out
        assert b"LF" in out

    def test_guess_long(self):
        out, err, rc = run_pynkf("--guess", input="テスト\n".encode("utf-8"))
        assert rc == 0
        assert b"UTF-8" in out
        assert b"LF" in out

    def test_guess_long_eq_1(self):
        out, err, rc = run_pynkf("--guess=1", input="テスト".encode("utf-8"))
        assert rc == 0
        assert out.strip() == b"UTF-8"

    def test_guess_long_eq_2(self):
        out, err, rc = run_pynkf("--guess=2", input="テスト\n".encode("utf-8"))
        assert rc == 0
        assert b"LF" in out

    def test_guess_jis(self):
        jis = b"\x1b$B%F%9%H\x1b(B"
        out, err, rc = run_pynkf("-g", input=jis)
        assert rc == 0
        assert out.strip() == b"ISO-2022-JP"

    def test_guess_file(self, tmp_path):
        f = tmp_path / "input.txt"
        f.write_bytes("テスト".encode("utf-8"))

        out, err, rc = run_pynkf("-g", str(f))
        assert rc == 0
        assert out.strip() == b"UTF-8"

    def test_guess_multiple_files(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.jis"
        f1.write_bytes("テスト".encode("utf-8"))
        f2.write_bytes(b"\x1b$B%F%9%H\x1b(B")

        out, err, rc = run_pynkf("-g", str(f1), str(f2))
        assert rc == 0
        lines = out.decode().strip().split("\n")
        assert len(lines) == 2
        assert "UTF-8" in lines[0]
        assert f1.name in lines[0]
        assert "ISO-2022-JP" in lines[1]
        assert f2.name in lines[1]


# ======================================================================
# python -m nkf
# ======================================================================


class TestModuleExecution:
    def test_python_m_nkf(self):
        out, err, rc = run_pynkf("-v")
        assert rc == 0
        assert b"pynkf" in err
