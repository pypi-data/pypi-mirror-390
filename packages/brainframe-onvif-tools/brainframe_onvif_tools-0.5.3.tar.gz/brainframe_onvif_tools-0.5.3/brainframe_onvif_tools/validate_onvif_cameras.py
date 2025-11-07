#!/usr/bin/env python3
"""
validate_onvif_cameras.py — Discovers correct RTSP credentials for cameras in an inventory,
applies specific, targeted workarounds for buggy firmware, takes snapshots, and updates all records.
"""
import os
import argparse
import json
import csv
import subprocess
from pathlib import Path
from shutil import which
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

try:
    from .command_utils import command, subcommand_parse_args, by_name
    # Import snapshot functionality
    from .take_snapshot import take_snapshot_from_main_profile
except ImportError:
    from command_utils import command, subcommand_parse_args, by_name
    # Import snapshot functionality
    from take_snapshot import take_snapshot_from_main_profile

# The FALLBACK_CREDENTIALS list is removed to prevent brute-force behavior.

def apply_firmware_workarounds(rtsp_url, device_ip, manufacturer, model):
    """Applies known URL corrections for specific buggy camera models and streams."""
    
    if model == "DS-2CD2342WD-I":
        try:
            parsed = urlparse(rtsp_url); params = parse_qs(parsed.query)
            if 'profile' in params:
                del params['profile']
                return parsed._replace(query=urlencode(params, doseq=True)).geturl()
        except Exception:
            return rtsp_url

    if manufacturer == "Tyco Security Products" and model == "Illustra Pro 2MP Minidome indoor":
        if 'StreamId=1' in rtsp_url:
            try:
                corrected_url = f"rtsp://{device_ip}:554/StreamId=1"
                
                if ";Audio?Codec" in rtsp_url:
                    audio_params_start = rtsp_url.find(';Audio?Codec')
                    audio_suffix = rtsp_url[audio_params_start:]
                    return corrected_url + audio_suffix
                
                return corrected_url
            except Exception:
                return rtsp_url
            
    return rtsp_url


def validate_and_get_stream_info(rtsp_url, username, password):
    """Probes a single RTSP stream. On success, returns the detailed stream info."""
    if not which("ffprobe"): return False, None, "ffprobe not found"

    if username:
        parsed = urlparse(rtsp_url)
        netloc = f"{username}:{password}@{parsed.hostname}"
        if parsed.port: netloc += f":{parsed.port}"
        url_for_probe = parsed._replace(netloc=netloc).geturl()
    else:
        url_for_probe = rtsp_url

    command = [
        "ffprobe", "-v", "error", "-rtsp_transport", "tcp",
        "-show_streams", "-print_format", "json", "-i", url_for_probe,
    ]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=10)
        if result.returncode == 0 and result.stdout:
            try:
                details = json.loads(result.stdout)
                if "streams" in details and details["streams"]:
                    return True, details, ""
            except json.JSONDecodeError:
                return False, None, "Failed to parse ffprobe JSON output."
        error = result.stderr.strip()
        error_line = error.splitlines()[-1] if error else f"Exited with code {result.returncode} and no stream data."
        return False, None, error_line
    except subprocess.TimeoutExpired:
        return False, None, "Connection timed out."
    except Exception as e:
        return False, None, str(e)


def embed_credentials_in_rtsp_url(rtsp_url, username, password):
    """Embed credentials into RTSP URL in the format rtsp://user:pass@host:port/path"""
    if not rtsp_url:
        return ""
    
    # If credentials are empty, return URL as-is
    if not username and not password:
        return rtsp_url
    
    try:
        parsed = urlparse(rtsp_url)
        # Build new netloc with credentials
        netloc = f"{username}:{password}@{parsed.hostname}"
        if parsed.port:
            netloc += f":{parsed.port}"
        # Reconstruct URL with credentials
        return parsed._replace(netloc=netloc).geturl()
    except Exception:
        return rtsp_url


