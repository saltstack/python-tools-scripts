from __future__ import annotations

import hashlib
import json
import logging
import os
import pathlib
import shutil
import subprocess
import sys
import textwrap
from typing import TYPE_CHECKING
from typing import TypedDict

try:
    from typing import NotRequired  # type: ignore[attr-defined]
except ImportError:
    from typing_extensions import NotRequired

import attr

from ptscripts import CWD

if TYPE_CHECKING:
    from ptscripts.parser import Context

log = logging.getLogger(__name__)


class VirtualEnvConfig(TypedDict):
    """
    Virtualenv Configuration Typing.
    """

    requirements: NotRequired[list[str]]
    requirements_files: NotRequired[list[pathlib.Path]]
    env: NotRequired[dict[str, str]]
    system_site_packages: NotRequired[bool]
    pip_requirement: NotRequired[str]
    setuptools_requirement: NotRequired[str]


def _cast_to_pathlib_path(value):
    if isinstance(value, pathlib.Path):
        return value
    return pathlib.Path(str(value))


@attr.s(frozen=True, slots=True)
class VirtualEnv:
    """
    Helper class to create and user virtual environments.
    """

    name: str = attr.ib()
    ctx: Context = attr.ib()
    requirements: list[str] | None = attr.ib(repr=False, default=None)
    requirements_files: list[pathlib.Path] | None = attr.ib(repr=False, default=None)
    env: dict[str, str] | None = attr.ib(default=None)
    system_site_packages: bool = attr.ib(default=False)
    pip_requirement: str = attr.ib(repr=False)
    setuptools_requirement: str = attr.ib(repr=False)
    environ: dict[str, str] = attr.ib(init=False, repr=False)
    venv_dir: pathlib.Path = attr.ib(init=False)
    venv_python: pathlib.Path = attr.ib(init=False, repr=False)
    venv_bin_dir: pathlib.Path = attr.ib(init=False, repr=False)
    requirements_hash: str = attr.ib(init=False, repr=False)

    @pip_requirement.default
    def _default_pip_requiremnt(self):
        return "pip>=22.3.1,<23.0"

    @setuptools_requirement.default
    def _default_setuptools_requirement(self):
        # https://github.com/pypa/setuptools/commit/137ab9d684075f772c322f455b0dd1f992ddcd8f
        return "setuptools>=65.6.3,<66"

    @venv_dir.default
    def _default_venv_dir(self):
        if "TOOLS_VIRTUALENVS_PATH" in os.environ:
            base_path = pathlib.Path(os.environ["TOOLS_VIRTUALENVS_PATH"])
        else:
            base_path = CWD
        venvs_path = base_path / ".tools-venvs"
        venvs_path.mkdir(exist_ok=True)
        return venvs_path / self.name

    @environ.default
    def _default_environ(self):
        environ = os.environ.copy()
        if self.env:
            environ.update(self.env)
        return environ

    @venv_python.default
    def _default_venv_python(self):
        if sys.platform.startswith("win"):
            return self.venv_dir / "Scripts" / "python.exe"
        return self.venv_dir / "bin" / "python"

    @venv_bin_dir.default
    def _default_venv_bin_dir(self):
        return self.venv_python.parent

    @requirements_hash.default
    def __default_requirements_hash(self):
        requirements_hash = hashlib.sha256(self.name.encode())
        if self.requirements:
            for requirement in sorted(self.requirements):
                requirements_hash.update(requirement.encode())
        if self.requirements_files:
            for fpath in sorted(self.requirements_files):
                with _cast_to_pathlib_path(fpath).open("rb") as rfh:
                    try:
                        digest = hashlib.file_digest(rfh, "sha256")  # type: ignore[attr-defined]
                    except AttributeError:
                        # Python < 3.11
                        buf = bytearray(2**18)  # Reusable buffer to reduce allocations.
                        view = memoryview(buf)
                        digest = hashlib.sha256()
                        while True:
                            size = rfh.readinto(buf)
                            if size == 0:
                                break  # EOF
                            digest.update(view[:size])
                    requirements_hash.update(digest.digest())
        return requirements_hash.hexdigest()

    def _install_requirements(self):
        requirements_hash_file = self.venv_dir / ".requirements.hash"
        if (
            requirements_hash_file.exists()
            and requirements_hash_file.read_text() == self.requirements_hash
        ):
            # Requirements are up to date
            self.ctx.debug(f"Requirements for virtualenv({self.name}) haven't changed.")
            return
        requirements = []
        if self.requirements_files:
            for fpath in sorted(self.requirements_files):
                requirements.extend(["-r", str(fpath)])
        if self.requirements:
            requirements.extend(sorted(self.requirements))
        if requirements:
            self.ctx.info(f"Install requirements for virtualenv({self.name}) ...")
            self.install(*requirements)
        self.venv_dir.joinpath(".requirements.hash").write_text(self.requirements_hash)

    def _create_virtualenv(self):
        if self.venv_dir.exists():
            self.ctx.debug("Virtual environment path already exists")
            return
        virtualenv = shutil.which("virtualenv")
        if virtualenv:
            cmd = [
                virtualenv,
                f"--python={self.get_real_python()}",
            ]
        else:
            cmd = [
                self.get_real_python(),
                "-m",
                "venv",
            ]
        if self.system_site_packages:
            cmd.append("--system-site-packages")
        cmd.append(str(self.venv_dir))
        self.ctx.info(f"Creating virtualenv({self.name}) in {self.venv_dir.relative_to(CWD)}")
        self.run(*cmd, cwd=str(self.venv_dir.parent))
        self.install(
            "-U",
            self.pip_requirement,
            self.setuptools_requirement,
        )

    def __enter__(self):
        """
        Creates the virtual environment when entering context.
        """
        try:
            self._create_virtualenv()
        except subprocess.CalledProcessError:
            raise AssertionError("Failed to create virtualenv")
        self._install_requirements()
        return self

    def __exit__(self, *args):
        """
        Exit the virtual environment context.
        """

    def install(self, *args, **kwargs):
        """
        Install the passed python packages.
        """
        return self.run(self.venv_python, "-m", "pip", "install", *args, **kwargs)

    def uninstall(self, *args, **kwargs):
        """
        Uninstall the passed python packages.
        """
        return self.run(self.venv_python, "-m", "pip", "uninstall", "-y", *args, **kwargs)

    def run(self, *args, **kwargs):
        """
        Run a command in the context of the virtual environment.
        """
        kwargs.setdefault("cwd", CWD)
        env = kwargs.pop("env", None)
        environ = self.environ.copy()
        if env:
            environ.update(env)
        if "PATH" not in environ:
            environ["PATH"] = str(self.venv_bin_dir)
        else:
            environ["PATH"] = f"{self.venv_bin_dir}{os.pathsep}{environ['PATH']}"
        return self.ctx._run(*args, env=environ, **kwargs)

    @staticmethod
    def get_real_python():
        """
        Get the real python binary.

        The reason why the virtualenv creation is proxied by this function is mostly
        because under windows, we can't seem to properly create a virtualenv off of
        another virtualenv(we can on linux) and also because, we really don't want to
        test virtualenv creation off of another virtualenv, we want a virtualenv created
        from the original python.
        Also, on windows, we must also point to the virtualenv binary outside the existing
        virtualenv because it will fail otherwise
        """
        try:
            if sys.platform.startswith("win"):
                return os.path.join(sys.real_prefix, os.path.basename(sys.executable))
            else:
                python_binary_names = [
                    "python{}.{}".format(*sys.version_info),
                    "python{}".format(*sys.version_info),
                    "python",
                ]
                for binary_name in python_binary_names:
                    python = os.path.join(sys.real_prefix, "bin", binary_name)  # type: ignore[attr-defined]
                    if os.path.exists(python):
                        break
                else:
                    raise AssertionError(
                        "Couldn't find a python binary name under '{}' matching: {}".format(
                            os.path.join(sys.real_prefix, "bin"),  # type: ignore[attr-defined]
                            python_binary_names,
                        )
                    )
                return python
        except AttributeError:
            return sys.executable

    def run_code(self, code_string, python=None, **kwargs):
        """
        Run a code string against the virtual environment.
        """
        if code_string.startswith("\n"):
            code_string = code_string[1:]
        code_string = textwrap.dedent(code_string).rstrip()
        log.debug("Code to run passed to python:\n>>>>>>>>>>\n%s\n<<<<<<<<<<", code_string)
        if python is None:
            python = str(self.venv_python)
        return self.run(python, "-c", code_string, **kwargs)

    def get_installed_packages(self):
        """
        Get the installed packages in the virtual environment.
        """
        data = {}
        ret = self.run(str(self.venv_python), "-m", "pip", "list", "--format", "json")
        for pkginfo in json.loads(ret.stdout):
            data[pkginfo["name"]] = pkginfo["version"]
        return data
