import requests
import csv
import os
import time

API_BASE = "http://api.qr-code-generator.com/v1"

def get_api_key():
    return input("Enter your API key: ").strip()

def get_account_info(api_key):
    url = f"{API_BASE}/account?access-token={api_key}&expand=folders,statistics"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch account info: {response.status_code} - {response.text}")
        exit(1)
    return response.json()

def choose_folder(folders):
    print("\nChoose a folder:")
    for idx, folder in enumerate(folders, start=1):
        print(f"{idx}. {folder['name']} (ID: {folder['id']})")
    print(f"{len(folders)+1}. ALL QR CODES")

    while True:
        choice = input("Enter the number of your choice: ").strip()
        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(folders):
                return folders[choice - 1]['id'], folders[choice - 1]['name']
            elif choice == len(folders) + 1:
                return 0, "ALL QR CODES"
        print("Invalid selection. Try again.")

def get_qr_codes(api_key, folder_id):
    all_codes = []
    page = 1

    while True:
        url = f"{API_BASE}/codes?access-token={api_key}&per-page=100&page={page}&folder_id={folder_id}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch QR codes on page {page}: {response.status_code} - {response.text}")
            break
        codes = response.json()
        if not codes:
            break
        all_codes.extend(codes)
        if len(codes) < 100:
            break
        page += 1
        time.sleep(0.11)  # <- Throttle to stay under 10 requests/sec

    return all_codes

def delete_qr_codes(api_key, qr_codes):
    deleted_codes_info = []

    for code in qr_codes:
        code_id = code['id']
        url = f"https://api.qr-code-generator.com/v1/codes/{code_id}?access-token={api_key}"
        response = requests.delete(url)
        if response.status_code == 204:
            print(f"Deleted QR Code ID: {code_id}")
            deleted_codes_info.append(code)
        else:
            print(f"Failed to delete QR Code ID {code_id}: {response.status_code} - {response.text}")
        time.sleep(0.11)  # <- Throttle each DELETE to avoid rate limits

    return deleted_codes_info

def write_csv_report(deleted_codes):
    # Specify the directory and filename
    directory = 'csv-exports'
    filename = 'deleted_qr_codes.csv'
    file_path = os.path.join(directory, filename)

    # Create the directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)  # This creates the directory if it doesn't exist

    # Open the file for writing
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=[
            'id', 'type_id', 'type_name', 'title',
            'short_code', 'short_url', 'target_url'
        ])
        writer.writeheader()

        # Write the data rows
        for code in deleted_codes:
            writer.writerow({
                'id': code.get('id'),
                'type_id': code.get('type_id'),
                'type_name': code.get('type_name'),
                'title': code.get('title'),
                'short_code': code.get('short_code'),
                'short_url': code.get('short_url'),
                'target_url': code.get('target_url')
            })

    print(f"\nCSV report saved as '{file_path}'.")

def main():
    print("QR Code Batch Deletion Tool\n------------------------")
    api_key = get_api_key()

    # Step 1: Get folders
    account_data = get_account_info(api_key)
    folders = account_data.get("folders", [])

    # Step 2: Let user pick a folder or all
    folder_id, folder_name = choose_folder(folders)
    print(f"\nSelected Folder: {folder_name} (ID: {folder_id})")

    # Step 3: Get QR codes
    qr_codes = get_qr_codes(api_key, folder_id)
    if not qr_codes:
        print("No QR codes found.")
        return

    #Step 4: Confirm deletion
    print(f"\nYou are about to permanently delete {len(qr_codes)} QR Code(s).")
    confirm = input("Would you like to proceed? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Operation cancelled. No QR codes were deleted.")
        return

    # Step 5: Delete each QR code
    deleted_codes = delete_qr_codes(api_key, qr_codes)

    # Step 6: Ask to save report
    if deleted_codes:
        choice = input("\nWould you like to save a CSV report of deleted QR codes? (y/n): ").lower()
        if choice == 'y':
            write_csv_report(deleted_codes)
        else:
            print("No report saved.")
    else:
        print("No QR codes were deleted.")

    print("\n✅ Process complete.")

if __name__ == "__main__":
    main()
