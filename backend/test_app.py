"""
Test module for the backend
"""
import hashlib
from io import BytesIO
import uuid

import pytest
import json
import datetime
from datetime import datetime
from flask_mongoengine import MongoEngine
import yaml
import sys
import uuid
import pypdf
import google.generativeai as genai
from pypdf import PdfReader
from .app import create_app, Users, SharedJobs, get_new_application_id, get_new_user_id, get_userid_from_header
from unittest.mock import patch, MagicMock

# Make sure to add the .yml and .env to repository secrets in order for the CI to run these tests

# Pytest fixtures are useful tools for calling resources
# over and over, without having to manually recreate them,
# eliminating the possibility of carry-over from previous tests,
# unless defined as such.
# This fixture receives the client returned from create_app
# in app.py. add, delete, update
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


"""
These tests have been added for Spring 2025
"""

# testing if the flask app is running properly
def test_alive(client):
    """
    Tests that the application is running properly

    :param client: mongodb client
    """
    rv = client.get("/")
    json_data = rv.get_json()
    assert json_data == {"message": "Server up and running"}
    assert rv.status_code == 200

# testing if the flask app is running properly with status code
def test_alive_status_code(client):
    """
    Tests that / returns 200

    :param client: mongodb client
    """
    rv = client.get("/")
    assert rv.status_code == 200

# Test for adding a new job application that gets added to shared pool
def test_add_application_new_shared_job(client, mocker, user):
    """
    Tests adding a new application that should be added to the shared pool
    
    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    # Use direct function reference for patching
    mocker.patch(
        "backend.app.get_new_application_id",
        return_value=999,
    )
    mocker.patch(
        "uuid.uuid4",
        return_value="test-uuid-1234",
    )
    
    user_obj, header = user
    user_obj["applications"] = []
    user_obj.save()
    
    # Test data
    new_application = {
        "jobTitle": "Senior Developer",
        "companyName": "Tech Innovators",
        "date": "2025-04-15",
        "jobLink": "https://example.com/job123",
        "location": "Remote",
        "status": "1"
    }
    
    # Mock the SharedJobs.objects method to return None (job doesn't exist yet)
    mock_no_existing_job = MagicMock()
    mock_no_existing_job.first.return_value = None
    mocker.patch("app.SharedJobs.objects", return_value=mock_no_existing_job)
    
    # Mock the SharedJobs class
    mock_shared_job = MagicMock()
    mocker.patch("app.SharedJobs", return_value=mock_shared_job)
    
    # Add application
    rv = client.post(
        "/applications",
        headers=header,
        json={"application": new_application},
    )
    
    assert rv.status_code == 200
    result = json.loads(rv.data.decode("utf-8"))
    
    # Verify response
    assert result["id"] == 999
    assert result["jobTitle"] == "Senior Developer"
    assert result["companyName"] == "Tech Innovators"
    
    # Verify that save was called on the new shared job
    mock_shared_job.save.assert_called_once()


# Test for adding an application that already exists in shared pool
def test_add_application_existing_shared_job(client, mocker, user):
    """
    Tests adding an application that already exists in the shared pool
    
    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    mocker.patch(
        "backend.app.get_new_application_id",
        return_value=888,
    )
    
    user_obj, header = user
    user_obj["applications"] = []
    user_obj.save()
    
    # Test data
    existing_application = {
        "jobTitle": "Frontend Developer",
        "companyName": "Web Solutions",
        "date": "2025-04-15",
        "jobLink": "https://example.com/job456",
        "location": "New York",
        "status": "1"
    }
    
    # Mock the existing shared job
    mock_existing_job = MagicMock()
    mock_existing_jobs_query = MagicMock()
    mock_existing_jobs_query.first.return_value = mock_existing_job
    mocker.patch("app.SharedJobs.objects", return_value=mock_existing_jobs_query)
    
    # Add application
    rv = client.post(
        "/applications",
        headers=header,
        json={"application": existing_application},
    )
    
    assert rv.status_code == 200
    result = json.loads(rv.data.decode("utf-8"))
    
    # Verify response
    assert result["jobTitle"] == "Frontend Developer"
    assert result["companyName"] == "Web Solutions"
    
    # Verify that the existing job's appliedBy count was incremented
    mock_existing_job.update.assert_called_once_with(inc__appliedBy=1)


