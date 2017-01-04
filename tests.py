import os
import shutil
import subprocess
import tempfile
import textwrap
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


def make_svninfo(url):
    def _svninfo(path):
        return textwrap.dedent('''\
            Path: .
            URL: %s
            Repository UUID: ab69c8a2-bfcb-0310-9bff-acb20127a769
            Revision: 1654
            Node Kind: directory
        ''') % url
    return _svninfo


def make_svnlog():
    def _svnlog(path):
        return textwrap.dedent('''\
            <?xml version="1.0" encoding="utf-8"?>
            <log>
              <logentry revision="4515">
                <author>mg</author>
                <date>2007-01-11T16:30:07.775378Z</date>
                <msg>Blah blah.</msg>
              </logentry>
              <logentry revision="4504">
                <author>mg</author>
                <date>2007-01-11T16:29:32.166370Z</date>
                <msg>create branch</msg>
              </logentry>
            </log>
        ''')
    return _svnlog


@pytest.mark.parametrize(['expected', 'svninfo_stdout'], [
    ('http://dev.worldcookery.com/svn/bla/trunk/blergh',
     textwrap.dedent('''\
      Path: .
      URL: http://dev.worldcookery.com/svn/bla/trunk/blergh
      Repository UUID: ab69c8a2-bfcb-0310-9bff-acb20127a769
      Revision: 1654
      Node Kind: directory
      ''')),
    ('http://dev.worldcookery.com/svn/bla/branches/foobar/blergh',
     textwrap.dedent('''\
      Path: .
      Working Copy Root Path: /home/mg/src/blugh
      URL: http://dev.worldcookery.com/svn/bla/branches/foobar/blergh
      Repository UUID: ab69c8a2-bfcb-0310-9bff-acb20127a769
      Revision: 1654
      Node Kind: directory
      ''')),
])
def test_currentbranch(expected, svninfo_stdout):
    url = es.currentbranch('.', _svninfo=lambda path: svninfo_stdout)
    assert url == expected


@pytest.mark.parametrize(['current_url', 'new_branch', 'expected_url'], [
    ('http://dev.worldcookery.com/svn/bla/trunk/blergh',
     'foobar',
     'http://dev.worldcookery.com/svn/bla/branches/foobar/blergh'),
    ('http://dev.worldcookery.com/svn/bla/trunk/blergh',
     'trunk',
     'http://dev.worldcookery.com/svn/bla/trunk/blergh'),
    ('http://dev.worldcookery.com/svn/bla/branches/foobar/blergh',
     'trunk',
     'http://dev.worldcookery.com/svn/bla/trunk/blergh'),
    ('http://dev.worldcookery.com/svn/bla/branches/foobar/blergh',
     'tag/3.4',
     'http://dev.worldcookery.com/svn/bla/tag/3.4/blergh'),
    ('http://dev.worldcookery.com/svn/bla/tags/foobar',
     'mybranch',
     'http://dev.worldcookery.com/svn/bla/branches/mybranch'),
    ('http://dev.worldcookery.com/svn/bla/branches/foobar',
     'mybranch',
     'http://dev.worldcookery.com/svn/bla/branches/mybranch'),
])
def test_determinebranch(current_url, new_branch, expected_url):
    url = es.determinebranch(new_branch, _svninfo=make_svninfo(current_url))
    assert url == expected_url


@pytest.mark.parametrize(['current_url', 'new_tag', 'expected_url'], [
    ('http://dev.worldcookery.com/svn/bla/trunk/blergh',
     'foobar',
     'http://dev.worldcookery.com/svn/bla/tags/foobar/blergh'),
    ('http://dev.worldcookery.com/svn/bla/branches/foobar/blergh',
     'foobaz',
     'http://dev.worldcookery.com/svn/bla/tags/foobaz/blergh'),
    ('http://dev.worldcookery.com/svn/bla/branch/foobar/blergh',
     'foobaz',
     'http://dev.worldcookery.com/svn/bla/tag/foobaz/blergh'),
])
def test_determinetag(current_url, new_tag, expected_url):
    url = es.determinetag(new_tag, _svninfo=make_svninfo(current_url))
    assert url == expected_url


