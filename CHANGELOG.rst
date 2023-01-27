.. _changelog:

=========
Changelog
=========

Versions follow `Semantic Versioning <https://semver.org>`_ (`<major>.<minor>.<patch>`).

Backward incompatible (breaking) changes will only be introduced in major versions with advance notice in the
**Deprecations** section of releases.

.. towncrier-draft-entries::

.. towncrier release notes start

0.10.0 (2023-01-27)
===================

Features
--------

- Add `virtualenv` support.

  Any python requirements that must be imported in the tools scripts cannot use this virtualenv support.
  This support is for when shelling out to binaries/scripts that get installed with the requirements. (`#13 <https://github.com/s0undt3ch/python-tools-scripts/issues/13>`_)


0.9.7 (2023-01-25)
==================

Features
--------

- Forward `ctx.run(..., **kwargs)` to the underlying subprocess call. (`#14 <https://github.com/s0undt3ch/python-tools-scripts/issues/14>`_)


0.9.6 (2023-01-23)
==================

Bug Fixes
---------

- Cleanup conflicting parser CLI options (`#12 <https://github.com/s0undt3ch/python-tools-scripts/issues/12>`_)


0.9.5 (2023-01-23)
==================

Features
--------

- Allow passing a maximum timeout for commands executed through `ctx.run()` (`#11 <https://github.com/s0undt3ch/python-tools-scripts/issues/11>`_)


0.9.4 (2023-01-12)
==================

Features
--------

- Allow `tools` to report it's version (`#10 <https://github.com/s0undt3ch/python-tools-scripts/issues/10>`_)


0.9.3 (2022-11-28)
==================

Improvements
------------

- Repeated caught signals now kill the process (`#9 <https://github.com/s0undt3ch/python-tools-scripts/issues/9>`_)


Bug Fixes
---------

- Fixed process interaction (`#9 <https://github.com/s0undt3ch/python-tools-scripts/issues/9>`_)


0.9.2 (2022-11-07)
==================

Bug Fixes
---------

- Properly handle `SIGINT` and `SIGTERM` on spawed subprocesses (`#7 <https://github.com/s0undt3ch/python-tools-scripts/issues/7>`_)


0.9.1 (2022-10-09)
==================

Improvements
------------

- Provide helper `chdir` method on the context object. (`#6 <https://github.com/s0undt3ch/python-tools-scripts/issues/6>`_)


0.9.0 (2022-10-07)
==================

Improvements
------------

- When a function has a keyword argument with a boolean default, the parser now automatically creates the `store_true` or `store_false` action(if not action was provided in the `arguments` keyword definition. (`#5 <https://github.com/s0undt3ch/python-tools-scripts/issues/5>`_)


0.9.0rc5 (2022-10-06)
=====================

Improvements
------------

- Provide a `run()` method to `ctx` to run subprocesses. (`#4 <https://github.com/s0undt3ch/python-tools-scripts/issues/4>`_)


0.9.0rc4 (2022-10-06)
=====================

Improvements
------------

- Several improvements with logging (`#3 <https://github.com/s0undt3ch/python-tools-scripts/issues/3>`_)


0.9.0rc3 (2022-10-01)
=====================

Bug Fixes
---------

- Fix typo in keyword argument (`#2 <https://github.com/s0undt3ch/python-tools-scripts/issues/2>`_)


0.9.0rc2 (2022-09-30)
=====================

Bug Fixes
---------

- Properly handle CI environment terminals (`#1 <https://github.com/s0undt3ch/python-tools-scripts/issues/1>`_)


0.9.0rc1 (2022-09-22)
=====================

First minimally working release.
