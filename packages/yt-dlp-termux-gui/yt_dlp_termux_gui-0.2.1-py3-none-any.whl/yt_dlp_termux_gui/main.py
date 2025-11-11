import sys


def launch(verbose: bool = True):
    try:
        from . import utils
        if not utils.detect_termux():
            if verbose:
                print("This script must run inside Termux.")
            sys.exit(1)
            
        import termuxgui as tg
        from . import gui
        with tg.Connection() as connection:
            gui.build(connection, verbose)
        
    except Exception as e:
        if verbose:
            print("Error:", str(e))
        sys.exit(1)
        

if __name__ == "__main__":
    launch()
