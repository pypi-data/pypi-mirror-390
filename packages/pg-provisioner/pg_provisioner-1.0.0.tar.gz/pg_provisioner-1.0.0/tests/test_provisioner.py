import pytest
import psycopg2
from provisioner import PostgresProvisioner
from exceptions import (
    ProvisioningError, ResizeError, DeletionError,
    ConnectionNotReady, ConnectionErrorPG, InvalidCredentialsError
)
from models import DBInstanceState


def test_create_instance(monkeypatch):
    p = PostgresProvisioner(region_name="us-west-2")
    monkeypatch.setattr(p.aws, "create_instance", lambda **_: {"ok": True})
    mock_db = type("Obj", (), {
        "endpoint": "x",
        "status": DBInstanceState.creating
    })
    monkeypatch.setattr(p, "describe_instance", lambda i: mock_db)
    monkeypatch.setattr("src.utils.wait_for_status", lambda *a, **k: True)
    result = p.create_instance("demo")
    assert result.endpoint == "x"
    assert result.status == DBInstanceState.creating


def test_resize_and_delete(monkeypatch):
    p = PostgresProvisioner(region_name="us-west-2")

    # Patch AWS interactions
    monkeypatch.setattr(p.aws, "modify_instance", lambda *a, **k: None)
    monkeypatch.setattr(p, "describe_instance", lambda i: type("Obj", (), {
        "instance_class": "db.t3.micro",
        "allocated_storage": 10
    }))

    # The important one:
    monkeypatch.setattr("provisioner.wait_for_status", lambda *a, **k: True)

    p.resize_instance("demo")

    # Test delete flow
    monkeypatch.setattr(p.aws, "delete_instance", lambda i, skip_snapshot=True: None)
    p.delete_instance("demo")


def test_connection_not_ready(monkeypatch):
    p = PostgresProvisioner(region_name="us-west-2")
    info = type("Obj", (), {
        "status": DBInstanceState.creating,
        "identifier": "demo"
    })
    monkeypatch.setattr(p, "describe_instance", lambda i: info)
    with pytest.raises(ConnectionNotReady):
        p.get_connection_info("demo", "pass")


def test_connection_success(monkeypatch):
    p = PostgresProvisioner(region_name="us-west-2")
    fake_info = type("Info", (), {
        "status": DBInstanceState.available,
        "identifier": "x",
        "endpoint": "h",
        "port": 5432,
        "db_name": "d",
        "master_user": "u",
        "is_available": staticmethod(lambda: True),
    })
    monkeypatch.setattr(p, "describe_instance", lambda i: fake_info)
    monkeypatch.setattr(psycopg2, "connect", lambda **k: "CONN")
    assert p.connect("demo", "pw") == "CONN"


def test_connection_fails(monkeypatch):
    p = PostgresProvisioner(region_name="us-west-2")
    info = type("Info", (), {
        "status": DBInstanceState.available,
        "identifier": "x",
        "endpoint": "h",
        "port": 5432,
        "db_name": "d",
        "master_user": "u",
        "is_available": staticmethod(lambda: True),
    })
    monkeypatch.setattr(p, "describe_instance", lambda i: info)
    monkeypatch.setattr(
        psycopg2,
        "connect",
        lambda **k: (_ for _ in ()).throw(psycopg2.OperationalError("password")),
    )

    # Expect InvalidCredentialsError instead of ConnectionErrorPG
    with pytest.raises(InvalidCredentialsError):
        p.connect("demo", "pw")
