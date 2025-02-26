import unittest
import hashlib

class TestPasswordHashing(unittest.TestCase):
    def hash_password(self, password):
        """Helper method to hash passwords within the test class"""
        return hashlib.md5(password.encode()).hexdigest()

    def test_password_hashing(self):
        """Test that password hashing works correctly"""
        # Test case 1: Basic password
        password = "hi"
        expected_hash = "49f68a5c8493ec2c0bf489821c21fc3b"
        self.assertEqual(self.hash_password(password), expected_hash)

        # Test case 2: Empty password
        self.assertEqual(self.hash_password(""), "d41d8cd98f00b204e9800998ecf8427e")

        # Test case 3: Special characters
        password_special = "hello!@#$%"
        hashed = self.hash_password(password_special)
        # Verify it's a valid MD5 hash (32 characters, hexadecimal)
        self.assertTrue(len(hashed) == 32)
        self.assertTrue(all(c in '0123456789abcdef' for c in hashed))

    def test_password_consistency(self):
        """Test that the same password always produces the same hash"""
        password = "testpassword123"
        hash1 = self.hash_password(password)
        hash2 = self.hash_password(password)
        self.assertEqual(hash1, hash2)

if __name__ == '__main__':
    unittest.main()