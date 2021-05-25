"""Contains code used for translation between external and internal data."""
import hashlib
import json
from collections.abc import Mapping
from typing import Callable, NewType, Union

Identifier = NewType("Identifier", str)
PrimaryKey = NewType("PrimaryKey", Mapping[str, Union[int, str, float]])


class DataJointTranslator:
    """Translator used to translate between DataJoint-specific primary keys and dommain-model-specific identifiers.

    Translations from identifier to primary key are only possible if the same primary key was previously translated into
    its corresponding identifier.
    """

    def __init__(self, to_identifier: Callable[[PrimaryKey], Identifier]) -> None:
        """Initialize the translator."""
        self._to_identifier = to_identifier
        self._reverse_translations: dict[Identifier, PrimaryKey] = {}

    def to_identifier(self, primary_key: PrimaryKey) -> Identifier:
        """Translate the identifier to its corresponding primary key."""
        identifier = self._to_identifier(primary_key)
        self._reverse_translations[identifier] = primary_key
        return identifier

    def to_primary_key(self, identifier: Identifier) -> PrimaryKey:
        """Translate the primary key into its corresponding identifier."""
        return self._reverse_translations[identifier]


def blake2b(primary_key: PrimaryKey) -> Identifier:
    """Convert the primary key into an identifier using the blake2b hashing algorithm."""
    return Identifier(hashlib.blake2b(json.dumps(primary_key, sort_keys=True).encode()).hexdigest())
