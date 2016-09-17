import os
import shutil
import subprocess
import tempfile
import urllib
from collections import namedtuple
from contextlib import contextmanager

import mock
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


@pytest.mark.parametrize('command', [
    'ezmerge', 'ezswitch', 'ezbranch', 'rmbranch', 'mvbranch',
    'branchdiff', 'branchpoint',
])
def test_list_branches(command, svncheckout, capsys):
    getattr(es, command)([command, '-l'])
    out, err = capsys.readouterr()
    assert out == '\n'


@pytest.mark.parametrize('command', [
    'ezmerge', 'ezswitch', 'ezbranch',
])
def test_list_tags(command, svncheckout, capsys):
    getattr(es, command)([command, '-l', '-t'])
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


def test_eazysvn_unknown_command():
    with pytest.raises(SystemExit, message="Unknown command: blargh."):
        es.eazysvn(['eazysvn', 'blargh'])


@pytest.mark.parametrize(('command', 'expected'), [
    ('ezmerge --help', 'merge changes'),
    ('eazysvn merge --help', 'merge changes'),
    ('eazysvn mvbranch --help', 'Rename a Subversion branch'),
    ('eazysvn --version', 'eazysvn version'),
    ('ezswitch --version', 'eazysvn version'),
])
def test_main(capsys, command, expected):
    with mock.patch('sys.argv', command.split()):
        with pytest.raises(SystemExit):
            es.main()
    out, err = capsys.readouterr()
    assert expected in out


def test_additional_tests():
    assert es.additional_tests().countTestCases() > 0
