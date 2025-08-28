# Script to create QR Codes in ACCOUNT_B

import csv
import requests
import json
import time
import sys

def create_qr_code_in_account_b(api_key_b, title, target_url, type_id=1):
    """
    Create a QR code in ACCOUNT_B using the provided data.
    Returns the response data with the new QR code's ID (ID_B).
    """
    url = "https://api.qr-code-generator.com/v1/codes?access-token=" + api_key_b
    headers = {"Content-Type": "application/json"}
    payload = {
        "typeId": type_id,
        "title": title,
        "data": {"url": target_url}
    }

    # Make the POST request to create the QR code in ACCOUNT_B
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        # Parse the response and get ID_B
        data = response.json()
        id_b = data.get("id")

        # Print only the success message and the ID_B
        print(f"Status 200: Successfully created QR Code in Account B. ID_B: {id_b}")
        return id_b
    else:
        # Print error message if request fails
        print(f"Error: Unable to create QR code in ACCOUNT_B. Status code {response.status_code}")
        return None


def load_csv_data(file_path):
    """
    Load the QR code data from the CSV file.
    Returns a list of dictionaries with the data from the CSV.
    """
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        data = [row for row in reader]

    return data


def save_mapping_to_csv(mapping, file_path="csv-exports/qr_code_mapping.csv"):
    """
    Save the mapping of ID_A (from ACCOUNT_A) and ID_B (from ACCOUNT_B) to a CSV file.
    """
    if not mapping:
        print("No mappings to save.")
        return

    fieldnames = ['ID_A', 'ID_B']
    with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(mapping)

    print(f"Mapping data has been saved to {file_path}")


def create_qr_codes_in_account_b_from_csv(csv_file_path, api_key_b):
    """
    Create QR codes in ACCOUNT_B based on the data from the CSV and save the mapping of IDs.
    """
    # Load the data from the CSV file
    qr_codes_data = load_csv_data(csv_file_path)

    # List to store the mapping of ID_A to ID_B
    id_mapping = []

    for qr_code in qr_codes_data:
        # Extract necessary details from the CSV data
        id_a = qr_code['id']
        title = qr_code['title']
        target_url = qr_code['target_url']

        # Create a QR code in ACCOUNT_B using the collected data
        id_b = create_qr_code_in_account_b(api_key_b, title, target_url)

        if id_b:
            # Save the mapping of ID_A to ID_B
            print(f"Mapping ID_A: {id_a} to ID_B: {id_b}")
            id_mapping.append({'ID_A': id_a, 'ID_B': id_b})

        # Handle rate limit
        if len(id_mapping) % 10 == 0:  # Assuming rate limit is 10 per second
            print("Rate limit reached, waiting for 1 second...")
            time.sleep(1)

    # Save the ID mapping to a CSV file
    save_mapping_to_csv(id_mapping)


# Main execution logic
if __name__ == "__main__":
    # Check if the script is being called from the main script or directly
    if len(sys.argv) > 2:
        # If run from subprocess.run, get the arguments passed (API_KEY_B, CSV file path)
        API_KEY_B = sys.argv[1]
        csv_file_path = sys.argv[2]
    else:
        # If run directly, ask for user input
        API_KEY_B = input("Please enter API_KEY_B: ")
        csv_file_path = input("Please enter the path to the CSV file (default: csv-exports/qr_codes.csv): ") or "csv-exports/qr_codes.csv"

    # Create QR codes in ACCOUNT_B based on the CSV data
    create_qr_codes_in_account_b_from_csv(csv_file_path, API_KEY_B)
