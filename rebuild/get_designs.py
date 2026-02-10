import csv
import json
import sys
import requests
from pathlib import Path

API_BASE = "https://api.qrcg.com/v3/qrcodes"

def main():
    if len(sys.argv) != 2:
        print("Error: API key required")
        sys.exit(1)

    api_key = sys.argv[1]
    input_csv = Path("csv-exports/qr_codes.csv")
    output_file = Path("csv-exports/qr_code_designs.json")

    if not input_csv.exists():
        print("Error: qr_codes.csv not found")
        sys.exit(1)

    headers = {
        "Authorization": f"Key {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    designs = {}

    with input_csv.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            qr_id = row.get("id")
            if not qr_id:
                continue

            response = requests.get(f"{API_BASE}/{qr_id}", headers=headers)
            if response.status_code != 200:
                print(f"Warning: Failed to fetch design for QR {qr_id}")
                continue

            data = response.json()

            designs[qr_id] = {
                "customizations": data.get("customizations"),
                "title": data.get("title"),
                "url": data.get("url"),
                "status": data.get("status")
            }

            print(f"✔ Retrieved design for QR {qr_id}")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(designs, indent=2))

    print(f"Saved {len(designs)} designs → {output_file}")

if __name__ == "__main__":
    main()
