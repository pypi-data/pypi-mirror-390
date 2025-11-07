import pytest
from aws_client import AWSClient
from exceptions import AWSOperationError

def test_aws_client_instantiation():
    c = AWSClient(region_name="us-west-2")
    assert c.region == "us-west-2"

def test_create_and_describe(monkeypatch):
    c = AWSClient(region_name="us-west-2")
    monkeypatch.setattr(c.rds, "create_db_instance", lambda **k: {"ok": True})
    resp = c.create_instance(DBInstanceIdentifier="demo")
    assert "ok" in resp

def test_retry_and_error(monkeypatch):
    c = AWSClient(region_name="us-west-2")

    class Dummy:
        def __call__(self, **_): raise Exception("boom")

    with pytest.raises(AWSOperationError):
        c._retry(Dummy(), operation="test")
