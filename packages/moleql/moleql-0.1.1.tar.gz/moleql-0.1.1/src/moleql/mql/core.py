"""
moleql.mql.core
===============

Core logic for MoleQL parsing and query construction.

This module defines the MoleQL class, which transforms
human-readable query-string expressions into MongoDB-
compatible query documents. It also provides utility
functions for parameter extraction, blacklist filtering,
and argument type detection.
"""

from collections.abc import Callable
from typing import Any
from urllib import parse

from moleql.mql.constants import (
    FIELDS_KEY,
    FILTER,
    FILTERS_KEY,
    LIMIT_KEY,
    PROJECTION_KEY,
    QUERY_STRING_PARAM_SEPARATOR,
    SKIP_KEY,
    SORT_KEY,
    TEXT_KEY,
)
from moleql.mql.filter_handler import FilterHandler
from moleql.mql.limit_skip_handler import LimitHandler, SkipHandler
from moleql.mql.projection_handler import ProjectionHandler
from moleql.mql.sort_handler import SortHandler
from moleql.mql.text_search_handler import TextSearchHandler

MONGO_QUERY_TEMPLATE: dict[str, Any] = {
    FILTERS_KEY: {},
    SORT_KEY: None,
    SKIP_KEY: 0,
    LIMIT_KEY: 0,
    PROJECTION_KEY: None,
}
EMPTY_STRING: str = ""


# ---------------------------------------------------------
# PARSE QUERY AS KEY VALUE
# ---------------------------------------------------------
def extract_parameter_list(hql_query: str) -> list[str]:
    """
    Decode and split a MoleQL query string.

    Converts a URL-encoded query string into a list of
    raw key–value parameter expressions.

    Args:
        hql_query: Encoded MoleQL query string.

    Returns:
        list[str]: Individual parameter expressions.
    """
    return list(parse.unquote(hql_query).split(QUERY_STRING_PARAM_SEPARATOR))


# ---------------------------------------------------------
# REMOVE BLACKLISTED
# ---------------------------------------------------------
def remove_blacklisted(hql_query: str, blacklist: tuple[str, ...] | None):
    """
    Remove parameters whose names match a blacklist.

    Args:
        hql_query: MoleQL query string to filter.
        blacklist: Optional tuple of parameter prefixes
            to exclude from parsing.

    Returns:
        list[str]: Parameters not matching the blacklist.
    """
    raw_parameters: list[str] = extract_parameter_list(hql_query=hql_query)
    if blacklist:
        return [parameter for parameter in raw_parameters if not parameter.startswith(blacklist)]
    return raw_parameters


def is_text_search_argument(parameter):
    """Check if parameter is a text-search argument."""
    return parameter.startswith(f"{TEXT_KEY}=")


def is_projection_argument(parameter):
    """Check if parameter defines a projection field list."""
    return parameter.startswith(f"{FIELDS_KEY}=")


def is_skip_argument(parameter):
    """Check if parameter defines a skip value."""
    return parameter.startswith(f"{SKIP_KEY}=")


def is_limit_argument(parameter):
    """Check if parameter defines a limit value."""
    return parameter.startswith(f"{LIMIT_KEY}=")


def is_sort_argument(parameter):
    """Check if parameter defines a sort expression."""
    return parameter.startswith(f"{SORT_KEY}=")


