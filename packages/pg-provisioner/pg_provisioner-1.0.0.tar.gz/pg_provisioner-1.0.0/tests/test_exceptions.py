import pytest
from exceptions import (
    ProvisioningError, AWSOperationError, ConnectionNotReady,
    NetworkError, InvalidCredentialsError, ConnectionErrorPG
)

def test_provisioning_error_str():
    e = ProvisioningError("Fail", identifier="db1", cause=ValueError("boom"))
    msg = str(e)
    assert "db1" in msg and "ValueError" in msg

def test_aws_operation_error_with_operation():
    e = AWSOperationError("bad", operation="create")
    assert "operation=create" in str(e)

def test_connection_not_ready_message():
    e = ConnectionNotReady("demo", "creating")
    assert "creating" in str(e)

def test_network_error_wraps_cause():
    cause = ConnectionError("network fail")
    e = NetworkError("failed", cause=cause)
    assert "network fail" in str(e)

def test_invalid_credentials_error():
    e = InvalidCredentialsError()
    assert "Invalid PostgreSQL" in str(e)

def test_connection_error_pg():
    e = ConnectionErrorPG("fail", cause=RuntimeError("x"))
    assert "RuntimeError" in str(e)
