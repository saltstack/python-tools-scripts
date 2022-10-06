from __future__ import annotations

import logging
import sys

from ptscripts.parser import Parser

log = logging.getLogger(__name__)


def main():
    """
    Main CLI entry-point for python tools scripts.
    """
    parser = Parser()
    cwd = str(parser.repo_root)
    log.debug(f"Searching for tools in {cwd}")
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
