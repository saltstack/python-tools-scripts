from __future__ import annotations

import hashlib
import os
import pathlib
import sys
from functools import cached_property
from typing import TYPE_CHECKING

from pydantic import BaseModel
from pydantic import Field

from ptscripts.utils import cast_to_pathlib_path
from ptscripts.utils import file_digest

if TYPE_CHECKING:
    from ptscripts.parser import Context


class _PipMixin(BaseModel):
    """
    Pip dependencies support.
    """

    requirements: list[str] = Field(default_factory=list)
    requirements_files: list[pathlib.Path] = Field(default_factory=list)
    install_args: list[str] = Field(default_factory=list)
    pip_requirement: str = Field(default="pip>=22.3.1,<23.0")
    setuptools_requirement: str = Field(default="setuptools>=65.6.3,<66")

    def _get_config_hash(self) -> bytes:
        """
        Return a hash digest of the configuration.
        """
        config_hash = hashlib.sha256()
        config_hash.update(self.pip_requirement.encode())
        config_hash.update(self.setuptools_requirement.encode())
        for argument in self.install_args:
            config_hash.update(argument.encode())
        for requirement in sorted(self.requirements):
            config_hash.update(requirement.encode())
        for fpath in sorted(self.requirements_files):
            config_hash.update(file_digest(cast_to_pathlib_path(fpath)))
        return config_hash.digest()

    def _install(self, ctx: Context, python_executable: str | None = None) -> None:
        """
        Install requirements.
        """
        if python_executable is None:
            python_executable = sys.executable
        args = []
        if self.requirements_files:
            for fpath in self.requirements_files:
                args.extend(["-r", str(fpath)])
        if self.requirements:
            args.extend(self.requirements)
        ctx.info("Installing base tools requirements ...")
        ctx.run(
            python_executable,
            "-m",
            "pip",
            "install",
            *self.install_args,
            *args,
        )

    def _setup_venv(self, ctx: Context, python_executable: str | None = None) -> None:
        """
        Setup the virtual environment.
        """
        if python_executable is None:
            python_executable = sys.executable
        ctx.info("Setting up virtual environment ...")
        ctx.run(
            python_executable,
            "-m",
            "pip",
            "install",
            self.pip_requirement,
            self.setuptools_requirement,
        )


class _PoetryMixin(BaseModel):
    """
    Poetry dependencies support.
    """

    no_root: bool = Field(default=True)
    groups: list[str] = Field(default_factory=list)
    install_args: list[str] = Field(default_factory=list)
    poetry_requirement: str = Field(default="poetry>=1.8.0")

    def _get_config_hash(self) -> bytes:
        """
        Return a hash of the configuration.
        """
        config_hash = hashlib.sha256()
        config_hash.update(self.poetry_requirement.encode())
        config_hash.update(str(self.no_root).encode())
        for argument in self.install_args:
            config_hash.update(argument.encode())
        for group in self.groups:
            config_hash.update(group.encode())

        # Late import to avoid circular import errors
        from ptscripts.__main__ import CWD

        config_hash.update(file_digest(CWD / "poetry.lock"))
        return config_hash.digest()

    def _install(self, ctx: Context, python_executable: str | None = None) -> None:
        """
        Install default requirements.
        """
        if python_executable is None:
            python_executable = sys.executable
        args: list[str] = []
        if self.no_root is True:
            args.append("--no-root")
        args.extend(f"--with={group}" for group in self.groups)
        ctx.info("Installing requirements ...")
        ctx.run(python_executable, "-m", "poetry", "install", *self.install_args, *args)

    def _setup_venv(self, ctx: Context, python_executable: str | None = None) -> None:
        """
        Setup the virtual environment.
        """
        if python_executable is None:
            python_executable = sys.executable
        ctx.info("Setting up virtual environment ...")
        ctx.run(
            python_executable,
            "-m",
            "pip",
            "install",
            *self.install_args,
            self.poetry_requirement,
        )


class _LockTimeoutMixin(BaseModel):
    """
    Mixin class to provide the lock timeout field.
    """

    lock_timeout_seconds: int = Field(default=5 * 60)


