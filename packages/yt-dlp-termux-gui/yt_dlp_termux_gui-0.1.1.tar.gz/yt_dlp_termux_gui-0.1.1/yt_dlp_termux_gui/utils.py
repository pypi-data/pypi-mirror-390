import os
import re
from io import BytesIO
from typing import Literal
from PIL import Image
import requests
import platform
from . import constants


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
    os.makedirs(constants.TERMUX_WIDGETS_TASKS_DIR, exist_ok=True)
    shortcut_path = os.path.join(constants.TERMUX_WIDGETS_TASKS_DIR, constants.WIDGET_SHORTCUT_NAME)
    shortcut_content = f"""#!/data/data/com.termux/files/usr/bin/sh
yt-dlp-termux-gui run
"""
    with open(shortcut_path, "w") as f:
        f.write(shortcut_content)
    os.chmod(shortcut_path, 0o755)

    
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
