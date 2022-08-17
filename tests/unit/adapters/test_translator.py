import pytest

from compenv.adapters.translator import DJTranslator, blake2b
from compenv.model.record import Identifier
from compenv.types import PrimaryKey


class TestDJTranslator:
    @staticmethod
    @pytest.fixture
    def translator() -> DJTranslator:
        def to_identifier(primary_key: PrimaryKey) -> Identifier:
            return Identifier("identifier")

        return DJTranslator(to_identifier)

    @staticmethod
    def test_translation_to_identifier(translator: DJTranslator, primary: PrimaryKey) -> None:
        assert translator.to_internal(primary) == "identifier"

    @staticmethod
    def test_translation_to_primary_key(translator: DJTranslator, primary: PrimaryKey) -> None:
        identifier = translator.to_internal(primary)
        assert translator.to_external(identifier) == primary

    @staticmethod
    def test_primary_key_cant_be_modified(translator: DJTranslator, primary: PrimaryKey) -> None:
        primary = dict(primary)
        orig_primary = primary.copy()
        identifier = translator.to_internal(primary)
        primary["c"] = 10
        assert translator.to_external(identifier) == orig_primary


class TestBlake2b:
    @staticmethod
    def test_same_primary_key_produces_same_output(primary: PrimaryKey) -> None:
        assert blake2b(primary) == blake2b(primary)

    @staticmethod
    def test_different_primary_key_produces_different_output(primary: PrimaryKey) -> None:
        other_primary_key: PrimaryKey = {"a": 0, "b": 2}
        assert blake2b(primary) != blake2b(other_primary_key)

    @staticmethod
    def test_order_invariant(primary: PrimaryKey) -> None:
        different_order_primary_key: PrimaryKey = {"b": 1, "a": 0}
        assert blake2b(primary) == blake2b(different_order_primary_key)
