# Main script for Dynamic Website QR Code rebuilds

import subprocess
import time

def get_api_keys():
    API_KEY_A = input("Enter API Key for ACCOUNT_A: ")
    API_KEY_B = input("Enter API Key for ACCOUNT_B: ")
    return API_KEY_A, API_KEY_B

def get_folder_id(api_key_a):
    """
    Run the get_folder_id.py script to get the folder ID.
    """
    print("Fetching Folder ID...")
    # Pass the API key as a command-line argument
    result = subprocess.run(["python", "get_folder_id.py", api_key_a], capture_output=True, text=True)
    folder_id = result.stdout.strip()  # Assuming the script prints the folder ID
    return folder_id

def get_qr_codes(api_key_a, folder_id):
    """
    Run the get_qr_codes.py script to get the QR Codes data.
    """
    print("Fetching QR Codes data from ACCOUNT_A...")
    result = subprocess.run(["python", "get_qr_codes.py", api_key_a, folder_id], capture_output=True, text=True)
    # The script should save the CSV file, so we assume it's in a predefined location
    return "csv-exports/qr_codes.csv"

def create_qr_codes(api_key_b, csv_file_path):
    """
    Run the create_qr_codes.py script to create QR Codes in ACCOUNT_B.
    """
    print("Creating QR Codes in ACCOUNT_B...")
    result = subprocess.run(["python", "create_qr_codes.py", api_key_b, csv_file_path], capture_output=True, text=True)
    return "csv-exports/qr_code_mapping.csv"

def delete_qr_codes(api_key_a):
    """
    Run the delete_qr_codes.py script to delete QR Codes in ACCOUNT_A.
    """
    print("Deleting QR Codes from ACCOUNT_A...")
    result = subprocess.run(["python", "delete_qr_codes.py", api_key_a], capture_output=True, text=True)
    return result

def update_short_urls(api_key_b):
    """
    Run the update_short_urls.py script to update the short URLs in ACCOUNT_B.
    """
    print("Updating short URLs in ACCOUNT_B...")
    result = subprocess.run(["python", "update_short_urls.py", api_key_b], capture_output=True, text=True)
    return result

def main():
    # Step 1: Get API Keys
    API_KEY_A, API_KEY_B = get_api_keys()

    # Step 2: Get FOLDER_ID from get_folder_id.py
    folder_id = get_folder_id(API_KEY_A)

    # Step 3: Get QR Codes from ACCOUNT_A and save to CSV (get_qr_codes.py)
    qr_codes_csv = get_qr_codes(API_KEY_A, folder_id)

    # Step 4: Create QR Codes in ACCOUNT_B (create_qr_codes.py)
    qr_code_mapping_csv = create_qr_codes(API_KEY_B, qr_codes_csv)

    # Step 5: Delete QR Codes in ACCOUNT_A (delete_qr_codes.py)
    delete_qr_codes(API_KEY_A)

    # Step 6: Update short URLs in ACCOUNT_B (update_short_urls.py)
    update_short_urls(API_KEY_B)

    print("Rebuild process completed successfully!")

if __name__ == "__main__":
    main()
