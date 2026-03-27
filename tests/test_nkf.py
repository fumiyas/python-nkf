#!/usr/bin/env python3
## -*- coding: utf-8 -*- vim:shiftwidth=4:expandtab:

import binascii

import nkf
import pytest


def _uudecode_line(raw):
    """Decode a single uuencoded line, tolerant of non-zero padding like Perl."""
    nbytes = (raw[0] - 0x20) & 0x3F
    out = bytearray()
    i = 1
    while len(out) < nbytes:
        a = (raw[i] - 0x20) & 0x3F if i < len(raw) else 0
        b = (raw[i + 1] - 0x20) & 0x3F if i + 1 < len(raw) else 0
        c = (raw[i + 2] - 0x20) & 0x3F if i + 2 < len(raw) else 0
        d = (raw[i + 3] - 0x20) & 0x3F if i + 3 < len(raw) else 0
        out.append((a << 2) | (b >> 4))
        out.append(((b & 0xF) << 4) | (c >> 2))
        out.append(((c & 0x3) << 6) | d)
        i += 4
    return bytes(out[:nbytes])


def _uudecode_block(block):
    return b"".join(
        _uudecode_line(line.encode("ascii"))
        for line in block.strip().splitlines()
    )


def _hex(data):
    return bytes.fromhex(data)


def _convert(options, data):
    result = nkf.nkf(options, data)
    assert isinstance(result, bytes)
    return result


def _assert_conversion(options, source, *expected):
    assert _convert(options, source) in expected


EXAMPLES = {
    "jis": _uudecode_block(r'''
M1FER<W0@4W1A9V4@&R1"(3DQ(3%^2R%+?D]3&RA"(%-E8V]N9"!3=&%G92`;
M)$)0)TU:&RA"($AI<F%G86YA(!LD0B0B)"0D)B0H)"HD;R1R)',;*$(*2V%T
M86MA;F$@&R1")2(E)"4F)2@E*B5O)7(E<QLH0B!+:6=O=2`;)$(A)B%G(S`C
/029!)E@G(B=!*$`;*$(*
'''),
    "sjis": _uudecode_block(r'''
M1FER<W0@4W1A9V4@@5B)0(F>ED"6GIAR(%-E8V]N9"!3=&%G92"8I9=Y($AI
M<F%G86YA((*@@J*"I(*F@JB"[8+P@O$*2V%T86MA;F$@@T&#0X-%@T>#28./
>@Y*#DR!+:6=O=2"!18&'@D^"8(._@]:$081@A+X*
'''),
    "euc": _uudecode_block(r'''
M1FER<W0@4W1A9V4@H;FQH;'^RZ'+_L_3(%-E8V]N9"!3=&%G92#0I\W:($AI
M<F%G86YA(*2BI*2DIJ2HI*JD[Z3RI/,*2V%T86MA;F$@I:*EI*6FI:BEJJ7O
>I?*E\R!+:6=O=2"AIJ'GH["CP:;!IMBGHJ?!J,`*
'''),
    "utf8": _uudecode_block(r'''
M[[N_1FER<W0@4W1A9V4@XX"%Z9FBY;^<YK.5YKJ`Z(65(%-E8V]N9"!3=&%G
M92#DN+SI@:4@2&ER86=A;F$@XX&"XX&$XX&&XX&(XX&*XX*/XX*2XX*3"DMA
M=&%K86YA(.."HN."I.."IN."J.."JN.#K^.#LN.#LR!+:6=O=2#C@[OBB)[O
1O)#OO*'.L<^)T)'0K^*5@@H`
'''),
    "utf8N": _uudecode_block(r'''
M1FER<W0@4W1A9V4@XX"%Z9FBY;^<YK.5YKJ`Z(65(%-E8V]N9"!3=&%G92#D
MN+SI@:4@2&ER86=A;F$@XX&"XX&$XX&&XX&(XX&*XX*/XX*2XX*3"DMA=&%K
M86YA(.."HN."I.."IN."J.."JN.#K^.#LN.#LR!+:6=O=2#C@[OBB)[OO)#O
.O*'.L<^)T)'0K^*5@@H`
'''),
    "u16L": _uudecode_block(r'''
M__Y&`&D`<@!S`'0`(`!3`'0`80!G`&4`(``%,&*6W%_5;(!N58$@`%,`90!C
M`&\`;@!D`"``4P!T`&$`9P!E`"``/$YED"``2`!I`'(`80!G`&$`;@!A`"``
M0C!$,$8P2#!*,(\PDC"3,`H`2P!A`'0`80!K`&$`;@!A`"``HC"D,*8PJ#"J
I,.\P\C#S,"``2P!I`&<`;P!U`"``^S`>(A#_(?^Q`\D#$00O!$(E"@``
'''),
    "u16L0": _uudecode_block(r'''
M1@!I`'(`<P!T`"``4P!T`&$`9P!E`"``!3!BEMQ?U6R`;E6!(`!3`&4`8P!O
M`&X`9``@`%,`=`!A`&<`90`@`#Q.99`@`$@`:0!R`&$`9P!A`&X`80`@`$(P
M1#!&,$@P2C"/,)(PDS`*`$L`80!T`&$`:P!A`&X`80`@`*(PI#"F,*@PJC#O
G,/(P\S`@`$L`:0!G`&\`=0`@`/LP'B(0_R'_L0/)`Q$$+P1")0H`
'''),
    "u16B": _uudecode_block(r'''
M_O\`1@!I`'(`<P!T`"``4P!T`&$`9P!E`"`P!99B7]QLU6Z`@54`(`!3`&4`
M8P!O`&X`9``@`%,`=`!A`&<`90`@3CR090`@`$@`:0!R`&$`9P!A`&X`80`@
M,$(P1#!&,$@P2C"/,)(PDP`*`$L`80!T`&$`:P!A`&X`80`@,*(PI#"F,*@P
IJC#O,/(P\P`@`$L`:0!G`&\`=0`@,/LB'O\0_R$#L0/)!!$$+R5"``H`
'''),
    "u16B0": _uudecode_block(r'''
M`$8`:0!R`',`=``@`%,`=`!A`&<`90`@,`668E_<;-5N@(%5`"``4P!E`&,_
M;P!N`&0`(`!3`'0`80!G`&4`($X\D&4`(`!(`&D`<@!A`&<`80!N`&$`(#!"
M,$0P1C!(,$HPCS"2,),`"@!+`&$`=`!A`&L`80!N`&$`(#"B,*0PIC"H,*HP
G[S#R,/,`(`!+`&D`9P!O`'4`(##[(A[_$/\A`[$#R001!"\E0@`*
'''),
    "jis1": _uudecode_block(r'''
M&R1";3%Q<$$L&RA""ALD0F4Z3F\;*$(*&R1"<FT;*$()&R1"/F5.3D]+&RA"
#"0D*
'''),
    "sjis1": _uudecode_block(r'''
8YU#ID)%+"N-9E^T*Z>L)C^.7S)AJ"0D*
'''),
    "euc1": _uudecode_block(r'''
8[;'Q\,&L"N6ZSN\*\NT)ON7.SL_+"0D*
'''),
    "utf1": _uudecode_block(r'''
AZ+J%Z:N/Z8JM"N>VNNFZEPKIM(D)Y+B*Z:"8Y+J8"0D*
'''),
    "amb": _uudecode_block(r'''
MI<*PL:7"L+&EPK"QI<*PL:7"L+&EPK"QI<*PL:7"L+&EPK"QI<*PL:7"L+&E
MPK"QI<*PL:7"L+&EPK"QI<(*I<*PL:7"L+&EPK"QI<*PL:7"L+&EPK"QI<*P
ML:7"L+&EPK"QI<*PL:7"L+&EPK"QI<*PL:7"L+&EPK"QI<(*I<*PL:7"L+&E
MPK"QI<*PL:7"L+&EPK"QI<*PL:7"L+&EPK"QI<*PL:7"L+&EPK"QI<*PL:7"
ML+&EPK"QI<(*I<*PL:7"L+&EPK"QI<*PL:7"L+&EPK"QI<*PL:7"L+&EPK"Q
MI<*PL:7"L+&EPK"QI<*PL:7"L+&EPK"QI<(*I<*PL:7"L+&EPK"QI<*PL:7"
ML+&EPK"QI<*PL:7"L+&EPK"QI<*PL:7"L+&EPK"QI<*PL:7"L+&EPK"QI<(*
'''),
    "amb.euc": _uudecode_block(r'''
M&R1")4(P,25",#$E0C`Q)4(P,25",#$E0C`Q)4(P,25",#$E0C`Q)4(P,25"
M,#$E0C`Q)4(P,25",#$E0C`Q)4(;*$(*&R1")4(P,25",#$E0C`Q)4(P,25"
M,#$E0C`Q)4(P,25",#$E0C`Q)4(P,25",#$E0C`Q)4(P,25",#$E0C`Q)4(;
M*$(*&R1")4(P,25",#$E0C`Q)4(P,25",#$E0C`Q)4(P,25",#$E0C`Q)4(P
M,25",#$E0C`Q)4(P,25",#$E0C`Q)4(;*$(*&R1")4(P,25",#$E0C`Q)4(P
M,25",#$E0C`Q)4(P,25",#$E0C`Q)4(P,25",#$E0C`Q)4(P,25",#$E0C`Q
M)4(;*$(*&R1")4(P,25",#$E0C`Q)4(P,25",#$E0C`Q)4(P,25",#$E0C`Q
>)4(P,25",#$E0C`Q)4(P,25",#$E0C`Q)4(;*$(*
'''),
    "amb.sjis": _uudecode_block(r'''
M&RA))4(P,25",#$E0C`Q)4(P,25",#$E0C`Q)4(P,25",#$E0C`Q)4(P,25"
M,#$E0C`Q)4(P,25",#$E0C`Q)4(;*$(*&RA))4(P,25",#$E0C`Q)4(P,25"
M,#$E0C`Q)4(P,25",#$E0C`Q)4(P,25",#$E0C`Q)4(P,25",#$E0C`Q)4(;
M*$(*&RA))4(P,25",#$E0C`Q)4(P,25",#$E0C`Q)4(P,25",#$E0C`Q)4(P
M,25",#$E0C`Q)4(P,25",#$E0C`Q)4(;*$(*&RA))4(P,25",#$E0C`Q)4(P
M,25",#$E0C`Q)4(P,25",#$E0C`Q)4(P,25",#$E0C`Q)4(P,25",#$E0C`Q
M)4(;*$(*&RA))4(P,25",#$E0C`Q)4(P,25",#$E0C`Q)4(P,25",#$E0C`Q
>)4(P,25",#$E0C`Q)4(P,25",#$E0C`Q)4(;*$(*
'''),
    "cp932": _uudecode_block(r'''
%^D`@_$L`
'''),
    "cp932.ans": _uudecode_block(r'''
%_/$@_.X`
'''),
    "no-cp932inv.ans": _uudecode_block(r'''
%[N\@[NP`
'''),
    "jisx0212_euc": b"\x8f\xa2\xaf\x8f\xed\xe3",
    "jisx0212_jis": b"\x1b\x24\x28\x44\x22\x2f\x6d\x63\x1b\x28\x42",
    "jisx0213_sjis": _uudecode_block(r'''
0@:V(G9ATF)WJIN_W\$#\]```
'''),
    "jisx0213_euc": _uudecode_block(r'''
2HJ^O_<_5S_WTJ/[YCZ&AC_[V
'''),
    "jisx0213_jis2004": _uudecode_block(r'''
;&R0H42(O+WU/54]]="A^>1LD*%`A(7YV&RA"
'''),
    "no_best_fit_chars": _uudecode_block(r'''
;XH"5XHBE[[R-[[^@[[^A[[^B[[^C[[^D[[^E
'''),
}

