.. miscreaders documentation master file, created by
   sphinx-quickstart on Sat Apr  5 17:43:19 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

miscreaders documentation
=========================

This library is a collection of parsers for various tools. It can read data from
`Loop Habit Tracker <https://github.com/iSoron/uhabits>`_,
`StayFree <https://stayfreeapps.com>`_ and from `Moonwatch.rs <https://github.com/tkarabela/moonwatch-rs>`_
(my desktop usage logging tool).

.. toctree::
   :maxdepth: 3
   :caption: API reference

   api-reference

Installation
------------

.. code-block:: bash

   pip install miscreaders

Example
-------

.. code-block:: python

   >>> from miscreaders.stayfree import StayfreeXlsReader
   >>> reader = StayfreeXlsReader("StayFree Export - Total Usage - 8_9_24.xls")
   >>> reader.get_usage_time_df()
   shape: (6_222, 4)
   ┌────────────┬─────────────┬──────────────┬────────┐
   │ date       ┆ app         ┆ duration     ┆ device │
   │ ---        ┆ ---         ┆ ---          ┆ ---    │
   │ date       ┆ str         ┆ duration[μs] ┆ str    │
   ╞════════════╪═════════════╪══════════════╪════════╡
   │ 2023-11-10 ┆ addititious ┆ 0µs          ┆        │
   │ 2023-11-11 ┆ addititious ┆ 0µs          ┆        │
   │ 2023-11-12 ┆ addititious ┆ 0µs          ┆        │
   │ 2023-11-13 ┆ addititious ┆ 0µs          ┆        │
   │ 2023-11-14 ┆ addititious ┆ 6s           ┆        │
   │ …          ┆ …           ┆ …            ┆ …      │
   │ 2024-03-06 ┆ xylometer   ┆ 53m 8s       ┆        │
   │ 2024-03-07 ┆ xylometer   ┆ 0µs          ┆        │
   │ 2024-03-08 ┆ xylometer   ┆ 30m 54s      ┆        │
   │ 2024-03-09 ┆ xylometer   ┆ 0µs          ┆        │
   │ 2024-03-10 ┆ xylometer   ┆ 0µs          ┆        │
   └────────────┴─────────────┴──────────────┴────────┘

License
-------

.. include:: ../../LICENSE.txt
