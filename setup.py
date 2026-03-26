#!/usr/bin/env python3

from setuptools import Extension, setup


setup(
    ext_modules=[
        Extension(
            "nkf._nkf",
            sources=[
                "ext/NKF_python.c",
            ],
        )
    ],
)
