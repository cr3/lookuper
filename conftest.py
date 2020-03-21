"""Pytest configuration."""


def pytest_make_parametrize_id(config, val, argname=None):
    """Return the canonical string representation of the value."""
    return repr(val)
