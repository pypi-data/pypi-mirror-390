import unittest
from utils.hash_utils import generate_hashes

class TestHashUtils(unittest.TestCase):
    def test_generate_hashes(self):
        pwd = "test123"
        results = generate_hashes(pwd)
        self.assertIn("MD5", results)
        self.assertIn("SHA256", results)
        self.assertIn("bcrypt", results)
        self.assertIn("PBKDF2", results)
        self.assertIn("Argon2", results)

if __name__ == "__main__":
    unittest.main()