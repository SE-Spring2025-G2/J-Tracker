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
from .app import create_app, Users

# Make sure to add the .yml and .env to repository secrets in order for the CI to run these tests

# Pytest fixtures are useful tools for calling resources
# over and over, without having to manually recreate them,
# eliminating the possibility of carry-over from previous tests,
# unless defined as such.
# This fixture receives the client returned from create_app
# in app.py. add, delete
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
            "host": f"mongodb+srv://{username}:{password}@cluster0.giavamz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
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


"""
Search feature has been deprecated for this version since it was redundant. Check v3.0 docs for more details
"""
# # 2. testing if the search function running properly
# def test_search(client):
#     """
#     Tests that the search is running properly

#     :param client: mongodb client
#     """
#     rv = client.get("/search")
#     jdata = json.loads(rv.data.decode("utf-8"))["label"]
#     assert jdata == "successful test search"


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


# Testing logging out does not return error
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


# 10 New Backend Tests

# 1. Test user signup functionality
def test_signup(client):
    """
    Tests the user signup endpoint
    
    :param client: mongodb client
    """
    # Data for a new user
    data = {
        "username": "newTestUser",
        "password": "testPassword",
        "fullName": "Test User"
    }
    
    rv = client.post("/users/signup", json=data)
    assert rv.status_code == 200
    result = json.loads(rv.data.decode("utf-8"))
    assert "id" in result
    assert result["fullName"] == "Test User"
    assert result["username"] == "newTestUser"
    
    # Try to create the same user again (should fail)
    rv = client.post("/users/signup", json=data)
    assert rv.status_code == 400
    result = json.loads(rv.data.decode("utf-8"))
    assert "error" in result
    assert result["error"] == "Username already exists"


# 2. Test login with invalid credentials
def test_login_invalid_credentials(client):
    """
    Tests login with invalid credentials
    
    :param client: mongodb client
    """
    data = {"username": "testUser", "password": "wrongPassword"}
    rv = client.post("/users/login", json=data)
    assert rv.status_code == 400
    result = json.loads(rv.data.decode("utf-8"))
    assert "error" in result
    assert result["error"] == "Wrong username or password"


# 3. Test get profile data
def test_get_profile_data(client, user):
    """
    Tests the getProfile endpoint
    
    :param client: mongodb client
    :param user: the test user object
    """
    user_obj, header = user
    # Update user with profile data
    user_obj["skills"] = ["Python", "JavaScript"]
    user_obj["job_levels"] = ["Entry", "Mid"]
    user_obj["locations"] = ["US", "Remote"]
    user_obj["phone_number"] = "1234567890"
    user_obj["address"] = "Test Address"
    user_obj["institution"] = "Test University"
    user_obj["email"] = "test@example.com"
    user_obj.save()
    
    rv = client.get("/getProfile", headers=header)
    assert rv.status_code == 200
    result = json.loads(rv.data.decode("utf-8"))
    
    assert result["skills"] == ["Python", "JavaScript"]
    assert result["job_levels"] == ["Entry", "Mid"]
    assert result["locations"] == ["US", "Remote"]
    assert result["phone_number"] == "1234567890"
    assert result["address"] == "Test Address"
    assert result["institution"] == "Test University"
    assert result["email"] == "test@example.com"
    assert result["fullName"] == "fullName"


# 4. Test update profile preferences
def test_update_profile_preferences(client, user):
    """
    Tests the updateProfile endpoint
    
    :param client: mongodb client
    :param user: the test user object
    """
    user_obj, header = user
    
    # Data to update
    data = {
        "skills": ["Java", "C++", "Python"],
        "job_levels": ["Senior"],
        "locations": ["Germany", "France"]
    }
    
    rv = client.post("/updateProfile", headers=header, json=data)
    assert rv.status_code == 200
    
    # Verify the data was updated
    user_obj = user_obj._get_collection().find_one({"id": user_obj.id})
    assert user_obj["skills"] == ["Java", "C++", "Python"]
    assert user_obj["job_levels"] == ["Senior"]
    assert user_obj["locations"] == ["Germany", "France"]


# 5. Test get applications when empty
def test_get_empty_applications(client, user):
    """
    Tests that using the application GET endpoint with no applications returns empty list
    
    :param client: mongodb client
    :param user: the test user object
    """
    user_obj, header = user
    user_obj["applications"] = []
    user_obj.save()
    
    rv = client.get("/applications", headers=header)
    assert rv.status_code == 200
    result = json.loads(rv.data.decode("utf-8"))
    assert result == []


