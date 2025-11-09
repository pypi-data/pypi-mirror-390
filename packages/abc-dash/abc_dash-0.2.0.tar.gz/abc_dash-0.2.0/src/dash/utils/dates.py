import datetime
from typing import Optional

__all__ = [
    "parse_timestamp",
    "get_beginning_of_day",
    "get_end_of_day",
]


def parse_timestamp(value) -> Optional[datetime.datetime]:
    if value is None or value == "":
        return None
    # The UNIX time, in milliseconds
    if isinstance(value, str):
        value = int(value)
    elif not isinstance(value, int):
        raise ValueError("value must be int or digit: {!r}".format(value))
    return datetime.datetime.fromtimestamp(value, datetime.timezone.utc)


def get_beginning_of_day(value, tzinfo=None):
    if isinstance(value, datetime.datetime):
        date = value.date()
        if tzinfo is None:
            tzinfo = value.tzinfo
    elif isinstance(value, datetime.date):
        date = value
    else:
        raise ValueError(
            "value must be an instance of datetime.datetime or datetime.date"
        )

    return datetime.datetime.combine(date, datetime.time.min, tzinfo)


def get_end_of_day(value, tzinfo=None):
    if isinstance(value, datetime.datetime):
        date = value.date()
        if tzinfo is None:
            tzinfo = value.tzinfo
    elif isinstance(value, datetime.date):
        date = value
    else:
        raise ValueError(
            "value must be an instance of datetime.datetime or datetime.date"
        )

    return datetime.datetime.combine(date, datetime.time.max, tzinfo)


def get_beginning_of_month(target_date=None) -> datetime.date:
    if not target_date:
        target_date = datetime.date.today()

    return datetime.date(target_date.year, target_date.month, 1)


def get_end_of_month(target_date=None) -> datetime.date:
    if not target_date:
        target_date = datetime.date.today()

    if target_date.month == 12:
        last_day = datetime.date(target_date.year + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        last_day = datetime.date(target_date.year, target_date.month + 1, 1) - datetime.timedelta(days=1)

    return last_day
