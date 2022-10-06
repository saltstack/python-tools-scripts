from __future__ import annotations

import asyncio.events
import asyncio.streams
import asyncio.subprocess
import logging
import os
import subprocess
import sys
from datetime import datetime
from datetime import timedelta
from typing import cast
from typing import TYPE_CHECKING

from . import logs

log = logging.getLogger(__name__)


class Process(asyncio.subprocess.Process):  # noqa: D101
    def __init__(self, *args, no_output_timeout_secs: int | timedelta | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        no_output_timeout_task = None
        if isinstance(no_output_timeout_secs, int):
            assert no_output_timeout_secs >= 1
            no_output_timeout_secs = timedelta(seconds=no_output_timeout_secs)
        elif isinstance(no_output_timeout_secs, timedelta):
            assert no_output_timeout_secs >= timedelta(seconds=1)
        if no_output_timeout_secs is not None:
            no_output_timeout_task = self._loop.create_task(  # type: ignore[attr-defined]
                self._check_no_output_timeout()
            )
        self._no_output_timeout_secs = no_output_timeout_secs
        self._no_output_timeout_task = no_output_timeout_task

    async def _check_no_output_timeout(self):
        self._protocol._last_write = datetime.utcnow()  # type: ignore[attr-defined]
        try:
            while self.returncode is None:
                await asyncio.sleep(1)
                last_write = self._protocol._last_write  # type: ignore[attr-defined]
                if TYPE_CHECKING:
                    assert self._no_output_timeout_secs
                if last_write + self._no_output_timeout_secs < datetime.utcnow():
                    try:
                        self.terminate()
                        log.warning(
                            "No output on has been seen for over %s second(s). "
                            "Terminating process.",
                            self._no_output_timeout_secs.seconds,
                        )
                    except ProcessLookupError:
                        pass
                    break
        except asyncio.CancelledError:
            pass

    async def _cancel_no_output_timeout_task(self):
        task = self._no_output_timeout_task
        if task is None:
            return
        self._no_output_timeout_task = None
        if task.done():
            return
        if not task.cancelled():
            task.cancel()
        await task

    async def wait(self):
        """
        Wait until the process exit and return the process return code.
        """
        retcode = await super().wait()
        await self._cancel_no_output_timeout_task()
        return retcode


class SubprocessStreamProtocol(asyncio.subprocess.SubprocessStreamProtocol):  # noqa: D101
    def __init__(self, *args, capture=False, **kwargs):
        super().__init__(*args, **kwargs)
        self._capture = capture
        self._last_write = None

    def pipe_data_received(self, fd, data):  # noqa: D102
        self._last_write = datetime.utcnow()
        if self._capture:
            super().pipe_data_received(fd, data)
            return
        data = data.decode("utf-8")
        if logs.include_timestamps() or "CI" in os.environ:
            if not data.strip():
                return
            if fd == 1:
                log.stdout(data)  # type: ignore[attr-defined]
            else:
                log.stderr(data)  # type: ignore[attr-defined]
        else:
            if fd == 1:
                sys.stdout.write(data)
                sys.stdout.flush()
            else:
                sys.stderr.write(data)
                sys.stderr.flush()


async def _create_subprocess_exec(
    program,
    *args,
    stdin=None,
    stdout=None,
    stderr=None,
    limit=asyncio.streams._DEFAULT_LIMIT,  # type: ignore[attr-defined]
    no_output_timeout_secs: int | None = None,
    capture: bool = False,
    **kwds,
):
    def protocol_factory():
        return SubprocessStreamProtocol(limit=limit, loop=loop, capture=capture)

    loop = asyncio.events.get_running_loop()
    transport, protocol = await loop.subprocess_exec(
        protocol_factory,
        program,
        *args,
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
        **kwds,
    )
    return Process(transport, protocol, loop, no_output_timeout_secs=no_output_timeout_secs)


async def _subprocess_run(
    f,
    cmdline,
    check=True,
    no_output_timeout_secs: int | None = None,
    capture: bool = False,
):
    stdout = subprocess.PIPE
    stderr = subprocess.PIPE
    proc = await _create_subprocess_exec(
        *cmdline,
        stdout=stdout,
        stderr=stderr,
        stdin=sys.stdin,
        limit=1,
        no_output_timeout_secs=no_output_timeout_secs,
        capture=capture,
    )
    stdout, stderr = await proc.communicate()
    result = subprocess.CompletedProcess(
        args=cmdline,
        stdout=stdout,
        stderr=stderr,
        returncode=proc.returncode,
    )
    f.set_result(result)


def run(
    *cmdline,
    check=True,
    no_output_timeout_secs: int | None = None,
    capture: bool = False,
) -> subprocess.CompletedProcess[str]:
    """
    Run a command.
    """
    loop = asyncio.new_event_loop()
    future = loop.create_future()
    try:
        loop.run_until_complete(
            _subprocess_run(
                future,
                cmdline,
                check,
                no_output_timeout_secs=no_output_timeout_secs,
                capture=capture,
            )
        )
        result = future.result()
        if check is True:
            result.check_returncode()
        return cast(subprocess.CompletedProcess[str], result)
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
