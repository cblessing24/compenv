# compenv

<p align="center">
<img src="compenv.png" alt="compenv logo" style="display: block; margin-left: auto; margin-right: auto; width: 20%">
<br>
<a href="https://github.com/sinzlab/compenv/actions/workflows/ci.yml"><img alt="Actions Status" src="https://github.com/sinzlab/compenv/actions/workflows/ci.yml/badge.svg"></a>
<a href="https://codecov.io/gh/sinzlab/compenv"><img src="https://codecov.io/gh/sinzlab/compenv/branch/main/graph/badge.svg?token=r1gr933Slt"/></a>
<a href="https://pypi.org/project/compenv/"><img alt="PyPI" src="https://img.shields.io/pypi/v/compenv"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

Track information about installed packages.

## Install

```bash
pip install compenv
```

## Usage

Decorate the auto-populated table on which you want to track the installed packages:

```python
from compenv import record_environment
from datajoint import Computed, schema

schema = schema("my_schema")

@record_environment(schema)
class MyAutoPopulatedTable(Computed):
    ...
```

After populating the table you can view the generated records in the records table:

```python
MyAutoPopulatedTable.records()
```

You can get a difference view between two records:

```python
MyAutoPopulatedTable.records.diff(key1, key2)
```