# Fix upstream uuencode data error in u16B0 (1-byte encoding mistake at offset 44)
EXAMPLES["u16B0"] = EXAMPLES["u16B"][2:]


@pytest.mark.parametrize(
    ("options", "source_key", "expected_key"),
    [
        ("-j", "jis", "jis"),
        ("-s", "jis", "sjis"),
        ("-e", "jis", "euc"),
        ("-w", "jis", "utf8N"),
        ("-j", "sjis", "jis"),
        ("-s", "sjis", "sjis"),
        ("-e", "sjis", "euc"),
        ("-w", "sjis", "utf8N"),
        ("-j", "euc", "jis"),
        ("-s", "euc", "sjis"),
        ("-e", "euc", "euc"),
        ("-w", "euc", "utf8N"),
        ("-j", "utf8N", "jis"),
        ("-s", "utf8N", "sjis"),
        ("-e", "utf8N", "euc"),
        ("-w", "utf8N", "utf8N"),
        ("-w8", "utf8N", "utf8"),
        ("-w80", "utf8N", "utf8N"),
        ("--ic=iso-2022-jp --oc=shift_jis", "jis", "sjis"),
        ("--ic=shift_jis --oc=euc-jp", "sjis", "euc"),
        ("--ic=euc-jp --oc=utf-8n", "euc", "utf8N"),
        ("--ic=utf-8 --oc=iso-2022-jp", "utf8N", "jis"),
        ("--ic=utf-8 --oc=utf-8-bom", "utf8N", "utf8"),
        ("-j", "jis1", "jis1"),
        ("-s", "jis1", "sjis1"),
        ("-e", "jis1", "euc1"),
        ("-w", "jis1", "utf1"),
        ("-j", "utf1", "jis1"),
        ("-s", "utf1", "sjis1"),
        ("-e", "utf1", "euc1"),
        ("-w", "utf1", "utf1"),
    ],
)
def test_basic_conversion_matrix(options, source_key, expected_key):
    _assert_conversion(options, EXAMPLES[source_key], EXAMPLES[expected_key])


@pytest.mark.parametrize(
    ("options", "source", "expected"),
    [
        ("-w", _hex("82A0"), _hex("E38182")),
        ("-w8", _hex("82A0"), _hex("EFBBBFE38182")),
        ("-w80", _hex("82A0"), _hex("E38182")),
        ("--oc=UTF-8-BOM", _hex("82A0"), _hex("EFBBBFE38182")),
        ("-w16", _hex("82A0"), _hex("FEFF3042")),
        ("-w16B0", _hex("82A0"), _hex("3042")),
        ("-w16L", _hex("82A0"), _hex("FFFE4230")),
        ("-w16L0", _hex("82A0"), _hex("4230")),
        ("--oc=UTF-16LE", _hex("82A0"), _hex("4230")),
    ],
)
def test_utf_output_variants(options, source, expected):
    _assert_conversion(options, source, expected)


def test_ambiguous_case():
    _assert_conversion("-j", EXAMPLES["amb"], EXAMPLES["amb.euc"])
    _assert_conversion("-jSx", EXAMPLES["amb"], EXAMPLES["amb.sjis"])


def test_broken_jis_cases():
    broken_jis = EXAMPLES["jis"].replace(b"\x1b", b"")
    _assert_conversion("-Be", broken_jis, EXAMPLES["euc"])
    _assert_conversion("-Be", EXAMPLES["jis"], EXAMPLES["euc"])


@pytest.mark.parametrize(
    ("options", "source", "expected"),
    [
        ("-eS", EXAMPLES["cp932"], EXAMPLES["cp932.ans"]),
        ("--ic=cp932 --oc=cp51932", EXAMPLES["cp932"], EXAMPLES["cp932.ans"]),
        ("-sE --cp932", EXAMPLES["cp932.ans"], EXAMPLES["cp932"]),
        ("-sE --no-cp932", EXAMPLES["cp932.ans"], EXAMPLES["no-cp932inv.ans"]),
    ],
)
def test_cp932_related_cases(options, source, expected):
    _assert_conversion(options, source, expected)


@pytest.mark.parametrize(
    ("options", "source", "expected"),
    [
        ("--ic=ISO-2022-JP-1 --oc=EUC-JP", EXAMPLES["jisx0212_jis"], EXAMPLES["jisx0212_euc"]),
        ("--ic=EUC-JP --oc=ISO-2022-JP-1", EXAMPLES["jisx0212_euc"], EXAMPLES["jisx0212_jis"]),
        ("--ic=EUC-JISX0213 --oc=Shift_JISX0213", EXAMPLES["jisx0213_euc"], EXAMPLES["jisx0213_sjis"]),
        ("--ic=ISO-2022-JP-2004 --oc=EUC-JISX0213", EXAMPLES["jisx0213_jis2004"], EXAMPLES["jisx0213_euc"]),
        ("--ic=EUC-JISX0213 --oc=ISO-2022-JP-2004", EXAMPLES["jisx0213_euc"], EXAMPLES["jisx0213_jis2004"]),
    ],
)
def test_jisx0212_and_jisx0213_cases(options, source, expected):
    _assert_conversion(options, source, expected)


@pytest.mark.parametrize(
    ("options", "source", "expected"),
    [
        ("-wZ", "　ａＡ&ア".encode("utf-8"), "　aA&ア".encode("utf-8")),
        ("-wZ1", "　ａＡ&ア".encode("utf-8"), " aA&ア".encode("utf-8")),
        ("-wZ3", "　ａＡ&ア".encode("utf-8"), "　aA&amp;ア".encode("utf-8")),
        ("-wZ4", "　ａＡ&ア".encode("utf-8"), "　aA&ｱ".encode("utf-8")),
    ],
)
def test_z_output_variants(options, source, expected):
    _assert_conversion(options, source, expected)

def test_ms_ucs_mapping():
    source = b"\x81\x60\x81\x61\x81\x7C\x81\x91\x81\x92\x81\xCA"
    _assert_conversion("-w16B0 -S --ms-ucs-map", source, b"\xFF\x5E\x22\x25\xFF\x0D\xFF\xE0\xFF\xE1\xFF\xE2")


class TestOptionsSequence:
    """Test that nkf.nkf() accepts list and tuple as the first argument."""

    def test_list_options(self):
        result = _convert(["-E", "-w"], EXAMPLES["euc"])
        assert result == EXAMPLES["utf8N"]

    def test_tuple_options(self):
        result = _convert(("-E", "-w"), EXAMPLES["euc"])
        assert result == EXAMPLES["utf8N"]

    def test_list_long_options(self):
        result = _convert(["--ic=euc-jp", "--oc=utf-8n"], EXAMPLES["euc"])
        assert result == EXAMPLES["utf8N"]

    def test_list_single_element(self):
        result = _convert(["-w"], EXAMPLES["euc"])
        assert result == EXAMPLES["utf8N"]

    def test_tuple_single_element(self):
        result = _convert(("-w",), EXAMPLES["euc"])
        assert result == EXAMPLES["utf8N"]

    def test_list_multiple_flags(self):
        source = b"\x81\x60\x81\x61\x81\x7C\x81\x91\x81\x92\x81\xCA"
        expected = b"\xFF\x5E\x22\x25\xFF\x0D\xFF\xE0\xFF\xE1\xFF\xE2"
        result = _convert(["-w16B0", "-S", "--ms-ucs-map"], source)
        assert result == expected

    def test_empty_list(self):
        result = nkf.nkf([], EXAMPLES["euc"])
        assert isinstance(result, bytes)

    def test_empty_tuple(self):
        result = nkf.nkf((), EXAMPLES["euc"])
        assert isinstance(result, bytes)

    def test_type_error_int(self):
        with pytest.raises(TypeError):
            nkf.nkf(123, EXAMPLES["euc"])

    def test_type_error_non_string_in_list(self):
        with pytest.raises(TypeError):
            nkf.nkf(["-w", 123], EXAMPLES["euc"])

    def test_type_error_none(self):
        with pytest.raises(TypeError):
            nkf.nkf(None, EXAMPLES["euc"])


class TestGuessDetail:
    """Test nkf.guess_detail() returns (encoding, newline) tuple."""

    def test_returns_tuple(self):
        result = nkf.guess_detail(EXAMPLES["utf8N"])
        assert isinstance(result, tuple)
        assert len(result) == 2

    @pytest.mark.parametrize(
        ("source_key", "expected_encoding"),
        [
            ("jis", "ISO-2022-JP"),
            ("sjis", "Shift_JIS"),
            ("euc", "EUC-JP"),
            ("utf8N", "UTF-8"),
        ],
    )
    def test_encoding_detection(self, source_key, expected_encoding):
        encoding, _ = nkf.guess_detail(EXAMPLES[source_key])
        assert encoding == expected_encoding

    def test_newline_lf(self):
        data = "あいう\nえお\n".encode("utf-8")
        _, newline = nkf.guess_detail(data)
        assert newline == "LF"

    def test_newline_cr(self):
        data = "あいう\rえお\r".encode("utf-8")
        _, newline = nkf.guess_detail(data)
        assert newline == "CR"

    def test_newline_crlf(self):
        data = "あいう\r\nえお\r\n".encode("utf-8")
        _, newline = nkf.guess_detail(data)
        assert newline == "CRLF"

    def test_newline_mixed(self):
        data = "あいう\nえお\r\n".encode("utf-8")
        _, newline = nkf.guess_detail(data)
        assert newline == "MIXED"

    def test_newline_none(self):
        data = "あいう".encode("utf-8")
        _, newline = nkf.guess_detail(data)
        assert newline is None


# --- New EXAMPLES data (Section A) ---

EXAMPLES["jis2"] = _uudecode_block(r'''
+&R1".EA&(QLH0@H`
''')

EXAMPLES["sjis2"] = _uudecode_block(r'''
%C=:3H0H`
''')

EXAMPLES["euc2"] = _uudecode_block(r'''
%NMC&HPH`
''')

EXAMPLES["utf2"] = _uudecode_block(r'''
'YI:.Z)>D"@``
''')


# --- Section A: UTF-16 conversions via short options ---

@pytest.mark.parametrize(
    ("options", "source_key", "expected_key"),
    [
        # JIS to U16L/U16B
        ("-w16L", "jis", "u16L"),
        ("-w16B", "jis", "u16B"),
        # SJIS to U16L/U16B
        ("-w16L", "sjis", "u16L"),
        ("-w16B", "sjis", "u16B"),
        # EUC to U16L/U16B
        ("-w16L", "euc", "u16L"),
        ("-w16B", "euc", "u16B"),
        # UTF8 to U16L/U16B/U16L0/U16B0
        ("-w16L", "utf8N", "u16L"),
        ("-w16L0", "utf8N", "u16L0"),
        ("-w16B", "utf8N", "u16B"),
        ("-w16B0", "utf8N", "u16B0"),
    ],
)
def test_utf16_conversion_short_options(options, source_key, expected_key):
    _assert_conversion(options, EXAMPLES[source_key], EXAMPLES[expected_key])


