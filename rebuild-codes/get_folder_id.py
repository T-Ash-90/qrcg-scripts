import requests
import sys

def get_folder_id(api_key_a):
    """
    Get the Folder ID for the 'REBUILDS' folder in ACCOUNT_A using the provided API key.
    """
    url = f"http://api.qr-code-generator.com/v1/account?access-token={api_key_a}&expand=folders,statistics"

    # Send the GET request to the API
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        folder_id = None

        # Loop through the 'folders' list to find the folder with title 'REBUILDS'
        for folder in data.get('folders', []):
            if folder.get('name') == "REBUILDS":
                folder_id = folder.get('id')
                break

        if folder_id:
            return folder_id
        else:
            print("Folder with title 'REBUILDS' not found.")
            return None
    else:
        print(f"Error: Unable to fetch data. Status code {response.status_code}")
        return None


# Check if the script is being run directly or imported
if __name__ == "__main__":
    if len(sys.argv) < 2:
        # If no command-line argument is provided, ask for input
        API_KEY_A = input("Please enter API_KEY_A: ")
        folder_id = get_folder_id(API_KEY_A)
    else:
        # If the script is called with a command-line argument, use that
        API_KEY_A = sys.argv[1]
        folder_id = get_folder_id(API_KEY_A)

    if folder_id:
        print(f"FOLDER_ID for 'REBUILDS': {folder_id}")
