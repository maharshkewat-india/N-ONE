import shutil
from pathlib import Path
from uuid import uuid4

import pandas as pd
import pytest

import app


@pytest.fixture
def case_workspace(monkeypatch: pytest.MonkeyPatch):
    root = Path(__file__).parent / f"_investigation_case_{uuid4().hex}"
    logs = root / "detection_logs"
    logs.mkdir(parents=True)
    monkeypatch.setattr(app, "CASE_RECORDS_PATH", logs / "investigation_cases.csv")
    monkeypatch.setattr(app, "CASE_ACTIVITY_LOG_PATH", logs / "case_activity_log.csv")
    monkeypatch.setattr(app, "VICTIM_SIGHTING_LOG_PATH", logs / "victim_sighting_log.csv")
    try:
        yield root
    finally:
        shutil.rmtree(root, ignore_errors=True)


def _victim_profiles() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "profile_id": "Victim_Ravi",
                "name": "Ravi",
                "category": "Victim",
                "file_name": "Victim_Ravi__front.jpg",
                "image_path": "registered_faces/Victim_Ravi__front.jpg",
            }
        ]
    )


def test_only_administrator_can_open_case(monkeypatch: pytest.MonkeyPatch, case_workspace: Path) -> None:
    monkeypatch.setattr(app.st, "session_state", {"role": "Operator"})
    monkeypatch.setattr(app, "get_registered_profiles_df", _victim_profiles)

    created, message, case_id = app.create_investigation_case("Victim_Ravi")

    assert not created
    assert "Administrator" in message
    assert case_id == ""
    assert app.load_investigation_cases().empty


def test_case_updates_create_a_reviewable_timeline(
    monkeypatch: pytest.MonkeyPatch, case_workspace: Path
) -> None:
    audit_events = []
    monkeypatch.setattr(app.st, "session_state", {"role": "Administrator"})
    monkeypatch.setattr(app, "get_registered_profiles_df", _victim_profiles)
    monkeypatch.setattr(app, "log_event", lambda **event: audit_events.append(event))

    created, _, case_id = app.create_investigation_case(
        "Victim_Ravi",
        priority="High",
        last_seen_location="Gate A",
        assigned_to="Officer A",
        notes="Family report received.",
    )
    updated, message = app.update_investigation_case(
        case_id=case_id,
        status="Verified Lead",
        priority="Critical",
        last_seen_location="Parking",
        assigned_to="Officer B",
        case_contact="Family desk",
        notes="Escalated after manual review.",
        activity_type="Lead verified",
        activity_location="Parking",
        activity_note="Operator checked the footage and verified the lead.",
    )

    assert created
    assert updated
    assert "updated" in message.lower()
    saved_case = app.get_investigation_case(case_id)
    assert saved_case["status"] == "Verified Lead"
    assert saved_case["priority"] == "Critical"
    assert saved_case["assigned_to"] == "Officer B"
    assert saved_case["case_contact"] == "Family desk"
    timeline = app.get_investigation_timeline(case_id)
    assert {"Case opened", "Lead verified"}.issubset(set(timeline["event_type"]))
    assert [event["event_type"] for event in audit_events] == ["Case Opened", "Case Updated"]


def test_timeline_includes_existing_camera_sightings(
    monkeypatch: pytest.MonkeyPatch, case_workspace: Path
) -> None:
    monkeypatch.setattr(app.st, "session_state", {"role": "Administrator"})
    monkeypatch.setattr(app, "get_registered_profiles_df", _victim_profiles)
    monkeypatch.setattr(app, "log_event", lambda **_: None)
    created, _, case_id = app.create_investigation_case("Victim_Ravi")
    assert created
    pd.DataFrame(
        [
            ["Victim_Ravi", "Ravi", "2026-11-03 11:10:00", "North gate"],
            ["Victim_Other", "Other", "2026-11-03 11:11:00", "East gate"],
        ],
        columns=["profile_id", "name", "timestamp", "location"],
    ).to_csv(app.VICTIM_SIGHTING_LOG_PATH, index=False)

    timeline = app.get_investigation_timeline(case_id)

    sighting = timeline[timeline["event_type"] == "Camera sighting recorded"]
    assert len(sighting) == 1
    assert sighting.iloc[0]["location"] == "North gate"
    assert sighting.iloc[0]["source"] == "Surveillance log"
