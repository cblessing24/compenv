"""Contains custom types."""
from __future__ import annotations

from typing import Mapping, Union

PrimaryKey = Mapping[str, Union[str, int, float]]
