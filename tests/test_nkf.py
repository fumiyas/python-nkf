#!/usr/bin/env python3
## -*- coding: utf-8 -*- vim:shiftwidth=4:expandtab:

import binascii

import nkf
import pytest


def _uudecode_block(block):
    return b"".join(
        binascii.a2b_uu((line + "\n").encode("ascii"))
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


class TestBufferProtocol:
    """Test that nkf() and guess() accept buffer protocol objects."""

    _sjis_data = EXAMPLES["sjis"]

    def test_nkf_bytes(self):
        result = nkf.nkf("-j", self._sjis_data)
        assert isinstance(result, bytes)
        assert result == EXAMPLES["jis"]

    def test_nkf_bytearray(self):
        result = nkf.nkf("-j", bytearray(self._sjis_data))
        assert isinstance(result, bytes)
        assert result == EXAMPLES["jis"]

    def test_nkf_memoryview(self):
        result = nkf.nkf("-j", memoryview(self._sjis_data))
        assert isinstance(result, bytes)
        assert result == EXAMPLES["jis"]

    def test_nkf_rejects_str(self):
        with pytest.raises(TypeError):
            nkf.nkf("-e", "hello")

    def test_guess_bytes(self):
        assert nkf.guess(self._sjis_data) == "Shift_JIS"

    def test_guess_bytearray(self):
        assert nkf.guess(bytearray(self._sjis_data)) == "Shift_JIS"

    def test_guess_memoryview(self):
        assert nkf.guess(memoryview(self._sjis_data)) == "Shift_JIS"

    def test_guess_rejects_str(self):
        with pytest.raises(TypeError):
            nkf.guess("hello")
