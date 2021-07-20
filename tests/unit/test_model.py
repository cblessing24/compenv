import textwrap
from collections.abc import Set
from pathlib import Path

import pytest

from repro import model
from repro.model import Computation, ComputationRecord, Distribution, Environment, Module, Record


class TestModule:
    @staticmethod
    def test_file_attribute_is_immutable():
        module = Module(Path("module.py"))
        with pytest.raises(AttributeError):
            module.file = Path("other_file.py")

    @staticmethod
    def test_module_is_not_equal_to_non_module_object():
        module = Module(Path("module.py"))
        other = object()
        assert (module == other) is False

    @staticmethod
    def test_modules_are_equal_if_their_files_are_equal():
        module1, module2 = (Module(Path("module.py")) for _ in range(2))
        assert (module1 == module2) is True

    @staticmethod
    def test_modules_are_not_equal_if_their_files_are_not_equal():
        module1 = Module(Path("module.py"))
        module2 = Module(Path("other_module.py"))
        assert (module1 == module2) is False

    @staticmethod
    def test_modules_have_same_hash_if_their_files_are_equal():
        module1, module2 = (Module(Path("module.py")) for _ in range(2))
        assert (hash(module1) == hash(module2)) is True

    @staticmethod
    def test_modules_have_different_hashes_if_their_files_are_not_equal():
        module1 = Module(Path("module.py"))
        module2 = Module(Path("other_module.py"))
        assert (hash(module1) == hash(module2)) is False

    @staticmethod
    def test_repr():
        file = Path("module.py")
        module = Module(file)
        assert repr(module) == f"Module(file={repr(file)})"


class TestDistribution:
    @staticmethod
    def test_name_attribute_is_immutable():
        dist = Distribution("dist", "0.1.0")
        with pytest.raises(AttributeError):
            dist.name = "other_dist"

    @staticmethod
    def test_version_attribute_is_immutable():
        dist = Distribution("dist", "0.1.0")
        with pytest.raises(AttributeError):
            dist.version = "0.1.2"

    @staticmethod
    def test_modules_attribute_is_immutable():
        dist = Distribution("dist", "0.1.0")
        with pytest.raises(AttributeError):
            dist.modules = {}

    @staticmethod
    def test_module_in_distribution_if_module_in_modules():
        module = Module(Path("module.py"))
        dist = Distribution("dist", "0.1.0", modules=frozenset((module,)))
        assert (module in dist) is True

    @staticmethod
    def test_module_not_in_distribution_if_module_not_in_modules():
        module = Module(Path("module.py"))
        dist = Distribution("dist", "0.1.0")
        assert (module in dist) is False

    @staticmethod
    def test_iterating_distribution_iterates_modules():
        modules = frozenset(Module(Path("module" + str(i) + ".py")) for i in range(5))
        dist = Distribution("dist", "0.1.0", modules=modules)
        assert frozenset(dist) == modules

    @staticmethod
    def test_length_of_distribution_is_equal_to_length_of_modules():
        modules = frozenset(Module(Path("module" + str(i) + ".py")) for i in range(5))
        dist = Distribution("dist", "0.1.0", modules=modules)
        assert len(dist) == len(modules)

    @staticmethod
    def test_distribution_is_instance_of_set_class():
        dist = Distribution("dist", "0.1.0")
        assert isinstance(dist, Set)

    @staticmethod
    def test_str():
        modules = frozenset(Module(Path("module" + str(i) + ".py")) for i in range(5))
        dist = Distribution("dist", "0.1.0", modules=modules)
        expected = textwrap.dedent(
            """
            Distribution:
                name: dist
                version: 0.1.0
                modules:
                    module0.py
                    module1.py
                    module2.py
                    module3.py
                    module4.py
            """
        ).strip()
        assert str(dist) == expected

    @staticmethod
    @pytest.mark.parametrize("method", ["__and__", "__or__", "__sub__", "__xor__"])
    def test_set_methods_produce_expected_result(method):
        modules1 = frozenset(Module(Path("module" + str(i) + ".py")) for i in [1, 2, 3])
        modules2 = frozenset(Module(Path("module" + str(i) + ".py")) for i in [4, 5, 6])
        dist1 = Distribution("dist1", "0.1.0", modules=modules1)
        dist2 = Distribution("dist2", "0.1.0", modules=modules2)
        assert getattr(dist1, method)(dist2) == getattr(modules1, method)(modules2)