# --- Section A: Full --ic/--oc conversion matrix ---

@pytest.mark.parametrize(
    ("options", "source_key", "expected_key"),
    [
        # JIS source (--ic=iso-2022-jp)
        (["--ic=iso-2022-jp", "--oc=iso-2022-jp"], "jis", "jis"),
        (["--ic=iso-2022-jp", "--oc=euc-jp"], "jis", "euc"),
        (["--ic=iso-2022-jp", "--oc=utf-8n"], "jis", "utf8N"),
        (["--ic=iso-2022-jp", "--oc=utf-16le-bom"], "jis", "u16L"),
        (["--ic=iso-2022-jp", "--oc=utf-16be-bom"], "jis", "u16B"),
        # SJIS source (--ic=shift_jis)
        (["--ic=shift_jis", "--oc=iso-2022-jp"], "sjis", "jis"),
        (["--ic=shift_jis", "--oc=shift_jis"], "sjis", "sjis"),
        (["--ic=shift_jis", "--oc=utf-8n"], "sjis", "utf8N"),
        (["--ic=shift_jis", "--oc=utf-16le-bom"], "sjis", "u16L"),
        (["--ic=shift_jis", "--oc=utf-16be-bom"], "sjis", "u16B"),
        # EUC source (--ic=euc-jp)
        (["--ic=euc-jp", "--oc=iso-2022-jp"], "euc", "jis"),
        (["--ic=euc-jp", "--oc=shift_jis"], "euc", "sjis"),
        (["--ic=euc-jp", "--oc=euc-jp"], "euc", "euc"),
        (["--ic=euc-jp", "--oc=utf-16le-bom"], "euc", "u16L"),
        (["--ic=euc-jp", "--oc=utf-16be-bom"], "euc", "u16B"),
        # UTF-8 source (--ic=utf-8)
        (["--ic=utf-8", "--oc=shift_jis"], "utf8N", "sjis"),
        (["--ic=utf-8", "--oc=euc-jp"], "utf8N", "euc"),
        (["--ic=utf-8", "--oc=utf-8"], "utf8N", "utf8N"),
        (["--ic=utf-8", "--oc=utf-8n"], "utf8N", "utf8N"),
        (["--ic=utf-8", "--oc=utf-16le-bom"], "utf8N", "u16L"),
        (["--ic=utf-8", "--oc=utf-16le"], "utf8N", "u16L0"),
        (["--ic=utf-8", "--oc=utf-16be-bom"], "utf8N", "u16B"),
        (["--ic=utf-8", "--oc=utf-16be"], "utf8N", "u16B0"),
    ],
)
def test_ic_oc_conversion_matrix(options, source_key, expected_key):
    _assert_conversion(options, EXAMPLES[source_key], EXAMPLES[expected_key])


# --- Section A: Secondary example set conversion matrix (jis2/sjis2/euc2/utf2) ---

@pytest.mark.parametrize(
    ("options", "source_key", "expected_key"),
    [
        ("-j", "jis2", "jis2"),
        ("-s", "jis2", "sjis2"),
        ("-e", "jis2", "euc2"),
        ("-w", "jis2", "utf2"),
        ("-j", "sjis2", "jis2"),
        ("-s", "sjis2", "sjis2"),
        ("-e", "sjis2", "euc2"),
        ("-w", "sjis2", "utf2"),
        ("-j", "euc2", "jis2"),
        ("-s", "euc2", "sjis2"),
        ("-e", "euc2", "euc2"),
        ("-w", "euc2", "utf2"),
        ("-j", "utf2", "jis2"),
        ("-s", "utf2", "sjis2"),
        ("-e", "utf2", "euc2"),
        ("-w", "utf2", "utf2"),
    ],
)
def test_secondary_conversion_matrix(options, source_key, expected_key):
    _assert_conversion(options, EXAMPLES[source_key], EXAMPLES[expected_key])


# --- Section B: UTF-32 output variants ---

@pytest.mark.parametrize(
    ("options", "source", "expected"),
    [
        ("-w32", _hex("82A0"), _hex("0000FEFF00003042")),
        ("--oc=UTF-32", _hex("82A0"), _hex("0000FEFF00003042")),
        ("-w32B", _hex("82A0"), _hex("0000FEFF00003042")),
        ("-w32B0", _hex("82A0"), _hex("00003042")),
        ("--oc=UTF-32BE", _hex("82A0"), _hex("00003042")),
        ("--oc=UTF-32BE-BOM", _hex("82A0"), _hex("0000FEFF00003042")),
        ("-w32L", _hex("82A0"), _hex("FFFE000042300000")),
        ("-w32L0", _hex("82A0"), _hex("42300000")),
        ("--oc=UTF-32LE", _hex("82A0"), _hex("42300000")),
        ("--oc=UTF-32LE-BOM", _hex("82A0"), _hex("FFFE000042300000")),
    ],
)
def test_utf32_output_variants(options, source, expected):
    _assert_conversion(options, source, expected)


# --- Section C: UTF-8 edge cases ---

def test_utf8_smp_character():
    _assert_conversion("-w", b"\xf0\xa0\x80\x8b", b"\xf0\xa0\x80\x8b")


def test_utf8_jis_second_level_kanji():
    source = b"\xe9\xa4\x83\xe5\xad\x90"
    _assert_conversion("-w", source, source)


# --- Additional UTF output variants (long-form --oc= options) ---

@pytest.mark.parametrize(
    ("options", "source", "expected"),
    [
        ("--oc=UTF-8", _hex("82A0"), _hex("E38182")),
        ("--oc=UTF-8N", _hex("82A0"), _hex("E38182")),
        ("--oc=UTF-16", _hex("82A0"), _hex("FEFF3042")),
        ("-w16B", _hex("82A0"), _hex("FEFF3042")),
        ("--oc=UTF-16BE-BOM", _hex("82A0"), _hex("FEFF3042")),
        ("--oc=UTF-16LE-BOM", _hex("82A0"), _hex("FFFE4230")),
    ],
)
def test_additional_utf_output_variants(options, source, expected):
    _assert_conversion(options, source, expected)


# --- Upstream test data (auto-generated from nkf_test.pl) ---

EXAMPLES["_Z4"] = _uudecode_block(r'''
MH:.AUJ'7H:*AIJ&\H:NAK*6AI:*EHZ6DI:6EIJ6GI:BEJ:6JI:NEK*6MI:ZE
MKZ6PI;&ELJ6SI;2EM:6VI;>EN*6YI;JENZ6\I;VEOJ6_I<"EP:7"I<.EQ*7%
MI<:EQZ7(I<FERJ7+I<RES:7.I<^ET*71I=*ETZ74I=6EUJ77I=BEV:7:I=NE
KW*7=I=ZEWZ7@I>&EXJ7CI>2EY:7FI>>EZ*7II>JEZZ7LI>VE[Z7RI?.E]```
''')

EXAMPLES["_Z4.ans"] = _uudecode_block(r'''
MCJ&.HHZCCJ2.I8ZPCMZ.WXZGCK&.J(ZRCJF.LXZJCK2.JXZUCK:.MH[>CK>.
MMX[>CKB.N([>CKF.N8[>CKJ.NH[>CKN.NX[>CKR.O([>CKV.O8[>CKZ.OH[>
MCK^.OX[>CL".P([>CL&.P8[>CJ^.PH["CMZ.PX[#CMZ.Q([$CMZ.Q8[&CL>.
MR([)CLJ.RH[>CLJ.WX[+CLN.WH[+CM^.S([,CMZ.S([?CLV.S8[>CLV.WX[.
MCLZ.WH[.CM^.SX[0CM&.TH[3CJR.U(ZMCM6.KH[6CM>.V([9CMJ.VX[<CJ:.
%W8ZSCMX`
''')

EXAMPLES["bug19779"] = _uudecode_block(r'''
2&R1","$;*$(*&R1"7V8;*$(*
''')

EXAMPLES["bug19779.ans"] = _uudecode_block(r'''
M/3])4T\M,C`R,BU*4#]"/T=Y4D--0T5B2T5)/3\]"CT_25-/+3(P,C(M2E`_
10C]'>5)#6#)98DM%23T_/0H`
''')

EXAMPLES["cr"] = _uudecode_block(r'''
1I,:DN:3(#71E<W0-=&5S=`T`
''')

EXAMPLES["cr.ans"] = _uudecode_block(r'''
7&R1")$8D.21(&RA""G1E<W0*=&5S=`H`
''')

EXAMPLES["fixed_qencode"] = _uudecode_block(r'''
M("`@("`@("`],4(D0CYE/STS1#TQ0BA""B`@("`@("`@/3%")$(^93TS1CTS
'1#TQ0BA""@``
''')

EXAMPLES["fixed_qencode.ans"] = _uudecode_block(r'''
F("`@("`@("`;)$(^93\]&RA""B`@("`@("`@&R1"/F4_/1LH0@H`
''')

EXAMPLES["jisx0213_jis2000"] = _uudecode_block(r'''
;&R0H3R(O+WU/54]]="A^>1LD*%`A(7YV&RA"
''')

EXAMPLES["jisx0213_utf8"] = _uudecode_block(r'''
:[[R'Y:REY:V!Y;>+Y;>BZ;ZB\*""B?"JFK(`
''')

EXAMPLES["jisx0213needx0213_f"] = _uudecode_block(r'''
MXH*LPKS#B<.?P['%C<6"Q)C$C<6OR:[%B\63RJ+)FLN0RZ;+GN*=O^*%M^*3
MFN.+DN.+G^*8GO"@@(OE@(+EA(OCDYOEC:'EC:/EEH;OJ+CEG+/EHJGEI9WE
MB9WFD[?FF8CFFJ#FGKOFH;+CKK;GI(#OJ8WGIKCOJ97GKYGGL:WGM9SGN8?H
M@+?PIJN_Z(VBZ(ZGZ(^1Z)2CZ)F;Z)FLZ*"?[ZFA[ZFB[ZFD\*B)M^F"F>F$
ME>F$I^>J@N>JN>>MI.>ML^>OL.>RIN>SM>2+G>>VI^>ZD>>]DO"CM([H@([P
MIIJPZ(2>\*:CG>B)B^^IG>B*M.B.E.B0C^B1O.B4F^B5D?"FO[;HF:_HFZ;H
MG+KHG;+HH(OPIYB4Z*.2Z*6%Y)JAZ*BUY)R,\*>NOO"GMJ#HM(GHN:SDH8[H
MOK;HO['I@K#IA8;IA9GIB9'PJ*:(Z8N&Z8N[Z8V:Z9")Z96XZ9J]Z9N:Z9Z6
MZ:"EZ:*\Z:.QZ:6`Z:B@Z:BQZ:NE\*FXO>FOKO"INZGIL:GPJH":Z;:9Z;B"
-\**(F/"JE['PJIJR"@``
''')

