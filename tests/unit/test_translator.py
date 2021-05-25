import pytest

from repro.translator import DataJointTranslator, blake2b


class TestDataJointTranslator:
    @pytest.fixture
    def translator(self):
        def to_identifier(primary_key):
            return "identifier"

        return DataJointTranslator(to_identifier)

    def test_translation_to_identifier(self, translator):
        assert translator.to_identifier("primary_key") == "identifier"

    def test_translation_to_primary_key(self, translator):
        identifier = translator.to_identifier("primary_key")
        assert translator.to_primary_key(identifier) == "primary_key"


class TestBlake2b:
    @pytest.fixture
    def primary_key(self):
        return {"a": 0, "b": 1}

    def test_same_primary_key_produces_same_output(self, primary_key):
        assert blake2b(primary_key) == blake2b(primary_key)

    def test_different_primary_key_produces_different_output(self, primary_key):
        other_primary_key = {"a": 0, "b": 2}
        assert blake2b(primary_key) != blake2b(other_primary_key)

    def test_order_invariant(self, primary_key):
        different_order_primary_key = {"b": 1, "a": 0}
        assert blake2b(primary_key) == blake2b(different_order_primary_key)
