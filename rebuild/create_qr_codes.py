import csv
import requests
import json
import time
import sys

def create_qr_code_in_account_b(api_key_b, title, target_url, type_id=1):
    url = "https://api.qr-code-generator.com/v1/codes?access-token=" + api_key_b
    headers = {"Content-Type": "application/json"}
    payload = {
        "typeId": type_id,
        "title": title,
        "data": {"url": target_url}
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        data = response.json()
        id_b = data.get("id")

        print(f"Status 200: Successfully created QR Code in Account B. ID_B: {id_b}")
        return id_b
    else:
        print(f"Error: Unable to create QR code in ACCOUNT_B. Status code {response.status_code}")
        return None


def load_csv_data(file_path):
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        data = [row for row in reader]

    return data


def save_mapping_to_csv(mapping, file_path="csv-exports/qr_code_mapping.csv"):
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
    qr_codes_data = load_csv_data(csv_file_path)

    id_mapping = []

    for qr_code in qr_codes_data:
        id_a = qr_code['id']
        title = qr_code['title']
        target_url = qr_code['target_url']

        id_b = create_qr_code_in_account_b(api_key_b, title, target_url)

        if id_b:
            print(f"Mapping ID_A: {id_a} to ID_B: {id_b}")
            id_mapping.append({'ID_A': id_a, 'ID_B': id_b})

        if len(id_mapping) % 10 == 0:
            print("Rate limit reached, waiting for 1 second...")
            time.sleep(1)

    save_mapping_to_csv(id_mapping)


if __name__ == "__main__":
    if len(sys.argv) > 2:
        API_KEY_B = sys.argv[1]
        csv_file_path = sys.argv[2]
    else:
        API_KEY_B = input("Please enter API_KEY_B: ")
        csv_file_path = input("Please enter the path to the CSV file (default: csv-exports/qr_codes.csv): ") or "csv-exports/qr_codes.csv"

    create_qr_codes_in_account_b_from_csv(csv_file_path, API_KEY_B)
