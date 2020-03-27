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
from itertools import starmap
from operator import (
    itemgetter,
    methodcaller,
)

try:
    # New in version 3.7
    RePattern = re.Pattern
except AttributeError:  # pragma: no cover
    RePattern = type(re.compile(''))


# Match constants.
ANY = type(
    '_Any', (), {'__call__': lambda *_: True, '__repr__': lambda _: 'ANY'}
)()


class Match:
    """Match a key/value pair."""

    def __init__(self, key=ANY, value=ANY):
        self.key = key
        self.value = value

    def __call__(self, key, value):
        return all(
            starmap(
                lambda target, arg: (
                    target(arg) if callable(target) else target == arg
                ),
                zip((self.key, self.value), (key, value)),
            )
        )

    def __repr__(self):
        return '{cls}(key={key!r}, value={value!r})'.format(
            cls=self.__class__.__name__, key=self.key, value=self.value,
        )


# Lookup constants.
STAR = type('_Star', (UserString,), {})('*')
GLOBSTAR = type('_GlobStar', (UserString,), {})('**')


def lookup(data, *targets):
    """Lookup a matching `target` in `data`."""
    return map(itemgetter(1), lookup_target(targets, ANY, data))


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
    Match, lambda target, _, v: (j for j in lookup_data(v) if target(*j))
)
lookup_target.register(
    Callable, lambda target, *i: lookup_target(Match(target), *i)
)
lookup_target.register(
    RePattern, lambda target, *i: lookup_target(target.match, *i)
)
lookup_target.register(type(STAR), lambda target, _, v: lookup_data(v))
lookup_target.register(
    type(GLOBSTAR),
    lambda target, *i: (
        (i, *(k for j in lookup_data(i[1]) for k in lookup_target(target, *j)))
    ),
)
