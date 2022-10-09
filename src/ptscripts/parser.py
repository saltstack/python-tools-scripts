"""
Python tools scripts CLI parser.
"""
from __future__ import annotations

import argparse
import inspect
import logging
import os
import pathlib
import sys
import typing
from collections.abc import Iterator
from contextlib import contextmanager
from functools import partial
from subprocess import CompletedProcess
from types import FunctionType
from types import GenericAlias
from typing import Any
from typing import cast
from typing import TYPE_CHECKING
from typing import TypedDict

import rich
from rich.console import Console
from rich.theme import Theme

from ptscripts import logs
from ptscripts import process

if TYPE_CHECKING:
    from argparse import ArgumentParser
    from argparse import _SubParsersAction

log = logging.getLogger(__name__)


class ArgumentOptions(TypedDict):
    """
    TypedDict class documenting the acceptable keys and their types for arguments.
    """

    flags: list[str]
    help: str
    action: str | argparse.Action
    nargs: int | str
    const: Any
    choices: list[str]
    required: bool
    metavar: str


class FullArgumentOptions(ArgumentOptions):
    """
    TypedDict class documenting the argparse.add_argument names and types.
    """

    dest: str
    type: type[Any]
    default: Any


class Context:
    """
    Context class passed to every command group function as the first argument.
    """

    def __init__(self, parser: Parser):
        self.parser = parser
        self.repo_root = parser.repo_root
        theme = Theme(
            {
                "log-debug": "dim blue",
                "log-info": "dim cyan",
                "log-warning": "magenta",
                "log-error": "bold red",
                "exit-ok": "green",
                "exit-failure": "bold red",
                "logging.level.stdout": "dim blue",
                "logging.level.stderr": "dim red",
            }
        )
        console_kwargs = {
            "theme": theme,
        }
        if os.environ.get("CI"):
            console_kwargs["force_terminal"] = True
            console_kwargs["force_interactive"] = False
        self.console = Console(stderr=True, **console_kwargs)
        self.console_stdout = Console(**console_kwargs)
        rich.reconfigure(stderr=True, **console_kwargs)

    def print(self, *args, **kwargs):
        """
        Print to stdout.
        """
        self.console_stdout.print(*args, **kwargs)

    def debug(self, *args):
        """
        Print debug message to stderr.
        """
        self.console.log(*args, style="log-debug")

    def info(self, *args):
        """
        Print info message to stderr.
        """
        self.console.log(*args, style="log-info")

    def warn(self, *args):
        """
        Print warning message to stderr.
        """
        self.console.log(*args, style="log-warning")

    def error(self, *args):
        """
        Print error message to stderr.
        """
        self.console.log(*args, style="log-error")

    def exit(self, status=0, message=None):
        """
        Exit the command execution.
        """
        if message is not None:
            if status == 0:
                style = "exit-ok"
            else:
                style = "exit-failure"
            self.console.print(message, style=style)
        self.parser.exit(status)

    def run(
        self,
        *cmdline,
        check=True,
        no_output_timeout_secs: int | None = None,
        capture: bool = False,
    ) -> CompletedProcess[str]:
        """
        Run a subprocess.
        """
        return process.run(
            *cmdline,
            check=check,
            no_output_timeout_secs=no_output_timeout_secs,
            capture=capture,
        )

    @contextmanager
    def chdir(self, path: pathlib.Path) -> Iterator[pathlib.Path]:
        """
        Change the current working directory to the provided path.
        """
        cwd = pathlib.Path.cwd()
        try:
            os.chdir(path)
            yield path
        finally:
            if not cwd.exists():
                self.error(f"Unable to change back to path {cwd}")
            else:
                os.chdir(cwd)


