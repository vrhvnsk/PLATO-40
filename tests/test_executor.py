from core.executor import execute, execute_decision


def test_missing_human_approval():
    decision = {
        "event_id": "A1",
        "action": "dispatch_technician",
        "requires_human_approval": True,
    }

    result = execute_decision(decision, {})

    assert result["status"] == "pending_approval"
    assert "human_approval" in result["missing_requirements"]
    assert result["simulated"] is False


def test_missing_guest_consent():
    decision = {
        "event_id": "A2",
        "action": "schedule_cleaning",
        "requires_guest_consent": True,
    }

    result = execute_decision(decision, {})

    assert result["status"] == "pending_consent"
    assert "guest_consent" in result["missing_requirements"]


def test_missing_dependency():
    decision = {
        "event_id": "A3",
        "action": "notify_guest",
        "dependencies": ["CLEAN-001"],
    }

    result = execute_decision(decision, {})

    assert result["status"] == "pending_dependency"
    assert "dependency:CLEAN-001" in result["missing_requirements"]


def test_missing_resource():
    decision = {
        "event_id": "A4",
        "action": "dispatch_robot",
    }

    result = execute_decision(decision, {})

    assert result["status"] == "pending_resource"
    assert "resource_availability" in result["missing_requirements"]


def test_room_release_requires_verification():
    decision = {
        "event_id": "A5",
        "action": "release_room",
    }

    result = execute_decision(decision, {})

    assert result["status"] == "pending_verification"
    assert "room_clean_verified" in result["missing_requirements"]
    assert result["simulated"] is False


def test_duplicate_decisions_blocked():
    decision = {
        "event_id": "A6",
        "timestamp_utc": "2026-01-01T10:00:00Z",
        "action": "flag_anomaly",
    }

    results = execute([decision, decision], context={})

    assert len(results) == 2
    assert results[1]["status"] == "blocked"
    assert results[1]["simulated"] is False

def test_simulated_cleaning_with_available_resource():
    decision = {
        "event_id": "A7",
        "action": "schedule_cleaning",
        "resource_id": "CLEANER-01",
    }

    context = {
        "resource_confirmations": {"A7": "CLEANER-01"},
        "duration_minutes": 45,
    }

    result = execute_decision(decision, context)

    assert result["status"] == "simulated_completed"
    assert result["simulated"] is True
    assert result["resource_id"] == "CLEANER-01"
    assert result["duration_minutes"] == 45
    assert result["verification"]["status"] == "not_verified"
    assert result["missing_requirements"] == []


def test_audit_records_multiple_missing_requirements():
    decision = {
        "event_id": "A8",
        "action": "release_room",
        "requires_human_approval": True,
        "dependencies": ["CLEAN-001"],
    }

    result = execute_decision(decision, {})

    assert result["status"] == "pending_dependency"
    assert result["missing_requirements"] == [
        "dependency:CLEAN-001",
        "human_approval",
        "room_clean_verified",
    ]
    assert result["reason"]
    assert result["simulated"] is False

def test_resource_confirmation_mismatch():
    decision = {
        "event_id": "A9",
        "action": "schedule_cleaning",
        "resource_id": "CLEANER-01",
    }

    context = {
        "resource_confirmations": {
            "A9": "CLEANER-02"
        }
    }

    result = execute_decision(decision, context)

    assert result["status"] == "pending_resource"
    assert "resource_availability" in result["missing_requirements"]
    assert result["simulated"] is False

def test_matching_resource_confirmation():
    decision = {
        "event_id": "A10",
        "action": "schedule_cleaning",
        "resource_id": "CLEANER-01",
    }

    context = {
        "resource_confirmations": {
            "A10": "CLEANER-01"
        }
    }

    result = execute_decision(decision, context)

    assert result["status"] == "simulated_completed"
    assert result["simulated"] is True
    assert result["resource_id"] == "CLEANER-01"
    assert result["missing_requirements"] == []
    assert result["verification"]["status"] == "not_verified"