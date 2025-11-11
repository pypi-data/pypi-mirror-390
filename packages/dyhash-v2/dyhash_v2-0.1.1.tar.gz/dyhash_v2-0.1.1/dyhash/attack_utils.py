import hashlib

def wordlist_attack(target_hash: str, algorithm: str, wordlist_file: str = "wordlists/sample.txt") -> str:
    """
    محاكاة هجوم Wordlist لمحاولة كسر كلمة المرور
    """
    try:
        with open(wordlist_file, "r", encoding="utf-8") as f:
            for word in f:
                word = word.strip()
                if algorithm.upper() == "MD5":
                    h = hashlib.md5(word.encode()).hexdigest()
                elif algorithm.upper() == "SHA1":
                    h = hashlib.sha1(word.encode()).hexdigest()
                elif algorithm.upper() == "SHA256":
                    h = hashlib.sha256(word.encode()).hexdigest()
                elif algorithm.upper() == "SHA512":
                    h = hashlib.sha512(word.encode()).hexdigest()
                else:
                    return "Unsupported Algorithm"

                if h == target_hash:
                    return word
        return "Not Found"
    except FileNotFoundError:
        return "Wordlist file not found"