class Parser:
    """
    Singleton parser class that wraps argparse.
    """

    _instance: Parser | None = None
    parser: ArgumentParser
    subparsers: _SubParsersAction[ArgumentParser]
    context: Context
    repo_root: pathlib.Path

    def __new__(cls):
        """
        Method that instantiates a singleton class and returns it.
        """
        if cls._instance is None:
            instance = super().__new__(cls)
            instance.repo_root = pathlib.Path.cwd()
            instance.context = Context(instance)
            instance.parser = argparse.ArgumentParser(
                prog="tools",
                description="Python Tools Scripts",
                epilog="These tools are discovered under `<repo-root>/tools`.",
                allow_abbrev=False,
            )
            log_group = instance.parser.add_argument_group("Logging")
            timestamp_meg = log_group.add_mutually_exclusive_group()
            timestamp_meg.add_argument(
                "--timestamps",
                "--ts",
                action="store_true",
                help="Add time stamps to logs",
                dest="timestamps",
            )
            timestamp_meg.add_argument(
                "--no-timestamps",
                "--nts",
                action="store_false",
                default=True,
                help="Remove time stamps from logs",
                dest="timestamps",
            )
            level_group = log_group.add_mutually_exclusive_group()
            level_group.add_argument(
                "--quiet",
                "-q",
                dest="quiet",
                action="store_true",
                default=False,
                help="Disable logging",
            )
            level_group.add_argument(
                "--debug",
                "-d",
                action="store_true",
                default=False,
                help="Show debug messages",
            )
            run_options = instance.parser.add_argument_group(
                "Run Subprocess Options", description="These options apply to ctx.run() calls"
            )
            run_options.add_argument(
                "--no-output-timeout-secs",
                "--nots",
                default=None,
                type=int,
                help="Timeout if no output has been seen for the provided seconds.",
                metavar="SECONDS",
                dest="no_output_timeout_secs",
            )

            instance.subparsers = instance.parser.add_subparsers(
                title="Commands", dest="command", required=True
            )
            cls._instance = instance
        return cls._instance

    def parse_args(self):
        """
        Parse CLI.
        """
        options = self.parser.parse_args()
        if options.quiet:
            logging.root.setLevel(logging.CRITICAL + 1)
        elif options.debug:
            logging.root.setLevel(logging.DEBUG)
        else:
            logging.root.setLevel(logging.INFO)
        if options.timestamps:
            for handler in logging.root.handlers:
                handler.setFormatter(logs.TIMESTAMP_FORMATTER)
        else:
            for handler in logging.root.handlers:
                handler.setFormatter(logs.NO_TIMESTAMP_FORMATTER)
        self.options = options
        if "func" not in options:
            self.context.exit(1, "No command was passed.")
        log.debug(f"CLI parsed options {options}")
        options.func(options)

    def __getattr__(self, attr):
        """
        Proxy unknown attributes to the parser instance.
        """
        return getattr(self.parser, attr)


