import re
import random
import string

def check_password_strength(password: str) -> str:
    """
    فحص قوة كلمة المرور بناءً على الطول والتنوع
    """
    if len(password) < 6:
        return "Weak"
    elif re.search(r"[A-Za-z]", password) and re.search(r"[0-9]", password):
        if len(password) >= 8 and re.search(r"[^A-Za-z0-9]", password):
            return "Strong"
        else:
            return "Medium"
    else:
        return "Weak"

def suggest_password(length: int = 12) -> str:
    """
    توليد كلمة مرور قوية عشوائية
    """
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))