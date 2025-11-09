.. image:: https://img.shields.io/pypi/v/txy.svg
    :alt: PyPI-Server
    :target: https://pypi.org/project/txy/
.. image:: https://github.com/clivern/txy/actions/workflows/ci.yml/badge.svg
    :alt: Build Status
    :target: https://github.com/clivern/txy/actions/workflows/ci.yml

|

====
Txy
====

To use txy, follow the following steps:

1. Install txy python command line tool.

.. code-block::

    $ pip install txy


2. Create a virtual environment project01

.. code-block::

    $ txy create project01


3. Get virtual environment project01 info

.. code-block::

    $ txy info project01


4. Get list of virtual environments

.. code-block::

    $ txy list


5. Remove virtual environment project01

.. code-block::

    $ txy remove project01


6. Load current project environment

.. code-block::

    $ source $(txy current)
