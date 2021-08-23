import pytest
from datajoint.user_tables import Lookup, Part

from repro.adapters.abstract import DJPartEntity
from repro.infrastructure.factory import RecordTableFactory


@pytest.fixture
def fake_schema():
    class FakeSchema:
        def __init__(self):
            self.table_cls = None

        def __call__(self, cls):
            self.table_cls = cls
            return cls

        def __repr__(self):
            return "FakeSchema()"

    return FakeSchema()


@pytest.fixture
def factory(fake_schema):
    return RecordTableFactory(fake_schema, parent="Parent")


@pytest.fixture
def produce_instance(factory):
    return factory()


@pytest.mark.usefixtures("produce_instance")
class TestMasterClass:
    @staticmethod
    def test_class_has_correct_name(fake_schema):
        assert fake_schema.table_cls.__name__ == "Record"

    @staticmethod
    def test_class_is_lookup_table(fake_schema):
        assert issubclass(fake_schema.table_cls, Lookup)

    @staticmethod
    def test_class_has_correct_definition(fake_schema):
        assert fake_schema.table_cls.definition == "-> Parent"


@pytest.mark.parametrize("part", DJPartEntity.__subclasses__())
@pytest.mark.usefixtures("produce_instance")
class TestPartClasses:
    @staticmethod
    def test_part_classes_are_present_on_table_class(fake_schema, part):
        assert hasattr(fake_schema.table_cls, part.__name__)

    @staticmethod
    def test_part_classes_are_subclass_of_part_table(fake_schema, part):
        assert issubclass(getattr(fake_schema.table_cls, part.__name__), Part)

    @staticmethod
    def test_part_classes_have_correct_definitions(fake_schema, part):
        assert getattr(fake_schema.table_cls, part.__name__).definition == "-> master\n" + part.definition


def test_if_instance_is_instance_of_class(produce_instance, fake_schema):
    assert isinstance(produce_instance, fake_schema.table_cls)


def test_instance_is_cached(factory):
    assert factory() is factory()


def test_repr(factory):
    assert repr(factory) == "RecordTableFactory(schema=FakeSchema(), parent='Parent')"
