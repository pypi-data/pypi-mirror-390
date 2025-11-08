from moleql.mql.errors import LimitError, SkipError

LIMIT_TEMPLATE: str = "limit="
SKIP_TEMPLATE: str = "skip="
SEPARATOR: str = "="
SECOND_ELEMENT_INDEX: int = 1
LIMIT_ERROR_TEMPLATE: str = "{parameter} if not a valid skip/limit value"
LIMIT_PROPERTY: str = "Limit"
SKIP_PROPERTY: str = "Skip"
NEGATIVE_ERROR_TEMPLATE: str = "{parameter} cannot be a negative number"


# ---------------------------------------------------------
# FUNCTION HAS VALUE
# ---------------------------------------------------------
def has_value(parameter: str, template: str):
    if parameter == template:
        return False
    return True


# ---------------------------------------------------------
# FUNCTION PARSE VALUE
# ---------------------------------------------------------
def parse_value(parameter: str):
    try:
        return int(parameter.split(SEPARATOR)[SECOND_ELEMENT_INDEX])
    except ValueError as error:
        raise ValueError(LIMIT_ERROR_TEMPLATE.format(parameter=parameter)) from error


# =========================================================
# CLASS HQL LIMIT HANDLER
# =========================================================
class LimitHandler:
    def __init__(self, limit_parameter: str):
        self.parameter: str = limit_parameter

    @property
    def limit(self) -> int:
        if has_value(self.parameter, LIMIT_TEMPLATE):
            limit_value: int = parse_value(self.parameter)
            if limit_value < 0:
                raise LimitError(NEGATIVE_ERROR_TEMPLATE.format(parameter=LIMIT_PROPERTY))
            return limit_value
        return 0


# =========================================================
# CLASS HQL SKIP HANDLER
# =========================================================
class SkipHandler:
    def __init__(self, skip_parameter: str):
        self.parameter: str = skip_parameter

    @property
    def skip(self) -> int:
        if has_value(self.parameter, SKIP_TEMPLATE):
            skip_value: int = parse_value(self.parameter)
            if skip_value < 0:
                raise SkipError(NEGATIVE_ERROR_TEMPLATE.format(parameter=SKIP_PROPERTY))
            return skip_value
        return 0
