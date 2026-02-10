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

    mapping_csv = Path("csv-exports/qr_code_mapping.csv")
    designs_file = Path("csv-exports/qr_code_designs.json")

    if not mapping_csv.exists() or not designs_file.exists():
        print("Error: Required input files missing")
        sys.exit(1)

    designs = json.loads(designs_file.read_text())

    headers = {
        "Authorization": f"Key {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    with mapping_csv.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            old_id = row.get("ID_A")
            new_id = row.get("ID_B")

            if not old_id or not new_id:
                continue

            design = designs.get(old_id)
            if not design:
                print(f"⚠ No design found for old QR {old_id}")
                continue

            if not design.get("customizations"):
                print(f"⚠ QR {old_id} has no customizations, skipping")
                continue

            customizations = design.get("customizations", {})

            logo = customizations.get("logo")
            if logo and isinstance(logo, dict):
                logo_name = logo.get("name", "")
                if logo_name.startswith("account"):
                    customizations["logo"] = {"name": "no-logo"}

            payload = {
                "status": design.get("status", "active"),
                "url": design.get("url"),
                "title": design.get("title"),
                "customizations": customizations
            }

            response = requests.patch(
                f"{API_BASE}/{new_id}",
                headers=headers,
                json=payload
            )

            if response.status_code not in (200, 204):
                print(f"❌ Failed to update design for new QR {new_id}")
                continue

            print(f"🎨 Design applied to new QR {new_id}")

    print("Design update process complete.")

if __name__ == "__main__":
    main()
