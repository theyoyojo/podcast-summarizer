#!/usr/bin/env python3

import json
import os
import requests
import urllib
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# === Custom HTTP handler ===
class SimpleAPIHandler(BaseHTTPRequestHandler):
    def return_json(self, data):
        # Send response
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({'count': len(data),
                                     'timestamp': datetime.now().timestamp(),
                                     'data': data}).encode('utf-8'))

    def do_GET(self):
        split = self.path.split('?')
        raw_path = split[0]
        query_str = split[1] if len(split) > 1 else ''
        queries = urllib.parse.parse_qs(query_str)
        match raw_path.split('/'):
            case ['','api', 'summary'] if (after := queries.get('after', None)) and (before := queries.get('before', None)):
                file = f'{after[0]}_{before[0]}/general.summary.txt'
                print(file)
                if os.path.exists(file):
                    with open(file, 'r') as f:
                        content = f.read()
                        self.return_json(content)
                else:
                    self.return_json('fuck')

            case _:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Not Found")

# === Server entrypoint ===
def run(server_class=ThreadingHTTPServer, handler_class=SimpleAPIHandler, port=8870):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    print(f"Serving on http://localhost:{port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run()

