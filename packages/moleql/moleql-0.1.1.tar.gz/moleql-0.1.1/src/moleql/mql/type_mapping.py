import re
from typing import Any

from moleql.mql.date_parser import parse_date
from moleql.mql.regex_parser import parse_regex

FLOAT_REGEX: str = r"^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$"
INT_REGEX: str = r"^[-+]?\d+$"
DATE_REGEX: str = (
    r"^[12]\d{3}(-(0[1-9]|1[0-2])(-(0[1-9]|[12][0-9]|3[01]))?)(T|"
    r" )?(([01][0-9]|2[0-3]):[0-5]\d(:[0-5]\d(\.\d+)?)?(Z|[+-]\d{2}:\d{2})?)?$"
)
LIST_VALUE_REGEX: str = r"^[A-Za-z ]+(?=(,?,))(?:\1[A-Za-z ]+)+$"
REGEX_VALUE_REGEX: str = (
    r"\/((?![*+?])(?:[^\r\n\[/\\]|\\.|\[(?:[^\r\n\]\\]|\\.)*\])+)"
    r"\/((?:g(?:im?|mi?)?|i(?:gm?|mg?)?|m(?:gi?|ig?)?)?)"
)

DEFAULT_CASTING_RULES: dict[str | re.Pattern[str], Any] = {
    re.compile(FLOAT_REGEX): float,
    re.compile(INT_REGEX): int,
    re.compile(DATE_REGEX): parse_date,
    re.compile(LIST_VALUE_REGEX): lambda list_value: list_value.split(","),
    re.compile(REGEX_VALUE_REGEX): parse_regex,
    "true": lambda boolean: True,
    "false": lambda boolean: False,
    "null": lambda null: None,
    "none": lambda none: None,
}