EXAMPLES["jisx0213needx0213_f.ans"] = _uudecode_block(r'''
MJ:&ILZG`J=6IYZG^JJZJOJK,JM6JZZKZJZJKO:O#J]6KX:OQK*JLO*S+K-VL
MZJW^KJ*NO*[,KMNN[Z[PKZJOMJ_%K]^OZ:_^]:3UN/7$]=CUX_7^^:WYM/G$
M^='YYOGP^J3ZM/K(^MWZ[?KY^Z'[MOO.^]+[Y_OY_*_\N/S)_-W\[/SPC_.M
MC_.TC_/.C_/1C_/CC_/VC_2HC_2[C_3$C_3>C_3JC_3UC_6EC_6ZC_7!C_76
MC_7KC_7TC_:BC_:WC_;!C_;2C_;FC_;PC_>AC_>[C_?.C_?:C_?BC_?\C_BJ
MC_BSC_C`C_C.C_C8C_CKC_CYC_FOC_FSC_G/C_G<C_GJC_GTC_JHC_J^C_K!
MC_K=C_KFC_KVC_NDC_NQC_O%C_O2C_OOC_OSC_RDC_R\C_S&C_S2C_SDC_S^
EC_VAC_VTC_W,C_W8C_WMC_WVC_ZKC_Z\C_[-C_[3C_[NC_[V"@``
''')

EXAMPLES["jisx0213nonbmp"] = _uudecode_block(r'''
MKJ*OPJ_,K^"O^\_4S^//[O6Z]?+VJ?:R]N#W[/C^^:GYQ_G4^>[ZW?NS^\G[
M[/S)_-'^YH^AH8^AJX^AKH^AMH^AQH^A\(^A]X^A^8^CHH^CI8^CIX^CL8^C
MLH^CN(^COX^CP8^CRH^CTH^CTX^CV8^CW(^C]X^DJH^DL8^DLH^DNH^DO8^D
MV8^DW(^DWH^DXX^DZH^DZX^D\H^D](^D]8^EI8^ELH^EOH^EQ(^EQX^EU8^E
MUH^E_H^HL(^HMX^HN(^HNH^HNX^HOX^HP(^HQ8^HR(^HRH^HRX^HVX^HYH^H
M[(^LHH^LJX^LL(^LT(^LY8^L[8^L\H^MI(^MJ8^MJH^MLH^MM(^MM8^MN8^M
MUH^M_8^NHX^NI(^NNH^NO(^NO8^NPH^NPX^NQ(^NQX^NR8^NU8^NUH^NUX^N
MVX^N]X^N^(^OJH^OOX^OP(^OPH^OPX^OSH^OV8^OX8^OZ8^OZH^O\(^O]8_N
MHX_NM(_NR8_NW(_NWH_NWX_NX(_OLH_OQX_OS8_OX8_OY(_PHH_PLX_PN8_P
MTX_P^X_QKH_QL(_QM8_QQ(_QW8_QX8_QYH_QZ8_Q]8_Q]X_Q^H_RH8_RHX_R
MI(_RJ(_RK(_RO8_RR(_RVX_R]8_R]H_SLH_SO8_SOH_SP(_STH_SW8_SWH_S
M\X_S](_S]8_S]X_S^X_S_8_THH_TI(_TIX_TKH_TKX_TM(_TM8_TO8_TPH_T
MSX_TZ8_TZX_T\H_T]8_T^8_UM8_UNH_UQH_UUH_UV(_UVH_UW8_UWX_UXX_U
MZH_U\(_U\X_VQ(_VSH_VW8_V]8_V_H_WH8_WHH_WLX_WMH_WY(_WY8_WZX_W
M[H_W\X_XJ8_XJH_XK(_XM(_XO(_XOH_XPH_XUH_XXX_X]X_X^8_X^H_YI8_Y
MKX_YLH_YN8_YPH_YR(_YV8_YWH_YYH_YZX_Y^H_Y_H_ZH8_ZK(_ZKX_ZSX_Z
MT(_ZUX_ZY8_ZYH_Z\8_Z\H_Z_H_[H8_[K(_[K8_[MH_[MX_[O8_[OH_[SH_[
MSX_[UX_[VH_[W(_[W8_[X8_[Y8_[YX_[Z8_[\8_\HH_\HX_\N(_\PH_\S(_\
MUH_\V8_\W8_\]H_]K(_]RX_]S(_]V8_]VX_]W8_]YX_][8_]\(_^I8_^J8_^
=JX_^LH_^M8_^TX_^V(_^VH_^[H_^\(_^\H_^]@H`
''')

EXAMPLES["jisx0213nonbmp.ans"] = _uudecode_block(r'''
M\*"`B_"AB+WPH8R;\*&1KO"AHKWPH*Z?\*&:M/"AN+3PHX>$\*.7A/"CG+_P
MHYVC\*.SOO"DG['PI9*.\*64CO"EG;'PI:>$\*6VH?"FJ[_PIKF`\*>#M/"G
MFH3PJ(FW\*B/C?"JAI#PH(*)\*""HO"@@J3PH(:B\*"(D_"@C*OPH(Z!\*"-
ML?"@C[GPH)&*\*"4B?"@EY;PH)BH\*"=C_"@H(?PH*"Z\*"BN?"@I;SPH*:=
M\*"KD_"@K)WPH+6%\*"WH?"@NI7PH+FM\*"YI/"@O9_PH8B!\*&)E?"AB;OP
MH8FT\*&+I/"ABY?PH8N]\*&,MO"AC83PH8^$\*&1K?"AEY?PIK"I\*&9A_"A
MG(;PH9V"\*&G@_"AL9;PH;2M\*&UA?"AM;CPH;6B\*&VH?"AMISPH;:2\*&V
MM_"AMZ#PH;BS\*&\GO"AO;;PH;^Z\**%N_"BC)[PHHZM\**;L_"BH9OPHJ*K
M\**FC_"BJKCPHJV/\**MD/"BK8;PHK"=\**NIO"BL*3PHK>A\*.'@_"CA[7P
MHX:V\*.-LO"CCY/PHX^2\*./D/"CCZ3PHX^5\*./FO"CCY_PHY&*\*.1D?"C
MD8OPHY&E\*.3I/"CE9KPHY:4\*.8N?"CF8?PHYBX\*.8NO"CG)SPHYR,\*.=
MI/"CG[_PHY^G\*.@I/"CH+WPHZJ8\*.QO_"CM(#PH[6`\*.WNO"CM[GPH[>3
M\*.]OO"D@I;PI(2#\*2'AO"DA[[PI(Z\\*28J?"DFJ7PI**6\*2IC?"DK9;P
MI*VO\*2PEO"DM)3PI+B.\*2XM_"DN:KPI+J+\*6!BO"E@97PI82B\*6&J?"E
MAZ7PI8>-\*6(GO"EB8SPI9"N\*63F?"EEJ?PI9ZI\*6>M/"EIY3PI:ND\*6K
MH_"EJ['PI:ZR\*6QB_"EL:3PI;BN\*6YEO"EN:7PI;FB\*6[F/"ENX+PI;NH
M\*6\H_"EO9SPI;^@\*6_E/"F@(SPI;^[\*:`E_"F@:#PIH.M\*:)L/"FBH;P
MIHV,\*.TCO"FD(+PIIF^\*::L/"FG)WPIJ.=\*:CJO"FI9'PIJ6O\*:GG?"F
MJ)[PIJF8\*:JC/"FJK?PIK&S\*:SG?"FN:7PIKZ4\*:_N/"FO[;PIK^W\*>$
MC?"GA+GPIX^;\*>/FO"GC[[PIY"0\*>1B?"GF)7PIYB4\*>8L?"GFI/PIYR.
M\*><H_"GG9+PIZ:%\*>JA/"GKK/PIZZ^\*>OA_"GLKCPI[:@\*>XD/"GOK?P
MJ(**\*B"N_"HBH+PJ(NS\*B0C/"HD97PJ)6K\*B7B/"HEXGPJ)N7\*B;NO"H
MI8GPJ*6&\*BEJ_"HIH?PJ*:(\*BFNO"HIKOPJ*B>\*BHJ?"HJ;'PJ*F#\*BJ
MF?"HJXWPJ*ND\*BKG?"HKX'PJ*^O\*BTD/"HM;'PJ+>[\*BXG_"HN+;PJ+J)
M\*B[J_"HO++PJ+^X\*F*H/"IBK'PJ9*0\*F7C_"IF;_PJ9NP\*F<F?"IG9#P
MJ:.&\*FILO"IMYOPJ;B]\*FXE?"INHKPJ;F)\*F[A/"INZGPJ;N;\*F_CO"J
K@*_PJH":\*J#N?"J@H+PHHB8\*J.C/"JD+?PJI>Q\*J8@O"JF)KPJIJR"@``
''')

EXAMPLES["mime.is8859"] = _uudecode_block(r'''
M/3])4T\M.#@U.2TQ/U$_*CU#-V%V83\_/2`*4&5E<B!4]G)N9W)E;@I,87-S
M92!(:6QL97+X92!0971E<G-E;B`@7"`B36EN(&MA97!H97-T(&AA<B!F86%E
M="!E="!F;V5L(2(*06%R:'5S(%5N:79E<G-I='DL($1%3DU!4DL@(%P@(DUI
<;B!KYG!H97-T(&AA<B!FY65T(&5T(&;X;"$B"@!K
''')

EXAMPLES["mime.is8859.ans"] = _uudecode_block(r'''
M*L=A=F$_(`I0965R(%3V<FYG<F5N"DQA<W-E($AI;&QE<OAE(%!E=&5R<V5N
M("!<(")-:6X@:V%E<&AE<W0@:&%R(&9A865T(&5T(&9O96PA(@I!87)H=7,@
M56YI=F5R<VET>2P@1$5.34%22R`@7"`B36EN(&OF<&AE<W0@:&%R(&;E970@
)970@9OAL(2(*
''')

EXAMPLES["mime_out"] = _uudecode_block(r'''
M"BTM+2T*4W5B:F5C=#H@86%A82!A86%A(&%A86$@86%A82!A86%A(&%A86$@
M86%A82!A86%A(&%A86$@86%A82!A86%A(&%A86$@86%A82!A86%A"BTM+2T*
M4W5B:F5C=#H@I**DI*2FI*BDJJ2KI*VDKZ2QI+.DM:2WI+FDNZ2]I+^DP:3$
MI,:DR*3*I,NDS*3-I,ZDSZ32I-6DV*3;I-ZDWZ3@I.&DXJ3DI*2DYJ2HI.@*
M+2TM+0I3=6)J96-T.B!A86%A(&%A86$@86%A82!A86%A(&%A86$@86%A82!A
I86%A(*2BI*2DIJ2HI*H@86%A82!A86%A(&%A86$@86%A80HM+2TM"@H`
''')

EXAMPLES["mime_out.ans"] = _uudecode_block(r'''
M"BTM+2T*4W5B:F5C=#H@86%A82!A86%A(&%A86$@86%A82!A86%A(&%A86$@
M86%A82!A86%A(&%A86$@86%A82!A86%A(&%A86$@86%A80H@86%A80HM+2TM
M"E-U8FIE8W0Z(#T_25-/+3(P,C(M2E`_0C]'>5)#2D-):TI#46U*0V=K2VE1
M<DI#,&M,>5%X2D1-:TY343-*1&MB2T5)/3\]"B`]/TE33RTR,#(R+4I0/T(_
M1WE20TI$<VM04U$O2D5%:U)#4D=*16=K4VE23$I%=VM44U)/2D4X:U5I4E9*
M1F=B2T5)/3\]"B`]/TE33RTR,#(R+4I0/T(_1WE20TI&<VM8:5)F2D=!:UE3
M4FE*1U%K2D-2;4I#9VMA0G-O46<]/3\]"BTM+2T*4W5B:F5C=#H@86%A82!A
M86%A(&%A86$@86%A82!A86%A(&%A86$@86%A80H@/3])4T\M,C`R,BU*4#]"
M/T=Y4D-*0TEK2D-1;4I#9VM+:'-O46<]/3\](&%A86$@86%A82!A86%A(&%A
)86$*+2TM+0H*
''')

