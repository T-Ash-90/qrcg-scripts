# QR Code Generator - Bulk QR Code Statistics

A Python script to fetch, analyze, and export QR code data from the [QR Code Generator API](https://www.qr-code-generator.com/) using your access token. Retrieve static and dynamic QR codes, display detailed statistics, and export data to CSV.

## Features

- Fetch static and dynamic QR codes from the API.
- Filter QR codes by creation date (optional).
- Display fetched QR code details in the terminal.
- Export fetched data to a CSV.
- Optionally request granular QR code data for each QR code, generating individual CSV files for each QR Code ID.

## Requirements

- Python 3.6 or higher
- Python packages:
  - `requests`
  - `rich`

## Setup & Usage

1. Clone the repository or download the script.
2. Obtain a QR Code Generator API access token from your QR Code Generator account.
3. Run the main script: `run_statistics_script.py`
4. Enter your API token when prompted.
5. Optionally, specify a date range to filter QR codes.
6. View QR code data and a summary in the terminal.
7. Export aggregate QR code data, Summary data and Granular QR code data (statistics per QR Code) as CSV files.

## CSV Export
- The main QR code data CSV includes:
  - ID, Created, Title, Short URL, Target URL, Solution Type, QR Code Type, Total Scans, Unique Scans.
- The Summary data allows users to view QR Code Type specific data. The CSV includes:
  - QR Code Type, QR Code Category, Count, Total Scans
- If granular data is requested, separate CSV files will be saved for each individual QR code with more detailed scan data:
  - Date/time, Country Name, Country ISO, City, Device, Operating System, Unique Visitor.

## Troubleshooting

- Ensure your API access token is valid.
- Verify that date inputs are in `YYYY-MM-DD` format.
