===========
Destination
===========
.. image:: https://travis-ci.org/futursolo/destination.svg?branch=master
   :target: https://travis-ci.org/futursolo/destination

.. image:: https://coveralls.io/repos/github/futursolo/destination/badge.svg?branch=master
   :target: https://coveralls.io/github/futursolo/destination?branch=master

Destination is a framework agnostic regular expression based path routing
library.

Installation
============

.. code-block:: shell

   $ pip install -U destination

Requirements
============
- Python 3.5.1 or higher

Thread Safety
=============
Currently, destination is not thread safety. Hence, you should deepcopy
instances or add a mutex lock before try to use dispatchers and rules in the
other threads.

Usage
=====
The default implementation of url parsing uses regular expressions. This is
similar to Django and Tornado. You create rules and dispatchers to resolve and
parse your url using regular expressions set in the rules.

Generally, you should start with creating a :code:`ReRule` and a
:code:`Dispatcher`. You can create a :code:`ReRule` with the regular expression
that is going to be used to parse (and possibly compose) the url, and an
optional identifier to help you identify which rule is parsed, if an identifier
is not provided or its value is set to :code:`None`, the rule itself will be
used as an identifier. A :code:`Dispatcher` may be instantiated with no
arguments as a storage of multiple rules. You can add or remove rules at
any time.

:code:`ReSubDispatcher` is a sub-dispatcher that can be added to a dispatcher
as a rule. It uses regular expressions to chop off the part matched to the
regular expression and dispatches the rest part to the rules added to it.

:code:`BaseRule` and :code:`BaseDispatcher` can be used to create custom rules
and dispatchers.

Licence
=======
MIT License

Copyright (c) 2017 Kaede Hoshikawa

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
