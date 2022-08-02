import pytest

from compenv.adapters.translator import DJTranslator, blake2b
from compenv.model.computation import Identifier

from ..conftest import Primary


class TestDJTranslator:
    @staticmethod
    @pytest.fixture
    def translator() -> DJTranslator:
        def to_identifier(primary_key: Primary) -> Identifier:
            return Identifier("identifier")

        return DJTranslator(to_identifier)

    @staticmethod
    def test_translation_to_identifier(translator: DJTranslator, primary: Primary) -> None:
        assert translator.to_internal(primary) == "identifier"

    @staticmethod
    def test_translation_to_primary_key(translator: DJTranslator, primary: Primary) -> None:
        identifier = translator.to_internal(primary)
        assert translator.to_external(identifier) == primary

    @staticmethod
    def test_primary_key_cant_be_modified(translator: DJTranslator, primary: Primary) -> None:
        orig_primary = primary.copy()
        identifier = translator.to_internal(primary)
        primary["c"] = 10
        assert translator.to_external(identifier) == orig_primary


class TestBlake2b:
    @staticmethod
    def test_same_primary_key_produces_same_output(primary: Primary) -> None:
        assert blake2b(primary) == blake2b(primary)

    @staticmethod
    def test_different_primary_key_produces_different_output(primary: Primary) -> None:
        other_primary_key: Primary = {"a": 0, "b": 2}
        assert blake2b(primary) != blake2b(other_primary_key)

    @staticmethod
    def test_order_invariant(primary: Primary) -> None:
        different_order_primary_key: Primary = {"b": 1, "a": 0}
        assert blake2b(primary) == blake2b(different_order_primary_key)