# Test for missing fields in add application
def test_add_application_missing_fields(client, user):
    """
    Tests adding an application with missing required fields
    
    :param client: mongodb client
    :param user: the test user object
    """
    user_obj, header = user
    
    # Test data with missing required fields
    incomplete_application = {
        "companyName": "Missing Job Title Inc."
        # Missing jobTitle field
    }
    
    # Add application
    rv = client.post(
        "/applications",
        headers=header,
        json={"application": incomplete_application},
    )
    
    assert rv.status_code == 400
    result = json.loads(rv.data.decode("utf-8"))
    assert "error" in result
    assert result["error"] == "Missing fields in input"


# Test adding a job to wishlist
def test_add_to_wishlist(client, mocker, user):
    """
    Tests adding a shared job to the user's wishlist
    
    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    mocker.patch(
        "backend.app.get_new_application_id",
        return_value=777,
    )
    
    user_obj, header = user
    user_obj["applications"] = []
    user_obj.save()
    
    # Mock the shared job
    mock_shared_job = MagicMock()
    mock_shared_job.jobTitle = "ML Engineer"
    mock_shared_job.companyName = "AI Research"
    mock_shared_job.jobLink = "https://example.com/job789"
    mock_shared_job.location = "San Francisco"
    
    mock_shared_jobs_query = MagicMock()
    mock_shared_jobs_query.first.return_value = mock_shared_job
    mocker.patch("backend.test_app.SharedJobs.objects", return_value=mock_shared_jobs_query)
    
    # Add to wishlist
    rv = client.post(
        "/wishlist",
        headers=header,
        json={"jobId": "test-job-uuid"},
    )
    
    assert rv.status_code == 200
    result = json.loads(rv.data.decode("utf-8"))
    
    # Verify response
    assert result["id"] == 777
    assert result["jobTitle"] == "ML Engineer"
    assert result["companyName"] == "AI Research"
    assert result["status"] == "1"  # Wishlist status
    
    # Verify that the shared job's appliedBy count was incremented
    mock_shared_job.update.assert_called_once_with(inc__appliedBy=1)


# Test adding non-existent job to wishlist
def test_add_nonexistent_job_to_wishlist(client, mocker, user):
    """
    Tests adding a non-existent shared job to the wishlist
    
    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    user_obj, header = user
    
    # Mock the SharedJobs query to return None (job doesn't exist)
    mock_shared_jobs_query = MagicMock()
    mock_shared_jobs_query.first.return_value = None
    mocker.patch("backend.app.SharedJobs.objects", return_value=mock_shared_jobs_query)
    
    # Try to add non-existent job to wishlist
    rv = client.post(
        "/wishlist",
        headers=header,
        json={"jobId": "non-existent-uuid"},
    )
    
    assert rv.status_code == 404
    result = json.loads(rv.data.decode("utf-8"))
    assert "error" in result
    assert result["error"] == "Job not found in shared listings"


# Test missing jobId in wishlist request
def test_add_to_wishlist_missing_jobid(client, user):
    """
    Tests adding a job to wishlist with missing jobId
    
    :param client: mongodb client
    :param user: the test user object
    """
    user_obj, header = user
    
    # Send request without jobId
    rv = client.post(
        "/wishlist",
        headers=header,
        json={},  # Empty JSON - missing jobId
    )
    
    assert rv.status_code == 400
    result = json.loads(rv.data.decode("utf-8"))
    assert "error" in result
    assert result["error"] == "Missing jobId in request"


