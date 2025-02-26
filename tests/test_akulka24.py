import pytest
import os
import json
import unittest
import hashlib
from pymongo import MongoClient
from backend.app import create_app  # Import the Flask app
from backend.jobsearch import get_ai_job_recommendations

# ------------------------ TEST 1: AI Job Recommendations ------------------------
def test_matching_jobs_skills_and_experience():
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        pytest.skip("OPENAI_API_KEY not found in environment variables")

    skills = [{"value": "Python", "label": "Python"}, {"value": "JavaScript", "label": "JavaScript"}]
    job_levels = [{"value": "Entry-Level", "label": "Entry-Level"}, {"value": "Junior", "label": "Junior"}]
    locations = [{"value": "Remote", "label": "Remote"}]

    jobs = get_ai_job_recommendations(skills, job_levels, locations)
    assert isinstance(jobs, list), "Response should be a list"
    assert len(jobs) > 0, "Should return at least one job"
    
    for job in jobs:
        assert "jobTitle" in job
        assert "requiredSkills" in job
        assert "experienceLevel" in job
        assert "location" in job

# ------------------------ TEST 2: Password Hashing ------------------------
class TestPasswordHashing(unittest.TestCase):
    def hash_password(self, password):
        return hashlib.md5(password.encode()).hexdigest()

    def test_password_hashing(self):
        password = "hi"
        expected_hash = "49f68a5c8493ec2c0bf489821c21fc3b"
        self.assertEqual(self.hash_password(password), expected_hash)

# ------------------------ TEST 3: MongoDB Connection ------------------------
@pytest.fixture(scope="module")
def mongodb_client():
    uri = os.getenv("MONGODB_URI")
    if not uri:
        pytest.fail("MONGODB_URI is not set in environment variables.")

    client = MongoClient(uri)
    client.admin.command('ping')
    yield client
    client.close()

def test_mongodb_connection(mongodb_client):
    db = mongodb_client['jobtracker']
    collections = db.list_collection_names()
    assert isinstance(collections, list)

# ------------------------ TEST 4: User Login ------------------------
@pytest.fixture(scope="module")
def test_client():
    app = create_app()
    return app.test_client()

def test_login_fail_wrong_password(test_client):
    login_data = {"username": "valid_user", "password": "wrong_password"}
    response = test_client.post("/users/login", data=json.dumps(login_data), content_type="application/json")
    assert response.status_code in [400, 401]
    response_data = json.loads(response.data)
    assert "error" in response_data

# ------------------------ TEST 5: AI Job Recommendations API ------------------------
def test_ai_job_recommendations_response():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not found in environment variables.")
    skills = [{"value": "Python", "label": "Python"}]
    job_levels = [{"value": "Entry-Level", "label": "Entry-Level"}]
    locations = [{"value": "Remote", "label": "Remote"}]
    jobs = get_ai_job_recommendations(skills, job_levels, locations)
    assert isinstance(jobs, list)

# ------------------------ TEST 6: API Key Validation ------------------------
def test_api_key_exists():
    api_key = os.getenv("OPENAI_API_KEY")
    assert api_key is not None

if __name__ == "__main__":
    pytest.main(["-v", "-s"])

