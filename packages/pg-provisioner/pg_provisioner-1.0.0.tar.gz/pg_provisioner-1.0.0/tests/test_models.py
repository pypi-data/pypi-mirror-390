from models import DBInstanceInfo, DBInstanceState

def test_safe_enum_handles_unknown():
    assert DBInstanceState.safe("strange") == DBInstanceState.unknown

def test_from_aws_parsing_minimal():
    db = {
        "DBInstanceIdentifier": "x",
        "Engine": "postgres",
        "DBInstanceStatus": "available",
        "AllocatedStorage": 10,
    }
    info = DBInstanceInfo.from_aws(db)
    assert info.identifier == "x"
    assert info.is_available()

def test_to_dict_and_json():
    db = {
        "DBInstanceIdentifier": "x",
        "Engine": "postgres",
        "DBInstanceStatus": "available",
        "AllocatedStorage": 10,
    }
    info = DBInstanceInfo.from_aws(db)
    assert isinstance(info.to_dict(), dict)
    assert '"identifier": "x"' in info.to_json(indent=2)
