# compenv

[![ci](https://github.com/cblessing24/compenv/actions/workflows/ci.yml/badge.svg)](https://github.com/cblessing24/compenv/actions/workflows/ci.yml)

Track information about the execution environment of computations.

## Install

```bash
pip install compenv
```

## Usage

Decorate the auto-populated table on which you want to track the execution environments:

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
