from datetime import datetime
import termuxgui as tg


def append_text(verbose: bool, activity: tg.Activity, status_container: tg.LinearLayout, message: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    if verbose:
        print(formatted_message)
    text_view = tg.TextView(activity, formatted_message, status_container)
    text_view.settextsize(15)
    text_view.setmargin(10, 'bottom')
    text_view.setclickable(True)
    

def get_thumbnail_view(activity: tg.Activity, parent: tg.View | None, url: str) -> tg.ImageView:
    from .utils import get_image_bytes 
    img = get_image_bytes(url, "thumbnail")
    thumbnail_view = tg.ImageView(activity, parent)
    thumbnail_view.setimage(img)
    thumbnail_view.setbackgroundcolor(0)
    return thumbnail_view
