import pytest


class FakeTable:
    @classmethod
    @property
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
            raise ValueError("Can't add already existing entity!")

        cls._data.append(entity)

    @classmethod
    def delete_quick(cls):
        for entity in cls._restricted_data:
            del cls._data[cls._data.index(entity)]

    @classmethod
    def fetch(cls, as_dict=False):
        if as_dict is not True:
            raise ValueError("'as_dict' must be set to 'True' when fetching!")
        return cls._restricted_data

    @classmethod
    def fetch1(cls):
        if len(cls._restricted_data) != 1:
            raise RuntimeError("Can't fetch zero or more than one entity!")

        return cls._restricted_data[0]

    @classmethod
    def __and__(cls, restriction):
        cls._check_attr_names(restriction)
        cls._restriction = restriction
        return cls

    @classmethod
    def __contains__(cls, item):
        return item in cls._restricted_data

    @classmethod
    def __eq__(cls, other):
        if not isinstance(other, list):
            raise TypeError(f"Expected other to be of type dict, got {type(other)}!")

        return all(e in cls._data for e in other)

    @classmethod
    def __len__(cls):
        return len(cls._restricted_data)

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
def fake_record_table():
    class FakeRecordTable(FakeTable):
        attrs = {"a": int, "b": int}

        class Module(FakeTable):
            attrs = {"a": int, "b": int, "module_file": str, "module_is_active": str}

        class InstalledDistribution(FakeTable):
            attrs = {"a": int, "b": int, "distribution_name": str, "distribution_version": str}

        class ModuleAffiliation(FakeTable):
            attrs = {"a": int, "b": int, "module_file": str, "distribution_name": str}

    return FakeRecordTable()
