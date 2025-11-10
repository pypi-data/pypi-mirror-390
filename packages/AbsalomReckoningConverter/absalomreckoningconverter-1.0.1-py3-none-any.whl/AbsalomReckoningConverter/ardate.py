"""Absalom Reckoning Date Class

Example:
    >>> ar_date = ArDate()  # typically created via convert()
    >>> ar_date.month = "Erastus"
    >>> ar_date.day = 10
    >>> ar_date.year = 4723
    >>> print(ar_date.long_date())
    "Erastus 10, 4723"
"""


class ArDate:
    """Represents an Absalom Reckoning Date

    Examples:
        >>> ar_date = ArDate()
        >>> ar_date.month = "Erastus"
        >>> ar_date.monthShort = "Era"
        >>> ar_date.commonMonth = "Fletch"
        >>> ar_date.day = 10
        >>> ar_date.year = 4723
        >>> ar_date.weekday = "Moonday"
        >>> ar_date.weekdayShort = "Moon"
        >>> ar_date.weekdayNum = 1
        >>> ar_date.monthNum = 7
        >>> ar_date.season = "Summer"
    """

    month: str
    day: int
    year: int
    weekday: str
    weekdayShort: str
    weekdayNum: int
    monthNum: int
    monthShort: str
    commonMonth: str
    season: str

    def short_date(self) -> str:
        """Returns a short date string

        Example:
            >>> ar_date.short_date()
            'Era 10, 4723'
        """
        return f'{self.monthShort} {self.day}, {self.year}'

    def long_date(self) -> str:
        """Returns a long date string

        Example:
            >>> ar_date.long_date()
            'Erastus 10, 4723'
        """
        return f'{self.month} {self.day}, {self.year}'

    def weekday_date(self) -> str:
        """Returns a weekday date string

        Example:
            >>> ar_date.weekday_date()
            'Moonday Erastus 10, 4723'
        """
        return f'{self.weekday} {self.month} {self.day}, {self.year}'

    def common_long_month(self) -> str:
        """Returns a long date string with common month name

        Example:
            >>> ar_date.common_long_month()
            'Fletch 10, 4723'
        """
        return f'{self.commonMonth} {self.day}, {self.year}'

    def month_season(self) -> str:
        """Returns the season for the current month

        Example:
            >>> ar_date.month_season()
            'Summer'
        """
        return self.season

    def __str__(self) -> str:
        """Returns a short date string"""
        return self.short_date()
