import os
import sys
from datetime import datetime
import termuxgui as tg
import platform
import shutil
from . import constants


def detect_termux() -> bool:
    system = platform.system()
    return system == "Linux" and (
        "ANDROID_STORAGE" in os.environ or "com.termux" in os.environ.get("HOME", "")
    )


def ensure_termux_widget():
    os.makedirs(constants.TERMUX_WIDGETS_TASKS_DIR, exist_ok=True)
    os.makedirs(constants.TERMUX_SCRIPTS_DIR, exist_ok=True)

    current_script = os.path.abspath(sys.argv[0])
    script_path = os.path.join(constants.TERMUX_SCRIPTS_DIR, constants.WIDGET_SCRIPT_NAME)
    shortcut_path = os.path.join(constants.TERMUX_WIDGETS_TASKS_DIR, constants.WIDGET_SHORTCUT_NAME)

    if os.path.basename(current_script) != constants.WIDGET_SCRIPT_NAME or not os.path.isfile(script_path):
        shutil.copyfile(current_script, script_path)
        os.chmod(script_path, 0o755)

    shortcut_content = f"""#!/data/data/com.termux/files/usr/bin/sh
python3 "{script_path}"
"""
    with open(shortcut_path, "w") as f:
        f.write(shortcut_content)
    os.chmod(shortcut_path, 0o755)


def append_text(verbose: bool, activity: tg.Activity, status_container: tg.LinearLayout, message: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    if verbose:
        print(formatted_message)
    text_view = tg.TextView(activity, formatted_message, status_container)
    text_view.settextsize(15)
    text_view.setmargin(10, 'bottom')
    text_view.setclickable(True)