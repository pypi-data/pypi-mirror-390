#!/usr/bin/env python3
"""
Enhanced ONVIF Camera Information Tool
Fetches comprehensive camera information including:
- Basic device info
- System date and time
- RTSP streams
- Snapshot URIs
- Video encoder settings
- OSD/Text overlay settings
- Imaging settings
- Audio capabilities
"""
import argparse
import json
from onvif import ONVIFCamera
from zeep.exceptions import Fault

import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from xml.etree import ElementTree as ET

def fix_snapshot_uri(uri):
    """
    Fix common issues in snapshot URIs returned by the ONVIF library.
    
    The python-onvif-zeep library has a bug where it duplicates port numbers
    for cameras on non-standard ports:
    - Bug: http://192.168.4.30:85:85/path
    - Fixed: http://192.168.4.30:85/path
    
    Args:
        uri: The snapshot URI from the ONVIF library
        
    Returns:
        Fixed URI with duplicate ports removed
    """
    import re
    
    if not uri:
        return uri
    
    # Fix duplicate port numbers (e.g., :85:85 → :85)
    # Pattern matches :PORT:PORT/ where both PORTs are identical
    pattern = r':(\d+):\1/'
    fixed_uri = re.sub(pattern, r':\1/', uri)
    
    # Also fix if duplicate port is at the end without trailing slash
    # Pattern matches :PORT:PORT at end of string or before query/fragment
    pattern = r':(\d+):\1($|[?#])'
    fixed_uri = re.sub(pattern, r':\1\2', fixed_uri)
    
    return fixed_uri


def get_system_datetime(device_service, verbose=False):
    """Get the camera's system date and time settings."""
    try:
        dt_info = device_service.GetSystemDateAndTime()
        date_time = dt_info.UTCDateTime or dt_info.LocalDateTime
        if date_time:
            datetime_string = f"{date_time.Date.Year}-{date_time.Date.Month:02d}-{date_time.Date.Day:02d} {date_time.Time.Hour:02d}:{date_time.Time.Minute:02d}:{date_time.Time.Second:02d}"
            return {
                "timezone": getattr(dt_info, "TimeZone", {}).get("TZ", "Unknown") if hasattr(dt_info, "TimeZone") else "Unknown",
                "dst_enabled": getattr(dt_info, "DaylightSavings", False),
                "date": {
                    "year": date_time.Date.Year,
                    "month": date_time.Date.Month,
                    "day": date_time.Date.Day
                },
                "time": {
                    "hour": date_time.Time.Hour,
                    "minute": date_time.Time.Minute,
                    "second": date_time.Time.Second
                },
                "datetime_string": datetime_string
            }
    except Exception as e:
        if verbose:
            print(f"  ⚠️  Could not get system date/time: {e}")
    return None


def get_snapshot_uri(media_service, profile_token, verbose=False):
    """
    Get the snapshot URI for a given profile.
    Automatically fixes buggy URIs from the ONVIF library.
    """
    try:
        snapshot_uri = media_service.GetSnapshotUri({"ProfileToken": profile_token})
        uri = snapshot_uri.Uri
        
        # Fix any issues with the URI (e.g., duplicate port numbers)
        fixed_uri = fix_snapshot_uri(uri)
        
        # Log if we fixed something
        if verbose and uri != fixed_uri:
            print(f"    🔧 Fixed snapshot URI:")
            print(f"       Original: {uri}")
            print(f"       Fixed:    {fixed_uri}")
        
        return fixed_uri
    except Exception as e:
        if verbose:
            print(f"  ⚠️  Could not get snapshot URI: {e}")
    return None


