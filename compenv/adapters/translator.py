"""Contains code used for translation between external and internal data."""
from __future__ import annotations

import hashlib
import json
from typing import TYPE_CHECKING, Callable, Dict

from ..model.computation import Identifier

if TYPE_CHECKING:
    from datajoint.table import PrimaryKey


class DJTranslator:
    """Translator used to translate between DataJoint-specific primary keys and dommain-model-specific identifiers.

    Translations from identifier to primary key are only possible if the same primary key was previously translated into
    its corresponding identifier.
    """

    def __init__(self, to_identifier: Callable[[PrimaryKey], Identifier]) -> None:
        """Initialize the translator."""
        self._to_identifier = to_identifier
        self._reverse_translations: Dict[Identifier, PrimaryKey] = {}

    def to_identifier(self, primary: PrimaryKey) -> Identifier:
        """Translate the identifier to its corresponding primary key."""
        identifier = self._to_identifier(primary)
        self._reverse_translations[identifier] = primary.copy()
        return identifier

    def to_primary(self, identifier: Identifier) -> PrimaryKey:
        """Translate the primary key into its corresponding identifier."""
        return self._reverse_translations[identifier]


def blake2b(primary: PrimaryKey) -> Identifier:
    """Convert the primary key into an identifier using the blake2b hashing algorithm."""
    return Identifier(hashlib.blake2b(json.dumps(primary, sort_keys=True).encode()).hexdigest())
