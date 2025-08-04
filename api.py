#!/usr/bin/env python3

import json
import os
import requests
import urllib
from datetime import datetime
from dateutil.relativedelta import relativedelta
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
        # truncate to first of month for now
        # all in chunks
        def make_dir_list(after, before):
            dta = datetime.strptime(after, "%Y-%m-%d")
            dfb = datetime.strptime(before, "%Y-%m-%d")
            first = datetime(year=dta.year, month=dta.month, day=1)
            second = datetime(year=dta.year, month=dta.month+, day=1)
            print(first,second)
            # this way partial months are included
            dir_list = []
            while second <= dtb:
                dir_list.append(f'{first.date()}_{second.date()}')
                first += relativedelta(months=1)
                second += relativedelta(months=1)
            return dir_list



        split = self.path.split('?')
        raw_path = split[0]
        query_str = split[1] if len(split) > 1 else ''
        queries = urllib.parse.parse_qs(query_str)
        content = []
        match raw_path.split('/'):
            case ['','api', target] if (after := queries.get('after', None)) and (before := queries.get('before', None)):
                dir_list = make_dir_list(after[0], before[0])
                for d in dir_list:
                    print(d)
                    match target:
                        case 'summary':
                            file = f'{d}/general.summary.txt'
                            if os.path.exists(file):
                                with open(file, 'r') as f:
                                    content.append(f.read())
                        case 'directory':
                            file = f'{d}/directory.json'
                            if os.path.exists(file):
                                with open(file, 'r') as f:
                                    content.append(f.read())
                                    self.return_json([json.loads(j) for j in content])
                        case _:
                            self.send_response(404)
                            self.end_headers()
                            self.wfile.write(b"Not Found")
                self.return_json(content)
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