EXAMPLES["mime_out.ans.alt"] = _uudecode_block(r'''
M"BTM+2T*4W5B:F5C=#H@86%A82!A86%A(&%A86$@86%A82!A86%A(&%A86$@
M86%A82!A86%A(&%A86$*(&%A86$@86%A82!A86%A(&%A86$@86%A80HM+2TM
M"E-U8FIE8W0Z(#T_25-/+3(P,C(M2E`_0C]'>5)#2D-):TI#46U*0V=K2VE1
M<DI#,&M,>5%X2D1-:TY343-'>6A#/ST*(#T_25-/+3(P,C(M2E`_0C]'>5)#
M2D1K:T]Y43E*1#AK45-214I%66M30U)+2D5S:U1#4DY*131K5'E24TI&56M7
M0U)B1WEH0S\]"B`]/TE33RTR,#(R+4I0/T(_1WE20TI&-&M8>5)G2D=%:UEI
M4FM*0U%K6FE1;TI'9V)+14D]/ST*+2TM+0I3=6)J96-T.B!A86%A(&%A86$@
M86%A82!A86%A(&%A86$@86%A82!A86%A"B`]/TE33RTR,#(R+4I0/T(_1WE2
M0TI#26M*0U%M2D-G:TMH<V]19ST]/ST@86%A82!A86%A(&%A86$*(&%A86$*
&+2TM+0H*
''')

EXAMPLES["mime_out.ans.alt2"] = _uudecode_block(r'''
M"BTM+2T*4W5B:F5C=#H@86%A82!A86%A(&%A86$@86%A82!A86%A(&%A86$@
M86%A82!A86%A(&%A86$@86%A82!A86%A(&%A86$@86%A80H@86%A80HM+2TM
M"E-U8FIE8W0Z(#T_25-/+3(P,C(M2E`_0C]'>5)#2D-):TI#46U*0V=K2VE1
M<DI#,&M,>5%X2D1-:TY343-*1&MK3WE1.4=Y:$,_/0H@/3])4T\M,C`R,BU*
M4#]"/T=Y4D-*1#AK45-214I%66M30U)+2D5S:U1#4DY*131K5'E24TI&56M7
M0U)B2D8T:UAY4F='>6A#/ST*(#T_25-/+3(P,C(M2E`_0C]'>5)#2D=%:UEI
M4FM*0U%K6FE1;TI'9V)+14D]/ST*+2TM+0I3=6)J96-T.B!A86%A(&%A86$@
M86%A82!A86%A(&%A86$@86%A82!A86%A(#T_25-/+3(P,C(M2E`_0C]'>5)#
M2D-):TI"<V]19ST]/ST*(#T_25-/+3(P,C(M2E`_0C]'>5)#2D-9:TM#47%'
@>6A#/ST@86%A82!A86%A(&%A86$@86%A80HM+2TM"@H`
''')

EXAMPLES["mime_out.ans.alt3"] = _uudecode_block(r'''
M"BTM+2T*4W5B:F5C=#H@86%A82!A86%A(&%A86$@86%A82!A86%A(&%A86$@
M86%A82!A86%A(&%A86$@86%A82!A86%A(&%A86$@86%A80H@86%A80HM+2TM
M"E-U8FIE8W0Z(#T_25-/+3(P,C(M2E`_0C]'>5)#2D-):TI#46U*0V=K2VE1
M<DI#,&M,>5%X2D1-:TY343-*1&MK3WE1.4=Y:$,_/0H@/3])4T\M,C`R,BU*
M4#]"/T=Y4D-*1#AK45-214I%66M30U)+2D5S:U1#4DY*131K5'E24TI&56M7
M0U)B2D8T:UAX<V]19ST]/ST*(#T_25-/+3(P,C(M2E`_0C]'>5)#2D=!:UE3
M4FE*1U%K2D-2;4I#9VMA0G-O46<]/3\]"BTM+2T*4W5B:F5C=#H@86%A82!A
M86%A(&%A86$@86%A82!A86%A(&%A86$@86%A82`]/TE33RTR,#(R+4I0/T(_
M1WE20TI#26M*0G-O46<]/3\]"B`]/TE33RTR,#(R+4I0/T(_1WE20TI#66M+
D0U%Q1WEH0S\](&%A86$@86%A82!A86%A(&%A86$*+2TM+0H*1
''')

EXAMPLES["ms_ucs_map_1_sjis"] = _hex("81608161817c8191819281ca")

EXAMPLES["ms_ucs_map_1_utf16"] = _hex("301c2016221200a200a300ac")

EXAMPLES["ms_ucs_map_1_utf16_ms"] = _hex("ff5e2225ff0dffe0ffe1ffe2")

EXAMPLES["nkf_19_bug_2"] = _uudecode_block(r'''
%I-NDL@H`
''')

EXAMPLES["nkf_19_bug_2.ans"] = _uudecode_block(r'''
%I-NDL@H`
''')

EXAMPLES["nkf_19_bug_3"] = _uudecode_block(r'''
8[;'Q\,&L"N6ZSN\*\NT)ON7.SL_+"0D*
''')

EXAMPLES["nkf_19_bug_3.ans"] = _uudecode_block(r'''
8[;'Q\,&L"N6ZSN\*\NT)ON7.SL_+"0D*
''')

EXAMPLES["non_strict_mime"] = _uudecode_block(r'''
M/3])4T\M,C`R,BU*4#]"/PIG<U-#;V]+.6=R-D-O;TQ%9W1Y0W0T1D-$46].
M0V\V16=S,D]N;T999S1Y1%=)3$IG=4-0:UD*2W!G<FU#>$E+:6=R,D-V;TMI
,9W-30V]O3&,*/ST*
''')

EXAMPLES["non_strict_mime.ans"] = _uudecode_block(r'''
M&R1")$8D)"0_)$`D)"1&)%XD.2$C&RA"#0H-"ALD0CMD)$\[?B$Y)6PE.21+
<)&(]<20K)#LD1B0D)#\D0"0D)$8D)"1>&RA""@``
''')

EXAMPLES["q_encode_softrap"] = _uudecode_block(r'''
H/3%")$(T03MZ)3T*,R$\)4DD3CTQ0BA""CTQ0B1"2E$T.3TQ0BA""@``
''')

EXAMPLES["q_encode_softrap.ans"] = _uudecode_block(r'''
>&R1"-$$[>B4S(3PE221.&RA""ALD0DI1-#D;*$(*
''')

EXAMPLES["rot13"] = _uudecode_block(r'''
MI+.D\Z3+I,&DSZ&BS:W"]*3(I*2DI*3>I+FAHPH*;FMF('9E<BXQ+CDR(*3R
MS?C-T:2UI+NDQJ2DI+^DP*2DI,:DI*3>I+FDK*&B05-#24D@I,O"T*2WI,8@
M4D]4,3,@I*P*P+6DMZ2OQK"DI*3&I*2DRJ2DI.BDIJ3'H:*PRK*\I,ZDZ*2F
MI,O*T;2YI+6D[*3>I+ND\Z&C"@HE(&5C:&\@)VAO9V4G('P@;FMF("UR"FAO
#9V4*
''')

EXAMPLES["rot13.ans"] = _uudecode_block(r'''
M&R1"4V)31%-Z4W!3?E!1?%QQ15-W4U-34U,O4VA04ALH0@H*87AS(&ER92XQ
M+CDR(!LD0E-#?$E\(E-D4VI3=5-34VY3;U-34W534U,O4VA36U!1&RA"3D90
M5E8@&R1"4WIQ(5-F4W4;*$(@14)',3,@&R1"4UL;*$(*&R1";V139E->=5]3
M4U-U4U-3>5-34SE355-V4%%?>6%K4WU3.5-54WIY(F-H4V13/5,O4VI31%!2
A&RA""@HE(')P=6(@)W5B='(G('P@87AS("UE"G5B='(*
''')

EXAMPLES["shift_jisx0213conflict_ibmext"] = _hex("8740ed40eef6fa52fb45fbfcfc4b")

EXAMPLES["shift_jisx0213conflict_ibmext.cp932utf8"] = _hex("e291a0e7ba8ae285b7e285a8e6b7bce9ab99e9bb91")

EXAMPLES["shift_jisx0213conflict_ibmext.x0213utf8"] = _hex("e291a0e7a183e9869ee8b489e98c8de9a8a0f0a9a9b2")

EXAMPLES["slash"] = _uudecode_block(r'''
7("`]/U8\5"U5.5=%2RTK.U<U32LE+PH`
''')

EXAMPLES["slash.ans"] = _uudecode_block(r'''
7("`]/U8\5"U5.5=%2RTK.U<U32LE+PH`
''')

EXAMPLES["x0201.euc"] = _uudecode_block(r'''
MP;2ST:6KI:VEKZ6QI;.EK*6NI;"ELJ6T"L&TL=&CP:/"H\.CQ*/%H\:CQZ/A
MH^*CXZ/DH^6CYJ/G"L&TM:VYYJ&JH?>A]*'PH?.AL*'UH?:ARJ'+H=VAW*'A
MH<ZASZ'0H=&A[PK(OK/1CK:.MXZX/8ZYCKJ.MH[>CK>.WHZXCMZ.N8[>CKJ.
MWJ3("LB^L]&.RH[?CLN.WX[,CM^.S8[?CLZ.WXZWCM^.L8[>"H[*CM^.RX[?
MCLP*:&%N:V%K=2".RH[?CLN.WX[,CJ0*CLJ.WX[+CM^.S([=CJ$*R+ZST:3.
#N.4*
''')

EXAMPLES["x0201.jis"] = _uudecode_block(r'''
M&R1"030S424K)2TE+R4Q)3,E+"4N)3`E,B4T&RA""ALD0D$T,5$C02-"(T,C
M1"-%(T8C1R-A(V(C8R-D(V4C9B-G&RA""ALD0D$T-2TY9B$J(7<A="%P(7,A
M,"%U(78A2B%+(5TA7"%A(4XA3R%0(5$A;QLH0@H;)$)(/C-1&RA)-C<X&RA"
M/1LH23DZ-EXW7CA>.5XZ7ALD0B1(&RA""ALD0D@^,U$;*$E*7TM?3%]-7TY?
M-U\Q7ALH0@H;*$E*7TM?3!LH0@IH86YK86MU(!LH24I?2U],)!LH0@H;*$E*
97TM?3%TA&RA""ALD0D@^,U$D3CAE&RA""@``
''')

EXAMPLES["x0201.sjis"] = _uudecode_block(r'''
MD5.*<(-*@TR#3H-0@U*#2X--@T^#48-3"I%3B7""8()A@F*"8X)D@F6"9H*!
M@H*"@X*$@H6"AH*'"I%3BTR-AH%)@9>!E(&0@9.!3X&5@9:!:8%J@7R!>X&!
M@6V!;H%O@7"!CPJ4O(IPMK>X/;FZMMZWWKC>N=ZZWH+&"I2\BG#*W\O?S-_-
MW\[?M]^QW@K*W\O?S`IH86YK86MU(,K?R]_,I`K*W\O?S-VA"I2\BG""S(SC
!"@!"
''')

