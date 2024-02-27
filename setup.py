#!/usr/bin/env python3

from setuptools import setup, Extension

# Support for Reproducible Builds
# https://reproducible-builds.org/docs/source-date-epoch/
# https://github.com/pypa/setuptools/issues/2133#issuecomment-1691158410

import os

timestamp = os.environ.get('SOURCE_DATE_EPOCH')
if timestamp is not None:
    import distutils.archive_util as archive_util
    import stat
    import tarfile
    import time

    timestamp = float(max(int(timestamp), 0))

    class Time:
        @staticmethod
        def time():
            return timestamp

        @staticmethod
        def localtime(_=None):
            return time.localtime(timestamp)

    class TarInfoMode:
        def __get__(self, obj, objtype=None):
            return obj._mode

        def __set__(self, obj, stmd):
            ifmt = stat.S_IFMT(stmd)
            mode = stat.S_IMODE(stmd) & 0o7755
            obj._mode = ifmt | mode

    class TarInfoAttr:
        def __init__(self, value):
            self.value = value

        def __get__(self, obj, objtype=None):
            return self.value

        def __set__(self, obj, value):
            pass

    class TarInfo(tarfile.TarInfo):
        mode = TarInfoMode()
        mtime = TarInfoAttr(timestamp)
        uid = TarInfoAttr(0)
        gid = TarInfoAttr(0)
        uname = TarInfoAttr('')
        gname = TarInfoAttr('')

    def make_tarball(*args, **kwargs):
        tarinfo_orig = tarfile.TarFile.tarinfo
        try:
            tarfile.time = Time()
            tarfile.TarFile.tarinfo = TarInfo
            return archive_util.make_tarball(*args, **kwargs)
        finally:
            tarfile.time = time
            tarfile.TarFile.tarinfo = tarinfo_orig

    archive_util.ARCHIVE_FORMATS['gztar'] = (
        make_tarball, *archive_util.ARCHIVE_FORMATS['gztar'][1:],
    )

setup(
    name="nkf",
    version="1.0.1",
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
