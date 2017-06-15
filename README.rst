===========
Destination
===========
.. image:: https://travis-ci.org/futursolo/destination.svg?branch=master
   :target: https://travis-ci.org/futursolo/destination

Destination is a framework agnostic regular expression based path routing
library.

Installation
============

.. code-block:: shell

   $ pip install -U https://github.com/futursolo/destination

Requirements
============
- Python 3.5.1 or higher

Usage
=====
This is a simple overview of the usage, for detailed documentation please
browse the source code.

Abstract Base Classes
---------------------
- :code:`BaseRule`:

  This class establishes a series of methods and properties that a rule
  should implement and provides helper method to simplify the implementation
  process.

- :code:`BaseDispatcher`:

  This class establishes a series of methods and propeties that a
  dispatcher should implement and provides helper method to simplify
  the implemenation process.

Implementations
---------------
- :code:`ReRule`:

  This class is an implementation of :code:`BaseRule` that uses regular
  expressions to implement path dispatching.

- :code:`Dispatcher`:

  This class is an implementation of :code:`BaseDispatcher` that accepts
  subclasses of :code:`BaseRule` and distributes the path over the rules.

- :code:`ReSubDispatcher`:

  This is a subclass of :code:`Dispatcher` and :code:`ReRule` that can be added
  to a :code:`Dispatcher` and distributes the path fragment over the rules.

Result & Exceptions
-------------------
- :code:`ResolvedPath`:

  This is a :code:`NamedTuple` that contains solved information from the path
  used to be parsed by a :code:`BaseRule` or resolved by a :code:`BaseDispatcher`.

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
