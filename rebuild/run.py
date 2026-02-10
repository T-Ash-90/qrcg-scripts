import subprocess
import sys
from rich.console import Console

console = Console()

def get_api_keys():
    while True:
        API_KEY_A = console.input("[bold green]🔑  Enter API Key for ACCOUNT A (📍 source location):[/bold green] ")
        if API_KEY_A.strip():
            break
        console.print("[bold red]Error: API Key for ACCOUNT A cannot be blank![/bold red]")

    while True:
        API_KEY_B = console.input("[bold green]🔑  Enter API Key for ACCOUNT B (🎯 target location):[/bold green] ")
        if API_KEY_B.strip():
            break
        console.print("[bold red]Error: API Key for ACCOUNT B cannot be blank![/bold red]")

    return API_KEY_A, API_KEY_B

def get_folder_id(api_key_a):
    console.print("[bold cyan]📂 Fetching Folder ID...[/bold cyan]")

    result = subprocess.run(["python", "get_folder_id.py", api_key_a], capture_output=True, text=True)

    print(result.stdout)

    if "Error" in result.stdout:
        console.print(f"[bold red]Error: Failed to fetch Folder[/bold red]")
        sys.exit(1)

    folder_id = result.stdout.split(":")[1].strip()

    return folder_id

def get_qr_codes(api_key_a, folder_id):
    console.print("[bold cyan]📱 Fetching QR Code data from ACCOUNT_A...[/bold cyan]")

    result = subprocess.run(
        ["python", "get_qr_codes.py", api_key_a, folder_id], capture_output=True, text=True
    )

    if result.returncode != 0:
        console.print(f"[bold red]Error: Failed to fetch QR Codes.[/bold red] {result.stderr}")
        return None

    if "No QR Codes found" in result.stdout or not result.stdout.strip():
        console.print("[bold red]Error: No QR Codes Found[/bold red]")
        return None

    return "csv-exports/qr_codes.csv"

def get_designs(api_key_a):
    console.print("[bold cyan]🎨 Fetching QR Code designs from ACCOUNT_A...[/bold cyan]")
    result = subprocess.run(
        ["python", "get_designs.py", api_key_a],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        console.print(f"[bold red]Error: Failed to fetch designs.[/bold red] {result.stderr}")
        return False

    return True

def create_qr_codes(api_key_b, csv_file_path):
    console.print("[bold cyan]🔨 Creating QR Codes in ACCOUNT_B...[/bold cyan]")
    result = subprocess.run(["python", "create_qr_codes.py", api_key_b, csv_file_path], capture_output=True, text=True)

    if result.returncode != 0:
        console.print(f"[bold red]Error: Failed to create QR Codes in ACCOUNT_B.[/bold red] {result.stderr}")
        return None

    return "csv-exports/qr_code_mapping.csv"

def delete_qr_codes(api_key_a):
    console.print("[bold cyan]🚮 Deleting QR Codes from ACCOUNT_A...[/bold cyan]")
    result = subprocess.run(["python", "delete_qr_codes.py", api_key_a], capture_output=True, text=True)

    if result.returncode != 0:
        console.print(f"[bold red]Error: Failed to delete QR Codes in ACCOUNT_A.[/bold red] {result.stderr}")
        return False

    return True

def update_short_urls(api_key_b):
    console.print("[bold cyan]⏳ Updating short URLs in ACCOUNT_B...[/bold cyan]")
    result = subprocess.run(["python", "update_short_urls.py", api_key_b], capture_output=True, text=True)

    if result.returncode != 0:
        console.print(f"[bold red]Error: Failed to update short URLs in ACCOUNT_B.[/bold red] {result.stderr}")
        return False

    return True

def update_designs(api_key_b):
    console.print("[bold cyan]🎯 Applying designs to QR Codes in ACCOUNT_B...[/bold cyan]")
    result = subprocess.run(
        ["python", "update_designs.py", api_key_b],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        console.print(f"[bold red]Error: Failed to update designs.[/bold red] {result.stderr}")
        return False

    return True

def main():
    # Step 1: Get API Keys
    API_KEY_A, API_KEY_B = get_api_keys()

    # Step 2: Get FOLDER_ID (get_folder_id.py)
    folder_id = get_folder_id(API_KEY_A)
    if not folder_id:
        console.print("[bold red]Error: Unable to fetch Folder ID, exiting process.[/bold red]")
        return

    # Step 3: Get QR Codes from ACCOUNT_A and save to CSV (get_qr_codes.py)
    qr_codes_csv = get_qr_codes(API_KEY_A, folder_id)
    if not qr_codes_csv:
        console.print("[bold red]Error: Unable to fetch QR Codes, exiting process.[/bold red]")
        return
    
    # Step 4: Get QR Code Designs from ACCOUNT_A (get_designs.py)
    if not get_designs(API_KEY_A):
        console.print("[bold red]Error: Unable to fetch designs, exiting process.[/bold red]")
        return

    # Step 5: Create QR Codes in ACCOUNT_B (create_qr_codes.py)
    qr_code_mapping_csv = create_qr_codes(API_KEY_B, qr_codes_csv)
    if not qr_code_mapping_csv:
        console.print("[bold red]Error: Unable to create QR Codes in ACCOUNT_B, exiting process.[/bold red]")
        return

    # Step 6: Delete QR Codes in ACCOUNT_A (delete_qr_codes.py)
    if not delete_qr_codes(API_KEY_A):
        console.print("[bold red]Error: Unable to delete QR Codes in ACCOUNT_A, exiting process.[/bold red]")
        return

    # Step 7: Update short URLs in ACCOUNT_B (update_short_urls.py)
    if not update_short_urls(API_KEY_B):
        console.print("[bold red]Error: Unable to update short URLs in ACCOUNT_B, exiting process.[/bold red]")
        return
    
    # Step 8: Update designs in ACCOUNT_B (update_designs.py)
    if not update_designs(API_KEY_B):
        console.print("[bold red]Error: Unable to update designs in ACCOUNT_B, exiting process.[/bold red]")
        return

    console.print("[bold magenta]✅ Rebuild process completed successfully![/bold magenta]")

if __name__ == "__main__":
    main()
