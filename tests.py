import os
import shutil
import subprocess
import tempfile
import urllib
from collections import namedtuple
from contextlib import contextmanager

import pytest

import eazysvn as es


@contextmanager
def tempdir():
    dirname = tempfile.mkdtemp(prefix='eazysvn-', suffix='-test')
    try:
        yield dirname
    finally:
        shutil.rmtree(dirname)


@contextmanager
def chdir(dirname):
    olddirname = os.getcwd()
    try:
        os.chdir(dirname)
        yield
    finally:
        os.chdir(olddirname)


SVNRepo = namedtuple('SVNRepo', 'url, path')


@pytest.yield_fixture
def svnrepo(name='repo'):
    with tempdir() as dirname:
        path = os.path.join(dirname, name)
        subprocess.call(['svnadmin', 'create', path])
        url = 'file://' + urllib.pathname2url(os.path.abspath(path))
        yield SVNRepo(path=path, url=url)


SVNCheckout = namedtuple('SVNCheckout', 'path, repo')


@pytest.yield_fixture
def svncheckout(svnrepo):
    with tempdir() as dirname:
        subprocess.call(['svn', 'co', svnrepo.url, dirname])
        with chdir(dirname):
            yield SVNCheckout(path=dirname, repo=svnrepo)


def test_svninfo(svncheckout):
    stdout = es.svninfo('.')
    assert 'URL: %s' % svncheckout.repo.url in stdout.splitlines()


def test_svnls(svncheckout):
    stdout = es.svnls('.')
    assert stdout == ''


def test_svnlog(svncheckout):
    stdout = es.svnlog('.')
    assert stdout.startswith('<?xml')


def test_ezmerge_list(svncheckout, capsys):
    es.ezmerge(['ezmerge', '-l'])
    out, err = capsys.readouterr()
    assert out == '\n'


def test_ezmerge_list_tags(svncheckout, capsys):
    es.ezmerge(['ezmerge', '-l', '-t'])
    out, err = capsys.readouterr()
    assert out == '\n'


def test_ezmerge_too_few_args(svncheckout, capsys):
    with pytest.raises(SystemExit):
        es.ezmerge(['ezmerge'])
    out, err = capsys.readouterr()
    assert 'too few arguments' in err


def test_eazysvn_selftest(capsys):
    es.selftest(['eazysvn', 'selftest'])
    out, err = capsys.readouterr()
    assert out.startswith('All') and out.endswith('tests passed.\n')


def test_eazysvn_help(capsys):
    es.help(['eazysvn', 'help'])
    out, err = capsys.readouterr()
    assert out.startswith('usage: eazysvn command arguments')
