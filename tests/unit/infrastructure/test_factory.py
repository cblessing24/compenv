import pytest
from datajoint.user_tables import Lookup, Part

from compenv.adapters.abstract import PartEntity
from compenv.infrastructure.factory import DJTableFactory


@pytest.fixture
def factory(fake_schema, fake_parent):
    return DJTableFactory(fake_schema, parent=fake_parent.__name__)


@pytest.fixture
def produce_instance(factory):
    return factory()


@pytest.mark.usefixtures("produce_instance")
class TestMasterClass:
    @staticmethod
    def test_class_has_correct_name(fake_schema):
        assert "FakeParentRecord" in fake_schema.decorated_tables

    @staticmethod
    def test_class_is_lookup_table(fake_schema):
        assert issubclass(fake_schema.decorated_tables["FakeParentRecord"], Lookup)

    @staticmethod
    def test_class_has_correct_definition(fake_schema):
        assert fake_schema.decorated_tables["FakeParentRecord"].definition == "-> FakeParent"


@pytest.mark.parametrize("part", PartEntity.__subclasses__())
@pytest.mark.usefixtures("produce_instance")
class TestPartClasses:
    @staticmethod
    def test_part_classes_are_present_on_table_class(fake_schema, part):
        assert hasattr(fake_schema.decorated_tables["FakeParentRecord"], part.__name__)

    @staticmethod
    def test_part_classes_are_subclass_of_part_table(fake_schema, part):
        assert issubclass(getattr(fake_schema.decorated_tables["FakeParentRecord"], part.__name__), Part)

    @staticmethod
    def test_part_classes_have_correct_definitions(fake_schema, part):
        assert getattr(fake_schema.decorated_tables["FakeParentRecord"], part.__name__).definition == part.definition


def test_parent_is_added_to_context_when_schema_is_called(fake_schema, fake_parent):
    fake_schema.context = {"foo": "bar"}
    _ = DJTableFactory(fake_schema, parent=fake_parent.__name__)()
    assert fake_schema.context == {"foo": "bar", "FakeParent": fake_parent}


def test_if_instance_is_instance_of_class(produce_instance, fake_schema):
    assert isinstance(produce_instance, fake_schema.decorated_tables["FakeParentRecord"])


def test_instance_is_cached(factory):
    assert factory() is factory()


def test_repr(factory):
    assert repr(factory) == f"DJTableFactory(schema=FakeSchema(), parent='FakeParent')"
