import pytest
from utils import wait_for_status
from exceptions import AWSOperationError

class DummyRDS:
    def __init__(self, statuses):
        self.statuses = iter(statuses)
    def describe_db_instances(self, DBInstanceIdentifier):
        return {"DBInstances": [{"DBInstanceStatus": next(self.statuses)}]}

def test_wait_for_status_reaches_state():
    rds = DummyRDS(["creating", "available"])
    assert wait_for_status(rds, "demo", "available", poll_interval=0.01)

def test_wait_for_status_timeout():
    rds = DummyRDS(["creating"] * 3)
    with pytest.raises(AWSOperationError):
        wait_for_status(rds, "demo", "available", poll_interval=0.01, timeout=0.02)
