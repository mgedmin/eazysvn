#!/usr/bin/env python
import os, sys
from setuptools import setup, find_packages

from eazysvn import ALIASES, VERSION

readme = os.path.join(os.path.dirname(__file__), 'README.rst')
changelog = os.path.join(os.path.dirname(__file__), 'CHANGES.rst')

changes_in_all_versions = file(changelog).read().split('\n\n\n', 1)[1]

long_description = file(readme).read().replace('See CHANGES.rst',
                                               changes_in_all_versions)

first_changelog_line = changes_in_all_versions.lstrip().split('\n', 1)[0]

version_indicates_unreleased = VERSION.endswith('dev')
changelog_indicates_unreleased = first_changelog_line.endswith('(unreleased)')
version_in_version = VERSION.rstrip('dev')
version_in_changelog = first_changelog_line.split()[0]

if (version_in_version != version_in_changelog or
    version_indicates_unreleased != changelog_indicates_unreleased):
    print >> sys.stderr, "VERSION is %s, but last changelog entry is for %s" % (
                            VERSION, first_changelog_line)

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
