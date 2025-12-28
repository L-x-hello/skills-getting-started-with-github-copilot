import os
import sys
import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

# ensure src is importable
ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)

from app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister():
    activity = "Chess Club"
    email = "pytest-user@example.com"

    # signup
    resp = client.post(f"/activities/{quote(activity)}/signup?email={email}")
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    # unregister
    resp = client.delete(f"/activities/{quote(activity)}/signup?email={email}")
    assert resp.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_nonexistent_returns_404():
    activity = "Chess Club"
    email = "does-not-exist@example.com"
    resp = client.delete(f"/activities/{quote(activity)}/signup?email={email}")
    assert resp.status_code == 404
