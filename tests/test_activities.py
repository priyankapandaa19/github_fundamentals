from fastapi.testclient import TestClient
from src import app as app_module
import copy

client = TestClient(app_module.app)

# Keep an original snapshot so tests can restore state
_original_activities = copy.deepcopy(app_module.activities)


def setup_function():
    # restore activities to original snapshot before each test
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(_original_activities))


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data


def test_signup_and_unregister():
    email = "testuser@example.com"
    activity = "Chess Club"

    # ensure clean
    if email in app_module.activities[activity]["participants"]:
        app_module.activities[activity]["participants"].remove(email)

    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert email in app_module.activities[activity]["participants"]

    # unregister
    resp = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 200
    assert email not in app_module.activities[activity]["participants"]


def test_duplicate_signup_behavior():
    email = "dup@example.com"
    activity = "Programming Class"

    # ensure clean
    while email in app_module.activities[activity]["participants"]:
        app_module.activities[activity]["participants"].remove(email)

    resp1 = client.post(f"/activities/{activity}/signup?email={email}")
    resp2 = client.post(f"/activities/{activity}/signup?email={email}")

    assert resp1.status_code == 200
    assert resp2.status_code == 200

    # Current behavior: duplicate entries are allowed (counts 2)
    assert app_module.activities[activity]["participants"].count(email) == 2

    # cleanup
    while email in app_module.activities[activity]["participants"]:
        app_module.activities[activity]["participants"].remove(email)