def get_video_encoder_configuration(media_service, profile_token, verbose=False):
    """Get video encoder settings for a profile."""
    try:
        configs = media_service.GetVideoEncoderConfigurations()
        for config in configs:
            result = {
                "name": getattr(config, "Name", "Unknown"),
                "token": config.token,
                "encoding": getattr(config, "Encoding", "Unknown"),
                "resolution": {
                    "width": config.Resolution.Width if hasattr(config, "Resolution") else None,
                    "height": config.Resolution.Height if hasattr(config, "Resolution") else None
                },
                "quality": getattr(config, "Quality", None),
                "framerate_limit": getattr(config.RateControl, "FrameRateLimit", None) if hasattr(config, "RateControl") else None,
                "bitrate_limit": getattr(config.RateControl, "BitrateLimit", None) if hasattr(config, "RateControl") else None,
                "encoding_interval": getattr(config.RateControl, "EncodingInterval", None) if hasattr(config, "RateControl") else None,
            }
            return result
    except Exception as e:
        if verbose:
            print(f"  ⚠️  Could not get video encoder configuration: {e}")
    return None


def get_osd_settings(media_service, profile, camera_info=None, verbose=False):
    """
    Get On-Screen Display (OSD) settings using multiple methods.
    
    Tries ONVIF first, then falls back to manufacturer-specific APIs.
    """
    # Try ONVIF GetOSDs() first (standard method)
    try:
        osd_configs = media_service.GetOSDs({"ConfigurationToken": profile.token})
        if osd_configs:
            osd_texts = []
            for osd in osd_configs:
                if hasattr(osd, "TextString"):
                    text = getattr(osd.TextString, "PlainText", None) or \
                           getattr(osd.TextString, "String", None)
                    if text:
                        osd_texts.append(text)
            
            if osd_texts:
                if verbose:
                    print(f"  ✅ OSD retrieved via ONVIF GetOSDs")
                return ", ".join(osd_texts)
    except Exception as e:
        if verbose:
            print(f"  ℹ️  ONVIF GetOSDs failed: {e}")
    
    # If ONVIF failed and we have camera info, try manufacturer-specific APIs
    if camera_info:
        manufacturer = camera_info.get('manufacturer', '').lower()
        
        if 'dahua' in manufacturer:
            if verbose:
                print(f"  🔍 Trying Dahua CGI API...")
            result = _get_dahua_osd(camera_info, verbose)
            if result:
                return result
        
        elif 'hikvision' in manufacturer or 'hik' in manufacturer:
            if verbose:
                print(f"  🔍 Trying Hikvision ISAPI...")
            result = _get_hikvision_osd(camera_info, verbose)
            if result:
                return result
        
        elif 'uniview' in manufacturer:
            if verbose:
                print(f"  🔍 Trying Uniview LAPI...")
            result = _get_uniview_osd(media_service, profile, verbose)
            if result:
                return result
        
        elif 'tyco' in manufacturer or 'illustra' in manufacturer:
            if verbose:
                print(f"  🔍 Trying Illustra iAPI...")
            result = _get_illustra_osd(camera_info, verbose)
            if result:
                return result
    
    return None


def _get_dahua_osd(camera_info, verbose=False):
    """Get OSD from Dahua camera via CGI API."""
    ip = camera_info['ip']
    port = camera_info.get('port', 80)
    username = camera_info.get('username', 'admin')
    password = camera_info.get('password', '')
    
    try:
        osd_texts = []
        
        # Get ChannelTitle
        url = f"http://{ip}:{port}/cgi-bin/configManager.cgi?action=getConfig&name=ChannelTitle"
        response = requests.get(url, auth=HTTPDigestAuth(username, password), timeout=5)
        
        if response.status_code == 200:
            for line in response.text.split('\n'):
                if 'table.ChannelTitle[0].Name' in line and '=' in line:
                    text = line.split('=', 1)[1].strip()
                    if text:
                        osd_texts.append(text)
        
        # Get VideoWidget custom titles
        url = f"http://{ip}:{port}/cgi-bin/configManager.cgi?action=getConfig&name=VideoWidget"
        response = requests.get(url, auth=HTTPDigestAuth(username, password), timeout=5)
        
        if response.status_code == 200:
            for line in response.text.split('\n'):
                if '.Text=' in line and '=' in line:
                    text = line.split('=', 1)[1].strip()
                    if text and text not in osd_texts:
                        osd_texts.append(text)
        
        if osd_texts:
            if verbose:
                print(f"  ✅ OSD retrieved via Dahua CGI API")
            return ", ".join(osd_texts)
            
    except Exception as e:
        if verbose:
            print(f"  ⚠️  Dahua CGI API failed: {e}")
    
    return None


