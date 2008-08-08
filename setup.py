#!/usr/bin/env python
import os
from setuptools import setup, find_packages

from eazysvn import ALIASES, VERSION

readme = os.path.join(os.path.dirname(__file__), 'README.txt')
changelog = os.path.join(os.path.dirname(__file__), 'CHANGES.txt')

changes_in_last_version = file(changelog).read().split('\n\n\n')[1]

long_description = file(readme).read().replace('See CHANGES.txt',
                                               changes_in_last_version)


setup(
    name='eazysvn',
    version=VERSION,
    author='Philipp von Weitershausen',
    author_email='philipp@weitershausen.de',
    maintainer='Marius Gedminas',
    maintainer_email='marius@gedmin.as',
    url='http://mg.pov.lt/eazysvn/',
    download_url='http://pypi.python.org/pypi/eazysvn',
    description='Make simple revision merges and branch switching much easier',
    long_description=long_description,
    license='GPL',

    py_modules=['eazysvn'],
    zip_safe=False,
    entry_points="""
    [console_scripts]
    eazysvn = eazysvn:main
    """ + '\n'.join('%s = eazysvn:main' % alias for alias in ALIASES),
    test_suite='eazysvn',
)
