#!/usr/bin/env python

from distutils.core import setup, Extension

setup (name = "nkf",
       version="0.1.1",
       description="Python Interface to NKF",
       author="SATOH Fumiyasu",
       author_email="fumiyas@osstech.jp",
       url="https://github.com/fumiyas/python-nkf",
       license="BSD",
       py_modules = ["nkf_codecs"],
       ext_modules = [Extension("nkf", ["nkf.c"])],
       )
