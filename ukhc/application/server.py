import re
import threading

from http.server import HTTPServer, BaseHTTPRequestHandler
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
        try:
            search = igv_link_parser.match(address)
            if not search:
                return None
            lifted_start = Lifter.liftover_coordinate('chr' + search.group('chrom'), int(search.group('start')))
            lifted_end = Lifter.liftover_coordinate('chr' + search.group('chrom'), int(search.group('end')))
            AddressTranslator.window.Element('LASTLIFTED').update(f"{search.group('chrom')}:{search.group('start')}-" +
                                                                  f"{search.group('end')} (source) -> " +
                                                                  f"{':'.join(lifted_start)}-{lifted_end[1]} (lifted)")
            return (f"http://localhost:{Config.get_igv_port()}/goto?locus={search.group('chrom')}:" +
                    f"{lifted_start[1]}-{lifted_end[1]}")
        except:
            return None


class LiftoverAndRedirect(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if Lifter.is_chain_file_set():
            liftover_address = AddressTranslator.translate_address(self.path)
            if liftover_address:
                self.send_response(303)
                self.send_header('Location', liftover_address)
                self.end_headers()
            else:
                self.send_response(200, 'OK')
                self.send_header('Content-type', 'html')
                self.end_headers()
                self.wfile.write(
                    bytes("<html> <head><title> IGV Translator - Error </title> </head> <body>", 'UTF-8'))
                self.wfile.write(
                    bytes(
                        f"<h1>Failed to liftover address: {self.path}</h1>",
                        "UTF-8"))
                self.wfile.write(bytes("</body></html>", 'UTF-8'))
        else:
            self.send_response(200, 'OK')
            self.send_header('Content-type', 'html')
            self.end_headers()
            self.wfile.write(
                bytes("<html> <head><title> IGV Translator - Setup Error </title> </head> <body>", 'UTF-8'))
            self.wfile.write(
                bytes("<h1>You must set a chain file using File -> Preferences in the IGV Translator application.</h1>",
                      "UTF-8"))
            self.wfile.write(bytes("</body></html>", 'UTF-8'))

class IGVRedirectionServer:
    def __init__(self):
        self.server = None
        self.thread = None
        self.interface = None

    def set_interface(self, interface):
        self.interface = interface

    def start_server(self):
        self.server = HTTPServer(('localhost', Config.get_server_port()), LiftoverAndRedirect)
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
        self.interface.Element('SERVERSTATUS').update(f"Listening on {Config.get_server_port()}")

    def stop_server(self):
        setattr(self.server, '_BaseServer__shutdown_request', True)
        self.server.socket.close()
        self.server = None
        self.thread = None
        self.interface.Element('SERVERSTATUS').update(f"Stopped")
