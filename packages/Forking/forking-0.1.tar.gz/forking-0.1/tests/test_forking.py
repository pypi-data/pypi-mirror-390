"""Tests for the forking module."""

import os
import sys

import pytest

from forking import Forking


def test_exit():
    with Forking():
        os._exit(0)


def test_side_effect():
    i = 1
    with Forking():
        i += 1
    assert i == 1


def test_stdout():
    child = Forking()
    with child:
        print("Youpi")
    assert child.stdout == b"Youpi\n"


def test_stderr():
    child = Forking()
    with child:
        print("Youpi", file=sys.stderr)
    assert child.stderr == b"Youpi\n"


def test_stdout_stderr():
    child = Forking()
    with child:
        print("Youpi", file=sys.stderr)
        print("Pouette", file=sys.stdout)
    assert child.stderr == b"Youpi\n"
    assert child.stdout == b"Pouette\n"


def test_reuse():
    child = Forking()
    with child:
        print("Youpi")
    assert child.stdout == b"Youpi\n"
    with child:
        print("Pouette")
    assert child.stdout == b"Pouette\n"


def test_pid():
    child = Forking()
    parent_pid = os.getpid()
    with child:
        print(os.getpid(), end="")
    first_child_pid = int(child.stdout)
    with child:
        print(os.getpid(), end="")
    second_child_pid = int(child.stdout)
    assert parent_pid != first_child_pid
    assert first_child_pid != second_child_pid


def test_exc():
    child = Forking()
    with child:
        raise ZeroDivisionError

    assert b"Traceback" in child.stderr
    assert b"ZeroDivisionError" in child.stderr


@pytest.mark.parametrize("exit_status", [0, 1, 2, 5, 10])
def test_exit_status(exit_status):
    child = Forking()
    with child:
        os._exit(exit_status)

    assert child.exit.code == exit_status


@pytest.mark.parametrize("exit_signal", [9, 15])
def test_exit_signal(exit_signal):
    child = Forking()
    with child:
        os.kill(os.getpid(), exit_signal)
    assert child.exit.signal == exit_signal


def test_exit_signal_with_core_dump():
    child = Forking()
    with child:
        os.kill(os.getpid(), 3)
    assert child.exit.signal == 3
    assert child.exit.has_core_dump
