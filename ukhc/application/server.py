import re
import threading

from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Optional

from ukhc.application import Config, Lifter

igv_link_parser = re.compile(r"/goto\?locus=(?P<chrom>[0-9xXyY]+):(?P<start>[0-9]+)-(?P<end>[0-9]+)")


class AddressTranslator:
    window = None

    @staticmethod
    def set_interface(window):
        AddressTranslator.window = window

    @staticmethod
    def translate_address(address: str) -> Optional[str]:
        search = igv_link_parser.match(address)
        if not search:
            return None
        lifted_start = Lifter.liftover_coordinate('chr' + search.group('chrom'), int(search.group('start')))
        lifted_end = Lifter.liftover_coordinate('chr' + search.group('chrom'), int(search.group('end')))
        AddressTranslator.window.Element('LASTLIFTED').update(f"{search.group('chrom')}:{search.group('start')}-" +
                                                              f"{search.group('end')} (hg38) -> " +
                                                              f"{search.group('chrom')}" +
                                                              f":{lifted_start[1]}-{lifted_end[1]} (GRCh37)")
        return (f"http://localhost:{Config.get_igv_port()}/goto?locus={search.group('chrom')}:" +
                f"{lifted_start[1]}-{lifted_end[1]}")


class LiftoverAndRedirect(SimpleHTTPRequestHandler):
    def do_GET(self):
        print(Config.get_igv_port())
        if Lifter.is_chain_file_set() and Config.is_igv_port_valid_for_server():
            self.send_response(303)
            self.send_header('Location', AddressTranslator.translate_address(self.path))
            self.end_headers()
        elif not Lifter.is_chain_file_set():
            self.send_response(200, 'OK')
            self.send_header('Content-type', 'html')
            self.end_headers()
            self.wfile.write(
                bytes("<html> <head><title> IGV Translator - Setup Error </title> </head> <body>", 'UTF-8'))
            self.wfile.write(
                bytes("<p>You must set a chain file using File -> Preferences in the IGV Translator application.</p>",
                      "UTF-8"))
            self.wfile.write(bytes("</body></html>", 'UTF-8'))
        elif not Config.is_igv_port_valid_for_server():
            self.send_response(200, 'OK')
            self.send_header('Content-type', 'html')
            self.end_headers()
            self.wfile.write(
                bytes("<html> <head><title> IGV Translator - Setup Error </title> </head> <body>", 'UTF-8'))
            self.wfile.write(
                bytes("<p>You must set an IGV port (other than 60151) using File -> Preferences in " +
                      "the IGV Translator application.</p>", "UTF-8"))
            self.wfile.write(bytes("</body></html>", 'UTF-8'))

class IGVRedirectionServer:
    def __init__(self):
        self.listening_port = 60151
        self.server = None
        self.thread = None
        self.interface = None

    def set_interface(self, interface):
        self.interface = interface

    def start_server(self):
        self.server = HTTPServer(('localhost', self.listening_port), LiftoverAndRedirect)
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
        self.interface.Element('SERVERSTATUS').update(f"Listening on {self.listening_port}")

    def stop_server(self):
        self.server.shutdown()
        self.server.socket.close()
        self.server = None
        self.thread = None
        self.interface.Element('SERVERSTATUS').update(f"Stopped")
