"""CLI for arconverter package."""

from datetime import datetime

from AbsalomReckoningConverter import convert


def main() -> None:
    """Print today's date in Absalom Reckoning format."""
    target_date = datetime.today()
    ar_date = convert(target_date)
    print(ar_date.weekday_date())


if __name__ == '__main__':
    main()
