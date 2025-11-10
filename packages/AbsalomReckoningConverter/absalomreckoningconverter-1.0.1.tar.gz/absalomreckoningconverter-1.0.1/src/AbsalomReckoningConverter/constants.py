"""Calendar constants for the Absalom Reckoning system.

This module contains the mapping dictionaries for converting between Gregorian and
Absalom Reckoning calendar systems. All dictionaries use month/day numbers as keys
starting from 1.
"""

arDays = {
    1: 'Moonday',   # First day of the week
    2: 'Toilday',   # Second day of the week
    3: 'Wealday',   # Third day of the week
    4: 'Oathday',   # Fourth day of the week
    5: 'Fireday',   # Fifth day of the week
    6: 'Starday',   # Sixth day of the week
    7: 'Sunday',    # Last day of the week
}

arDayShort = {
    # Three-letter abbreviations for weekdays
    1: 'Moon',
    2: 'Toil',
    3: 'Weal',
    4: 'Oath',
    5: 'Fire',
    6: 'Star',
    7: 'Sun',
}

arMonths = {
    # Religious calendar months of Golarion
    1: 'Abadius',    # First month of winter
    2: 'Calistril',  # Second month of winter
    3: 'Pharast',    # First month of spring
    4: 'Gozran',     # Second month of spring
    5: 'Desnus',     # Third month of spring
    6: 'Sarenith',   # First month of summer
    7: 'Erastus',    # Second month of summer
    8: 'Arodus',     # Third month of summer
    9: 'Rova',       # First month of fall
    10: 'Lamashan',  # Second month of fall
    11: 'Neth',      # Third month of fall
    12: 'Kuthona',   # Third month of winter
}

arShortMonths = {
    # Three-letter abbreviations for religious calendar months
    1: 'Ab',
    2: 'Cal',
    3: 'Phar',
    4: 'Goz',
    5: 'Des',
    6: 'Sar',
    7: 'Era',
    8: 'Aro',
    9: 'Rov',
    10: 'Lam',
    11: 'Net',
    12: 'Kut',
}

arCommonMonths = {
    # Common folk names for months used by regular citizens
    1: 'Prima',     # New Year's month
    2: 'Snappe',    # Late winter month
    3: 'Anu',       # Spring planting month
    4: 'Rusanne',   # Spring growth month
    5: 'Farlong',   # Late spring month
    6: 'Sola',      # Midsummer month
    7: 'Fletch',    # High summer month
    8: 'Hazen',     # Late summer month
    9: 'Nuvar',     # Harvest month
    10: 'Shaldo',   # Late harvest month
    11: 'Joya',     # Early winter month
    12: 'Kai',      # Year's end month
}

arMonthSeasons = {
    # Seasonal mapping for each month
    1: 'Winter',
    2: 'Winter',
    3: 'Spring',
    4: 'Spring',
    5: 'Spring',
    6: 'Summer',
    7: 'Summer',
    8: 'Summer',
    9: 'Fall',
    10: 'Fall',
    11: 'Fall',
    12: 'Winter',
}