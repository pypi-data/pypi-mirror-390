ASCENDING_PREFIX: str = "+"
DESCENDING_PREFIX: str = "-"
ASCENDING: int = 1
DESCENDING: int = -1
SEPARATOR: str = "="
SECOND_ELEMENT_INDEX: int = 1
INVALID_SORT_VALUE_ERROR: str = (
    "{value} is not a valid format for sort. "
    "Valid formats are: sort=-property or "
    "sort=+property"
)
PARAM_ITEM_SEPARATOR: str = ","
EMPTY_STRING: str = ""


class SortHandler:
    # -----------------------------------------------------
    # CLASS CONSTRUCTOR
    # -----------------------------------------------------
    def __init__(self, sort_parameter: str):
        self.parameters: str = sort_parameter
        self.mongo_sort: list[tuple[str, int]] = []
        self.value: str = self.parse_value()

    # -----------------------------------------------------
    # METHOD PARSE VALUE
    # -----------------------------------------------------
    def parse_value(self) -> str | None:
        parts: list[str] = self.parameters.split(SEPARATOR)
        if len(parts) == 2 and parts[SECOND_ELEMENT_INDEX] != EMPTY_STRING:
            return parts[SECOND_ELEMENT_INDEX]
        return None

    # -----------------------------------------------------
    # METHOD MAP SORT PARAMS
    # -----------------------------------------------------
    def map_sort_params(self):
        for parameter in self.value.split(PARAM_ITEM_SEPARATOR):
            if parameter.startswith(ASCENDING_PREFIX):
                self.mongo_sort.append((parameter[1:], ASCENDING))
            elif parameter.startswith(DESCENDING_PREFIX):
                self.mongo_sort.append((parameter[1:], DESCENDING))
            else:
                self.mongo_sort.append((parameter, ASCENDING))

    # -----------------------------------------------------
    # PROPERTY QUERY ELEMENT
    # -----------------------------------------------------
    @property
    def query_element(self) -> list[tuple[str, int]] | None:
        if self.value and self.value != EMPTY_STRING:
            self.map_sort_params()
            return self.mongo_sort
        return None
