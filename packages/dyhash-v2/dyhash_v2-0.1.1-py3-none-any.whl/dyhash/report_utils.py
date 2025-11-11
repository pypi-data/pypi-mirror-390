import json

def save_json_report(data: dict, filename: str = "report.json") -> str:
    """
    حفظ النتائج في ملف JSON منظم
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    return f"✅ JSON report saved to {filename}"


def save_html_report(data: dict, filename: str = "report.html") -> str:
    """
    حفظ النتائج في ملف HTML منسق
    """
    html_content = f"""
    <html>
    <head>
        <title>DyHash-v2 Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #2c3e50; }}
            .section {{ margin-bottom: 20px; }}
            .hashes {{ font-family: monospace; }}
            .strong {{ color: green; }}
            .weak {{ color: red; }}
            .medium {{ color: orange; }}
        </style>
    </head>
    <body>
        <h1>DyHash-v2 Security Report</h1>
        <div class="section">
            <h2>Password Strength</h2>
            <p class="{data['strength'].lower()}">{data['strength']}</p>
            {"<p><b>Suggested Strong Password:</b> " + data['suggestion'] + "</p>" if data.get('suggestion') else ""}
        </div>
        <div class="section">
            <h2>Generated Hashes</h2>
            <div class="hashes">
                {"<br>".join([f"{algo}: {h}" for algo, h in data['hashes'].items()])}
            </div>
        </div>
        <div class="section">
            <h2>Wordlist Attack Simulation</h2>
            <p>Algorithm: {data['wordlist_attack']['algorithm']}</p>
            <p>Result: {data['wordlist_attack']['result']}</p>
        </div>
    </body>
    </html>
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    return f"✅ HTML report saved to {filename}"