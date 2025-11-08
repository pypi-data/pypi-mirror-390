import re

_SLASHED_RE = re.compile(
    r"""
    ^/
    (?P<pattern>(?:\\.|[^/])*)   # allow escaped slashes like \/
    /
    (?P<flags>[a-z]*)?           # optional flags (letters only)
    $
    """,
    re.VERBOSE,
)

# MongoDB-supported inline flags commonly encountered
_ALLOWED_FLAGS = frozenset("imsx")  # i=ignorecase, m=multiline, s=dotall, x=verbose


def parse_regex(value: str) -> dict[str, str]:
    """
    Convert a string like '/foo.+/i' into a MongoDB regex query dict.

    If the value is not in the slash-delimited form, the whole string
    is treated as the pattern.

    Examples:
        '/ab+c/i'      -> {'$regex': 'ab+c', '$options': 'i'}
        '/a\\/b/x'     -> {'$regex': 'a\\/b', '$options': 'x'}
        'plain-text'   -> {'$regex': 'plain-text'}

    Args:
        value: The user-supplied regex string.

    Returns:
        A dict suitable for MongoDB queries, e.g.
        {'$regex': '<pattern>', '$options': '<flags>'}.
    """
    s = value.strip()
    m = _SLASHED_RE.fullmatch(s)

    if not m:
        return {"$regex": s}

    pattern = m.group("pattern")
    flags_raw = m.group("flags") or ""
    flags = "".join(ch for ch in flags_raw if ch in _ALLOWED_FLAGS)

    out: dict[str, str] = {"$regex": pattern}
    if flags:
        out["$options"] = flags
    return out
