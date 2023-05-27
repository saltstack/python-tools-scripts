from __future__ import annotations

import pathlib

CWD = pathlib.Path.cwd()

import ptscripts.logs
from ptscripts.parser import command_group
from ptscripts.parser import Context, RegisteredImports, DefaultVirtualenvConfig
from ptscripts.virtualenv import VirtualEnvConfig

__all__ = ["command_group", "register_tools_module", "Context", "CWD"]


def register_tools_module(import_module: str, venv_config: VirtualEnvConfig | None = None) -> None:
    """
    Register a module to be imported when instantiating the tools parser.
    """
    RegisteredImports.register_import(import_module, venv_config=venv_config)


def set_default_venv_config(venv_config: VirtualEnvConfig) -> None:
    """
    Define the default virtualenv configuration.

    This virtualenv will be available to all commands, and it's ``site-packages``
    dir(s) will be added to the current python interpreter site.
    """
    DefaultVirtualenvConfig.set_default_venv_config(venv_config)
