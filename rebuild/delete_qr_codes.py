import csv
import requests
import time
import sys

def load_mapping_from_csv(file_path="csv-exports/qr_code_mapping.csv"):
    mappings = []
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        mappings = [row for row in reader]

    return mappings

def delete_qr_code_in_account_a(api_key_a, id_a):
    url = f"https://api.qr-code-generator.com/v1/codes/{id_a}?access-token={api_key_a}"
    response = requests.delete(url)

    if response.status_code == 200 or response.status_code == 204:
        print(f"Successfully deleted QR code with ID_A: {id_a}")
        return True
    else:
        print(f"Error: Unable to delete QR code with ID_A: {id_a}. Status code: {response.status_code}")
        return False

def delete_qr_codes_from_account_a(api_key_a, mapping_file="csv-exports/qr_code_mapping.csv"):
    mappings = load_mapping_from_csv(mapping_file)

    call_counter = 0
    start_time = time.time()

    for mapping in mappings:
        id_a = mapping.get('ID_A')

        if id_a:
            success = delete_qr_code_in_account_a(api_key_a, id_a)

            if not success:
                print(f"Failed to delete QR code with ID_A: {id_a}. Retrying after 1 second...")
                time.sleep(1)

            call_counter += 1

            if call_counter >= 10:
                elapsed_time = time.time() - start_time
                if elapsed_time < 1:
                    sleep_time = 1 - elapsed_time
                    print(f"Rate limit reached, sleeping for {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)

                call_counter = 0
                start_time = time.time()

    print("Deletion process completed.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        API_KEY_A = input("Please enter API_KEY_A: ")
    else:
        API_KEY_A = sys.argv[1]

    delete_qr_codes_from_account_a(API_KEY_A)
