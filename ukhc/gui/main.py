import re
import traceback
import webbrowser

import PySimpleGUI as Sg

from ukhc.application import Config, Lifter, AddressTranslator, IGVRedirectionServer

from .icon import get_gui_icon
from .preferences import preferences_window

scrape = re.compile(r'.*(?P<coord>chr[^:]+:[0-9]+).*')


def main_window():
    server = IGVRedirectionServer()
    menu = [
        [
            '&File',
            [
                '&Preferences',
                'E&xit',
            ]
        ]
    ]
    server_tab = [
        [
            Sg.Button('Start Server', key='REDIRECTSERVERSTART'),
            Sg.Text('Status: '), Sg.Text('Stopped', key='SERVERSTATUS'),
        ], [
            Sg.Button('Stop Server', key='REDIRECTSERVERSTOP', disabled=True),
        ],
    ]
    manual_tab = [
        [
            Sg.Text('Source coordinate:', size=(18, 1)),
            Sg.Input(key="SOURCECOORDINATE", enable_events=True),
        ], [
            Sg.Button("Open in IGV", key="OPENINIGV", visible=True),
        ]
    ]
    layout = [
        [
            Sg.Menu(menu),
        ], [
            Sg.Text('Liftover source coordinate(s) into different refrence genome .bam file in IGV'),
        ], [
            Sg.Text('Expected IGV Port: '),
            Sg.Text(Config.get_igv_port(60151), key='CURRENTIGVPORT'),
        ], [
            [
                Sg.Text('Last Lifted & Opened:', size=(17, 1)),
            ], [
                Sg.Text('', size=(3, 1)), Sg.Text('', key="LASTLIFTED"),
            ],
        ], [
            Sg.TabGroup(
                [
                    [
                        Sg.Tab("Redirect Server", server_tab),
                        Sg.Tab("Copy/Paste Textbox", manual_tab),
                    ]
                ]
            )
        ]
    ]

    window = Sg.Window('IGV Translator', layout, icon=get_gui_icon(), finalize=True)
    window['SOURCECOORDINATE'].bind("<Return>", "_Enter")
    AddressTranslator.set_interface(window)
    server.set_interface(window)
    if Config.get_autostart():
        server.start_server()
        window['REDIRECTSERVERSTART'].update(disabled=True)
        window['REDIRECTSERVERSTOP'].update(disabled=False)
        window.Refresh()

    while True:
        event, values = window.read(timeout=250)
        if event is None or event == 'Exit':
            break
        if event == 'Preferences':
            preferences_window()
        if event == 'REDIRECTSERVERSTART':
            server.start_server()
            window['REDIRECTSERVERSTART'].update(disabled=True)
            window['REDIRECTSERVERSTOP'].update(disabled=False)
            window.Refresh()
        if event == 'REDIRECTSERVERSTOP':
            server.stop_server()
            window['REDIRECTSERVERSTART'].update(disabled=False)
            window['REDIRECTSERVERSTOP'].update(disabled=True)
            window.Refresh()
        if event == 'OPENINIGV' or event == "SOURCECOORDINATE" + "_Enter":
            if values['SOURCECOORDINATE'] == '':
                Sg.Popup("Error", "Please paste line with coordinate to lift and open")
            elif not Lifter.is_chain_file_set():
                Sg.Popup("Error", "Please supply a liftover chain file in File -> Preferences")
            else:
                coordinate_to_open = values['SOURCECOORDINATE']
                window.Element('SOURCECOORDINATE').update('')
                try:
                    search = scrape.match(coordinate_to_open)
                    if not search:
                        Sg.Popup("Error", "Did not find chr#:### coordinate in input, please copy again from Fabric")
                    else:
                        coord = search.group('coord')
                        if not coord.startswith('chr'):
                            coord = "chr" + coord
                        input_parts = coord.split(":")
                        try:
                            output = Lifter.liftover_coordinate(input_parts[0], int(input_parts[1]))
                            webbrowser.open(f"http://localhost:{Config.get_igv_port()}/goto?locus={':'.join(output)}")
                            window.Element('LASTLIFTED').update(f"{':'.join(input_parts)} (Source) -> {':'.join(output)} (Lifted)")
                        except IndexError:
                            Sg.Popup("Error", f"Coordinate {input_parts[0]}:{input_parts[1]} did not lift over")
                except Exception as e:
                    tb = traceback.format_exc()
                    Sg.Print(f'An error happened. Here is the info:', e, tb)
        window.Element('CURRENTIGVPORT').update(Config.get_igv_port(60151))
        window.Refresh()
    window.close()
