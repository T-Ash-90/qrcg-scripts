import requests
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text

console = Console()


def main():
    console.print(Panel.fit(
        "[bold cyan]q-r.to Short URL Updater[/bold cyan]\n",
        border_style="cyan"
    ))

    api_key = Prompt.ask("[bold yellow]Enter API Key[/bold yellow]")
    qr_code_id = Prompt.ask("[bold yellow]Enter QR Code ID[/bold yellow]")
    backhalf = Prompt.ask("[bold yellow]Enter desired backhalf[/bold yellow]")

    url = f"https://api.qr-code-generator.com/v1/codes/{qr_code_id}"
    params = {"access-token": api_key}

    payload = {
        "short_code": backhalf,
        "domain_id": 1
    }

    headers = {
        "Content-Type": "application/json"
    }

    console.print("\n[bold cyan]Updating QR Code…[/bold cyan]")

    try:
        response = requests.put(
            url,
            headers=headers,
            params=params,
            json=payload,
            timeout=15
        )

        if response.status_code in (200, 201):
            console.print(
                Panel.fit(
                    "[bold green]Success![/bold green]\n"
                    f"Short URL updated to: [bold]q-r.to/{backhalf}[/bold]",
                    border_style="green"
                )
            )
        else:
            console.print(
                Panel.fit(
                    Text.from_markup(
                        "[bold red]Update failed[/bold red]\n\n"
                        f"Status Code: {response.status_code}\n"
                        f"Response:\n{response.text}"
                    ),
                    border_style="red"
                )
            )

    except requests.exceptions.RequestException as e:
        console.print(
            Panel.fit(
                f"[bold red]Request error[/bold red]\n{e}",
                border_style="red"
            )
        )

if __name__ == "__main__":
    main()