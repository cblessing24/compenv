import pytest

from compenv.model.record import ComputationRecord, Distribution, Identifier
from compenv.service.diff import DiffRequest, DiffResponse, DiffService

from ..conftest import FakeOutputPort
from .conftest import FakeUnitOfWork


@pytest.mark.parametrize(
    "version1,version2,differ",
    [
        ("1.16.4", "1.16.4", False),
        ("1.16.4", "1.16.5", True),
    ],
)
def test_diff_behvaior_of_computation_records(
    version1: str, version2: str, differ: bool, fake_output_port: FakeOutputPort, fake_uow: FakeUnitOfWork
) -> None:
    rec1 = ComputationRecord(
        Identifier("identifier1"), distributions=frozenset((Distribution(name="numpy", version=version1),))
    )
    rec2 = ComputationRecord(
        Identifier("identifier2"), distributions=frozenset((Distribution(name="numpy", version=version2),))
    )
    fake_uow.records.add(rec1)
    fake_uow.records.add(rec2)

    diff = DiffService(output_port=fake_output_port, uow=fake_uow)
    request = DiffRequest(Identifier("identifier1"), Identifier("identifier2"))
    diff(request)
    assert fake_output_port.responses == [DiffResponse(differ=differ)]


def test_unit_of_work_is_committed(fake_output_port: FakeOutputPort, fake_uow: FakeUnitOfWork) -> None:
    rec1 = ComputationRecord(
        Identifier("identifier1"), distributions=frozenset((Distribution(name="numpy", version="0.1.2"),))
    )
    rec2 = ComputationRecord(
        Identifier("identifier2"), distributions=frozenset((Distribution(name="numpy", version="0.2.3"),))
    )
    fake_uow.records.add(rec1)
    fake_uow.records.add(rec2)

    diff = DiffService(output_port=fake_output_port, uow=fake_uow)
    request = DiffRequest(Identifier("identifier1"), Identifier("identifier2"))
    diff(request)
    assert fake_uow.committed