@pytest.mark.parametrize(['current_url', 'expected_url'], [
    ('http://dev.worldcookery.com/svn/bla/tag/foo/bar/baz',
     'http://dev.worldcookery.com/svn/bla/branch'),
    ('http://dev.worldcookery.com/svn/bla/branch/foo/bar/baz',
     'http://dev.worldcookery.com/svn/bla/branch'),
    ('http://dev.worldcookery.com/svn/bla/tags/foo/bar/baz',
     'http://dev.worldcookery.com/svn/bla/branches'),
    ('http://dev.worldcookery.com/svn/bla/branches/foo/bar/baz',
     'http://dev.worldcookery.com/svn/bla/branches'),
    ('http://dev.worldcookery.com/svn/bla/trunk/foo/bar/baz',
     'http://dev.worldcookery.com/svn/bla/branches'),
])
def test_listbranches(current_url, expected_url):
    def svnls(url):
        assert url == expected_url
        return "a/\nb/\nc\n"
    svninfo = make_svninfo(current_url)
    branches = es.listbranches('.', _svninfo=svninfo, _svnls=svnls)
    assert branches == ["a", "b"]


@pytest.mark.parametrize(['current_url', 'expected_url'], [
    ('http://dev.worldcookery.com/svn/bla/tag/foo/bar/baz',
     'http://dev.worldcookery.com/svn/bla/tag'),
    ('http://dev.worldcookery.com/svn/bla/branch/foo/bar/baz',
     'http://dev.worldcookery.com/svn/bla/tag'),
    ('http://dev.worldcookery.com/svn/bla/tags/foo/bar/baz',
     'http://dev.worldcookery.com/svn/bla/tags'),
    ('http://dev.worldcookery.com/svn/bla/branches/foo/bar/baz',
     'http://dev.worldcookery.com/svn/bla/tags'),
    ('http://dev.worldcookery.com/svn/bla/trunk/foo/bar/baz',
     'http://dev.worldcookery.com/svn/bla/tags'),
])
def test_listtags(current_url, expected_url):
    def svnls(url):
        assert url == expected_url
        return "a/\nb/\nc\n"
    svninfo = make_svninfo(current_url)
    branches = es.listtags('.', _svninfo=svninfo, _svnls=svnls)
    assert branches == ["a", "b"]


def test_branchpoints_error_handling():
    def svnlog(url):
        return 'hahaha this is not xml'
    branch_url = 'http://dev.worldcookery.com/svn/bla/branches/foo'
    with pytest.raises(SystemExit):
        es.branchpoints(branch_url, _svnlog=svnlog)


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


@pytest.mark.parametrize(['command', 'nargs'], [
    ('ezmerge', 4),
    ('ezrevert', 3),
    ('ezswitch', 3),
    ('eztag', 3),
    ('ezbranch', 3),
    ('rmbranch', 2),
    ('mvbranch', 3),
])
def test_too_many_args(command, nargs, capsys):
    with pytest.raises(SystemExit):
        getattr(es, command)([command] + ['FOO'] * nargs)
    out, err = capsys.readouterr()
    assert 'too many arguments' in err


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


def test_ezmerge():
    url = 'http://dev.worldcookery.com/svn/bla/trunk'
    with mock.patch('eazysvn.svninfo', make_svninfo(url)), \
            mock.patch('eazysvn.svnlog', make_svnlog()), \
            mock.patch('os.system') as mock_system:
        es.ezmerge(['ezmerge', 'fix-bug-1234'])
    assert mock_system.mock_calls == [
        mock.call('svn log -r 4505:4515 http://dev.worldcookery.com/svn/bla/branches/fix-bug-1234'),
        mock.call('svn merge -r 4504:4515 http://dev.worldcookery.com/svn/bla/branches/fix-bug-1234 .'),
    ]


def test_ezmerge_dry_run():
    url = 'http://dev.worldcookery.com/svn/bla/trunk'
    with mock.patch('eazysvn.svninfo', make_svninfo(url)), \
            mock.patch('eazysvn.svnlog', make_svnlog()), \
            mock.patch('os.system') as mock_system:
        es.ezmerge(['ezmerge', '-n', 'fix-bug-1234'])
    assert mock_system.mock_calls == [
        mock.call('svn log -r 4505:4515 http://dev.worldcookery.com/svn/bla/branches/fix-bug-1234'),
    ]


def test_ezmerge_diff():
    url = 'http://dev.worldcookery.com/svn/bla/trunk'
    with mock.patch('eazysvn.svninfo', make_svninfo(url)), \
            mock.patch('eazysvn.svnlog', make_svnlog()), \
            mock.patch('os.system') as mock_system:
        es.ezmerge(['ezmerge', '-d', 'fix-bug-1234'])
    assert mock_system.mock_calls == [
        mock.call('svn log -r 4505:4515 http://dev.worldcookery.com/svn/bla/branches/fix-bug-1234'),
        mock.call('svn diff -r 4504:4515 http://dev.worldcookery.com/svn/bla/branches/fix-bug-1234'),
    ]


def test_additional_tests():
    assert es.additional_tests().countTestCases() > 0
