from __future__ import annotations

import time
import typing
import weakref


class _Hashable(typing.Protocol):
    def __hash__(self) -> int: ...


class ThrottlerProtocol(typing.Protocol):
    def is_throttled(self, key: str) -> bool: ...


class _Link:
    """A link in a doubly-linked list"""

    __slots__ = "at", "previous", "next", "__weakref__"
    previous: "_Link" | None
    next: "_Link" | None
    at: float | None


class TimeThrottler:
    """A throttler for time-based throttling."""

    def __init__(self, every_seconds: int | float) -> None:
        self.every = every_seconds

        self._last: _Link | None = None
        self._indexes = weakref.WeakValueDictionary()

    def is_throttled(self, key: _Hashable) -> bool:
        """Determine whether ``key`` is throttled.

        Examples:
            >>> tt = TimeThrottler(every_seconds=1)
            >>> tt.is_throttled("event")
            False
            >>> tt.is_throttled("event")
            True
            >>> tt.is_throttled("another-event")
            False
            >>> tt.is_throttled("another-event")
            True
            >>> time.sleep(1)
            >>> tt.is_throttled("event")
            False
            >>> tt.is_throttled("another-event")
            False
        """
        now = time.monotonic()

        if key not in self._indexes:
            new = _Link()
            new.at = now
            # Stores a weak reference
            self._indexes[key] = new

            if self._last:
                # 'next' is a weak reference
                self._last.next = self._indexes[key]
                # 'previous' is not
                new.previous = self._last

            self._last = new

            return False

        link = self._indexes[key]
        if (now - link.at) >= self.every:
            del link
            return False

        return True
