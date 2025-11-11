from __future__ import annotations

import time
import typing
import weakref


class ThrottlerProtocol(typing.Protocol):
    def is_throttled(self, key: str) -> bool: ...


class _Hashable(typing.Protocol):
    def __hash__(self) -> int: ...


class _Link:
    """A link in a doubly-linked list"""

    __slots__ = "at", "previous", "next", "__weakref__"
    previous: "_Link" | None
    next: "_Link" | None
    at: float | None


class TimeThrottler:
    """A throttler for time-based throttling.

    The intuition is that if we determine that a particular key is no longer throttled,
    then it follows that any key that came before it (i.e. any key that was throttled
    with an earlier timestamp) is also no longer throttled. Thus it is possible to save
    memory by clearing multiple keys simultaneously.

    This is achieved by maintaining two data structures:
    * A doubly-linked list of ``_Link``.
    * A ``weakref.WeakValueDictionary`` mapping keys to links in the list.

    In each ``_Link`` of the doubly-linked list we store:
    * The timestamp observed when a ``key`` is throttled.
    * A weak reference to the ``next`` ``_Link``, which will contain the registered
        timestamp for the next ``key`` that was throttled.
    * A strong reference to the ``previous`` ``_Link``, which will contain the
        registered timestamp for the ``key`` that was just previously throttled.

    The idea is that there is only one strong reference to each link: In the link that
    comes next in the list. This allows preserving memory by dropping multiple keys from
    the list simultaneously by dropping a single link in the list. By dropping a single
    link, we will drop the only strong reference to the previous link, thus it will also
    be garbage collected, and this will subsequently drop the only reference to the
    previous link of the previous link, which will also be garbage collected, and so on.

    This design was inspired by ``collections.OrderedDict``.
    """

    def __init__(self, every_seconds: int | float) -> None:
        self.every = every_seconds

        self._last: _Link | None = None
        self._indexes = weakref.WeakValueDictionary()

    def is_throttled(self, key: _Hashable) -> bool:
        """Determine whether *key* is throttled.

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
            if self._last == link:
                # Unset '_last' otherwise we will still be holding a strong reference to
                # 'link' and it won't be GC'd.
                self._last = None

            del link

            return False

        return True


class CountThrottler:
    """A throttler based on the count of times a key was seen."""

    def __init__(self, every: int) -> None:
        self.every = every

        self._counts = {}

    def is_throttled(self, key: _Hashable) -> bool:
        """Determine whether *key* is throttled.

        Examples:
            >>> ct = CountThrottler(every=2)
            >>> ct.is_throttled("event")
            False
            >>> ct.is_throttled("event")
            True
            >>> ct.is_throttled("event")
            False
        """
        if key not in self._counts:
            self._counts[key] = self.every

        current = self._counts[key]
        if current % self.every == 0:
            should_throttle = False
        else:
            should_throttle = True

        if current - 1 == 0:
            del self._counts[key]
        else:
            self._counts[key] = current - 1

        return should_throttle