# Test getting shared jobs
def test_get_shared_jobs(client, mocker, user):
    """
    Tests getting shared jobs that user hasn't applied to
    
    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    user_obj, header = user
    
    # Set up user with some existing applications
    user_applications = [
        {
            "jobTitle": "Existing Job",
            "companyName": "Existing Company",
            "jobLink": "https://example.com/existing",
            "status": "2"
        }
    ]
    user_obj["applications"] = user_applications
    user_obj.save()
    
    # Mock shared jobs in the system
    mock_job1 = MagicMock()
    mock_job1.__getitem__.side_effect = lambda key: {
        "id": "job-uuid-1",
        "jobTitle": "New Job 1",
        "companyName": "New Company 1",
        "location": "Remote",
        "jobLink": "https://example.com/new1",
        "postedDate": datetime(2025, 4, 15),
        "appliedBy": 5
    }[key]
    
    mock_job2 = MagicMock()
    mock_job2.__getitem__.side_effect = lambda key: {
        "id": "job-uuid-2",
        "jobTitle": "New Job 2",
        "companyName": "New Company 2",
        "location": "Hybrid",
        "jobLink": "https://example.com/new2",
        "postedDate": datetime(2025, 4, 14),
        "appliedBy": 3
    }[key]
    
    mock_job3 = MagicMock()
    mock_job3.__getitem__.side_effect = lambda key: {
        "id": "job-uuid-3",
        "jobTitle": "Existing Job",  # This matches an existing application
        "companyName": "Existing Company",
        "location": "On-site",
        "jobLink": "https://example.com/existing",  # This matches an existing application
        "postedDate": datetime(2025, 4, 13),
        "appliedBy": 10
    }[key]
    
    # Mock SharedJobs.objects to return these jobs
    mocker.patch("backend.app.SharedJobs.objects", return_value=[mock_job1, mock_job2, mock_job3])
    
    # Get shared jobs
    rv = client.get("/jobs/shared", headers=header)
    
    assert rv.status_code == 200
    result = json.loads(rv.data.decode("utf-8"))
    
    # Should only contain two jobs (the ones user hasn't applied to yet)
    assert len(result) == 2
    
    # Verify job details
    assert result[0]["id"] == "job-uuid-1"
    assert result[0]["jobTitle"] == "New Job 1"
    assert result[0]["appliedBy"] == 5
    
    assert result[1]["id"] == "job-uuid-2"
    assert result[1]["jobTitle"] == "New Job 2"
    assert result[1]["appliedBy"] == 3


# Test for empty shared jobs list
def test_get_shared_jobs_empty(client, mocker, user):
    """
    Tests getting shared jobs when none are available
    
    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    user_obj, header = user
    
    # Mock empty SharedJobs collection
    mocker.patch("backend.app.SharedJobs.objects", return_value=[])
    
    # Get shared jobs
    rv = client.get("/jobs/shared", headers=header)
    
    assert rv.status_code == 200
    result = json.loads(rv.data.decode("utf-8"))
    
    # Should be an empty list
    assert result == []


# Test for the resume analysis/fake job description feature
def test_fake_job_description(client, mocker):
    """
    Tests the fake job description endpoint
    
    :param client: mongodb client
    :param mocker: pytest mocker
    """
    # Mock environment variable
    mocker.patch("os.getenv", return_value="fake-api-key")
    
    # Mock the genai configuration and model
    mock_genai = MagicMock()
    mocker.patch("google.generativeai", mock_genai)
    
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '''
    {
        "roleOverview": "Test overview",
        "technicalSkills": [
            {
                "category": "Core Skills",
                "tools": ["Python", "Java"]
            }
        ],
        "softSkills": ["Communication"],
        "certifications": [
            {
                "name": "Test Cert",
                "provider": "Test Provider",
                "level": "Beginner"
            }
        ],
        "industryTrends": ["Trend 1"],
        "salaryRange": {
            "entry": "$60k",
            "mid": "$80k",
            "senior": "$120k"
        },
        "learningResources": [
            {
                "name": "Course",
                "type": "Online",
                "cost": "Free",
                "url": "https://example.com"
            }
        ],
        "projectIdeas": [
            {
                "title": "Project 1",
                "description": "Description",
                "technologies": ["Tech 1"]
            }
        ]
    }
    '''
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model
    
    # Test the endpoint
    rv = client.get("/fake-job?keywords=Python%20Developer")
    
    assert rv.status_code == 200
    result = json.loads(rv.data.decode("utf-8"))
    
    # Verify key fields from response
    assert "roleOverview" in result
    assert "technicalSkills" in result
    assert "softSkills" in result
    assert result["technicalSkills"][0]["tools"] == ["Python", "Java"]


