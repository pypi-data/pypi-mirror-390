from datetime import datetime

from AbsalomReckoningConverter import convert


def main() -> None:
    """CLI entrypoint that prints today's AR date."""
    target_date = datetime.today()
    ar_date = convert(target_date)
    print(ar_date.weekday_date())


if __name__ == '__main__':
    main()
