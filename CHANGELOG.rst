.. _changelog:

=========
Changelog
=========

Versions follow `Semantic Versioning <https://semver.org>`_ (`<major>.<minor>.<patch>`).

Backward incompatible (breaking) changes will only be introduced in major versions with advance notice in the
**Deprecations** section of releases.

.. towncrier-draft-entries::

.. towncrier release notes start

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
