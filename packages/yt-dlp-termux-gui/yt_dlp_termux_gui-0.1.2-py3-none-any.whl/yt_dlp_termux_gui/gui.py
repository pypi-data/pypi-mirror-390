import subprocess
import termuxgui as tg
from . import utils
from . import utils_gui
from . import settings
from . import command


def build(connection: tg.Connection, verbose: bool = True):
    previous = settings.load()
    activity = tg.Activity(connection)
    root = tg.LinearLayout(activity)

    scroll = tg.NestedScrollView(activity, root)
    container = tg.LinearLayout(activity, scroll)
    container.setmargin(10, 'top')
    container.setmargin(10, 'right')
    container.setmargin(80, 'bottom')
    container.setmargin(10, 'left')

    title = tg.TextView(activity, "YT-DLP TERMUX GUI", container)
    title.settextsize(25)
    title.setmargin(20, 'bottom')
    
    thumbnail_container = tg.LinearLayout(activity, container)
    thumbnail_container.setheight(200)
    thumbnail_container.setmargin(10, 'bottom')
    
    paste_btn: tg.Button | None = None
    inputs: dict[str, tg.EditText | str] = {label: placeholder for label, placeholder in settings.defaults.items()}
    
    for label, placeholder in inputs.items():
        title = tg.TextView(activity, label, container)
        title.settextsize(18)
        title.setmargin(6, 'top')
        inputs[label] = tg.EditText(activity, previous.get(label, placeholder), container, singleline=True)
        inputs[label].settextsize(16)
        inputs[label].setmargin(2, 'top')
        
        if label == "Video URL":
            paste_btn = tg.Button(activity, "📋 Paste URL from clipboard", container)
            paste_btn.setmargin(6, 'bottom')
            continue
        
        inputs[label].setmargin(6, 'bottom')
            
    cmd_template_title = tg.TextView(activity, label, container)
    cmd_template_title.settextsize(18)
    cmd_template_title.setmargin(6, 'top')

    force_keyframes_cbx = tg.Checkbox(activity, "Force keyframes at cuts", container)
    force_keyframes_cbx.setmargin(6, 'bottom')
    force_keyframes_cbx.settextsize(16)
    force_keyframes_cbx.setchecked(previous.get("Force Keyframes at Cuts", True))
    
    verbose_cbx = tg.Checkbox(activity, "Verbose logging", container)
    verbose_cbx.setmargin(6, 'bottom')
    verbose_cbx.settextsize(16)
    verbose_cbx.setchecked(previous.get("Verbose", False))
    
    reset_settings_btn = tg.Button(activity, "Reset Settings", container)
    
    run_row = tg.LinearLayout(activity, container, False)
    cancel_btn = tg.Button(activity, "Exit", run_row)
    run_btn = tg.Button(activity, "Run", run_row)

    status_text_container_scroll = tg.NestedScrollView(activity, container)
    status_text_container = tg.LinearLayout(activity, status_text_container_scroll)
    
    status_text_title = tg.TextView(activity, "Status", status_text_container)
    status_text_title.settextsize(18)
    status_text_title.setmargin(10, 'top')
    status_text_title.setmargin(5, 'bottom')

    for event in connection.events():
        if event.type == tg.Event.text:
            input_id = event.value["id"]
            
            if input_id == inputs["Video URL"]:
                media_url = inputs["Video URL"].gettext().strip()
                if utils.is_valid_url(media_url):
                    metadata = command.get_metadata(media_url)
                    media_thumbnail_url = metadata["thumbnail_url"]
                    media_uploader = metadata["uploader"]
                    media_title = metadata["title"]
                    media_duration = metadata["duration"]
                    
                    thumbnail_container.clearchildren()
                    
                    if media_thumbnail_url:
                        thumbnail_view = utils_gui.get_thumbnail_view(activity, thumbnail_container, media_thumbnail_url)
                        thumbnail_view.setmargin(6, 'bottom')
                    
                    if media_uploader:
                        media_uploader_view = tg.TextView(activity, f"Uploader: {media_uploader}", thumbnail_container)
                        media_uploader_view.settextsize(14)
                        media_uploader_view.setmargin(2, 'bottom')
                    
                    if media_title:
                        media_title_view = tg.TextView(activity, f"Title: {media_title}", thumbnail_container)
                        media_title_view.settextsize(14)
                        media_title_view.setmargin(2, 'bottom')
                    
                    if media_duration:
                        media_duration_view = tg.TextView(activity, f"Duration: {media_duration}", thumbnail_container)
                        media_duration_view.settextsize(14)
                
        elif event.type == tg.Event.click:
            btn_id = event.value["id"]

            if btn_id == paste_btn:
                try:
                    clip = subprocess.check_output(["termux-clipboard-get"], text=True).strip()
                    if clip and "\n" not in clip:
                        inputs["Video URL"].settext(clip)
                    else:
                        utils_gui.append_text(verbose, activity, status_text_container, "Clipboard is empty or multi-line")
                except Exception:
                    utils_gui.append_text(verbose, activity, status_text_container, "Clipboard unavailable")

            elif btn_id == reset_settings_btn:
                utils_gui.append_text(verbose, activity, status_text_container, "Resetting settings...")
                settings.clear()
                inputs_defaults = settings.defaults
                for item in inputs.items():
                    label = item[0]
                    if label == "Video URL":
                        continue
                    inputs[label].settext(inputs_defaults[label])
                utils_gui.append_text(verbose, activity, status_text_container, "Settings has been reset!")
                break

            if btn_id == run_btn:
                try:
                    status_text_container.clearchildren()
                    sanitized_inputs = {label: value.gettext().strip() for label, value in inputs.items()}
                    command.run(
                        sanitized_inputs,
                        verbose_cbx.checked,
                        force_keyframes_cbx.checked,
                        activity,
                        status_text_container,
                        verbose,
                    )
                    settings.save(sanitized_inputs)
                except Exception as e:
                    utils_gui.append_text(verbose, activity, status_text_container, f"Error: {str(e)}")

            elif btn_id == cancel_btn:
                utils_gui.append_text(verbose, activity, status_text_container, "Exiting...")
                break