"""Unit tests for the lookuper module."""

import re

from lookuper import (
    anything,
    GLOBSTAR,
    STAR,
    lookup,
    lookup_data,
    lookup_target,
    Match,
)

import pytest


def test_anything_new():
    """Initializing anything should return the same instance."""
    result = type(anything)()

    assert result is anything


@pytest.mark.parametrize(
    'b', [0, 1, True, False, None],
)
def test_anything_call(b):
    """Mathing anything should always return True."""
    result = anything(b)

    assert result is True


@pytest.mark.parametrize(
    'match, key, value, expected',
    [
        (Match(), 'a', 1, True),
        (Match(key='a'), 'a', 1, True),
        (Match(key='b'), 'a', 1, False),
        (Match(value=1), 'a', 1, True),
        (Match(value=2), 'a', 1, False),
        (Match('a', 1), 'a', 1, True),
        (Match('b', 1), 'a', 1, False),
        (Match('a', 2), 'a', 1, False),
    ],
)
def test_match_call(match, key, value, expected):
    """Matching key/value pairs should return the expected result."""
    result = match(key, value)

    assert result is expected


@pytest.mark.parametrize(
    'match, expected',
    [
        (anything, 'ANYTHING'),
        (Match(), 'Match(key=ANYTHING, value=ANYTHING)'),
        (Match(1), 'Match(key=1, value=ANYTHING)'),
        (Match('a'), "Match(key='a', value=ANYTHING)"),
        (Match(value=1), 'Match(key=ANYTHING, value=1)'),
        (Match(value='a'), "Match(key=ANYTHING, value='a')"),
        (Match(1, 2), 'Match(key=1, value=2)'),
    ],
)
def test_match_repr(match, expected):
    """Representing matches should return the expected result."""
    result = repr(match)

    assert result == expected


@pytest.mark.parametrize(
    'constant, string', [(STAR, '*'), (GLOBSTAR, '**')],
)
def test_lookup_constants(constant, string):
    """Lookup constants should behave like strings."""
    assert constant == string


@pytest.mark.parametrize(
    'targets, data, expected',
    [
        ([], None, [None]),
        ([], {'a': 1}, [{'a': 1}]),
        (['a'], {'a'}, ['a']),
        (['0'], {'0'}, ['0']),
        ([0], {0}, [0]),
        (['a'], {'a': 1}, [1]),
        (['b'], {'a': 1}, []),
        (['a'], {'a': {'b': 1}}, [{'b': 1}]),
        (['a', 'b'], {'a': {'b': 1}}, [1]),
        (['a', 'b'], {'a': 1}, []),
        ([0], ['a'], ['a']),
        (['0'], ['a'], []),
        ([1], ['a'], []),
        ([0], [['a']], [['a']]),
        ([0, 0], [['a']], ['a']),
        (['a', 0], {'a': ['b']}, ['b']),
        (['a', 'b'], {'a': {'b'}}, ['b']),
        ([0, 'a'], [{'a': 1}], [1]),
        (['a', 0, 'b'], {'a': [{'b': 1}]}, [1]),
        ([0, 'a', 0], [{'a': [1]}], [1]),
        (['*'], {'a': 1}, [1]),
        (['*'], {'a': 1, 'b': 2}, [1, 2]),
        (['*'], ['a'], ['a']),
        (['*'], ['a', 'b'], ['a', 'b']),
        (['a', '*'], {'a': [1]}, [1]),
        (['a', '*'], {'a': {'b': 1}}, [1]),
        (['b', '*'], {'a': [1]}, []),
        (['*', 0], {'a': [1]}, [1]),
        (['*', 1], {'a': [1]}, []),
        ([0, '*'], [{'a': 1}], [1]),
        ([1, '*'], [{'a': 1}], []),
        (['*', 'a'], [{'a': 1}], [1]),
        (['*', 'b'], {'a': {'b': 1}}, [1]),
        (['*', 'b'], [{'a': 1}], []),
        (['a', '*', 'b'], {'a': [1, {'b': 2}]}, [2]),
        (['a', '*', 'c'], {'a': {'b': {'c': 1}}}, [1]),
        (['a', '*', 'c'], {'a': [{'c': 1}]}, [1]),
        ([0, '*', 0], [{'a': [1]}], [1]),
        (['**'], {'a': 1}, [{'a': 1}, 1]),
        (['**'], {'a': {'b': 2}}, [{'a': {'b': 2}}, {'b': 2}, 2]),
        (['**', 'a'], {'a': 1}, [1]),
        (['**', 'b'], [{'b': 1}], [1]),
        (['**', 'b'], [{'a': {'b': 1}}], [1]),
        (['**', 'b'], {'a': [{'b': 1}]}, [1]),
        (['**', 'c'], {'a': {'b': {'c': 1}}}, [1]),
        (['**', 'c'], {'a': [{'c': 1}]}, [1]),
        (['**', 'c'], [[{'c': 1}]], [1]),
        (['a', '**', 'd'], {'a': {'b': {'c': {'d': 1}}}}, [1]),
        (['a', '**', 'd'], {'a': {'b': [{'d': 1}]}}, [1]),
        (['a', '**', 'd'], {'a': [{'c': {'d': 1}}]}, [1]),
        (['a', '**', 'd'], {'a': [[{'d': 1}]]}, [1]),
        (['a', Match(0), 'b'], {'a': [{'b': 2}]}, [2]),
        (['a', Match(value=1)], {'a': {'b': 1}}, [1]),
    ],
)
def test_lookup(targets, data, expected):
    """Looking up a target from data should yield the expected results."""
    result = list(lookup(data, *targets))

    assert result == expected


