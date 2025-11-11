import argparse
import requests
import os
import sys
import hashlib
import multiprocessing
from requests_toolbelt.multipart.encoder import MultipartEncoder, MultipartEncoderMonitor
import math
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import qrcode
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, BarColumn, TextColumn, TransferSpeedColumn, TimeRemainingColumn
from rich.console import Group
from rich.live import Live

# Default configuration
DEFAULT_SERVER_URL = "https://tempspace.fly.dev/"
CHUNK_SIZE = 1024 * 1024  # 1MB

def parse_time(time_str: str) -> int:
    """
    Parse a time string (e.g., '7d', '24h', '360') into an integer number of hours.
    Returns the number of hours as an integer, or None if parsing fails.
    """
    time_str = time_str.lower().strip()
    if time_str.endswith('d'):
        try:
            days = int(time_str[:-1])
            return days * 24
        except ValueError:
            return None
    elif time_str.endswith('h'):
        try:
            return int(time_str[:-1])
        except ValueError:
            return None
    else:
        try:
            return int(time_str)
        except ValueError:
            return None

def format_size(size_bytes: int) -> str:
    """Converts a size in bytes to a human-readable format."""
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

def main():
    """Main function to handle argument parsing and file upload."""
    console = Console()

    # --- Header ---
    console.print(Panel("[bold cyan]Tempspace File Uploader[/bold cyan]", expand=False, border_style="blue"))


    parser = argparse.ArgumentParser(
        description="Upload a file to Tempspace.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("filepath", nargs='?', default=None, help="The path to the file you want to upload.")
    parser.add_argument("-t", "--time", type=str, default='24', help="Set the file's expiration time. Examples: '24h', '7d', '360' (hours).\nDefault: '24' (24 hours).")
    parser.add_argument("-p", "--password", type=str, help="Protect the file with a password.")
    parser.add_argument("--one-time", action="store_true", help="The file will be deleted after the first download.")
    parser.add_argument("--url", type=str, default=os.environ.get("TEMPSPACE_URL", DEFAULT_SERVER_URL), help=f"The URL of the Tempspace server.\nCan also be set with the TEMPSPACE_URL environment variable.\nDefault: {DEFAULT_SERVER_URL}")
    parser.add_argument("--qr", action="store_true", help="Display a QR code of the download link.")
    parser.add_argument("--it", action="store_true", help="Enable interactive mode.")

    args = parser.parse_args()

    # --- Interactive Mode ---
    if args.it:
        args.filepath = Prompt.ask("Enter the path to the file you want to upload")
        args.time = Prompt.ask("Set the file's expiration time (e.g., '24h', '7d')", default='24')
        args.password = Prompt.ask("Protect the file with a password?", default=None, password=True)
        args.one_time = Confirm.ask("Delete the file after the first download?", default=False)
        args.qr = Confirm.ask("Display a QR code of the download link?", default=False)


    # --- Validate Inputs ---
    if not args.filepath or not os.path.isfile(args.filepath):
        console.print(Panel(f"[bold red]Error:[/] File not found at '{args.filepath}'", title="[bold red]Error[/bold red]", border_style="red"))
        sys.exit(1)

    hours = parse_time(args.time)
    if hours is None:
        console.print(Panel(f"[bold red]Error:[/] Invalid time format '{args.time}'. Use formats like '24h', '7d', or '360'.", title="[bold red]Error[/bold red]", border_style="red"))
        sys.exit(1)

    # --- Display File Details ---
    table = Table(title="File Details", show_header=False, box=box.ROUNDED, border_style="cyan")
    table.add_column("Field", style="bold")
    table.add_column("Value")
    table.add_row("File Name", os.path.basename(args.filepath))
    table.add_row("File Size", format_size(os.path.getsize(args.filepath)))
    table.add_row("Expiration", f"{hours} hours")
    table.add_row("Password", "[green]Yes[/green]" if args.password else "[red]No[/red]")
    table.add_row("One-Time Download", "[green]Yes[/green]" if args.one_time else "[red]No[/red]")
    console.print(table)


    # --- Prepare Upload ---
    upload_url = f"{args.url.rstrip('/')}"
    filename = os.path.basename(args.filepath)
    file_size = os.path.getsize(args.filepath)

    # --- Chunked Upload ---
    response = None
    try:
        # 1. Initiate Upload
        initiate_response = requests.post(f"{upload_url}/upload/initiate")
        initiate_response.raise_for_status()
        upload_id = initiate_response.json()['upload_id']

        # 2. Upload Chunks
        progress = Progress(
            TextColumn("[bold blue]{task.description}", justify="right"),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.1f}%", "•",
            TransferSpeedColumn(), "•",
            TimeRemainingColumn(),
        )

        with Live(Panel(progress, title="[cyan]Uploading[/cyan]", border_style="cyan", title_align="left")) as live:
            task_id = progress.add_task(filename, total=file_size)
            with open(args.filepath, 'rb') as f:
                chunk_number = 0
                while chunk := f.read(CHUNK_SIZE):
                    chunk_number += 1
                    chunk_data = {
                        'upload_id': upload_id,
                        'chunk_number': str(chunk_number)
                    }
                    files = {'file': (f'chunk_{chunk_number}', chunk, 'application/octet-stream')}

                    chunk_response = requests.post(
                        f"{upload_url}/upload/chunk",
                        data=chunk_data,
                        files=files
                    )
                    chunk_response.raise_for_status()
                    progress.update(task_id, advance=len(chunk))

        # 3. Finalize Upload
        console.print(Panel("[bold green]Finalizing upload...[/bold green]", border_style="green"))
        finalize_data = {
            'upload_id': upload_id,
            'filename': filename,
            'hours': str(hours),
            'one_time': str(args.one_time).lower(),
        }
        if args.password:
            finalize_data['password'] = args.password

        response = requests.post(f"{upload_url}/upload/finalize", data=finalize_data)
        response.raise_for_status()

    except FileNotFoundError:
        console.print(Panel(f"[bold red]Error:[/] The file '{args.filepath}' was not found.", title="[bold red]Error[/bold red]", border_style="red"))
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        if e.response:
            try:
                error_message = e.response.json().get('detail', e.response.text)
            except:
                error_message = e.response.text
        console.print(Panel(f"[bold red]An error occurred:[/] {error_message}", title="[bold red]Error[/bold red]", border_style="red"))
        sys.exit(1)
    except Exception as e:
        console.print(Panel(f"[bold red]An unexpected error occurred:[/] {e}", title="[bold red]Error[/bold red]", border_style="red"))
        sys.exit(1)

    # --- Handle Response ---
    if response is not None:
        if response.status_code == 200:
            download_link = response.text.strip()
            success_panel = Panel(f"[bold green]Upload successful![/bold green]\n\nDownload Link: {download_link}",
                                  title="[bold cyan]Success[/bold cyan]", border_style="green")
            console.print(success_panel)

            if args.qr:
                qr = qrcode.QRCode()
                qr.add_data(download_link)
                qr.make(fit=True)
                qr.print_ascii()
        else:
            try:
                error_details = response.json()
                error_message = error_details.get('detail', 'No details provided.')
            except requests.exceptions.JSONDecodeError:
                error_message = response.text
            console.print(Panel(f"[bold red]Error:[/] Upload failed with status code {response.status_code}\n[red]Server message:[/] {error_message}", title="[bold red]Error[/bold red]", border_style="red"))
            sys.exit(1)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