EXAMPLES["x0201.sosi"] = _uudecode_block(r'''
M&R1"030S424K)2TE+R4Q)3,E+"4N)3`E,B4T&RA*"ALD0D$T,5$C02-"(T,C
M1"-%(T8C1R-A(V(C8R-D(V4C9B-G&RA*"ALD0D$T-2TY9B$J(7<A="%P(7,A
M,"%U(78A2B%+(5TA7"%A(4XA3R%0(5$A;QLH2@H;)$)(/C-1&RA*#C8W.`\;
M*$H]#CDZ-EXW7CA>.5XZ7@\;)$(D2!LH2@H;)$)(/C-1&RA*#DI?2U],7TU?
M3E\W7S%>#PH.2E]+7TP/&RA*"FAA;FMA:W4@#DI?2U],)`\;*$H*#DI?2U],
672$/&RA*"ALD0D@^,U$D3CAE&RA""@``
''')

EXAMPLES["x0201.utf"] = _uudecode_block(r'''
MY86HZ*>2XX*KXX*MXX*OXX*QXX*SXX*LXX*NXX*PXX*RXX*T"N6%J.B+L>^\
MH>^\HN^\H^^\I.^\I>^\IN^\I^^]@>^]@N^]@^^]A.^]A>^]AN^]APKEA:CH
MJ)CEC[?OO('OO*#OO(/OO(3OO(7OO+[OO(;OO(KOO(COO(GBB)+OO(OOO)WO
MO+OOO+WOO9OOO9W"I0KEC8KHIY+OO;;OO;?OO;@][[VY[[VZ[[VV[[Z>[[VW
M[[Z>[[VX[[Z>[[VY[[Z>[[VZ[[Z>XX&H"N6-BNBGDN^^BN^^G^^^B^^^G^^^
MC.^^G^^^C>^^G^^^CN^^G^^]M^^^G^^]L>^^G@KOOHKOOI_OOHOOOI_OOHP*
M:&%N:V%K=2#OOHKOOI_OOHOOOI_OOHSOO:0*[[Z*[[Z?[[Z+[[Z?[[Z,[[Z=
1[[VA"N6-BNBGDN.!KN6^C`H`
''')

EXAMPLES["x0201.x0208"] = _uudecode_block(r'''
M&R1"030S424K)2TE+R4Q)3,E+"4N)3`E,B4T&RA""ALD0D$T,5$;*$)!0D-$
M149'86)C9&5F9PH;)$)!-#4M.68;*$(A0",D)5XF*B@I+2L]6UU[?1LD0B%O
M&RA""ALD0D@^,U$E*R4M)2\;*$(]&R1")3$E,R4L)2XE,"4R)30D2!LH0@H;
M)$)(/C-1)5$E5"57)5HE724M(2PE(B$K&RA""ALD0B51)50E51LH0@IH86YK
M86MU(!LD0B51)50E52$B&RA""ALD0B51)50E525S(2,;*$(*&R1"2#XS421.
&.&4;*$(*
''')


# =========================================================================
# Upstream test ports (from nkf_test.pl)
# =========================================================================


class TestJISX0213Extended:
    """Tests for JIS X 0213 extended character sets."""

    def test_jisx0213_euc_to_utf8(self):
        _assert_conversion(["--ic=EUC-JISX0213", "-w"], EXAMPLES["jisx0213_euc"], EXAMPLES["jisx0213_utf8"])

    def test_jisx0213_utf8_to_euc(self):
        _assert_conversion(["--oc=EUC-JISX0213", "-W"], EXAMPLES["jisx0213_utf8"], EXAMPLES["jisx0213_euc"])

    def test_jisx0213_jis2000_to_utf8(self):
        _assert_conversion(["--ic=ISO-2022-JP-2004", "-w"], EXAMPLES["jisx0213_jis2000"], EXAMPLES["jisx0213_utf8"])

    def test_jisx0213_jis2004_to_utf8(self):
        _assert_conversion(["--ic=ISO-2022-JP-2004", "-w"], EXAMPLES["jisx0213_jis2004"], EXAMPLES["jisx0213_utf8"])

    def test_jisx0213_utf8_to_jis2004(self):
        _assert_conversion(["--oc=ISO-2022-JP-2004", "-W"], EXAMPLES["jisx0213_utf8"], EXAMPLES["jisx0213_jis2004"])

    def test_jisx0213_nonbmp_euc_to_utf8(self):
        _assert_conversion(["--ic=EUC-JISX0213", "-w"], EXAMPLES["jisx0213nonbmp"], EXAMPLES["jisx0213nonbmp.ans"])

    def test_jisx0213_nonbmp_utf8_to_euc(self):
        _assert_conversion(["--oc=EUC-JISX0213", "-W"], EXAMPLES["jisx0213nonbmp.ans"], EXAMPLES["jisx0213nonbmp"])

    def test_jisx0213_needx0213_f(self):
        _assert_conversion(["--oc=EUC-JISX0213", "-W"], EXAMPLES["jisx0213needx0213_f"], EXAMPLES["jisx0213needx0213_f.ans"])

    def test_ibmext_x0213_to_utf8(self):
        _assert_conversion(["--ic=Shift_JISX0213", "-w"], EXAMPLES["shift_jisx0213conflict_ibmext"], EXAMPLES["shift_jisx0213conflict_ibmext.x0213utf8"])

    def test_ibmext_cp932_to_utf8(self):
        _assert_conversion(["--ic=CP932", "-w"], EXAMPLES["shift_jisx0213conflict_ibmext"], EXAMPLES["shift_jisx0213conflict_ibmext.cp932utf8"])


def test_normal_ucs_map():
    _assert_conversion(["--ic=Shift_JIS", "-w16B0"], EXAMPLES["ms_ucs_map_1_sjis"], EXAMPLES["ms_ucs_map_1_utf16"])


def test_cp932_to_utf16be():
    _assert_conversion(["--ic=CP932", "--oc=UTF-16BE"], EXAMPLES["ms_ucs_map_1_sjis"], EXAMPLES["ms_ucs_map_1_utf16_ms"])


class TestX0201:
    """Tests for X0201 kana conversion."""

    def test_x0201_sjis_jXZ(self):
        _assert_conversion("-jXZ", EXAMPLES["x0201.sjis"], EXAMPLES["x0201.x0208"])

    def test_x0201_jis_jZ(self):
        _assert_conversion("-jZ", EXAMPLES["x0201.jis"], EXAMPLES["x0201.x0208"])

    def test_x0201_sosi_jZ(self):
        _assert_conversion("-jZ", EXAMPLES["x0201.sosi"], EXAMPLES["x0201.x0208"])

    def test_x0201_euc_jZ(self):
        _assert_conversion("-jZ", EXAMPLES["x0201.euc"], EXAMPLES["x0201.x0208"])

    def test_x0201_utf_jZ(self):
        _assert_conversion("-jZ", EXAMPLES["x0201.utf"], EXAMPLES["x0201.x0208"])

    def test_x0201_xs(self):
        _assert_conversion("-xs", EXAMPLES["x0201.euc"], EXAMPLES["x0201.sjis"])

    def test_x0201_xj(self):
        _assert_conversion("-xj", EXAMPLES["x0201.euc"], EXAMPLES["x0201.jis"])

    def test_x0201_xe(self):
        _assert_conversion("-xe", EXAMPLES["x0201.euc"], EXAMPLES["x0201.euc"])

    def test_x0201_xw(self):
        _assert_conversion("-xw", EXAMPLES["x0201.euc"], EXAMPLES["x0201.utf"])


class TestMIMEUpstream:
    """MIME encoding/decoding tests from upstream."""

    def test_mime_is8859(self):
        _assert_conversion("-jml", EXAMPLES["mime.is8859"], EXAMPLES["mime.is8859.ans"])

    def test_mime_output(self):
        _assert_conversion("-jM", EXAMPLES["mime_out"],
                           EXAMPLES["mime_out.ans"], EXAMPLES["mime_out.ans.alt"],
                           EXAMPLES["mime_out.ans.alt2"], EXAMPLES["mime_out.ans.alt3"])

    def test_mime_qencode_softrap(self):
        _assert_conversion("-jmQ", EXAMPLES["q_encode_softrap"], EXAMPLES["q_encode_softrap.ans"])


class TestBugFixUpstream:
    """Bug fix regression tests from upstream."""

    def test_cr(self):
        _assert_conversion("-jd", EXAMPLES["cr"], EXAMPLES["cr.ans"])

    def test_nkf19_2(self):
        _assert_conversion("-e", EXAMPLES["nkf_19_bug_2"], EXAMPLES["nkf_19_bug_2.ans"])

    def test_nkf19_3(self):
        _assert_conversion("-e", EXAMPLES["nkf_19_bug_3"], EXAMPLES["nkf_19_bug_3.ans"])

    def test_non_strict_mime(self):
        _assert_conversion("-jmN", EXAMPLES["non_strict_mime"], EXAMPLES["non_strict_mime.ans"])

    def test_z4_euc(self):
        _assert_conversion(["-e", "-Z4"], EXAMPLES["_Z4"], EXAMPLES["_Z4.ans"])

    def test_rot13(self):
        _assert_conversion("-jr", EXAMPLES["rot13"], EXAMPLES["rot13.ans"])

    def test_slash(self):
        _assert_conversion("-j", EXAMPLES["slash"], EXAMPLES["slash.ans"])

    def test_fixed_qencode(self):
        _assert_conversion("-jmQ", EXAMPLES["fixed_qencode"], EXAMPLES["fixed_qencode.ans"])

    def test_bug19779(self):
        _assert_conversion("-jM", EXAMPLES["bug19779"], EXAMPLES["bug19779.ans"])


class TestNewlineUpstream:
    """Newline conversion tests from upstream nkf_test.pl."""

    _P1 = b"\x1b$B$\"$$$&$($*\x1b(B"
    _P2 = b"\x1b$B$+$-$/$1$3\x1b(B"
    _P3 = b"\x1b$B$5$7$9$;$=\x1b(B"

    _INPUTS = [
        _P1 + b"\n" + _P2 + b"\n" + _P3 + b"\n",
        _P1 + b"\r" + _P2 + b"\r" + _P3 + b"\r",
        _P1 + b"\r\n" + _P2 + b"\r\n" + _P3 + b"\r\n",
        _P1 + b"\n" + _P2 + b"\r" + _P3 + b"\r\n",
        _P1 + b"\r" + _P2 + b"\r\n" + _P3 + b"\n",
        _P1 + b"\r\n" + _P2 + b"\n" + _P3 + b"\r",
        _P1 + b"\n" + _P2 + b"\n" + _P3,
        _P1 + b"\r" + _P2 + b"\r" + _P3,
        _P1 + b"\r\n" + _P2 + b"\r\n" + _P3,
        _P1 + b"\n" + _P2 + b"\r" + _P3,
        _P1 + b"\r" + _P2 + b"\r\n" + _P3,
        _P1 + b"\r\n" + _P2 + b"\n" + _P3,
        _P1 + b"\n" + _P2,
        _P1 + b"\r" + _P2,
        _P1 + b"\r\n" + _P2,
        _P1 + b"\n",
        _P1 + b"\r",
        _P1 + b"\r\n",
        _P1,
        b"\n",
        b"\r",
        b"\r\n",
        b"",
    ]

    @staticmethod
    def _expected_nl(data, nl):
        result = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        if nl != b"\n":
            result = result.replace(b"\n", nl)
        return result

    @pytest.mark.parametrize("idx", range(23))
    def test_newline_lu(self, idx):
        """Convert to LF (-jLu)."""
        _assert_conversion("-jLu", self._INPUTS[idx], self._expected_nl(self._INPUTS[idx], b"\n"))

    @pytest.mark.parametrize("idx", range(23))
    def test_newline_lm(self, idx):
        """Convert to CR (-jLm)."""
        _assert_conversion("-jLm", self._INPUTS[idx], self._expected_nl(self._INPUTS[idx], b"\r"))

    @pytest.mark.parametrize("idx", range(23))
    def test_newline_lw(self, idx):
        """Convert to CRLF (-jLw)."""
        _assert_conversion("-jLw", self._INPUTS[idx], self._expected_nl(self._INPUTS[idx], b"\r\n"))


