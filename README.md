# QR Code Generator Automation Scripts

This repository contains a collection of Python scripts designed for automating tasks in the QR Code Generator platform.

## Features:
- API usage monitoring — Track your account’s API consumption.
- Bulk deletion — Remove large batches of QR Codes from folders or entire accounts.
- Bulk rebuild — Rebuild Dynamic Website QR Codes from one account to another.
- Statistics extraction — Retrieve global and per‑QR‑Code analytics.

## Requirements:
Install dependencies using:

```bash
pip install -r requirements.txt
```

## List of Scripts:
### 1. **API**
- Checks the API usage for an account. Monitor your account’s API usage and limits to avoid service interruptions.
### 2. **DELETE**
- Deletes a batch of QR Codes from a specific folder or account. Useful for cleanup or restructuring.
### 3. **REBUILD**
- Rebuild Dynamic Website QR Codes from one account to another. This deletes codes in one account and recreates them in another account. API keys for both accounts are required.
### 4. **STATS**
- Provides global and individual statistics for QR Codes within an account.

## Usage:
Run scripts directly in your terminal by navigating to the respective folders and initializing run.py
Examples:

```bash
python3 api/run.py
python3 delete/run.py
python3 rebuild/run.py
python3 stats/run.py
```

Follow instructions to complete the desired actions.
