"""Lookup nested data structures."""

import re
from collections.abc import (
    Callable,
    Mapping,
    Sequence,
    Set,
)
from functools import singledispatch
from itertools import islice

try:
    # New in version 3.7
    RePattern = re.Pattern
except AttributeError:
    RePattern = type(re.compile(''))


# Lookup types.
STAR = type('_Star', (), {'__repr__': lambda _: '*'})()
GLOBSTAR = type('_GlobStar', (), {'__repr__': lambda _: '**'})()

# Match functions.
ALWAYS = type('_Always', (), {'__call__': lambda *_: True})()


@singledispatch
def lookup(target, data):
    """Lookup matching 'targets' in `data`."""
    raise TypeError('Unsupported lookup target: {!r}'.format(target))


lookup.register(str, lambda target, data: (
    lookup([
        STAR if k == '*'
        else GLOBSTAR if k == '**'
        else int(k) if k.isdigit()
        else k
        for k in target.split('.')
    ] if target else [], data)
))
lookup.register(Sequence, lambda target, data: (
    lookup_data(data, target)
))
lookup_data = singledispatch(lambda data, targets: (
    () if targets else (data,)
))
lookup_data.register(Mapping, lambda data, targets: (
    (
        k
        for d in lookup_key(targets[0], data)
        for k in lookup_data(d, targets[1:])
    ) if targets else (data,)
))
lookup_data.register(Sequence, lambda data, targets: (
    (
        k
        for d in lookup_index(targets[0], data)
        for k in lookup_data(d, targets[1:])
    ) if targets else (data,)
))
lookup_data.register(Set, lambda data, targets: (
    (
        k
        for d in lookup_value(targets[0], data)
        for k in lookup_data(d, targets[1:])
    ) if targets else (data,)
))
# A `str` is a `Sequence`, so register a separate handler.
lookup_data.register(str, lambda data, targets: (
    () if targets else (data,)
))
lookup_index = singledispatch(lambda index, data: ())
lookup_index.register(Callable, lambda index, data: (
    d
    for i, v in enumerate(data)
    for d in index(i, v, data)
))
lookup_index.register(int, lambda index, data: (
    (data[index],) if index < len(data) else ()
))
lookup_index.register(type(STAR), lambda index, data: (
    data
))
lookup_index.register(type(GLOBSTAR), lambda index, data: (
    data,
    *(
        k
        for d in lookup_index(STAR, data)
        for k in (d, *islice(lookup_data(d, [index]), 1, None))
    ),
))
lookup_key = singledispatch(lambda key, data: (
    (data[key],) if key in data else ()
))
lookup_key.register(Callable, lambda key, data: (
    d
    for k, v in data.items()
    for d in key(k, v, data)
))
lookup_key.register(RePattern, lambda key, data: (
    lookup_key(match_key(key.match), data)
))
lookup_key.register(type(STAR), lambda key, data: (
    data.values()
))
lookup_key.register(type(GLOBSTAR), lambda key, data: (
    data,
    *(
        k
        for d in lookup_key(STAR, data)
        for k in (d, *islice(lookup_data(d, [key]), 1, None))
    ),
))
lookup_value = singledispatch(lambda value, data: (
    (value,) if value in data else ()
))
lookup_value.register(Callable, lambda value, data: (
    d
    for v in data
    for d in value(v, v, data)
))
lookup_value.register(RePattern, lambda value, data: (
    lookup_value(match_key(value.match), data)
))
lookup_value.register(type(STAR), lambda value, data: (
    data
))
lookup_value.register(type(GLOBSTAR), lambda value, data: (
    data,
    *(
        k
        for d in lookup_value(STAR, data)
        for k in (d, *islice(lookup_data(d, [value]), 1, None))
    ),
))


def match(key=ALWAYS, value=ALWAYS):
    """Match a key/value pair within lookups."""
    key_func = match_key(key)
    value_func = match_value(value)
    return lambda k, v, data: (
        (data,) if key_func(k, v, data) and value_func(k, v, data) else ()
    )


# Higher-order functions to match within lookups.
match_key = singledispatch(lambda key: (
    match_key(lambda k: k == key)
))
match_key.register(Callable, lambda key: (
    lambda k, v, _: (v,) if key(k) else ()
))
match_value = singledispatch(lambda value: (
    match_value(lambda v: v == value)
))
match_value.register(Callable, lambda value: (
    lambda k, v, _: (k,) if value(v) else ()
))
