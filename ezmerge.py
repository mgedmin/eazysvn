#!/usr/bin/env python
#
# Make simple revision merges much easier
#
# Copyright (c) 2006 Philipp von Weitershausen
# Copyright (c) 2007 Marius Gedminas
#
# Usage: ezmerge rev branch [path]
#    or: ezmerge beginrev:endrev branch [path]
#    or: ezmerge ALL branch [path]
#

import os
import sys
import optparse
import popen2
from xml.dom import minidom


def revs(rev):
    """
    Make sense out of convenient way of mentioning revisions

    For example, the revision 43 starts at r42 and ends at r43:

      >>> revs('43')
      (42, '43')

    Revision ranges are also supported:

      >>> revs('42-21252')
      (41, 21252)
      >>> revs('42-HEAD')
      (41, 'HEAD')

    SVN-compatible revision ranges also work

      >>> revs('41:21252')
      (41, 21252)
      >>> revs('41:HEAD')
      (41, 'HEAD')

    Even reverse diffs that undo certain revisions are supported
    correctly:

      >>> revs('42:41') # undo r42
      (42, 41)

    But not with the "simple rev" syntax

      >>> revs('42-41')
      Traceback (most recent call last):
        ...
      ValueError: empty range (42-41)

    """
    if '-' in rev:
        rev, endrev = rev.split('-')
        rev = int(rev) - 1
        if not endrev == 'HEAD':
            endrev = int(endrev)
        if rev >= endrev:
            raise ValueError('empty range (%s-%s)' % (rev + 1, endrev))
    elif ':' in rev:
        rev, endrev = rev.split(':')
        rev = int(rev)
        if not endrev == 'HEAD':
            endrev = int(endrev)
    else:
        endrev = rev
        rev = int(rev) - 1
    return rev, endrev


def svninfo(path):
    """
    Return svn information about ``path``.
    """
    stdout, stdin = popen2.popen2('svn info %s' % path)
    return stdout.read()


def svnlog(url):
    """
    Return svn log of ``url``, stopping on branchpoints, in XML.
    """
    stdout, stdin = popen2.popen2('svn log --non-interactive --stop-on-copy'
                                  ' --xml %s' % url)
    return stdout.read()


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
    lines = svninfo(path).splitlines()
    if lines[1].startswith('URL: '):
        url = lines[1][5:]
    else:
        url = lines[2][5:]

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


def branchpoints(branch, svnlog=svnlog):
    r"""
    Let's set up a dummy 'svn log' command handler:

      >>> def dummylog(url):
      ...     return '''\
      ... <?xml version="1.0" encoding="utf-8"?>
      ... <log>
      ... <logentry
      ...    revision="4515">
      ... <author>mg</author>
      ... <date>2007-01-11T16:30:07.775378Z</date>
      ... <msg>Blah blah.
      ... 
      ... Blah blah.
      ... 
      ... </msg>
      ... </logentry>
      ... <logentry
      ...    revision="4504">
      ... <author>mg</author>
      ... <date>2007-01-11T16:29:32.166370Z</date>
      ... <msg>create branch</msg>
      ... </logentry>
      ... </log>
      ... '''

    ``branchpoints()`` takes the svn URL and finds the revision number of the
    branch point.

      >>> branchpoints('http://dev.worldcookery.com/svn/bla/branches/foobar',
      ...             svnlog=dummylog)
      (4504, 4515)

    """
    xml = svnlog(branch)
    try:
        dom = minidom.parseString(xml)
    except:
        sys.exit("Could not parse svn log output:\n\n" + xml)
    newest_entry = dom.getElementsByTagName('logentry')[0]
    oldest_entry = dom.getElementsByTagName('logentry')[-1]
    return (int(oldest_entry.getAttribute('revision')),
            int(newest_entry.getAttribute('revision')))


def main(argv):
    progname = os.path.basename(argv[0])
    parser = optparse.OptionParser(
                "usage: %prog [options] rev source-branch [wc-path]",
                prog=progname,
                description="merge changes from Subversion branches")
    parser.add_option('-n', '--dry-run',
                      help='do not touch any files on disk or in subversion',
                      action='store_true', dest='dry_run', default=False)
    try:
        opts, args = parser.parse_args(argv[1:])
        if len(args) < 2:
            parser.error("too few arguments, try %s --help" % progname)
        elif len(args) > 3:
            parser.error("too many arguments, try %s --help" % progname)
    except optparse.OptParseError, e:
        sys.exit(e)

    rev = args[0]
    branchname = args[1]
    path = '.'
    if len(args) > 2:
        path = args[2]

    branch = determinebranch(branchname, path)
    if branchname != 'trunk' and not branchname.endswith('branch'):
        branchname += ' branch'
    if rev == 'ALL':
        beginrev, endrev = branchpoints(branch)
        print "Merge %s with" % (branchname)
    else:
        beginrev, endrev = revs(rev)
        if '-' in rev or ':' in rev:
            what = "revisions %s" % rev
        else:
            what = "revision %s" % rev
        print "Merge %s from %s with" % (what, branchname)
    print
    merge_cmd = "svn merge -r %s:%s %s %s" % (beginrev, endrev, branch, path)
    print " ", merge_cmd
    print
    log_cmd = "svn log -r %s:%s %s" % (beginrev + 1, endrev, branch)
    os.system(log_cmd)
    if not opts.dry_run:
        os.system(merge_cmd)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        import doctest
        doctest.testmod()
    else:
        main(sys.argv)
