import os
import sys
from pathlib import Path

import customtkinter as ctk

# ==============================================================================
# PATHS
# ==============================================================================

# APP_ROOT points at the bundled app resources (read-only at runtime --
# e.g. favicon.ico, and the gallery-dl executable if you ship one alongside).
# In --onefile PyInstaller builds this is a TEMP folder that gets deleted
# when the app closes, so nothing the app writes to should live under it.
if getattr(sys, 'frozen', False):
    APP_ROOT = Path(sys._MEIPASS)
    # USER_DATA_ROOT is a separate, persistent, writable location -- the
    # standard place for a Windows app's own data (settings, db, downloads).
    USER_DATA_ROOT = Path(os.environ["APPDATA"]) / "MediaFetcher"
else:
    APP_ROOT = Path(__file__).resolve().parent
    USER_DATA_ROOT = APP_ROOT

USER_DATA_ROOT.mkdir(parents=True, exist_ok=True)

DEFAULT_DOWNLOAD_PATH = USER_DATA_ROOT / "MediaFetcher Assets" / "Downloads"
DEFAULT_DOWNLOAD_PATH.mkdir(parents=True, exist_ok=True)

DATABASE_ROOT = USER_DATA_ROOT / "download_history.db"

# PyInstaller only bundles Python code/imports -- it has no idea subprocess
# is shelling out to a separate CLI tool, so gallery-dl won't be included
# automatically. If you ship gallery-dl.exe next to your packaged app (in
# the same folder as the built .exe, added via PyInstaller's --add-binary
# or --add-data), this picks it up; otherwise it falls back to whatever
# "gallery-dl" resolves to on PATH, which is what dev machines use today.
_bundled_gallery_dl = APP_ROOT / ("gallery-dl.exe" if sys.platform == "win32" else "gallery-dl")
GALLERY_DL_PATH = str(_bundled_gallery_dl) if _bundled_gallery_dl.exists() else "gallery-dl"

# ==============================================================================
# DOMAIN WHITELIST
# ==============================================================================

# Open-Access, Public Domain & Creative Commons Platforms
SUPPORTED_DOMAINS = (
    "commons.wikimedia.org",
    "archive.org",
    "pexels.com",
    "pixabay.com",
    "flickr.com",
    "unsplash.com",
    "twimg.com",
    "x.com",
    "twitter.com",
)

# ==============================================================================
# COLORS
# ==============================================================================

COLORS = {
    "light": {
        "bg": "#F4F7F6",
        "card_border": "#E1E8E5",
        "text": "#132E27",
        "entry_border": "#B2C5BD",
        "placeholder": "#657E74",
        "download_button_idle": "#0D9488",
        "download_button_idle_text": "#FFFFFF",
        "download_button_hover": "#0F766E",
        "error_message": "#E11D48",
    },
    "dark": {
        "bg": "#0B1D17",
        "card_border": "#17382D",
        "text": "#ECFDF5",
        "entry_border": "#214E3F",
        "placeholder": "#6EE7B7",
        "download_button_idle": "#14B8A6",
        "download_button_idle_text": "#0B1D17",
        "download_button_hover": "#2DD4BF",
        "error_message": "#FB7185",
    },
    "success_dwnldbutton": {
        "download_button_idle": "#22c55e",
        "download_button_hover": "#118d11",
    },
}

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("green")