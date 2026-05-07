from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)
INITIAL_ACTIVITIES = deepcopy(app_module.activities)


def reset_activities() -> None:
    app_module.activities.clear()
    app_module.activities.update(deepcopy(INITIAL_ACTIVITIES))


@pytest.fixture(autouse=True)
def restore_activities() -> None:
    reset_activities()
    yield
    reset_activities()


def test_get_activities_returns_expected_keys() -> None:
    # Arrange
    expected_keys = {"Chess Club", "Programming Class", "Gym Class"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert expected_keys.issubset(set(response.json().keys()))


def test_signup_adds_participant() -> None:
    # Arrange
    activity_name = "Chess Club"
    email = "test.student@mergington.edu"
    initial_count = len(app_module.activities[activity_name]["participants"])

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert len(app_module.activities[activity_name]["participants"]) == initial_count + 1
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_duplicate_returns_400() -> None:
    # Arrange
    activity_name = "Chess Club"
    email = "duplicate.student@mergington.edu"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant() -> None:
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    assert email in app_module.activities[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in app_module.activities[activity_name]["participants"]


def test_remove_nonexistent_participant_returns_404() -> None:
    # Arrange
    activity_name = "Chess Club"
    email = "missing.student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_remove_from_invalid_activity_returns_404() -> None:
    # Arrange
    activity_name = "Nonexistent Club"
    email = "someone@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
