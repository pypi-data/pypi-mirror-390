from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from enum import IntEnum, unique
from math import ceil, floor
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

    from typing_extensions import Self  # upgrade: py3.10: import from typing

TRUE_VAR = {"0", "false", "no"}


@unique
class SGRCodes(IntEnum):
    RESET = 0

    BOLD = 1
    ITALIC = 3
    UNDERLINE = 4
    BLINK = 5
    REVERSE = 7
    CONCEAL = 8

    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    GREY = 37

    BG_BLACK = 40
    BG_RED = 41
    BG_GREEN = 42
    BG_YELLOW = 43
    BG_BLUE = 44
    BG_MAGENTA = 45
    BG_CYAN = 46
    BG_GREY = 47

    BLACK_BRIGHT = 90
    RED_BRIGHT = 91
    GREEN_BRIGHT = 92
    YELLOW_BRIGHT = 93
    BLUE_BRIGHT = 94
    MAGENTA_BRIGHT = 95
    CYAN_BRIGHT = 96
    WHITE_BRIGHT = 97

    BG_BLACK_BRIGHT = 100
    BG_RED_BRIGHT = 101
    BG_GREEN_BRIGHT = 102
    BG_YELLOW_BRIGHT = 103
    BG_BLUE_BRIGHT = 104
    BG_MAGENTA_BRIGHT = 105
    BG_CYAN_BRIGHT = 106
    BG_WHITE_BRIGHT = 107

    @property
    def sequence(self) -> str:
        return f"\033[{self.value}m"


@dataclass(frozen=True, order=True, slots=True)
class SGRString:
    _string: str
    _sgr: tuple[SGRCodes, ...]
    _prefix: str
    _suffix: str
    _force_prefix: bool
    _force_sgr: bool
    _is_error: bool

    def __init__(
        self,
        obj: object,
        *,
        prefix: str = "",
        suffix: str = "",
        params: Iterable[SGRCodes] = (),
        force_prefix: bool = False,
        force_sgr: bool = False,
        is_error: bool = False,
    ) -> None:
        params = tuple(params)
        force_prefix = (
            force_prefix or os.getenv("PY_UTIL_FORCE_PREFIX", "").lower() in TRUE_VAR
        )
        force_sgr = force_sgr or os.getenv("PY_UTIL_FORCE_SGR", "").lower() in TRUE_VAR

        object.__setattr__(self, "_prefix", prefix)
        object.__setattr__(self, "_string", str(obj))
        object.__setattr__(self, "_sgr", params)
        object.__setattr__(self, "_suffix", suffix)
        object.__setattr__(self, "_force_prefix", force_prefix)
        object.__setattr__(self, "_force_sgr", force_sgr)
        object.__setattr__(self, "_is_error", is_error)

    def __str__(self) -> str:
        sgr_prefix = "".join(code.sequence for code in self._sgr)
        sgr_suffix = SGRCodes.RESET.sequence if self._sgr else ""
        return f"{self._prefix}{sgr_prefix}{self._string}{sgr_suffix}{self._suffix}"

    def __len__(self) -> int:
        return len(self._prefix) + len(self._string) + len(self._suffix)

    def __mul__(self, other: object) -> Self:
        if not isinstance(other, int):
            return NotImplemented
        return type(self)(
            self._string * other,
            prefix=self._prefix,
            suffix=self._suffix,
            params=self._sgr,
            force_prefix=self._force_prefix,
            force_sgr=self._force_sgr,
            is_error=self._is_error,
        )

    def __rmul__(self, other: object) -> Self:
        if not isinstance(other, int):
            return NotImplemented
        return type(self)(
            self._string * other,
            prefix=self._prefix,
            suffix=self._suffix,
            params=self._sgr,
            force_prefix=self._force_prefix,
            force_sgr=self._force_sgr,
            is_error=self._is_error,
        )

    def print(self, end: str = os.linesep, *, full_color: bool = False) -> None:
        """Print the command output.

        The command will be printed to stdout if it's not the output of an error,
        otherwise to stderr.

        If the output stream isn't a tty, it will strip the SGR codes and the prefix,
        unless forced to keep them.
        """
        file = sys.stderr if self._is_error else sys.stdout
        if file.isatty():
            prefix = self._prefix
            sgr_prefix = "".join(code.sequence for code in self._sgr)
            sgr_suffix = SGRCodes.RESET.sequence if self._sgr else ""
            suffix = self._suffix
        else:
            prefix = ""
            sgr_prefix = ""
            sgr_suffix = ""
            suffix = ""
            if self._force_sgr:
                sgr_prefix = "".join(code.sequence for code in self._sgr)
                sgr_suffix = SGRCodes.RESET.sequence if self._sgr else ""
            if self._force_prefix:
                prefix = self._prefix
                suffix = self._suffix

        if full_color:
            prefix, sgr_prefix = sgr_prefix, prefix
            suffix, sgr_suffix = sgr_suffix, suffix

        print(
            prefix,
            sgr_prefix,
            self._string,
            sgr_suffix,
            suffix,
            sep="",
            end=end,
            file=file,
        )

    def header(
        self,
        *,
        padding: str = " ",
        left_spaces: int = 1,
        right_spaces: int = 1,
        space: str = " ",
    ) -> None:
        try:
            terminal_size = os.get_terminal_size()
        except OSError:
            # in pseudo-terminals an OSError is thrown
            self.print()
            return

        columns = terminal_size.columns
        title_length = left_spaces + len(self) + right_spaces
        if title_length >= columns:
            self.print()
            return

        half = (columns - title_length) / 2
        prefix = f"{padding * ceil(half)}{space * left_spaces}{self._prefix}"
        suffix = f"{self._suffix}{space * right_spaces}{padding * floor(half)}"
        type(self)(self._string, prefix=prefix, suffix=suffix, params=self._sgr).print()


