from __future__ import annotations

import os
import pathlib
import sys
from typing import TYPE_CHECKING

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


def register_tools_module(import_module: str, venv_config: VirtualEnvConfig | None = None) -> None:
    """
    Register a module to be imported when instantiating the tools parser.
    """
    if venv_config and not isinstance(venv_config, VirtualEnvConfig):
        msg = (
            "The 'venv_config' keyword argument must be an instance "
            f"of '{VirtualEnvConfig.__module__}.VirtualEnvConfig'"
        )
        raise RuntimeError(msg)
    RegisteredImports.register_import(import_module, venv_config=venv_config)


def set_default_virtualenv_config(venv_config: VirtualEnvConfig) -> None:
    """
    Define the default tools virtualenv configuration.
    """
    if venv_config and not isinstance(venv_config, VirtualEnvConfig):
        msg = (
            "The 'venv_config' keyword argument must be an instance "
            f"of '{VirtualEnvConfig.__module__}.VirtualEnvConfig'"
        )
        raise RuntimeError(msg)
    DefaultVirtualEnv.set_default_virtualenv_config(venv_config)


def set_default_config(config: DefaultConfig) -> None:
    """
    Define the default tools requirements configuration.
    """
    if config and not isinstance(config, DefaultConfig):
        msg = f"The 'config' keyword argument must be an instance of '{DefaultConfig.__module__}.DefaultConfig'"
        raise RuntimeError(msg)
    DefaultToolsPythonRequirements.set_default_requirements_config(config)
