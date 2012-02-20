=======
eazysvn
=======

Eazysvn is a Python script that simplifies some common operations with
Subversion branches.

.. contents::


Installation
============

Get it from the `Python Package Index <http://pypi.python.org/pypi/eazysvn>`_.
If you have `easy_install <http://peak.telecommunity.com/DevCenter/EasyInstall>`_,
you should be able to ::

  easy_install eazysvn

You'll need Python 2.4 or later, as well as the Subversion command-line client.


Usage
=====


Getting help
------------

At the shell prompt type ::

  eazysvn help

It will print a list of commands.  Some of the commands have aliases::

  ezswitch = eazysvn switch
  ezmerge = eazysvn merge
  ezrevert = eazysvn revert
  ezbranch = eazysvn branchurl


Switching between branches
--------------------------

In a subversion working directory run ::

  ezswitch -l

to see all the branches available in your project.  This assumes your
Subversion repository uses the standard layout with 'trunk', 'tags', and
'branches' in it.

Then run

.. parsed-literal::

  ezswitch *branchname*

to switch to a branch, and ::

  ezswitch trunk

to switch back to trunk.


Working with branches
---------------------

Say you're working on a project and in the middle of a difficult refactoring
suddenly realize the changes you've made are too risky for trunk you want to
put them in a branch.  Run

.. parsed-literal::

  ezswitch --create *my-branch*

This will create a new branch and switch your working directory to it.  All
your changes in progress are kept intact and you can commit them directly
to the new branch with svn commit.


Seeing all the changes on a branch
----------------------------------

You may want to see the overall diff of changes made on a branch since it was
created, say, to review it before attempting a merge.

.. parsed-literal::

  eazysvn branchdiff *branchname*

does exactly that.  For extra readability, install `colordiff
<http://colordiff.sourceforge.net/>`_ and use

.. parsed-literal::

  eazysvn branchdiff *branchname* | colordiff | less -R


Merging branches
----------------

After you've finished hacking on your branch, you will want to switch back to
trunk and start merging.  Run ::

  ezswitch trunk

then

.. parsed-literal::

  ezmerge *my-branch*

You will see the svn command used for the merge as well as a log of all the
changes.  Fix merge conflicts (if any), run the test suite, then commit.
The output of ezmerge helps you produce an informative commit message.

If instead of merging the changes to your working directory you'd like to see
the combined diff, pass the -d (or --diff) option to ezmerge

.. parsed-literal::

  ezmerge -d *featurebranch*


Cherrypicking
-------------

If you want to merge only some of the changes made in a branch, you can pass the
revision number (or a range) to ezmerge.  For example, to backport a bugfix
implemented in revision 1234 of trunk to a release branch,

.. parsed-literal::

  ezswitch *release-branch*
  ezmerge 1234 trunk

You can also merge a range of revisions ::

  ezmerge 1234-1236 trunk

This range is inclusive, unlike Subversion.  If you want to, you can also use
Subversion-style half-open ranges as well ::

  ezmerge 1233:1236 trunk

The --diff option works here too.

.. parsed-literal::

  ezmerge -d 1234-1236 trunk


Reverting comitted changes
--------------------------

It's like cherrypicking, but in reverse: you want to unapply changes already
committed to this branch. ::

  ezrevert 1234


Making tags
-----------

To tag the current version of the source tree in your working directory, run

.. parsed-literal::

  eazysvn tag *tagname*


Manipulating branches
---------------------

To remove a branch completely, run

.. parsed-literal::

  eazysvn rmbranch *branchname*

To rename a branch, run

.. parsed-literal::

  eazysvn mvbranch *oldbranchname* *newbranchname*

To do other kinds of operations, eazysvn provides a shortcut that lets you
use branch names instead of full branch URLs (this bit assumes a Unix-like
shell):