@pytest.mark.parametrize(
    'data, expected',
    [
        # Default
        (None, []),
        ('a', []),
        (1, []),
        # Mapping
        ({}, []),
        ({'a': 1}, [('a', 1)]),
        ({'a': 1, 'b': 2}, [('a', 1), ('b', 2)]),
        # Sequence
        ([], []),
        (['a'], [(0, 'a')]),
        (['a', 'b'], [(0, 'a'), (1, 'b')]),
        # Set
        (set(), []),
        ({'a'}, [('a', 'a')]),
    ],
)
def test_lookup_data(data, expected):
    """Looking up a data should yield the expected results."""
    result = list(lookup_data(data))

    assert result == expected


@pytest.mark.parametrize(
    'target, key, value, expected',
    [
        # Default
        ('a', None, {'a': 1}, [('a', 1)]),
        ('b', None, {'a': 1}, []),
        # str
        ('a', None, {'a': 1}, [('a', 1)]),
        ('b', None, {'a': 1}, []),
        ('*', None, {'a': 1}, [('a', 1)]),
        (r'\*', None, {'a': 1}, []),
        (r'\*', None, {'*': 1}, [('*', 1)]),
        ('**', 'a', {'b': 1}, [('a', {'b': 1}), ('b', 1)]),
        (r'\**', 'a', {'b': 1}, []),
        (r'\**', None, {'**': 1}, [('**', 1)]),
        (r'*\*', None, {'**': 1}, [('**', 1)]),
        (r'\*\*', None, {'**': 1}, [('**', 1)]),
        # Callable
        (str.isalpha, None, {'a': 1}, [('a', 1)]),
        (str.isdigit, None, {'a': 1}, []),
        # Match
        (Match('a'), None, {'a': 1}, [('a', 1)]),
        (Match('b'), None, {'a': 1}, []),
        (Match(value=1), None, {'a': 1}, [('a', 1)]),
        (Match(value=2), None, {'a': 1}, []),
        # RePattern
        (re.compile(r'\w'), None, {'a': 1}, [('a', 1)]),
        (re.compile(r'\d'), None, {'a': 1}, []),
        # Sequence
        (['a'], None, {'a': 1}, [('a', 1)]),
        (['a', 'b'], None, {'a': {'b': 1}}, [('b', 1)]),
        # STAR
        (STAR, None, {'a': 1}, [('a', 1)]),
        (STAR, None, {'a': 1, 'b': 2}, [('a', 1), ('b', 2)]),
        # GLOBSTAR
        (GLOBSTAR, 'a', {'b': 1}, [('a', {'b': 1}), ('b', 1)]),
    ],
)
def test_lookup_target(target, key, value, expected):
    """Looking up a target from data should yield the expected results."""
    result = list(lookup_target(target, key, value))

    assert result == expected
