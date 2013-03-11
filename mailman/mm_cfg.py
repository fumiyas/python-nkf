## Override Japanese codecs by NKF codecs (if available) to
## treat invalid encoded Japanese messages from bogus MUAs.
## NOTE: mailman-no-load-iso2022jp.patch required
try:
    import nkf_codecs
    nkf_codecs.overrideEncodings()
except:
    pass

