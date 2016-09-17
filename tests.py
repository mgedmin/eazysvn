import os
import shutil
import subprocess
import tempfile
from collections import namedtuple
from contextlib import contextmanager

try:
    from urllib.request import pathname2url     # Python 3
except:
    from urllib import pathname2url             # Python 2

import mock
import pytest

import eazysvn as es


@contextmanager
def tempdir():
    dirname = tempfile.mkdtemp(prefix='eazysvn-', suffix='-test')
    try:
        yield dirname
    finally:
        rmtree(dirname)


def rmtree(path):
    """A version of rmtree that can remove read-only files on Windows.

    Needed because the stock shutil.rmtree() fails with an access error
    when there are read-only files in the directory.
    """
    def onerror(func, path, exc_info):
        if func is os.remove or func is os.unlink:  # pragma: nocover
            # Did you know what on Python 3.3 on Windows os.remove() and
            # os.unlink() are distinct functions?
            os.chmod(path, 0o644)
            func(path)
        else:
            raise
    shutil.rmtree(path, onerror=onerror)


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
        url = pathname2url(os.path.abspath(path))
        if not url.startswith('///'):  # linux vs windows
            url = '//' + url
        url = 'file:' + url
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


def test_eztag_list(svncheckout, capsys):
    es.eztag(['eztag', '-l'])
    out, err = capsys.readouterr()
    assert out == '\n'


def test_ezswitch_current_branch(svncheckout, capsys):
    es.ezswitch(['ezswitch'])
    out, err = capsys.readouterr()
    assert out.endswith('/repo\n')


@pytest.mark.parametrize('command', [
    'ezmerge', 'ezrevert', 'eztag', 'rmbranch', 'mvbranch',
])
def test_too_few_args(command, capsys):
    with pytest.raises(SystemExit):
        getattr(es, command)([command])
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
    ('eazysvn --help', 'usage: eazysvn command arguments'),
])
def test_main(capsys, command, expected):
    with mock.patch('sys.argv', command.split()):
        with pytest.raises(SystemExit):
            es.main()
    out, err = capsys.readouterr()
    assert expected in out


def test_additional_tests():
    assert es.additional_tests().countTestCases() > 0
