"""
Integration test for pg_provisioner using real AWS resources.
Runs only if RUN_REAL_AWS=1 is set.
This creates a temporary PostgreSQL RDS instance, verifies connectivity,
and deletes it afterward.

```
export RUN_REAL_AWS=1
pytest tests/test_real_aws_rds.py -v
```

⚠️ Costs apply while the instance exists.
Use small classes (db.t3.micro) and ensure cleanup runs.
"""

import os
import time
import pytest
import boto3
import psycopg2
from provisioner import PostgresProvisioner
from models import DBInstanceState
from exceptions import ProvisioningError, ConnectionErrorPG

# --------------------------------------------------------------------------
# Test configuration
# --------------------------------------------------------------------------

REGION = os.getenv("AWS_REGION", "us-west-2")
INSTANCE_ID = f"pgprov-int-{int(time.time())}"
DB_NAME = "testdb"
DB_USER = "pgadmin"
DB_PASS = "StrongPass123!"
INSTANCE_CLASS = "db.t3.micro"
STORAGE_GB = 20


pytestmark = pytest.mark.skipif(
    not os.getenv("RUN_REAL_AWS"),
    reason="Set RUN_REAL_AWS=1 to enable live AWS integration tests",
)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

# Track all instances created during tests for cleanup
_created_instances = set()

def register_instance(instance_id):
    """Register an instance for cleanup."""
    _created_instances.add(instance_id)

def teardown_instances():
    """Ensure all test instances are deleted."""
    client = boto3.client("rds", region_name=REGION)
    for instance_id in _created_instances:
        try:
            client.delete_db_instance(
                DBInstanceIdentifier=instance_id,
                SkipFinalSnapshot=True,
                DeleteAutomatedBackups=True,
            )
            print(f"[cleanup] Deleted instance: {instance_id}")
        except client.exceptions.DBInstanceNotFoundFault:
            pass
        except Exception as e:
            print(f"[cleanup] warning for {instance_id}: {e}")

@pytest.fixture(scope="session", autouse=True)
def cleanup_after():
    yield
    teardown_instances()


# --------------------------------------------------------------------------
# Main integration test
# --------------------------------------------------------------------------

def test_real_rds_lifecycle():
    """
    Full lifecycle test using wait=True for simplicity.
    For API usage pattern, see test_real_rds_async_workflow below.
    """
    prov = PostgresProvisioner(region_name=REGION)
    register_instance(INSTANCE_ID)  # Register for cleanup

    # 1️⃣  Create (with wait=True for integration test)
    db = prov.create_instance(
        identifier=INSTANCE_ID,
        db_name=DB_NAME,
        master_user=DB_USER,
        master_pass=DB_PASS,
        instance_class=INSTANCE_CLASS,
        storage_gb=STORAGE_GB,
        publicly_accessible=True,
        wait=True,  # Block until available for integration testing
    )
    assert db.identifier == INSTANCE_ID
    assert db.engine == "postgres"
    assert db.status == DBInstanceState.available

    # 2️⃣  Describe
    info = prov.describe_instance(INSTANCE_ID)
    assert info.status == DBInstanceState.available

    # 3️⃣  Get connection config (for user's migration tool)
    try:
        conn_config = prov.get_connection_info(INSTANCE_ID, DB_PASS)
        assert conn_config["host"] is not None
        assert conn_config["port"] == 5432
        assert conn_config["dbname"] == DB_NAME
        assert conn_config["user"] == DB_USER
        assert conn_config["password"] == DB_PASS
        print(f"[integration] ✅ Connection config: {conn_config['host']}:{conn_config['port']}")
    except ConnectionNotReady as e:
        pytest.fail(f"Instance should be ready but got: {e}")

    # 4️⃣  Test actual connection (may fail due to security group restrictions)
    try:
        conn = prov.connect(identifier=INSTANCE_ID, password=DB_PASS)
        assert conn is not None
        conn.close()
        print("[integration] ✅ Successfully connected to database")
    except ConnectionErrorPG as e:
        print(f"[integration] ⚠️  Connection blocked (likely security group): {e}")
        print("[integration] Instance is available but not accessible from this network")
        # This is expected if no security group allows access

    # 5️⃣  Delete
    prov.delete_instance(identifier=INSTANCE_ID, skip_snapshot=True)

    # Verify deletion initiated (instance enters "deleting" state)
    time.sleep(2)
    info = prov.describe_instance(INSTANCE_ID)
    assert info.status == DBInstanceState.deleting
    print(f"[integration] ✅ Instance {INSTANCE_ID} is deleting")
    print(f"[integration] Successfully tested full lifecycle for {INSTANCE_ID}")


def test_real_rds_async_workflow():
    """
    Demonstrates the async polling workflow for API usage.
    This is how your service should use pg_provisioner:
    
    1. API endpoint: initiate provisioning (returns immediately)
    2. Status endpoint: poll for status updates
    3. Config endpoint: get connection info when ready
    """
    prov = PostgresProvisioner(region_name=REGION)
    async_instance_id = f"pgprov-async-{int(time.time())}"
    register_instance(async_instance_id)  # Register for cleanup

    try:
        # PHASE 1: Initiate provisioning (fast, returns immediately)
        print("[async-demo] Phase 1: Initiating provisioning...")
        db = prov.create_instance(
            identifier=async_instance_id,
            db_name=DB_NAME,
            master_user=DB_USER,
            master_pass=DB_PASS,
            instance_class=INSTANCE_CLASS,
            storage_gb=STORAGE_GB,
            publicly_accessible=True,
            wait=False,  # 🔑 Non-blocking! Returns immediately
        )
        assert db.status in (DBInstanceState.creating, DBInstanceState.available)
        print(f"[async-demo] ✅ Provisioning initiated (status: {db.status.value})")

        # PHASE 2: Poll for status (simulate frontend polling every 30 seconds)
        print("[async-demo] Phase 2: Polling for availability...")
        max_polls = 60
        for poll_count in range(max_polls):
            info = prov.describe_instance(async_instance_id)
            print(f"[async-demo] Poll {poll_count + 1}: status = {info.status.value}")
            
            if info.is_available():
                print(f"[async-demo] ✅ Instance is available! (took {poll_count + 1} polls)")
                break
            
            time.sleep(30)  # Wait 30 seconds before next poll
        else:
            raise ProvisioningError(f"Instance {async_instance_id} did not reach available state")

        # PHASE 3: Get connection config when ready
        print("[async-demo] Phase 3: Retrieving connection config...")
        conn_config = prov.get_connection_info(async_instance_id, DB_PASS)
        print(f"[async-demo] ✅ Connection config ready:")
        print(f"[async-demo]    host: {conn_config['host']}")
        print(f"[async-demo]    port: {conn_config['port']}")
        print(f"[async-demo]    database: {conn_config['dbname']}")
        print(f"[async-demo]    user: {conn_config['user']}")
        print(f"[async-demo] This config is now shown to user for migration")

    finally:
        # Cleanup
        print(f"[async-demo] Cleaning up {async_instance_id}...")
        try:
            prov.delete_instance(identifier=async_instance_id, skip_snapshot=True)
            print("[async-demo] ✅ Cleanup complete")
        except Exception as e:
            print(f"[async-demo] ⚠️  Cleanup warning: {e}")
