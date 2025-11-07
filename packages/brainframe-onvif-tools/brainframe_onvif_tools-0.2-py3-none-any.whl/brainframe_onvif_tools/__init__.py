try:
    from importlib.metadata import version
    __version__ = version("brainframe-onvif-tools")
except Exception:
    __version__ = "unknown"

from .cli import cli_main
from .discover_onvif_cameras import discover_main
from .scan_onvif_cameras import scan_main 
from .validate_onvif_cameras import validate_main
