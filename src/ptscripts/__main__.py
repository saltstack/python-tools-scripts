from __future__ import annotations

import logging
import sys

from rich.console import Console
from rich.logging import RichHandler

from ptscripts.parser import Parser

FORMAT = "%(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=FORMAT,
    datefmt="[%X]",
    handlers=[
        RichHandler(
            console=Console(stderr=True),
            markup=True,
            rich_tracebacks=True,
        ),
    ],
)


def main():
    """
    Main CLI entry-point for python tools scripts.
    """
    parser = Parser()
    cwd = str(parser.repo_root)
    if cwd in sys.path:
        sys.path.remove(cwd)
    sys.path.insert(0, cwd)
    try:
        import tools  # noqa: F401
    except ImportError:
        # No tools/ directory in the current CWD
        pass

    parser.parse_args()


if __name__ == "__main__":
    main()
