import unittest
from dyhash.attack_utils import wordlist_attack
import hashlib
import os

class TestAttackUtils(unittest.TestCase):
    def setUp(self):
        # إنشاء ملف wordlist مؤقت للتجربة
        self.wordlist_file = "wordlists/test_wordlist.txt"
        os.makedirs("wordlists", exist_ok=True)
        with open(self.wordlist_file, "w", encoding="utf-8") as f:
            f.write("test123\npassword\n123456\n")

        # توليد هاش لكلمة "test123" باستخدام SHA256
        self.target_hash = hashlib.sha256("test123".encode()).hexdigest()

    def tearDown(self):
        # حذف ملف wordlist بعد الاختبار
        if os.path.exists(self.wordlist_file):
            os.remove(self.wordlist_file)

    def test_wordlist_attack_found(self):
        result = wordlist_attack(self.target_hash, "SHA256", self.wordlist_file)
        self.assertEqual(result, "test123")

    def test_wordlist_attack_not_found(self):
        result = wordlist_attack("invalidhash", "SHA256", self.wordlist_file)
        self.assertEqual(result, "Not Found")

if __name__ == "__main__":
    unittest.main()