from __future__ import annotations

import logging
import typing

from structlog import DropEvent
from structlog.typing import EventDict

from .throttlers import ThrottlerProtocol, TimeThrottler

_T = typing.TypeVar("_T", bound=ThrottlerProtocol)

__all__ = [
    "LogTimeThrottler",
]


class LogTimeThrottler:
    """Drop logs when throttled based on time in between calls.

    This should generally be close to the top of your processor chain so that processors
    run in a log that will ultimately be throttled.

    Args:
        key: Unique key in the ``event_dict`` to determine if log should be throttled.
        every_seconds: How long to throttle logs for, in seconds.
    """

    def __init__(self, key: str, every_seconds: int | float) -> None:
        self.key = key
        self.throttler = TimeThrottler(every_seconds)

    def __call__(self, _: logging.Logger, __: str, event_dict: EventDict) -> EventDict:
        if self.throttler.is_throttled(event_dict[self.key]):
            raise DropEvent
        return event_dict
