import re
import sys
from .constants import METADATA, SETTINGS_PATH, WIDGET_SCRIPT_NAME, WIDGET_SHORTCUT_NAME


def print_help(prefix: list[str] = []):
    contents: list[str] = []
    contents.extend(prefix)
    contents.extend([
        "Usage: yt-dlp-termux-gui [OPTIONS...] [COMMAND]\n",
        
        "Commands:",
        "launch --> Launch the GUI",
        "widget --> Ensure Termux::Widget for the GUI\n",
        
        "Options:",
        "--no-verbose --> Disable logs in termux by the GUI",
        "--widget-name --> Print widget name",
        "--widget-script-name --> Print widget script filename",
        "--settings-path --> Print settings path",
        "--print-settings --> Print current settings",
        "--reset-settings --> Reset settings\n",
    ])
    print("\n".join(contents))
    
    
def handle_commands(commands: list[str], options: list[str]):
    if commands.count("launch"):
        from .main import launch as launch_gui
        launch_gui(options.count("--no-verbose") == 0)
        
    elif commands.count("widget"):
        from .utils import ensure_termux_widget
        ensure_termux_widget()
        print("Script for Termux::Widget has been created.")
    
    
def handle_options(options: list[str]):
    try:
        options.remove("--no-verbose")
    except ValueError:
        pass
        
    if options.count("--widget-script-name"):
        print(WIDGET_SCRIPT_NAME)
        
    if options.count("--widget-name"):
        print(WIDGET_SHORTCUT_NAME)
        
    if options.count("--settings-path"):
        print(SETTINGS_PATH)
        
    if options.count("--print-settings"):
        from .settings import print as print_settings
        print_settings()
        
    if options.count("--reset-settings"):
        from .settings import clear as clear_settings
        clear_settings()
        print("Settings has been reset.")
        

def run():
    try:
        args = sys.argv[1:]
        commands = [s for s in args if re.match(r"^(launch|widget)$", s)]
        options = [s for s in args if s.startswith("-")]
        
        if commands == [] and options == []:
            print_help(["Need help with yt-dlp-termux-gui?\n"])
            sys.exit(1)
    
        if options.count("-v") or options.count("-V") or options.count("--version"):
            print_help([f"v{METADATA.get('version')}"])
            sys.exit(0)
    
        if options.count("-h") or options.count("-H") or options.count("--help"):
            print_help([f"yt-dlp-termux-gui (v{METADATA.get('version')})\n"])
            sys.exit(0)
            
        handle_commands(commands, options)
        handle_options(options)
        
    except Exception as e:
        print("Error:", str(e))
        sys.exit(1)
        
        
if __name__ == "__main__":
    run()