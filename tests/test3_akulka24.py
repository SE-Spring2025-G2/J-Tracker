import unittest
import os
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

class TestJobApplications(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up MongoDB connection"""
        mongodb_uri = os.getenv('MONGODB_URI')
        if not mongodb_uri:
            raise EnvironmentError("MONGODB_URI environment variable is not set")
        
        cls.client = MongoClient(mongodb_uri)
        cls.db = cls.client['jobtracker']
        cls.applications = cls.db['applications']
        
        # Test user ID
        cls.test_user_id = ObjectId()  # Generate a unique test user ID
        
        # Test data
        cls.test_applications = [
            {
                "userId": cls.test_user_id,
                "jobTitle": "Software Engineer",
                "company": "Tech Corp",
                "status": "Applied",
                "applicationDate": datetime.now(),
                "location": "Remote",
                "description": "Full-stack development position"
            },
            {
                "userId": cls.test_user_id,
                "jobTitle": "Full Stack Developer",
                "company": "Startup Inc",
                "status": "In Progress",
                "applicationDate": datetime.now(),
                "location": "New York, NY",
                "description": "Exciting startup opportunity"
            }
        ]

    def setUp(self):
        """Set up test data before each test"""
        # Clear existing test data and insert new ones
        self.applications.delete_many({"userId": self.test_user_id})
        self.applications.insert_many(self.test_applications)

    def test_fetch_job_applications(self):
        """Test retrieving all job applications for a user"""
        # Fetch applications from MongoDB
        user_applications = list(self.applications.find(
            {"userId": self.test_user_id}
        ))

        # Verify number of applications
        self.assertEqual(
            len(user_applications), 
            len(self.test_applications),
            "Should return correct number of applications"
        )

        print(f"\nFound {len(user_applications)} applications")

        # Check each application has required fields
        for app in user_applications:
            print(f"\nChecking application: {app}")
            
            # Verify required fields
            required_fields = [
                'userId', 'jobTitle', 'company', 'status', 
                'applicationDate', 'location', 'description'
            ]
            for field in required_fields:
                self.assertIn(field, app, f"Application should have {field}")

            # Verify data types
            self.assertEqual(app['userId'], self.test_user_id)
            self.assertIsInstance(app['jobTitle'], str)
            self.assertIsInstance(app['company'], str)
            self.assertIsInstance(app['status'], str)
            self.assertIsInstance(app['applicationDate'], datetime)
            
            # Verify status is valid
            valid_statuses = ['Applied', 'In Progress', 'Rejected', 'Accepted']
            self.assertIn(app['status'], valid_statuses, 
                         "Status should be valid")

    def test_empty_applications(self):
        """Test handling of user with no applications"""
        # Clear all applications for test user
        self.applications.delete_many({"userId": self.test_user_id})
        
        # Fetch applications
        empty_applications = list(self.applications.find(
            {"userId": self.test_user_id}
        ))
        
        print("\nTesting empty applications case")
        self.assertEqual(len(empty_applications), 0, 
                        "Should return empty list for user with no applications")

    def test_application_count(self):
        """Test counting total applications for a user"""
        count = self.applications.count_documents({"userId": self.test_user_id})
        
        print(f"\nFound {count} total applications")
        self.assertEqual(count, len(self.test_applications),
                        "Should return correct total count of applications")

    def tearDown(self):
        """Clean up test data after each test"""
        self.applications.delete_many({"userId": self.test_user_id})

    @classmethod
    def tearDownClass(cls):
        """Clean up MongoDB connection"""
        cls.client.close()

if __name__ == '__main__':
    unittest.main()