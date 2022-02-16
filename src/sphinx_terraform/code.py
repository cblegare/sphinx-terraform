from __future__ import annotations

from typing import NamedTuple


class CodePosition(NamedTuple):
    """
    Define position in a code file, a pair of integers (line, column).
    """

    line: int
    column: int


class CodeSpan(NamedTuple):
    """
    Define a HCL definition within code, a signature and its position.
    """

    start_position: CodePosition
    end_position: CodePosition
