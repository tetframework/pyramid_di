Changes
=======

0.4.1
=====

* 2021-03-19 The request-scoped services were not quite correct as they could have been instantiated twice
  - once in the traversal-time and the other time after context was set. Now the context is forced to None
  for the request-scoped services.

0.4.0
=====

* 2020-11-25 Python 3.6+ only; better test coverage, fixes for scoped services, deprecations and so forth.

0.3.dev0
========

* 2020-11 Unreleased development version


0.2.dev0
========

* 2020-11-04 Require Python 3 for cleaner code

0.1
===

* 2018-03-26 Initial release