def extract_video_encoder_info(streams):
    """Extract video encoder information from ONVIF video_encoder configuration.
    
    Prefers video_encoder section (camera's configured limits) over ffprobe details.
    Returns tuple: (encoding, width, height, framerate, bitrate)
    """
    encoding = ""
    width = ""
    height = ""
    framerate = ""
    bitrate = ""
    
    # Look for the first validated stream with video_encoder configuration
    for stream in streams:
        if not stream.get('validated'):
            continue
        
        # Priority 1: Use video_encoder section from ONVIF (configured limits)
        video_encoder = stream.get('video_encoder')
        if video_encoder:
            # Extract encoding (e.g., "H264" -> "h264")
            encoding = video_encoder.get('encoding', '').lower()
            
            # Extract resolution from video_encoder
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
        
        # Priority 2: Fall back to ffprobe details if no video_encoder section
        details = stream.get('details')
        if details and details.get('codec_type') == 'video':
            # Extract encoding (codec name)
            if not encoding:
                encoding = details.get('codec_name', '')
            
            # Extract resolution from details if not already set
            if not width:
                width = str(details.get('width', ''))
            if not height:
                height = str(details.get('height', ''))
            
            # Note: We don't use r_frame_rate from ffprobe as it's the instantaneous rate,
            # not the configured limit. Only use if we have no other option.
            if not framerate:
                r_frame_rate = details.get('r_frame_rate', '')
                if r_frame_rate and '/' in r_frame_rate:
                    try:
                        num, denom = r_frame_rate.split('/')
                        if int(denom) != 0:
                            framerate = str(int(int(num) / int(denom)))
                    except (ValueError, ZeroDivisionError):
                        framerate = r_frame_rate
            
            # Extract bitrate from details if not already set
            if not bitrate:
                bit_rate = details.get('bit_rate', '')
                if bit_rate:
                    try:
                        # Convert from bps to kbps
                        bitrate = str(int(int(bit_rate) / 1000))
                    except (ValueError, TypeError):
                        bitrate = str(bit_rate)
            
            # Found video stream, break if we have encoding
            if encoding:
                break
    
    return encoding, width, height, framerate, bitrate


def update_camera_config(config_file, data, rtsp_url="", username="", password=""):
    """Updates the config.csv file with validated info, preserving manual json column."""
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

    # Extract video encoder information from validated streams
    encoding, width, height, framerate, bitrate = extract_video_encoder_info(data.get('rtsp_streams', []))
    
    # Embed credentials into RTSP URL
    rtsp_url_with_creds = embed_credentials_in_rtsp_url(rtsp_url, username, password)
    
    # Add new entry with all fields including rtsp_url with embedded credentials and video encoder info
    new_entry = [
        f"{data['ip']}:{data['port']}",
        username, # Use the explicitly passed username
        password, # Use the explicitly passed password
        data.get("manufacturer", ""),
        data.get("model", ""),
        data.get("serial", ""),
        "yes" if data.get("has_audio_input") else "no",
        "yes" if data.get("has_audio_output") else "no",
        "no" if not username else "yes",
        encoding,
        width,
        height,
        framerate,
        bitrate,
        system_datetime_str,
        rtsp_url_with_creds,
        osd_text,
        original_json_data # Add the preserved json data
    ]
    new_rows.append(new_entry)

    # Write file with proper format
    with open(config_file, "w", newline="") as f:
        f.write("<add_stream, load_settings, start_analyzing>\n")
        f.write(header + "\n")
        writer = csv.writer(f)
        writer.writerows(new_rows)
        f.write("</>\n")
    
    print(f"    💾 Confirmed credentials and settings saved to {config_file}")


