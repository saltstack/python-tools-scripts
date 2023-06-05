from __future__ import annotations

import os
import pathlib
import sys
from typing import TYPE_CHECKING

import ptscripts.logs
from ptscripts.parser import Context
from ptscripts.parser import DefaultToolsPythonRequirements
from ptscripts.parser import DefaultVirtualEnv
from ptscripts.parser import RegisteredImports
from ptscripts.parser import command_group

if TYPE_CHECKING:
    from ptscripts.parser import DefaultRequirementsConfig
    from ptscripts.virtualenv import VirtualEnvConfig

__all__ = ["command_group", "register_tools_module", "Context"]


def register_tools_module(import_module: str, venv_config: VirtualEnvConfig | None = None) -> None:
    """
    Register a module to be imported when instantiating the tools parser.
    """
    RegisteredImports.register_import(import_module, venv_config=venv_config)


def set_default_virtualenv_config(venv_config: VirtualEnvConfig) -> None:
    """
    Define the default tools virtualenv configuration.
    """
    DefaultVirtualEnv.set_default_virtualenv_config(venv_config)


def set_default_requirements_config(reqs_config: DefaultRequirementsConfig) -> None:
    """
    Define the default tools requirements configuration.
    """
    DefaultToolsPythonRequirements.set_default_requirements_config(reqs_config)
