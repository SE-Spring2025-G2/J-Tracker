"""
THIS TEST HAS BEEN DEPRECATED DUE TO REMOVAL OF ALL OPENAI APIs. Refer to latest GEMINI BASED FEATURE DOCUMENTATION FOR MORE DETAILS
"""
# import pytest
# import os
# from backend.jobsearch import get_ai_job_recommendations

# def test_ai_job_recommendations_response():
#     """Test that AI job recommendation API returns a list of job results."""

#     # Ensure API Key is set
#     api_key = os.getenv("OPENAI_API_KEY")
#     if not api_key:
#         pytest.skip("❌ OPENAI_API_KEY not found in environment variables.")

#     # Dummy test input
#     skills = [{"value": "Python", "label": "Python"}]
#     job_levels = [{"value": "Entry-Level", "label": "Entry-Level"}]
#     locations = [{"value": "Remote", "label": "Remote"}]

#     # Call the function
#     jobs = get_ai_job_recommendations(skills, job_levels, locations)

#     # Assertions
#     assert isinstance(jobs, list), "❌ API response should be a list."
#     print("✅ AI job recommendation API returned a valid list.")

# if __name__ == "__main__":
#     pytest.main(["-v", "-s"])
