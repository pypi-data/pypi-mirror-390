# brainframe-onvif-tools

Python CLI tools for discovering, scanning, and validating ONVIF cameras.

## Installation

```bash
pip install brainframe-onvif-tools
```

## Usage

```bash
brainframe-onvif-tools <command> [options]
```

### Commands

- `discover` - Find ONVIF cameras on network
- `scan` - Get camera details and credentials
- `validate` - Verify RTSP streams

### Example Workflow

```bash
# 1. Discover cameras
brainframe-onvif-tools discover --auto

# 2. Scan for details
brainframe-onvif-tools scan

# 3. Validate RTSP streams
brainframe-onvif-tools validate
```

### Single Camera

```bash
brainframe-onvif-tools scan --host 192.168.1.10 --user admin --password pass
```

## Output

Creates `config.csv` with camera details including RTSP URLs with embedded credentials.

## Help

```bash
brainframe-onvif-tools <command> --help
```
