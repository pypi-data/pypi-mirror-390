import os
import importlib.metadata as lib_metadata

SETTINGS_PATH = os.path.expanduser("~/.config/yt_dlp_termux_gui/settings.json").replace("\\", "/")
SETTINGS_DIR = os.path.dirname(SETTINGS_PATH).replace("\\", "/")

TERMUX_WIDGETS_DIR = os.path.expanduser("~/.shortcuts").replace("\\", "/")
TERMUX_WIDGETS_TASKS_DIR = os.path.join(TERMUX_WIDGETS_DIR, "tasks").replace("\\", "/")

WIDGET_SCRIPT_NAME = "main.py"
WIDGET_SHORTCUT_NAME = "YT-DLP GUI"

METADATA = lib_metadata.metadata("yt-dlp-termux-gui")

ADDITIONAL_ARGS_TEMPLATE = [
    "--newline",
    "-N", "3",
    "--retries", "3",
    "--fragment-retries", "3",
    "--restrict-filenames",
    "--embed-metadata",
    "--embed-thumbnail",
    "--impersonate", "Chrome-99",
    "--no-overwrites",
    "--no-post-overwrites",
]