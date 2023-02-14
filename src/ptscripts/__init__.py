from __future__ import annotations

import pathlib

CWD = pathlib.Path.cwd()

import ptscripts.logs
from ptscripts.parser import command_group
from ptscripts.parser import Context, RegisteredImports

__all__ = ["command_group", "register_tools_module", "Context", "CWD"]


def register_tools_module(import_module: str) -> None:
    """
    Register a module to be imported when instantiating the tools parser.
    """
    RegisteredImports.register_import(import_module)
