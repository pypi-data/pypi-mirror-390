#!/usr/bin/env python3
import os
import argparse
import json
import socket
import csv
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

try:
    from .command_utils import command, subcommand_parse_args, by_name
    from .get_camera_onvif_info import get_onvif_info
except ImportError:
    from command_utils import command, subcommand_parse_args, by_name
    from get_camera_onvif_info import get_onvif_info

ONVIF_PORTS = [80, 81, 82, 83, 85, 88, 443, 5000, 8080, 8081, 8899, 8999, 60002]
# This is now a fallback for when credentials.txt is missing
DEFAULT_CREDENTIALS = [
    ("admin", "admin"),
    ("admin", "password"),
]

# New function to make credentials user-configurable
def read_credentials_file():
    """
    Reads credentials using a three-tiered fallback system:
    1. Looks for 'credentials.txt' in the current working directory.
    2. Looks for 'credentials.txt' in the same directory as the script package.
    3. Falls back to a hardcoded default list if no file is found.
    """
    # Path 1: Current working directory
    local_path = Path("credentials.txt")

    # Path 2: Same directory as the package
    package_dir = Path(__file__).parent.resolve()
    package_path = package_dir / "credentials.txt"

    creds_file_to_use = None
    if local_path.is_file():
        creds_file_to_use = local_path
        print(f"ℹ️  Loading credentials from local file: '{local_path.resolve()}'")
    elif package_path.is_file():
        creds_file_to_use = package_path
        print(f"ℹ️  Loading credentials from package file: '{package_path}'")

    # If a file was found, read it
    if creds_file_to_use:
        creds = []
        with open(creds_file_to_use, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "," in line:
                    user, password = line.split(",", 1)
                    creds.append((user.strip(), password.strip()))
        return creds

    # Path 3: Fallback to hardcoded defaults
    print("⚠️  Credential file not found in local or package directory. Using default credentials.")
    return DEFAULT_CREDENTIALS


def extract_video_encoder_info(rtsp_streams):
    """Extract video encoder information from ONVIF data.
    
    Returns tuple: (encoding, width, height, framerate, bitrate)
    """
    encoding = ""
    width = ""
    height = ""
    framerate = ""
    bitrate = ""
    
    # Look for the first stream with video_encoder configuration
    for stream in rtsp_streams:
        video_encoder = stream.get('video_encoder')
        if video_encoder:
            # Extract encoding (e.g., "H264" -> "h264")
            encoding = video_encoder.get('encoding', '').lower()
            
            # Extract resolution
            resolution = video_encoder.get('resolution', {})
            width = str(resolution.get('width', ''))
            height = str(resolution.get('height', ''))
            
            # Extract configured framerate limit
            framerate_limit = video_encoder.get('framerate_limit', '')
            if framerate_limit:
                framerate = str(framerate_limit)
            
            # Extract configured bitrate limit (already in kbps)
            bitrate_limit = video_encoder.get('bitrate_limit', '')
            if bitrate_limit:
                bitrate = str(bitrate_limit)
            
            # Found video encoder config, break
            if encoding:
                break
    
    return encoding, width, height, framerate, bitrate


def is_port_open(ip, port, timeout=1.5):
    """Quick TCP connection test."""
    try:
        sock = socket.create_connection((ip, port), timeout=timeout)
        sock.close()
        return True
    except Exception:
        return False


def parse_ip_port(ip_field):
    """Split ip:port format safely."""
    if ":" in ip_field:
        ip, port_str = ip_field.split(":", 1)
        try:
            return ip.strip(), int(port_str)
        except (ValueError, TypeError):
            return ip.strip(), None
    return ip_field.strip(), None


def try_combinations(ip, known_port=None, cli_user=None, cli_pass=None, debug=False):
    """Try known credentials first, then fallback ports & defaults with cleaner logging."""
    print(f"\n🔍 Checking {ip} ...", flush=True)

    # Prioritize known port
    ports_to_try = ONVIF_PORTS.copy()
    if known_port and str(known_port).isdigit():
        known_port = int(known_port)
        if known_port in ports_to_try:
            ports_to_try.remove(known_port)
        ports_to_try.insert(0, known_port)

    # Iterate through ports
    for port in ports_to_try:
        if not is_port_open(ip, port):
            continue

        # Priority 1: Anonymous Access.
        data = get_onvif_info(ip, port, "", "", verbose=debug)
        if data:
            print(f"    ✅ Success on port {port} (Authenticated anonymously)")
            return data

        # Priority 2: CLI Override. If provided, it's exclusive.
        if cli_user is not None and cli_pass is not None:
            data = get_onvif_info(ip, port, cli_user, cli_pass, verbose=debug)
            if data:
                print(f"    ✅ Success on port {port} (Authenticated with CLI override user: '{cli_user}')")
                return data
            else:
                print(f"    🚫 CLI override user '{cli_user}' failed on port {port}. No other credentials will be tried for this host.")
                return None # Stop immediately if the expert override fails.

        # Priority 3: Common Credentials from file (only runs if no CLI override).
        common_credentials = read_credentials_file()
        for username, password in common_credentials:
            data = get_onvif_info(ip, port, username, password, verbose=debug)
            if data:
                print(f"    ✅ Success on port {port} (Authenticated with user: '{username}')")
                return data
            # To prevent lockouts, wait briefly after a failed attempt.
            time.sleep(2)

    # If the loops complete without success, print one clean failure message.
    print(f"🚫 No working ONVIF port found for {ip}\n")
    return None


def read_ips_from_config(file_path):
    """Read IPs and optional known metadata from config.csv file."""
    if not Path(file_path).exists():
        return []

    entries = []
    with open(file_path, "r", newline="") as f:
        for line in f:
            line = line.strip()
            # Skip opening/closing tags and header lines
            if not line or line.startswith("<") or line.startswith("#"):
                continue
            
            # Parse CSV line
            row = list(csv.reader([line]))[0]
            if not row or not row[0].strip():
                continue
                
            ip_field = row[0].strip()
            ip, port = parse_ip_port(ip_field)
            # This script's purpose is discovery, so we only need the address.
            entries.append({
                "ip": ip,
                "port": port,
            })
    return entries


def update_camera_config(config_file, data, args):
    """Update config.csv with discovered info, preserving manual json column."""
    rows = []
    header = "# ip:port,username,password,manufacturer,model,serial_number,audio_in,audio_out,auth_required,encoding,width,height,framerate,bitrate,system_datetime,rtsp_url,osd,json"
    
    # Read existing file
    try:
        with open(config_file, "r", newline="") as f:
            for line in f:
                line = line.strip()
                # Skip opening/closing tags and header
                if not line or line.startswith("<") or line.startswith("#"):
                    continue
                row = list(csv.reader([line]))[0]
                if row and row[0].strip():
                    rows.append(row)
    except (FileNotFoundError, StopIteration): 
        pass

    updated_ip = data['ip']
    
    # Find original entry to preserve manual json column
    original_json_data = ""
    for r in rows:
        if urlparse(f"//{r[0]}").hostname == updated_ip:
            # The new header has 18 columns, so the json column is at index 17
            if len(r) > 17:
                original_json_data = r[17]
            break
            
    # Remove old entry for this IP
    new_rows = [r for r in rows if urlparse(f"//{r[0]}").hostname != updated_ip]

    # Get system datetime string
    system_datetime_str = ""
    if data.get('system_datetime'):
        system_datetime_str = data['system_datetime'].get('datetime_string', '')

    # Get OSD text (will be quoted in CSV writer if it contains commas)
    osd_text = data.get('osd_text', '') or ''

    # Extract video encoder information from ONVIF data
    encoding, width, height, framerate, bitrate = extract_video_encoder_info(data.get('rtsp_streams', []))

    # Get primary RTSP URL if available (without credentials - validate will add them later)
    rtsp_url = ""
    if data.get('rtsp_streams'):
        # Use first stream URL as-is, without embedded credentials
        rtsp_url = data['rtsp_streams'][0].get('rtsp', '')

    # Build new entry with all fields, including video encoder data from ONVIF
    new_entry = [
        f"{data['ip']}:{data['port']}",
        data.get("username", ""),
        data.get("password", ""),
        data.get("manufacturer", ""),
        data.get("model", ""),
        data.get("serial", ""),
        "yes" if data.get("has_audio_input") else "no",
        "yes" if data.get("has_audio_output") else "no",
        "no" if not data.get("username") else "yes",
        encoding,
        width,
        height,
        framerate,
        bitrate,
        system_datetime_str,
        rtsp_url,
        osd_text,
        original_json_data # Add the preserved json data
    ]
    new_rows.append(new_entry)

    # Conditionally sort rows
    if args.sort_by_serial_number:
        # Sort by serial number (column index 5), handling missing values
        new_rows.sort(key=lambda r: r[5] if len(r) > 5 and r[5] else "")

    # Write file with proper format
    with open(config_file, "w", newline="") as f:
        f.write("<add_stream, load_settings, start_analyzing>\n")
        f.write(header + "\n")
        writer = csv.writer(f)
        writer.writerows(new_rows)
        f.write("</>\n")


def scan_one(entry, config_file, args):
    """Wrapper to run scan and update config for a single device."""
    ip = entry["ip"]
    known_port = entry.get("port")
    
    # Pass the CLI override credentials from args down to the test function
    data = try_combinations(ip, known_port, args.user, args.password, debug=args.debug)
    if data:
        update_camera_config(config_file, data, args)
    return data


@command("scan")
def scan_main(is_command=True):
    parser = argparse.ArgumentParser(description="Scan ONVIF cameras and retrieve ONVIF information.")
    parser.add_argument("--host", help="Single IP to scan (e.g., 192.168.1.10). Bypasses file I/O and prints result.")
    parser.add_argument("--user", help="Username override. When provided, only this user will be tried after an anonymous attempt.")
    parser.add_argument("--password", help="Password for username override. Required if --user is provided.")
    HOME_DIR = os.environ.get('APP_HOME', '.')
    parser.add_argument("--input", default=os.path.join(HOME_DIR, "config.csv"), help="Input config file.")
    parser.add_argument("--output", default=os.path.join(HOME_DIR, "camera_onvif_info.json"), help="Output ONVIF JSON file.")
    parser.add_argument("--debug", action="store_true", help="Print detailed error messages for debugging.")
    parser.add_argument("--sort-by-serial-number", action="store_true", help="Sort the output by serial number instead of IP address.")
    args = subcommand_parse_args(parser, is_command)

    # Added argument dependency check
    if args.user is not None and args.password is None:
        parser.error("--password is required when --user is specified.")

    # If --host is used, perform a scan, print the full results, and then exit.
    if args.host:
        ip, port = parse_ip_port(args.host)
        # Pass command-line credentials to the scanning function.
        data = try_combinations(ip, port, args.user, args.password, debug=args.debug)
        if data:
            # Print the full, structured ONVIF info as formatted JSON to the console.
            print("\n--- ONVIF Info ---")
            print(json.dumps(data, indent=2))
        return

    # --- The following code only runs if --host is NOT provided ---

    results = []
    entries = read_ips_from_config(args.input)
    if not entries:
        print(f"⚠️ No IPs found in {args.input}");
        return

    for entry in entries:
        # The main loop now calls the restored scan_one wrapper
        data = scan_one(entry, args.input, args)
        if data:
            results.append(data)

    if results:
        # Sort results based on the CLI argument
        if args.sort_by_serial_number:
            results.sort(key=lambda d: d.get("serial", ""))
            
        output = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "devices": results,
        }
        with open(args.output, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\n✅ Inventory saved to {args.output}")
    else:
        print("\n🚫 No devices discovered.")


if __name__ == "__main__":
    by_name["scan"](False)

