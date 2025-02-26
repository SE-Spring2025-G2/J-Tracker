# J-Tracker - Your Job Tracking Assistant

[![GitHub license](https://img.shields.io/github/license/jashgopani/application-tracking-system)](https://github.com/jashgopani/application-tracking-system/blob/main/LICENSE)
[![DOI](https://zenodo.org/badge/426259091.svg)](https://zenodo.org/badge/latestdoi/426259091)
[![codecov](https://codecov.io/gh/jashgopani/application-tracking-system/branch/main/graph/badge.svg)](https://codecov.io/gh/kingan1/application-tracking-system)
[![GitHub issues](https://img.shields.io/github/issues/jashgopani/application-tracking-system)](https://github.com/jashgopani/application-tracking-system/issues)
[![Github closes issues](https://img.shields.io/github/issues-closed-raw/jashgopani/application-tracking-system)](https://github.com/jashgopani/application-tracking-system/issues?q=is%3Aissue+is%3Aclosed)
![GitHub top language](https://img.shields.io/github/languages/top/jashgopani/application-tracking-system)
![Test Status](https://github.com/ncsu-csc-510/Project2/workflows/Test/badge.svg)

<p align="center"><img width="700" src="./resources/ApplicationTrackingAnimation.gif"></p>

The internship application and job application process is no picnic. Job application management is time-consuming. With the referrals and deadlines, the whole process can get daunting. Our app enables you to track and organize your job application process, and manage it, without the inconvenience of clunky Excel spreadsheets.

Our software maintains a record of the work you have wish-listed. It records those companies that you have applied for and records any rejections. Instead of making the user visit each company's website for prospects, our software enables the applicant to look for them directly using simple keywords. Any possible offer of work may then be wish-listed by the applicant.

## New Features in Phase 2
🎥[Phase-2 Demo Video](https://www.youtube.com/watch?v=VKTob1N19ug)

## ⭐ Highlight of Phase 2 ⭐
### Dockerization 🗃️
Containerizing the application with docker has helped us achieve 2 prominent things
1. Significantly increasing the speed in which one would be able to setup the project on their machines.
2. Automation of the entire run of the application including running the tests!

### Other new features
1. Upload Resume versions
2. Bookmark option for the job recommendations
3. Enhanced Search to fetch latest job opportunities
4. Updated country list that now supports 120+ countries
5. Updated skills list so that you can present your profile without missing on any skill
6. Refactorization of Class components into functional components which makes the code more maintainable

#### Bug fixes
1. Undefined profile image.
2. Authentication into the application randomly not working.
3. Unable to load matched jobs
4. Application screen throwing null pointer randomly

---

### Application Demo video

https://user-images.githubusercontent.com/89501363/144725439-5d9191f8-df13-4814-aa15-99cd752ab0cc.mp4

## Table of contents

- [Basic Design](#basic-design)
- [Samples](#samples)
- [New Features In Phase 3](#new-features-in-phase-3)
- [Future Scope](#future-scope)
- [Explanation](#explanation)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
  - [Requirements](#requirements)
  - [Steps to follow for the installation](#steps-to-follow-for-the-installation)
- [Hosting the Database](#hosting-the-database)
  - [Local MongoDB](#local-mongodb)
  - [Hosted database with MongoDB Atlas](#hosted-database-with-mongodb-atlas)
- [License](#license)
- [How to Contribute](#how-to-contribute)
- [Team Members](#team-members)

## Basic Design:

![Basic Design](https://github.com/prithvish-doshi-17/application-tracking-system/blob/main/resources/Overall%20Design.PNG)

## Samples:

### Login Page / Signup Page

The introductory visual interface displayed from which a user is able to register and log into the application. User can also login or sign up through Google Authorization.

<p align="center"><img width="700" src="./resources/login_page.png"></p>
The Google Authorization Login:

<p align="center"><img width="700" src="./resources/googleauth.png"></p>

### HomeScreen - Profile Page

After Logging In, the Profile page of the user is displayed where the user details such as Name, Institution, email, phone number, address, skills, and more are shown.
Users can add or update information to their profile, such as their personal information, skills, preferred job locations, and their experience level.

<p align="center"><img width="700" src="./resources/profilepage.png"></p>

### SearchPage

The interface through which a user is able to search for specific jobs and apply on them through the 'Apply' button.

1. Navigate to Job search page, search for particular Job.
2. Click on Details button to see the Job Details
3. Click on Apply button which will redirect to the Job Apply link.

<p align="center"><img width="700" src="./resources/search_roles_companywise.png"></p> 
<p align="center"><img width="700" src="./resources/FindJobs.png"></p>
<p align="center"><img width="700" src="./resources/Job_Description.png"></p>

### ApplicationPage

The user is able to access different saved applications - Waitlisted applications, Waiting for Refereals, Applied Jobs, Application Status. The user can also add more jobs to track through this screen.

<p align="center"><img width="700" src="./resources/AddApplicationpage.png"></p>

### MatchesPage

On this page, user can see different jobs that would be recommended to them based on their profile and their preferences. User can apply for that position from this page too.

<p align="center"><img width="700" src="./resources/Recommendjobspage.png"></p>

## Future Scope:

- Include deadline reminders for the application and interview.
- Add a feature that allows users to attach these reminders to their Google calendar.
- Incorporate notifications for upcoming deadlines.
- Include a link to the university’s career fair page.
- Direct connection to Linkedin, allowing for the addition of job opportunities to the wishlist.
- An option to maintain separate profiles for job tracking.
- Integrate the database into docker

## Explanation:

Currently, we have four fundamental steps in our project:

1. The SearchPage where users can search about the Job Postings
2. The MatchesPage where users get recommendation about the jobs according to their preferences
3. The ApplicationsPage where users can add and see the position they applied to and can update/delete the the information. Any details in any table can be modified at any time during the process
4. The ProfilePage where user can add his skills, experience level and preffered location. This information is used to recommend user jobs that require similar skillsets

## Technologies Used:

- Python
- Node.Js
- Flask
- MongoDB
- React
- Docker

## Installation:

### Requirements:

- [Python](https://www.python.org/downloads/) (recommended >= 3.8)
- [pip](https://pip.pypa.io/en/stable/installation/) (Latest version 21.3 used as of 11/3)
- [npm](https://nodejs.org/en/) (Latest version 6.14.4 used as of 11/3)
- [Docker-Desktop](https://www.docker.com/products/docker-desktop/) (Latest version as of 11/27)

### Steps to follow for the installation:

1. **Clone the Repository**
    - Use the command `git clone https://github.com/jashgopani/application-tracking-system.git` to clone the repository.

2. **Start the Docker Engine**
    - Ensure that Docker is installed on your system. If not, you can download it from the official Docker website.
    - Start the Docker engine on your machine. The command varies based on your operating system.

3. **Build Images**
    - Navigate to the backend folder and build the image for the API using the following command:
        ```
        docker build -f dockerfile.api -t ats-api .
        ```
    - Similarly, navigate to the frontend folder and build the image for the client using the following command:
        ```
        docker build -f dockerfile.client -t ats-client .
        ```

4. **Run Docker Compose**
    - Finally, run the following command to start the application:
        ```
        docker-compose up
        ```

## Hosting the Database:

### Local MongoDB:

1. Download [MongoDB Community Server](https://docs.mongodb.com/manual/administration/install-community/)
2. Follow the [Installion Guide](https://docs.mongodb.com/guides/server/install/)
3. In app.py set 'host' string to 'localhost'
4. Run the local database:

mongodb

- Recommended: Use a GUI such as [Studio 3T](https://studio3t.com/download/) to more easily interact with the database

### Hosted database with MongoDB Atlas:

1. [Create account](https://account.mongodb.com/account/register) for MongoDB

- **If current MongoDB Atlas owner adds your username/password to the cluster, skip to step 4** \*

2. Follow MongoDB Atlas [Setup Guide](https://docs.atlas.mongodb.com/getting-started/) to create a database collection for hosting applications
3. Create application.yml in the backend folder with the following content:
   ```
   GOOGLE_CLIENT_ID : <Oauth Google ID>
   GOOGLE_CLIENT_SECRET : <Oauth Google Secret>
   CONF_URL : https://accounts.google.com/.well-known/openid-configuration
   SECRET_KEY : <Any Secret You Want>
   USERNAME : <MongoDB Atlas Username>
   PASSWORD : <MongoDB Atlas Password>
   CLUSTER_URL : <MongoDB Cluster URL>
   ```
4. In app.py set 'host' string to your MongoDB Atlas connection string. Replace the username and password with {username} and {password} respectively
6. For testing through CI to function as expected, repository secrets will need to be added through the settings. Create individual secrets with the following keys/values:

MONGO_USER: <MongoDB Atlas cluster username>
MONGO_PASS: <MongoDB Atlas cluster password>

## License

The project is licensed under the [MIT](https://choosealicense.com/licenses/mit/) license.

## How to Contribute?

Please see our CONTRIBUTING.md for instructions on how to contribute to the repository and assist us in improving the project.

## Team Members

- Akhilesh Neeruganti
- Jash Gopani
- Hemil Mehta
- Rohan Ajmera

## Contact Info
For any questions, please email neerua08@gmail.com.
