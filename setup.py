#!/usr/bin/env python3

from setuptools import setup, Extension

setup(
    name="nkf",
    version="1.0.0",
    description="Python Interface to NKF",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author="SATOH Fumiyasu",
    author_email="fumiyas@osstech.co.jp",
    url="https://github.com/fumiyas/python-nkf",
    license="BSD",
    py_modules=["nkf_codecs"],
    ext_modules=[Extension("nkf", ["nkf.c"])],
)
