from compenv.model.computation import Algorithm, AlgorithmName, ArgumentsHash, Computation
from compenv.model.environment import Environment


def test_executing_algorithm_records_computation() -> None:
    algorithm = Algorithm(AlgorithmName("myalgorithm"))
    environment = Environment(frozenset())
    algorithm.execute(environment, ArgumentsHash("myarguments"))
    assert algorithm[environment] == frozenset(
        [Computation(AlgorithmName("myalgorithm"), ArgumentsHash("myarguments"), environment)]
    )


def test_algorithm_has_name_attribute() -> None:
    assert Algorithm(AlgorithmName("myalgorithm")).name == AlgorithmName("myalgorithm")


def test_can_instantiate_with_computations() -> None:
    environment = Environment(frozenset())
    computation = Computation(AlgorithmName("myalgorithm"), ArgumentsHash("myarguments"), environment)
    algorithm = Algorithm(
        AlgorithmName("myalgorithm"),
        computations={environment: [computation]},
    )
    assert algorithm[environment] == frozenset([computation])