# =========================================================
# CLASS MOLEQL
# =========================================================
class MoleQL:
    """
    MoleQL parser for transforming query strings.

    This class interprets MoleQL-formatted query strings
    and builds MongoDB-compatible query dictionaries that
    include filters, sorting, limits, skips, and field
    projections.

    Attributes:
        moleql_query: Original MoleQL query string.
        blacklist: Optional tuple of fields to exclude.
        casters: Optional mapping of type-casting callables.
        output_query: Internal MongoDB-style query dict.
    """

    # -----------------------------------------------------
    # CLASS CONSTRUCTOR
    # -----------------------------------------------------
    def __init__(
        self,
        moleql_query: str,
        blacklist: tuple[str, ...] | None = None,
        casters: dict[str, Callable] | None = None,
    ):
        """
        Initialize a MoleQL instance.

        Args:
            moleql_query: MoleQL query string to parse.
            blacklist: Optional tuple of field prefixes
                to exclude during parsing.
            casters: Optional mapping of value casters
                to convert strings into typed objects.
        """
        self.moleql_query: str = moleql_query
        self.blacklist = blacklist
        self.raw_parameters: list[str] = remove_blacklisted(
            hql_query=self.moleql_query, blacklist=self.blacklist
        )
        self.casters: dict[str, Callable] | None = casters
        self.output_query: dict[str, any] = {
            FILTER: {},
            SORT_KEY: None,
            SKIP_KEY: 0,
            LIMIT_KEY: 0,
            PROJECTION_KEY: None,
        }
        self.process_parameters()

    # -----------------------------------------------------
    # PROPERTY MONGO FILTER
    # -----------------------------------------------------
    @property
    def mongo_filter(self) -> dict[str, Any] | None:
        """Return the MongoDB filter portion."""
        return self.output_query[FILTER]

    # -----------------------------------------------------
    # PROPERTY MONGO PROJECTION
    # -----------------------------------------------------
    @property
    def mongo_projection(self) -> dict[str, Any] | None:
        """Return the MongoDB projection document."""
        return self.output_query[PROJECTION_KEY]

    # -----------------------------------------------------
    # METHOD PROCESS PARAMETERS
    # -----------------------------------------------------
    def process_parameters(self):
        """
        Parse and dispatch each MoleQL parameter.

        Determines the parameter type (filter, sort, limit,
        etc.) and delegates to the corresponding handler.
        """
        for parameter in self.raw_parameters:
            if is_sort_argument(parameter):
                self.sort(parameter)
            elif is_limit_argument(parameter):
                self.limit(parameter)
            elif is_skip_argument(parameter):
                self.skip(parameter)
            elif is_projection_argument(parameter):
                self.project(parameter)
            elif is_text_search_argument(parameter):
                self.search_text(parameter)
            elif parameter != EMPTY_STRING:
                self.filter(parameter)

    # -----------------------------------------------------
    # FILTER
    # -----------------------------------------------------
    def filter(self, parameter):
        """
        Apply a filter parameter using FilterHandler.

        Merges sub-filters for repeated field names.

        Args:
            parameter: MoleQL filter expression string.
        """
        for key, sub_filter in FilterHandler(
            filter_parameter=parameter, custom_casters=self.casters
        ).filter.items():
            if key in self.output_query[FILTER]:
                self.output_query[FILTER][key] = {
                    **self.output_query[FILTER][key],
                    **sub_filter,
                }
            else:
                self.output_query[FILTER][key] = sub_filter

    # -----------------------------------------------------
    # SEARCH TEXT
    # -----------------------------------------------------
    def search_text(self, parameter):
        """
        Apply a text-search filter using TextSearchHandler.

        Args:
            parameter: MoleQL text-search parameter string.
        """
        self.output_query[FILTER].update(TextSearchHandler(text_search_parameter=parameter).filter)

    # -----------------------------------------------------
    # PROJECT
    # -----------------------------------------------------
    def project(self, parameter):
        """
        Apply a projection using ProjectionHandler.

        Args:
            parameter: MoleQL projection parameter string.
        """
        self.output_query[PROJECTION_KEY] = ProjectionHandler(
            projection_parameter=parameter
        ).projection

    # -----------------------------------------------------
    # SKIP
    # -----------------------------------------------------
    def skip(self, parameter):
        """
        Apply a skip value using SkipHandler.

        Args:
            parameter: MoleQL skip parameter string.
        """
        self.output_query[SKIP_KEY] = SkipHandler(skip_parameter=parameter).skip

    # -----------------------------------------------------
    # LIMIT
    # -----------------------------------------------------
    def limit(self, parameter):
        """
        Apply a limit value using LimitHandler.

        Args:
            parameter: MoleQL limit parameter string.
        """
        self.output_query[LIMIT_KEY] = LimitHandler(limit_parameter=parameter).limit

    # -----------------------------------------------------
    # SORT
    # -----------------------------------------------------
    def sort(self, parameter):
        """
        Apply sorting using SortHandler.

        Args:
            parameter: MoleQL sort parameter string.
        """
        self.output_query[SORT_KEY] = SortHandler(sort_parameter=parameter).query_element

    # -----------------------------------------------------
    # PROPERTY MONGO QUERY
    # -----------------------------------------------------
    @property
    def mongo_query(self) -> dict[str, Any] | None:
        """
        Return the complete MongoDB query document.

        Combines filters, projections, sort order, and
        pagination metadata into one structure.
        """
        return self.output_query
