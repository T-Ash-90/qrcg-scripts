import requests
import csv
import os
import sys
import math
import time
import traceback
from rich.console import Console

console = Console()

PER_PAGE = 100


# -------------------------
# DEBUG LOGGER
# -------------------------
def debug(msg, level="INFO"):
    print(f"[{level}] {msg}")


# -------------------------
# FETCH TOTAL COUNT
# -------------------------
def get_total_qr_codes(api_key):
    debug("Fetching total QR code count")

    url = f"https://api.qr-code-generator.com/v1/account?access-token={api_key}"

    try:
        response = requests.get(url)
        debug(f"Account endpoint status: {response.status_code}")

        if response.status_code != 200:
            debug(f"Failed response: {response.text}", "ERROR")
            return None

        data = response.json()
        total = data.get("qrcodes", {}).get("activeTotalCodes")

        if total is None:
            debug("activeTotalCodes not found in response", "ERROR")
            return None

        debug(f"Total QR codes (account-wide): {total}")
        return int(total)

    except Exception as e:
        debug(f"Error fetching total QR codes: {e}", "CRITICAL")
        traceback.print_exc()
        return None


# -------------------------
# FETCH QR CODES (REFACTORED)
# -------------------------
def get_qr_codes(api_key, folder_id):
    qr_codes = []

    total = get_total_qr_codes(api_key)
    if total is None:
        console.print("[bold red]Error: Unable to fetch total QR count[/bold red]")
        sys.exit(1)

    total_pages = math.ceil(total / PER_PAGE)
    debug(f"Total pages to fetch: {total_pages}")

    for page in range(1, total_pages + 1):
        url = (
            f"http://api.qr-code-generator.com/v1/codes"
            f"?access-token={api_key}"
            f"&per-page={PER_PAGE}"
            f"&page={page}"
            f"&folder_id={folder_id}"
        )

        debug(f"Fetching page {page}/{total_pages}")

        try:
            start_time = time.time()
            response = requests.get(url)
            elapsed = time.time() - start_time

            debug(f"Response {page}: {response.status_code} ({elapsed:.2f}s)")

            if response.status_code != 200:
                debug(f"Failed page {page}: {response.text}", "ERROR")
                continue

            try:
                data = response.json()
            except Exception as json_err:
                debug(f"JSON parse failed on page {page}: {json_err}", "ERROR")
                continue

            if isinstance(data, list):
                if not data:
                    debug(f"Empty page {page}", "WARNING")
                    continue

                qr_codes.extend(data)

            # Optional: small delay to avoid rate limiting
            time.sleep(0.05)

        except Exception as e:
            debug(f"Request failed on page {page}: {e}", "CRITICAL")
            traceback.print_exc()
            continue

    if not qr_codes:
        console.print("[bold red]Error: No QR Codes Found[/bold red]")
        sys.exit(1)

    debug(f"Total QR codes fetched (filtered by folder): {len(qr_codes)}")

    return qr_codes


# -------------------------
# PROCESS QR CODES
# -------------------------
def process_qr_codes(qr_codes):
    processed_data = []

    for qr in qr_codes:
        qr_info = {
            'id': qr.get('id'),
            'type_id': qr.get('type_id'),
            'type_name': qr.get('type_name'),
            'title': qr.get('title'),
            'short_code': qr.get('short_code'),
            'short_url': qr.get('short_url'),
            'domain_id': get_domain_id(qr.get('short_url')),
            'target_url': qr.get('target_url'),
        }

        processed_data.append(qr_info)

    processed_data.reverse()
    return processed_data


def get_domain_id(short_url):
    if short_url.startswith("http://q-r.to/"):
        return 1
    elif short_url.startswith("http://l.ead.me/"):
        return 2
    elif short_url.startswith("https://l.ead.me/"):
        return 3
    elif short_url.startswith("https://qrco.de/"):
        return 4
    return 4


# -------------------------
# SAVE CSV
# -------------------------
def save_to_csv(data, folder="csv-exports", filename="qr_codes.csv"):
    if not os.path.exists(folder):
        os.makedirs(folder)

    data.reverse()

    filepath = os.path.join(folder, filename)

    fieldnames = ['id', 'type_id', 'type_name', 'title', 'domain_id', 'short_code', 'short_url', 'target_url']

    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"Data has been saved to {filepath}")


# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    if len(sys.argv) > 2:
        API_KEY_A = sys.argv[1]
        FOLDER_ID = sys.argv[2]
    else:
        API_KEY_A = input("Please enter API_KEY_A: ")
        FOLDER_ID = input("Please enter the REBUILDS FOLDER_ID: ")

    qr_codes = get_qr_codes(API_KEY_A, FOLDER_ID)

    processed_data = process_qr_codes(qr_codes)

    save_to_csv(processed_data)