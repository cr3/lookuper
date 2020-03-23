"""Lookup nested data structures."""

import re
from collections import UserString
from collections.abc import (
    Callable,
    Mapping,
    Sequence,
    Set,
)
from functools import (
    partial,
    singledispatch,
)
from itertools import islice
from operator import (
    eq,
    methodcaller,
)

try:
    # New in version 3.7
    RePattern = re.Pattern
except AttributeError:
    RePattern = type(re.compile(''))


# Lookup types.
STAR = type('_Star', (UserString,), {})('*')
GLOBSTAR = type('_GlobStar', (UserString,), {})('**')

# Match functions.
ALWAYS = type('_Always', (), {'__call__': lambda *_: True})()


@singledispatch
def lookup(target, data):
    """Lookup matching 'targets' in `data`."""
    raise TypeError('Unsupported lookup target: {!r}'.format(target))


lookup.register(
    str,
    lambda target, data: (
        lookup(
            [
                STAR
                if k == '*'
                else GLOBSTAR
                if k == '**'
                else int(k)
                if k.isdigit()
                else k
                for k in target.split('.')
            ]
            if target
            else [],
            data,
        )
    ),
)
lookup.register(
    Sequence,
    lambda target, data: (
        (
            i
            for k, v in lookup_data(data)
            for d in lookup_target(target[0], k, v, data)
            for i in lookup(target[1:], d)
        )
        if target
        else (data,)
    ),
)

lookup_data = singledispatch(lambda _: ())
lookup_data.register(Mapping, methodcaller('items'))
lookup_data.register(Sequence, enumerate)
lookup_data.register(Set, lambda data: ((v, v) for v in data))
# A `str` is a `Sequence`, so register a separate handler.
lookup_data.register(str, lambda _: ())

lookup_target = singledispatch(
    lambda target, key, value, data: (
        lookup_target(match_key(target), key, value, data)
    )
)
lookup_target.register(
    Callable, lambda target, key, value, data: (target(key, value, data))
)
lookup_target.register(
    RePattern,
    lambda target, key, value, data: (
        lookup_target(match_key(target.match), key, value, data)
    ),
)
lookup_target.register(type(STAR), lambda target, key, value, _: ((value,)))
lookup_target.register(
    type(GLOBSTAR),
    lambda target, key, value, data: (
        (data, value, *islice(lookup([GLOBSTAR], value), 1, None))
    ),
)


def match(key=ALWAYS, value=ALWAYS):
    """Match a key/value pair within lookups."""
    key_func = match_key(key)
    value_func = match_value(value)
    return lambda k, v, data: (
        (data,) if key_func(k, v, data) and value_func(k, v, data) else ()
    )


# Higher-order functions to match within lookups.
match_key = singledispatch(lambda key: match_key(partial(eq, key)))
match_key.register(
    Callable, lambda key: (lambda k, v, _: (v,) if key(k) else ())
)
match_value = singledispatch(lambda value: match_value(partial(eq, value)))
match_value.register(
    Callable, lambda value: (lambda k, v, _: (k,) if value(v) else ())
)
