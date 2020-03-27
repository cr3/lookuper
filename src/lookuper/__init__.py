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
    reduce,
    singledispatch,
)
from operator import (
    eq,
    itemgetter,
    methodcaller,
)

try:
    # New in version 3.7
    RePattern = re.Pattern
except AttributeError:  # pragma: no cover
    RePattern = type(re.compile(''))


# Lookup types.
STAR = type('_Star', (UserString,), {})('*')
GLOBSTAR = type('_GlobStar', (UserString,), {})('**')

# Match functions.
ALWAYS = type('_Always', (), {'__call__': lambda *_: True})()
NEVER = type('_Never', (), {'__call__': lambda *_: False})()


def lookup(data, *targets):
    """Lookup a matching `target` in `data`."""
    return map(itemgetter(1), lookup_target(targets, ALWAYS, data))


lookup_data = singledispatch(lambda _: ())
lookup_data.register(Mapping, methodcaller('items'))
lookup_data.register(Sequence, enumerate)
lookup_data.register(Set, lambda data: zip(data, data))
# A `str` is a `Sequence`, so register a separate handler.
lookup_data.register(str, lambda _: ())

lookup_target = singledispatch(
    lambda target, *i: lookup_target(match(target), *i)
)
lookup_target.register(
    Sequence,
    lambda target, *i: reduce(
        lambda j, t: (l for k in j for l in lookup_target(t, *k)),
        target,
        (i,),
    ),
)
lookup_target.register(
    str,
    lambda target, *i: lookup_target(
        [
            STAR
            if k == '*'
            else GLOBSTAR
            if k == '**'
            else int(k)
            if k.isdigit()
            else match(re.sub(r'\\([\.\*])', r'\1', k))
            for k in re.split(r'(?<!\\)\.', target)
        ]
        if target
        else [],
        *i
    ),
)
lookup_target.register(
    Callable, lambda target, _, v: (j for j in lookup_data(v) if target(*j))
)
lookup_target.register(
    RePattern, lambda target, *i: lookup_target(match(target.match), *i)
)
lookup_target.register(type(STAR), lambda target, _, v: lookup_data(v))
lookup_target.register(
    type(GLOBSTAR),
    lambda target, *i: (
        (i, *(k for j in lookup_data(i[1]) for k in lookup_target(target, *j)))
    ),
)


def match(key=ALWAYS, value=ALWAYS):
    """Match a key/value pair within lookups."""
    key_func = match_key(key)
    value_func = match_value(value)
    return lambda *i: key_func(*i) and value_func(*i)


# Higher-order functions to match within lookups.
match_key = singledispatch(lambda key: match_key(partial(eq, key)))
match_key.register(Callable, lambda func: (lambda k, _: func(k)))
match_value = singledispatch(lambda value: match_value(partial(eq, value)))
match_value.register(Callable, lambda func: (lambda _, v: func(v)))
