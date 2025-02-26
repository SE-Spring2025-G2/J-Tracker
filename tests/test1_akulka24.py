import pytest
import os
from backend.jobsearch import get_ai_job_recommendations

def test_matching_jobs_skills_and_experience():
    """
    Test that AI returns job listings matching input skills and experience levels
    """
    # Verify API key is available
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        pytest.skip("OPENAI_API_KEY not found in environment variables")

    # Test input data
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
        # Get job recommendations
        jobs = get_ai_job_recommendations(skills, job_levels, locations)

        # Print debug information
        print(f"\nReceived {len(jobs)} jobs from API")
        
        # Assertions
        assert isinstance(jobs, list), "Response should be a list"
        assert len(jobs) > 0, "Should return at least one job"

        # Check each job matches requirements
        for job in jobs:
            print(f"\nChecking job: {job}")
            
            # Verify job has required fields
            assert "jobTitle" in job, "Job should have a title"
            assert "requiredSkills" in job, "Job should have required skills"
            assert "experienceLevel" in job, "Job should have experience level"
            
            # Check if job requires at least one of the input skills
            job_skills = set(job["requiredSkills"])
            input_skills = {skill["value"] for skill in skills}
            matching_skills = job_skills.intersection(input_skills)
            assert matching_skills, \
                f"Job {job['jobTitle']} should require at least one of the input skills"
            
            # Check if experience level matches
            job_level = job["experienceLevel"]
            input_levels = {level["value"] for level in job_levels}
            assert job_level in input_levels, \
                f"Job {job['jobTitle']} experience level should match input levels"

            # Check location
            assert job["location"] in [loc["value"] for loc in locations], \
                f"Job {job['jobTitle']} location should match input locations"

    except Exception as e:
        print(f"\nError during test execution: {str(e)}")
        raise

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])