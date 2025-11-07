#!/usr/bin/env python3
"""
Take Snapshot from ONVIF Camera
Simple tool to capture snapshots from individual cameras.
Snapshot filename uses IP address + timestamp for easy identification.
"""
import argparse
import sys
import requests
from pathlib import Path
from datetime import datetime

try:
    from .get_camera_onvif_info import get_onvif_info, fix_snapshot_uri
except ImportError:
    from get_camera_onvif_info import get_onvif_info, fix_snapshot_uri

def download_snapshot(snapshot_url, username, password, output_path=None, verbose=False, manufacturer=None):
    """
    Download a snapshot from the camera.
    
    Args:
        snapshot_url: URL to download snapshot from
        username: Camera username
        password: Camera password
        output_path: Path to save snapshot
        verbose: Print status messages
        manufacturer: Camera manufacturer (used to determine auth method)
    
    Returns:
        Path to saved snapshot or content bytes, None if failed
    """
    from requests.auth import HTTPBasicAuth, HTTPDigestAuth
    
    try:
        # Fix common URI issues (e.g., duplicate port numbers)
        snapshot_url = fix_snapshot_uri(snapshot_url)
        
        # Determine authentication method based on manufacturer
        # Dahua and QSee cameras typically require Digest authentication
        if manufacturer and (
            'dahua' in manufacturer.lower() or 
            'qsee' in manufacturer.lower()
        ):
            auth_methods = [
                ('Digest', HTTPDigestAuth(username, password)),
                ('Basic', HTTPBasicAuth(username, password)),
            ]
        else:
            # Most cameras use Basic auth
            auth_methods = [
                ('Basic', HTTPBasicAuth(username, password)),
                ('Digest', HTTPDigestAuth(username, password)),
            ]
        
        # Try authentication methods
        last_error = None
        for auth_name, auth in auth_methods:
            try:
                if username:
                    response = requests.get(snapshot_url, auth=auth, timeout=10)
                else:
                    response = requests.get(snapshot_url, timeout=10)
                
                if response.status_code == 200:
                    if output_path:
                        with open(output_path, 'wb') as f:
                            f.write(response.content)
                        if verbose:
                            file_size = len(response.content) / 1024  # KB
                            print(f"✅ Snapshot saved: {output_path} ({file_size:.1f} KB)")
                        return output_path
                    else:
                        return response.content
                else:
                    last_error = f"HTTP {response.status_code}"
                    # Try next auth method
                    continue
            except Exception as e:
                last_error = str(e)
                continue
        
        # All auth methods failed
        if verbose:
            print(f"❌ Failed to download snapshot: {last_error}")
    except Exception as e:
        if verbose:
            print(f"❌ Error downloading snapshot: {e}")
    return None


def take_snapshot_from_main_profile(ip, port, username, password, output_dir=".", verbose=True):
    """
    Take a snapshot from the main (first) profile of a camera.
    Saves snapshot with IP address + timestamp as filename.
    
    Returns:
        Path to saved snapshot or None if failed
    """
    try:
        if verbose:
            print(f"📸 Connecting to camera at {ip}:{port}...")
        
        # Get camera information
        result = get_onvif_info(ip, port, username, password, verbose=False)
        
        if result and result.get('rtsp_streams'):
            # Get manufacturer for auth method selection
            manufacturer = result.get('manufacturer', '')
            
            # Use the first profile (main profile)
            main_profile = result['rtsp_streams'][0]
            
            if 'snapshot_uri' in main_profile:
                profile_name = main_profile.get('name', 'main')
                if verbose:
                    print(f"   Using profile: {profile_name}")
                
                # Use IP address with timestamp as filename (replace dots with underscores)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{ip.replace('.', '_')}_{timestamp}.jpg"
                output_path = Path(output_dir) / filename
                
                # Show snapshot URL if verbose
                if verbose:
                    print(f"   Snapshot URL: {main_profile['snapshot_uri']}")
                
                # Download snapshot with manufacturer info for proper auth
                downloaded = download_snapshot(
                    main_profile['snapshot_uri'],
                    username,
                    password,
                    output_path,
                    verbose=verbose,
                    manufacturer=manufacturer
                )
                
                return downloaded
            else:
                if verbose:
                    print(f"❌ No snapshot URI available for main profile")
        else:
            if verbose:
                print(f"❌ Failed to get camera info or no profiles found")
        
        return None
    except Exception as e:
        if verbose:
            print(f"❌ Error taking snapshot: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Take snapshot from ONVIF camera. Filename format: IP_TIMESTAMP.jpg",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Take snapshot from main profile (default directory)
  %(prog)s --host 10.1.1.125 --user admin --password password
  
  # Custom output directory
  %(prog)s --host 10.1.1.125 --user admin --password password --output-dir ./images
  
  # Take snapshots from all profiles
  %(prog)s --host 10.1.1.125 --user admin --password password --all-profiles
  
Snapshot filename format: 10_1_1_125_20251021_143022.jpg (IP_TIMESTAMP.jpg)
        """
    )
    
    # Required and optional arguments
    parser.add_argument("--host", required=True, help="Camera IP address")
    parser.add_argument("--port", type=int, default=80, help="ONVIF port (default: 80)")
    parser.add_argument("--user", default="", help="Username (optional for anonymous access)")
    parser.add_argument("--password", default="", help="Password")
    parser.add_argument("--output-dir", default=".", help="Directory to save snapshot (default: current directory)")
    parser.add_argument("--all-profiles", action="store_true", help="Take snapshots from all profiles (not just main)")
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if args.all_profiles:
        # Download snapshots from all profiles
        print(f"📸 Connecting to {args.host}:{args.port}...")
        result = get_onvif_info(args.host, args.port, args.user, args.password, verbose=False)
        
        if result and result.get('rtsp_streams'):
            print(f"   Downloading snapshots from all profiles to: {output_dir}\n")
            
            # Get manufacturer for auth method selection
            manufacturer = result.get('manufacturer', '')
            
            success_count = 0
            for i, stream in enumerate(result['rtsp_streams']):
                if 'snapshot_uri' in stream:
                    profile_name = stream.get('name', f"profile_{i+1}")
                    print(f"Profile {i+1}: {profile_name}")
                    
                    # Use IP address + timestamp + profile number as filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{args.host.replace('.', '_')}_{timestamp}_profile{i+1}.jpg"
                    output_path = output_dir / filename
                    
                    downloaded = download_snapshot(
                        stream['snapshot_uri'],
                        args.user,
                        args.password,
                        output_path,
                        verbose=True,
                        manufacturer=manufacturer
                    )
                    if downloaded:
                        success_count += 1
                else:
                    print(f"Profile {i+1}: {stream.get('name', 'unknown')} - No snapshot URI available")
            
            if success_count > 0:
                sys.exit(0)
            else:
                print("\n❌ No snapshots were successfully captured")
                sys.exit(1)
        else:
            print("❌ Failed to connect to camera or no profiles found")
            sys.exit(1)
    else:
        # Take snapshot from main profile only (default behavior)
        snapshot_path = take_snapshot_from_main_profile(
            args.host,
            args.port,
            args.user,
            args.password,
            output_dir,
            verbose=True
        )
        
        if snapshot_path:
            sys.exit(0)
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()
