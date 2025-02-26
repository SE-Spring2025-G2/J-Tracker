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
from jobsearch import get_ai_job_recommendations


import yaml



import requests

from authlib.integrations.flask_client import OAuth
from authlib.common.security import generate_token


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

    # get all the variables from the application.yml file
    # with open("application.yml") as f:
    #     info = yaml.load(f, Loader=yaml.FullLoader)
    #     GOOGLE_CLIENT_ID = info["GOOGLE_CLIENT_ID"]
    #     GOOGLE_CLIENT_SECRET = info["GOOGLE_CLIENT_SECRET"]
    #     CONF_URL = info["CONF_URL"]
    #     app.secret_key = info['SECRET_KEY']

    with open("application.yml") as f:
        info = yaml.load(f, Loader=yaml.FullLoader)
        app.secret_key = info.get("SECRET_KEY", "default_secret_key")  # Use a default value if not found


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

    @app.route("/getRecommendations", methods=["GET"])
    def getRecommendations():
        """
        Get AI-powered job recommendations based on user's profile
        """
        try:
            userid = get_userid_from_header()
            user = Users.objects(id=userid).first()
            
            # Get AI-powered recommendations
            recommendedJobs = get_ai_job_recommendations(
                user["skills"],
                user["job_levels"],
                user["locations"]
            )
            
            if not recommendedJobs:
                return jsonify({
                    "message": "No matching jobs found. Please update your profile with skills and preferences."
                }), 200

            return jsonify(recommendedJobs), 200

        except Exception as err:
            print(f"Error in getRecommendations: {str(err)}")
            return jsonify({"error": "Internal server error"}), 500
    
    # @app.route("/users/login", methods=["POST"])
    # def login():
    #     """
    #     Logs in the user and creates a new authorization token and stores it in the database
    #     """
    #     try:
    #         data = json.loads(request.data)

    #         if "username" not in data or "password" not in data:
    #             return jsonify({"error": "Missing username or password"}), 400

    #         # Find user by username
    #         user = Users.objects(username=data["username"]).first()
    #         if not user:
    #             print("❌ User not found:", data["username"])
    #             return jsonify({"error": "User not found"}), 400

    #         # Debug: Print stored and entered password hashes
    #         entered_password_hash = hashlib.md5(data["password"].encode()).hexdigest()
    #         print(f"🔍 Entered Hash: {entered_password_hash}")
    #         print(f"🔍 Stored Hash: {user.password}")

    #         # Compare hashed password
    #         if user.password != entered_password_hash:
    #             print("❌ Password does not match")
    #             return jsonify({"error": "Wrong username or password"}), 400

    #         # Generate session token
    #         expiry = datetime.now() + timedelta(days=1)
    #         expiry_str = expiry.strftime("%m/%d/%Y, %H:%M:%S")
    #         token = f"{user.id}.{uuid.uuid4()}"

    #         # Store token
    #         user.authTokens.append({"token": token, "expiry": expiry_str})
    #         user.save()

    #         print("✅ Login successful")
    #         return jsonify({
    #             "message": "Login successful",
    #             "token": token,
    #             "expiry": expiry_str
    #         }), 200

    #     except Exception as e:
    #         print("❌ Error in login:", e)
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
    @app.route("/search", methods=["GET"])
    def search():
        try:
            job_title = request.args.get('keywords', '')
            if not job_title:
                return jsonify({"error": "Job title is required"}), 400

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

        # Rest of the code remains the same...

            headers = {
                "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a career advisor. Return only JSON without any markdown formatting."
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "response_format": { "type": "json_object" }
            }

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            )

            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Clean the content string
                content = content.strip()
                if content.startswith('```json'):
                    content = content[7:]
                if content.startswith('```'):
                    content = content[3:]
                if content.endswith('```'):
                    content = content[:-3]
                
                # Parse the JSON content
                insights = json.loads(content.strip())
                
                # Return the parsed JSON directly
                return jsonify(insights), 200
            else:
                return jsonify({"error": "Failed to get insights"}), 500

        except Exception as e:
            print(f"Error in search: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
            
    @app.route("/search", methods=["GET"])
    def search_jobs():
        try:
            job_title = request.args.get('keywords', '')
            if not job_title:
                return jsonify({"error": "Job title is required"}), 400

            # Create detailed prompt for job insights
            prompt = f"""
                Provide comprehensive insights for the role: {job_title}

                Return a JSON object with this exact structure:
                {{
                    "roleOverview": "string describing the role",
                    "technicalSkills": [
                        {{
                            "category": "category name",
                            "tools": ["tool1", "tool2"]
                        }}
                    ],
                    "softSkills": ["skill1", "skill2"],
                    "certifications": [
                        {{
                            "name": "cert name",
                            "provider": "provider name",
                            "level": "difficulty level"
                        }}
                    ],
                    "projectIdeas": [
                        {{
                            "title": "project name",
                            "description": "project description",
                            "technologies": ["tech1", "tech2"]
                        }}
                    ],
                    "industryTrends": ["trend1", "trend2"],
                    "salaryRange": {{
                        "entry": "entry level range",
                        "mid": "mid level range",
                        "senior": "senior level range"
                    }},
                    "learningResources": [
                        {{
                            "name": "resource name",
                            "type": "resource type",
                            "cost": "free/paid",
                            "url": "resource url"
                        }}
                    ]
                }}
                """

            # OpenAI API call
            headers = {
                "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a career advisor and industry expert providing detailed insights about tech roles."
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "response_format": { "type": "json_object" }
            }

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            )

            if response.status_code == 200:
                result = response.json()
                insights = json.loads(result['choices'][0]['message']['content'])
                return jsonify(insights), 200
            else:
                return jsonify({"error": "Failed to get insights"}), 500

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
        Add a new job application for the user

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
            # Use a PDF parsing library like PyPDF2 or pdfplumber to extract text
            # For this example, we'll use PyPDF2
            from PyPDF2 import PdfReader
            
            reader = PdfReader(resume_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()

            # Use GPT to structure the resume content
            headers = {
                "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""
            Parse this resume text and extract key information in JSON format:
            {text}
            
            Return format:
            {{
                "skills": ["skill1", "skill2"],
                "experience": ["exp1", "exp2"],
                "education": ["edu1", "edu2"],
                "certifications": ["cert1", "cert2"]
            }}
            """
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "You are a resume parser."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7
                }
            )
            
            parsed_resume = response.json()['choices'][0]['message']['content']
            return jsonify(json.loads(parsed_resume))

        except Exception as e:
            print(f"Error parsing resume: {str(e)}")
            return jsonify({"error": "Failed to parse resume"}), 500

    @app.route("/compare-resume", methods=["POST"])
    def compare_resume():
        try:
            data = request.json
            resume = data['resume']
            job_insights = data['jobInsights']
            
            # Use GPT to compare resume with job requirements
            headers = {
                "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""
            Compare this resume with the job requirements and provide a detailed analysis:
            Resume: {json.dumps(resume)}
            Job Requirements: {json.dumps(job_insights)}
            
            Return format:
            {{
                "overallMatch": percentage,
                "matchingSkills": ["skill1", "skill2"],
                "missingSkills": ["skill1", "skill2"],
                "recommendations": ["rec1", "rec2"]
            }}
            """
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "You are a resume analyzer."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7
                }
            )
            
            comparison = response.json()['choices'][0]['message']['content']
            return jsonify(json.loads(comparison))

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

    return app


app = create_app()


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
    "db": "Cluster0",
    "host": "mongodb+srv://akakadi:PHzJPFrq3t9bNuVN@cluster0.brnbh.mongodb.net/",
    "tlsCAFile": certifi.where(),
}
# app.config["tlsAllowInvalidCertificates"]=True


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

# def build_preflight_response():
    # response = make_response()
    # response.headers.add("Access-Control-Allow-Origin", "*")
    # response.headers.add('Access-Control-Allow-Headers', "*")
    # response.headers.add('Access-Control-Allow-Methods', "*")
    # return response
# def build_actual_response(response):
    # response.headers.add("Access-Control-Allow-Origin", "*")
    # return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
