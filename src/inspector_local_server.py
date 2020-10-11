import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class InspectorLocalServer:
    def __init__(self, url, port):
        self._port = port
        self.Redirect._url = url
        self._server = HTTPServer(("", self._port), self.Redirect)
        self._thread = threading.Thread(target = self._server.serve_forever)
    
    class Redirect(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(302)
            self.send_header('Location', self._url)
            self.end_headers()
    
    def __enter__(self):
        self._thread.start()    

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._server.shutdown()
        self._thread.join()
    
if __name__ == "__main__":
    import time
    with InspectorLocalServer("http://nyu.edu", 8080):
        time.sleep(5)