def _get_hikvision_osd(camera_info, verbose=False):
    """
    Get OSD from Hikvision camera via ISAPI using a consolidated, robust method.
    This function probes all OSD element endpoints, including the Channel Name.
    """
    ip = camera_info['ip']
    port = camera_info.get('port', 80)
    username = camera_info.get('username', 'admin')
    password = camera_info.get('password', '')
    auth = HTTPDigestAuth(username, password)
    
    # To format the date/time, this function will now fetch it directly.
    dt = None
    try:
        cam = ONVIFCamera(ip, port, username, password)
        device_service = cam.create_devicemgmt_service()
        dt_info = device_service.GetSystemDateAndTime()
        dt_part = dt_info.UTCDateTime or dt_info.LocalDateTime
        if dt_part:
            from datetime import datetime
            dt = datetime(
                dt_part.Date.Year, dt_part.Date.Month, dt_part.Date.Day,
                dt_part.Time.Hour, dt_part.Time.Minute, dt_part.Time.Second
            )
    except Exception as e:
        if verbose:
            print(f"  ℹ️  Could not fetch Hikvision time for OSD formatting: {e}")

    found_osd_elements = {}
    
    try:
        # 1. Fetch the Channel Name TEXT from the correct endpoint
        channel_name_text = None
        url_channel_info = f"http://{ip}:{port}/ISAPI/System/Video/inputs/channels"
        try:
            response_channel = requests.get(url_channel_info, auth=auth, timeout=5)
            if response_channel.status_code == 200:
                root = ET.fromstring(response_channel.text)
                name_elem = root.find('.//{*}VideoInputChannel/{*}name')
                if name_elem is not None and name_elem.text:
                    channel_name_text = name_elem.text.strip()
        except Exception as e:
            if verbose:
                print(f"  ℹ️  Could not fetch Hikvision channel name: {e}")

        # 2. Fetch all OSD overlay settings
        url_main_overlay = f"http://{ip}:{port}/ISAPI/System/Video/inputs/channels/1/overlays"
        response_main = requests.get(url_main_overlay, auth=auth, timeout=5)

        if response_main.status_code == 200:
            root = ET.fromstring(response_main.text)
            
            # Check if Channel Name Overlay is enabled
            chan_name_overlay = root.find('.//{*}channelNameOverlay')
            if chan_name_overlay is not None:
                enabled_elem = chan_name_overlay.find('.//{*}enabled')
                if enabled_elem is not None and enabled_elem.text.lower() == 'true' and channel_name_text:
                    found_osd_elements['channel_name'] = channel_name_text

            # Check if DateTime Overlay is enabled and get its settings
            datetime_overlay = root.find('.//{*}DateTimeOverlay')
            if datetime_overlay is not None:
                enabled_elem = datetime_overlay.find('.//{*}enabled')
                if enabled_elem is not None and enabled_elem.text.lower() == 'true':
                    date_style_elem = datetime_overlay.find('.//{*}dateStyle')
                    if date_style_elem is not None and date_style_elem.text and date_style_elem.text.lower() != 'none':
                        found_osd_elements['date'] = date_style_elem.text.strip()

                    time_style_elem = datetime_overlay.find('.//{*}timeStyle')
                    if time_style_elem is not None and time_style_elem.text and time_style_elem.text.lower() != 'none':
                        found_osd_elements['time'] = time_style_elem.text.strip()

                    week_elem = datetime_overlay.find('.//{*}displayWeek')
                    if week_elem is not None and week_elem.text.lower() == 'true':
                        found_osd_elements['week'] = True

        # 3. Get Custom Text Overlays (from the correct parent in the overlays XML)
        if response_main.status_code == 200:
            root = ET.fromstring(response_main.text)
            text_overlay_list = root.find('.//{*}TextOverlayList')
            if text_overlay_list is not None:
                for i, text_overlay in enumerate(text_overlay_list.findall('.//{*}TextOverlay')):
                    enabled_elem = text_overlay.find('.//{*}enabled')
                    if enabled_elem is not None and enabled_elem.text.lower() == 'true':
                        text_elem = text_overlay.find('.//{*}displayText')
                        if text_elem is not None and text_elem.text and text_elem.text.strip():
                            found_osd_elements[f'custom_{i+1}'] = text_elem.text.strip()

        # 4. Assemble the final OSD string
        if found_osd_elements:
            if verbose:
                print(f"  ✅ OSD retrieved via consolidated Hikvision ISAPI method")
            
            ordered_osd = []
            
            # Assemble in the user-requested order
            if 'channel_name' in found_osd_elements:
                ordered_osd.append(found_osd_elements['channel_name'])

            custom_texts = sorted([v for k, v in found_osd_elements.items() if k.startswith('custom_')])
            ordered_osd.extend(custom_texts)

            date_format = found_osd_elements.get('date')
            if dt and date_format:
                format_map = {'YYYY-MM-DD': '%Y-%m-%d', 'MM-DD-YYYY': '%m-%d-%Y', 'DD-MM-YYYY': '%d-%m-%Y'}
                py_format = format_map.get(date_format)
                if py_format:
                    ordered_osd.append(dt.strftime(py_format))
            elif date_format:
                ordered_osd.append(date_format)

            time_format = found_osd_elements.get('time')
            if dt and time_format:
                if time_format == '24hour':
                    ordered_osd.append(dt.strftime('%H:%M:%S'))
                elif time_format == '12hour':
                    ordered_osd.append(dt.strftime('%I:%M:%S %p'))
            elif time_format:
                ordered_osd.append(time_format)

            if found_osd_elements.get('week'):
                if dt:
                    ordered_osd.append(dt.strftime('%A'))
                else:
                    ordered_osd.append("Week")
            
            return ", ".join(ordered_osd)
            
    except Exception as e:
        if verbose:
            print(f"  ⚠️  Consolidated Hikvision ISAPI method failed: {e}")
    
    return None