# A more complex test for applications with multiple entries
# 6. Test getting multiple applications
def test_get_multiple_applications(client, user):
    """
    Tests getting multiple applications from the endpoint
    
    :param client: mongodb client
    :param user: the test user object
    """
    user_obj, header = user
    
    # Add multiple applications
    applications = [
        {
            "id": 1,
            "jobTitle": "Software Engineer",
            "companyName": "Tech Corp",
            "date": str(datetime.date(2021, 9, 23)),
            "status": "1",
        },
        {
            "id": 2,
            "jobTitle": "Data Scientist",
            "companyName": "Data Inc",
            "date": str(datetime.date(2021, 9, 24)),
            "status": "2",
        },
        {
            "id": 3,
            "jobTitle": "DevOps Engineer",
            "companyName": "Cloud LLC",
            "date": str(datetime.date(2021, 9, 25)),
            "status": "3",
        }
    ]
    
    user_obj["applications"] = applications
    user_obj.save()
    
    rv = client.get("/applications", headers=header)
    assert rv.status_code == 200
    result = json.loads(rv.data.decode("utf-8"))
    
    assert len(result) == 3
    assert result[0]["jobTitle"] == "Software Engineer"
    assert result[1]["companyName"] == "Data Inc"
    assert result[2]["status"] == "3"


# 7. Test application update with missing fields
def test_update_application_missing_fields(client, user):
    """
    Tests that application update with missing fields returns appropriate error
    
    :param client: mongodb client
    :param user: the test user object
    """
    user_obj, header = user
    
    # Add an application to update
    application = {
        "id": 5,
        "jobTitle": "Test Engineer",
        "companyName": "Test Corp",
        "date": str(datetime.date(2021, 9, 23)),
        "status": "1",
    }
    
    user_obj["applications"] = [application]
    user_obj.save()
    
    # Try to update with empty data
    rv = client.put(
        "/applications/5", 
        headers=header, 
        json={}  # Empty data
    )
    
    assert rv.status_code == 400
    result = json.loads(rv.data.decode("utf-8"))
    assert "error" in result
    assert result["error"] == "No fields found in input"


# 8. Test deleting non-existent application
def test_delete_nonexistent_application(client, user):
    """
    Tests deleting a non-existent application returns appropriate error
    
    :param client: mongodb client
    :param user: the test user object
    """
    user_obj, header = user
    
    # Clear applications
    user_obj["applications"] = []
    user_obj.save()
    
    # Try to delete application with ID 999 (which doesn't exist)
    rv = client.delete("/applications/999", headers=header)
    
    assert rv.status_code == 400
    result = json.loads(rv.data.decode("utf-8"))
    assert "error" in result
    assert result["error"] == "Application not found"

"""
/search API endpoint has been deprecated. Removing this test from the CI pipeline 
"""
# # 9. Test search endpoint
# def test_search_functionality(client, monkeypatch):
#     """
#     Tests the search endpoint with mocked response
    
#     :param client: mongodb client
#     :param monkeypatch: pytest monkeypatch
#     """
#     # Mock the OpenAI API response
#     class MockResponse:
#         def __init__(self, status_code, json_data):
#             self.status_code = status_code
#             self.json_data = json_data
            
#         def json(self):
#             return self.json_data
    
#     mock_ai_response = {
#         "choices": [
#             {
#                 "message": {
#                     "content": '{"roleOverview": "Test overview", "technicalSkills": [{"category": "Core Skills", "tools": ["Python", "Java"]}], "softSkills": ["Communication"], "certifications": [{"name": "Test Cert", "provider": "Test Provider", "level": "Beginner"}], "industryTrends": ["Trend 1"], "salaryRange": {"entry": "$60k", "mid": "$80k", "senior": "$120k"}, "learningResources": [{"name": "Course", "type": "Online", "cost": "Free", "url": "https://example.com"}], "projectIdeas": [{"title": "Project 1", "description": "Description", "technologies": ["Tech 1"]}]}'
#                 }
#             }
#         ]
#     }
    
#     def mock_post(*args, **kwargs):
#         return MockResponse(200, mock_ai_response)
    
#     monkeypatch.setattr(requests, "post", mock_post)
    
#     # Test search endpoint
#     rv = client.get("/search?keywords=Python Developer")
    
#     assert rv.status_code == 200
#     result = json.loads(rv.data.decode("utf-8"))
    
#     assert "roleOverview" in result
#     assert "technicalSkills" in result
#     assert "softSkills" in result
#     assert "certifications" in result
#     assert "salaryRange" in result


# 10. Test resume upload with invalid data
def test_resume_upload_invalid(client, user):
    """
    Tests resume upload with invalid data returns appropriate error
    
    :param client: mongodb client
    :param user: the test user object
    """
    user_obj, header = user
    
    # Test without providing a file
    rv = client.post("/resume", headers=header, content_type="multipart/form-data")
    
    assert rv.status_code == 400
    result = json.loads(rv.data.decode("utf-8"))
    assert "error" in result
    assert result["error"] == "No resume file found in the input"
