import csv
import os
import time
import requests
from pathlib import Path
from datetime import datetime

API_BASE = "https://api.qr-code-generator.com/v1"
THROTTLE_DELAY = 0.11 


def get_api_key():
    return input("Enter your API key: ").strip()


def get_csv_path():
    path = input("Enter path to CSV file with an 'ID' column: ").strip()
    return Path(path).expanduser()


def read_ids_from_csv(csv_path):
    if not csv_path.exists():
        print(f"❌ File not found: {csv_path}")
        return []

    ids = []
    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            print("❌ CSV appears empty or missing headers.")
            return []

        cols_lower = {c.lower(): c for c in reader.fieldnames}
        if "id" not in cols_lower:
            print(f"❌ CSV missing required column 'ID'. Found columns: {reader.fieldnames}")
            return []

        id_col = cols_lower["id"]
        seen = set()
        for row in reader:
            raw = (row.get(id_col) or "").strip()
            if not raw or raw in seen:
                continue
            seen.add(raw)
            ids.append(raw)

    return ids


def delete_code(api_key, code_id):
    url = f"{API_BASE}/codes/{code_id}?access-token={api_key}"
    resp = requests.delete(url)
    if resp.status_code == 204:
        return True
    else:
        print(f"⚠️  Failed to delete ID {code_id}: {resp.status_code} - {resp.text}")
        return False


def write_report(deleted_ids):
    out_dir = Path("csv-exports")
    out_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_path = out_dir / f"deleted_qr_codes_{timestamp}.csv"

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id"])
        for cid in deleted_ids:
            writer.writerow([cid])

    print(f"\n✅ Deletion report saved to: {out_path}")


def main():
    print("QR Code Deletion Tool (CSV)\n----------------------------")

    api_key = get_api_key()
    if not api_key:
        print("❌ API key is required.")
        return

    csv_path = get_csv_path()
    ids = read_ids_from_csv(csv_path)

    if not ids:
        print("❌ No valid IDs found in CSV.")
        return

    print(f"\nLoaded {len(ids)} unique ID(s) from {csv_path}")
    confirm = input("You are about to permanently delete these QR Codes. Proceed? (y/n): ").strip().lower()
    if confirm != "y":
        print("Operation cancelled.")
        return

    deleted = []
    for i, cid in enumerate(ids, start=1):
        ok = delete_code(api_key, cid)
        if ok:
            print(f"[{i}/{len(ids)}] Deleted ID: {cid}")
            deleted.append(cid)
        else:
            print(f"[{i}/{len(ids)}] Skipped ID: {cid}")
        time.sleep(THROTTLE_DELAY)

    if deleted:
        write_report(deleted)
    else:
        print("No QR Codes were deleted.")

    print("\n✅ Process complete.")


if __name__ == "__main__":
    main()
