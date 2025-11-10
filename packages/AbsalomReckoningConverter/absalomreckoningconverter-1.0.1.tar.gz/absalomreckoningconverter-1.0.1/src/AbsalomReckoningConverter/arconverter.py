"""Convert dates to Absalom Reckoning calendar system.

Examples:
    >>> from datetime import datetime
    >>> date = datetime(2023, 12, 25)
    >>> ar_date = convert(date)
    >>> print(ar_date.year)  # 4723
"""

from datetime import datetime
from typing import Final

from AbsalomReckoningConverter.ardate import ArDate
from AbsalomReckoningConverter.constants import (
    arCommonMonths,
    arDays,
    arDayShort,
    arMonths,
    arMonthSeasons,
    arShortMonths,
)

MIN_YEAR: Final[int] = 1970  # Unix epoch
MAX_YEAR: Final[int] = 2099  # Upper limit before conversion breaks

YEAR_OFFSET: Final[int] = 2700  # Set by the Absalom Reckoning calendar (Paizo)


class ArConverterError(Exception):
    """Base exception for arconverter errors."""

    pass


def validate_date(date: datetime) -> None:
    """Validate the input date is within acceptable ranges."""
    if not isinstance(date, datetime):
        raise ArConverterError('Input must be a datetime object')

    if date.year < MIN_YEAR or date.year > MAX_YEAR:
        raise ArConverterError(f'Year must be between {MIN_YEAR} and {MAX_YEAR}')


def convert(target_date: datetime) -> ArDate:
    """Convert a datetime object to an Absalom Reckoning date.

    Args:
        target_date: A datetime object representing the Gregorian calendar date to convert

    Returns:
        ArDate: An Absalom Reckoning date object with the following attributes:
            - year: AR year (Gregorian + 2700)
            - month: Full month name
            - monthShort: 3-letter month abbreviation
            - commonMonth: Common folk month name
            - day: Day of month
            - weekday: Full weekday name
            - weekdayShort: 3-letter weekday abbreviation
            - weekdayNum: Day of week (1-7, Moonday=1)
            - monthNum: Month number (1-12)
            - season: Current season name

    Raises:
        ArConverterError: If input is not a datetime object or year is out of valid range

    Examples:
        >>> from datetime import datetime
        >>> date = datetime(2023, 7, 10)
        >>> ar_date = convert(date)
        >>> print(ar_date.long_date())
        'Erastus 10, 4723'
        >>> print(ar_date.season)
        'Summer'
    """
    validate_date(target_date)

    try:
        # Break the year up into pieces
        year = target_date.year
        month = target_date.month
        day = target_date.day
        day_of_week = target_date.weekday() + 1

        # Build the resulting arDate and it's properties
        result = ArDate()
        result.year = year + YEAR_OFFSET
        result.monthNum = month
        result.day = day
        result.month = arMonths[month]
        result.monthShort = arShortMonths[month]
        result.weekday = arDays[day_of_week]
        result.weekdayNum = day_of_week
        result.weekdayShort = arDayShort[day_of_week]
        result.commonMonth = arCommonMonths[month]
        result.season = arMonthSeasons[month]

        return result

    except KeyError as e:
        raise ArConverterError(f'Invalid calendar mapping: {e}')
    except Exception as e:
        raise ArConverterError(f'Conversion error: {e}')