def _get_uniview_osd(media_service, profile, verbose=False):
    """
    Get OSD from UNIVIEW camera using the VideoSourceConfiguration token, which was
    found to be required via debugging. Also uses robust parsing for the response.
    """
    try:
        # Step 1: Get the correct token from the profile object.
        if not (hasattr(profile, 'VideoSourceConfiguration') and profile.VideoSourceConfiguration):
            if verbose:
                print("  ⚠️  UNIVIEW: Profile is missing VideoSourceConfiguration. Cannot get OSD.")
            return None
        
        video_source_token = profile.VideoSourceConfiguration.token
        if verbose:
            print(f"  ℹ️  UNIVIEW: Using VideoSourceConfiguration token: '{video_source_token}'")

        # Step 2: Call GetOSDs with the correct token.
        osd_configs = media_service.GetOSDs({"ConfigurationToken": video_source_token})
        
        if osd_configs:
            osd_texts = []
            # Step 3: Use robust parsing to safely extract text.
            for osd in osd_configs:
                if hasattr(osd, "TextString") and osd.TextString:
                    text = getattr(osd.TextString, "PlainText", None)
                    if text:  # This check handles the case where PlainText is None
                        osd_texts.append(text)
            
            if osd_texts:
                if verbose:
                    print(f"  ✅ OSD retrieved successfully via UNIVIEW-specific method")
                return ", ".join(sorted(list(set(osd_texts))))

    except Exception as e:
        if verbose:
            print(f"  ⚠️  UNIVIEW-specific ONVIF GetOSDs failed: {e}")
            
    return None


