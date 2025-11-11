"""Module exposing a context manager to run code in a separate process."""

from __future__ import annotations

import inspect
import os
import sys
import traceback
from dataclasses import dataclass
from selectors import EVENT_READ, PollSelector
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types import FrameType
    from typing import Self


class _InTheParent(Exception):
    """Internal exception to tell the parent that it should **not** run the code."""


@dataclass
class ExitInfo:
    """Represents the exit information of a process.

    Its exit code (up to 255), signal received (up to 127), and if a
    core dump has been produced.
    """

    code: int
    signal: int
    has_core_dump: bool

    @classmethod
    def from_exit_info(cls, exit_info):
        return cls(
            code=exit_info >> 8,
            signal=exit_info & 0x7F,
            has_core_dump=bool(exit_info & 0b10000000),
        )


class Forking:
    """Context manager to run code in a different process."""

    rout: int
    rerr: int
    exit: ExitInfo
    frame: FrameType
    pid: int

    def __init__(self) -> None:
        self.stdout: list[bytes] = []
        self.stderr: list[bytes] = []

    def tracer_cb(self, frame, event, arg):
        if frame is self.frame and event == "opcode":
            raise _InTheParent

    def __enter__(self) -> Self:
        self.stdout = []
        self.stderr = []
        self.rout, wout = os.pipe()
        self.rerr, werr = os.pipe()
        self.pid = os.fork()
        if self.pid:
            os.close(wout)
            os.close(werr)
            current_frame = inspect.currentframe()
            assert current_frame
            assert current_frame.f_back
            self.frame = current_frame.f_back
            self.frame.f_trace = self.tracer_cb
            self.frame.f_trace_opcodes = True
            sys.settrace(self.tracer_cb)
            return self
        else:
            os.dup2(wout, 1)
            os.dup2(werr, 2)
            os.close(wout)
            os.close(werr)
            return self

    def __exit__(self, exc_type, exc_value, tb):
        if self.pid == 0:
            return self.child_leaving(exc_type, exc_value, tb)
        else:
            return self.parent_leaving(exc_type)

    def child_leaving(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(None, value=exc_value, tb=tb)
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(0)

    def parent_leaving(self, exc_type):
        """Parent should always leave with an _InTheParent exception."""
        if exc_type is not _InTheParent:
            return False
        with PollSelector() as selector:
            selector.register(self.rout, EVENT_READ)
            selector.register(self.rerr, EVENT_READ)
            while selector.get_map():
                ready = selector.select(1)
                for key, _events in ready:
                    data = os.read(key.fd, 32768)
                    if not data:
                        selector.unregister(key.fd)
                        os.close(key.fd)
                    if key.fd == self.rout:
                        self.stdout.append(data)
                    if key.fd == self.rerr:
                        self.stderr.append(data)
        _pid, exit_info = os.wait()
        self.exit = ExitInfo.from_exit_info(exit_info)

        self.stdout = b"".join(self.stdout)
        self.stderr = b"".join(self.stderr)
        return True
