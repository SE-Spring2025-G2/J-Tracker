"""
The flask application for our program
"""
# importing required python libraries
import json
from datetime import datetime, timedelta
import hashlib
import uuid
import random
from flask import Flask, jsonify, request, send_file, redirect, url_for, session
from flask_mongoengine import MongoEngine
from flask_cors import CORS, cross_origin

from bs4 import BeautifulSoup
import os
from fake_useragent import UserAgent
import pandas as pd
# from .jobsearch import get_ai_job_recommendations
from pypdf import PdfReader
import google.generativeai as genai
import yaml
import re
import requests

from authlib.integrations.flask_client import OAuth
from authlib.common.security import generate_token

# need to add all endpoints to this list in order to place auth checks
existing_endpoints = ["/applications", "/resume"]

user_agent = UserAgent()


def create_app():
    """
    Creates a server hosted on localhost

    :return: Flask object
    """
    app = Flask(__name__)
    # # make flask support CORS
    CORS(app)


    with open("application.yml") as f:
        info = yaml.load(f, Loader=yaml.FullLoader)
        app.secret_key = info.get("SECRET_KEY", "default_secret_key")  # Use a default value if not found
        GOOGLE_CLIENT_ID = info["GOOGLE_CLIENT_ID"]
        GOOGLE_CLIENT_SECRET = info["GOOGLE_CLIENT_SECRET"]
        CONF_URL = info["CONF_URL"]


    app.config["CORS_HEADERS"] = "Content-Type"

    oauth = OAuth(app)

    @app.errorhandler(404)
    def page_not_found():
        """
        Returns a json object to indicate error 404

        :return: JSON object
        """
        return jsonify({"error": "Not Found"}), 404

    @app.errorhandler(405)
    # pylint: disable=C0103
    def page_not_allowed():
        """
        Returns a json object to indicate error 405

        :return: JSON object
        """
        return jsonify({"error": "Method not Allowed"}), 405

    @app.before_request
    def middleware():
        """
        Checks for user authorization tokens and returns message

        :return: JSON object
        """
        try:
            if request.method == "OPTIONS":
                return jsonify({"success": "OPTIONS"}), 200
            if request.path in existing_endpoints:
                headers = request.headers
                try:
                    token = headers["Authorization"].split(" ")[1]
                except:
                    return jsonify({"error": "Unauthorized"}), 401
                userid = token.split(".")[0]
                user = Users.objects(id=userid).first()

                if user is None:
                    return jsonify({"error": "Unauthorized"}), 401

                expiry_flag = False
                for tokens in user["authTokens"]:
                    if tokens["token"] == token:
                        expiry = tokens["expiry"]
                        expiry_time_object = datetime.strptime(
                            expiry, "%m/%d/%Y, %H:%M:%S"
                        )
                        if datetime.now() <= expiry_time_object:
                            expiry_flag = True
                        else:
                            delete_auth_token(tokens, userid)
                        break

                if not expiry_flag:
                    return jsonify({"error": "Unauthorized"}), 401

        except:
            return jsonify({"error": "Internal server error"}), 500

    def get_token_from_header():
        """
        Evaluates token from the request header

        :return: string
        """
        headers = request.headers
        token = headers["Authorization"].split(" ")[1]
        return token

    def get_userid_from_header():
        """
        Evaluates user id from the request header

        :return: string
        """
        headers = request.headers
        token = headers["Authorization"].split(" ")[1]
        print(token)
        userid = token.split(".")[0]
        return userid

    def delete_auth_token(token_to_delete, user_id):
        """
        Deletes authorization token of the given user from the database

        :param token_to_delete: token to be deleted
        :param user_id: user id of the current active user
        :return: string
        """
        user = Users.objects(id=user_id).first()
        auth_tokens = []
        for token in user["authTokens"]:
            if token != token_to_delete:
                auth_tokens.append(token)
        user.update(authTokens=auth_tokens)

    @app.route("/")
    @cross_origin()
    def health_check():
        return jsonify({"message": "Server up and running"}), 200

    @app.route("/users/signupGoogle")
    def signupGoogle():

        oauth.register(
            name='google',
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            server_metadata_url=CONF_URL,
            client_kwargs={
                'scope': 'openid email profile'
            },
            nonce='foobar'
        )

        # Redirect to google_auth function
        redirect_uri = url_for('authorized', _external=True)
        print(redirect_uri)

        session['nonce'] = generate_token()
        return oauth.google.authorize_redirect(redirect_uri, nonce=session['nonce'])

    @app.route('/users/signupGoogle/authorized')
    def authorized():
        print("Entered google auth!")
        token = oauth.google.authorize_access_token()
        user = oauth.google.parse_id_token(token, nonce=session['nonce'])
        session['user'] = user

        user_exists = Users.objects(email=user["email"]).first()

        users_email = user["email"]
        full_name = user["given_name"] + " " + user["family_name"]

        if user['email_verified']:
            if user_exists is None:
                userSave = Users(
                    id=get_new_user_id(),
                    fullName=full_name,
                    email=users_email,
                    authTokens=[],
                    applications=[],
                    skills=[],
                    job_levels=[],
                    locations=[],
                    phone_number="",
                    address=""
                )
                userSave.save()
                unique_id = userSave['id']
            else:
                unique_id = user_exists['id']

        userSaved = Users.objects(email=user['email']).first()
        expiry = datetime.now() + timedelta(days=1)
        expiry_str = expiry.strftime("%m/%d/%Y, %H:%M:%S")
        token_whole = str(unique_id) + "." + token['access_token']
        auth_tokens_new = userSaved['authTokens'] + \
            [{"token": token_whole, "expiry": expiry_str}]
        userSaved.update(authTokens=auth_tokens_new)

        return redirect(f"http://127.0.0.1:3000/?token={token_whole}&expiry={expiry_str}&userId={unique_id}")

    @app.route("/users/signup", methods=["POST"])
    def sign_up():
        """
        Creates a new user profile and adds the user to the database and returns the message

        :return: JSON object
        """
        try:
            # print(request.data)
            data = json.loads(request.data)
            print(data)
            try:
                _ = data["username"]
                _ = data["password"]
                _ = data["fullName"]
            except:
                return jsonify({"error": "Missing fields in input"}), 400

            username_exists = Users.objects(username=data["username"])
            if len(username_exists) != 0:
                return jsonify({"error": "Username already exists"}), 400
            password = data["password"]
            password_hash = hashlib.md5(password.encode())
            user = Users(
                id=get_new_user_id(),
                fullName=data["fullName"],
                username=data["username"],
                password=password_hash.hexdigest(),
                authTokens=[],
                applications=[],
                skills=[],
                job_levels=[],
                locations=[],
                phone_number="",
                address="",
                institution="",
                email=""
            )
            user.save()
            # del user.to_json()["password", "authTokens"]
            return jsonify(user.to_json()), 200
        except:
            return jsonify({"error": "Internal server error"}), 500

    @app.route("/getProfile", methods=["GET"])
    def get_profile_data():
        """
        Gets user's profile data from the database

        :return: JSON object with application data
        """
        try:
            userid = get_userid_from_header()
            user = Users.objects(id=userid).first()
            profileInformation = {}
            profileInformation["skills"] = user["skills"]
            profileInformation["job_levels"] = user["job_levels"]
            profileInformation["locations"] = user["locations"]
            profileInformation["institution"] = user["institution"]
            profileInformation["phone_number"] = user["phone_number"]
            profileInformation["address"] = user["address"]
            profileInformation["email"] = user["email"]
            profileInformation["fullName"] = user["fullName"]

            return jsonify(profileInformation)
        except:
            return jsonify({"error": "Internal server error"}), 500

    @app.route("/updateProfile", methods=["POST"])
    def updateProfilePreferences():
        """
        Update the user profile with preferences: skills, job-level and location
        """
        try:
            print(request.data)
            userid = get_userid_from_header()
            user = Users.objects(id=userid).first()
            data = json.loads(request.data)
            print(user)

            for key in data.keys():
                user[key] = data[key]
            user.save()
            return jsonify(user.to_json()), 200

        except Exception as err:
            print(err)
            return jsonify({"error": "Internal server error"}), 500

    # removing this API since its completely useless tbh
    # @app.route("/getRecommendations", methods=["GET"])
    # def getRecommendations():
    #     """
    #     Get AI-powered job recommendations based on user's profile
    #     """
    #     try:
    #         userid = get_userid_from_header()
    #         user = Users.objects(id=userid).first()
            
    #         # Get AI-powered recommendations
    #         recommendedJobs = get_ai_job_recommendations(
    #             user["skills"],
    #             user["job_levels"],
    #             user["locations"]
    #         )
            
    #         if not recommendedJobs:
    #             return jsonify({
    #                 "message": "No matching jobs found. Please update your profile with skills and preferences."
    #             }), 200

    #         return jsonify(recommendedJobs), 200
    
    #     except Exception as err:
    #         print(f"Error in getRecommendations: {str(err)}")
    #         return jsonify({"error": "Internal server error"}), 500

    @app.route("/users/login", methods=["POST"])
    def login():
        """
        Logs in the user and creates a new authorization token and stores it in the database
        """
        try:
            data = json.loads(request.data)

            if "username" not in data or "password" not in data:
                return jsonify({"error": "Missing username or password"}), 400

            # Find user by username
            user = Users.objects(username=data["username"]).first()
            if not user:
                return jsonify({"error": "User not found"}), 400

            # Hash entered password and compare with stored password
            entered_password_hash = hashlib.md5(data["password"].encode()).hexdigest()
            if user.password != entered_password_hash:
                return jsonify({"error": "Wrong username or password"}), 400

            # Generate session token
            expiry = datetime.now() + timedelta(days=1)
            expiry_str = expiry.strftime("%m/%d/%Y, %H:%M:%S")
            token = f"{user.id}.{uuid.uuid4()}"

            # Store token
            user.authTokens.append({"token": token, "expiry": expiry_str})
            user.save()

            # Return full profile in response
            return jsonify({
                "message": "Login successful",
                "token": token,
                "expiry": expiry_str,
                "profile": {
                    "id": user.id,
                    "fullName": user.fullName,
                    "username": user.username,
                    "email": user.email,
                    "phone_number": user.phone_number,
                    "address": user.address,
                    "institution": user.institution,
                    "skills": user.skills,
                    "job_levels": user.job_levels,
                    "locations": user.locations
                }
            }), 200
        except Exception as e:
            print("Error in login:", e)
            return jsonify({"error": "Internal server error"}), 500



    @app.route("/users/logout", methods=["POST"])
    def logout():
        """
        Logs out the user and deletes the existing token from the database

        :return: JSON object with status and message
        """
        try:
            userid = get_userid_from_header()
            user = Users.objects(id=userid).first()
            auth_tokens = []
            incoming_token = get_token_from_header()
            for token in user["authTokens"]:
                if token["token"] != incoming_token:
                    auth_tokens.append(token)
            user.update(authTokens=auth_tokens)

            return jsonify({"success": ""}), 200

        except:
            return jsonify({"error": "Internal server error"}), 500

    # search function
    # params:
    #   -keywords: string
    @app.route("/fake-job", methods=["GET"])
    def search():
        try:
            job_title = request.args.get('keywords', '')
            if not job_title:
                return jsonify({"error": "Job title is required"}), 400
            
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                return jsonify({"error": "GEMINI_API_KEY not set in .env"}), 500
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')

            prompt = f"""
            Create a comprehensive career guide for a {job_title} role. Be specific to this role and provide detailed, practical information.
            
            Return a JSON object with the following structure:
            {{
                "roleOverview": "Detailed description specific to {job_title}, including day-to-day responsibilities, career progression, and industry impact",
                
                "technicalSkills": [
                    {{
                        "category": "Core Skills for {job_title}",
                        "tools": ["List specific tools and technologies required"]
                    }},
                    {{
                        "category": "Additional Technical Skills",
                        "tools": ["List complementary skills that would be valuable"]
                    }},
                    {{
                        "category": "Emerging Technologies",
                        "tools": ["List new technologies relevant to this role"]
                    }}
                ],
                
                "softSkills": [
                    "List 5-7 soft skills specifically important for {job_title}, with brief explanations"
                ],
                
                "certifications": [
                    {{
                        "name": "Certification name specific to {job_title}",
                        "provider": "Certification provider",
                        "level": "Difficulty level",
                        "description": "Why this certification is valuable for {job_title}"
                    }}
                ],
                
                "projectIdeas": [
                    {{
                        "title": "Project name relevant to {job_title}",
                        "description": "Detailed project description showing relevant skills",
                        "technologies": ["Required technologies"],
                        "learningOutcomes": ["What you'll learn from this project"]
                    }}
                ],
                
                "industryTrends": [
                    "List 5 current trends specifically affecting {job_title} roles"
                ],
                
                "salaryRange": {{
                    "entry": "Entry-level salary range for {job_title}",
                    "mid": "Mid-level salary range for {job_title}",
                    "senior": "Senior-level salary range for {job_title}",
                    "factors": ["List factors that affect salary in this role"]
                }},
                
                "learningResources": [
                    {{
                        "name": "Resource name specific to {job_title}",
                        "type": "Course/Book/Tutorial/Workshop",
                        "cost": "Free/Paid with approximate cost",
                        "url": "Resource URL",
                        "duration": "Estimated time to complete",
                        "description": "What you'll learn from this resource"
                    }}
                ],
                
                "prerequisites": {{
                    "education": ["Required/recommended education"],
                    "experience": ["Required/recommended experience"],
                    "skills": ["Must-have skills before starting"]
                }},
                
                "careerPath": {{
                    "entryLevel": "Entry-level positions",
                    "midLevel": "Mid-level positions",
                    "senior": "Senior-level positions",
                    "advancement": ["Possible career advancement paths"]
                }}
            }}
            
            Ensure all information is:
            1. Specific to the {job_title} role
            2. Current and industry-relevant
            3. Detailed and actionable
            4. Realistic and practical
            """
            
            #Gemini API call
            response = model.generate_content(prompt)

            output = response.text
            output = re.sub(r'```json\n', '', output)
            output = re.sub(r'```', '', output)

            """
            Use this print statement to debug if the LLM is giving an incorrectly formatted output string
            """
            # print(f"The API call has been sent and received: {output}")
            
            # Parse the JSON content and return to client
            try:
                insights = json.loads(output)
                return jsonify(insights)
            except:
                print(f"Error: Gemini response was not valid JSON: {output}")
                return jsonify({"error": "Gemini response was not valid JSON"}), 500
            
        except Exception as e:
            print(f"Error in search: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    # get data from the CSV file for rendering root page
    @app.route("/applications", methods=["GET"])
    def get_data():
        """
        Gets user's applications data from the database

        :return: JSON object with application data
        """
        try:
            userid = get_userid_from_header()
            user = Users.objects(id=userid).first()
            applications = user["applications"]
            return jsonify(applications)
        except:
            return jsonify({"error": "Internal server error"}), 500

    @app.route("/applications", methods=["POST"])
    def add_application():
        """
        Add a new job application for the user to the applications tab. Check if this job exists in the shared application pool
        If the job exists in the shared pool then we just increment the appliedBy count of the shared pool listing
        If not then we add the job listing to the shared pool

        :return: JSON object with status and message
        """
        try:
            userid = get_userid_from_header()
            try:
                request_data = json.loads(request.data)["application"]
                _ = request_data["jobTitle"]
                _ = request_data["companyName"]
            except:
                return jsonify({"error": "Missing fields in input"}), 400

            user = Users.objects(id=userid).first()
            current_application = {
                "id": get_new_application_id(userid),
                "jobTitle": request_data["jobTitle"],
                "companyName": request_data["companyName"],
                "date": request_data.get("date"),
                "jobLink": request_data.get("jobLink"),
                "location": request_data.get("location"),
                "status": request_data.get("status", "1"),
            }
            applications = user["applications"] + [current_application]

            user.update(applications=applications)

            try:
                # Check if job already exists in shared pool (is this logic correct?)
                existing_job = SharedJobs.objects(
                jobTitle=request_data["jobTitle"],
                companyName=request_data["companyName"],
                jobLink=request_data["jobLink"],
                ).first()

                if existing_job:
                    # Increment the appliedBy counter by 1
                    existing_job.update(inc__appliedBy=1)
                    return jsonify(current_application), 200
                
                # Create new shared job
                job_id = str(uuid.uuid4())
                new_job = SharedJobs(
                    id=job_id,
                    jobTitle=request_data["jobTitle"],
                    companyName=request_data["companyName"],
                    location=request_data.get("location", ""),
                    jobLink=request_data.get("jobLink", ""),
                    postedBy=userid,
                    appliedBy=1  # current user is the only one who has applied to the job
                )
                new_job.save()

                return jsonify(current_application), 200
                
            except:
                return jsonify(current_application), 200

        except:
            return jsonify({"error": "Internal server error"}), 500

    @app.route("/applications/<int:application_id>", methods=["PUT"])
    def update_application(application_id):
        """
        Updates the existing job application for the user

        :param application_id: Application id to be modified
        :return: JSON object with status and message
        """
        try:
            userid = get_userid_from_header()
            try:
                request_data = json.loads(request.data)["application"]
            except:
                return jsonify({"error": "No fields found in input"}), 400

            user = Users.objects(id=userid).first()
            current_applications = user["applications"]

            if len(current_applications) == 0:
                return jsonify({"error": "No applications found"}), 400
            else:
                updated_applications = []
                app_to_update = None
                application_updated_flag = False
                for application in current_applications:
                    if application["id"] == application_id:
                        app_to_update = application
                        application_updated_flag = True
                        for key, value in request_data.items():
                            application[key] = value
                    updated_applications += [application]
                if not application_updated_flag:
                    return jsonify({"error": "Application not found"}), 400
                user.update(applications=updated_applications)

            return jsonify(app_to_update), 200
        except:
            return jsonify({"error": "Internal server error"}), 500

    @app.route("/applications/<int:application_id>", methods=["DELETE"])
    def delete_application(application_id):
        """
        Deletes the given job application for the user

        :param application_id: Application id to be modified
        :return: JSON object with status and message
        """
        try:
            userid = get_userid_from_header()
            user = Users.objects(id=userid).first()

            current_applications = user["applications"]

            application_deleted_flag = False
            updated_applications = []
            app_to_delete = None
            for application in current_applications:
                if application["id"] != application_id:
                    updated_applications += [application]
                else:
                    app_to_delete = application
                    application_deleted_flag = True

            if not application_deleted_flag:
                return jsonify({"error": "Application not found"}), 400
            user.update(applications=updated_applications)
            return jsonify(app_to_delete), 200
        except:
            return jsonify({"error": "Internal server error"}), 500
        
    @app.route("/wishlist", methods=["POST"])
    def add_application_as_wishlist():
        """
        Add a shared job to the user's wishlist using only the job ID
        This endpoint retrieves the job details from the SharedJobs collection
        and adds it to the user's applications with status "1" (wishlist)

        Expected request body: {"jobId": "some-uuid-here"}

        :return: JSON object with the added application or error message
        """
        
        try:
            # Get user ID from authentication token
            userid = get_userid_from_header()
            
            # Parse request data
            try:
                request_data = json.loads(request.data)
                job_id = request_data.get("jobId")
                
                if not job_id:
                    return jsonify({"error": "Missing jobId in request"}), 400
                    
            except Exception as e:
                return jsonify({"error": f"Invalid request format: {str(e)}"}), 400
                
            # Find the shared job by ID
            shared_job = SharedJobs.objects(id=job_id).first()
            if not shared_job:
                return jsonify({"error": "Job not found in shared listings"}), 404
                
            # Get the user
            user = Users.objects(id=userid).first()
            if not user:
                return jsonify({"error": "User not found"}), 404
                
            # Create new application object with wishlist status
            current_application = {
                "id": get_new_application_id(userid),
                "jobTitle": shared_job.jobTitle,
                "companyName": shared_job.companyName,
                "date": datetime.now().strftime("%Y-%m-%d"),  # Current date
                "jobLink": shared_job.jobLink,
                "location": shared_job.location,
                "status": "1",  # 1 stands for wishlist
            }
            
            # Add to user's applications
            applications = user["applications"] + [current_application]
            user.update(applications=applications)
            
            # Increment the appliedBy counter in shared job
            shared_job.update(inc__appliedBy=1)
            
            return jsonify(current_application), 200
            
        except Exception as e:
            print(f"Error adding to wishlist: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500


    @app.route("/resume", methods=["POST"])
    def upload_resume():
        """
        Uploads resume file or updates an existing resume for the user

        :return: JSON object with status and message
        """
        try:
            userid = get_userid_from_header()
            try:
                file = request.files["file"]  # .read()
            except:
                return jsonify({"error": "No resume file found in the input"}), 400

            user = Users.objects(id=userid).first()
            if not user.resume.read():
                # There is no file
                user.resume.put(file, filename=file.filename,
                                content_type="application/pdf")
                user.save()
                return jsonify({"message": "resume successfully uploaded"}), 200
            else:
                # There is a file, we are replacing it
                user.resume.replace(
                    file, filename=file.filename, content_type="application/pdf")
                user.save()
                return jsonify({"message": "resume successfully replaced"}), 200
        except Exception as e:
            print(e)
            return jsonify({"error": "Internal server error"}), 500



    @app.route("/resume", methods=["GET"])
    def get_resume():
        """
        Retrieves the resume file for the user

        :return: response with file
        """
        try:
            userid = get_userid_from_header()
            try:
                user = Users.objects(id=userid).first()
                if len(user.resume.read()) == 0:
                    raise FileNotFoundError
                else:
                    user.resume.seek(0)

            except:
                return jsonify({"error": "resume could not be found"}), 400

            filename = user.resume.filename
            content_type = user.resume.contentType
            response = send_file(
                user.resume,
                mimetype=content_type,
                download_name=filename,
                as_attachment=True,
            )
            response.headers["x-filename"] = filename
            response.headers["Access-Control-Expose-Headers"] = "x-filename"
            return response, 200
        except:
            return jsonify({"error": "Internal server error"}), 500
    
    @app.route("/parse-resume", methods=["POST"])
    def parse_resume():
        try:
            resume_file = request.files['resume']
            print(f"Trying to read the resume!")
            # Use a PDF parsing library like PyPDF2 or pdfplumber to extract text
            # For this example, we'll use PyPDF2
            
            reader = PdfReader(resume_file)
            text = ""
            print(f"The resume has been read!")
            for page in reader.pages:
                text += page.extract_text()

            # Use Gemini to structure the resume content
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                return jsonify({"error": "GEMINI_API_KEY not set in .env"}), 500
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            prompt = f"""
            Parse this resume text and extract key information in JSON format. Enter pure JSON without any extra characters or pretty formatting:
            {text}
            
            Return format:
            {{
                "skills": ["skill1", "skill2"],
                "experience": ["exp1", "exp2"],
                "education": ["edu1", "edu2"],
                "certifications": ["cert1", "cert2"]
            }}
            """

            response = model.generate_content(prompt)

            """
            Printing the output to see if the LLM answers with any extra characters or formatting to then remove it using RE
            """
            # print(f"The API call has been sent and received: {response.text}")

            output = response.text
            output = re.sub(r'```json\n', '', output)
            output = re.sub(r'```', '', output)

            try:
                parsed_resume = json.loads(output)
                return jsonify(parsed_resume)
            
            except json.JSONDecodeError:
                print(f"Error: Gemini response was not valid JSON: {output}")
                return jsonify({"error": "Gemini response was not valid JSON"}), 500

        except Exception as e:
            print(f"Error parsing resume: {str(e)}")
            return jsonify({"error": "Failed to parse resume"}), 500

    @app.route("/compare-resume", methods=["POST"])
    def compare_resume():
        try:
            data = request.json
            resume = data['resume']
            job_insights = data['jobInsights']
            
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                return jsonify({"error": "GEMINI_API_KEY not set in .env"}), 500
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            prompt = f"""
            Compare this resume with the job requirements and provide a detailed analysis:
            Resume: {json.dumps(resume)}
            Job Requirements: {json.dumps(job_insights)}
            
            Return a JSON object with the following structure:
            {{
                "overallMatch": percentage,
                "matchingSkills": ["skill1", "skill2", ...],
                "missingSkills": ["skill1", "skill2", ...],
                "recommendations": ["rec1", "rec2", ...]
            }}
            """
            
            response = model.generate_content(prompt)
            comparison = response.text
            comparison = re.sub(r'```json\n', '', comparison)
            comparison = re.sub(r'```', '', comparison)

            """
            Use this print statement to debug if the LLM is giving an incorrectly formatted output string
            """
            # print(f"The API call has been sent and received: {comparison}")
            
            # Parse the JSON content and return to client
            try:
                insights = json.loads(comparison)
                return jsonify(insights)
            except:
                print(f"Error: Gemini response was not valid JSON: {comparison}")
                return jsonify({"error": "Gemini response was not valid JSON"}), 500

        except Exception as e:
            print(f"Error comparing resume: {str(e)}")
            return jsonify({"error": "Failed to compare resume"}), 500
        
    @app.errorhandler(404)
    def page_not_found(error):  # Add error parameter
        """
        Returns a json object to indicate error 404

        :return: JSON object
        """
        return jsonify({"error": "Not Found"}), 404
    
    @app.route("/analyses", methods=["GET"])
    def get_analyses():
        """
        Gets user's saved analyses from the database
        """
        try:
            userid = get_userid_from_header()
            user = Users.objects(id=userid).first()
            
            if not hasattr(user, 'analyses'):
                return jsonify([])
                
            return jsonify(user.analyses)
        except Exception as e:
            print(f"Error getting analyses: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

    @app.route("/analyses", methods=["POST"]) 
    def save_analysis():
        """
        Saves a new analysis to the user's profile
        """
        try:
            userid = get_userid_from_header()
            user = Users.objects(id=userid).first()
            
            analysis = json.loads(request.data)
            
            if not hasattr(user, 'analyses'):
                user.analyses = []
                
            user.analyses.append(analysis)
            user.save()
            
            return jsonify({"message": "Analysis saved successfully"}), 200
        except Exception as e:
            print(f"Error saving analysis: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
        
    
    @app.route("/jobs/shared", methods=["GET"])
    def get_shared_jobs():
        """
        Gets all shared jobs that the user hasn't applied to yet
        """
        try:
            userid = get_userid_from_header()
            user = Users.objects(id=userid).first()

            # Get all shared jobs
            all_shared_jobs = SharedJobs.objects()

            # Filter out jobs the user has already applied to
            user_applications = [app["companyName"].lower() + ":" + app["jobLink"].lower()
                              for app in user["applications"]]

            available_jobs = []
            for job in all_shared_jobs:
                job_key = job["companyName"].lower() + ":" + job["jobLink"].lower()

                # Check if user hasn't already applied to this job
                if job_key not in user_applications:
                    print(f"Found applications {job_key}")
                    available_jobs.append({
                        "id": job["id"],
                        "jobTitle": job["jobTitle"],
                        "companyName": job["companyName"],
                        "location": job["location"],
                        "jobLink": job["jobLink"],
                        "date": job["postedDate"].strftime("%Y-%m-%d"),
                        "appliedBy": job["appliedBy"]
                    })

            return jsonify(available_jobs), 200
        except Exception as e:
            print(f"Error getting shared jobs: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
        

    # @app.route("/jobs/share", methods=["POST"])
    # def share_job():
    #     """
    #     Shares a job application with all users
    #     """
    #     try:
    #         userid = get_userid_from_header()
    #         data = json.loads(request.data)

    #         # Check if job already exists (is this logic correct?)
    #         existing_job = SharedJobs.objects(
    #             jobTitle=data["jobTitle"],
    #             companyName=data["companyName"],
    #             jobLink=data["jobLink"],
    #         ).first()

    #         if existing_job:
    #             return jsonify({"message": "Job already shared", "id": existing_job.id}), 200

    #         # Create new shared job
    #         job_id = str(uuid.uuid4())
    #         new_job = SharedJobs(
    #             id=job_id,
    #             jobTitle=data["jobTitle"],
    #             companyName=data["companyName"],
    #             location=data.get("location", ""),
    #             jobLink=data.get("jobLink", ""),
    #             postedBy=userid,
    #             appliedBy=1  # Add current user to applied list
    #         )
    #         new_job.save()

    #         return jsonify({
    #             "message": "Job shared successfully",
    #             "id": job_id
    #         }), 201
    #     except Exception as e:
    #         print(f"Error sharing job: {str(e)}")
    #         return jsonify({"error": "Internal server error"}), 500

    return app


app = create_app()

# class Users(db.Document):
#     """
#     Users class. Holds full name, username, password, as well as applications and resumes
#     """
#     id = db.IntField(primary_key=True)
#     # ... existing fields ...
#     profilePhoto = db.FileField()  # Add this field
#     # ... rest of the fields ...

# # Add these new routes inside create_app():

#     @app.route("/profilePhoto", methods=["POST"])
#     def upload_profile_photo():
#         """
#         Uploads or updates the profile photo for the user.
#         The file should be sent with the form field 'profilePhoto'.
#         """
#         try:
#             userid = get_userid_from_header()
#             try:
#                 file = request.files["profilePhoto"]
#             except:
#                 return jsonify({"error": "No profile photo file found in the input"}), 400

#             user = Users.objects(id=userid).first()
#             try:
#                 if not user.profilePhoto.read():
#                     user.profilePhoto.put(file, filename=file.filename, content_type=file.content_type)
#                     user.save()
#                     return jsonify({"message": "Profile photo successfully uploaded"}), 200
#                 else:
#                     user.profilePhoto.replace(file, filename=file.filename, content_type=file.content_type)
#                     user.save()
#                     return jsonify({"message": "Profile photo successfully replaced"}), 200
#             except Exception as inner_e:
#                 user.profilePhoto.put(file, filename=file.filename, content_type=file.content_type)
#                 user.save()
#                 return jsonify({"message": "Profile photo successfully uploaded"}), 200
#         except Exception as e:
#             print(e)
#             return jsonify({"error": "Internal server error"}), 500

#     @app.route("/profilePhoto", methods=["GET"])
#     def get_profile_photo_url():
#         """
#         Returns the URL for accessing the user's profile photo.
#         The returned URL points to the '/profilePhoto/file' endpoint.
#         """
#         try:
#             userid = get_userid_from_header()
#             user = Users.objects(id=userid).first()
#             if not user.profilePhoto or not user.profilePhoto.read():
#                 return jsonify({"error": "No profile photo found"}), 404
#             user.profilePhoto.seek(0)
#             photo_url = url_for("serve_profile_photo", _external=True)
#             return jsonify({"url": photo_url}), 200
#         except Exception as e:
#             print(e)
#             return jsonify({"error": "Internal server error"}), 500

#     @app.route("/profilePhoto/file", methods=["GET"])
#     def serve_profile_photo():
#         """
#         Serves the actual profile photo file.
#         """
#         try:
#             userid = get_userid_from_header()
#             user = Users.objects(id=userid).first()
#             if not user.profilePhoto or not user.profilePhoto.read():
#                 return jsonify({"error": "No profile photo found"}), 404
#             user.profilePhoto.seek(0)
#             filename = user.profilePhoto.filename
#             content_type = user.profilePhoto.contentType if user.profilePhoto.contentType else "application/octet-stream"
#             response = send_file(
#                 user.profilePhoto,
#                 mimetype=content_type,
#                 download_name=filename,
#                 as_attachment=True,
#             )
#             response.headers["x-filename"] = filename
#             response.headers["Access-Control-Expose-Headers"] = "x-filename"
#             return response, 200
#         except Exception as e:
#             print(e)
#             return jsonify({"error": "Internal server error"}), 500


# with open("application.yml") as f:
#     info = yaml.load(f, Loader=yaml.FullLoader)
#     username = info["USERNAME"]
#     password = info["PASSWORD"]
#     cluster_url = info["CLUSTER_URL"]
#     # ca=certifi.where()
#     app.config["MONGODB_SETTINGS"] = {
#         "db": "appTracker",
#         "host": f"mongodb+srv://{username}:{password}@{cluster_url}/",
#     }

# username = "test_user"
# password = "test_pass"
# cluster_url = "localhost"

with open("application.yml") as f:
    info = yaml.load(f, Loader=yaml.FullLoader)

MONGO_USERNAME = info.get("USERNAME", "default_user")
MONGO_PASSWORD = info.get("PASSWORD", "default_pass")
MONGO_CLUSTER = info.get("CLUSTER_URL", "cluster0.jmi6a.mongodb.net")

app.config["MONGODB_SETTINGS"] = {
    "db": "appTracker",
    "host": f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@cluster0.giavamz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
}


db = MongoEngine()
db.init_app(app)


class Users(db.Document):
    """
    Users class. Holds full name, username, password, as well as applications and resumes
    """
    id = db.IntField(primary_key=True)
    fullName = db.StringField()
    username = db.StringField()
    password = db.StringField()
    authTokens = db.ListField()
    email = db.StringField()
    applications = db.ListField()
    resume = db.FileField()
    skills = db.ListField()
    job_levels = db.ListField()
    locations = db.ListField()
    institution = db.StringField()
    phone_number = db.StringField()
    address = db.StringField()
    analyses = db.ListField()  # Add analyses field

    def to_json(self):
        """
        Returns the user details in JSON object

        :return: JSON object
        """
        return {"id": self.id, "fullName": self.fullName, "username": self.username}

class SharedJobs(db.Document):
    """
    Shared jobs collection. Contains job postings that can be viewed by all users.
    """
    id = db.StringField(primary_key=True)   #job id in the recommended jobs section
    jobTitle = db.StringField(required=True)    # title of the job
    companyName = db.StringField(required=True) # name of the company where the job is
    location = db.StringField() #location / region of the job
    jobLink = db.StringField()  #link to the job posting
    postedBy = db.IntField(required=True)  # User ID who added this job
    postedDate = db.DateTimeField(default=datetime.now)
    appliedBy = db.IntField(default=1)  # number of people who have applied
    active = db.IntField(default=1) #whether the job is still open or not

def get_new_user_id():
    """
    Returns the next value to be used for new user

    :return: key with new user_id
    """
    user_objects = Users.objects()
    if len(user_objects) == 0:
        return 1

    new_id = 0
    for a in user_objects:
        new_id = max(new_id, a["id"])

    return new_id + 1


def get_new_application_id(user_id):
    """
    Returns the next value to be used for new application

    :param: user_id: User id of the active user
    :return: key with new application_id
    """
    user = Users.objects(id=user_id).first()

    if len(user["applications"]) == 0:
        return 1

    new_id = 0
    for a in user["applications"]:
        new_id = max(new_id, a["id"])

    return new_id + 1

if __name__ == "__main__":
    app.run(host='localhost', port=5000)
