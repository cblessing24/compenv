from __future__ import annotations

import os
from typing import Callable, Dict, Iterable, Iterator, List, Literal, Optional, Union

import pytest

from compenv.adapters.distribution import DistributionConverter
from compenv.model.record import Distribution, Distributions


class FakePackagePath:
    def __init__(self, path: Union[str, os.PathLike[str]]) -> None:
        """Fake version of importlib.metadata.PackagePath."""

        self.path = os.fspath(path)
        self.suffix = "." + self.path.split(".")[-1]

    def locate(self) -> FakePackagePath:
        return self

    def __fspath__(self) -> str:
        return self.path

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.path})"


class FakePath(FakePackagePath):
    """Fake version of pathlib.Path."""

    _not_existing_paths = {"/dist1/tests/module1.py", "/dist2/tests/module1.py"}

    def exists(self) -> bool:
        return self.path not in self._not_existing_paths

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FakePackagePath):
            raise TypeError()
        return self.path == other.path

    def __hash__(self) -> int:
        return hash(self.path)


class FakeMetadata:
    """Fake version of importlib.metadata.Distribution.metadata."""

    def __init__(self, name: str, version: str) -> None:
        self._metadata = {"Name": name, "Version": version}

    def __getitem__(self, item: Literal["Name", "Version"]) -> str:
        return self._metadata[item]


class FakeDistribution:
    """Fake version of importlib.metadata.Distribution."""

    def __init__(self, metadata: FakeMetadata, files: Optional[List[FakePackagePath]]) -> None:
        self._metadata = metadata
        self._files = files

    @property
    def metadata(self) -> FakeMetadata:
        return self._metadata

    @property
    def files(self) -> Optional[List[FakePackagePath]]:
        return self._files


@pytest.fixture
def fake_metadata() -> Dict[str, FakeMetadata]:
    return {
        "dist1": FakeMetadata("dist1", "0.1.0"),
        "dist2": FakeMetadata("dist2", "0.1.2"),
        "dist3": FakeMetadata("dist3", "1.2.3"),
    }


@pytest.fixture
def fake_distribution_files() -> Dict[str, Optional[List[FakePackagePath]]]:
    return {
        "dist1": [
            FakePackagePath("/dist1/package1/module1.py"),
            FakePackagePath("/dist1/README.md"),
            FakePackagePath("/dist1/package1/__init__.py"),
            FakePackagePath("/dist1/tests/module1.py"),
        ],
        "dist2": [
            FakePackagePath("/dist2/tests/module1.py"),
            FakePackagePath("/dist2/requirements.txt"),
            FakePackagePath("/dist2/package1/__init__.py"),
            FakePackagePath("/dist2/package1/module1.py"),
        ],
        "dist3": None,
    }


@pytest.fixture
def fake_distributions(
    fake_metadata: Dict[str, FakeMetadata],
    fake_distribution_files: Dict[str, Optional[List[FakePackagePath]]],
) -> List[FakeDistribution]:
    return [FakeDistribution(m, fake_distribution_files[n]) for n, m in fake_metadata.items()]


@pytest.fixture
def fake_get_distributions(
    fake_distributions: List[FakeDistribution],
) -> Callable[[], Iterator[FakeDistribution]]:
    def _fake_get_distributions() -> Iterator[FakeDistribution]:
        return iter(fake_distributions)

    return _fake_get_distributions


@pytest.fixture
def converter(
    fake_get_distributions: Callable[[], Iterable[FakeDistribution]],
) -> DistributionConverter:
    return DistributionConverter(
        path_cls=FakePath,
        get_distributions=fake_get_distributions,
    )


def test_correct_distributions_returned(converter: DistributionConverter) -> None:
    expected_distributions = Distributions(
        {Distribution("dist1", "0.1.0"), Distribution("dist2", "0.1.2"), Distribution("dist3", "1.2.3")}
    )
    actual_distributions = converter()
    assert actual_distributions == expected_distributions


def test_repr(converter: DistributionConverter) -> None:
    assert repr(converter) == "DistributionConverter()"
