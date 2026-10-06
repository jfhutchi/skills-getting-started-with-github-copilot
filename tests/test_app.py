from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


ACTIVITY_NAME = "Basketball Team"


@pytest.fixture
def client():
    original_activities = deepcopy(activities)
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        activities.clear()
        activities.update(original_activities)


def test_get_activities_returns_activity_data(client):
    # Arrange
    expected_activity = ACTIVITY_NAME

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert expected_activity in response.json()
    assert "participants" in response.json()[expected_activity]


def test_signup_adds_participant(client):
    # Arrange
    email = "new-student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": email},
    )
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {ACTIVITY_NAME}"
    assert email in activities_response.json()[ACTIVITY_NAME]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "existing-student@mergington.edu"
    activities[ACTIVITY_NAME]["participants"].append(email)

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activities[ACTIVITY_NAME]["participants"].count(email) == 1


def test_signup_rejects_unknown_activity(client):
    # Arrange
    unknown_activity = "Unknown Activity"

    # Act
    response = client.post(
        f"/activities/{unknown_activity}/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    # Arrange
    email = "registered-student@mergington.edu"
    activities[ACTIVITY_NAME]["participants"].append(email)

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": email},
    )
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {ACTIVITY_NAME}"
    assert email not in activities_response.json()[ACTIVITY_NAME]["participants"]


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    unknown_activity = "Unknown Activity"

    # Act
    response = client.delete(
        f"/activities/{unknown_activity}/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_rejects_unregistered_participant(client):
    # Arrange
    email = "not-registered@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"