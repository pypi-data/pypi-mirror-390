# *structlog-throttling*: Throttling for *[structlog](https://www.structlog.org/)* loggers

<a href="https://pypi.org/project/structlog-throttling/"><img src="https://img.shields.io/pypi/pyversions/structlog-throttling.svg" alt="Supported Python versions from PyPI." /></a>

Logging offers a trade-off between visibility and performance. A particularly high performance cost can be incurred when logging in each iteration of a loop, common [hot spots](https://en.wikipedia.org/wiki/Hot_spot_%28computer_programming%29) in most programs. A solution to this problem is to space out the log calls such that they only happen every some time instead of on every iteration of the loop. By tweaking the time in between log calls we can move within the visibility-performance trade-off.

*structlog-throttling* brings this solution to *[structlog](https://www.structlog.org/)* in the form of processors to throttle log calls based on time, or call count.

## Getting started

### Installation

Install *structlog-throttling* from PyPI:

```sh
pip install structlog-throttling
```

### Configure

When configuring *structlog*, use one of the processors offered by *structlog-throttling*. I recommend putting the processor close to the beginning of your processor chain, to avoid processing logs that will ultimately be dropped:

```python
import structlog
from structlog_throttling.processors import LogTimeThrottler


structlog.configure(
    processors=[
        # Logs with the same 'event' will only be allowed through every 5 seconds.
        LogTimeThrottler("event", every_seconds=5),
        ...
    ]
)
```

## Examples

Throttle logs based on log level every 5 seconds:

```python
import structlog
from structlog_throttling.processors import LogTimeThrottler


structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        LogTimeThrottler("level", every_seconds=5),
        ...
    ],
)
```
