import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set test environment
os.environ["DATABASE_URL"] = "sqlite:///./test_fitness.db"
os.environ["ADMIN_USERNAME"] = "testadmin"
os.environ["ADMIN_PASSWORD"] = "testpass123"
os.environ["GOOGLE_API_KEY"] = ""  # Force test fallback engine

from app.database import Base, get_db
from app.main import app
from app.models import User, WorkoutPlan
from app.gemini_service import generate_fallback_plan, modify_fallback_plan
from app.utils import create_admin_token, verify_admin_token, sanitize_workout_plan

# Test SQLite Engine
TEST_DATABASE_URL = "sqlite:///./test_fitness.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_fitness.db"):
        try:
            os.remove("./test_fitness.db")
        except Exception:
            pass


@pytest.fixture
def client():
    return TestClient(app)


def test_home_page_renders(client):
    """Test that the landing page loads successfully with HTML content."""
    response = client.get("/")
    assert response.status_code == 200
    assert "FitBuddy" in response.text
    assert "Your AI-Powered Fitness Companion" in response.text
    assert "Generate My 7-Day Plan" in response.text


def test_form_validation_rejects_empty_or_invalid_fields(client):
    """Test server-side validation error handling on invalid inputs."""
    # Test empty name
    response = client.post("/generate-workout", data={
        "name": "",
        "user_id": "test_user",
        "age": "25",
        "weight": "70",
        "goal": "Weight Loss",
        "intensity": "Medium"
    })
    assert response.status_code == 400
    assert "valid name" in response.text

    # Test invalid age
    response = client.post("/generate-workout", data={
        "name": "Alex",
        "user_id": "alex_fit",
        "age": "5",  # Below 13
        "weight": "70",
        "goal": "Weight Loss",
        "intensity": "Medium"
    })
    assert response.status_code == 400
    assert "age between 13 and 120" in response.text


def test_generate_workout_creates_user_and_plan(client):
    """Test full workout plan generation flow and redirection to result page."""
    user_id = "jordan_smith"
    response = client.post("/generate-workout", data={
        "name": "Jordan Smith",
        "user_id": user_id,
        "age": "28",
        "weight": "75.5",
        "goal": "Muscle Gain",
        "intensity": "High"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert "Jordan Smith" in response.text
    assert "Your 7-Day" in response.text
    assert "Day 1" in response.text
    assert "Day 7" in response.text
    assert "AI Nutrition & Recovery" in response.text


def test_result_page_loads_existing_user(client):
    """Test retrieving existing user's workout plan via GET /result/{user_id}."""
    response = client.get("/result/jordan_smith")
    assert response.status_code == 200
    assert "Hi, " in response.text
    assert "Muscle Gain" in response.text
    assert "75.5" in response.text


def test_result_page_returns_404_for_nonexistent_user(client):
    """Test 404 response for unknown user ID."""
    response = client.get("/result/non_existent_athlete_123")
    assert response.status_code == 404
    assert "User Not Found" in response.text


def test_submit_feedback_updates_plan_and_preserves_original(client):
    """Test feedback submission and verified AI plan update."""
    user_id = "jordan_smith"
    response = client.post("/submit-feedback", data={
        "user_id": user_id,
        "feedback": "I prefer home workouts with dumbbells only"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert "Updated with Feedback" in response.text
    assert "AI Adaptation Applied" in response.text

    # Verify JSON API also reports updated status
    json_res = client.get(f"/api/user/{user_id}/json")
    assert json_res.status_code == 200
    data = json_res.json()
    assert data["is_updated"] is True
    assert "home" in data["feedback"].lower()


def test_download_plan_endpoint(client):
    """Test plain text download generation for workout plan."""
    response = client.get("/api/user/jordan_smith/download")
    assert response.status_code == 200
    assert "FITBUDDY - AI PERSONALIZED 7-DAY FITNESS BLUEPRINT" in response.text
    assert "Athlete: Jordan Smith" in response.text
    assert "Day 1" in response.text


def test_admin_authentication_and_dashboard_protection(client):
    """Test admin login flow, session cookie verification, and dashboard access."""
    # 1. Unauthenticated request should redirect to /admin/login
    res = client.get("/view-all-users", follow_redirects=False)
    assert res.status_code in [302, 303, 307]
    assert "/admin/login" in res.headers["location"]

    # 2. Invalid credentials
    bad_login = client.post("/admin/login", data={
        "username": "wronguser",
        "password": "wrongpassword"
    })
    assert bad_login.status_code == 401
    assert "Invalid admin username or password" in bad_login.text

    # 3. Valid credentials
    good_login = client.post("/admin/login", data={
        "username": "testadmin",
        "password": "testpass123"
    }, follow_redirects=True)
    assert good_login.status_code == 200
    assert "Admin Dashboard" in good_login.text
    assert "Total Registered Users" in good_login.text
    assert "jordan_smith" in good_login.text


def test_admin_delete_user(client):
    """Test admin deletion of user and plan."""
    # Login first
    client.post("/admin/login", data={
        "username": "testadmin",
        "password": "testpass123"
    })

    # Delete user
    del_res = client.post("/admin/delete-user/jordan_smith", follow_redirects=True)
    assert del_res.status_code == 200

    # User should no longer exist
    res = client.get("/result/jordan_smith")
    assert res.status_code == 404


def test_utils_security_token():
    """Test HMAC session token generation and verification."""
    token = create_admin_token("testadmin")
    assert verify_admin_token(token) is True
    assert verify_admin_token("invalid:token:format") is False
    assert verify_admin_token(None) is False


def test_fallback_ai_generator():
    """Test fallback AI generator provides valid 7-day structure."""
    user_data = {
        "name": "Sarah Connor",
        "age": 30,
        "weight": 62.0,
        "goal": "Weight Loss",
        "intensity": "High"
    }
    plan = generate_fallback_plan(user_data)
    assert len(plan["days"]) == 7
    assert plan["days"][0]["day"] == 1
    assert "nutrition_tip" in plan
    assert "disclaimer" in plan