@pytest.fixture
def installed_distributions():
    return frozenset(
        {
            Distribution("dist1", "0.1.0", modules=frozenset({Module("module1.py")})),
            Distribution("dist2", "0.1.1", modules=frozenset({Module("module2.py")})),
        }
    )


@pytest.fixture
def active_modules():
    return frozenset({Module("module2.py")})


@pytest.fixture
def active_distributions():
    return frozenset({Distribution("dist2", "0.1.1", modules=frozenset({Module("module2.py")}))})


@pytest.fixture
def record(installed_distributions, active_modules, active_distributions):
    return Record(
        installed_distributions=installed_distributions,
        active_distributions=active_distributions,
        active_modules=active_modules,
    )


class TestComputationRecord:
    @staticmethod
    @pytest.fixture
    def computation_record(record):
        return ComputationRecord("identifier", record)

    @staticmethod
    @pytest.mark.parametrize("attr", ["identifier", "record"])
    def test_attributes_are_immutable(computation_record, attr):
        with pytest.raises(AttributeError):
            setattr(computation_record, attr, "another_value")


@pytest.fixture
def environment(installed_distributions, active_modules):
    def fake_get_active_modules():
        return iter(active_modules)

    def fake_get_installed_distributions():
        return iter(installed_distributions)

    model.get_active_modules = fake_get_active_modules
    model.get_installed_distributions = fake_get_installed_distributions
    return Environment()


class TestComputation:
    @staticmethod
    @pytest.fixture
    def fake_trigger():
        class FakeTrigger:
            triggered = False
            change_environment = False

            def __call__(self):
                if self.change_environment:
                    self._change_environment()
                self.triggered = True

            def _change_environment(self):
                def fake_get_active_modules():
                    return iter(frozenset())

                model.get_active_modules = fake_get_active_modules

            def __repr__(self):
                return f"{self.__class__.__name__}()"

        return FakeTrigger()

    @staticmethod
    @pytest.fixture
    def computation(environment, fake_trigger):
        return Computation("identifier", environment, trigger=fake_trigger)

    @staticmethod
    def test_computation_record_gets_returned_when_computation_gets_executed(computation, record):
        assert computation.execute() == ComputationRecord("identifier", record)

    @staticmethod
    def test_trigger_gets_triggered_when_computation_gets_executed(computation, fake_trigger):
        computation.execute()
        assert fake_trigger.triggered

    @staticmethod
    def test_computation_can_not_be_executed_more_than_once(computation):
        computation.execute()
        with pytest.raises(RuntimeError, match="Computation already executed!"):
            computation.execute()

    @staticmethod
    def test_computation_raises_warning_if_environment_changes_during_computation(computation, fake_trigger):
        fake_trigger.change_environment = True
        with pytest.warns(UserWarning, match="Environment changed during execution!"):
            computation.execute()

    @staticmethod
    def test_computation_raises_no_warning_if_environment_does_not_change_during_computation(computation):
        with pytest.warns(None) as record:
            computation.execute()
            assert not record

    @staticmethod
    def test_repr(computation):
        assert (
            repr(computation)
            == f"Computation(identifier='identifier', environment=Environment(), trigger=FakeTrigger())"
        )


class TestEnvironment:
    @staticmethod
    def test_correct_record_is_recorded(environment, record):
        assert environment.record() == record

    @staticmethod
    def test_repr(environment):
        assert repr(environment) == "Environment()"


class TestRecord:
    @staticmethod
    @pytest.mark.parametrize("attr", ["installed_distributions", "active_distributions", "active_modules"])
    def test_attributes_are_read_only(record, attr):
        with pytest.raises(AttributeError):
            setattr(record, attr, "something")

    @staticmethod
    def test_str(record):
        expected = textwrap.dedent(
            """
            Record:
                installed distributions:
                    dist1 (0.1.0)
                    dist2 (0.1.1)
                active distributions:
                    dist2 (0.1.1)
                active modules:
                    module2.py
            """
        ).strip()
        assert str(record) == expected