.. parsed-literal::

  svn ls $(ezbranch *branchname*)
  svn diff \`ezbranch *branch1*\` \`ezbranch *branch2*\`

Another possibly useful eazysvn command is ``branchpoint``.  It shows the
revision when a branch was created.  For example, to see the changes
in trunk that are not present in a branch, run

.. parsed-literal::

  svn diff -r \`eazysvn branchpoint *branch*\`:HEAD \`ezbranch *trunk*\`


Overall options
---------------

All commands that require a branch name as an argument accept a -l (or --list)
option that lists all branches, e.g. ::

  ezbranch -l

All commands that make changes to the repository or working directory accept
a -n (or --dry-run) option that just prints the svn commands that would
otherwise be executed. ::

  ezmerge -n 1234 otherbranch

All commands that make changes to the repository (create/remove/rename branches
or tags) accept a -m option with a commit message.  If not specified, you'll
get a text editor spawned by subversion itself to type the commit message.  ::

  ezswitch -c newbranch -m "Create branch for the new feature"

Many of the commands accept other options as well.  Use

.. parsed-literal::

  eazysvn *cmd* --help
  ezmerge --help
  ezswitch --help
  *etc.*

to discover those.


Appendixes
==========


Revision numbers
----------------

A revision to Subversion means the state of the whole project tree at a given
instant of time.  Sometimes the changeset that converts one revision to another
is more interesting.  When you specify a single number N to ezmerge, it assumes
that you want to merge the changeset that changes revision (N-1) to revision N.

If you specify a range N-M, ezmerge.py merges all the changesets
that change revision (N-1) to revision M.  For compatibility with ``svn
merge`` you can specify the revision range as N:M, and ezmerge will
merge all the changesets that convert revision N to revision M.  In the last
case N can be greater than M, which is useful if you want to revert some
changes, although ``ezrevert`` is more convenient for that.

When you specify ranges (N-M or N:M) M can be a special name ``HEAD``.
It means the latest revision in the repository.

You can also specify a special range ``ALL``, which means all the changesets
made in the branch.  ezmerge will parse the output of ``svn log`` to get the
revision numbers for you.  ``ezmerge branchname`` is a shortcut for ``ezmerge
ALL branchname``.

For easier copying & pasting from ``svn log`` output, you can prefix numbers
with the letter ``r``, e.g. ``r1234``.


Branch names
------------

Eazysvn expects you to use the traditional repository layout, and can
find its way from any of these to any other of these URLs if you specify the
desired branch name as 'trunk', 'foo', or 'bar'.

.. parsed-literal::

  *scheme://server/path/to/svn/repo*/trunk/*subdirs*
  *scheme://server/path/to/svn/repo*/branches/foo/*subdirs*
  *scheme://server/path/to/svn/repo*/branches/bar/*subdirs*

You do not have to be at the top of the project to switch or merge, any
subdirectory will work.  The part of your checkout above the current
directory will not be touched by the merge/switch.

An alternative scheme is partially supported:

.. parsed-literal::

  *scheme://server/path/to/svn/repo*/trunk/*subdirs*
  *scheme://server/path/to/svn/repo*/branch/foo/*subdirs*
  *scheme://server/path/to/svn/repo*/branch/bar/*subdirs*

Eazysvn will be able to find the location of trunk or other branches if you
start out in a branch checkout, but it won't be able to find your branches
from a trunk checkout.  This is a bug that should be fixed one day.

You can force eazysvn to use any nonstandard scheme if you explicitly enter the
prefix with a slash in front of the branch name, e.g. ``ezswitch feature/foo``
in a trunk checkout would switch from

.. parsed-literal::

  *scheme://server/path/to/svn/repo*/trunk/*subdirs*

to

.. parsed-literal::

  *scheme://server/path/to/svn/repo*/feature/foo/*subdirs*

If you start out in a checkout of such a nonstandard location, Eazysvn won't be
able to find the location of trunk or other branches.  This is a bug that
should be fixed one day.


Branch merge logic
------------------

When you merge a branch (to trunk or to another branch), eazysvn uses ``svn
log`` to find the revision number when the branch was created.  Then it merges
all the changes ever comitted on that branch.

This means you usually can't merge from the same branch more than once.  It's
a consequence of Subversion's lack of merge tracking.

Also, since there's no fancy searching for common ancestors or anything like
that, if you branch A from trunk make some changes, then branch B from branch
A, make some changes, then if you ezmerge B on trunk, you won't get any changes
made in branch A.

When you merge a trunk to a branch, eazysvn again uses ``svn log`` to find the
branch point and then merges all the changes made on trunk since that revision.

It's a bad idea to merge from trunk to a branch, because then you won't easily
be able to merge that branch back to trunk.  You may try, subversion might
apply the already-applied changes twice cleanly, but it's a matter of luck.

Keep it simple: always merge a branch only once, back to the same place you
branched from, and you'll avoid trouble.  Remove branches you've merged to
avoid accidentally making new changes that will be harder to merge.


Changelog
=========

See CHANGES.rst


Licencing and source code
=========================

Eazysvn is licenced under the GNU General Public Licence version 2 or later.

You can get the latest source code with

.. parsed-literal::

  git clone git://github.com/mgedmin/eazysvn.git

Eazysvn began life as Philipp von Weitershausen's `ezmerge.py
<http://codespeak.net/svn/user/philikon/ezmerge.py>`_.  Then Marius Gedminas
took over, created a `home page <http://mg.pov.lt/eazysvn>`_, and started
adding random features.


Bugs
====

Report bugs at https://github.com/mgedmin/eazysvn/issues


Wishlist/Todo
=============

``ezmerge`` should accept a comma-separated list of revisions (1,2,4-6,9).

There should be ``eazysvn rmtag`` and ``eazysvn mvtag``.

``eazysvn help cmd`` should be the same as ``eazysvn cmd --help`` and not an
error.

``eazysvn -n cmd`` should be the same as ``eazysvn cmd -n`` and not an error.

``eazysvn`` should do an ``svn ls`` to discover the branching scheme in use
('branch' or the more traditional 'branches').