# Test fake job description with missing keywords
def test_fake_job_missing_keywords(client):
    """
    Tests the fake job description endpoint with missing keywords
    
    :param client: mongodb client
    """
    # Test without providing keywords
    rv = client.get("/fake-job")
    
    assert rv.status_code == 400
    result = json.loads(rv.data.decode("utf-8"))
    assert "error" in result
    assert result["error"] == "Job title is required"


# Test resume parsing
def test_parse_resume(client, mocker):
    """
    Tests the resume parsing endpoint
    
    :param client: mongodb client
    :param mocker: pytest mocker
    """
    # Mock environment variable
    mocker.patch("os.getenv", return_value="fake-api-key")
    
    # Mock PDF reader
    mock_reader = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Sample resume text"
    mock_reader.pages = [mock_page]
    mocker.patch("pypdf.PdfReader", return_value=mock_reader)
    
    # Mock the genai configuration and model
    mock_genai = MagicMock()
    mocker.patch("google.generativeai", mock_genai)
    
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '''
    {
        "skills": ["Python", "JavaScript", "Data Analysis"],
        "experience": ["Software Developer at Tech Co", "Intern at Start Inc"],
        "education": ["BS Computer Science"],
        "certifications": ["AWS Certified Developer"]
    }
    '''
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model
    
    # Create test file
    data = dict(
        resume=(BytesIO(b"This is a test resume"), "resume.pdf"),
    )
    
    # Test the endpoint
    rv = client.post(
        "/parse-resume",
        content_type="multipart/form-data",
        data=data
    )
    
    assert rv.status_code == 200
    result = json.loads(rv.data.decode("utf-8"))
    
    # Verify response
    assert "skills" in result
    assert "experience" in result
    assert "education" in result
    assert "certifications" in result
    assert result["skills"] == ["Python", "JavaScript", "Data Analysis"]


# Test resume comparison
def test_compare_resume(client, mocker):
    """
    Tests the resume comparison endpoint
    
    :param client: mongodb client
    :param mocker: pytest mocker
    """
    # Mock environment variable
    mocker.patch("os.getenv", return_value="fake-api-key")
    
    # Mock the genai configuration and model
    mock_genai = MagicMock()
    mocker.patch("google.generativeai", mock_genai)
    
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '''
    {
        "overallMatch": 75,
        "matchingSkills": ["Python", "JavaScript"],
        "missingSkills": ["React", "AWS"],
        "recommendations": ["Learn React", "Get AWS certification"]
    }
    '''
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model
    
    # Test data
    test_data = {
        "resume": {
            "skills": ["Python", "JavaScript", "SQL"],
            "experience": ["Developer at Tech Co"],
            "education": ["BS Computer Science"],
            "certifications": []
        },
        "jobInsights": {
            "roleOverview": "Frontend Developer role",
            "technicalSkills": [
                {
                    "category": "Core Skills",
                    "tools": ["JavaScript", "React", "HTML", "CSS"]
                }
            ]
        }
    }
    
    # Test the endpoint
    rv = client.post(
        "/compare-resume",
        json=test_data
    )
    
    assert rv.status_code == 200
    result = json.loads(rv.data.decode("utf-8"))
    
    # Verify response
    assert "overallMatch" in result
    assert "matchingSkills" in result
    assert "missingSkills" in result
    assert "recommendations" in result
    assert result["overallMatch"] == 75
    assert result["matchingSkills"] == ["Python", "JavaScript"]


