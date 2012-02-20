Changelog
=========


1.12.2 (2012-02-20)
-------------------

* New argument: ``ezmerge --accept=ARG``, passed directly to subversion.

* Moved the source code from self-hosted Subversion to GitHub.


1.12.1 (2010-09-14)
-------------------

* A somewhat better error message for ``ezswitch -c newbranch`` when eazysvn
  is unable to understand the branch structure (LP#446369).

* ``ezswitch -t tagname; ezswitch branchname`` switches to a branch named
  ``branchname`` instead of trying to switch to a tag named ``branchname``
  (LP#617888, fix by Wolfgang Schnerring).


1.12.0 (2010-07-22)
-------------------

* Minor fixes to various options --help messages.

* Don't pass revision range to svn when using ``ezmerge --reintegrate``.
  Patch by Michael Howitz <mh@gocept.com>.

* New option: ``ezmerge --tag``.
  Contributed by Michael Howitz <mh@gocept.com>.


1.11.0 (2009-05-26)
-------------------

* New option: ``ezmerge --reintegrate``, passed straight to svn merge.
  Contributed by Wolfgang Schnerring <wosc@wosc.de>.


1.10.0 (2009-04-08)
-------------------

* Uses ``subprocess`` instead of ``os.popen2``; no more deprecation warnings
  on Python 2.6.


1.9.0 (2008-08-08)
------------------

* ``eazysvn tag`` accepts the -l (--list) option.
* ``ezbranch`` and ``ezswitch`` accept the -t option.
* New command: ``eazysvn branchpoint``.
* You can refer to tags in all commands that accept branch names; use a branch
  named "tags/*tagname*".  This works for all kinds of prefixes, e.g.
  "obsolete-branches/*branchname*" etc.


1.8.0 (2008-06-26)
------------------

* Nice PyPI documentation page with a changelog.
* New command: ``eazysvn tag``.
* ``eazysvn --version`` prints the version number.


1.7.0 (2008-06-11)
------------------

* New command: ``eazysvn branchdiff``.


1.6.1 (2007-12-12)
------------------

* ``ezmerge`` accepts the -l (--list) option.
* ``ezmerge branchname`` is short for ``ezmerge ALL branchname``.


1.6.0 (2007-12-11)
------------------

* ``ezmerge`` accepts the -d (--diff) option.


1.5.1 (2007-06-28)
------------------

* ``ezrevert`` is short for ``eazysvn revert``.


1.5 (2007-06-28)
----------------

* New command: ``ezbranch``, short for ``eazysvn branchurl``.


1.5 (2007-06-28)
----------------

* New command: ``ezbranch``, short for ``eazysvn branchurl``.


1.4.1 (2007-06-20)
------------------

* Bugfix for ``eazysvn rmbranch``.


1.4.0 (2007-06-11)
------------------

* New command: ``eazysvn rmbranch``.
* New command: ``eazysvn mvbranch``.


1.3.1 (2007-04-04)
------------------

* Make ``ezmerge ALL trunk`` useful: merge changes from the branch point of the
  current branch, not from the start of trunk.


1.3 (2007-01-25)
----------------

* New command: ``eazysvn revert``.


1.2 (2007-01-16)
----------------

* First setuptools-based release, thanks to Philipp von Weitershausen.
* New command: ``eazysvn`` with four subcommands: ``merge`` (same as the old
  ``ezmerge`` command), ``switch`` (same as the old ``ezswitch`` command),
  ``help`` and ``selftest``.


1.1 (2007-01-12)
----------------

* New command: ``ezswitch``.
* Changed ``ezmerge`` output format to be clearer.
* ``ezmerge`` now accepts 'rXXX' as revision numbers.
* ``ezmerge XXX:YYY`` treats the range as SVN-compatible
* ``ezmerge XXX-YYY`` is the new syntax for user-friendly inclusive ranges
* ``ezmerge ALL branchname`` figures out the appropriate revision numbers to
  merge all of the changes made in that branch.
* ``ezmerge`` now accepts -n (--dry-run) option.
* ``ezmerge`` now accepts -h (--help) and shows a help message.


1.0 (2006-08-23)
----------------

* The original ``ezmerge.py`` by Philipp von Weitershausen.


Some of the dates before version 1.7.0 may be approximate, and the changes
misattributed to the wrong revision.
