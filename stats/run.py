import os
import requests
import csv
import re
import traceback
import time
from rich.console import Console
from rich.prompt import Prompt
from datetime import datetime
from collections import defaultdict
from granular_statistics import process_qr_codes

console = Console()

# -------------------------
# CONFIG
# -------------------------
PER_PAGE = 100
MAX_SAFE_PAGES = 5000


# -------------------------
# DEBUG HELPER
# -------------------------
def debug(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    console.print(f"[grey][{timestamp}][{level}] {message}[/grey]")


# -------------------------
# CLEANER
# -------------------------
def remove_rich_formatting(text):
    try:
        return re.sub(r'\[.*?\]', '', str(text))
    except Exception:
        return text


# -------------------------
# FETCH TOTAL COUNT
# -------------------------
def get_total_qr_codes(access_token):
    debug("Fetching total QR code count")

    url = f"https://api.qr-code-generator.com/v1/account?access-token={access_token}"

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

        debug(f"Total QR codes: {total}")
        return int(total)

    except Exception as e:
        debug(f"Error fetching total QR codes: {e}", "CRITICAL")
        traceback.print_exc()
        return None


# -------------------------
# FETCH QR CODE PAGES
# -------------------------
def fetch_qr_pages(access_token, total_pages):
    debug(f"Fetching {total_pages} pages")

    base_url = f"https://api.qr-code-generator.com/v1/codes?access-token={access_token}&per-page={PER_PAGE}"

    qr_codes = []

    with console.status("[bold green]Fetching QR codes..."):
        for page in range(1, total_pages + 1):
            url = f"{base_url}&page={page}"
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

                qr_codes_page = data if isinstance(data, list) else data.get("data", [])

                if not qr_codes_page:
                    debug(f"Empty page {page} (unexpected)", "WARNING")
                    continue

                qr_codes.extend(qr_codes_page)

            except Exception as e:
                debug(f"Request failed on page {page}: {e}", "CRITICAL")
                traceback.print_exc()
                continue

    debug(f"Total QR codes fetched: {len(qr_codes)}")
    return qr_codes


# -------------------------
# PROCESS QR CODES
# -------------------------
def process_qr_data(qr_codes):
    debug("Processing QR codes")

    static_qr_count = 0
    dynamic_qr_count = 0
    total_scans_all_time = 0

    static_qr_types = defaultdict(int)
    dynamic_qr_types = defaultdict(lambda: {'count': 0, 'scans': 0})

    qr_code_data = []

    with console.status("[bold green]Processing QR codes..."):
        for qr in qr_codes:
            try:
                id = qr.get("id", "N/A")
                created = qr.get("created", "N/A")
                title = qr.get("title")
                short_url = qr.get("short_url", "")
                target_url = qr.get("target_url")
                type_name = qr.get("type_name", "Unknown")
                total_scans = qr.get("total_scans", 0)
                unique_scans = qr.get("unique_scans", 0)
                status = (qr.get("status") or "unknown").lower()

                is_dynamic = bool(short_url)

                # Counters
                if is_dynamic:
                    dynamic_qr_count += 1
                    dynamic_qr_types[type_name]['count'] += 1
                    dynamic_qr_types[type_name]['scans'] += total_scans
                    if isinstance(total_scans, int):
                        total_scans_all_time += total_scans
                else:
                    static_qr_count += 1
                    static_qr_types[type_name] += 1

                qr_code_data.append({
                    "Created": remove_rich_formatting(created),
                    "ID": remove_rich_formatting(str(id)),
                    "Title": remove_rich_formatting(title),
                    "Short URL": remove_rich_formatting(short_url),
                    "Target URL": remove_rich_formatting(target_url),
                    "Solution Type": remove_rich_formatting(type_name),
                    "QR Code Type": "Dynamic" if is_dynamic else "Static",
                    "Status": status,
                    "Total Scans": str(total_scans) if is_dynamic else "",
                    "Unique Scans": str(unique_scans) if is_dynamic else "",
                })

            except Exception as e:
                debug(f"Processing error: {e}", "ERROR")
                traceback.print_exc()

    return {
        "static_count": static_qr_count,
        "dynamic_count": dynamic_qr_count,
        "total_scans": total_scans_all_time,
        "data": qr_code_data
    }


# -------------------------
# EXPORT CSV
# -------------------------
def export_csv(qr_code_data):
    if not qr_code_data:
        debug("No data to export", "WARNING")
        return None

    folder = "csv-exports"
    os.makedirs(folder, exist_ok=True)

    filename = os.path.join(
        folder,
        f"QR_CODE_DATA_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    try:
        with open(filename, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=qr_code_data[0].keys())
            writer.writeheader()
            writer.writerows(qr_code_data)

        debug(f"CSV written: {filename}")
        return filename

    except Exception as e:
        debug(f"CSV export failed: {e}", "CRITICAL")
        traceback.print_exc()
        return None


# -------------------------
# MAIN FUNCTION
# -------------------------
def fetch_qr_codes(access_token):
    total_codes = get_total_qr_codes(access_token)

    if total_codes is None:
        console.print("[red]Failed to retrieve total QR code count[/red]")
        return

    total_pages = (total_codes + PER_PAGE - 1) // PER_PAGE
    total_pages = min(total_pages, MAX_SAFE_PAGES)

    debug(f"Total pages to fetch: {total_pages}")

    qr_codes = fetch_qr_pages(access_token, total_pages)

    results = process_qr_data(qr_codes)

    console.print(f"[bold magenta]TOTAL STATIC:[/bold magenta] {results['static_count']}")
    console.print(f"[bold magenta]TOTAL DYNAMIC:[/bold magenta] {results['dynamic_count']}")
    console.print(f"[bold magenta]TOTAL SCANS:[/bold magenta] {results['total_scans']}")

    # -------------------------
    # EXPORT FLOW
    # -------------------------
    csv_file = None

    if Prompt.ask("Download CSV summary data? (y/n)", default="n").lower() == "y":
        csv_file = export_csv(results["data"])

    if csv_file:
        if Prompt.ask("Download granular QR code data? (y/n)", default="n").lower() == "y":
            try:
                process_qr_codes(csv_file, access_token, "csv-exports/qr-code-exports")
            except Exception as e:
                debug(f"Granular processing failed: {e}", "ERROR")
                traceback.print_exc()


# -------------------------
# ENTRY POINT
# -------------------------
if __name__ == "__main__":
    debug("Script started")

    access_token = Prompt.ask("Enter API token")

    fetch_qr_codes(access_token)

    debug("Script finished")