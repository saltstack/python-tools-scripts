from __future__ import annotations

import os
import pathlib
import sys
from typing import TYPE_CHECKING
from typing import Any

from pydantic import NonNegativeFloat

import ptscripts.logs
from ptscripts.models import DefaultConfig
from ptscripts.models import VirtualEnvConfig
from ptscripts.parser import Context
from ptscripts.parser import DefaultToolsPythonRequirements
from ptscripts.parser import DefaultVirtualEnv
from ptscripts.parser import RegisteredImports
from ptscripts.parser import command_group

__all__ = ["command_group", "register_tools_module", "Context"]


def register_tools_module(
    import_module: str, venv_config: VirtualEnvConfig | dict[str, Any] | None = None
) -> None:
    """
    Register a module to be imported when instantiating the tools parser.
    """
    if venv_config and isinstance(venv_config, dict):
        venv_config = VirtualEnvConfig(**venv_config)
    if TYPE_CHECKING:
        assert isinstance(venv_config, VirtualEnvConfig)
    RegisteredImports.register_import(import_module, venv_config=venv_config)


def set_default_virtualenv_config(venv_config: VirtualEnvConfig | dict[str, Any]) -> None:
    """
    Define the default tools virtualenv configuration.
    """
    if venv_config and isinstance(venv_config, dict):
        venv_config = VirtualEnvConfig(**venv_config)
    if TYPE_CHECKING:
        assert isinstance(venv_config, VirtualEnvConfig)
    DefaultVirtualEnv.set_default_virtualenv_config(venv_config)


def set_default_config(config: DefaultConfig | dict[str, Any]) -> None:
    """
    Define the default tools requirements configuration.
    """
    if config and isinstance(config, dict):
        config = DefaultConfig(**config)
    if TYPE_CHECKING:
        assert isinstance(config, DefaultConfig)
    DefaultToolsPythonRequirements.set_default_requirements_config(config)
