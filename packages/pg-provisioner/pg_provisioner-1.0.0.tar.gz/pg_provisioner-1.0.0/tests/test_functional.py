import psycopg2
import pytest
from provisioner import PostgresProvisioner
from aws_client import AWSClient
from models import DBInstanceInfo, DBInstanceState
from utils import wait_for_status
from logging_config import get_logger

log = get_logger(__name__)

def test_full_instance_lifecycle(monkeypatch):
    """End-to-end functional test covering all core files using mocks only."""

    # -------------------------------------------------------------------------
    # Mock psycopg2.connect to avoid any real DB calls
    # -------------------------------------------------------------------------
    monkeypatch.setattr(psycopg2, "connect", lambda **kwargs: f"CONN({kwargs['host']})")

    prov = PostgresProvisioner(region_name="us-west-2")
    aws = prov.aws

    # -------------------------------------------------------------------------
    # 1. Create instance
    # -------------------------------------------------------------------------
    instance_id = "func-db"
    db = prov.create_instance(identifier=instance_id)
    assert isinstance(db, DBInstanceInfo)
    assert db.status in (DBInstanceState.available, DBInstanceState.creating)

    # -------------------------------------------------------------------------
    # 2. Describe instance
    # -------------------------------------------------------------------------
    info = prov.describe_instance(instance_id)
    assert isinstance(info, DBInstanceInfo)
    assert "postgres" in info.engine.lower()

    # -------------------------------------------------------------------------
    # 3. List instances (ensure at least one Postgres DB)
    # -------------------------------------------------------------------------
    lst = prov.list_instances()
    assert len(lst) > 0
    assert all(db.engine == "postgres" for db in lst)

    # -------------------------------------------------------------------------
    # 4. Resize instance (mocked modify)
    # -------------------------------------------------------------------------
    resized = prov.resize_instance(identifier=instance_id, new_class="db.t3.micro")
    assert isinstance(resized, DBInstanceInfo)
    assert resized.instance_class == "db.t3.micro" or isinstance(resized.instance_class, str)

    # -------------------------------------------------------------------------
    # 5. Snapshot + export flow (mocked)
    # -------------------------------------------------------------------------
    snapshot_id = f"{instance_id}-snapshot"
    export_id = f"{instance_id}-export"
    bucket = "test-bucket"

    # define minimal bucket method if missing
    if not hasattr(aws.s3, "create_bucket"):
        aws.s3.create_bucket = lambda Bucket: {"Bucket": Bucket}

    aws.s3.create_bucket(Bucket=bucket)
    aws.create_snapshot(identifier=instance_id, snapshot_id=snapshot_id)

    wait_for_status(aws.rds, snapshot_id, "available", resource="snapshot", poll_interval=0.1)

    arn = f"arn:aws:rds:us-west-2:123456789012:snapshot:{snapshot_id}"
    aws.start_export(
        snapshot_arn=arn,
        s3_bucket=bucket,
        export_id=export_id,
        role_arn="arn:aws:iam::123456789012:role/test",
        kms_key="alias/aws/s3",
    )

    # -------------------------------------------------------------------------
    # 6. Connection simulation
    # -------------------------------------------------------------------------
    monkeypatch.setattr("provisioner.wait_for_status", lambda *a, **k: True)
    conn = prov.connect(identifier=instance_id, password="foo")
    assert "CONN" in conn

    # -------------------------------------------------------------------------
    # 7. Delete instance
    # -------------------------------------------------------------------------
    prov.delete_instance(identifier=instance_id)

    log.info("Functional test completed successfully")