def get_imaging_settings(cam, verbose=False):
    """Get imaging settings like brightness, contrast, saturation."""
    try:
        imaging_service = cam.create_imaging_service()
        media_service = cam.create_media_service()
        profiles = media_service.GetProfiles()
        
        if profiles:
            video_source_token = profiles[0].VideoSourceConfiguration.SourceToken
            settings = imaging_service.GetImagingSettings({"VideoSourceToken": video_source_token})
            
            result = {
                "brightness": getattr(settings, "Brightness", None),
                "contrast": getattr(settings, "Contrast", None),
                "saturation": getattr(settings, "Saturation", None),
                "sharpness": getattr(settings, "Sharpness", None),
            }
            
            if hasattr(settings, "Exposure"):
                result["exposure"] = {
                    "mode": getattr(settings.Exposure, "Mode", None),
                    "min_exposure_time": getattr(settings.Exposure, "MinExposureTime", None),
                    "max_exposure_time": getattr(settings.Exposure, "MaxExposureTime", None),
                }
            
            if hasattr(settings, "WhiteBalance"):
                result["white_balance"] = {
                    "mode": getattr(settings.WhiteBalance, "Mode", None),
                }
            
            return result
    except Exception as e:
        if verbose:
            print(f"  ⚠️  Could not get imaging settings: {e}")
    return None


def _get_illustra_osd(camera_info, verbose=False):
    """
    Get OSD from Illustra/Tyco camera via iAPI.
    
    Illustra cameras use a proprietary iAPI interface:
      /iAPI/element.cgi?action=read&group=System.Friendlyname
    
    The System.Friendlyname is displayed as OSD text on the video.
    Date/time is shown automatically and not retrievable via this API.
    This function will try provided credentials first, then a known default.
    """
    from requests.auth import HTTPBasicAuth

    ip = camera_info['ip']
    port = camera_info.get('port', 80)
    url = f"http://{ip}:{port}/iAPI/element.cgi?action=read&group=System.Friendlyname"

    # Create a list of credentials to try.
    # First, use the credentials discovered by the main scan.
    creds_to_try = [
        (camera_info.get('username', ''), camera_info.get('password', ''))
    ]

    # As a special fallback for this camera model, if the first set is anonymous,
    # also try a common lab default, as the iAPI often requires authentication.
    if not creds_to_try[0][0] and not creds_to_try[0][1]:
        creds_to_try.append(("admin", "AOTU_CAMERA1"))

    for username, password in creds_to_try:
        try:
            # Use HTTPBasicAuth as required by Illustra
            auth = HTTPBasicAuth(username, password) if username else None
            response = requests.get(url, auth=auth, timeout=5)
            
            if response.status_code == 200:
                text = response.text.strip()
                
                # Check for a valid response, not an HTML login page
                if '=' in text and '[Error' not in text and '<!DOCTYPE' not in text:
                    camera_name = text.split('=', 1)[1].strip()
                    if camera_name:
                        if verbose:
                            print(f"  ✅ OSD retrieved via Illustra iAPI with user '{username}'")
                        return camera_name
            
            if verbose:
                # This will now only print if the attempt fails
                print(f"  ℹ️  Illustra iAPI attempt with user '{username}' failed.")

        except Exception as e:
            if verbose:
                print(f"  ⚠️  Illustra iAPI failed: {e}")
            continue # Try next credential
    
    return None


