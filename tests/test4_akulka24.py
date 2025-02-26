import json
import pytest
from backend.app import create_app  # Import the Flask app

@pytest.fixture(scope="module")
def test_client():
    """Fixture to create a test client for Flask."""
    app = create_app()
    return app.test_client()

def test_login_fail_wrong_password(test_client):
    """Test that login fails with an incorrect password."""
    login_data = {
        "username": "valid_user",
        "password": "wrong_password"
    }

    response = test_client.post("/users/login", data=json.dumps(login_data), content_type="application/json")

    # Verify response is 400 (Bad Request) or 401 (Unauthorized)
    assert response.status_code in [400, 401], f"❌ Unexpected status code: {response.status_code}"

    response_data = json.loads(response.data)
    
    assert "error" in response_data, "❌ No error message returned"
    assert response_data["error"] in ["Wrong username or password", "Invalid credentials"], "❌ Unexpected error message"

    print("✅ Login failure test with incorrect password passed successfully.")
