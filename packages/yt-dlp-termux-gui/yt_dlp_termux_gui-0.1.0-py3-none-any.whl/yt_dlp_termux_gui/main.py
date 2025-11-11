import sys
import termuxgui as tg
from . import utils
from . import gui


def run(verbose: bool = True):
    try:
        if not utils.detect_termux():
            if verbose:
                print("This script must run inside Termux.")
            sys.exit(1)
        
        utils.ensure_termux_widget()
        
        with tg.Connection() as connection:
            gui.build(connection, verbose)
        
    except Exception as e:
        if verbose:
            print("Error:", str(e))
        sys.exit(1)
        

if __name__ == "__main__":
    run()
