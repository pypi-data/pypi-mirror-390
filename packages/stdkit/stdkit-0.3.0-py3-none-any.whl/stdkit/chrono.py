__all__ = [
    "DateTimeLike",
    "parse",
]

import datetime as dt
from typing import TypeAlias

DateTimeLike: TypeAlias = str | dt.time | dt.date | dt.datetime


def parse(value: DateTimeLike, /, fmt: str | None = None) -> dt.datetime:
    """Return a datetime.datetime object from the given date/time value.

    Parameters
    ----------
    value : DateTimeLike
        A str, time, date, or datetime representing a date/time. Behavior:
        - For str, attempts multiple parsing strategies (see ``fmt``).
        - For datetime.time, returns a datetime with date set to 1900-01-01.
        - For datetime.date, returns a datetime with time to 00:00:00.
        - For datetime.datetime, returns input value unchanged.
    fmt : str, optional
        A format string compatible with :func:`datetime.datetime.strptime`.
        If provided and ``value`` is a string, parsing uses this format only.
        If ``None``, the function will try (in order): ``datetime.fromisoformat``,
        then a set of common ``strptime`` patterns.

    Returns
    -------
    datetime.datetime
        A :class:`datetime.datetime` representing the parsed value.
        If the input is timezone-aware (``tzinfo`` set), that information is preserved;
        otherwise a naive datetime is returned.

    Raises
    ------
    TypeError
        If ``value`` is not one of: ``str``, ``datetime.time``, ``datetime.date``,
        or ``datetime.datetime``.
    ValueError
        If ``value`` is a string but cannot be parsed using the provided ``fmt``
        or any of the fallback strategies.

    Examples
    --------
    >>> from stdkit import chrono
    >>> chrono.parse("2000-01-02T03:04:05.123456")
    datetime.datetime(2000, 1, 2, 3, 4, 5, 123456)

    >>> chrono.parse("2020-10-30")
    datetime.datetime(2020, 10, 30, 0, 0)

    >>> chrono.parse("00:11:22")
    datetime.datetime(1900, 1, 1, 0, 11, 22)
    """
    # direct pass-through for datetime
    if isinstance(value, dt.datetime):
        return value

    # date -> midnight
    if isinstance(value, dt.date):
        return dt.datetime.combine(value, dt.time.min)

    # time -> combine with 1900-01-01 (matches datetime.time behavior)
    if isinstance(value, dt.time):
        return dt.datetime.combine(dt.date(1900, 1, 1), value)

    # strings -> parse
    if isinstance(value, str):
        # 1) explicit format requested
        if fmt is not None:
            try:
                return dt.datetime.strptime(value, fmt)
            except Exception as exc:
                raise ValueError(f"{value=!r} - expected format {fmt=!r}") from exc

        # 2) try fromisoformat (handles many ISO forms, including offsets)
        try:
            return dt.datetime.fromisoformat(value)
        except Exception:
            # parsing error is expected - try next strategy
            pass

        # 3) try common strptime patterns (some produce date-only or time-only)
        patterns = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d_%H:%M:%S",
            "%Y-%m-%d-%H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d_%H:%M",
            "%Y-%m-%d-%H:%M",
            "%Y%m%d %H%M%S",
            "%Y%m%d_%H%M%S",
            "%Y%m%d-%H%M%S",
            "%Y%m%d %H%M",
            "%Y%m%d_%H%M",
            "%Y%m%d-%H%M",
            "%d-%m-%Y %H:%M:%S",
            "%d-%m-%Y %H:%M",
            "%Y%m%d",
            "%Y.%m.%d",
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d.%m.%Y",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%H%M",
            "%H:%M",
            "%H%M%S",
            "%H:%M:%S",
            "T%H%M",
            "T%H:%M",
            "T%H%M%S",
            "T%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S%Z",
            "%Y-%m-%dT%H:%M:%S%Z%z",
        ]
        fill_dt = dt.datetime(1900, 1, 1, 0, 0, 0, 0)
        for pattern in patterns:
            try:
                parsed = dt.datetime.strptime(value, pattern)
                if "%Y" not in pattern:
                    parsed = parsed.replace(year=fill_dt.year)
                if "%m" not in pattern:
                    parsed = parsed.replace(month=fill_dt.month)
                if "%d" not in pattern:
                    parsed = parsed.replace(day=fill_dt.day)
                return parsed
            except Exception:
                # format mismatch is expected - try next pattern
                continue

        # 4) no parser succeeded
        raise ValueError(f"{value=!r} - unable to parse datetime from string")

    # invalid type
    raise TypeError(f"{type(value)=} - unsupported type")
