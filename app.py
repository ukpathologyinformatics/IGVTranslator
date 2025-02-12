import PySimpleGUI as Sg

from ukhc.application import Config, Dirs, Lifter
from ukhc.gui import get_gui_icon512, main_window

if __name__ == "__main__":
    Sg.ChangeLookAndFeel('Default 1')
    Sg.SetOptions(icon=get_gui_icon512())
    try:
        Dirs.initialize()
        Config.load_config()
        if Config.get_chain_file() is not None and Config.get_chain_file() != '':
            Lifter.load_chain(Config.get_chain_file())
    except OSError as e:
        exit(1)
    main_window()
