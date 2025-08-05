#!/usr/bin/env python3

import json
import os
import db
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
        self.wfile.write(json.dumps({'timestamp_served': datetime.now().timestamp(),
                                     'data': data}).encode('utf-8'))

    def do_GET(self):
        split = self.path.split('?')
        raw_path = split[0]
        query_str = split[1] if len(split) > 1 else ''
        queries = urllib.parse.parse_qs(query_str)
        content = []

        match raw_path.split('/'):
            case ['','api', target] if (after := queries.get('after', None)) and (before := queries.get('before', None)) and (feeds := queries.get('feeds')):

                if report := db.get_latest_report(after, before, feeds):
                    self.return_json({'text':report.text, 'after':report.after.isoformat(), 'before':report.before.isoformat(), 'timestamp_generated': report.timestamp})
                else:
                    self.return_json('no extant generated report')
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

