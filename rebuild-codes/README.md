# Dynamic Website QR Code Rebuilds

This script allows you to rebuild QR codes across two different accounts, Account A and Account B.

## Requirements

- Python 3.x
- `requests`
- `rich`
  
- API keys for both QR Code Generator accounts
- The QR Codes that are to be rebuilt must be Dynamic Website QR Codes
- The QR Codes that are to be rebuilt must be in Account A in a folder named REBUILDS

## Setup

1. Clone the repository
2. Run the main script: `run_rebuild_script.py`
3. Follow the prompts to enter your API keys for Account A and Account B. The script will:
    - Fetch the folder ID from Account A.
    - Retrieve the QR code data from the specified folder.
    - Create the QR codes in Account B.
    - Delete the original QR codes from Account A.
    - Update the short URLs for the created QR codes in Account B.
