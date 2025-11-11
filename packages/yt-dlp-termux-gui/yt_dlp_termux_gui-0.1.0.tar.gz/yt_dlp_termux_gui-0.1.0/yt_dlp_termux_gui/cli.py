import sys
from .command import additional_args_template
from .settings import clear as clear_settings, print as print_settings
from .constants import CONFIG_PATH, WIDGET_SCRIPT_NAME, WIDGET_SHORTCUT_NAME, TERMUX_SCRIPTS_DIR as SCRIPTS_DIR

def run():
    try:
        i = 0
        args = sys.argv[1:]
        while i < len(args):
            cmd = args[i].lower()
        
            if cmd == "--config-path":
                print(CONFIG_PATH)
            elif cmd == "--scripts-dir":
                print(SCRIPTS_DIR)
            elif cmd == "--widget-script-name":
                print(WIDGET_SCRIPT_NAME)
            elif cmd == "--widget-name":
                print(WIDGET_SHORTCUT_NAME)
            elif cmd == "--widget-name":
                print(WIDGET_SHORTCUT_NAME)
            elif cmd == "--print-settings":
                print_settings(" ".join(additional_args_template))
            elif cmd == "--reset-settings":
                clear_settings()
                print("Settings has been reset.")
            else:
                print(f"Unknown command: {cmd}")
                sys.exit(1)
                
            i += 1
        
    except Exception as e:
        print("Error:", str(e))
        sys.exit(1)