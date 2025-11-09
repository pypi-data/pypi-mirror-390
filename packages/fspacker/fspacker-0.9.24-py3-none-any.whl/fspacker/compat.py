"""Compatibility module for old Python versions."""

try:
    # Python 3.11+ standard library
    import tomllib  # type: ignore  # noqa: PGH003
except ImportError:
    # For old version python
    import tomli as tomllib  # noqa: F401
