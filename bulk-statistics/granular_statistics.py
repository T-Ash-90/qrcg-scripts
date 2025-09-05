import csv
import requests
import time
from datetime import datetime
from io import StringIO
import os

# Function to fetch data from the API and parse the CSV response
def fetch_qr_code_data(qr_code_id, access_token, created_date):
    # Convert the 'Created' date to the required 'YYYY-MM-DD' format
    created_date_obj = datetime.strptime(created_date, "%Y-%m-%dT%H:%M:%S.%fZ") if 'T' in created_date else datetime.strptime(created_date, "%Y-%m-%d %H:%M:%S")
    from_date = created_date_obj.strftime("%Y-%m-%d")

    # Get today's date (current timestamp)
    to_date = datetime.now().strftime("%Y-%m-%d")

    # Build the API URL
    url = f"https://api.qr-code-generator.com/v1/export/{qr_code_id}?access-token={access_token}&type=totals&from={from_date}&to={to_date}"

    try:
        # Make the API request
        response = requests.get(url)

        # Check if the response is successful
        if response.status_code == 200:
            # Parse the CSV data returned in the response
            return parse_csv_response(response.text)  # Parse CSV response
        else:
            print(f"Failed to fetch data for QR Code {qr_code_id}: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching data for QR Code {qr_code_id}: {e}")
        return None

# Function to parse CSV response data
def parse_csv_response(csv_data):
    # Use StringIO to treat the CSV string like a file
    csv_file = StringIO(csv_data)
    reader = csv.DictReader(csv_file)

    # Convert the CSV to a list of dictionaries
    parsed_data = [row for row in reader]
    return parsed_data

# Function to save parsed data into a CSV file specific to the QR Code ID
def save_to_csv(parsed_data, qr_code_id, title, output_folder):
    if parsed_data or not parsed_data:  # Create file even if no data
        # Create a subfolder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Clean up the title to ensure it's a valid filename and no longer than 20 characters
        sanitized_title = (title.replace(" ", "_").replace(",", "").replace("/", "_")[:20]) if title else "No_Title"

        # Define the filename based on QR Code ID and Title
        output_filename = os.path.join(output_folder, f"{qr_code_id}_{sanitized_title}.csv")

        # Get the headers from the first row (since it's a list of dictionaries)
        fieldnames = parsed_data[0].keys() if parsed_data else ["Date/time", "Country Name", "Country ISO", "City", "Device", "Operating System", "Unique Visitor"]

        # Write the parsed data to a new CSV file
        with open(output_filename, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            if parsed_data:
                writer.writerows(parsed_data)  # Write the actual data
            else:
                # Write an empty row or just the header if no data is available
                writer.writerow({field: "" for field in fieldnames})

        print(f"Data for QR Code {qr_code_id} has been successfully saved!")
    else:
        print(f"No data to save for QR Code {qr_code_id}.")

# Main function to process the CSV and make the API calls
def process_qr_codes(csv_filename, access_token, output_folder):
    try:
        with open(csv_filename, mode='r') as file:
            # Read the CSV file
            reader = csv.DictReader(file)

            # Keep track of API call count
            call_count = 0

            for row in reader:
                qr_code_id = row.get("ID")  # Assuming the column in CSV is "ID"
                created_date = row.get("Created")  # Assuming the column in CSV is "Created"
                title = row.get("Title", "No_Title")  # Assuming the column in CSV is "Title"

                if qr_code_id and created_date:
                    # Call the function to fetch data for each QR code
                    parsed_data = fetch_qr_code_data(qr_code_id, access_token, created_date)

                    # Save the data to a CSV file named by the QR Code ID and Title
                    save_to_csv(parsed_data, qr_code_id, title, output_folder)

                    # Increment the call count
                    call_count += 1

                    # Check if we've made 10 API calls
                    if call_count >= 10:
                        print("Reached 10 API calls. Waiting for 1 second...")
                        time.sleep(1)  # Wait for 1 second to stay within the rate limit
                        call_count = 0  # Reset the call count after waiting
                else:
                    print(f"Skipping row due to missing ID or Created date: {row}")

    except FileNotFoundError:
        print(f"Error: The file '{csv_filename}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Get the access token from the user
    access_token = input("Enter your access token: ").strip()

    # Ask the user for the CSV file title
    csv_filename = input("Enter the CSV file name (full path, e.g., /Users/user1/qrcg-api-statistics/csv-exports/qrcg_statistics_12345.csv): ").strip()

    # Define the folder where all CSV files will be saved
    output_folder = "csv-exports/qr-code-exports"  # You can customize this folder name

    # Call the main function to process the CSV and make API calls
    process_qr_codes(csv_filename, access_token, output_folder)
