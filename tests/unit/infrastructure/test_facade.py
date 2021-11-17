import dataclasses

import pytest
from datajoint.errors import DuplicateError

from compenv.adapters.repository import DJComputationRecord
from compenv.infrastructure.facade import DJTableFacade


class FakeTable:
    @classmethod
    def _restricted_data(cls):
        if not cls._restriction:
            return cls._data
        return [d for d in cls._data if all(i in d.items() for i in cls._restriction.items())]

    @classmethod
    def insert(cls, entities):
        for entity in entities:
            cls.insert1(entity)

    @classmethod
    def insert1(cls, entity):
        cls._check_attr_names(entity)

        for attr_name, attr_value in entity.items():
            if not isinstance(attr_value, cls.attrs[attr_name]):
                raise ValueError(
                    f"Expected instance of type '{cls.attrs[attr_name]}' "
                    f"for attribute with name {attr_name}, got '{type(attr_value)}'!"
                )

        if entity in cls._data:
            raise DuplicateError

        cls._data.append(entity)

    @classmethod
    def delete_quick(cls):
        for entity in cls._restricted_data():
            del cls._data[cls._data.index(entity)]

    @classmethod
    def fetch(cls, as_dict=False):
        if as_dict is not True:
            raise ValueError("'as_dict' must be set to 'True' when fetching!")
        return cls._restricted_data()

    @classmethod
    def fetch1(cls):
        if len(cls._restricted_data()) != 1:
            raise RuntimeError("Can't fetch zero or more than one entity!")

        return cls._restricted_data()[0]

    @classmethod
    def __and__(cls, restriction):
        cls._check_attr_names(restriction)
        cls._restriction = restriction
        return cls

    @classmethod
    def __contains__(cls, item):
        return item in cls._restricted_data()

    @classmethod
    def __eq__(cls, other):
        if not isinstance(other, list):
            raise TypeError(f"Expected other to be of type dict, got {type(other)}!")

        return all(e in cls._data for e in other)

    @classmethod
    def __iter__(cls):
        return iter(cls._restricted_data())

    @classmethod
    def __len__(cls):
        return len(cls._restricted_data())

    @classmethod
    def __repr__(cls):
        return f"{cls.__name__}()"

    def __init_subclass__(cls):
        cls._data = []
        cls._restriction = {}

    @classmethod
    def _check_attr_names(cls, attr_names):
        for attr_name in attr_names:
            if attr_name not in cls.attrs:
                raise ValueError(f"Table doesn't have attribute with name '{attr_name}'!")


@pytest.fixture
def fake_tbl():
    class FakeRecordTable(FakeTable):
        attrs = {"a": int, "b": int}

        class Module(FakeTable):
            attrs = {"a": int, "b": int, "module_file": str, "module_is_active": str}

        class Distribution(FakeTable):
            attrs = {"a": int, "b": int, "distribution_name": str, "distribution_version": str}

        class Membership(FakeTable):
            attrs = {"a": int, "b": int, "module_file": str, "distribution_name": str, "distribution_version": str}

    return FakeRecordTable()


@pytest.fixture
def fake_factory(fake_tbl):
    class FakeFactory:
        def __call__(self):
            return fake_tbl

        def __repr__(self):
            return self.__class__.__name__ + "()"

    return FakeFactory()


@pytest.fixture
def facade(fake_factory):
    return DJTableFacade(fake_factory)


class TestInsert:
    @staticmethod
    def test_raises_error_if_record_already_exists(facade, primary, dj_comp_rec):
        facade[primary] = dj_comp_rec
        with pytest.raises(ValueError, match="already exists!"):
            facade[primary] = dj_comp_rec

    @staticmethod
    def test_inserts_master_entity_into_master_table(facade, primary, dj_comp_rec, fake_tbl):
        facade[primary] = dj_comp_rec
        assert fake_tbl.fetch1() == primary

    @staticmethod
    @pytest.mark.parametrize("part,attr", list((p.__name__, p.master_attr) for p in DJComputationRecord.parts))
    def test_inserts_part_entities_into_part_tables(facade, primary, dj_comp_rec, fake_tbl, part, attr):
        facade[primary] = dj_comp_rec
        assert getattr(fake_tbl, part).fetch(as_dict=True) == [
            {**primary, **dataclasses.asdict(m)} for m in getattr(dj_comp_rec, attr)
        ]


@pytest.mark.parametrize("method", ["__delitem__", "__getitem__"])
def test_raises_error_if_record_does_not_exist(facade, primary, method):
    with pytest.raises(KeyError, match="does not exist!"):
        getattr(facade, method)(primary)


class TestDelete:
    @staticmethod
    @pytest.mark.parametrize("part", list(DJComputationRecord.parts))
    def test_deletes_part_entities_from_part_tables(facade, primary, dj_comp_rec, fake_tbl, part):
        facade[primary] = dj_comp_rec
        del facade[primary]
        assert len(getattr(fake_tbl, part.__name__)()) == 0

    @staticmethod
    def test_deletes_master_entity_from_master_table(facade, primary, dj_comp_rec, fake_tbl):
        facade[primary] = dj_comp_rec
        del facade[primary]
        assert len(fake_tbl) == 0


def test_fetches_dj_computation_record(facade, primary, dj_comp_rec):
    facade[primary] = dj_comp_rec
    assert facade[primary] == dj_comp_rec


def test_length(facade, primary, dj_comp_rec):
    facade[primary] = dj_comp_rec
    assert len(facade) == 1


def test_iteration(facade, primary, dj_comp_rec, fake_tbl):
    facade[primary] = dj_comp_rec
    assert list(iter(facade)) == list(iter(fake_tbl))


def test_repr(facade):
    assert repr(facade) == "DJTableFacade(factory=FakeFactory())"
