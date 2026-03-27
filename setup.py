#!/usr/bin/env python3

from setuptools import Extension, setup


setup(
    ext_modules=[
        Extension(
            "nkf._nkf",
            sources=[
                "ext/NKF_python.c",
                "ext/nkf/nkf.c",
                "ext/nkf/utf8tbl.c",
            ],
            include_dirs=[
                "ext",
                "ext/nkf",
            ],
        )
    ],
)
