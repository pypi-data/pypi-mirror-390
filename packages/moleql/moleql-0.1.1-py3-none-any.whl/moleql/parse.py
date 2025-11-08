from collections.abc import Callable

from moleql.default_casters import DEFAULT_HQL_CASTERS
from moleql.mql.core import MoleQL


# ---------------------------------------------------------
# PARSE
# ---------------------------------------------------------
def get_casters(
    casters: dict[str, Callable] | None = None,
):
    """
    Merge default and user-provided casters.

    When user casters are supplied, they override or extend
    the default type-conversion functions used by MoleQL.

    Args:
        casters: Optional mapping of custom caster names
            to callable objects that transform string
            values into typed Python objects.

    Returns:
        dict[str, Callable]: Combined dictionary of
        default casters and any user additions.
    """
    if casters:
        return DEFAULT_HQL_CASTERS | casters
    return DEFAULT_HQL_CASTERS


# ---------------------------------------------------------
# PARSE
# ---------------------------------------------------------
def parse(
    moleql_query: str,
    blacklist: tuple[str, ...] | None = None,
    casters: dict[str, Callable] | None = None,
) -> dict:
    """
    Convert a MoleQL string into a MongoDB query document.

    This function is the primary entry point for MoleQL.
    It parses a human-readable query expression and returns
    the equivalent MongoDB filter dictionary.

    Args:
        moleql_query: Query expression in MoleQL syntax,
            such as ``"age>30&status=in(active,pending)"``.
        blacklist: Optional tuple of field names that
            should be ignored during parsing.
        casters: Optional mapping of additional or
            overriding value-casting functions.

    Returns:
        dict: MongoDB-compatible query document suitable
        for direct use in ``collection.find()``.
    """
    return MoleQL(
        moleql_query=moleql_query,
        blacklist=blacklist,
        casters=get_casters(casters),
    ).mongo_query


# ---------------------------------------------------------
# MOLEQULARIZE
# ---------------------------------------------------------
def moleqularize(
    moleql_query: str,
    blacklist: tuple[str, ...] | None = None,
    casters: dict[str, Callable] | None = None,
) -> MoleQL:
    """
    Parse a MoleQL string and return the MoleQL object.

    Unlike :func:`parse`, this exposes the full MoleQL
    instance so callers can inspect internal attributes,
    such as parsed tokens or validation steps.

    Args:
        moleql_query: Query expression in MoleQL syntax.
        blacklist: Optional tuple of fields to exclude.
        casters: Optional mapping of custom type casters.

    Returns:
        MoleQL: Fully constructed MoleQL parser instance
        with access to ``.mongo_query`` and metadata.
    """
    return MoleQL(
        moleql_query=moleql_query,
        blacklist=blacklist,
        casters=get_casters(casters),
    )
