#!/usr/bin/env python
#
# Make switching between SVN branches easier
#
# Copyright (c) 2007 Marius Gedminas
# Portions Copyright (c) 2006 Philipp von Weitershausen
#
# This program is distributed under the terms of the GNU General Public Licence
# See the file COPYING for details.
#
# Usage: ezswitch.py --help
#
# Bugs: lack of serious command-line argument quoting.
#       e.g. `ezswitch.py -c -m "it's a good branch" mybranch` will fail
#

import os
import sys
import optparse
import popen2


def svninfo(path):
    """
    Return svn information about ``path``.
    """
    stdout, stdin = popen2.popen2('svn info %s' % path)
    return stdout.read()


def svnls(url):
    """
    Return a list of files under ``url``.
    """
    stdout, stdin = popen2.popen2('svn ls %s' % url)
    return stdout.read()


def currentbranch(path, svninfo=svninfo):
    """
    Let's set up a dummy 'svn info' command handler:

      >>> def dummyinfo(path):
      ...     return '''\
      ... Path: .
      ... URL: http://dev.worldcookery.com/svn/bla/trunk/blergh
      ... Repository UUID: ab69c8a2-bfcb-0310-9bff-acb20127a769
      ... Revision: 1654
      ... Node Kind: directory
      ... '''

    ``currentbranch()`` takes the svn path of the current working
    directory path returns it.

      >>> currentbranch('.', svninfo=dummyinfo)
      'http://dev.worldcookery.com/svn/bla/trunk/blergh'

      >>> def dummyinfo(path):
      ...     return '''\
      ... Path: .
      ... URL: http://dev.worldcookery.com/svn/bla/branches/foobar/blergh
      ... Repository UUID: ab69c8a2-bfcb-0310-9bff-acb20127a769
      ... Revision: 1654
      ... Node Kind: directory
      ... '''

      >>> currentbranch('.', svninfo=dummyinfo)
      'http://dev.worldcookery.com/svn/bla/branches/foobar/blergh'
 
    """
    lines = svninfo(path).splitlines()
    if lines[1].startswith('URL: '):
        url = lines[1][5:]
    else:
        url = lines[2][5:]
    return url


def determinebranch(branch, path, svninfo=svninfo):
    """
    Let's set up a dummy 'svn info' command handler:

      >>> def dummyinfo(path):
      ...     return '''\
      ... Path: .
      ... URL: http://dev.worldcookery.com/svn/bla/trunk/blergh
      ... Repository UUID: ab69c8a2-bfcb-0310-9bff-acb20127a769
      ... Revision: 1654
      ... Node Kind: directory
      ... '''

    ``determinebranch()`` takes the svn path of the current working
    directory path and mangles in either trunk or a branch repository
    path.  Here's an example for turning 'trunk' into 'branches':

      >>> determinebranch('foobar', '.', svninfo=dummyinfo)
      'http://dev.worldcookery.com/svn/bla/branches/foobar/blergh'

    Of course, if the current working copy is a trunk and we specify
    trunk, it keeps the trunk:

      >>> determinebranch('trunk', '.', svninfo=dummyinfo)
      'http://dev.worldcookery.com/svn/bla/trunk/blergh'

    Here's the whole thing the other way around:

      >>> def dummyinfo(path):
      ...     return '''\
      ... Path: .
      ... URL: http://dev.worldcookery.com/svn/bla/branches/foobar/blergh
      ... Repository UUID: ab69c8a2-bfcb-0310-9bff-acb20127a769
      ... Revision: 1654
      ... Node Kind: directory
      ... '''

      >>> determinebranch('trunk', '.', svninfo=dummyinfo)
      'http://dev.worldcookery.com/svn/bla/trunk/blergh'
 
    """
    url = currentbranch(path, svninfo=svninfo)

    chunks = url.split('/')
    chunks.reverse()
    new_chunks = []

    while chunks:
        ch = chunks.pop()
        if ch in ('branch', 'branches'):
            chunks.pop()
            if branch == 'trunk':
                new_chunks.append(branch)
            else:
                new_chunks.append(ch)
                new_chunks.append(branch)
        elif ch == 'trunk' and branch != 'trunk':
            new_chunks.append('branches')
            new_chunks.append(branch)
        else:
            new_chunks.append(ch)

    return '/'.join(new_chunks)


def listbranches(path, svninfo=svninfo, svnls=svnls):
    r"""
    Let's set up a dummy 'svn info' command handler:

      >>> def dummyinfo(path):
      ...     return '''\
      ... Path: .
      ... URL: http://dev.worldcookery.com/svn/bla/trunk/blergh
      ... Repository UUID: ab69c8a2-bfcb-0310-9bff-acb20127a769
      ... Revision: 1654
      ... Node Kind: directory
      ... '''

    and a dummy 'svn ls' as well:

      >>> def dummyls(path):
      ...     assert path == 'http://dev.worldcookery.com/svn/bla/branches'
      ...     return '''\
      ... foo/
      ... README.txt
      ... bar/
      ... baz/
      ... '''

    ``listbranches()`` takes the svn path of the current working
    directory path, finds the URL of the repository, and lists all branches
    in that repository.

      >>> listbranches('.', svninfo=dummyinfo, svnls=dummyls)
      ['foo', 'bar', 'baz']
 
    """
    url = currentbranch(path, svninfo=svninfo)
    chunks = url.split('/')

    while chunks:
        ch = chunks.pop()
        if ch in ('branch', 'branches'):
            chunks.append(ch)
            break
        elif ch == 'trunk':
            chunks.append('branches')
            break

    branches = []
    for line in svnls('/'.join(chunks)).splitlines():
        if line.endswith('/'):
            branches.append(line[:-1])
    return branches


def main(argv):
    progname = os.path.basename(argv[0])
    parser = optparse.OptionParser(
                "usage: %prog [-n] [-c] [-m MSG] branch [wc-path]\n"
                "       %prog -l\n"
                "       %prog",
                prog=progname,
                description="Switch the working directory to a different"
                            " Subversion branch.  When run without"
                            " arguments, %prog will print the"
                            " URL of the current branch.")
    parser.add_option('-l', '--list',
                      help='list existing branches',
                      action='store_true', dest='list_branches', default=False)
    parser.add_option('-c', '--create-branch',
                      help='create the new branch before switching to it',
                      action='store_true', dest='create_branch', default=False)
    parser.add_option('-m',
                      help='commit message for --create-branch',
                      action='store', dest='message', default=None)
    parser.add_option('-n', '--dry-run',
                      help='do not touch any files on disk or in subversion',
                      action='store_true', dest='dry_run', default=False)
    try:
        opts, args = parser.parse_args(argv[1:])
        if len(args) > 2:
            parser.error("too many arguments, try %s --help" % progname)
    except optparse.OptParseError, e:
        sys.exit(e)

    path = '.'

    if opts.list_branches:
        print '\n'.join(listbranches(path))
        return

    if not args:
        print currentbranch(path)
        return

    branch = args[0]
    if len(args) > 1:
        path = args[1]

    branch = determinebranch(branch, path)
    if opts.create_branch:
        cur_branch = currentbranch(path)
        cmd = "svn cp %s %s" % (cur_branch, branch)
        if opts.message:
            cmd += " -m '%s'" % opts.message
        print cmd
        if not opts.dry_run:
            os.system(cmd)

    cmd = "svn switch %s %s" % (branch, path)
    print cmd
    if not opts.dry_run:
        os.system(cmd)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        import doctest
        doctest.testmod()
    else:
        main(sys.argv)
