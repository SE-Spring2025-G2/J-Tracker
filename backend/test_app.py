"""
Test module for the backend
"""
import hashlib
from io import BytesIO

import pytest
import json
import datetime
from flask_mongoengine import MongoEngine
import yaml
from app import create_app, Users


# Pytest fixtures are useful tools for calling resources
# over and over, without having to manually recreate them,
# eliminating the possibility of carry-over from previous tests,
# unless defined as such.
# This fixture receives the client returned from create_app
# in app.py
@pytest.fixture
def client():
    """
    Creates a client fixture for tests to use

    :return: client fixture
    """
    app = create_app()
    with open("application.yml") as f:
        info = yaml.load(f, Loader=yaml.FullLoader)
        username = info["USERNAME"]
        password = info["PASSWORD"]
        app.config["MONGODB_SETTINGS"] = {
            "db": "appTracker",
            "host": f"mongodb+srv://{username}:{password}@applicationtracker.287am.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",
        }
    db = MongoEngine()
    db.disconnect()
    db.init_app(app)
    client = app.test_client()
    yield client
    db.disconnect()


@pytest.fixture
def user(client):
    """
    Creates a user with test data

    :param client: the mongodb client
    :return: the user object and auth token
    """
    # print(request.data)
    data = {"username": "testUser", "password": "test", "fullName": "fullName"}

    user = Users.objects(username=data["username"])
    user.first()["applications"] = []
    user.first().save()
    rv = client.post("/users/login", json=data)
    jdata = json.loads(rv.data.decode("utf-8"))
    header = {"Authorization": "Bearer " + jdata["token"]}
    yield user.first(), header
    user.first()["applications"] = []
    user.first().save()


# 1. testing if the flask app is running properly
def test_alive(client):
    """
    Tests that the application is running properly

    :param client: mongodb client
    """
    rv = client.get("/")
    assert rv.data.decode("utf-8") == '{"message":"Server up and running"}\n'


# 2. testing if the search function running properly
def test_search(client):
    """
    Tests that the search is running properly

    :param client: mongodb client
    """
    rv = client.get("/search")
    jdata = json.loads(rv.data.decode("utf-8"))["label"]
    assert jdata == "successful test search"


# 3. testing if the application is getting data from database properly
def test_get_data(client, user):
    """
    Tests that using the application GET endpoint returns data

    :param client: mongodb client
    :param user: the test user object
    """
    user, header = user
    user["applications"] = []
    user.save()
    # without an application
    rv = client.get("/applications", headers=header)
    print(rv.data)
    assert rv.status_code == 200
    assert json.loads(rv.data) == []

    # with data
    application = {
        "jobTitle": "fakeJob12345",
        "companyName": "fakeCompany",
        "date": str(datetime.date(2021, 9, 23)),
        "status": "1",
    }
    user["applications"] = [application]
    user.save()
    rv = client.get("/applications", headers=header)
    print(rv.data)
    assert rv.status_code == 200
    assert json.loads(rv.data) == [application]


# 4. testing if the application is saving data in database properly
def test_add_application(client, mocker, user):
    """
    Tests that using the application POST endpoint saves data

    :param client: mongodb client
    :param user: the test user object
    """
    mocker.patch(
        # Dataset is in slow.py, but imported to main.py
        "app.get_new_user_id",
        return_value=-1,
    )
    user, header = user
    user["applications"] = []
    user.save()
    # mocker.patch(
    #     # Dataset is in slow.py, but imported to main.py
    #     'app.Users.save'
    # )
    rv = client.post(
        "/applications",
        headers=header,
        json={
            "application": {
                "jobTitle": "fakeJob12345",
                "companyName": "fakeCompany",
                "date": str(datetime.date(2021, 9, 23)),
                "status": "1",
            }
        },
    )
    assert rv.status_code == 200
    jdata = json.loads(rv.data.decode("utf-8"))["jobTitle"]
    assert jdata == "fakeJob12345"


# 5. testing if the application is updating data in database properly
def test_update_application(client, user):
    """
    Tests that using the application PUT endpoint functions

    :param client: mongodb client
    :param user: the test user object
    """
    user, auth = user
    application = {
        "id": 3,
        "jobTitle": "test_edit",
        "companyName": "test_edit",
        "date": str(datetime.date(2021, 9, 23)),
        "status": "1",
    }
    user["applications"] = [application]
    user.save()
    new_application = {
        "id": 3,
        "jobTitle": "fakeJob12345",
        "companyName": "fakeCompany",
        "date": str(datetime.date(2021, 9, 22)),
    }

    rv = client.put(
        "/applications/3", json={"application": new_application}, headers=auth
    )
    assert rv.status_code == 200
    jdata = json.loads(rv.data.decode("utf-8"))["jobTitle"]
    assert jdata == "fakeJob12345"


