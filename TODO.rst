====
TODO
====

Structural
----------

* Implement Scrutinizer

Documentation
-------------

* Change all documentation to be rst-friendly for sphinx.

Tests
-----

* Dev tests for metadata retrieval.
* Dev tests for track retrieval.
* Dev tests for track deletion (both styles).
* Base function unit tests.

Current Example
---------------

* Iterate over matches (should really use 2 search terms to show how that would work)
* Change example to use get_link_href() & other new helper functions.
* Iterate through items & result arrays together.  In py2:
  import itertools
  for f, b in intertools.izip(foo, bar):
      print(f, b)

Examples
--------

* Retrieving and processing YouTube channel.

Features
--------

* Python objects that return dates should return datetimes.

Implementation
--------------

* Simplify embed list handling.

