#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='eazysvn',
    version='1.7.0',
    author='Philipp von Weitershausen',
    author_email='philipp@weitershausen.de',
    maintainer='Marius Gedminas',
    maintainer_email='marius@gedmin.as',
    url='http://mg.pov.lt/eazysvn/',
    download_url='http://mg.pov.lt/eazysvn/svn/#egg=eazysvn-dev',
    description='Make simple revision merges and branch switching much easier',
    license='GPL',

    py_modules=['eazysvn'],
    zip_safe=False,
    entry_points="""
    [console_scripts]
    eazysvn = eazysvn:main
    ezmerge = eazysvn:main
    ezswitch = eazysvn:main
    ezbranch = eazysvn:main
    ezrevert = eazysvn:main
    """,
)
