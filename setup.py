#!/usr/bin/env python

from distutils.core import setup, Extension

setup (name = "nkf",
       version="0.1.0",
       description="Python Interface to NKF",
       author="SATOH Fumiyasu",
       author_email="fumiyas@sfo.jp",
       url="https://github.com/fumiyas/python-nkf",
       py_modules = ["japanesenkf"],
       ext_modules = [Extension("nkf", ["nkf.c"])],
       )
