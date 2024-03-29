Release history and notes
=========================
`Sequence based identifiers
<http://en.wikipedia.org/wiki/Software_versioning#Sequence-based_identifiers>`_
are used for versioning (schema follows below):

.. code-block:: text

    major.minor[.revision]

- It's always safe to upgrade within the same minor version (for example, from
  0.3 to 0.3.4).
- Minor version changes might be backwards incompatible. Read the
  release notes carefully before upgrading (for example, when upgrading from
  0.3.4 to 0.4).
- All backwards incompatible changes are mentioned in this document.

0.2.2
-----
2022-12-28

- Added more attributes to the ``search_dsl`` module.
- Tested against Python 3.11.
- Stop testing against Python 3.6 (due to GitHub CI difficulties).

0.2.1
-----
2022-07-31

- Added some of the missing attributes to the ``search_dsl`` module.

0.2
---
2022-07-27

- Dropped support for ``Django`` integration packages. Support for both
  ``Elasticsearch`` and ``OpenSearch`` will either be built in the
  ``django-elasticsearch-dsl`` package or a (rebranded)
  `fork of it <https://github.com/barseghyanartur/django-elasticsearch-dsl/tree/anysearch>`__.

0.1.7
-----
2022-07-26

- Improved ``elasticsearch-py``/``opensearch-py`` support.

0.1.6
-----
2022-07-25

- Documentation fixes.
- More tests.

0.1.5
-----
2022-07-24

Loosen Python requirements to allow Python 3.6 installations. Note, that
although package is not "officially" tested with Python 3.6, it has been tested
locally.

0.1.4
-----
2022-07-24

- Improved Django support.

0.1.3
-----
2022-07-22

- Better support of ``elasticsearch``/``opensearch``.

0.1.2
-----
2022-07-21

- Minor Python 3.7 and 3.8 fixes.

0.1.1
-----
2022-07-21

- Minor improvements.
- Add docs.

0.1
---
2022-07-21

- Initial beta release.
