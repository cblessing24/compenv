from compenv.model.computation import Algorithm, AlgorithmName


def test_algorithm_has_name_attribute() -> None:
    assert Algorithm(AlgorithmName("myalgorithm")).name == AlgorithmName("myalgorithm")
