import json
from typing import Any

from moleql.mql.errors import ProjectionError

FIRST_ELEMENT_INDEX: int = 0
SECOND_ELEMENT_INDEX: int = 1
PARAMETER_SEPARATOR: str = "="
EMPTY_STRING: str = ""
PROJECTION_TEMPLATE: str = "fields="
FIELD_SEPARATOR: str = ","
EXCLUSION_PREFIX: str = "-"
JSON_PREFIX: str = "{"
JSON_SUFFIX: str = "}"
EXCLUDE: int = 0
INCLUDE: int = 1
PROJECTION_DECODE_ERROR_TEMPLATE: str = (
    "Unable to decode projection value. Make sure fields are valid"
    " and if json is used, make sure it is valid json"
)


# ---------------------------------------------------------
# FUNCTION EXTRACT PARAMETER VALUE
# ---------------------------------------------------------
def extract_parameter_value(parameter: str) -> str | None:
    return parameter.split(PARAMETER_SEPARATOR)[SECOND_ELEMENT_INDEX]


# ---------------------------------------------------------
# FUNCTION HAS PROJECTION PARAMETERS
# ---------------------------------------------------------
def has_projection_parameters(parameter: str):
    segments: list[str] = parameter.split(PARAMETER_SEPARATOR)
    if len(segments) > 1 and segments[SECOND_ELEMENT_INDEX] != EMPTY_STRING:
        return True
    return False


# ---------------------------------------------------------
# FUNCTION FIELD HAS TO BE EXCLUDED FROM RESULTS
# ---------------------------------------------------------
def field_has_to_be_excluded_from_projection(field: str) -> bool:
    return field.startswith(EXCLUSION_PREFIX)


# ---------------------------------------------------------
# FUNCTION IS JSON PARAMETER
# ---------------------------------------------------------
def is_json_parameter(field):
    return field.startswith(JSON_PREFIX) and field.endswith(JSON_SUFFIX)


# =========================================================
# CLASS PROJECTION HANDLER
# =========================================================
class ProjectionHandler:
    """
    Converts projection parameters into MongoDB
    Projection format
    """

    def __init__(self, projection_parameter: str):
        self.parameters: str = projection_parameter
        self.projection_query: dict[str, Any] = {}

    def map_parameters(self):
        for field in self.parameter_list:
            if field_has_to_be_excluded_from_projection(field):
                self.exclude_from_projection(field)
            elif is_json_parameter(field):
                self.parse_json_parameter(field)
            else:
                self.include_in_projection(field)

    @property
    def parameter_list(self):
        return extract_parameter_value(self.parameters).split(FIELD_SEPARATOR)

    def include_in_projection(self, field):
        self.projection_query[field] = INCLUDE

    def exclude_from_projection(self, field):
        self.projection_query[field[1:]] = EXCLUDE

    def parse_json_parameter(self, field):
        try:
            json_value = json.loads(field)
            self.projection_query[next(iter(json_value))] = json_value[next(iter(json_value))]
        except Exception as error:
            raise ProjectionError(PROJECTION_DECODE_ERROR_TEMPLATE) from error

    @property
    def projection(self) -> dict[str, Any] | None:
        if has_projection_parameters(self.parameters):
            self.map_parameters()
            return self.projection_query
        return None
