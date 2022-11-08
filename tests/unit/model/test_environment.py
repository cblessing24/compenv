from compenv.model.environment import Environment


def test_identical_environments_have_identical_hashes() -> None:
    assert hash(Environment(frozenset())) == hash(Environment(frozenset()))