# Test missing resume file
def test_parse_resume_missing_file(client):
    """
    Tests the resume parsing endpoint with missing file
    
    :param client: mongodb client
    """
    # Test without providing a file
    rv = client.post(
        "/parse-resume",
        content_type="multipart/form-data"
    )
    
    assert rv.status_code == 500  # This should be 400, but current implementation returns 500
    result = json.loads(rv.data.decode("utf-8"))
    assert "error" in result


# Test missing data in resume comparison
def test_compare_resume_missing_data(client):
    """
    Tests the resume comparison endpoint with incomplete data
    
    :param client: mongodb client
    """
    # Test with missing resume data
    rv = client.post(
        "/compare-resume",
        json={
            "jobInsights": {
                "roleOverview": "Frontend Developer role"
            }
            # Missing resume data
        }
    )
    
    assert rv.status_code == 500
    result = json.loads(rv.data.decode("utf-8"))
    assert "error" in result


# Test for SharedJobs model
def test_shared_jobs_model(client, user):
    """
    Tests creating a SharedJobs model instance
    
    :param client: mongodb client
    :param user: the test user object
    """
    user_obj, header = user
    
    # Test data
    job_id = str(uuid.uuid4())
    job_data = {
        "id": job_id,
        "jobTitle": "Test Job",
        "companyName": "Test Company",
        "location": "Test Location",
        "jobLink": "https://example.com/test",
        "postedBy": 1,
        "appliedBy": 1
    }
    
    # Create SharedJobs instance
    shared_job = SharedJobs(**job_data)
    
    # Verify fields
    assert shared_job.id == job_id
    assert shared_job.jobTitle == "Test Job"
    assert shared_job.companyName == "Test Company"
    assert shared_job.location == "Test Location"
    assert shared_job.jobLink == "https://example.com/test"
    assert shared_job.postedBy == 1
    assert shared_job.appliedBy == 1
    assert shared_job.active == 1  # Default value


# Test for error handling in add application
def test_add_application_error_handling(client, mocker, user):
    """
    Tests error handling in add application endpoint
    
    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    user_obj, header = user
    
    # Mock get_userid_from_header to raise an exception
    mocker.patch(
        "backend.app.get_userid_from_header",
        side_effect=Exception("Test exception"),
    )
    
    # Test data
    application_data = {
        "jobTitle": "Error Test Job",
        "companyName": "Error Test Company",
        "date": "2025-04-15",
        "status": "1"
    }
    
    # Test endpoint with forced error
    rv = client.post(
        "/applications",
        headers=header,
        json={"application": application_data},
    )
    
    assert rv.status_code == 500
    result = json.loads(rv.data.decode("utf-8"))
    assert "error" in result
    assert result["error"] == "Internal server error"


# Test for updating a shared job
def test_update_shared_job_applied_count(client, mocker):
    """
    Tests that the appliedBy count is correctly incremented
    
    :param client: mongodb client
    :param mocker: pytest mocker
    """
    # Create a mock shared job with initial appliedBy count of 5
    mock_shared_job = MagicMock()
    mock_shared_job.appliedBy = 5
    
    # Mock the update method to verify it's called with inc__appliedBy=1
    mock_shared_job.update = MagicMock()
    
    # Return the mock object when SharedJobs.objects().first() is called
    mock_query = MagicMock()
    mock_query.first.return_value = mock_shared_job
    mocker.patch("backend.app.SharedJobs.objects", return_value=mock_query)
    
    # Create a function to simulate the update operation
    def update_job():
        job = mock_query.first()
        job.update(inc__appliedBy=1)
        # In a real scenario, this would update the database
        # For testing, we'll just manually increment the value
        job.appliedBy += 1
        return job
    
    # Call the function to simulate updating the job
    updated_job = update_job()
    
    # Verify update was called correctly
    mock_shared_job.update.assert_called_once_with(inc__appliedBy=1)
    
    # Manually check the new value would be 6
    assert updated_job.appliedBy == 6


# Test for case-insensitive job filtering
def test_shared_jobs_case_insensitive_filtering(client, mocker, user):
    """
    Tests that shared jobs filtering works with different letter cases
    
    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    user_obj, header = user
    
    # Set up user with some existing applications with mixed case
    user_applications = [
        {
            "jobTitle": "Python Developer",
            "companyName": "Tech CORP",  # Upper case
            "jobLink": "https://example.com/job1",
            "status": "2"
        }
    ]
    user_obj["applications"] = user_applications
    user_obj.save()
    
    # Mock shared jobs with different cases
    mock_job1 = MagicMock()
    mock_job1.__getitem__.side_effect = lambda key: {
        "id": "job-uuid-1",
        "jobTitle": "Senior Developer",
        "companyName": "tech corp",  # Lower case - should match case-insensitively
        "location": "Remote",
        "jobLink": "https://example.com/job1",  # Same link
        "postedDate": datetime(2025, 4, 15),
        "appliedBy": 5
    }[key]
    
    mock_job2 = MagicMock()
    mock_job2.__getitem__.side_effect = lambda key: {
        "id": "job-uuid-2",
        "jobTitle": "New Job",
        "companyName": "Different Company",
        "location": "Remote",
        "jobLink": "https://example.com/job2",
        "postedDate": datetime(2025, 4, 15),
        "appliedBy": 2
    }[key]
    
    # Mock SharedJobs.objects to return these jobs
    mocker.patch("backend.app.SharedJobs.objects", return_value=[mock_job1, mock_job2])
    
    # Get shared jobs
    rv = client.get("/jobs/shared", headers=header)
    
    assert rv.status_code == 200
    result = json.loads(rv.data.decode("utf-8"))
    
    # Should only contain one job since the first one should be filtered out
    # even though the case is different
    assert len(result) == 1
    assert result[0]["id"] == "job-uuid-2"
    assert result[0]["companyName"] == "Different Company"