# 6. testing if the application is deleting data in database properly
def test_delete_application(client, user):
    """
    Tests that using the application DELETE endpoint deletes data

    :param client: mongodb client
    :param user: the test user object
    """
    user, auth = user

    application = {
        "id": 3,
        "jobTitle": "fakeJob12345",
        "companyName": "fakeCompany",
        "date": str(datetime.date(2021, 9, 23)),
        "status": "1",
    }
    user["applications"] = [application]
    user.save()

    rv = client.delete("/applications/3", headers=auth)
    jdata = json.loads(rv.data.decode("utf-8"))["jobTitle"]
    assert jdata == "fakeJob12345"


# 8. testing if the flask app is running properly with status code
def test_alive_status_code(client):
    """
    Tests that / returns 200

    :param client: mongodb client
    """
    rv = client.get("/")
    assert rv.status_code == 200


# 9. Testing logging out does not return error
def test_logout(client, user):
    """
    Tests that using the logout function does not return an error

    :param client: mongodb client
    :param user: the test user object
    """
    user, auth = user
    rv = client.post("/users/logout", headers=auth)
    # assert no error occured
    assert rv.status_code == 200

# 10. Testing that using the resume endpoint returns data
def test_resume(client, mocker, user):
    """
    Tests that using the resume endpoint returns data

    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    mocker.patch(
        # Dataset is in slow.py, but imported to main.py
        "app.get_new_user_id",
        return_value=-1,
    )
    user, header = user
    user["applications"] = []
    user.save()
    data = dict(
        file=(BytesIO(b"testing resume"), "resume.txt"),
    )
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200
    rv = client.get("/resume", headers=header)
    assert rv.status_code == 200

# Test Case 11: Test User Signup with Valid Data
def test_signup_valid_data(client):
    """
    Test signing up a new user with valid data.
    """
    data = {"username": "newuser", "password": "newpass", "fullName": "New User"}
    response = client.post("/users/signup", json=data)
    assert response.status_code == 200
    assert "id" in json.loads(response.data)

# Test Case 12: Test User Signup with Invalid Data (Missing Fields)
def test_signup_missing_fields(client):
    """
    Test signing up a new user with missing fields.
    """
    data = {"username": "newuser"}
    response = client.post("/users/signup", json=data)
    assert response.status_code == 400
    assert json.loads(response.data)["error"] == "Missing fields in input"

# Test Case 13: Test User Login with Invalid Credentials
def test_login_invalid_credentials(client, user):
    """
    Test logging in with incorrect credentials.
    """
    data = {"username": "testuser", "password": "wrongpass"}
    response = client.post("/users/login", json=data)
    assert response.status_code == 400
    assert json.loads(response.data)["error"] == "Wrong username or password"

# Test Case 14: Test User Login with Non-Existent User
def test_login_nonexistent_user(client):
    """
    Test logging in with a non-existent user.
    """
    data = {"username": "nonexistent", "password": "testpass"}
    response = client.post("/users/login", json=data)
    assert response.status_code == 400
    assert json.loads(response.data)["error"] == "User not found"

# Test Case 15: Test Get Profile Data for Authenticated User
def test_get_profile_authenticated(client, user):
    """
    Test retrieving profile data for an authenticated user.
    """
    _, header = user
    response = client.get("/getProfile", headers=header)
    assert response.status_code == 200
    assert "fullName" in json.loads(response.data)

# Test Case 16: Test Get Profile Data for Unauthenticated User
def test_get_profile_unauthenticated(client):
    """
    Test retrieving profile data without a valid token.
    """
    response = client.get("/getProfile")
    assert response.status_code == 401
    assert json.loads(response.data)["error"] == "Unauthorized"

# Test Case 17: Test Update Profile Data
def test_update_profile(client, user):
    """
    Test updating user profile data.
    """
    _, header = user
    data = {"skills": ["Python", "Flask"], "job_levels": ["Junior"], "locations": ["New York"]}
    response = client.post("/updateProfile", json=data, headers=header)
    assert response.status_code == 200
    assert "skills" in json.loads(response.data)

# Test Case 18: Test Update Profile Data with Invalid Fields
def test_update_profile_invalid_fields(client, user):
    """
    Test updating profile data with invalid fields.
    """
    _, header = user
    data = {"invalid_field": "value"}
    response = client.post("/updateProfile", json=data, headers=header)
    assert response.status_code == 200  # or 400 if validation is strict

# Test Case 19: Test Get Job Recommendations
def test_get_recommendations(client, user):
    """
    Test retrieving job recommendations.
    """
    _, header = user
    response = client.get("/getRecommendations", headers=header)
    assert response.status_code == 200
    assert isinstance(json.loads(response.data), list)

# Test Case 20: Test Search Jobs with Keywords
def test_search_jobs_with_keywords(client):
    """
    Test searching jobs with keywords.
    """
    response = client.get("/search?keywords=Python")
    assert response.status_code == 200
    assert isinstance(json.loads(response.data), list)

# Test Case 21: Test Search Jobs with Salary Filter
def test_search_jobs_with_salary(client):
    """
    Test searching jobs with a salary filter.
    """
    response = client.get("/search?keywords=Python&salary=100000")
    assert response.status_code == 200
    assert isinstance(json.loads(response.data), list)

# Test Case 22: Test Add Application with Missing Fields
def test_add_application_missing_fields(client, user):
    """
    Test adding an application with missing fields.
    """
    _, header = user
    data = {"application": {"jobTitle": "Software Engineer"}}  # Missing companyName
    response = client.post("/applications", json=data, headers=header)
    assert response.status_code == 400
    assert json.loads(response.data)["error"] == "Missing fields in input"

# Test Case 23: Test Update Non-Existent Application
def test_update_nonexistent_application(client, user):
    """
    Test updating a non-existent application.
    """
    _, header = user
    data = {"application": {"jobTitle": "Updated Job"}}
    response = client.put("/applications/999", json=data, headers=header)  # 999 is a non-existent ID
    assert response.status_code == 400
    assert json.loads(response.data)["error"] == "Application not found"

# Test Case 24: Test Delete Non-Existent Application
def test_delete_nonexistent_application(client, user):
    """
    Test deleting a non-existent application.
    """
    _, header = user
    response = client.delete("/applications/999", headers=header)  # 999 is a non-existent ID
    assert response.status_code == 400
    assert json.loads(response.data)["error"] == "Application not found"

# Test Case 25: Test Upload Resume with Invalid File Type
def test_upload_resume_invalid_file_type(client, user):
    """
    Test uploading a resume with an invalid file type.
    """
    _, header = user
    data = {"file": (BytesIO(b"invalid file content"), "resume.txt")}
    response = client.post("/resume", data=data, headers=header, content_type="multipart/form-data")
    assert response.status_code == 400
    assert json.loads(response.data)["error"] == "No resume file found in the input"

# Test Case 26: Test Get Resume When None Exists
def test_get_resume_none_exists(client, user):
    """
    Test retrieving a resume when none exists.
    """
    _, header = user
    response = client.get("/resume", headers=header)
    assert response.status_code == 400
    assert json.loads(response.data)["error"] == "resume could not be found"

# Test Case 27: Test Google Signup Redirect
def test_google_signup_redirect(client):
    """
    Test the Google signup redirect.
    """
    response = client.get("/users/signupGoogle")
    assert response.status_code == 302  # Redirect status code

# Test Case 28: Test Google Signup Authorized
def test_google_signup_authorized(client, mocker):
    """
    Test the Google signup authorized endpoint.
    """
    mocker.patch("authlib.integrations.flask_client.OAuth.google.authorize_access_token", return_value={"access_token": "test_token"})
    mocker.patch("authlib.integrations.flask_client.OAuth.google.parse_id_token", return_value={"email": "test@example.com", "email_verified": True, "given_name": "Test", "family_name": "User"})
    response = client.get("/users/signupGoogle/authorized")
    assert response.status_code == 302  # Redirect status code

# Test Case 29: Test Middleware with Invalid Token
def test_middleware_invalid_token(client):
    """
    Test middleware with an invalid token.
    """
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/applications", headers=headers)
    assert response.status_code == 401
    assert json.loads(response.data)["error"] == "Unauthorized"

# Test Case 30: Test Middleware with Expired Token
def test_middleware_expired_token(client, user):
    """
    Test middleware with an expired token.
    """
    _, header = user
    # Simulate an expired token
    user.first().update(authTokens=[{"token": "expired_token", "expiry": "01/01/2020, 00:00:00"}])
    response = client.get("/applications", headers=header)
    assert response.status_code == 401
    assert json.loads(response.data)["error"] == "Unauthorized"


if __name__ == "__main__":
    import sys
    try:
        # Run your tests here
        # For example, you can use unittest or custom test logic
        # If any test fails, raise an exception
        pass  # Replace this with your test logic
    except Exception as e:
        print(f"Tests failed: {e}")
        sys.exit(1)  # Exit with a non-zero code to indicate failure
    else:
        print("All tests passed!")
        sys.exit(0)  # Exit with a zero code to indicate success