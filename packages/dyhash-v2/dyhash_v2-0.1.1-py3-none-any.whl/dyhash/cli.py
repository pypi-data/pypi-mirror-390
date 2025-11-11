import argparse
from .hash_utils import generate_hashes
from .strength_utils import check_password_strength, suggest_password
from .attack_utils import wordlist_attack
from .report_utils import save_json_report, save_html_report

def analyze_command(password: str):
    strength = check_password_strength(password)
    suggestion = None
    if strength != "Strong":
        suggestion = suggest_password()
        print(f"💡 Suggested Strong Password: {suggestion}")

    results = generate_hashes(password)
    print("\nDyHash-v2 Results:")
    for algo, h in results.items():
        print(f"{algo}: {h}")

    return {
        "password": password,
        "strength": strength,
        "suggestion": suggestion,
        "hashes": results
    }

def crack_command(hash_value: str, algorithm: str, wordlist: str):
    print(f"\nWordlist Attack Simulation ({algorithm}):")
    cracked = wordlist_attack(hash_value, algorithm, wordlist)
    print(f"Result: {cracked}")
    return {
        "algorithm": algorithm,
        "result": cracked
    }

def report_command(data: dict, json_file: str = None, html_file: str = None):
    if json_file:
        print(save_json_report(data, json_file))
    if html_file:
        print(save_html_report(data, html_file))

def main():
    parser = argparse.ArgumentParser(description="DyHash-v2 - Advanced Password Security Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a password")
    analyze_parser.add_argument("--password", "-p", type=str, required=True, help="Password to analyze")

    # crack command
    crack_parser = subparsers.add_parser("crack", help="Crack a hash using wordlist attack")
    crack_parser.add_argument("--hash", "-H", type=str, required=True, help="Target hash")
    crack_parser.add_argument("--algorithm", "-a", type=str, choices=["MD5", "SHA1", "SHA256", "SHA512"], required=True, help="Hash algorithm")
    crack_parser.add_argument("--wordlist", "-w", type=str, default="wordlists/sample.txt", help="Wordlist file path")

    # report command
    report_parser = subparsers.add_parser("report", help="Generate a report")
    report_parser.add_argument("--password", "-p", type=str, required=True, help="Password to analyze")
    report_parser.add_argument("--json", type=str, help="Save report as JSON")
    report_parser.add_argument("--html", type=str, help="Save report as HTML")

    args = parser.parse_args()

    if args.command == "analyze":
        analyze_command(args.password)

    elif args.command == "crack":
        crack_command(args.hash, args.algorithm, args.wordlist)

    elif args.command == "report":
        data = analyze_command(args.password)
        data["wordlist_attack"] = {"algorithm": "SHA256", "result": wordlist_attack(data["hashes"]["SHA256"], "SHA256")}
        report_command(data, args.json, args.html)