class CommandGroup:
    """
    Command group which holds the available tool functions.
    """

    def __init__(self, name, help, description=None, parent=None):
        self.name = name
        if description is None:
            description = help
        if parent is None:
            parent = Parser()
        self.parser = parent.subparsers.add_parser(
            name.replace("_", "-"),
            help=help,
            description=description,
        )
        self.subparsers = self.parser.add_subparsers(
            title="Commands",
            dest=f"{name.replace('-', '_')}_command",
        )
        self.context = parent.context

    def command(
        self,
        func: FunctionType | None = None,
        *,
        name: str | None = None,
        help: str | None = None,
        description: str | None = None,
        arguments: dict[str, ArgumentOptions] | None = None,
    ):
        """
        Register a sub-command in the command group.
        """
        if func is None:
            return partial(
                self.command,
                name=name,
                help=help,
                description=description,
                arguments=arguments,
            )

        func_name = func.__name__
        func_file = sys.modules[func.__module__].__file__
        if TYPE_CHECKING:
            assert func_file
        func_path = str(pathlib.Path(func_file).relative_to(self.context.repo_root))

        if name is None:
            name = func_name

        if description is None:
            description = inspect.getdoc(func)
        if help is None and description is not None:
            help = description.splitlines()[0]
        command = self.subparsers.add_parser(name=name, help=help, description=description)

        signature = inspect.signature(func)

        if arguments is None:
            if len(signature.parameters) > 1:
                raise RuntimeError(
                    f"'arguments' is a mandatory keyword argument to the '@{self.name}.command' "
                    "decorator when additional arguments(besides the required 'ctx' as first "
                    "argument) or keyword arguments are defined. Please update the decorated "
                    f"function {func_name!r} in {func_path!r}."
                )
            arguments = {}

        for key in arguments:
            if key not in signature.parameters:
                raise RuntimeError(
                    "Only pass argument names or keyword argument names on the 'arguments' "
                    f"keyword for the '@{self.name}.command' decorated function {func_name!r} "
                    f"in {func_path!r} which are also present in it's signature, {key!r} is "
                    "not present."
                )

        type_annotation = typing.get_type_hints(func)
        first_parameter_seen = False
        for parameter in signature.parameters.values():
            if first_parameter_seen is False:
                first_parameter_seen = True
                if parameter.name != "ctx":
                    raise RuntimeError(
                        f"'ctx' is a mandatory first argument to the '@{self.name}.command' "
                        f"decorated function {func_name!r} in {func_path!r}."
                    )
                continue
            if parameter.annotation is parameter.empty:
                # No typing annotations
                continue

            # Get the correct type for the parameter
            param_type = type_annotation[parameter.name]
            param_type_args = typing.get_args(param_type)
            if param_type_args:
                # This is something like typing.Optional[list[str]]
                # Let's unwrap it to the inner type, which, for the example
                # here is, list[str]
                param_type = param_type_args[0]

            if isinstance(param_type, GenericAlias):
                param_type = typing.get_args(param_type)[0]

            kwargs = cast(FullArgumentOptions, arguments.get(parameter.name) or {})
            if parameter.default is parameter.empty:
                # Positional argument
                kwargs["type"] = param_type
                command.add_argument(parameter.name, **kwargs)
                continue

            if kwargs.get("nargs") == "*":
                # Positional argument
                kwargs["type"] = param_type
                command.add_argument(parameter.name, **kwargs)
                continue

            # Keyword argument
            kwargs["dest"] = parameter.name
            if "type" not in kwargs:
                if param_type is not bool:
                    kwargs["type"] = param_type
                elif "action" not in kwargs:
                    action = None
                    if parameter.default is True:
                        action = "store_false"
                    elif parameter.default is False:
                        action = "store_true"
                    if action is not None:
                        kwargs["action"] = action

            kwargs["default"] = parameter.default
            if "help" in kwargs:
                if parameter.default is not None:
                    if not kwargs["help"].endswith("."):
                        kwargs["help"] += "."
                    kwargs["help"] += " Default %(default)s"
            flags = kwargs.pop("flags", None)  # type: ignore[misc]
            if flags is None:
                flags = [f"--{parameter.name.replace('_', '-')}"]
            log.debug("Adding Command %r. Flags: %s; KwArgs: %s", name, flags, kwargs)
            command.add_argument(*flags, **kwargs)
        command.set_defaults(func=partial(self, func))
        return func

    def __getattr__(self, attr):
        """
        Proxy unknown attributes to the parser instance.
        """
        return getattr(self.parser, attr)

    def __call__(self, func, options):
        """
        Execute the selected tool function.
        """
        signature = inspect.signature(func)
        args = []
        kwargs = {}
        for name, parameter in signature.parameters.items():
            if parameter.annotation is parameter.empty:
                # No typing annotations
                continue
            if name in options:
                if parameter.default is parameter.empty:
                    args.append(getattr(options, name))
                else:
                    kwargs[name] = getattr(options, name)

        bound = signature.bind_partial(*args, **kwargs)
        func(self.context, *bound.args, **bound.kwargs)


def command_group(name: str, help: str, description: str | None = None) -> CommandGroup:
    """
    Create a new command group.
    """
    return CommandGroup(name, help, description=description)
