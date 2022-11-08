from compenv.model.computation import Algorithm, AlgorithmName, ArgumentsHash, Computation
from compenv.model.environment import Environment


def test_algorithm_has_name_attribute() -> None:
    assert Algorithm(AlgorithmName("myalgorithm")).name == AlgorithmName("myalgorithm")


def test_can_execute_algorithm() -> None:
    algorithm = Algorithm(AlgorithmName("myalgorithm"))
    environment = Environment(frozenset())
    algorithm.execute(environment, ArgumentsHash("myarguments"))
    assert list(algorithm.computations[environment]) == [
        Computation(AlgorithmName("myalgorithm"), ArgumentsHash("myarguments"), environment)
    ]
