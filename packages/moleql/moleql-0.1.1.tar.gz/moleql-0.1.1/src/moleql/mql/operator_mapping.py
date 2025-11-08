MONGO_OPERATOR_MAPPING: dict[str, str] = {
    "=": "$eq",
    "!=": "$ne",
    ">": "$gt",
    ">=": "$gte",
    "<": "$lt",
    "<=": "$lte",
    "!": "$exists",
    "": "$exists",
}

MOLEQL_OPERATORS: list[str] = ["<=", ">=", "!=", "=", ">", "<", "!"]
