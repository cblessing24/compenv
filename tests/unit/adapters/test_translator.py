import pytest

from repro.adapters.translator import DJTranslator, blake2b


class TestDataJointTranslator:
    @staticmethod
    @pytest.fixture
    def translator():
        def to_identifier(primary_key):
            return "identifier"

        return DJTranslator(to_identifier)

    @staticmethod
    def test_translation_to_identifier(translator):
        assert translator.to_identifier("primary_key") == "identifier"

    @staticmethod
    def test_translation_to_primary_key(translator):
        identifier = translator.to_identifier("primary_key")
        assert translator.to_primary(identifier) == "primary_key"


class TestBlake2b:
    @staticmethod
    @pytest.fixture
    def primary_key():
        return {"a": 0, "b": 1}

    @staticmethod
    def test_same_primary_key_produces_same_output(primary_key):
        assert blake2b(primary_key) == blake2b(primary_key)

    @staticmethod
    def test_different_primary_key_produces_different_output(primary_key):
        other_primary_key = {"a": 0, "b": 2}
        assert blake2b(primary_key) != blake2b(other_primary_key)

    @staticmethod
    def test_order_invariant(primary_key):
        different_order_primary_key = {"b": 1, "a": 0}
        assert blake2b(primary_key) == blake2b(different_order_primary_key)