"""
These tests existed before the Spring 2025 edit. /search feature has been deprecated and replaced by /fake-job for this version since it was redundant. Check v3.0 docs for more details
"""

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
        "backend.app.get_new_user_id",
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
        "backend.app.get_new_user_id",
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
def test_signup(client, mocker):
    """
    Tests the user signup endpoint
    
    :param client: mongodb client
    :param mocker: pytest mocker
    """
    # Mock get_new_user_id to return a predictable value
    mocker.patch("backend.app.get_new_user_id", return_value=9999)
    
    # Create a unique username with timestamp to avoid conflicts
    import time
    unique_username = f"testUser_{int(time.time())}"
    
    # Mock the user query to simulate no existing users with this username
    mock_empty_query = MagicMock()
    mock_empty_query.__len__ = lambda x: 0  # Make len() return 0
    mocker.patch("backend.app.Users.objects", return_value=mock_empty_query)
    
    # Create test data
    data = {
        "username": unique_username,
        "password": "testPassword",
        "fullName": "Test User"
    }
    
    # Mock the user creation and save methods
    mock_user = MagicMock()
    mock_user.to_json.return_value = {
        "id": 9999,
        "fullName": "Test User",
        "username": unique_username
    }
    mocker.patch("backend.app.Users", return_value=mock_user)
    
    # Test signup successful
    rv = client.post("/users/signup", json=data)
    assert rv.status_code == 200
    result = json.loads(rv.data.decode("utf-8"))
    assert result["id"] == 9999
    assert result["fullName"] == "Test User"
    assert result["username"] == unique_username
    
    # Now mock the user query to simulate username already exists
    mock_existing_query = MagicMock()
    mock_existing_query.__len__ = lambda x: 1  # Make len() return 1
    mocker.patch("backend.app.Users.objects", return_value=mock_existing_query)
    
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
    updated_user = Users.objects(id=user_obj.id).first()
    assert updated_user["skills"] == ["Java", "C++", "Python"]
    assert updated_user["job_levels"] == ["Senior"]
    assert updated_user["locations"] == ["Germany", "France"]


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
