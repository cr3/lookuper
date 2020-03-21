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

``lookuper`` makes it easy to lookup a target in nested data structures. A
lookup can return the values matching a target as a string or,
equivalently, as a list:

.. code-block:: python

    >>> from lookuper import lookup
    >>> list(lookup('a.0.b', {'a': [{'b': 1}]}))
    [1]
    >>> list(lookup(['a', 0, 'b'], {'a': [{'b': 1}]}))
    [1]

As a string, a target can contain stars ('*') or globstars ('**'):

.. code-block:: python

    >>> list(lookup('a.*', {'a': {'b': 1, 'B': 2}}))
    [1, 2]
    >>> list(lookup('**.b', [{'b': 1}, {'a': {'b': 2}}]))
    [1, 2]

As a list, it can contain regular expressions or functions:

.. code-block:: python

    >>> import re
    >>> list(lookup(['a', re.compile(r'[a-z]')], {'a': {'b': 1, 'B': 2}}))
    [1]
    >>> from lookuper import match_key
    >>> list(lookup(['a', match_key(str.islower)], {'a': {'b': 1, 'B': 2}}))
    [1]

A lookup can also be useful to update all dictionaries that match the key `b`:

.. code-block:: python

    >>> from lookuper import GLOBSTAR, match
    >>> data = {'a': {'b': 1}, 'c': [{'b': 2}]}
    >>> for d in lookup([GLOBSTAR, match(key='b')], data):
    ...   d.update(b=d['b'] + 1)
    >>> data
    {'a': {'b': 2}, 'c': [{'b': 3}]}

Or to update all lists that contain `0`:

.. code-block:: python

    >>> data = {'a': [0, 1], 'b': {'c': [0, 2]}}
    >>> for l in lookup([GLOBSTAR, match(value=0)], data):
    ...   l.remove(0)
    >>> data
    {'a': [1], 'b': {'c': [2]}}


Project information
===================

``lookuper`` is released under the `MIT <https://choosealicense.com/licenses/mit/>`_ license,
the code on `GitHub <https://github.com/cr3/lookuper>`_,
and the latest release on `PyPI <https://pypi.org/project/lookuper/>`_.
