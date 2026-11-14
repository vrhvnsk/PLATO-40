import json
from core.candidate_evidence import match, report

def test_cleaning_match_not_execution(tmp_path):
    (tmp_path/"events.jsonl").write_text(
        json.dumps({"event_id":"E1","timestamp_utc":"2026-01-01T11:00:00Z",
                    "room_id":"R101","type":"cleaning_completed"})+"\n")
    d=[{"event_id":"D1","timestamp_utc":"2026-01-01T10:00:00Z",
        "affected_assets":["R101"],"action":"schedule_cleaning","issue_type":"room_turnaround"}]
    rows=match(d,tmp_path)
    assert rows[0]["observational_status"]=="candidate_observation"
    assert rows[0]["execution_confirmed"] is False
    assert rows[0]["outcome_attributable"] is False
    assert rows[0]["candidate_evidence"][0]["source_id"]=="E1"

def test_future_and_prior_not_confused(tmp_path):
    (tmp_path/"events.jsonl").write_text(
        json.dumps({"event_id":"E1","timestamp_utc":"2026-01-01T09:00:00Z",
                    "room_id":"R101","type":"cleaning_completed"})+"\n")
    d=[{"event_id":"D1","timestamp_utc":"2026-01-01T10:00:00Z",
        "affected_assets":["R101"],"action":"schedule_cleaning"}]
    assert match(d,tmp_path)[0]["candidate_evidence"]==[]

def test_temperature_observation(tmp_path):
    (tmp_path/"room_telemetry.csv").write_text(
        "timestamp_utc,room_id,temperature_c\n"
        "2026-01-01T10:00:00Z,R101,18.0\n"
        "2026-01-01T11:00:00Z,R101,21.0\n")
    d=[{"event_id":"D1","timestamp_utc":"2026-01-01T10:00:00Z",
        "affected_assets":["R101"],"action":"adjust_room_setpoint","issue_type":"heating_comfort"}]
    rows=match(d,tmp_path)
    assert rows[0]["candidate_evidence"][0]["value_c"]==21.0

def test_work_order_requires_completed(tmp_path):
    (tmp_path/"work_orders.csv").write_text(
        "work_order_id,asset_id,status,completed_utc\n"
        "WO1,HP1,open,2026-01-01T11:00:00Z\n"
        "WO2,HP1,completed,2026-01-01T12:00:00Z\n")
    d=[{"event_id":"D1","timestamp_utc":"2026-01-01T10:00:00Z",
        "affected_assets":["HP1"],"action":"dispatch_technician"}]
    assert match(d,tmp_path)[0]["candidate_evidence"][0]["source_id"]=="WO2"

def test_report(tmp_path):
    d=[{"event_id":"D1"}]
    rows=[{"observational_status":"no_matching_observation","candidate_evidence":[]}]
    m=report(d,rows,tmp_path/"out")
    assert m["confirmed_executions"]==0
    assert (tmp_path/"out"/"REPORT_CANDIDATES.md").exists()

def test_unsupported_action_not_misclassified(tmp_path):
    d=[{"event_id":"D1","timestamp_utc":"2026-01-01T10:00:00Z","affected_assets":["R101"],"action":"notify_guest"}]
    assert match(d,tmp_path)[0]["observational_status"] == "not_evaluated"

def test_heating_requires_cold_baseline(tmp_path):
    (tmp_path/"room_telemetry.csv").write_text("timestamp_utc,room_id,temperature_c\n2026-01-01T10:00:00Z,R101,21.0\n2026-01-01T11:00:00Z,R101,21.0\n")
    d=[{"event_id":"D1","timestamp_utc":"2026-01-01T10:00:00Z","affected_assets":["R101"],"action":"adjust_room_setpoint","issue_type":"heating_comfort"}]
    assert match(d,tmp_path)[0]["observational_status"] == "no_observation_found"

def test_cleaning_event_reuse_flagged(tmp_path):
    (tmp_path/"events.jsonl").write_text(json.dumps({"event_id":"E1","timestamp_utc":"2026-01-01T11:00:00Z","room_id":"R101","type":"cleaning_completed"})+"\n")
    d=[{"event_id":i,"timestamp_utc":"2026-01-01T10:00:00Z","affected_assets":["R101"],"action":"schedule_cleaning"} for i in ["D1","D2"]]
    rows=match(d,tmp_path)
    assert all(r["candidate_evidence"][0]["match_strength"]=="ambiguous_reused_event" for r in rows)

def test_work_order_asset_only_not_proof(tmp_path):
    (tmp_path/"work_orders.csv").write_text("work_order_id,asset_id,status,completed_utc\nWO1,HP1,completed,2026-01-01T12:00:00Z\n")
    d=[{"event_id":"D1","timestamp_utc":"2026-01-01T10:00:00Z","affected_assets":["HP1"],"action":"dispatch_technician"}]
    assert match(d,tmp_path)[0]["candidate_evidence"][0]["match_strength"]=="asset_only_unattributed"
