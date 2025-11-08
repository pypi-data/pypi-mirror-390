from datetime import datetime

from dateparser import parse


def parse_date(date: str) -> datetime | str:
    """Cast string date into datetime using dateparse library.

    Args:
        date (str): Date as string format.

     Returns:
        Optional[datetime]: Cast value.
    """

    return parse(date, languages=["en"]) or date