def get_onvif_info(ip, port, username, password, verbose=False):
    """
    Fetch comprehensive camera information including:
    - Basic device info
    - System date/time
    - RTSP streams with snapshot URIs
    - Video encoder settings
    - OSD settings
    - Imaging settings
    - Audio capabilities
    """
    try:
        cam = ONVIFCamera(ip, port, username, password)
        device_service = cam.create_devicemgmt_service()
        info = device_service.GetDeviceInformation()

        # Get system date and time
        system_datetime = get_system_datetime(device_service, verbose)

        media_service = cam.create_media_service()
        profiles = media_service.GetProfiles()

        # --- Audio Capabilities ---
        has_audio_input = False
        has_audio_output = False
        try:
            audio_sources = media_service.GetAudioSources()
            if audio_sources and len(audio_sources) > 0:
                has_audio_input = True
        except Exception:
            pass

        try:
            audio_outputs = media_service.GetAudioOutputs()
            if audio_outputs and len(audio_outputs) > 0:
                has_audio_output = True
        except Exception:
            pass

        # Get OSD settings from first profile if available
        osd_text = None
        if profiles:
            camera_info_for_osd = {
                'ip': ip,
                'port': port,
                'username': username,
                'password': password,
                'manufacturer': getattr(info, "Manufacturer", "Unknown")
            }
            if verbose:
                print(f'camera_info_for_osd: {camera_info_for_osd}')
            
            # Pass the entire profile object to get_osd_settings
            osd_text = get_osd_settings(media_service, profiles[0], camera_info_for_osd, verbose)

        # Get RTSP streams with enhanced information
        streams = []
        for p in profiles:
            profile_info = {
                "name": getattr(p, "Name", f"profile_{p.token}"),
                "token": p.token,
            }
            
            # Get RTSP URL
            try:
                uri = media_service.GetStreamUri({
                    "StreamSetup": {"Stream": "RTP-Unicast", "Transport": {"Protocol": "RTSP"}},
                    "ProfileToken": p.token
                })
                profile_info["rtsp"] = uri.Uri
            except Exception:
                profile_info["rtsp"] = None

            # Get snapshot URI
            snapshot_uri = get_snapshot_uri(media_service, p.token, verbose)
            if snapshot_uri:
                profile_info["snapshot_uri"] = snapshot_uri

            # Get video encoder configuration
            encoder_config = get_video_encoder_configuration(media_service, p.token, verbose)
            if encoder_config:
                profile_info["video_encoder"] = encoder_config

            streams.append(profile_info)

        # Get imaging settings
        imaging_settings = get_imaging_settings(cam, verbose)

        result = {
            "ip": ip,
            "port": port,
            "username": username,
            "password": password,
            "manufacturer": getattr(info, "Manufacturer", "Unknown"),
            "model": getattr(info, "Model", "Unknown"),
            "firmware": getattr(info, "FirmwareVersion", "Unknown"),
            "serial": getattr(info, "SerialNumber", "Unknown"),
            "hardware_id": getattr(info, "HardwareId", "Unknown"),
            "has_audio_input": has_audio_input,
            "has_audio_output": has_audio_output,
            "system_datetime": system_datetime,
            "osd_text": osd_text,
            "imaging_settings": imaging_settings,
            "poe_info": "Not Available via ONVIF",
            "rtsp_streams": streams,
        }

        if verbose:
            print(json.dumps(result, indent=2))
        return result

    except Fault as e:
        if verbose:
            print(f"❌ ONVIF Fault: {e}")
    except Exception as e:
        if verbose:
            print(f"❌ Failed to connect to {ip}:{port} — {e}")

    return None


def main():
    parser = argparse.ArgumentParser(description="Fetch comprehensive ONVIF camera info using known credentials.")
    parser.add_argument("--host", required=True, help="Camera IP address")
    parser.add_argument("--port", required=True, type=int, help="ONVIF port")
    parser.add_argument("--user", required=True, help="Username")
    parser.add_argument("--password", required=True, help="Password")
    args = parser.parse_args()

    result = get_onvif_info(args.host, args.port, args.user, args.password, verbose=True)
    if result is None:
        exit(1)


if __name__ == "__main__":
    main()
