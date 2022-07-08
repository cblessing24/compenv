import pytest

from compenv.model.environment import Environment


@pytest.mark.usefixtures("prepare_environment")
class TestEnvironment:
    @staticmethod
    @pytest.fixture
    def environment():
        return Environment()

    @staticmethod
    def test_correct_record_is_recorded(environment, record):
        assert environment.record() == record

    @staticmethod
    @pytest.mark.parametrize("attr", ["success", "record"])
    def test_consistency_check_attributes_can_not_be_accessed_in_with_block(environment, attr):
        with pytest.raises(RuntimeError, match=f"Can not access '{attr}'"):
            with environment.consistency_check() as check:
                getattr(check, attr)

    @staticmethod
    def test_consistency_check_repr(environment):
        with environment.consistency_check() as check:
            assert repr(check) == "_ConsistencyCheck(environment=Environment())"

    @staticmethod
    def test_repr(environment):
        assert repr(environment) == "Environment()"