class DefaultConfig(_LockTimeoutMixin, BaseModel):
    """
    Default tools configuration model.
    """

    def _get_config_hash(self) -> bytes:
        """
        Return a hash of the configuration.
        """
        raise NotImplementedError

    def _install(self, ctx: Context, python_executable: str | None = None) -> None:
        """
        Install default requirements.
        """
        raise NotImplementedError

    def _setup_venv(self, ctx: Context, python_executable: str | None = None) -> None:
        """
        Setup the virtual environment.
        """
        raise NotImplementedError

    @cached_property
    def config_hash(self) -> str:
        """
        Returns a sha256 hash of the requirements.
        """
        config_hash = hashlib.sha256()
        # The first part of the hash should be the path to the tools executable
        config_hash.update(sys.argv[0].encode())
        # The second, TOOLS_VIRTUALENV_CACHE_SEED env variable, if set
        hash_seed = os.environ.get("TOOLS_VIRTUALENV_CACHE_SEED", "")
        config_hash.update(hash_seed.encode())
        config_hash.update(self._get_config_hash())
        return config_hash.hexdigest()

    def install(self, ctx: Context) -> None:
        """
        Install default requirements.
        """
        from ptscripts.__main__ import TOOLS_VENVS_PATH

        config_hash_file = TOOLS_VENVS_PATH / ".default-config.hash"
        if config_hash_file.exists() and config_hash_file.read_text() == self.config_hash:
            # Requirements are up to date
            ctx.debug(
                f"Base tools requirements haven't changed. Hash file: '{config_hash_file}'; "
                f"Hash: '{self.config_hash}'"
            )
            return

        self._install(ctx)

        config_hash_file.parent.mkdir(parents=True, exist_ok=True)
        config_hash_file.write_text(self.config_hash)
        ctx.debug(f"Wrote '{config_hash_file}' with contents: '{self.config_hash}'")

    def setup_venv(self, ctx: Context, python_executable: str | None = None) -> None:
        """
        Setup the virtual environment.
        """
        self._setup_venv(ctx, python_executable=python_executable)


class DefaultPipConfig(_PipMixin, DefaultConfig):
    """
    Default tools pip configuration model.
    """


class DefaultPoetryConfig(_PoetryMixin, DefaultConfig):
    """
    Default tools poetry configuration model.
    """


class VirtualEnvConfig(_LockTimeoutMixin, BaseModel):
    """
    Virtualenv Configuration Typing.
    """

    name: str = Field(default=None)
    env: dict[str, str] = Field(default=None)
    system_site_packages: bool = Field(default=False)
    add_as_extra_site_packages: bool = Field(default=False)

    def _get_config_hash(self) -> bytes:
        """
        Return a hash of the configuration.
        """
        raise NotImplementedError

    def _install(self, ctx: Context, python_executable: str | None = None) -> None:
        """
        Install default requirements.
        """
        raise NotImplementedError

    def _setup_venv(self, ctx: Context, python_executable: str | None = None) -> None:
        """
        Setup the virtual environment.
        """
        raise NotImplementedError

    def get_config_hash(self) -> str:
        """
        Return a hash digest of the configuration.
        """
        config_hash = hashlib.sha256()
        # The first part of the hash should be the path to the tools executable
        config_hash.update(sys.argv[0].encode())
        # The second, TOOLS_VIRTUALENV_CACHE_SEED env variable, if set
        hash_seed = os.environ.get("TOOLS_VIRTUALENV_CACHE_SEED", "")
        config_hash.update(hash_seed.encode())
        config_hash.update(self._get_config_hash())
        return config_hash.hexdigest()

    def install(self, ctx: Context, python_executable: str | None = None) -> None:
        """
        Install requirements.
        """
        self._install(ctx, python_executable=python_executable)

    def setup_venv(self, ctx: Context, python_executable: str | None = None) -> None:
        """
        Setup the virtual environment.
        """
        self._setup_venv(ctx, python_executable=python_executable)


class VirtualEnvPipConfig(_PipMixin, VirtualEnvConfig):
    """
    Virtualenv pip configuration.
    """


class VirtualEnvPoetryConfig(_PoetryMixin, VirtualEnvConfig):
    """
    Virtualenv poetry configuration.
    """
