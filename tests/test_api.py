import uuid
import urllib.parse

from fastapi.testclient import TestClient

from src.app import app


def test_get_activities():
    client = TestClient(app)
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # basic sanity check for a known activity
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    client = TestClient(app)
    activity = "Chess Club"
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"

    # get current participants
    resp = client.get("/activities")
    assert resp.status_code == 200
    before = resp.json()[activity]["participants"][:]

    # sign up
    signup_path = f"/activities/{urllib.parse.quote(activity)}/signup?email={urllib.parse.quote(email)}"
    resp = client.post(signup_path)
    assert resp.status_code == 200
    assert f"Signed up {email}" in resp.json().get("message", "")

    # verify participant present
    resp = client.get("/activities")
    participants = resp.json()[activity]["participants"]
    assert email in participants

    # unregister
    delete_path = f"/activities/{urllib.parse.quote(activity)}/participants?email={urllib.parse.quote(email)}"
    resp = client.delete(delete_path)
    assert resp.status_code == 200
    assert f"Unregistered {email}" in resp.json().get("message", "")

    # verify removed
    resp = client.get("/activities")
    participants = resp.json()[activity]["participants"]
    assert email not in participants
