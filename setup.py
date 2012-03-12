#!/usr/bin/env python

from distutils.core import setup, Extension

setup (name = "nkf",
       version="1.0",
       description="Python Interface to NKF",
       author="SATOH Fumiyasu",
       author_email="fumiyas@sfo.jp",
       ext_modules = [
               Extension("nkf", ["nkf.c"],
                         extra_link_args = ['-s'])])