# =========================================================================
# Section H: MIME Tests
# =========================================================================

_MIME_ISO_SRC = _hex(
    "3d3f49534f2d323032322d4a503f423f477952414e4545376569524f4a55596c"
    "4f5356494779684b3f3d0a3d3f69736f2d323032322d4a503f423f477952414e"
    "4545376569524f4a55596c4f5356494779684b3f3d0a3d3f69736f2d32303232"
    "2d4a503f513f3d31422442244624513d314228425f656e643f3d0a1b2100243d"
    "2426242b244a1b284a203d3f49534f2d323032322d4a503f423f477952414e45"
    "45376569524f50796b376468736f53673d3d3f3d20656e64206f66206c696e65"
    "0a3d3f49534f2d323032322d4a503f423f477952414e4545376569524f50796b"
    "376468736f53673d3d3f3d203d3f49534f2d323032322d4a503f423f47795241"
    "4e4545376569524f50796b376468736f53673d3d3f3d0a42726f6b656e206361"
    "73650a3d3f49534f2d323032322d4a503f423f477952414e4545376569524f50"
    "796b37640a68736f53673d3d3f3d203d3f49534f2d32300a32322d4a503f423f"
    "477952414e4545376569524f50796b376468736f53673d3d3f3d0a3d3f49534f"
    "2d323032322d4a503f423f477952414e4545376569524f4a55596c4f1b5b4b53"
    "56494779684b3f3d0a"
)

_MIME_B64_SRC = _hex(
    "67736d542f494c6e67726d43784a4b346771754333498b3367717142515a4f4d"
    "6935364c33343134677357425131304b676d6144566f4f480a67324b44546f4c"
    "776b6232516c494b6f67714b4378498b6767756d42714a4e596773474378494b"
    "6767756d4338594c466772574335594b6b67716d420a"
)

_MIME_8859_SRC = _hex(
    "3d3f49534f2d383835392d313f513f2a3d43376176613f3f3d200a5065657220"
    "54f6726e6772656e0a4c617373652048696c6c6572f86520506574657273656e"
    "20205c20224d696e206b61657068657374206861722066616165742065742066"
    "6f656c21220a41617268757320556e69766572736974792c2044454e4d41524b"
    "20205c20224d696e206be67068657374206861722066e565742065742066f86c"
    "21220a"
)

_MIME_STRICT_EXP = _hex(
    "1b244234413b7a244e2546253925481b28420a1b244234413b7a244e25462539"
    "25481b28420a1b2442244624511b284220656e640a1b2100243d2426242b244a"
    "201b244234413b7a244e3f293b761b284220656e64206f66206c696e650a1b24"
    "4234413b7a244e3f293b7634413b7a244e3f293b761b28420a42726f6b656e20"
    "636173650a3d3f49534f2d323032322d4a503f423f477952414e454537656952"
    "4f50796b37640a68736f53673d3d3f3d203d3f49534f2d32300a32322d4a503f"
    "423f477952414e4545376569524f50796b376468736f53673d3d3f3d0a3d3f49"
    "534f2d323032322d4a503f423f477952414e4545376569524f4a55596c4f1b5b"
    "4b5356494779684b3f3d0a"
)

_MIME_NS_EXP = _hex(
    "1b244234413b7a244e2546253925481b28420a1b244234413b7a244e25462539"
    "25481b28420a1b2442244624511b284220656e640a1b2100243d2426242b244a"
    "201b244234413b7a244e3f293b761b284220656e64206f66206c696e650a1b24"
    "4234413b7a244e3f293b7634413b7a244e3f293b761b28420a42726f6b656e20"
    "636173650a1b244234413b7a244e3f293b7634413b7a244e3f293b761b28420a"
    "1b244234413b7a244e2546253925241b28"
)

_MIME_UNBUF_EXP = _hex(
    "1b244234413b7a244e2546253925481b28420a1b244234413b7a244e25462539"
    "25481b28420a1b2442244624511b284220656e640a1b2100243d2426242b244a"
    "201b244234413b7a244e3f293b761b284220656e64206f66206c696e650a1b24"
    "4234413b7a244e3f293b7634413b7a244e3f293b761b28420a42726f6b656e20"
    "636173650a1b244234413b7a244e3f293b7634413b7a244e3f293b761b28420a"
    "1b244234413b7a244e2546253925241b28"
)

_MIME_B64_EXP = _hex(
    "1b2442244b467e2469243b2446443a242d245e1b2842c11b2442456c357e3661"
    "3959244721241b28425d0a1b24422347253725672543252f2472423f3f74242a"
    "242424461b2842a81b2442244324462422246b24732447243724672426242b1b"
    "28"
)

_MIME_8859_EXP = _hex(
    "2ac76176613f200a506565722054f6726e6772656e0a4c617373652048696c6c"
    "6572f86520506574657273656e20205c20224d696e206b616570686573742068"
    "617220666161657420657420666f656c21220a41617268757320556e69766572"
    "736974792c2044454e4d41524b20205c20224d696e206be67068657374206861"
    "722066e565742065742066f86c21220a"
)


@pytest.mark.parametrize(
    ("options", "source", "expected"),
    [
        pytest.param("-jmS", _MIME_ISO_SRC, _MIME_STRICT_EXP, id="strict"),
        pytest.param("-jmN", _MIME_ISO_SRC, _MIME_NS_EXP, id="nonstrict"),
        pytest.param("-jmNu", _MIME_ISO_SRC, _MIME_UNBUF_EXP, id="unbuf"),
        pytest.param("-jmB", _MIME_B64_SRC, _MIME_B64_EXP, id="base64"),
        pytest.param("-jml", _MIME_8859_SRC, _MIME_8859_EXP, id="iso8859"),
    ],
)
def test_mime_decode(options, source, expected):
    _assert_conversion(options, source, expected)


# =========================================================================
# Section I: Bug Fix Tests
# =========================================================================

@pytest.mark.parametrize(
    ("options", "source", "expected"),
    [
        pytest.param(
            '-jd',
            _hex("a4c6a4b9a4c80d746573740d746573740d"),
            _hex("1b24422446243924481b28420a746573740a746573740a"),
            id="cr",
        ),
        pytest.param(
            '-jmQ',
            _hex("20202020202020203d314224423e653f3d33443d314228420a20202020202020203d314224423e653d33463d33443d314228420a"),
            _hex("20202020202020201b24423e653f3d1b28420a20202020202020201b24423e653f3d1b28420a"),
            id="fixed-qencode",
        ),
        pytest.param(
            '-e',
            _hex("a4caa4aca4a4a4caa4aca4a4a4caa4aca1c1a4a4a4aea4e7a4a6a4aca4a2a4eaa4dea4b7a4c6a1a200a4af94eca4f2a4bda4cea4dea4dea4a2a4c4a4aba4a6a4c8a1a2a4c9a4a6a4e2a4dfa4d0a4a8a4aca4efa4eba4a4a4b7a1a2a4c8a4c1a4e5a4a6a4c7a4c1a4e7a4f3a4aea4eca4eba4aba4e2a4b7a4f3a4caa4a4a1a30aa4b3a4b3a4cfc3bba4a4b9d4a1a3000aa4b3a4b3a4cfc3bba4a4b9d4a1a30a"),
            _hex("a1a2a5cfa1a2a5e3a1a2a1a2a1a2a5cfa1a2a5e3a1a2a1a2a1a2a5cfa1a2a5e3a1a3a5c1a1a2a1a2a1a2a5e7a1a2eea6a5f2a1a2a5e3a1a2a1d6a1a2f4a6a1aba1a2a5ada1a2a5cba1a3a1d600a1a2a5c3c8eea1a2a5b9a1a2a5dba1a2a1aba1a2a1aba1a2a1d6a1a2a5c8a1a2a5a9a1a2a5f2a1a2a5cda1a3a1d6a1a2a5cea1a2a5f2a1a2e4a6a1aca1a2a5dfa1a2a5a3a1a2a5e3a1a2efa4eba4a4a4b7a1a2a4c8a4c1a4e5a4a6a4c7a4c1a4e7a4f3a4aea4eca4eba4aba4e2a4b7a4f3a4caa4a4a1a4b3a4b3a4cfc3bba4a4b9d4a1a3000aa4b3a4b3a4cfc3bba4a4b9d4a1a30a"),
            id="multi-line",
        ),
        pytest.param(
            '-eEZ4',
            _hex("a1a3a1d6a1d7a1a2a1a6a1bca1aba1aca5a1a5a2a5a3a5a4a5a5a5a6a5a7a5a8a4a9a5aaa5aba5aca5ada5aea5afa5b0a5b1a5b2a5b3a5b4a5b5a5b6a5b7a5b8a5b9a5baa5bba5bca5bda5bea5bfa5c0a5c1a5c2a5c3a5c4a5c5a5c6a5c7a5c8a5c9a5caa5cba5cca5cda5cea5cfa5d0a5f1a5d2a5d3a5d4a5d5a5d6a5d7a5d8a5d9a5daa5dba5dca5dda5dea5dfa5e0a5e1a5e2a5e3a5e4a5e5a5e6a5e7a5e8a5e9a5eaa5cfa5eca5eda5edb5f2a5f3a5f4"),
            _hex("8ea18ea28ea38ea48ea58eb08ede8edf8ea78eb18ea88eb28ea98eb38eaa8eb4a4a98eb58eb68eb68ede8eb78eb78ede8eb88eb88ede8eb98eb98ede8eba8eba8ede8ebb8ebb8ede8ebc8ebc8ede8ebd8ebd8ede8ebe8ebe8ede8ebf8ebf8ede8ec08ec08ede8ec18ec18ede8eaf8ec28ec28ede8ec38ec38ede8ec48ec48ede8ec58ec68ec78ec88ec98eca8eca8edea5f18ecb8ecb8ede8ecb8edf8ecc8ecc8ede8ecc8edf8ecd8ecd8ede8ecd8edf8ece8ece8ede8ece8edf8ecf8ed08ed18ed28ed38eac8ed48ead8ed58eae8ed68ed78ed88eca8eda8edb8edbb5f28edd8eb38ede"),
            id="-Z4",
        ),
        pytest.param(
            '-Ej',
            _hex("a4a6a4aba4a40abad8c6a30a"),
            _hex("1b24422426242b24241b28420a1b24423a5846231b28420a"),
            id="nkf-19-bug-1",
        ),
        pytest.param(
            '-Ee',
            _hex("a4dba4b20a"),
            _hex("a4dba4b20a"),
            id="nkf-19-bug-2",
        ),
        pytest.param(
            '-e',
            _hex("edb1f1f0c1ac0ae5baceef0af2ed09bee5cececfcb09090a"),
            _hex("edb1f1f0c1ac0ae5baceef0af2ed09bee5cececfcb09090a"),
            id="nkf-19-bug-3",
        ),
        pytest.param(
            '-jmN',
            _hex("3d3f49534f2d323032322d4a503f423f0a677353436f6f4b39677236436f6f4c45677479437434464344616f4e436f36556773324f6e6f46596734794457494c4a677543d06b590a4b7067726d4378494b6967723243766f4b69677353436f6f4c630a3f3d0a"),
            _hex("1b244224462424243f244024242446245e243921231b28420d1b244225271b28420d0a1b24423b74244f3b7e2139256c2539244b24623171242b243b24462424243f2440242424462424245e1b28420a"),
            id="non-strict-mime",
        ),
        pytest.param(
            '-jmQ',
            _hex("3d3142244234413b7a253d0a33213c2549244e3d314228420a3d314224424a5134393d314228420a"),
            _hex("1b244234413b7a2533213c2549244e1b28420a1b24424a5134391b28420a"),
            id="q-encode-softrap",
        ),
        pytest.param(
            '-jr',
            _hex("a4b3a4f3a4cba4c1a4cfa1a2cdadc2f4a4c8a4a4a4a4a4dea4b9a1a30a0a6e6b26207665722e312e393220a4f2cdf8cdd1a4b5a4bba4c6a4a4a4bfa4c0a4a4a4c6a4a4a4dea4b9a4aca1a2415343498920a4cbc2d0a4b7a4c620524f54313320a4ac0ac0b5a4b7a4afc6b0a4a4a4c6a4a4a4caa4a4a4e064a6a4c7a1a2b0caa2bca4cea4e4a4a6a4cbcad1b4b9a4b6a4eca4dea4bba4e5a1a30a0a25206563686f2027686f676527207c206e6b26202d720a686f67650a"),
            _hex("1b244253625344537a5370537e50517c5c7145537753535353532f536850521b28420a0a617826206972652e312e3932201b244253437c497c225364536a53755353536e536f535353755353532f5368535b50511b28424e4650561b2442537a7121536653751b2842204542473133201b2442535b1b28420a1b24426f645366535e755f5353537553535379535353311b2842711b244255537650515f79516b537d53355355537a792263685365533d532f536a5336501b28420a25207270756220277562747227207c20617826202d650a756274720a"),
            id="rot13",
        ),
        pytest.param(
            '-j',
            _hex("20203d3f563c542d553957454b2d2b3b57354d2b252f0a"),
            _hex("20203d3f563c542d553957454b2d2b3b57354d2b252f0a"),
            id="slash",
        ),
        pytest.param(
            ['-e', '-Z'],
            _hex("a1a1"),
            _hex("a1a1"),
            id="z1space-0",
        ),
        pytest.param(
            ['-e', '-Z1'],
            _hex("a1a1"),
            _hex("20"),
            id="z1space-1",
        ),
        pytest.param(
            ['-e', '-Z2'],
            _hex("a1a1"),
            _hex("2020"),
            id="z1space-2",
        ),
        pytest.param(
            '-e',
            _hex("3d3f69736f2d323032322d6a703f713f3d39363d41323d38463d42333d38313d46383b38444c3d38443d39303d38313d41360a687474703a2f2f6578616d706c652e636f6d2f3f6f70653d73656c0a687474703a2f2f65786d61706c652e6a702f0a2e2e2e0a"),
            _hex("cca4beb5a2fa3b38444cb9f0a2a80a687474703a2f2f6578616d706c652e636f6d2f3f6f70653d73656c0a687474703a2f2f65786d61706c652e6a702f0a2e2e2e0a"),
            id="bug2273",
        ),
    ],
)
def test_bugfix(options, source, expected):
    _assert_conversion(options, source, expected)


