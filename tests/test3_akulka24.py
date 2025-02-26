import os
import pytest
from pymongo import MongoClient

@pytest.fixture(scope="module")
def mongodb_client():
    """Fixture to create and return a MongoDB client."""
    uri = os.getenv("MONGODB_URI")  # Fetch MongoDB URI from GitHub Secrets
    if not uri:
        pytest.fail("❌ MONGODB_URI is not set in the environment variables.")

    try:
        client = MongoClient(uri)
        # Test the connection
        client.admin.command('ping')
        yield client  # Provide the MongoDB client to the test
    finally:
        client.close()

def test_mongodb_connection(mongodb_client):
    """Test that we can connect to MongoDB and access collections."""
    db = mongodb_client['jobtracker']  # Ensure this matches your DB name
    collections = db.list_collection_names()

    assert isinstance(collections, list), "❌ MongoDB did not return a list of collections."
    print(f"✅ Available collections: {collections}")

def test_insert_and_retrieve_job_application(mongodb_client):
    """Test inserting and retrieving a job application."""
    db = mongodb_client['jobtracker']
    job_collection = db['applications']

    # Insert a test job application
    test_job = {
        "jobTitle": "Software Engineer",
        "companyName": "TechCorp",
        "location": "Remote",
        "status": "Applied"
    }
    inserted_job = job_collection.insert_one(test_job)

    # Retrieve the inserted job
    retrieved_job = job_collection.find_one({"_id": inserted_job.inserted_id})

    assert retrieved_job is not None, "❌ Job application was not retrieved."
    assert retrieved_job["jobTitle"] == "Software Engineer", "❌ Job title does not match."
    assert retrieved_job["companyName"] == "TechCorp", "❌ Company name does not match."
    assert retrieved_job["location"] == "Remote", "❌ Location does not match."
    assert retrieved_job["status"] == "Applied", "❌ Status does not match."

    print("✅ Job application successfully inserted and retrieved.")

    # Cleanup: Remove test data
    job_collection.delete_one({"_id": inserted_job.inserted_id})

def test_invalid_mongodb_uri():
    """Test MongoDB connection with an invalid URI."""
    with pytest.raises(Exception):
        client = MongoClient("mongodb://invalid_uri")
        client.admin.command('ping')  # This should fail
        client.close()
