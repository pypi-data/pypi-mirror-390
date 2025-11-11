from __future__ import annotations

import logging

from structlog import DropEvent
from structlog.typing import EventDict

from .throttlers import CountThrottler, ThrottlerProtocol, TimeThrottler

__all__ = [
    "LogThrottler",
    "LogTimeThrottler",
    "CountThrottler",
]


class LogThrottler:
    """Drop logs when throttled based on *throttler*.

    This should generally be close to the top of your processor chain so that a log that
    will ultimately be throttled is not processed further.

    Args:
        key: Unique key in the *event_dict* to determine if log should be throttled.
        throttler:
            A ``ThrottlerProtocol`` implementation to decide if *key should be
            throttled.
    """

    def __init__(
        self,
        key: str,
        throttler: ThrottlerProtocol,
    ):
        self.key = key
        self.throttler = throttler

    def __call__(self, _: logging.Logger, __: str, event_dict: EventDict) -> EventDict:
        if self.throttler.is_throttled(event_dict[self.key]):
            raise DropEvent
        return event_dict


class LogTimeThrottler:
    """Drop logs when throttled based on time in between calls.

    This is a convinience class to initialize a ``LogThrottler`` with a
    ``TimeThrottler``.

    Args:
        key: Unique key in the *event_dict* to determine if log should be throttled.
        every_seconds: How long to throttle logs for, in seconds.
    """

    def __init__(self, key: str, every_seconds: int | float) -> None:
        self.key = key
        self.throttler = TimeThrottler(every_seconds)

    def __call__(self, _: logging.Logger, __: str, event_dict: EventDict) -> EventDict:
        if self.throttler.is_throttled(event_dict[self.key]):
            raise DropEvent
        return event_dict


class LogCountThrottler:
    """Drop logs when throttled based on the number of times *key* was in a log call.

    This is a convinience class to initialize a ``LogThrottler`` with a
    ``CountThrottler``.

    Args:
        key: Unique key in the *event_dict* to determine if log should be throttled.
        every: How frequently to throttle logs.
    """

    def __init__(self, key: str, every: int) -> None:
        self.key = key
        self.throttler = CountThrottler(every)

    def __call__(self, _: logging.Logger, __: str, event_dict: EventDict) -> EventDict:
        if self.throttler.is_throttled(event_dict[self.key]):
            raise DropEvent
        return event_dict
