import csv
import requests
import time
import sys

def load_mapping_from_csv(file_path="csv-exports/qr_code_mapping.csv"):
    """
    Load the mapping data from the qr_code_mapping.csv file.
    Returns a list of dictionaries containing ID_A and ID_B.
    """
    mappings = []
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        mappings = [row for row in reader]

    return mappings

def delete_qr_code_in_account_a(api_key_a, id_a):
    """
    Delete the QR code in ACCOUNT_A by referencing ID_A.
    Treats status code 204 as success (successful deletion but no content returned).
    """
    url = f"https://api.qr-code-generator.com/v1/codes/{id_a}?access-token={api_key_a}"
    response = requests.delete(url)

    # If status code is 204, treat it as success
    if response.status_code == 200 or response.status_code == 204:
        print(f"Successfully deleted QR code with ID_A: {id_a}")
        return True
    else:
        print(f"Error: Unable to delete QR code with ID_A: {id_a}. Status code: {response.status_code}")
        return False

def delete_qr_codes_from_account_a(api_key_a, mapping_file="csv-exports/qr_code_mapping.csv"):
    """
    Load the QR code mappings and delete each QR code in ACCOUNT_A by referencing ID_A.
    Implements throttling to no more than 10 API calls per second.
    """
    # Load the QR code mappings from the CSV file
    mappings = load_mapping_from_csv(mapping_file)

    # Counter for API calls to handle throttling
    call_counter = 0
    start_time = time.time()

    # Loop through each mapping and delete the corresponding QR code in ACCOUNT_A
    for mapping in mappings:
        id_a = mapping.get('ID_A')

        if id_a:
            success = delete_qr_code_in_account_a(api_key_a, id_a)

            if not success:
                print(f"Failed to delete QR code with ID_A: {id_a}. Retrying after 1 second...")
                time.sleep(1)  # Retry after 1 second if there was an error

            call_counter += 1

            # Throttling: If 10 calls have been made, wait for the next second
            if call_counter >= 10:
                elapsed_time = time.time() - start_time
                if elapsed_time < 1:
                    sleep_time = 1 - elapsed_time  # Calculate how much longer to wait
                    print(f"Rate limit reached, sleeping for {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)  # Sleep to maintain throttling
                # Reset counter and start time for the next batch of 10 calls
                call_counter = 0
                start_time = time.time()

    print("Deletion process completed.")

# Check if the script is being run directly or imported
if __name__ == "__main__":
    # If running directly, ask for user input
    if len(sys.argv) < 2:
        API_KEY_A = input("Please enter API_KEY_A: ")
    else:
        # If called via subprocess, get the API key from command-line arguments
        API_KEY_A = sys.argv[1]

    # Start the deletion process
    delete_qr_codes_from_account_a(API_KEY_A)
