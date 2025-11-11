import os
import json
from . import constants


def get_defaults(additional_args: str = ""):
    return {
        "Video URL": "https://example.com/video",
        "Output Directory": "~/storage/downloads",
        "Start Time (optional)": "*00:00",
        "End Time (optional)": "inf",
        "Cookies File (optional)": os.path.join(constants.TERMUX_SCRIPTS_DIR, "cookies.txt"),
        "Filename Template": f"%(uploader).30B - %(title)s (%(extractor)s) [%(upload_date>%Y-%m-%d)s].%(ext)s",
        "Additional Arguments": additional_args,
    }


def load() -> dict:
    if os.path.exists(constants.CONFIG_PATH):
        try:
            with open(constants.CONFIG_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save(settings: dict):
    os.makedirs(os.path.dirname(constants.CONFIG_PATH), exist_ok=True)
    to_save = {k: v for k, v in settings.items() if k != "Video URL"}
    with open(constants.CONFIG_PATH, "w") as f:
        json.dump(to_save, f, indent=2)


def clear():
    if os.path.exists(constants.CONFIG_PATH):
        os.remove(constants.CONFIG_PATH)


def print(additional_args: str = ""):
    if os.path.exists(constants.CONFIG_PATH):
        with open(constants.CONFIG_PATH, "r") as f:
            print(json.load(f))
    else:
        print(get_defaults(additional_args))