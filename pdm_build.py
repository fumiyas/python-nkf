#!/usr/bin/env python3

from setuptools import Extension

ext_modules = [
    Extension(
        "nkf._nkf",
        sources=[
            "ext/NKF_python.c",
        ]
    )
]


def pdm_build_update_setup_kwargs(context, setup_kwargs):
    setup_kwargs.update(ext_modules=ext_modules)
