# Dynamic Website QR Code Rebuilds

This script allows you to rebuild QR codes across two different accounts, Account A and Account B, by:

1. Fetching QR code data from Account A.
2. Creating corresponding QR codes in Account B.
3. Deleting the original QR codes in Account A.
4. Updating the short URLs in Account B to match the originals.

## Features

- **Fetch QR Codes**: Pulls QR code data from a specific folder in Account A.
- **Create QR Codes**: Creates corresponding QR codes in Account B.
- **Delete QR Codes**: Deletes QR codes from Account A after they've been recreated in Account B.
- **Update Short URLs**: Ensures that short URLs in Account B match the original ones from Account A.

## Requirements

- Python 3.x
- `requests` library (can be installed via `pip install requests`)
- API keys for both QR Code Generator accounts

## Setup

1. Clone the repository
2. Run main_script.py
3. Follow the prompts to enter your API keys for Account A and Account B. The script will:
    - Fetch the folder ID from Account A.
    - Retrieve the QR code data from the specified folder.
    - Create the QR codes in Account B.
    - Delete the original QR codes from Account A.
    - Update the short URLs for the created QR codes in Account B.
