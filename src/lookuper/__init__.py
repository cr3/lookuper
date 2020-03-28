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
    reduce,
    singledispatch,
)
from operator import (
    itemgetter,
    methodcaller,
)

try:
    # New in version 3.7
    RePattern = re.Pattern
except AttributeError:  # pragma: no cover
    RePattern = type(re.compile(''))


class _Anything:
    """Callable class to match anything by always returning `True`.

    This is a singleton - there is only ever one of it.
    """

    _singleton = None

    def __new__(cls):
        if _Anything._singleton is None:
            _Anything._singleton = super(_Anything, cls).__new__(cls)
        return _Anything._singleton

    def __call__(self, _):
        return True

    def __repr__(self):
        return 'ANYTHING'


anything = _Anything()
"""Callable to match anything by always returning `True`."""


class _Something:
    """Callable class to match equality with a value."""

    __slots__ = ('a',)

    def __init__(self, a):
        self.a = a

    def __call__(self, b):
        return self.a == b

    def __repr__(self):
        return repr(self.a)


class Match:
    """Match a key/value pair."""

    __slots__ = (
        'key',
        'value',
    )

    def __init__(self, key=anything, value=anything):
        self.key = key if callable(key) else _Something(key)
        self.value = value if callable(value) else _Something(value)

    def __call__(self, key, value):
        return self.key(key) and self.value(value)

    def __repr__(self):
        return '{cls}(key={key!r}, value={value!r})'.format(
            cls=self.__class__.__name__, key=self.key, value=self.value,
        )


# Lookup constants.
STAR = type('_Star', (UserString,), {})('*')
GLOBSTAR = type('_GlobStar', (UserString,), {})('**')


def lookup(data, *targets):
    """Lookup a matching `target` in `data`."""
    return map(itemgetter(1), lookup_target(targets, anything, data))


lookup_data = singledispatch(lambda _: ())
lookup_data.register(Mapping, methodcaller('items'))
lookup_data.register(Sequence, enumerate)
lookup_data.register(Set, lambda data: zip(data, data))
# A `str` is a `Sequence`, so register a separate handler.
lookup_data.register(str, lambda _: ())

lookup_target = singledispatch(
    lambda target, *i: lookup_target(Match(target), *i)
)
lookup_target.register(
    str,
    lambda target, *i: lookup_target(
        STAR
        if target == '*'
        else GLOBSTAR
        if target == '**'
        else Match(re.sub(r'\\(\*)', r'\1', target)),
        *i
    )
    if target
    else (),
)
lookup_target.register(
    Callable, lambda target, *i: lookup_target(Match(target), *i)
)
lookup_target.register(
    Match, lambda target, _, v: (j for j in lookup_data(v) if target(*j))
)
lookup_target.register(
    RePattern, lambda target, *i: lookup_target(target.match, *i)
)
lookup_target.register(
    Sequence,
    lambda target, *i: reduce(
        lambda j, t: (l for k in j for l in lookup_target(t, *k)),
        target,
        (i,),
    ),
)
lookup_target.register(type(STAR), lambda target, _, v: lookup_data(v))
lookup_target.register(
    type(GLOBSTAR),
    lambda target, *i: (
        (i, *(k for j in lookup_data(i[1]) for k in lookup_target(target, *j)))
    ),
)
