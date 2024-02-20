from __future__ import annotations

import hashlib
import os
import shutil
import sys
import tempfile
from functools import cached_property
from typing import TYPE_CHECKING
from typing import Any

from pydantic import BaseModel
from pydantic import Field
from pydantic import model_validator

from ptscripts.utils import cast_to_pathlib_path
from ptscripts.utils import file_digest

if TYPE_CHECKING:
    import pathlib

    from ptscripts.parser import Context


class Pip(BaseModel):
    """
    Pip dependencies support.
    """

    requirements: list[str] = Field(default_factory=list)
    requirements_files: list[pathlib.Path] = Field(default_factory=list)
    install_args: list[str] = Field(default_factory=list)

    def get_config_hash(self) -> bytes:
        """
        Return a hash digest of the configuration.
        """
        config_hash = hashlib.sha256()
        for argument in self.install_args:
            config_hash.update(argument.encode())
        for requirement in sorted(self.requirements):
            config_hash.update(requirement.encode())
        for fpath in sorted(self.requirements_files):
            config_hash.update(file_digest(cast_to_pathlib_path(fpath)))
        return config_hash.digest()

    def install(self, ctx: Context, python_executable: str | None = None) -> None:
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


class Poetry(BaseModel):
    """
    Poetry dependencies support.
    """

    no_root: bool = Field(default=True)
    groups: list[str] = Field(default_factory=list)
    export_args: list[str] = Field(default_factory=list)
    install_args: list[str] = Field(default_factory=list)

    def get_config_hash(self) -> bytes:
        """
        Return a hash digest of the configuration.
        """
        config_hash = hashlib.sha256()
        config_hash.update(str(self.no_root).encode())
        for argument in self.export_args:
            config_hash.update(argument.encode())
        for argument in self.install_args:
            config_hash.update(argument.encode())
        for group in self.groups:
            config_hash.update(group.encode())

        # Late import to avoid circular import errors
        from ptscripts.__main__ import CWD

        config_hash.update(file_digest(CWD / "poetry.lock"))
        return config_hash.digest()

    def install(self, ctx: Context, python_executable: str | None = None) -> None:
        """
        Install default requirements.
        """
        if python_executable is None:
            python_executable = sys.executable
        with tempfile.NamedTemporaryFile(prefix="reqs-", suffix=".txt") as tfile:
            args: list[str] = []
            if self.no_root is True:
                param_name = "only"
            else:
                param_name = "with"
            args.extend(f"--{param_name}={group}" for group in self.groups)
            args.append(f"--output={tfile.name}")
            poetry = shutil.which("poetry")
            if poetry is None:
                ctx.error("Did not find the 'poetry' binary in path")
                ctx.exit(1)
            ctx.info("Exporting requirements from poetry ...")
            ctx.run(poetry, "export", *self.export_args, *args)
            ctx.info("Installing requirements ...")
            ctx.run(
                python_executable,
                "-m",
                "pip",
                "install",
                *self.install_args,
                "-r",
                tfile.name,
            )


class DefaultConfig(BaseModel):
    """
    Default tools configuration model.
    """

    pip: Pip = Field(default=None)
    poetry: Poetry = Field(default=None)

    @model_validator(mode="before")
    @classmethod
    def _pip_or_poetry_not_both(cls, data: Any) -> Any:
        if isinstance(data, dict) and "poetry" in data and "pip" in data:
            msg = "Only configure 'pip' or 'poetry', not both."
            raise ValueError(msg)
        return data

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
        if self.pip:
            config_hash.update(self.pip.get_config_hash())
        if self.poetry:
            config_hash.update(self.poetry.get_config_hash())

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

        if self.pip:
            self.pip.install(ctx)
        if self.poetry:
            self.poetry.install(ctx)
        config_hash_file.parent.mkdir(parents=True, exist_ok=True)
        config_hash_file.write_text(self.config_hash)
        ctx.debug(f"Wrote '{config_hash_file}' with contents: '{self.config_hash}'")


class VirtualEnvConfig(BaseModel):
    """
    Virtualenv Configuration Typing.
    """

    name: str = Field(default=None)
    env: dict[str, str] = Field(default=None)
    system_site_packages: bool = Field(default=False)
    pip_requirement: str = Field(default="pip>=22.3.1,<23.0")
    setuptools_requirement: str = Field(default="setuptools>=65.6.3,<66")
    poetry_requirement: str = Field(default=">=1.7")
    add_as_extra_site_packages: bool = Field(default=False)
    pip: Pip = Field(default=None)
    poetry: Poetry = Field(default=None)

    @model_validator(mode="before")
    @classmethod
    def _pip_or_poetry_not_both(cls, data: Any) -> Any:
        if isinstance(data, dict) and "poetry" in data and "pip" in data:
            msg = "Only configure 'pip' or 'poetry', not both."
            raise ValueError(msg)
        return data

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
        if self.pip:
            config_hash.update(self.pip.get_config_hash())
        if self.poetry:
            config_hash.update(self.poetry.get_config_hash())

        return config_hash.hexdigest()

    def install(self, ctx: Context, python_executable: str | None = None) -> None:
        """
        Install requirements.
        """
        if self.pip:
            return self.pip.install(ctx, python_executable=python_executable)
        if self.poetry:
            return self.poetry.install(ctx, python_executable=python_executable)
        return None
