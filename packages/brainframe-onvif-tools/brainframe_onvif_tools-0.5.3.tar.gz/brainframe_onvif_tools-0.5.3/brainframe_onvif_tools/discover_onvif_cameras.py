#!/usr/bin/env python3
"""
discover_onvif_cameras.py — Discover ONVIF-capable devices across all LAN interfaces.

Output config.csv format:
  <add_stream, load_settings, start_analyzing>
  # ip:port,username,password,manufacturer,model,serial_number,audio_in,audio_out,auth_required,rtsp_url
  192.168.1.10:80,,,,,,,,,,,,,
  192.168.1.11:8080,admin,password,HIKVISION,DS-2CD2342WD-I,ABC123456,yes,no,yes,rtsp://...,,,
  </>

Examples:
  192.168.1.10:80
  192.168.1.11:8080,admin,password,HIKVISION,DS-2CD2342WD-I,ABC123456,yes,no,yes,rtsp://192.168.1.11:554/stream
"""

import os
import ipaddress
import concurrent.futures
import netifaces
import requests
import argparse
import csv
from pathlib import Path

try:
    from .command_utils import command, subcommand_parse_args, by_name
except ImportError:
    from command_utils import command, subcommand_parse_args, by_name

try:
    from wsdiscovery import WSDiscovery
    HAS_WSD = True
except ImportError:
    HAS_WSD = False

ONVIF_PORTS = [80, 81, 82, 83, 85, 88, 443, 554, 5000, 8080, 8081, 8899, 8999, 60002]
MAX_WORKERS = 150


def get_local_networks():
    nets = {}
    for iface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(iface)
        if netifaces.AF_INET not in addrs:
            continue
        ipv4 = addrs[netifaces.AF_INET][0]
        addr, netmask = ipv4.get("addr"), ipv4.get("netmask")
        if not addr or not netmask:
            continue
        try:
            network = ipaddress.IPv4Network(f"{addr}/{netmask}", strict=False)
            if not str(network).startswith("127."):
                nets[iface] = str(network)
        except Exception:
            pass
    return nets


def ws_discover():
    if not HAS_WSD:
        print("⚠️  WS-Discovery not available (install 'wsdiscovery'). Skipping.\n")
        return []

    print("Attempting WS-Discovery broadcast...")
    try:
        wsd = WSDiscovery()
        wsd.start()
        services = wsd.searchServices()
        wsd.stop()
    except Exception as e:
        print(f"⚠️  WS-Discovery failed: {e}")
        return []

    addresses = []
    for s in services:
        for xaddr in s.getXAddrs():
            if "http://" in xaddr:
                try:
                    ip = xaddr.split("//")[1].split("/")[0].split(":")[0]
                    if ip and ip not in addresses and not ip.startswith("[fe80"):
                        addresses.append(ip)
                except Exception:
                    pass

    if addresses:
        print(f"✅ WS-Discovery found {len(addresses)} addresses: {', '.join(addresses)}\n")
    else:
        print("No devices responded to WS-Discovery.\n")
    return addresses


def is_onvif_device(ip, ports=ONVIF_PORTS, timeout=1.5):
    for port in ports:
        try:
            url = f"http://{ip}:{port}/onvif/device_service"
            r = requests.get(url, timeout=timeout)
            if r.status_code in (200, 401, 404, 405) or "onvif" in r.text.lower():
                return port
        except requests.exceptions.RequestException:
            continue
    return None


def scan_subnet(subnet_str, workers=MAX_WORKERS):
    net = ipaddress.IPv4Network(subnet_str, strict=False)
    print(f"\nScanning network {subnet_str} on ports {ONVIF_PORTS} (workers={workers}) ...\n")
    found = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(is_onvif_device, str(ip)): str(ip) for ip in net.hosts()}
        for f in concurrent.futures.as_completed(futures):
            ip = futures[f]
            try:
                port = f.result()
                if port:
                    print(f"✅ Found potential ONVIF device at {ip}:{port}")
                    found.append((ip, port))
            except Exception:
                pass
    return found


@command("discover")
def discover_main(is_command=True):
    parser = argparse.ArgumentParser(description="Discover ONVIF devices on your LAN(s).")
    parser.add_argument("--auto", action="store_true", help="Run WS-Discovery + all subnet scans (no prompts).")
    HOME_DIR = os.environ.get('APP_HOME', '.')
    parser.add_argument("--output", default=os.path.join(HOME_DIR, "config.csv"), help="Output config file.")
    
    args = subcommand_parse_args(parser, is_command)

    all_found = []
    nets = get_local_networks()
    if not nets:
        print("❌ No active IPv4 networks found."); return
    iface_list = list(nets.items())

    if args.auto:
        print("Running automatic WS-Discovery + all subnet scans...\n")
        if HAS_WSD:
            all_found.extend([(ip, 80) for ip in ws_discover()])
        for _, net in iface_list:
            all_found.extend(scan_subnet(net))
    else:
        # Interactive mode remains the same
        print("Select network(s) to scan:")
        print("[1] WS-Discovery (recommended)")
        for i, (iface, net) in enumerate(iface_list, 2): print(f"[{i}] {iface:<10} → {net}")
        print(f"[{len(iface_list)+2}] all")
        print(f"[{len(iface_list)+3}] skip")
        choice_str = input("\n> (default: 1; comma-separated for multiple) ").strip().lower() or "1"
        choices = [c.strip() for c in choice_str.split(',')]

        for choice in choices:
            if choice == "1":
                all_found.extend([(ip, 80) for ip in ws_discover()])
            elif choice == str(len(iface_list)+2) or choice == "all":
                for _, net in iface_list: all_found.extend(scan_subnet(net))
            elif choice == str(len(iface_list)+3) or choice == "skip":
                print("Skipping subnet scan.\n")
            else:
                try:
                    idx = int(choice)
                    if 2 <= idx < len(iface_list) + 2:
                        all_found.extend(scan_subnet(iface_list[idx-2][1]))
                    else: print("❌ Invalid selection.");
                except ValueError: print("❌ Invalid input.");

    # Deduplicate and sort
    seen = set()
    unique_found = []
    for ip, port in all_found:
        key = f"{ip}:{port}"
        if key not in seen:
            seen.add(key)
            unique_found.append((ip, port))
    unique_found.sort(key=lambda x: (ipaddress.ip_address(x[0]), x[1]))

    if not unique_found:
        print("No ONVIF devices found.")
        return

    print("\nDiscovered ONVIF-capable devices:")
    for ip, port in unique_found: print(f" - {ip}:{port}")

    output_file = Path(args.output)
    with open(output_file, "w", newline="") as f:
        # Write the opening tag
        f.write("<add_stream, load_settings, start_analyzing>\n")
        # Write the header with # prefix including the new json column
        f.write("# ip:port,username,password,manufacturer,model,serial_number,audio_in,audio_out,auth_required,encoding,width,height,framerate,bitrate,system_datetime,rtsp_url,osd,json\n")
        # Write the discovered devices
        for ip, port in unique_found:
            f.write(f"{ip}:{port}\n")
        # Write the closing tag
        f.write("</>\n")

    # Change the print statement to show the absolute path
    absolute_output_path = Path(output_file).resolve()
    print(f"\n✅ Saved {len(unique_found)} addresses to: {absolute_output_path}")


if __name__ == "__main__":
    by_name["discover"](False)

