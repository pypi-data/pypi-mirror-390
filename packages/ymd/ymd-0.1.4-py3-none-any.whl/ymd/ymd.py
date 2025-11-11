import datetime
import zoneinfo
from typing import List, Iterator


def parse_date(
    date: str | datetime.date | datetime.datetime,
    format: str = "%Y-%m-%d"
) -> datetime.date:
    if isinstance(date, str):
        return datetime.datetime.strptime(date, format)
    elif isinstance(date, (datetime.datetime, datetime.date)):
        return date
    else:
        raise ValueError("Invalid date type")


def date_range(
    start: str | datetime.date | datetime.datetime | int,
    stop: str | datetime.date | datetime.datetime | int,
    step: int = 1,
    format: str = "%Y-%m-%d",
    timezone: str = None
) -> Iterator[str]:
    """
    Return an object that produces a sequence of date strings from
    start (inclusive) to stop (exclusive) by step. When step is given,
    it specifies the increment (or decrement) in days.
    """
    if isinstance(start, int):
        start = today(offset=start, timezone=timezone)
    date = parse_date(start, format=format)
    if isinstance(stop, int):
        stop = date + datetime.timedelta(days=stop)
    else:
        stop = parse_date(stop, format=format)
    while True:
        if (date >= stop and step > 0) or (date <= stop and step < 0):
            break
        yield date.strftime(format)
        date += datetime.timedelta(days=step)
    return None


def date_list(
    start: str | datetime.date,
    stop: str | datetime.date | int,
    step: int = 1,
    format: str = "%Y-%m-%d",
    timezone: str = None
) -> List[str]:
    """
    Return a list of date strings from start (inclusive) to stop (exclusive)
    by step. When step is given, it specifies the increment (or decrement).
    """
    return list(date_range(start, stop, step, format, timezone))


def today(
    offset: int = 0,
    timezone: str = None,
    format: str = "%Y-%m-%d"
) -> str:
    """
    Return current date with an optional offset in days.
    """
    if timezone:
        date = datetime.datetime.now(tz=zoneinfo.ZoneInfo(timezone))
    else:
        date = datetime.date.today()
    if offset:
        date = date + datetime.timedelta(days=offset)
    return date.strftime(format)


def next_date(
    date: str | datetime.date | datetime.datetime,
    offset: int = 1,
    format: str = "%Y-%m-%d"
) -> str:
    """
    Returns the next date after the input date by a specified number of days.

    Args:
        date: The input date.
        offset: The number of days to add to the input date. Defaults to 1.
        format: The output format.

    Returns:
        str: The next date after the input date as a string in the specified
        format.
    """
    date1 = parse_date(date, format=format)
    date2 = date1 + datetime.timedelta(days=offset)
    return date2.strftime(format)
