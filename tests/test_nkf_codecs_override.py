#!/usr/bin/env python3
## -*- coding: utf-8 -*- vim:shiftwidth=4:expandtab:

def test_nkf():
    import nkf.codecs
    import codecs
    import io

    nkf.codecs.overrideEncodings()

    # ASCII
    unicoded = u'abc ABC'
    # Kanji, Hiragana
    unicoded += u' 阿異雨あいう'
    # Katakana (JIS X 0201)
    unicoded += u' アイウｱｲｳ'
    # NEC specials, IBM extended
    unicoded += u' ①ⅰⅠ㈱〜'
    # MIME header encoded
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
        'ujis',
        'u_jis',
        'u-jis',
        'shift_jis',
        'shift-jis',
        'shiftjis',
        'sjis',
        's-jis',
    ]

    for encoding in encoding_list:
        encoded = unicoded.encode(encoding)

        text = (encoded + b'\n') * 17
        text_unicoded = text.decode(encoding)
        encoder, decoder, reader, writer = codecs.lookup(encoding)
        for func_name in ['read', 'readline', 'readlines']:
            for size in [None, -1] + list(range(1, 33)) + [64, 128, 256, 512, 1024]:
                istream = reader(io.BytesIO(text))
                ostream = writer(io.BytesIO())
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
