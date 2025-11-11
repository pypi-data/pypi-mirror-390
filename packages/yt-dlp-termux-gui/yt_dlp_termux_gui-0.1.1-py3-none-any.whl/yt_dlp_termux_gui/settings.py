import os
import json
from . import constants


defaults = {
    "Video URL": "https://example.com/video",
    "Output Directory": "~/storage/downloads",
    "Start Time (optional)": "*00:00",
    "End Time (optional)": "inf",
    "Cookies File (optional)": os.path.join(constants.SETTINGS_DIR, "cookies.txt"),
    "Filename Template": f"%(uploader).30B - %(title)s (%(extractor)s) [%(upload_date>%Y-%m-%d)s].%(ext)s",
    "Additional Arguments": constants.ADDITIONAL_ARGS_TEMPLATE,
}


def load() -> dict:
    if os.path.exists(constants.SETTINGS_PATH):
        try:
            with open(constants.SETTINGS_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save(settings: dict):
    os.makedirs(os.path.dirname(constants.SETTINGS_PATH), exist_ok=True)
    to_save = {k: v for k, v in settings.items() if k != "Video URL"}
    with open(constants.SETTINGS_PATH, "w") as f:
        json.dump(to_save, f, indent=2)


def clear():
    if os.path.exists(constants.SETTINGS_PATH):
        os.remove(constants.SETTINGS_PATH)


def print():
    if os.path.exists(constants.SETTINGS_PATH):
        with open(constants.SETTINGS_PATH, "r") as f:
            print(json.load(f))
    else:
        print(constants.ADDITIONAL_ARGS_TEMPLATE)