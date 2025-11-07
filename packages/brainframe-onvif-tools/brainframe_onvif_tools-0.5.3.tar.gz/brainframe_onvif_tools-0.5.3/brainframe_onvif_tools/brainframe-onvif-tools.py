#!/usr/bin/env python3
"""
A unified command-line interface for ONVIF camera tools.
Provides discover, scan, and validate sub-commands.
"""
import sys
import argparse

# Import the main function from each of your tool scripts
from discover_onvif_cameras import main as discover_main
from scan_onvif_cameras import main as scan_main
from validate_onvif_cameras import main as validate_main

def main():
    # Main parser
    parser = argparse.ArgumentParser(
        description="BrainFrame ONVIF Camera Tools Suite.",
        formatter_class=argparse.RawTextHelpFormatter  # Keeps help message formatting clean
    )

    # This is where we will register the sub-commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands', required=True)

    # --- Discover Command ---
    parser_discover = subparsers.add_parser(
        'discover',
        help='Discover ONVIF-capable devices on the network.',
        description='Scans the local network(s) using WS-Discovery and subnet scans to find potential ONVIF cameras.'
    )
    # We don't define arguments here; the discover_main script will parse them.
    # We just link the command to the function.
    parser_discover.set_defaults(func=discover_main)

    # --- Scan Command ---
    parser_scan = subparsers.add_parser(
        'scan',
        help='Scan devices to find credentials and build a detailed inventory.',
        description='Reads IPs from config.csv, finds working credentials, and saves a detailed camera_onvif_info.json file.'
    )
    parser_scan.set_defaults(func=scan_main)

    # --- Validate Command ---
    parser_validate = subparsers.add_parser(
        'validate',
        help='Validate RTSP streams and find correct credentials.',
        description='Reads camera_onvif_info.json, tests each RTSP stream, applies firmware workarounds, and updates the inventory file.'
    )
    parser_validate.set_defaults(func=validate_main)

    # The magic: We parse only the first argument to know which command was chosen.
    # The rest of the arguments are left for the sub-script's own argparse to handle.
    # We use parse_known_args() which returns a tuple of (known_args, remaining_args)
    args, remaining_argv = parser.parse_known_args()

    # Reconstruct sys.argv for the target script, so it can parse its own arguments.
    # It should look like ['script_name.py', '--arg1', 'value1', ...]
    sys.argv = [sys.argv[0]] + remaining_argv

    # Call the function that was associated with the chosen sub-command
    args.func()

if __name__ == '__main__':
    main()