@dataclass(frozen=True, order=True, slots=True)
class SGROutput:
    _strings: tuple[SGRString, ...]

    def __init__(
        self,
        strings: Iterable[object],
        *,
        force_prefix: bool | None = None,
        force_sgr: bool | None = None,
        is_error: bool | None = None,
    ) -> None:
        strings = tuple(
            self._clean_string(
                string,
                force_prefix=force_prefix,
                force_sgr=force_sgr,
                is_error=is_error,
            )
            for string in strings
        )

        object.__setattr__(self, "_strings", strings)

    @staticmethod
    def _clean_string(
        string: object,
        *,
        force_prefix: bool | None,
        force_sgr: bool | None,
        is_error: bool | None,
    ) -> SGRString:
        if not isinstance(string, SGRString):
            string = SGRString(string)
        force_prefix = (
            string._force_prefix  # noqa: SLF001
            if force_prefix is None
            else force_prefix
        )
        force_sgr = (
            string._force_sgr if force_sgr is None else force_sgr  # noqa: SLF001
        )
        is_error = string._is_error if is_error is None else is_error  # noqa: SLF001
        return SGRString(
            string._string,  # noqa: SLF001
            prefix=string._prefix,  # noqa: SLF001
            suffix=string._suffix,  # noqa: SLF001
            params=string._sgr,  # noqa: SLF001
            force_prefix=force_prefix,
            force_sgr=force_sgr,
            is_error=is_error,
        )

    def print(self, sep: str = "", end: str = os.linesep) -> None:
        n = len(self._strings)
        for index, string in enumerate(self._strings, start=1):
            current_end = end if index == n else sep
            string.print(end=current_end)

    def header(
        self,
        *,
        padding: str = " ",
        left_spaces: int = 1,
        right_spaces: int = 1,
        space: str = " ",
    ) -> None:
        n = len(self._strings)
        if n > 1:
            msg = "Only one string is allowed for the header"
            raise ValueError(msg)

        self._strings[0].header(
            padding=padding,
            left_spaces=left_spaces,
            right_spaces=right_spaces,
            space=space,
        )
