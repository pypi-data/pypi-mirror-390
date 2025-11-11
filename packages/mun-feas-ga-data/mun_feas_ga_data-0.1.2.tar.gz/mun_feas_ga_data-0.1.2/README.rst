=================
GAD: GA Data tool
=================


Installation
============

To install from `PyPI <pypi.org>`_, run `pip install mun-feas-ga-data`.


Usage
=====

Given some GA data in a directory called `ga-data` and a curriculum map in a file
called `ENEL-map.xlsx`, you can convert the data into a format ready for FEAMS
processing using the following command:

```
gad feamsify ga-data/ --curriculum-map ENEL-map.xlsx --output FEAMS-ENEL`
```

This will *check* the data for consistency with the curriculum map,
*convert* it into FEAMS' expected format and *output* that data to the
specified output directory (here, `FEAMS-ENEL`).


Development
===========

To hack on GAD, install
`Python <https://www.python.org/downloads>`_
and
`Poetry <https://python-poetry.org/docs/#installation>`_,
check out this repository and then run
`poetry install`.
By default, this will install GAD in editable mode: make changes to the code and they
will be immediately reflected when you next run `gad`.
