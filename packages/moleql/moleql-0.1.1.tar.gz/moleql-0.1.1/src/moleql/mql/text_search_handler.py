from moleql.mql.errors import TextOperatorError

TEXT_SEARCH_KEY: str = "$text"
SEARCH_KEY: str = "$search"
KEY_VALUE_SEPARATOR: str = "="
SECOND_ELEMENT_INDEX: int = 1


def convert_with_text_operator(parameter: str):
    if parameter == f"{TEXT_SEARCH_KEY}=":
        raise TextOperatorError()
    return parameter.split(KEY_VALUE_SEPARATOR)[SECOND_ELEMENT_INDEX]


class TextSearchHandler:
    def __init__(self, text_search_parameter: str):
        self.parameter: str = text_search_parameter

    @property
    def filter(self) -> dict:
        return {TEXT_SEARCH_KEY: {SEARCH_KEY: convert_with_text_operator(self.parameter)}}
