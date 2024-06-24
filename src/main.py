from constants import *
from packets import *
from ui import gui

import threading

if __name__ == '__main__':

    # Start the gui thread here
    gui_thread = threading.Thread(target=gui.run_gui, daemon=True);
    gui_thread.start();

    gui_thread.join();