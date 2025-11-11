import unittest
from dyhash.strength_utils import check_password_strength, suggest_password

class TestStrengthUtils(unittest.TestCase):
    def test_weak_password(self):
        self.assertEqual(check_password_strength("123"), "Weak")

    def test_medium_password(self):
        self.assertEqual(check_password_strength("abc123"), "Medium")

    def test_strong_password(self):
        self.assertEqual(check_password_strength("abc123!@#"), "Strong")

    def test_suggest_password(self):
        pwd = suggest_password()
        self.assertTrue(len(pwd) >= 12)

if __name__ == "__main__":
    unittest.main()