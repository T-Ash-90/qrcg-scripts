# dynamic_website_rebuild.py

import requests
import csv
import json

# Step 1: Input API Keys
API_KEY_A = input("Enter API Key for ACCOUNT_A: ")
API_KEY_B = input("Enter API Key for ACCOUNT_B: ")

# Base URL for API requests
BASE_URL = "http://api.qr-code-generator.com/v1"

# Step 2: Fetch Folder ID for REBUILDS folder in ACCOUNT_A
def get_folder_id(api_key):
    url = f"{BASE_URL}/account?access-token={api_key}&expand=folders"
    response = requests.get(url)
    data = response.json()

    # Find REBUILDS folder
    for folder in data['folders']:
        if folder['title'] == "REBUILDS":
            return folder['id']
    raise Exception("REBUILDS folder not found!")

# Step 3: Get QR Codes in REBUILDS folder (handle pagination)
def get_qr_codes(api_key, folder_id):
    qr_codes = []
    page = 1
    while True:
        url = f"{BASE_URL}/codes?access-token={api_key}&per-page=100&page={page}&folder_id={folder_id}"
        response = requests.get(url)
        data = response.json()
        qr_codes.extend(data['codes'])

        if len(data['codes']) < 100:
            break
        page += 1
    return qr_codes

# Step 4: Create QR Codes in ACCOUNT_B
def create_qr_code(api_key, title, target_url):
    url = f"{BASE_URL}/codes?access-token={api_key}"
    payload = {
        "typeId": 1,  # Dynamic Website type
        "title": title,
        "data": {"url": target_url}
    }
    response = requests.post(url, json=payload)
    return response.json()

# Step 5: Delete QR Codes in REBUILDS folder in ACCOUNT_A
def delete_qr_code(api_key, qr_id):
    url = f"{BASE_URL}/codes/{qr_id}?access-token={api_key}"
    response = requests.delete(url)
    return response.status_code == 200

# Step 6: Update short_url in ACCOUNT_B to match original from ACCOUNT_A
def update_short_url(api_key, qr_id, short_code, domain_id):
    url = f"{BASE_URL}/codes/{qr_id}?access-token={api_key}"
    payload = {
        "short_code": short_code,
        "domain_id": domain_id
    }
    response = requests.put(url, json=payload)
    return response.json()

# Step 7: Helper to determine DOMAIN_ID based on SHORT_URL
def get_domain_id(short_url):
    if short_url.startswith("http://q-r.to/"):
        return 1
    elif short_url.startswith("http://l.ead.me/"):
        return 2
    elif short_url.startswith("https://l.ead.me/"):
        return 3
    elif short_url.startswith("https://qrco.de/"):
        return 4
    return None

# Step 8: Export to CSV
def export_to_csv(qr_codes):
    with open('rebuilt_qr_codes.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['ID_A', 'TITLE', 'SHORT_URL', 'TARGET_URL', 'ID_B', 'NEW_SHORT_URL'])

        for qr in qr_codes:
            writer.writerow([qr['ID_A'], qr['TITLE'], qr['SHORT_URL'], qr['TARGET_URL'], qr['ID_B'], qr['NEW_SHORT_URL']])

# Main Script Logic
def main():
    # Step 2: Get Folder ID for REBUILDS folder
    folder_id = get_folder_id(API_KEY_A)
    print(f"Found REBUILDS folder with ID: {folder_id}")

    # Step 3: Get QR Codes from REBUILDS folder
    qr_codes = get_qr_codes(API_KEY_A, folder_id)

    rebuilt_codes = []

    # Process each QR Code
    for qr in qr_codes:
        # Extract details
        ID_A = qr['id']
        TITLE = qr['title']
        SHORT_CODE = qr['short_code']
        SHORT_URL = qr['short_url']
        TARGET_URL = qr['data']['url']
        DOMAIN_ID = get_domain_id(SHORT_URL)

        # Step 4: Create QR Code in ACCOUNT_B
        created_qr = create_qr_code(API_KEY_B, TITLE, TARGET_URL)
        ID_B = created_qr['id']
        NEW_SHORT_URL = created_qr['short_url']

        # Step 5: Delete the QR Code from REBUILDS folder in ACCOUNT_A
        delete_qr_code(API_KEY_A, ID_A)

        # Step 6: Update the short_url in ACCOUNT_B
        update_short_url(API_KEY_B, ID_B, SHORT_CODE, DOMAIN_ID)

        # Add to rebuilt list for CSV export and printing
        rebuilt_codes.append({
            'ID_A': ID_A,
            'TITLE': TITLE,
            'SHORT_URL': SHORT_URL,
            'TARGET_URL': TARGET_URL,
            'ID_B': ID_B,
            'NEW_SHORT_URL': NEW_SHORT_URL
        })

    # Step 8: Export to CSV
    export_to_csv(rebuilt_codes)

    # Step 9: Print the rebuilt QR Codes
    print("The Following QR Codes have been rebuilt:")
    for code in rebuilt_codes:
        print(f"- {code['NEW_SHORT_URL']}")

# Run the script
if __name__ == "__main__":
    main()
