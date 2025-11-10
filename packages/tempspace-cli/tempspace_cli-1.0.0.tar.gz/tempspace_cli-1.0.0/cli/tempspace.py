import argparse
import requests
import os
import sys
import hashlib
import multiprocessing
from tqdm import tqdm
from requests_toolbelt.multipart.encoder import MultipartEncoder, MultipartEncoderMonitor
from rich.console import Console
from rich.panel import Panel

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

def calculate_file_hash(filepath: str) -> str:
    """Calculate the SHA256 hash of a file in chunks."""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(CHUNK_SIZE), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except IOError as e:
        print(f"Error reading file for hashing: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    """Main function to handle argument parsing and file upload."""
    console = Console()

    parser = argparse.ArgumentParser(
        description="Upload a file to Tempspace.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("filepath", help="The path to the file you want to upload.")
    parser.add_argument("-t", "--time", type=str, default='24', help="Set the file's expiration time. Examples: '24h', '7d', '360' (hours).\nDefault: '24' (24 hours).")
    parser.add_argument("-p", "--password", type=str, help="Protect the file with a password.")
    parser.add_argument("--one-time", action="store_true", help="The file will be deleted after the first download.")
    parser.add_argument("--url", type=str, default=os.environ.get("TEMPSPACE_URL", DEFAULT_SERVER_URL), help=f"The URL of the Tempspace server.\nCan also be set with the TEMPSPACE_URL environment variable.\nDefault: {DEFAULT_SERVER_URL}")

    args = parser.parse_args()

    # --- Validate Inputs ---
    if not os.path.isfile(args.filepath):
        console.print(f"[bold red]Error:[/] File not found at '{args.filepath}'")
        sys.exit(1)

    hours = parse_time(args.time)
    if hours is None:
        console.print(f"[bold red]Error:[/] Invalid time format '{args.time}'. Use formats like '24h', '7d', or '360'.")
        sys.exit(1)

    # --- Hashing ---
    console.print("[cyan]Calculating file hash...[/]")
    client_hash = calculate_file_hash(args.filepath)
    console.print(f"  [cyan]- Hash:[/] {client_hash}")

    # --- Prepare Upload ---
    upload_url = f"{args.url.rstrip('/')}/upload"
    filename = os.path.basename(args.filepath)
    file_size = os.path.getsize(args.filepath)

    fields = {
        'hours': str(hours),
        'one_time': str(args.one_time).lower(),
        'client_hash': client_hash,
        'file': (filename, open(args.filepath, 'rb'), 'application/octet-stream')
    }
    if args.password:
        fields['password'] = args.password

    encoder = MultipartEncoder(fields=fields)
    response = None

    try:
        bar_format = "{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [Speed: {rate_fmt}, ETA: {remaining}]"
        with tqdm(total=encoder.len, unit='B', unit_scale=True, desc=f"Uploading {filename}", bar_format=bar_format) as pbar:
            monitor = MultipartEncoderMonitor(encoder, lambda m: pbar.update(m.bytes_read - pbar.n))
            response = requests.post(upload_url, data=monitor, headers={'Content-Type': monitor.content_type})

    except FileNotFoundError:
        console.print(f"[bold red]Error:[/] The file '{args.filepath}' was not found.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        console.print("\n[bold red]An error occurred while connecting to the server:[/]")
        console.print(e)
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]An unexpected error occurred:[/] {e}")
        sys.exit(1)
    finally:
        # Ensure the file handle is closed
        if 'file' in fields and not fields['file'][1].closed:
            fields['file'][1].close()

    # --- Handle Response ---
    if response is not None:
        if response.status_code == 200:
            console.print("\n[bold green]Upload successful![/]")
            console.print(Panel(response.text.strip(), title="[bold cyan]Download Link[/]", border_style="green"))
        else:
            console.print(f"\n[bold red]Error:[/] Upload failed with status code {response.status_code}")
            try:
                error_details = response.json()
                console.print(f"[red]Server message:[/] {error_details.get('detail', 'No details provided.')}")
            except requests.exceptions.JSONDecodeError:
                console.print(f"[red]Server response:\n[/]{response.text}")
            sys.exit(1)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
