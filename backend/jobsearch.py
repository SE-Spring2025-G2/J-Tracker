import requests
import json
import os
from datetime import datetime

def get_ai_job_recommendations(skills, job_levels, locations):
    """
    Get AI-powered job recommendations using a structured prompt
    """
    try:
        # Format the user preferences for the prompt
        skills_str = ", ".join([skill["value"] for skill in skills])
        levels_str = ", ".join([level["value"] for level in job_levels])
        locations_str = ", ".join([loc["value"] for loc in locations])

        # Create a structured prompt for the AI
        prompt = f"""
        Create 5 realistic job postings as a JSON array. Each job should be a JSON object with these exact keys:
        "Job Title", "Company Name", "Location", "Brief Job Description", "Required Skills", "Experience Level", "application URL"

        Use these requirements:
        Skills: {skills_str}
        Experience Level: {levels_str}
        Locations: {locations_str}

        Ensure the response is valid JSON format and each job matches the candidate's skills and experience level.
        """

        headers = {
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a job matching assistant that creates realistic job recommendations. Always respond with valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "response_format": { "type": "json_object" }  # Force JSON response
        }

        print("Sending request to OpenAI API...")
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )

        print(f"API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            # Parse the AI response
            ai_response = response.json()
            print("Raw API Response:", json.dumps(ai_response, indent=2))
            
            try:
                # Extract the content from the API response
                content = ai_response['choices'][0]['message']['content']
                print("Content from API:", content)
                
                # Parse the content as JSON
                job_listings = json.loads(content)
                print("Parsed job listings:", json.dumps(job_listings, indent=2))
                
                # Format the jobs for your application
                formatted_jobs = []
                for job in job_listings['jobs']:  # Assuming the response has a 'jobs' array
                    formatted_job = {
                        "jobTitle": job["Job Title"],
                        "companyName": job["Company Name"],
                        "location": job["Location"],
                        "description": job["Brief Job Description"],
                        "requiredSkills": job["Required Skills"],
                        "experienceLevel": job["Experience Level"],
                        "data_share_url": job["application URL"]
                    }
                    formatted_jobs.append(formatted_job)

                # Save the results for debugging
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                with open(f"ai_job_results_{timestamp}.json", "w") as f:
                    json.dump(formatted_jobs, f, indent=2)
                
                print(f"Successfully formatted {len(formatted_jobs)} jobs")
                return formatted_jobs

            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {str(e)}")
                print("Content that failed to parse:", content)
                return []
            except KeyError as e:
                print(f"Key error while processing response: {str(e)}")
                return []

        else:
            print(f"Error from OpenAI API: {response.status_code}")
            print("Error response:", response.text)
            return []

    except Exception as e:
        print(f"Error in AI job matching: {str(e)}")
        print("Full error details:", e.__class__.__name__)
        return []

# Example usage
if __name__ == "__main__":
    # Test data
    test_skills = [
        {"value": "Software Development", "label": "Software Development"},
        {"value": "Python", "label": "Python"},
        {"value": "Data Analysis", "label": "Data Analysis"}
    ]
    
    test_levels = [
        {"value": "Entry-Level", "label": "Entry-Level"},
        {"value": "Junior", "label": "Junior"}
    ]
    
    test_locations = [
        {"value": "United States of America", "label": "United States of America"}
    ]

    print("\nStarting job recommendation test...")
    print(f"Skills: {[s['value'] for s in test_skills]}")
    print(f"Levels: {[l['value'] for l in test_levels]}")
    print(f"Locations: {[l['value'] for l in test_locations]}")
    
    jobs = get_ai_job_recommendations(test_skills, test_levels, test_locations)
    
    print("\nAI Generated Job Recommendations:")
    if jobs:
        for job in jobs:
            print("\n" + "="*50)
            print(f"Title: {job['jobTitle']}")
            print(f"Company: {job['companyName']}")
            print(f"Location: {job['location']}")
            print(f"Description: {job['description']}")
            print(f"Required Skills: {job['requiredSkills']}")
            print(f"Experience Level: {job['experienceLevel']}")
            print(f"Apply at: {job['data_share_url']}")
    else:
        print("No jobs were generated.")