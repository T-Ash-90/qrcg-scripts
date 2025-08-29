# Script that updates the short URLs for rebuilt QR Codes

import sys
import csv
import requests
import json
import time

# Function to load the QR Code mapping data (ID_A and ID_B)
def load_mapping_from_csv(file_path="csv-exports/qr_code_mapping.csv"):
    mappings = []
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        mappings = [row for row in reader]
    return mappings

# Function to load QR codes from csv to get domain_id and short_code based on ID_A
def load_qr_codes_from_csv(file_path="csv-exports/qr_codes.csv"):
    qr_codes = {}
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            id_a = row['id']
            qr_codes[id_a] = {
                'domain_id': row['domain_id'],
                'short_code': row['short_code']
            }
    return qr_codes

# Function to update the short URL in ACCOUNT_B
def update_short_url_in_account_b(api_key_b, id_b, short_code, domain_id):
    url = f"https://api.qr-code-generator.com/v1/codes/{id_b}?access-token={api_key_b}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "short_code": short_code,
        "domain_id": domain_id
    }
    response = requests.put(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        print(f"Successfully updated short URL for ID_B: {id_b}")
    else:
        print(f"Failed to update short URL for ID_B: {id_b}. Status code: {response.status_code}")

# Function to update short URLs for QR codes in ACCOUNT_B
def update_qr_codes_short_urls(api_key_b, mapping_file="csv-exports/qr_code_mapping.csv", qr_codes_file="csv-exports/qr_codes.csv"):
    mappings = load_mapping_from_csv(mapping_file)
    qr_codes_data = load_qr_codes_from_csv(qr_codes_file)

    request_count = 0
    for mapping in mappings:
        id_a = mapping['ID_A']
        id_b = mapping['ID_B']

        if id_a in qr_codes_data:
            short_code = qr_codes_data[id_a]['short_code']
            domain_id = qr_codes_data[id_a]['domain_id']
            update_short_url_in_account_b(api_key_b, id_b, short_code, domain_id)

            request_count += 1
            if request_count % 10 == 0:
                print("Rate limit reached, waiting for 1 second...")
                time.sleep(1)
        else:
            print(f"No data found for ID_A: {id_a} in qr_codes.csv. Skipping update for ID_B: {id_b}")

# Handle API key passed via command line argument
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: API_KEY_B is required.")
        sys.exit(1)  # Exit if API_KEY_B is not provided

    API_KEY_B = sys.argv[1]  # Get API_KEY_B passed by the main script
    update_qr_codes_short_urls(API_KEY_B)
