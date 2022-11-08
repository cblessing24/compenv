"""Contains model objects related to computation."""
from dataclasses import dataclass
from typing import NewType

AlgorithmName = NewType("AlgorithmName", str)
ArgumentsHash = NewType("ArgumentsHash", str)
EnvironmentHash = NewType("EnvironmentHash", str)


@dataclass(frozen=True)
class Computation:
    """The execution of a particular algorithm on a particular set of arguments in a particular environment."""

    algorithm: AlgorithmName
    arguments: ArgumentsHash
    environment: EnvironmentHash
