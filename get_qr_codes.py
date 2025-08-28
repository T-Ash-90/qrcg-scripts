# Script to get the list of QR Codes to be rebuilt and export as CSV

import requests
import csv
import json
import os

def get_qr_codes(api_key, folder_id):
    """
    Fetch QR Code data from the 'REBUILDS' folder.
    This function handles pagination and returns a list of QR code data.
    """
    qr_codes = []
    page = 1

    while True:
        # URL for the API call with pagination
        url = f"http://api.qr-code-generator.com/v1/codes?access-token={api_key}&per-page=100&page={page}&folder_id={folder_id}"

        # Send the GET request to the API
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()

            # If the response is a list, handle it directly
            if isinstance(data, list):
                # If the list is empty, break out of the loop
                if not data:
                    break
                qr_codes.extend(data)

            # If there are no QR codes in the response, break out of the loop
            if len(data) < 100:
                break

            # Otherwise, move to the next page
            page += 1
        else:
            print(f"Error: Unable to fetch data. Status code {response.status_code}")
            break

    return qr_codes

def process_qr_codes(qr_codes):
    """
    Process the fetched QR codes to extract necessary details and determine DOMAIN_ID.
    Returns a list of dictionaries with the processed data.
    """
    processed_data = []

    for qr in qr_codes:
        # Extract necessary details from the QR code
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

    # Reverse the list here before returning
    processed_data.reverse()

    return processed_data

def get_domain_id(short_url):
    """
    Determine the DOMAIN_ID based on the short URL.
    """
    if short_url.startswith("http://q-r.to/"):
        return 1
    elif short_url.startswith("http://l.ead.me/"):
        return 2
    elif short_url.startswith("https://l.ead.me/"):
        return 3
    elif short_url.startswith("https://qrco.de/"):
        return 4
    return None  # Default if no match found

def save_to_csv(data, folder="csv-exports", filename="qr_codes.csv"):
    """
    Save the processed QR code data to a CSV file in the specified folder.
    If the folder does not exist, it will be created.
    """
    # Ensure the 'csv-exports' folder exists, if not create it
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Reverse the data so the rows are written in reverse order
    data.reverse()

    # Define the full path to the CSV file
    filepath = os.path.join(folder, filename)

    # Define CSV fieldnames
    fieldnames = ['id', 'type_id', 'type_name', 'title', 'domain_id', 'short_code', 'short_url', 'target_url']

    # Write the data to the CSV file
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"Data has been saved to {filepath}")


# Check if the script is being run directly or imported
if __name__ == "__main__":
    # Ask for the API key if running standalone
    API_KEY_A = input("Please enter API_KEY_A: ")

    # You can also pass the folder_id directly, or import it from another script
    FOLDER_ID = input("Please enter the REBUILDS FOLDER_ID: ")  # In practice, this would be imported or passed in

    # Fetch the QR Codes data
    qr_codes = get_qr_codes(API_KEY_A, FOLDER_ID)

    # Process the data
    processed_data = process_qr_codes(qr_codes)

    # Save the data to a CSV
    save_to_csv(processed_data)
