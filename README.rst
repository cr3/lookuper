.. image:: https://img.shields.io/pypi/v/lookuper.svg
   :target: https://pypi.org/project/lookuper/
   :alt: PyPI
.. image:: https://img.shields.io/pypi/pyversions/lookuper.svg
   :target: https://pypi.org/project/lookuper/
   :alt: Versions
.. image:: https://travis-ci.org/cr3/lookuper.svg?branch=master
   :target: https://travis-ci.org/cr3/lookuper/
   :alt: Travis
.. image:: https://codecov.io/github/cr3/lookuper/branch/master/graph/badge.svg
   :target: https://codecov.io/github/cr3/lookuper/
   :alt: Codecov
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black/
   :alt: Black

``lookuper`` makes it easy to lookup a target in nested data structures. A
lookup yields the values matching a target as an arguments list:

.. code-block:: python

    >>> from lookuper import lookup
    >>> list(lookup({'a': [{'b': 1}]}, 'a', 0, 'b'))
    [1]

A target can contain stars (``*``) to match anything and globstars
(``**``) to match anything recursively:

.. code-block:: python

    >>> list(lookup({'a': {'b': 1, 'B': 2}}, 'a', '*'))
    [1, 2]
    >>> list(lookup([{'b': 1}, {'a': {'b': 2}}], '**', 'b'))
    [1, 2]

Note that these special characters can be escaped:

    >>> list(lookup({'*': 1}, r'\*'))
    [1]

A target can also contain functions and regular expressions:

.. code-block:: python

    >>> list(lookup({'a': {'b', 'B'}}, 'a', str.islower))
    ['b']
    >>> import re
    >>> list(lookup({'a': {'b', 'B'}}, 'a', re.compile(r'[a-z]')))
    ['b']

Recipes
-------

``lookuper`` can be combined with other libraries like
`more-itertools <https://pypi.org/project/more-itertools/>`_
to return only one value:

.. code-block:: python

    >>> from more_itertools import only
    >>> def lookup1(data, *targets, **kw):
    ...     return only(lookup(data, *targets), **kw)
    >>> lookup1({}, 'a')
    >>> lookup1({'a': 1}, 'a')
    1
    >>> lookup1({'a': 1, 'b': 2}, '*')
    Traceback (most recent call last):
    ...
    ValueError: Expected exactly one item in iterable, but got 1, 2, and perhaps more.

Extensions
----------

By default, ``lookuper`` only supports nested data structures like
mappings, sequences and sets. It can extended to support other types:

.. code-block:: python

    >>> from lookuper import lookup_data
    >>> func = lookup_data.register(object, lambda data: (
    ...     (name, getattr(data, name, None)) for name in dir(data)
    ... ))
    >>> list(lookup(object(), '__class__', '__class__', '__name__'))
    ['type']

Project information
===================

``lookuper`` is released under the `MIT <https://choosealicense.com/licenses/mit/>`_ license,
the code on `GitHub <https://github.com/cr3/lookuper>`_,
and the latest release on `PyPI <https://pypi.org/project/lookuper/>`_.
