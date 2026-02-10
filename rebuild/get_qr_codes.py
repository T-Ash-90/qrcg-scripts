import requests
import csv
import os
import sys
from rich.console import Console

console = Console()

def get_qr_codes(api_key, folder_id):
    qr_codes = []
    page = 1

    while True:
        url = f"http://api.qr-code-generator.com/v1/codes?access-token={api_key}&per-page=100&page={page}&folder_id={folder_id}"

        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            if isinstance(data, list):
                if not data:
                    break
                qr_codes.extend(data)

            if len(data) < 100:
                break

            page += 1
        else:
            print(f"Error: Unable to fetch data. Status code {response.status_code}")
            break

    if not qr_codes:
        console.print("[bold red]Error: No QR Codes Found[/bold red]")
        sys.exit(1)

    return qr_codes

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