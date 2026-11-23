import os
import sys
from pathlib import Path

def platform_name():
    if sys.platform.startswith("win"):
        return "Windows"
    if sys.platform.startswith("linux"):
        if "ANDROID_ROOT" in os.environ:
            return "Android"
        return "Linux"
    if sys.platform == "darwin":
        return "macOS"
    return "Unknown"

def platform_info():
    return {
        "name": platform_name(),
        "system": sys.platform,
        "python": sys.version.split()[0],
        "path_separator": os.sep,
        "home": str(Path.home()),
    }

def normalize_path(value):
    return str(Path(value).expanduser())

def is_absolute_path(value):
    return Path(value).is_absolute()
