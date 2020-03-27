"""Unit tests for the lookuper module."""

import re

from lookuper import (
    ANY,
    GLOBSTAR,
    STAR,
    lookup,
    lookup_data,
    lookup_target,
    Match,
)

import pytest


@pytest.mark.parametrize(
    'lookup_type, string', [(STAR, '*'), (GLOBSTAR, '**')],
)
def test_lookup_types(lookup_type, string):
    """Lookup types should behave like strings."""
    assert lookup_type == string


@pytest.mark.parametrize(
    'func, args, matches',
    [(ANY, (), True), (ANY, (0,), True), (ANY, (0, 0,), True)],
)
def test_match_functions(func, args, matches):
    """Calling match functions should return the expected result."""
    result = func(*args)

    assert result == matches


@pytest.mark.parametrize(
    'func, matches',
    [
        (ANY, 'ANY'),
        (Match(), 'Match(key=ANY, value=ANY)'),
        (Match(1), 'Match(key=1, value=ANY)'),
        (Match('a'), "Match(key='a', value=ANY)"),
        (Match(value=1), 'Match(key=ANY, value=1)'),
        (Match(value='a'), "Match(key=ANY, value='a')"),
        (Match(1, 2), 'Match(key=1, value=2)'),
    ],
)
def test_match_repr(func, matches):
    """Representating match functions should return the expected result."""
    result = repr(func)

    assert result == matches


@pytest.mark.parametrize(
    'targets, data, matches',
    [
        ([], None, [None]),
        ([], {'a': 1}, [{'a': 1}]),
        (['a'], {'a'}, ['a']),
        (['a'], {'a': 1}, [1]),
        (['b'], {'a': 1}, []),
        (['a'], {'a': {'b': 1}}, [{'b': 1}]),
        (['a', 'b'], {'a': {'b': 1}}, [1]),
        (['a', 'b'], {'a': 1}, []),
        ([0], ['a'], ['a']),
        (['0'], ['a'], ['a']),
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
        (['a.b'], {'a': {'b': 1}}, [1]),
        (['a.b'], {'a': 1}, []),
        ([r'\*'], {'*': 1}, [1]),
        ([r'a\.b'], {'a.b': 1}, [1]),
        ([r'a\.b\.c'], {'a.b.c': 1}, [1]),
        ([r'a\.b.c'], {'a.b': {'c': 1}}, [1]),
        ([r'a.b\.c'], {'a': {'b.c': 1}}, [1]),
    ],
)
def test_lookup(targets, data, matches):
    """Looking up a target from data should yield the expected results."""
    result = list(lookup(data, *targets))

    assert result == matches


@pytest.mark.parametrize(
    'data, matches',
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
def test_lookup_data(data, matches):
    """Looking up a data should yield the expected results."""
    result = list(lookup_data(data))

    assert result == matches


@pytest.mark.parametrize(
    'target, key, value, matches',
    [
        # Default
        ('a', None, {'a': 1}, [('a', 1)]),
        ('b', None, {'a': 1}, []),
        # List
        (['a'], None, {'a': 1}, [('a', 1)]),
        (['a', 'b'], None, {'a': {'b': 1}}, [('b', 1)]),
        # String
        ('a', None, {'a': 1}, [('a', 1)]),
        ('a.b', None, {'a': {'b': 1}}, [('b', 1)]),
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
        # STAR
        (STAR, None, {'a': 1}, [('a', 1)]),
        # GLOBSTAR
        (GLOBSTAR, 'a', {'b': 1}, [('a', {'b': 1}), ('b', 1)]),
    ],
)
def test_lookup_target(target, key, value, matches):
    """Looking up a target from data should yield the expected results."""
    result = list(lookup_target(target, key, value))

    assert result == matches


@pytest.mark.parametrize(
    'func, key, value, matches',
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
def test_match(func, key, value, matches):
    """Matching key/value pairs should return the expected data."""
    result = func(key, value)

    assert result == matches