@command("validate")
def validate_main(is_command=True):
    parser = argparse.ArgumentParser(description="Validate, enrich, discover RTSP credentials, take snapshots, and update all records.")
    HOME_DIR = os.environ.get('APP_HOME', '.')
    parser.add_argument("--json_file", default=os.path.join(HOME_DIR, "camera_onvif_info.json"), help="Input/Output JSON inventory file.")
    parser.add_argument("--input", default=os.path.join(HOME_DIR, "config.csv"), help="Input/Output config master file.")
    parser.add_argument("--snapshot-dir", default=os.path.join(HOME_DIR, "snapshots"), help="Directory to save camera snapshots (default: ./snapshots)")
    parser.add_argument("--skip-snapshots", action="store_true", help="Skip taking snapshots during validation")
    # New arguments for providing an expert override
    parser.add_argument("--user", help="Username override. When provided, IGNORES credentials from the JSON file and uses this.")
    parser.add_argument("--password", help="Password for username override. Required if --user is provided.")
    args = subcommand_parse_args(parser, is_command)

    # Argument dependency check
    if args.user is not None and args.password is None:
        parser.error("--password is required when --user is specified.")

    if not which("ffprobe"):
        print("❌ Error: 'ffprobe' is not installed or not in your system's PATH."); return

    json_file = Path(args.json_file);
    if not json_file.exists():
        print(f"❌ Error: JSON file not found at '{json_file}'"); return

    # Create snapshot directory
    snapshot_dir = Path(args.snapshot_dir)
    if not args.skip_snapshots:
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        print(f"📸 Snapshots will be saved to: {snapshot_dir}\n")

    with open(json_file, "r") as f: inventory = json.load(f)
    print(f"🔍 Validating and enriching RTSP streams from '{json_file}'...\n")

    for device in inventory.get("devices", []):
        ip, port, manufacturer, model = device.get("ip"), device.get("port", 80), device.get("manufacturer"), device.get("model")
        print(f"Camera: {ip} ({manufacturer} {model})")

        # The 'confirmed_creds' variable is preserved for minimal diff.
        # It is now assigned the single credential set to be used.
        if args.user is not None and args.password is not None:
            # Priority 1: CLI Override is used.
            confirmed_creds = (args.user, args.password)
            print(f"    ℹ️  Using CLI override credentials for user '{confirmed_creds[0]}'")
        else:
            # Priority 2: Default to credentials from the JSON file.
            confirmed_creds = (device.get("username", ""), device.get("password", ""))

        validated_rtsp_url = ""
        streams = device.get("rtsp_streams", [])
        if not streams: print("    ⚪ No RTSP streams to validate."); continue

        for stream in streams:
            stream_name, original_rtsp_url = stream.get("name"), stream.get("rtsp")
            if not original_rtsp_url or "metadata" in stream_name.lower():
                stream['validated'] = "skipped"; stream['details'] = None; continue

            corrected_rtsp_url = apply_firmware_workarounds(original_rtsp_url, ip, manufacturer, model)
            print(f"    ▶️ Testing RTSP stream '{stream_name}'...")
            
            is_valid, stream_details, error_msg = False, None, "No credentials confirmed yet."

            # The brute-force loop is gone. We only test with the single 'confirmed_creds'.
            is_valid, stream_details, error_msg = validate_and_get_stream_info(corrected_rtsp_url, confirmed_creds[0], confirmed_creds[1])
            
            if is_valid:
                print(" ✅ SUCCESS")
                stream['rtsp'] = corrected_rtsp_url
                stream['details'] = stream_details['streams'][0] if (stream_details and stream_details.get('streams')) else None
                # Store the first validated RTSP URL
                if not validated_rtsp_url:
                    validated_rtsp_url = corrected_rtsp_url
            else:
                 # Provide a more helpful failure message
                 user_str = f"user '{confirmed_creds[0]}'" if confirmed_creds[0] else "anonymous access"
                 print(f" ❌ FAILED (RTSP stream rejected credentials for {user_str}: {error_msg})")
            stream['validated'] = is_valid

        # Take snapshot from main profile if credentials confirmed
        if confirmed_creds and not args.skip_snapshots:
            print(f"    📸 Taking snapshot from main profile...")
            try:
                snapshot_path = take_snapshot_from_main_profile(
                    ip,
                    port,
                    confirmed_creds[0],
                    confirmed_creds[1],
                    snapshot_dir,
                    verbose=False
                )
                if snapshot_path:
                    print(f"    ✅ Snapshot saved: {snapshot_path}")
                else:
                    print(f"    ⚠️  Failed to take snapshot")
            except Exception as e:
                print(f"    ⚠️  Snapshot error: {e}")

        # The credentials used for the test are passed to update the config file.
        update_camera_config(args.input, device, validated_rtsp_url, confirmed_creds[0], confirmed_creds[1])
        print()

    with open(json_file, "w") as f:
        json.dump(inventory, f, indent=2)
    print(f"\n✅ Inventory file '{json_file}' has been updated with validation results and stream details.")
    if not args.skip_snapshots:
        print(f"✅ Snapshots saved to: {snapshot_dir}")


if __name__ == "__main__":
    by_name["validate"](False)

