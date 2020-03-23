"""Unit tests for the lookuper module."""

import re

from lookuper import (
    ALWAYS,
    GLOBSTAR,
    STAR,
    lookup,
    lookup_data,
    lookup_target,
    match,
    match_key,
    match_value,
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
    [(ALWAYS, (), True), (ALWAYS, (0,), True), (ALWAYS, (0, 0,), True)],
)
def test_match_functions(func, args, matches):
    """Calling match functions should return the expected result."""
    result = func(*args)

    assert result == matches


@pytest.mark.parametrize(
    'target, data, matches',
    [
        # str
        ('', None, [None]),
        ('', {'a': 1}, [{'a': 1}]),
        ('0', [1], [1]),
        ('a', {'a'}, ['a']),
        ('a', {'a': 1}, [1]),
        ('a.b', {'a': 1}, []),
        ('a.b', {'a': {'b': 1}}, [1]),
        ('a.0', {'a': ['b']}, ['b']),
        ('a.b', {'a': {'b'}}, ['b']),
        ('0.a', [{'a': 1}], [1]),
        ('*', {'a': 1}, [1]),
        ('a.*', {'a': {'b': 1}}, [1]),
        ('a.*', {'a': [1]}, [1]),
        ('*.b', {'a': {'b': 1}}, [1]),
        ('*.b', [{'b': 1}], [1]),
        ('a.*.c', {'a': {'b': {'c': 1}}}, [1]),
        ('a.*.c', {'a': [{'c': 1}]}, [1]),
        ('**', {'a': 1}, [{'a': 1}, 1]),
        ('**.a', {'a': 1}, [1]),
        ('**.b', {'a': {'b': 1}}, [1]),
        ('**.c', {'a': {'b': {'c': 1}}}, [1]),
        ('**.c', {'a': [{'c': 1}]}, [1]),
        ('**.c', [[{'c': 1}]], [1]),
        ('a.**.d', {'a': {'b': {'c': {'d': 1}}}}, [1]),
        ('a.**.d', {'a': {'b': [{'d': 1}]}}, [1]),
        ('a.**.d', {'a': [{'c': {'d': 1}}]}, [1]),
        ('a.**.d', {'a': [[{'d': 1}]]}, [1]),
        # Sequence
        ([], None, [None]),
        (['a'], {'a': 1}, [1]),
        (['b'], {'a': 1}, []),
        (['a'], {'a': {'b': 1}}, [{'b': 1}]),
        (['a', 'b'], {'a': {'b': 1}}, [1]),
        (['a', 'b'], {'a': 1}, []),
        ([0], ['a'], ['a']),
        ([1], ['a'], []),
        ([0], [['a']], [['a']]),
        ([0, 0], [['a']], ['a']),
        (['a', 0], {'a': [1]}, [1]),
        ([0, 'a'], [{'a': 1}], [1]),
        (['a', 0, 'b'], {'a': [{'b': 1}]}, [1]),
        ([0, 'a', 0], [{'a': [1]}], [1]),
        ([STAR], {'a': 1}, [1]),
        ([STAR], {'a': 1, 'b': 2}, [1, 2]),
        ([STAR], ['a'], ['a']),
        ([STAR], ['a', 'b'], ['a', 'b']),
        (['a', STAR], {'a': [1]}, [1]),
        (['b', STAR], {'a': [1]}, []),
        ([STAR, 0], {'a': [1]}, [1]),
        ([STAR, 1], {'a': [1]}, []),
        ([0, STAR], [{'a': 1}], [1]),
        ([1, STAR], [{'a': 1}], []),
        ([STAR, 'a'], [{'a': 1}], [1]),
        ([STAR, 'b'], [{'a': 1}], []),
        (['a', STAR, 'b'], {'a': [1, {'b': 2}]}, [2]),
        ([0, STAR, 0], [{'a': [1]}], [1]),
        ([GLOBSTAR], {'a': 1}, [{'a': 1}, 1]),
        ([GLOBSTAR], {'a': {'b': 2}}, [{'a': {'b': 2}}, {'b': 2}, 2]),
        ([GLOBSTAR, 'b'], {'b': 1}, [1]),
        ([GLOBSTAR, 'b'], [{'b': 1}], [1]),
        ([GLOBSTAR, 'b'], [{'a': {'b': 1}}], [1]),
        ([GLOBSTAR, 'b'], {'a': [{'b': 1}]}, [1]),
        (['a', match_key(0), 'b'], {'a': [{'b': 2}]}, [2]),
        (['a', match_value(1)], {'a': {'b': 1}}, ['b']),
    ],
)
def test_lookup(target, data, matches):
    """Looking up a target from data should yield the expected results."""
    result = list(lookup(target, data))

    assert result == matches


@pytest.mark.parametrize('target', [0, {}, None])
def test_lookup_error(target):
    """Looking up an unsupported target should raise an exception."""
    with pytest.raises(TypeError):
        lookup(target, {})


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
    'target, key, value, data, matches',
    [
        # Default
        ('a', 'a', 1, None, [1]),
        ('b', 'a', 1, None, []),
        # Callable
        (match_key('a'), 'a', 1, None, [1]),
        (match_key('b'), 'a', 1, None, []),
        (match_value(1), 'a', 1, None, ['a']),
        (match_value(2), 'a', 1, None, []),
        # RePattern
        (re.compile(r'\w'), 'a', 1, None, [1]),
        (re.compile(r'\d'), 'a', 1, None, []),
        # STAR
        (STAR, 'a', 1, None, [1]),
        # GLOBSTAR
        (GLOBSTAR, 'a', 1, {}, [{}, 1]),
    ],
)
def test_lookup_target(target, key, value, data, matches):
    """Looking up a target from data should yield the expected results."""
    result = list(lookup_target(target, key, value, data))

    assert result == matches


@pytest.mark.parametrize(
    'func, args, matches',
    [
        (match(), ('a', 1, {'a': 1}), [{'a': 1}]),
        (match(key='a'), ('a', 1, {'a': 1}), [{'a': 1}]),
        (match(value=1), ('a', 1, {'a': 1}), [{'a': 1}]),
        (match('a', 1), ('a', 1, {'a': 1}), [{'a': 1}]),
        (match('b', 1), ('a', 1, {'a': 1}), []),
        (match('a', 2), ('a', 1, {'a': 1}), []),
    ],
)
def test_match(func, args, matches):
    """Matching key/value pairs should return the expected data."""
    result = list(func(*args))

    assert result == matches


@pytest.mark.parametrize(
    'key, args, matches',
    [
        (ALWAYS, ('a', 1, {}), [1]),
        ('a', ('a', 1, {}), [1]),
        ('b', ('a', 1, {}), []),
        (ALWAYS, (0, 'a', []), ['a']),
        (0, (0, 'a', []), ['a']),
        (1, (0, 'a', []), []),
    ],
)
def test_match_key(key, args, matches):
    """Matching a key should return the expected value."""
    result = list(match_key(key)(*args))

    assert result == matches


@pytest.mark.parametrize(
    'value, args, matches',
    [
        (ALWAYS, ('a', 1, {}), ['a']),
        (1, ('a', 1, {}), ['a']),
        (2, ('a', 1, {}), []),
        (ALWAYS, (0, '', []), [0]),
        ('a', (0, 'a', []), [0]),
        ('b', (0, 'a', []), []),
    ],
)
def test_match_value(value, args, matches):
    """Matching a value should return the expected key."""
    result = list(match_value(value)(*args))

    assert result == matches
