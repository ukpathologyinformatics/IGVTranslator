import PySimpleGUI as Sg

from ukhc.application import Config, Lifter


def preferences_window():
    layout = [
        [
            Sg.Text('Application Preferences:'),
        ],[
            Sg.Text("IGV Port"),
            Sg.Input(default_text=Config.get_igv_port(), key="IGVPORT", size=(12, 1)),
        ], [
            Sg.Text("Server Listening Port"),
            Sg.Input(default_text=Config.get_server_port(), key="SERVERPORT", size=(12, 1)),
        ], [
            Sg.Checkbox("Autostart Server", default=Config.get_autostart(), key="AUTOSTART"),
        ], [
            Sg.Text('Liftover Chain File:'),
            Sg.Input(default_text=Config.get_chain_file(), key="CHAINFILEPATH", size=(65, 1)),
            Sg.FileBrowse()
        ],
        [
            Sg.Button("Save Changes", key="-SAVECHANGES-")
        ]
    ]

    window = Sg.Window('Preferences', layout)

    while True:
        event, values = window.read()
        if event is None or event == 'Exit':
            break
        if event == '-SAVECHANGES-':
            Config.set_igv_port(values["IGVPORT"])
            Config.set_server_port(values["SERVERPORT"])
            Config.set_autostart(values["AUTOSTART"])
            Config.set_chain_file(values['CHAINFILEPATH'])
            Lifter.load_chain(values['CHAINFILEPATH'])
            break
    window.close()