def test_bugfix_q_encode_utf8():
    source = (
        b"=?utf-8?Q?=E3=81=82=E3=81=84=E3=81=86=E3=81=88=E3=81=8A?=\n"
        b"=?utf-8?Q?=E3=81=8B=E3=81=8D=E3=81=8F=E3=81=91=E3=81=93?=\n"
    )
    expected = (
        b"\xE3\x81\x82\xE3\x81\x84\xE3\x81\x86\xE3\x81\x88\xE3\x81\x8A\n"
        b"\xE3\x81\x8B\xE3\x81\x8D\xE3\x81\x8F\xE3\x81\x91\xE3\x81\x93\n"
    )
    _assert_conversion("-w", source, expected)


@pytest.mark.parametrize(
    ("options", "source", "expected"),
    [
        pytest.param(
            ["--ic=UTF-8", "--oc=CP932"],
            b"\xEF\xBD\xBC\xEF\xBE\x9E\xEF\xBD\xAC\xEF\xBD\xB0"
            b"\xEF\xBE\x8F\xEF\xBE\x9D\xEF\xBD\xA5\xEF\xBE\x8E"
            b"\xEF\xBE\x9F\xEF\xBE\x83\xEF\xBE\x84\xEF\xBD\xA1",
            b"\xBC\xDE\xAC\xB0\xCF\xDD\xA5\xCE\xDF\xC3\xC4\xA1",
            id="nkf-bug-21393-x",
        ),
        pytest.param(
            ["--ic=UTF-8", "--oc=CP932", "-X"],
            b"\xEF\xBD\xBC\xEF\xBE\x9E\xEF\xBD\xAC\xEF\xBD\xB0"
            b"\xEF\xBE\x8F\xEF\xBE\x9D\xEF\xBD\xA5\xEF\xBE\x8E"
            b"\xEF\xBE\x9F\xEF\xBE\x83\xEF\xBE\x84\xEF\xBD\xA1",
            b"\x83W\x83\x83\x81[\x83}\x83\x93\x81E\x83|\x83e\x83g\x81B",
            id="nkf-bug-21393-X",
        ),
        pytest.param("-Sw", b"\x1b\x82\xa0", b"\x1b\xe3\x81\x82", id="nkf-bug-32328-SJIS"),
        pytest.param("-Jw", b"\x1b\x1b$B$\x22\x1b(B", b"\x1b\xe3\x81\x82", id="nkf-bug-32328-JIS"),
        pytest.param(
            ["-sW", "--fb-html"],
            b"\xe6\xbf\xb9\xe4\xb8\x8a",
            b"&#28665;\x8f\xe3",
            id="nkf-bug-36572",
        ),
        pytest.param(
            ["--ic=CP50221", "--oc=CP932"],
            b"\x1b\x24\x42\x7f\x21\x80\x21\x1b\x28\x42\n",
            b"\xf0\x40\xf0\x9f\x0a",
            id="nkf-forum-65482",
        ),
        pytest.param(
            ["-W", "-e", "--fb-java"],
            b"\xF0\xA0\xAE\xB7",
            b"\\uD842\\uDFB7",
            id="nkf-bug-38800",
        ),
    ],
)
def test_bugfix_inline(options, source, expected):
    _assert_conversion(options, source, expected)


# =========================================================================
# Section J: Newline Conversion Tests
# =========================================================================


_NL_TO_LF_CASES = [
    (b"none", b"none"),
    (b"\n", b"\n"),
    (b"\n\n", b"\n\n"),
    (b"\n\r", b"\n\n"),
    (b"\n\r\n", b"\n\n"),
    (b"\n.\n", b"\n.\n"),
    (b"\n.\r", b"\n.\n"),
    (b"\n.\r\n", b"\n.\n"),
    (b"\r", b"\n"),
    (b"\r\r", b"\n\n"),
    (b"\r\r\n", b"\n\n"),
    (b"\r.\n", b"\n.\n"),
    (b"\r.\r", b"\n.\n"),
    (b"\r.\r\n", b"\n.\n"),
    (b"\r\n", b"\n"),
    (b"\r\n\n", b"\n\n"),
    (b"\r\n\r", b"\n\n"),
    (b"\r\n\r\n", b"\n\n"),
    (b"\r\n.\n", b"\n.\n"),
    (b"\r\n.\r", b"\n.\n"),
    (b"\r\n.\r\n", b"\n.\n"),
]


@pytest.mark.parametrize(("source", "expected"), _NL_TO_LF_CASES)
def test_newline_to_lf(source, expected):
    _assert_conversion("-jLu", source, expected)


_NL_TO_CR_CASES = [
    (b"none", b"none"),
    (b"\n", b"\r"),
    (b"\n\n", b"\r\r"),
    (b"\n\r", b"\r\r"),
    (b"\n\r\n", b"\r\r"),
    (b"\n.\n", b"\r.\r"),
    (b"\n.\r", b"\r.\r"),
    (b"\n.\r\n", b"\r.\r"),
    (b"\r", b"\r"),
    (b"\r\r", b"\r\r"),
    (b"\r\r\n", b"\r\r"),
    (b"\r.\n", b"\r.\r"),
    (b"\r.\r", b"\r.\r"),
    (b"\r.\r\n", b"\r.\r"),
    (b"\r\n", b"\r"),
    (b"\r\n\n", b"\r\r"),
    (b"\r\n\r", b"\r\r"),
    (b"\r\n\r\n", b"\r\r"),
    (b"\r\n.\n", b"\r.\r"),
    (b"\r\n.\r", b"\r.\r"),
    (b"\r\n.\r\n", b"\r.\r"),
]


@pytest.mark.parametrize(("source", "expected"), _NL_TO_CR_CASES)
def test_newline_to_cr(source, expected):
    _assert_conversion("-jLm", source, expected)


_NL_TO_CRLF_CASES = [
    (b"none", b"none"),
    (b"\n", b"\r\n"),
    (b"\n\n", b"\r\n\r\n"),
    (b"\n\r", b"\r\n\r\n"),
    (b"\n\r\n", b"\r\n\r\n"),
    (b"\n.\n", b"\r\n.\r\n"),
    (b"\n.\r", b"\r\n.\r\n"),
    (b"\n.\r\n", b"\r\n.\r\n"),
    (b"\r", b"\r\n"),
    (b"\r\r", b"\r\n\r\n"),
    (b"\r\r\n", b"\r\n\r\n"),
    (b"\r.\n", b"\r\n.\r\n"),
    (b"\r.\r", b"\r\n.\r\n"),
    (b"\r.\r\n", b"\r\n.\r\n"),
    (b"\r\n", b"\r\n"),
    (b"\r\n\n", b"\r\n\r\n"),
    (b"\r\n\r", b"\r\n\r\n"),
    (b"\r\n\r\r\n", b"\r\n\r\n\r\n"),
    (b"\r\n.\n", b"\r\n.\r\n"),
    (b"\r\n.\r", b"\r\n.\r\n"),
    (b"\r\n.\r\n", b"\r\n.\r\n"),
]


@pytest.mark.parametrize(("source", "expected"), _NL_TO_CRLF_CASES)
def test_newline_to_crlf(source, expected):
    _assert_conversion("-jLw", source, expected)
