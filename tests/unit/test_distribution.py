import pytest

from repro.distribution import InstalledDistributionConverter
from repro.model import Distribution


class FakePath:
    def __init__(self, path):
        self.path = path

    def locate(self):
        return FakeAbsolutePath(self.path)

    def __str__(self):
        raise RuntimeError("Path should be made absolute before converting to string")


class FakeAbsolutePath(FakePath):
    def __str__(self):
        return self.path


class FakeImportlibMetadataDistribution:
    def __init__(self, metadata, files):
        self.metadata = metadata
        self.files = files


@pytest.fixture
def fake_distribution_metadata():
    return {"foo": {"Name": "foo", "Version": "0.1.0"}, "bar": {"Name": "bar", "Version": "0.1.2"}}


@pytest.fixture
def fake_distribution_files():
    return {"foo": [FakePath("/foo/module1.py"), FakePath("/foo/module2.py")], "bar": [FakePath("/bar/module.py")]}


@pytest.fixture
def fake_distributions(fake_distribution_metadata, fake_distribution_files):
    return [
        FakeImportlibMetadataDistribution(m, fake_distribution_files[n]) for n, m in fake_distribution_metadata.items()
    ]


@pytest.fixture
def fake_get_installed_distributions_func(fake_distributions):
    def _fake_get_installed_distributions_func():
        return iter(fake_distributions)

    return _fake_get_installed_distributions_func


@pytest.fixture
def converter(fake_get_installed_distributions_func):
    InstalledDistributionConverter._get_installed_distributions_func = staticmethod(
        fake_get_installed_distributions_func
    )
    return InstalledDistributionConverter()


def test_correct_distributions_returned(converter):
    expected_distributions = {
        "foo": Distribution("foo", "0.1.0", {"/foo/module1.py", "/foo/module2.py"}),
        "bar": Distribution("bar", "0.1.2", {"/bar/module.py"}),
    }
    actual_distributions = converter()
    assert actual_distributions == expected_distributions


def test_repr(converter):
    assert repr(converter) == "InstalledDistributionConverter()"
