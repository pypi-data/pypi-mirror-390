import os
import re
import threading
from typing import Iterable, Any
from io import BytesIO
from typing import Literal
from PIL import Image
import requests
import platform
# import shutil
# from importlib import resources
# from pathlib import Path
from . import constants


# resources_dir = resources.files("yt_dlp_termux_gui").joinpath("resources")
# widget_dir = resources_dir.joinpath("widget")
# curl_dir = resources_dir.joinpath("curl")
    
    
# def copy_files():
#     external_base = Path("/data/data/com.termux/files/home/yt-dlp-gui-resources")
#     external_base.mkdir(parents=True, exist_ok=True)
    
#     shutil.copytree(curl_dir, external_base / "curl")
#     shutil.copytree(widget_dir, external_base / "widget")


def run_job(target=None, args=Iterable[Any]):
    threading.Thread(target=target, args=args, daemon=True).start()
    

def is_valid_url(url: str) -> bool:
    url_pattern = re.compile(
        r'^(https?://)?'                        # optional http or https
        r'(([A-Za-z0-9-]+\.)+[A-Za-z]{2,})'     # domain (example.com)
        r'(:\d+)?'                              # optional port
        r'(/[\w\-.~:/?#[\]@!$&\'()*+,;%=]*)?$'  # optional path/query
    )
    return bool(url_pattern.match(url))


def detect_termux() -> bool:
    system = platform.system()
    return system == "Linux" and (
        "ANDROID_STORAGE" in os.environ or "com.termux" in os.environ.get("HOME", "")
    )


def ensure_termux_widget():
    shortcut_path = os.path.join(constants.TERMUX_WIDGETS_TASKS_DIR, constants.WIDGET_SCRIPT_NAME)
    
    if os.path.exists(shortcut_path):
        return False

    os.makedirs(constants.TERMUX_WIDGETS_TASKS_DIR, exist_ok=True)
    
    shortcut_content = f"""#!/data/data/com.termux/files/usr/bin/sh
yt-dlp-termux-gui launch
"""
    
    with open(shortcut_path, "w") as f:
        f.write(shortcut_content)
        
    os.chmod(shortcut_path, 0o755)
    
    return True

    
def get_image_bytes(image_url: str, size: Literal['thumbnail', 'default']):
    response = requests.get(image_url)
    response.raise_for_status()  # ensure it downloaded successfully
    
    buf_png = BytesIO()
    img = Image.open(BytesIO(response.content))

    if size == "default":
        img.save(buf_png, format="PNG", optimize=True)
        return buf_png.getvalue()
    
    target_ratio = 3 / 2
    width, height = img.size
    current_ratio = width / height

    if current_ratio > target_ratio:
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        right = left + new_width
        top = 0
        bottom = height
    else:
        new_height = int(width / target_ratio)
        top = (height - new_height) // 2
        bottom = top + new_height
        left = 0
        right = width

    img_cropped = img.crop((left, top, right, bottom))
    img_cropped.save(buf_png, format="PNG", optimize=True)
    png_bytes = buf_png.getvalue()
    
    return png_bytes
