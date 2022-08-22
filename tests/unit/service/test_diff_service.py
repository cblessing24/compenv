from compenv.model.record import ComputationRecord, Distribution, Identifier
from compenv.service.diff import DiffRequest, DiffResponse, DiffService

from ..conftest import FakeOutputPort, FakeRepository


def test_computation_records_with_identical_distributions_do_not_differ(
    fake_output_port: FakeOutputPort, fake_repository: FakeRepository
) -> None:
    rec1 = ComputationRecord(
        Identifier("identifier1"), distributions=frozenset((Distribution(name="numpy", version="1.16.4"),))
    )
    rec2 = ComputationRecord(
        Identifier("identifier2"), distributions=frozenset((Distribution(name="numpy", version="1.16.4"),))
    )
    fake_repository.add(rec1)
    fake_repository.add(rec2)

    diff = DiffService(output_port=fake_output_port, repo=fake_repository)
    request = DiffRequest(Identifier("identifier1"), Identifier("identifier2"))
    diff(request)
    assert fake_output_port.responses == [DiffResponse(differ=False)]


def test_computation_records_with_different_distributions_do_differ(
    fake_output_port: FakeOutputPort, fake_repository: FakeRepository
) -> None:
    rec1 = ComputationRecord(
        Identifier("identifier1"), distributions=frozenset((Distribution(name="numpy", version="1.16.4"),))
    )
    rec2 = ComputationRecord(
        Identifier("identifier2"), distributions=frozenset((Distribution(name="numpy", version="1.16.5"),))
    )
    fake_repository.add(rec1)
    fake_repository.add(rec2)

    diff = DiffService(output_port=fake_output_port, repo=fake_repository)
    request = DiffRequest(Identifier("identifier1"), Identifier("identifier2"))
    diff(request)
    assert fake_output_port.responses == [DiffResponse(differ=True)]
