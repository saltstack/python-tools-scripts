.. _changelog:

=========
Changelog
=========

Versions follow `Semantic Versioning <https://semver.org>`_ (`<major>.<minor>.<patch>`).

Backward incompatible (breaking) changes will only be introduced in major versions with advance notice in the
**Deprecations** section of releases.

.. towncrier-draft-entries::

.. towncrier release notes start

0.18.5 (2023-11-25)
===================

No significant changes.


0.18.4 (2023-11-23)
===================

No significant changes.


0.18.3 (2023-11-17)
===================

No significant changes.


0.18.2 (2023-11-17)
===================

No significant changes.


0.18.1 (2023-08-28)
===================

Features
--------

- Switch to `RawDescriptionHelpFormatter` as the formatter class. This will help to include properly indented examples. (`#42 <https://github.com/s0undt3ch/python-tools-scripts/issues/42>`_)


0.18.0 (2023-08-28)
===================

Bug Fixes
---------

- Fix traceback thrown during install reqs for virtualenv(changelog) (`#40 <https://github.com/s0undt3ch/python-tools-scripts/issues/40>`_)


0.17.0 (2023-06-05)
===================

Improvements
------------

- Add support for just default requirements configs (`#39 <https://github.com/s0undt3ch/python-tools-scripts/issues/39>`_)


0.16.2 (2023-06-05)
===================

Bug Fixes
---------

- Don't force the default virtualenv to `system_site_packages=True` (`#38 <https://github.com/s0undt3ch/python-tools-scripts/issues/38>`_)


0.16.1 (2023-06-05)
===================

Bug Fixes
---------

- Properly handle non relative paths (`#37 <https://github.com/s0undt3ch/python-tools-scripts/issues/37>`_)


0.16.0 (2023-06-05)
===================

Improvements
------------

- Switch to [ruff](https://github.com/charliermarsh/ruff) (`#36 <https://github.com/s0undt3ch/python-tools-scripts/issues/36>`_)


0.15.0 (2023-05-31)
===================

Improvements
------------

- `VirtualEnvConfig` now additionally accepts `pip_args` which is a list of strings to pass to `pip` when installing the virtualenv's requirements. (`#35 <https://github.com/s0undt3ch/python-tools-scripts/issues/35>`_)


0.14.0 (2023-05-29)
===================

Bug Fixes
---------

- Remove virtualenv `site-packages` from `sys.path` in context manager exit (`#34 <https://github.com/s0undt3ch/python-tools-scripts/issues/34>`_)


0.13.6 (2023-05-29)
===================

Bug Fixes
---------

- Set `DefaultVirtualenvConfig.venv_config` to `None` when creating the class instance. (`#33 <https://github.com/s0undt3ch/python-tools-scripts/issues/33>`_)


0.13.5 (2023-05-29)
===================

Bug Fixes
---------

- Handle `-d/--debug` and `-q/--quiet` as early as possible (`#32 <https://github.com/s0undt3ch/python-tools-scripts/issues/32>`_)


0.13.4 (2023-05-29)
===================

Bug Fixes
---------

- Fixed bug where `venv_config` defined in `command_group` was getting ignored (`#31 <https://github.com/s0undt3ch/python-tools-scripts/issues/31>`_)


0.13.3 (2023-05-28)
===================

Bug Fixes
---------

- Don't set `context.vent` to a `nullcontext` (`#30 <https://github.com/s0undt3ch/python-tools-scripts/issues/30>`_)


0.13.2 (2023-05-27)
===================

Bug Fixes
---------

- Improved some type definitions (`#29 <https://github.com/s0undt3ch/python-tools-scripts/issues/29>`_)


0.13.1 (2023-05-27)
===================

Bug Fixes
---------

- Add `py.typed` to the source code (`#28 <https://github.com/s0undt3ch/python-tools-scripts/issues/28>`_)


0.13.0 (2023-05-27)
===================

Improvements
------------

- Allow importing the virtualenv's dependencies into the python running ``tools``.
  This will allow maintaining a lighter ``tools.txt`` requirements file, and install additional dependencies only for the commands that really need them. (`#25 <https://github.com/s0undt3ch/python-tools-scripts/issues/25>`_)
- Add support for a default Virtualenv. The default virtualenv site-packages will be added to the running python as an extra site dir. (`#26 <https://github.com/s0undt3ch/python-tools-scripts/issues/26>`_)
- Allow passing virtualenv configuration when calling ``ptscripts.register_tools_module`` (`#27 <https://github.com/s0undt3ch/python-tools-scripts/issues/27>`_)


0.12.0 (2023-03-07)
===================

Improvements
------------

- Allow passing a string or list of strings as the parent to avoid circular imports. (`#22 <https://github.com/s0undt3ch/python-tools-scripts/issues/22>`_)
- Take the `TOOLS_VIRTUALENV_CACHE_SEED` environmental variable into account when calculating the virtual environments cache hash. (`#23 <https://github.com/s0undt3ch/python-tools-scripts/issues/23>`_)


Bug Fixes
---------

- Catch `NotImplementedError` exception when setting up signal handling. Windows, for example, does not support signal handling with asyncio. (`#24 <https://github.com/s0undt3ch/python-tools-scripts/issues/24>`_)


0.11.1 (2023-02-16)
===================

Bug Fixes
---------

- Properly handle `subprocess.CalledProcessError`. Catch the exception, print the error, and exit with the `.returncode` attribute value. (`#21 <https://github.com/s0undt3ch/python-tools-scripts/issues/21>`_)


0.11.0 (2023-02-14)
===================

Features
--------

- The `ctx` now has a `web` attribute, a `requests.Session` instance which can be used to make web requests. (`#19 <https://github.com/s0undt3ch/python-tools-scripts/issues/19>`_)
- Improve the user experience when an `ImportError` occurs while instantiating tools.
  Instead of relying on direct imports, users can now call, `pyscripts.register_tools_module('tools.<whatever>')`.
  Python tools scripts will then import them one by one, catching and reporting any `ImportErrors` occurring.
  Due to these errors, some of the commands might be unavailable, but most likely not all, while providing a clue as to why that is. (`#20 <https://github.com/s0undt3ch/python-tools-scripts/issues/20>`_)


0.10.4 (2023-02-13)
===================

Features
--------

- The filename on console logs is now only shown when debug output is enabled. (`#18 <https://github.com/s0undt3ch/python-tools-scripts/issues/18>`_)


0.10.3 (2023-02-12)
===================

Bug Fixes
---------

- The parser CLI logs now show the right file making the call (`#17 <https://github.com/s0undt3ch/python-tools-scripts/issues/17>`_)


0.10.2 (2023-02-07)
===================

Bug Fixes
---------

- Allow passing `parent` to `command_group` (`#16 <https://github.com/s0undt3ch/python-tools-scripts/issues/16>`_)


Trivial/Internal Changes
------------------------

- Update pre-commit hooks versions (`#16 <https://github.com/s0undt3ch/python-tools-scripts/issues/16>`_)


0.10.1 (2023-01-27)
===================

Bug Fixes
---------

- Allow creating the virtual environments with `venv` as a fallback if `virtualenv` is not available. (`#15 <https://github.com/s0undt3ch/python-tools-scripts/issues/15>`_)


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
