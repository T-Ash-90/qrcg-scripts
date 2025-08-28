# Script that updates the short URLs for rebuilt QR Codes

import csv
import requests
import json
import time

def load_mapping_from_csv(file_path="csv-exports/qr_code_mapping.csv"):
    """
    Load the QR Code mapping data (ID_A and ID_B) from the CSV file.
    Returns a list of mappings.
    """
    mappings = []
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        mappings = [row for row in reader]

    return mappings

def load_qr_codes_from_csv(file_path="csv-exports/qr_codes.csv"):
    """
    Load the QR codes data from the qr_codes.csv file to find domain_id and short_code based on ID_A.
    Returns a dictionary with ID_A as the key and corresponding domain_id, short_code as values.
    """
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

def update_short_url_in_account_b(api_key_b, id_b, short_code, domain_id):
    """
    Update the short URL for the QR code in ACCOUNT_B using the PUT request.
    """
    url = f"https://api.qr-code-generator.com/v1/codes/{id_b}?access-token={api_key_b}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "short_code": short_code,
        "domain_id": domain_id
    }

    response = requests.put(url, headers=headers, data=json.dumps(payload))

    # Handle the response status codes
    if response.status_code == 200:
        print(f"Successfully updated short URL for ID_B: {id_b}")
    else:
        print(f"Failed to update short URL for ID_B: {id_b}. Status code: {response.status_code}")

def update_qr_codes_short_urls(api_key_b, mapping_file="csv-exports/qr_code_mapping.csv", qr_codes_file="csv-exports/qr_codes.csv"):
    """
    Update the short URL for each QR code in ACCOUNT_B by using the mapping from ID_A to ID_B and the data from qr_codes.csv.
    Implements throttling behavior to avoid exceeding 10 requests per second.
    """
    # Load the mapping of ID_A and ID_B from the CSV file
    mappings = load_mapping_from_csv(mapping_file)

    # Load the QR code data from qr_codes.csv to get the short_code and domain_id for ID_A
    qr_codes_data = load_qr_codes_from_csv(qr_codes_file)

    # Track the number of requests made
    request_count = 0

    # For each ID_B in the mapping file, get the corresponding ID_A, short_code, and domain_id
    for mapping in mappings:
        id_a = mapping['ID_A']
        id_b = mapping['ID_B']

        # Get the corresponding short_code and domain_id for ID_A
        if id_a in qr_codes_data:
            short_code = qr_codes_data[id_a]['short_code']
            domain_id = qr_codes_data[id_a]['domain_id']

            # Update the short URL for ID_B in ACCOUNT_B
            update_short_url_in_account_b(api_key_b, id_b, short_code, domain_id)

            # Increment the request count
            request_count += 1

            # If we have made 10 requests, wait for 1 second
            if request_count % 10 == 0:
                print("Rate limit reached, waiting for 1 second...")
                time.sleep(1)
        else:
            print(f"No data found for ID_A: {id_a} in qr_codes.csv. Skipping update for ID_B: {id_b}")

# Main execution logic
if __name__ == "__main__":
    # Ask for the API key for ACCOUNT_B (since it is separate)
    API_KEY_B = input("Please enter API_KEY_B: ")

    # Update the short URL for QR codes in ACCOUNT_B
    update_qr_codes_short_urls(API_KEY_B)
