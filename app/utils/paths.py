import sys
from pathlib import Path


def app_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def resource_path(relative):
    base = Path(getattr(sys, "_MEIPASS", app_dir()))
    return base / relative
