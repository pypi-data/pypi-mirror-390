import os

CONFIG_PATH = os.path.expanduser("~/.config/yt_dlp_termux_gui_config.json")

TERMUX_WIDGETS_DIR = os.path.expanduser("~/.shortcuts")
TERMUX_WIDGETS_TASKS_DIR = os.path.join(TERMUX_WIDGETS_DIR, "tasks")
TERMUX_SCRIPTS_DIR = os.path.expanduser("~/.scripts/yt-dlp-termux-gui")

WIDGET_SCRIPT_NAME = "main.py"
WIDGET_SHORTCUT_NAME = "YT-DLP GUI"