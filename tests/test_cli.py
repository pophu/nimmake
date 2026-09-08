"""Tests for the CLI module."""

import io
import sys

import pytest

from nimmake.cli import main


def test_hello_default() -> None:
    captured = io.StringIO()
    sys.stdout = captured
    try:
        main(["hello"])
    except SystemExit:
        pass
    finally:
        sys.stdout = sys.__stdout__
    assert "Hello, World!" in captured.getvalue()


# def test_hello_custom() -> None:
#     captured = io.StringIO()
#     sys.stdout = captured
#     try:
#         main(["hello", "Alice"])
#     except SystemExit:
#         pass
#     finally:
#         sys.stdout = sys.__stdout__
#     assert "Hello, Alice!" in captured.getvalue()


# def test_no_command() -> None:
#     with pytest.raises(SystemExit) as exc_info:
#         main([])
#     assert exc_info.value.code == 1


# def test_version() -> None:
#     captured = io.StringIO()
#     sys.stdout = captured
#     try:
#         main(["--version"])
#     except SystemExit:
#         pass
#     finally:
#         sys.stdout = sys.__stdout__
#     assert "nimmake" in captured.getvalue()