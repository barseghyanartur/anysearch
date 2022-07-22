=========
anysearch
=========
``AnySearch`` is a ``Elasticsearch`` and ``OpenSearch`` compatibility library.
It provides utility functions for smoothing over the differences between the
Python libraries with the goal of writing Python code that is compatible on
both (including the ``*search``, ``*search-dsl`` and ``django-*search-dsl``
integration packages).

See the documentation for more information on what is provided.

.. image:: https://img.shields.io/pypi/v/anysearch.svg
   :target: https://pypi.python.org/pypi/anysearch
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/anysearch.svg
    :target: https://pypi.python.org/pypi/anysearch/
    :alt: Supported Python versions

.. image:: https://github.com/barseghyanartur/anysearch/workflows/test/badge.svg
   :target: https://github.com/barseghyanartur/anysearch/actions?query=workflow%3Atest
   :alt: Build Status

.. image:: https://readthedocs.org/projects/anysearch/badge/?version=latest
    :target: http://anysearch.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://github.com/barseghyanartur/anysearch/#License
   :alt: MIT

.. image:: https://coveralls.io/repos/github/barseghyanartur/anysearch/badge.svg?branch=master
    :target: https://coveralls.io/github/barseghyanartur/anysearch?branch=master
    :alt: Coverage

Documentation
=============
Documentation is available on `Read the Docs
<http://anysearch.readthedocs.io/>`_.

Prerequisites
=============
- Python 3.7, 3.8, 3.9 and 3.10.

Installation
============
Install latest stable version from PyPI:

.. code-block:: sh

    pip install anysearch

or latest stable version from GitHub:

.. code-block:: sh

    pip install https://github.com/barseghyanartur/anysearch/archive/main.tar.gz

Configuration
=============
``AnySearch`` automatically detects whether you use ``Elasticsearch`` or 
``OpenSearch`` by looking at which packages are installed.
However, if you have both packages installed and you can instruct ``AnySearch``
which one do you actually want to use. The way to do that is to set the
``ANYSEARCH_PREFERRED_BACKEND`` environment variable to either ``Elasticsearch`` 
or ``OpenSearch``.

For ``Elasticsearch``:

.. code-block:: python

    import os
    os.environ.setdefault("ANYSEARCH_PREFERRED_BACKEND", "Elasticsearch")

For ``OpenSearch``:

.. code-block:: python

    import os
    os.environ.setdefault("ANYSEARCH_PREFERRED_BACKEND", "OpenSearch")

Usage
=====
``elasticsearch``/``opensearch``
----------------------------------------
How-to
~~~~~~
In ``elasticsearch`` you would do:

.. code-block:: python

    from elasticsearch import Connection, Elasticsearch

In ``opensearch`` you would do:

.. code-block:: python

    from opensearch_py import Connection, OpenSearch

With ``anysearch`` you would change that to:

.. code-block:: python

    from anysearch.search import Connection, AnySearch

``elasticsearch-dsl``/``opensearch-dsl``
----------------------------------------
How-to
~~~~~~
In ``elasticsearch-dsl`` you would do:

.. code-block:: python

    from elasticsearch_dsl import AggsProxy, connections, Keyword
    from elasticsearch_dsl.document import Document

In ``opensearch-dsl`` you would do:

.. code-block:: python

    from opensearch_dsl import AggsProxy, connections, Keyword
    from opensearch_dsl.document import Document

With ``anysearch`` you would change that to:

.. code-block:: python

    from anysearch.search_dsl import AggsProxy, connections, Keyword
    from anysearch.search_dsl.document import Document

``django-elasticsearch-dsl``/``django-opensearch-dsl``
------------------------------------------------------
How-to
~~~~~~
In ``django-elasticsearch-dsl`` you would do:

.. code-block:: python

    from django_elasticsearch_dsl import fields, registry
    from django_elasticsearch_dsl.documents import Document
    from django_elasticsearch_dsl.fields import TextField

In ``opensearch-dsl`` you would do:

.. code-block:: python

    from django_opensearch_dsl import fields, registry
    from django_opensearch_dsl.documents import Document
    from django_opensearch_dsl.fields import TextField

With ``anysearch`` you would change that to:

.. code-block:: python

    from anysearch.django_search_dsl import fields, registry
    from anysearch.django_search_dsl.documents import Document
    from anysearch.django_search_dsl.fields import TextField

Testing
=======
Project is covered with tests.

To test with all supported Python versions type:

.. code-block:: sh

    tox

To test against specific environment, type:

.. code-block:: sh

    tox -e py39

To test just your working environment type:

.. code-block:: sh

    pytest

To run a single test in your working environment type:

.. code-block:: sh

    pytest test_anysearch.py

To run a single test class in a given test module in your working environment
type:

.. code-block:: sh

    pytest test_anysearch.py::DjangoSearchDSLTestCase

It's assumed that you have either ``elasticsearch-dsl`` or ``opensearch-dsl``
installed. If not, install the requirements first.

Writing documentation
=====================
Keep the following hierarchy.

.. code-block:: text

    =====
    title
    =====

    header
    ======

    sub-header
    ----------

    sub-sub-header
    ~~~~~~~~~~~~~~

    sub-sub-sub-header
    ^^^^^^^^^^^^^^^^^^

    sub-sub-sub-sub-header
    ++++++++++++++++++++++

    sub-sub-sub-sub-sub-header
    **************************

License
=======
MIT

Support
=======
For any security issues contact me at the e-mail given in the `Author`_ section.
For overall issues, go to `GitHub <https://github.com/barseghyanartur/anysearch/issues>`_.

Author
======
Artur Barseghyan <artur.barseghyan@gmail.com>
