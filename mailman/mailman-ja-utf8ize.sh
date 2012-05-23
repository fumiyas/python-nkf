#!/bin/sh
##
## Mailman の日本語向けエンコーディングを UTF-8 にするハック
##
## Mailman の既定では日本語を EUC-JP で処理するが、これでは
## 当然 JIS X 0213 や Unicode の文字を扱えないので UTF-8 化。
## Mailman ソースツリーでビルド前に実行すること。
##
## Pytyon-NKF と同梱の Mailman 向けパッチと設定も入れると完璧。
## https://github.com/fumiyas/python-nkf

## FIXME: Python で書き直したい。

perl -pi.UTF-8~ -MEncode \
  -e 'Encode::from_to($_, "EUC-JP", "UTF-8");' \
  -e 's/EUC-JP/UTF-8/;' \
  messages/ja/LC_MESSAGES/mailman.po
perl -pi.UTF-8~ -MEncode \
  -e 'Encode::from_to($_, "EUC-JP", "UTF-8");' \
  messages/ja/README.ja \
  templates/ja/*.{txt,html}
perl -pi.UTF-8~ \
  -e 's/euc-jp/utf-8/;' \
  Mailman/Defaults.py.in

