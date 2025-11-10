"""Base tests for arConverter.py"""

from datetime import datetime

import pytest

from AbsalomReckoningConverter.arconverter import ArConverterError, convert


def test_convert_base_ok() -> None:
    """Test the base conversion"""
    # arrange
    target_date = datetime(2023, 7, 10)

    # act
    ar_date = convert(target_date)

    # assert
    assert ar_date.month == 'Erastus'
    assert ar_date.day == 10
    assert ar_date.year == 4723
    assert ar_date.weekday == 'Moonday'
    assert ar_date.weekdayNum == 1
    assert ar_date.monthNum == 7
    assert ar_date.monthShort == 'Era'


def test_short_ar_date_ok() -> None:
    """Test the short date conversion"""
    # arrange
    target_date = datetime(2023, 7, 10)

    # act
    ar_date = convert(target_date)
    result = ar_date.short_date()

    # assert
    assert result == 'Era 10, 4723'


def test_long_ar_date_ok() -> None:
    """Test the long date conversion"""
    # arrange
    target_date = datetime(2023, 7, 10)

    # act
    ar_date = convert(target_date)
    result = ar_date.long_date()

    # assert
    assert result == 'Erastus 10, 4723'


def test_weekday_ar_date_ok() -> None:
    """Test the weekday date conversion"""
    # arrange
    target_date = datetime(2023, 7, 10)

    # act
    ar_date = convert(target_date)
    result = ar_date.weekday_date()

    # assert
    assert result == 'Moonday Erastus 10, 4723'


def test_normal_year_ok() -> None:
    """Test a normal year conversion"""
    # arrange
    target_date = datetime(2023, 2, 28)

    # act
    ar_date = convert(target_date)

    # assert
    assert ar_date.day == 28
    assert ar_date.weekday == 'Toilday'


def test_leap_year_ok() -> None:
    """Test a leap year conversion"""
    # arrange
    target_date = datetime(2024, 2, 29)

    # act
    ar_date = convert(target_date)

    # assert
    assert ar_date.day == 29
    assert ar_date.weekday == 'Oathday'


def test_valid_date_conversion() -> None:
    """Test a valid date conversion"""
    # Arrange
    test_date = datetime(2023, 12, 25)

    # Act
    result = convert(test_date)

    # Assert
    assert result.year == 4723
    assert result.monthNum == 12
    assert result.day == 25


def test_invalid_year() -> None:
    """Test an invalid year conversion"""
    # Arrange
    test_date = datetime(2100, 1, 1)

    # Act/Assert
    with pytest.raises(ArConverterError, match='Year must be between'):
        convert(test_date)


def test_invalid_input_type() -> None:
    # Arrange
    test_date = '2023-12-25'

    # Act/Assert
    with pytest.raises(ArConverterError, match='Input must be a datetime object'):
        convert(test_date)


def test_common_month_long_date_ok() -> None:
    """Test the common month long date conversion"""
    # arrange
    target_date = datetime(2023, 7, 10)

    # act
    ar_date = convert(target_date)
    result = ar_date.common_long_month()

    # assert
    assert result == 'Fletch 10, 4723'


def test_month_season_ok() -> None:
    """Test the month season conversion"""
    # arrange
    target_date = datetime(2023, 7, 10)

    # act
    ar_date = convert(target_date)
    result = ar_date.month_season()

    # assert
    assert result == 'Summer'


def test_season_changes_ok() -> None:
    """Test season changes throughout the year"""
    # arrange
    test_dates = [
        (datetime(2023, 1, 1), 'Winter'),
        (datetime(2023, 3, 1), 'Spring'),
        (datetime(2023, 6, 1), 'Summer'),
        (datetime(2023, 9, 1), 'Fall'),
        (datetime(2023, 12, 1), 'Winter'),
    ]

    for date, expected_season in test_dates:
        # act
        ar_date = convert(date)

        # assert
        assert ar_date.season == expected_season
