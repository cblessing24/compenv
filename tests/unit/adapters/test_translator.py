import pytest

from compenv.adapters.translator import DJTranslator, blake2b


class TestDJTranslator:
    @staticmethod
    @pytest.fixture
    def translator():
        def to_identifier(primary_key):
            return "identifier"

        return DJTranslator(to_identifier)

    @staticmethod
    def test_translation_to_identifier(translator, primary):
        assert translator.to_identifier(primary) == "identifier"

    @staticmethod
    def test_translation_to_primary_key(translator, primary):
        identifier = translator.to_identifier(primary)
        assert translator.to_primary(identifier) == primary

    @staticmethod
    def test_primary_key_cant_be_modified(translator, primary):
        orig_primary = primary.copy()
        identifier = translator.to_identifier(primary)
        primary["c"] = 10
        assert translator.to_primary(identifier) == orig_primary


class TestBlake2b:
    @staticmethod
    def test_same_primary_key_produces_same_output(primary):
        assert blake2b(primary) == blake2b(primary)

    @staticmethod
    def test_different_primary_key_produces_different_output(primary):
        other_primary_key = {"a": 0, "b": 2}
        assert blake2b(primary) != blake2b(other_primary_key)

    @staticmethod
    def test_order_invariant(primary):
        different_order_primary_key = {"b": 1, "a": 0}
        assert blake2b(primary) == blake2b(different_order_primary_key)
