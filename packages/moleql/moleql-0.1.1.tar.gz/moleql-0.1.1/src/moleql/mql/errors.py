class MoleQLError(Exception):
    """Base HQL errors."""


class SkipError(MoleQLError):
    """Raised when skip is negative / bad value."""


class LimitError(MoleQLError):
    """Raised when limit is negative / bad value."""


class ListOperatorError(MoleQLError):
    """Raised list operator was not possible."""


class FilterError(MoleQLError):
    """Raised when parse filter method fail to find a valid match."""


class TextOperatorError(MoleQLError):
    """Raised when parse text operator contain an empty string."""


class CustomCasterError(MoleQLError):
    """Raised when a custom cast fail."""


class ProjectionError(MoleQLError):
    """Raised when projection json is invalid."""


class LogicalPopulationError(MoleQLError):
    """Raised when method fail to find logical population item."""


class LogicalSubPopulationError(MoleQLError):
    """Raised when method fail to find logical sub population item."""
