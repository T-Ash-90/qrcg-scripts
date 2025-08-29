# Create a Dynamic Website QR Code

import requests
import json
import re
import os

# Base API endpoint
base_url = 'https://api.qr-code-generator.com/v1/codes'

# Get user input for Title and URL
api_token = input("Enter your API token: ").strip()
url_input = input("Enter the URL for the QR Code: ").strip()
if not url_input.startswith(("http://", "https://")):
    url_input = "https://" + url_input
title = input("Enter the title for the QR Code: ").strip() or "My QR Code - API"

# Sanitize title for filename use
title_clean = title.replace(" ", "_")
safe_title = re.sub(r'[^A-Za-z0-9_-]', '', title_clean)

# POST endpoint for creating QR code
post_url = f'{base_url}?access-token={api_token}'

# Data payload with dynamic title and URL
data = {
    'typeId': 1,
    'title': title,
    'data': {
        'url': url_input
    }
}

# Headers
headers = {
    'Content-Type': 'application/json'
}

# Step 1: Make the POST request to create the QR code
response = requests.post(post_url, headers=headers, json=data)

# Step 2: Check if the request was successful
if response.status_code == 200:
    print("✅ QR Code generated successfully!")

    # Parse the JSON response
    response_data = response.json()
    created_id = response_data.get('id')
    image_url = response_data.get('image_url')  # Not used, but available

    if not created_id:
        print("⚠️ Could not retrieve ID from QR code creation response.")
    else:
        # Step 3: Make the second API call to get the list of QR codes
        get_url = f'{base_url}?access-token={api_token}&per-page=3'
        get_response = requests.get(get_url)

        if get_response.status_code == 200:
            codes_data = get_response.json()  # List of recent QR codes

            # Step 4: Search for the matching QR code by ID
            matched = None
            for code in codes_data:
                if code.get('id') == created_id:
                    matched = code
                    break

            # Step 5: Output the short URL if found
            if matched:
                short_url = matched.get('short_url')
                print(f"🔗 Your QR Code has been created with the short URL: {short_url}")
            else:
                print("❌ Could not find the matching QR Code in the list.")

            # Step 6: Ask if user wants to download the QR code image
            download_choice = input("Do you want to download the QR code image? (y/n): ").strip().lower()
            if download_choice in ['y', 'yes'] and created_id:
                # Step 7: Download the image using the new endpoint
                download_url = f'https://api.qr-code-generator.com/v1/codes/{created_id}/download?access-token={api_token}&format=PNG'

                # Ensure the directory exists
                os.makedirs("png-exports", exist_ok=True)

                # Generate sanitized file name
                file_name = f"png-exports/{created_id}_{safe_title}.png"

                try:
                    img_response = requests.get(download_url)

                    if img_response.status_code == 200:
                        with open(file_name, 'wb') as file:
                            file.write(img_response.content)
                        print(f"✅ QR Code image has been downloaded as {file_name}!")
                    else:
                        print(f"❌ Failed to download the image. Status Code: {img_response.status_code}")
                except Exception as e:
                    print(f"❌ An error occurred while downloading the image: {e}")
            elif download_choice not in ['y', 'yes']:
                print("The QR code image will not be downloaded.")
        else:
            print(f"❌ Failed to fetch QR code list. Status Code: {get_response.status_code}")
else:
    print(f"❌ Error creating QR code: {response.status_code}")
    print("Response Text:", response.text)
