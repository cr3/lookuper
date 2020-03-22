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
lookup can return the values matching a target as a string or,
equivalently, as a list:

.. code-block:: python

    >>> from lookuper import lookup
    >>> list(lookup('a.0.b', {'a': [{'b': 1}]}))
    [1]
    >>> list(lookup(['a', 0, 'b'], {'a': [{'b': 1}]}))
    [1]

As a string, a target can contain stars (``*``) to match anything and
globstars (``**``) to match anything recursively:

.. code-block:: python

    >>> list(lookup('a.*', {'a': {'b': 1, 'B': 2}}))
    [1, 2]
    >>> list(lookup('**.b', [{'b': 1}, {'a': {'b': 2}}]))
    [1, 2]

As a list, the same matching can be achieved with ``STAR`` and
``GLOBSTAR`` respectively. Additionally, a target can also contain
regular expressions and functions:

.. code-block:: python

    >>> from lookuper import STAR
    >>> list(lookup(['a', STAR], {'a': {'b': 1, 'B': 2}}))
    [1, 2]
    >>> import re
    >>> list(lookup(['a', re.compile(r'[a-z]')], {'a': {'b': 1, 'B': 2}}))
    [1]
    >>> from lookuper import match_key
    >>> list(lookup(['a', match_key(str.islower)], {'a': {'b': 1, 'B': 2}}))
    [1]

Extensions
----------

By default, ``lookuper`` only supports nested data structures like
mappings, sequences and sets. It can extended to support other types:

.. code-block:: python

    >>> from lookuper import lookup_data
    >>> func = lookup_data.register(object, lambda data: (
    ...     (name, getattr(data, name)) for name in dir(data)
    ... ))
    >>> list(lookup('__class__.__doc__', object()))
    ['The most base type']

Project information
===================

``lookuper`` is released under the `MIT <https://choosealicense.com/licenses/mit/>`_ license,
the code on `GitHub <https://github.com/cr3/lookuper>`_,
and the latest release on `PyPI <https://pypi.org/project/lookuper/>`_.
