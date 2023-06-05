from __future__ import annotations

import logging
import os
import sys
from typing import NoReturn

from ptscripts.parser import TOOLS_DEPS_PATH
from ptscripts.parser import Parser

if str(TOOLS_DEPS_PATH) in sys.path and sys.path[0] != str(TOOLS_DEPS_PATH):
    sys.path.remove(str(TOOLS_DEPS_PATH))
if TOOLS_DEPS_PATH not in sys.path:
    sys.path.insert(0, str(TOOLS_DEPS_PATH))

log = logging.getLogger(__name__)


def main() -> NoReturn:  # type: ignore[misc]
    """
    Main CLI entry-point for python tools scripts.
    """
    parser = Parser()
    cwd = str(parser.repo_root)
    log.debug("Searching for tools in %s", cwd)
    if cwd in sys.path:
        sys.path.remove(cwd)
    sys.path.insert(0, cwd)
    try:
        import tools  # noqa: F401
    except ImportError as exc:
        if os.environ.get("TOOLS_DEBUG_IMPORTS", "0") == "1":
            raise exc from None

    parser.parse_args()


if __name__ == "__main__":
    main()
