from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter_ns
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator
    from types import TracebackType

    from typing_extensions import Self  # upgrade: py3.10: import from typing

METRIC_MULTIPLIER = 1_000
SECONDS_PER_MINUTE = 60
MINUTES_PER_HOUR = 60
HOURS_PER_DAY = 24
SECONDS_PER_DAY = SECONDS_PER_MINUTE * MINUTES_PER_HOUR * HOURS_PER_DAY


@dataclass(frozen=True, order=True, slots=True)
class Timing:
    nanoseconds: int

    def __init__(
        self,
        *,
        days: int = 0,
        seconds: int = 0,
        milliseconds: int = 0,
        microseconds: int = 0,
        nanoseconds: int = 0,
    ) -> None:
        total_nanoseconds = (
            nanoseconds
            + METRIC_MULTIPLIER * microseconds
            + METRIC_MULTIPLIER**2 * milliseconds
            + METRIC_MULTIPLIER**3 * seconds
            + SECONDS_PER_DAY * METRIC_MULTIPLIER**3 * days
        )
        object.__setattr__(self, "nanoseconds", total_nanoseconds)

    def __str__(self) -> str:
        if self.nanoseconds == 0:
            return "0ns"
        sign = "" if self.nanoseconds > 0 else "-"
        nanoseconds = abs(self.nanoseconds)
        if nanoseconds < METRIC_MULTIPLIER:
            return f"{sign}{nanoseconds}ns"
        microseconds = nanoseconds / METRIC_MULTIPLIER
        if microseconds < METRIC_MULTIPLIER:
            return f"{sign}{microseconds:.1f}µs"
        milliseconds = microseconds / METRIC_MULTIPLIER
        if milliseconds < METRIC_MULTIPLIER:
            return f"{sign}{milliseconds:.1f}ms"
        seconds = milliseconds / METRIC_MULTIPLIER
        if seconds < SECONDS_PER_MINUTE:
            return f"{sign}{seconds:.2f}s"
        round_seconds = int(seconds)
        minutes, seconds = divmod(round_seconds, SECONDS_PER_MINUTE)
        hours, minutes = divmod(minutes, MINUTES_PER_HOUR)
        if hours < HOURS_PER_DAY:
            return f"{sign}{hours:02d}:{minutes:02d}:{seconds:02d}"
        days, hours = divmod(hours, HOURS_PER_DAY)
        return f"{sign}{days:,}d {hours:02d}:{minutes:02d}:{seconds:02d}"

    def __bool__(self) -> bool:
        return bool(self.nanoseconds)

    def __neg__(self) -> Self:
        return self.__class__(nanoseconds=-self.nanoseconds)

    def __add__(self, other: object) -> Timing:
        if not isinstance(other, Timing):
            return NotImplemented
        return Timing(nanoseconds=self.nanoseconds + other.nanoseconds)

    def __radd__(self, other: object) -> Timing:
        if not isinstance(other, Timing):
            return NotImplemented
        return Timing(nanoseconds=self.nanoseconds + other.nanoseconds)

    def __sub__(self, other: object) -> Timing:
        if not isinstance(other, Timing):
            return NotImplemented
        return Timing(nanoseconds=self.nanoseconds - other.nanoseconds)

    def __rsub__(self, other: object) -> Timing:
        if not isinstance(other, Timing):
            return NotImplemented
        return Timing(nanoseconds=other.nanoseconds - self.nanoseconds)

    def __mul__(self, other: object) -> Timing:
        if not isinstance(other, int):
            return NotImplemented
        return Timing(nanoseconds=self.nanoseconds * other)

    def __rmul__(self, other: object) -> Timing:
        if not isinstance(other, int):
            return NotImplemented
        return Timing(nanoseconds=self.nanoseconds * other)

    def __floordiv__(self, other: object) -> Timing:
        if not isinstance(other, int):
            return NotImplemented
        return Timing(nanoseconds=self.nanoseconds // other)

    def __truediv__(self, other: object) -> Timing:
        if not isinstance(other, int):
            return NotImplemented
        return Timing(nanoseconds=round(self.nanoseconds / other))


class Stopwatch:
    _start: int
    laps: list[Timing]
    __slots__ = ("_start", "_zero", "laps")

    def __init__(self) -> None:
        self.laps: list[Timing] = []
        self._zero = Timing()

    def __enter__(self) -> Self:
        self._start = perf_counter_ns()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        end = perf_counter_ns()
        self.laps.append(Timing(nanoseconds=end - self._start))
        del self._start

    def __bool__(self) -> bool:
        return bool(self.elapsed)

    def __len__(self) -> int:
        return len(self.laps)

    def __iter__(self) -> Iterator[Timing]:
        return iter(self.laps)

    def reset(self) -> None:
        self.laps.clear()

    @property
    def elapsed(self) -> Timing:
        return sum(self.laps, self._zero)

    @property
    def average(self) -> Timing:
        if not self.laps:
            msg = "No laps recorded"
            raise ZeroDivisionError(msg)
        return self.elapsed // len(self)

    @property
    def min(self) -> Timing:
        return min(self.laps)

    @property
    def max(self) -> Timing:
        return max(self.laps)
