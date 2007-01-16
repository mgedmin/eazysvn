from setuptools import setup, find_packages

setup(
    name='easysvn',
    version='1.2',
    author='Philipp von Weitershausen',
    author_email='philipp@weitershausen.de',
    maintainer='Marius Gedminas',
    maintainer_email='mgedmin@b4net.lt',
    url='http://mg.pov.lt/eazysvn/',
    download_url='http://mg.pov.lt/eazysvn/svn/#egg=easysvn-dev',
    description='Make simple revision merges and branch switching much easier',
    license='GPL',

    packages=find_packages('.'),
    zip_safe=False,
    entry_points="""
    [console_scripts]
    ezmerge = ezmerge:main
    ezswitch = ezmerge:main
    """,
)
