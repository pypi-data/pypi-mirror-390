import sys
import subprocess
import traceback
from datetime import datetime
import termuxgui as tg
from . import utils
from . import utils_gui
from . import settings
from . import command
from . import constants
    
    
def get_timestamp():
    return datetime.now().strftime("%H:%M:%S")
    
    
def print_msg(verbose: bool, message: str):
    if not verbose:
        return
    print(f"[{get_timestamp()}] {message}")


def handle_lifecycle_events(connection: tg.Connection, verbose: bool = True):
    for event in connection.events():
        if event.type == tg.Event.create:
            try:
                print_msg(verbose, "Starting GUI...")
            except Exception as e:
                print(verbose, f"GUI Event error: {str(e)}")
        elif event.type == tg.Event.start:
            try:
                print_msg(verbose, "GUI has started")
            except Exception as e:
                print(verbose, f"GUI Event error: {str(e)}")
        elif event.type == tg.Event.resume:
            try:
                print_msg(verbose, "GUI is active")
            except Exception as e:
                print(verbose, f"GUI Event error: {str(e)}")
        elif event.type == tg.Event.pause:
            try:
                print_msg(verbose, "GUI is inactive")
            except Exception as e:
                print(verbose, f"GUI Event error: {str(e)}")
        elif event.type == tg.Event.stop:
            try:
                print_msg(verbose, "GUI lost focus")
            except Exception as e:
                print(verbose, f"GUI Event error: {str(e)}")
        elif event.type == tg.Event.destroy:
            try:
                print_msg(verbose, "GUI was destroyed")
            except Exception as e:
                print(verbose, f"GUI Event error: {str(e)}")
        elif event.type == tg.Event.destroy:
            try:
                print_msg(verbose, "User hints to go back")
            except Exception as e:
                print(verbose, f"GUI Event error: {str(e)}")
        elif event.type == tg.Event.pipchanged:
            try:
                print_msg(verbose, "Picture-in-picture mode changed")
            except Exception as e:
                print(verbose, f"GUI Event error: {str(e)}")
        elif event.type == tg.Event.config:
            try:
                print_msg(verbose, "State changed")
            except Exception as e:
                print(verbose, f"GUI Event error: {str(e)}")
        elif event.type == tg.Event.back:
            try:
                print_msg(verbose, "User pressed back")
            except Exception as e:
                print(verbose, f"GUI Event error: {str(e)}")
            break


def build_gui(connection: tg.Connection, verbose: bool = True):
    print_msg(verbose, "Loading previous settings...")
    previous_settings = settings.load()
    
    print_msg(verbose, "Initializing GUI...")
    activity = tg.Activity(connection)
    
    print_msg(verbose, "Building GUI...")
    root_container = tg.LinearLayout(activity)

    scroll_container = tg.NestedScrollView(activity, root_container)
    container = tg.LinearLayout(activity, scroll_container)
    container.setmargin(10, 'top')
    container.setmargin(10, 'right')
    container.setmargin(80, 'bottom')
    container.setmargin(10, 'left')

    title = tg.TextView(activity, constants.WIDGET_TITLE, container)
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
        inputs[label] = tg.EditText(activity, previous_settings.get(label, placeholder), container, singleline=True)
        inputs[label].settextsize(16)
        inputs[label].setmargin(2, 'top')
        
        if label == "Video URL":
            paste_btn = tg.Button(activity, "📋 Paste URL from clipboard", container)
            paste_btn.setmargin(6, 'bottom')
            continue
        
        inputs[label].setmargin(6, 'bottom')

    force_keyframes_cbx = tg.Checkbox(activity, "Force keyframes at cuts", container)
    force_keyframes_cbx.setmargin(6, 'bottom')
    force_keyframes_cbx.settextsize(16)
    force_keyframes_cbx.setchecked(previous_settings.get("Force Keyframes at Cuts", True))
    
    verbose_cbx = tg.Checkbox(activity, "Verbose logging", container)
    verbose_cbx.setmargin(6, 'bottom')
    verbose_cbx.settextsize(16)
    verbose_cbx.setchecked(previous_settings.get("Verbose", False))
    
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
                try:
                    media_url = event.value["text"]
                    if utils.is_valid_url(media_url):
                        def update_metadata():
                            metadata = command.get_metadata(media_url)
                            media_thumbnail_url = metadata.get("thumbnail")
                            media_uploader = metadata.get("uploader")
                            media_title = metadata.get("title")
                            media_duration = metadata.get("duration")
                            
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
                                
                        utils.run_job(update_metadata)
                except Exception as e:
                    print(verbose, f"GUI Event error: {str(e)}")
                
        elif event.type == tg.Event.click:
            btn_id = event.value["id"]

            if btn_id == paste_btn:
                try:
                    try:
                        clip = subprocess.check_output(["termux-clipboard-get"], text=True).strip()
                        if clip and "\n" not in clip:
                            inputs["Video URL"].settext(clip)
                        else:
                            utils_gui.append_text(verbose, activity, status_text_container, "Clipboard is empty or multi-line")
                    except Exception:
                        utils_gui.append_text(verbose, activity, status_text_container, "Clipboard unavailable")
                except Exception as e:
                    print(verbose, f"GUI Event error: {str(e)}")

            elif btn_id == reset_settings_btn:
                try:
                    utils_gui.append_text(verbose, activity, status_text_container, "Resetting settings...")
                    settings.reset_settings()
                    inputs_defaults = settings.defaults
                    for item in inputs.items():
                        label = item[0]
                        if label == "Video URL":
                            continue
                        inputs[label].settext(inputs_defaults[label])
                    utils_gui.append_text(verbose, activity, status_text_container, "Settings has been reset!")
                except Exception as e:
                    print(verbose, f"GUI Event error: {str(e)}")

            elif btn_id == run_btn:
                try:
                    def download_media():
                        try:
                            status_text_container.clearchildren()
                            sanitized_inputs = {label: value.gettext().strip() for label, value in inputs.items()}
                            command.run_yt_dlp(
                                sanitized_inputs,
                                verbose_cbx.checked,
                                force_keyframes_cbx.checked,
                                activity,
                                status_text_container,
                                verbose,
                            )
                            settings.save_settings(sanitized_inputs)
                        except Exception as e:
                            utils_gui.append_text(verbose, activity, status_text_container, f"GUI error: {str(e)}")
                        
                    utils.run_job(download_media)
                except Exception as e:
                    print(verbose, f"GUI Event error: {str(e)}")

            elif btn_id == cancel_btn:
                try:
                    utils_gui.append_text(verbose, activity, status_text_container, "Exiting...")
                except Exception as e:
                    print(verbose, f"GUI Event error: {str(e)}")
                
            break

            
def launch_gui(verbose: bool = True):
    try:
        from . import utils
        if not utils.detect_termux():
            print_msg(verbose, "This script must run inside Termux.")
            sys.exit(1)
            
        with tg.Connection() as connection:
            utils.run_job(handle_lifecycle_events, (connection, verbose))
            build_gui(connection, verbose)
        
    except Exception:
        e = traceback.format_exc()
        if verbose:
            print("GUI error:", e)
        sys.exit(1)