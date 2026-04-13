import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Fixture to provide a TestClient instance."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Fixture to reset the in-memory activities database before each test."""
    # Reset to initial state
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    })


def test_get_activities(client):
    """Test GET /activities returns the activity dictionary."""
    # Arrange: Activities are reset by fixture

    # Act: Make GET request to /activities
    response = client.get("/activities")

    # Assert: Response is successful and contains expected activities
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_for_activity_success(client):
    """Test successful signup for an activity."""
    # Arrange: Activities are reset by fixture

    # Act: Make POST request to signup for Chess Club
    response = client.post("/activities/Chess%20Club/signup?email=newstudent@mergington.edu")

    # Assert: Response is successful and participant is added
    assert response.status_code == 200
    data = response.json()
    assert "Signed up newstudent@mergington.edu for Chess Club" in data["message"]
    # Verify participant was added
    get_response = client.get("/activities")
    activities_data = get_response.json()
    assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]


def test_signup_for_activity_duplicate(client):
    """Test duplicate signup returns 400 error."""
    # Arrange: Activities are reset by fixture, michael@mergington.edu is already signed up

    # Act: Attempt to sign up michael@mergington.edu again
    response = client.post("/activities/Chess%20Club/signup?email=michael@mergington.edu")

    # Assert: Response is 400 Bad Request
    assert response.status_code == 400
    data = response.json()
    assert "Student already signed up for this activity" in data["detail"]


def test_remove_participant_success(client):
    """Test successful removal of a participant."""
    # Arrange: Activities are reset by fixture, michael@mergington.edu is signed up

    # Act: Make DELETE request to remove michael@mergington.edu from Chess Club
    response = client.delete("/activities/Chess%20Club/participants?email=michael@mergington.edu")

    # Assert: Response is successful and participant is removed
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered michael@mergington.edu from Chess Club" in data["message"]
    # Verify participant was removed
    get_response = client.get("/activities")
    activities_data = get_response.json()
    assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]


def test_remove_participant_not_found(client):
    """Test removing a non-existent participant returns 404 error."""
    # Arrange: Activities are reset by fixture

    # Act: Attempt to remove a participant not in the activity
    response = client.delete("/activities/Chess%20Club/participants?email=nonexistent@mergington.edu")

    # Assert: Response is 404 Not Found
    assert response.status_code == 404
    data = response.json()
    assert "Participant not found" in data["detail"]


def test_root_redirect(client):
    """Test GET / redirects to /static/index.html."""
    # Arrange: No special setup needed

    # Act: Make GET request to /
    response = client.get("/")

    # Assert: Response is a redirect to /static/index.html
    assert response.status_code == 307  # Temporary Redirect
    assert response.headers["location"] == "/static/index.html"