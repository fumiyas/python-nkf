## Override Japanese codecs by NKF codecs (if available) to
## treat invalid encoded Japanese messages from bogus MUAs.
try:
    import japanesenkf
    japanesenkf.overrideEncodings()
except:
    pass
