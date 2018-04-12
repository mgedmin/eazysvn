#!/usr/bin/env python
import os
import sys
from setuptools import setup

from eazysvn import ALIASES, __version__

readme = os.path.join(os.path.dirname(__file__), 'README.rst')
changelog = os.path.join(os.path.dirname(__file__), 'CHANGES.rst')

with open(changelog) as f:
    changes_in_all_versions = f.read().split('\n\n\n', 1)[1]

with open(readme) as f:
    long_description = f.read().replace('See CHANGES.rst',
                                        changes_in_all_versions)

first_changelog_line = changes_in_all_versions.lstrip().split('\n', 1)[0]

version_indicates_unreleased = 'dev' in __version__
changelog_indicates_unreleased = first_changelog_line.endswith('(unreleased)')
version_in_version = __version__.split('dev')[0].rstrip('.')
version_in_changelog = first_changelog_line.split()[0]

if (version_in_version != version_in_changelog or
        version_indicates_unreleased != changelog_indicates_unreleased):
    sys.exit("__version__ is %s, but last changelog entry is for %s"
             % (__version__, first_changelog_line))

setup(
    name='eazysvn',
    version=__version__,
    author='Philipp von Weitershausen',
    author_email='philipp@weitershausen.de',
    maintainer='Marius Gedminas',
    maintainer_email='marius@gedmin.as',
    url='https://mg.pov.lt/eazysvn/',
    project_urls={
        'Source': 'https://github.com/mgedmin/eazysvn',
    },
    description='Make simple revision merges and branch switching much easier',
    long_description=long_description,
    license='GPL',
    keywords='svn subversion wrapper',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Version Control',
    ],

    py_modules=['eazysvn'],
    zip_safe=False,
    entry_points=dict(
        console_scripts=[
            '%s = eazysvn:main' % alias
            for alias in ['eazysvn'] + list(ALIASES)
        ],
    ),
    test_suite='eazysvn',
)
