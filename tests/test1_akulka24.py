import pytest
import os
from backend.jobsearch import get_ai_job_recommendations

@pytest.fixture(scope="module")
def api_key():
    """Ensure the API key exists, otherwise skip the test"""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        pytest.skip("❌ OPENAI_API_KEY not found in environment variables.")
    return key

def test_matching_jobs_skills_and_experience(api_key):
    """
    Test that AI returns job listings matching input skills and experience levels.
    """

    # Define test inputs
    skills = [
        {"value": "Python", "label": "Python"},
        {"value": "JavaScript", "label": "JavaScript"}
    ]
    
    job_levels = [
        {"value": "Entry-Level", "label": "Entry-Level"},
        {"value": "Junior", "label": "Junior"}
    ]
    
    locations = [
        {"value": "Remote", "label": "Remote"}
    ]

    try:
        # Fetch AI job recommendations
        jobs = get_ai_job_recommendations(skills, job_levels, locations)

        # Ensure a valid response
        assert isinstance(jobs, list), "❌ Response should be a list."
        assert len(jobs) > 0, "❌ AI should return at least one job."

        # Verify each job matches input criteria
        for job in jobs:
            print(f"\n✅ Checking job: {job.get('jobTitle', 'Unknown')}")

            # Ensure job contains necessary fields
            required_fields = ["jobTitle", "requiredSkills", "experienceLevel", "location"]
            for field in required_fields:
                assert field in job, f"❌ Job is missing required field: {field}"

            # Check if job requires at least one of the input skills
            job_skills = set(job["requiredSkills"])
            input_skills = {skill["value"] for skill in skills}
            assert job_skills.intersection(input_skills), \
                f"❌ Job {job['jobTitle']} should require at least one input skill."

            # Check if experience level matches
            assert job["experienceLevel"] in {lvl["value"] for lvl in job_levels}, \
                f"❌ Job {job['jobTitle']} experience level does not match input levels."

            # Check if location matches
            assert job["location"] in [loc["value"] for loc in locations], \
                f"❌ Job {job['jobTitle']} location does not match input locations."

    except Exception as e:
        pytest.fail(f"❌ API call failed with error: {str(e)}")

if __name__ == "__main__":
    pytest.main(["-v", "-s"])
