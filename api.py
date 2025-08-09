#!/usr/bin/env python3

import json
import db
import urllib
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def fmt_dt(dt):
    return dt.astimezone().isoformat()


class SimpleAPIHandler(BaseHTTPRequestHandler):
    def return_json_error(self, error, code=404):
        self.send_response(code)
        self.end_headers()
        self.wfile.write(json.dumps({
            'timestamp': fmt_dt(datetime.now()),
            'error': error
        }).encode('utf-8'))

    def return_json(self, data):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({
            'timestamp': fmt_dt(datetime.now()),
            'data': data
        }).encode('utf-8'))

    def do_GET(self):
        split = self.path.split('?')
        raw_path = split[0]
        query_str = split[1] if len(split) > 1 else ''
        queries = urllib.parse.parse_qs(query_str)

        if raw_path[-1] == '/':
            raw_path = raw_path[:-1]
        match raw_path.split('/'):
            case ['', 'api', 'directory']:
                return self.return_json(db.feed_directory())
            case ['', 'api', 'reports', source]:
                after = queries.get('after', None)
                before = queries.get('before', None)
                if after is None or before is None:

                    return self.return_json([{'after': fmt_dt(r.after), 'before': fmt_dt(r.before)}
                                             for r in db.get_reports_by_source(source)])

                if report := db.get_latest_report(after, before, source):
                    return self.return_json({'text': report.text,
                                             'after': fmt_dt(report.after),
                                             'before': fmt_dt(report.before),
                                             'timestamp': report.timestamp})
                else:
                    return self.return_json_error('report not available yet',
                                                  code=425)  # 425 Too Early
            case ['', 'api', 'sources', source, 'feeds']:
                # potentially allow filtering output fields
                if feeds := db.get_feeds_by_source(source):
                    return self.return_json([{'id': feed.id} for feed in feeds])
                else:
                    return self.return_json_error(f'no feeds for source {source}')
            case ['', 'api', 'sources', source]:
                if source := db.get_source(source):
                    return self.return_json({'source': source,
                                             'last_updated': db.get_last_updated_by_source(source)})
                else:
                    return self.return_json_error(f'no such source {source}')
            case ['', 'api', 'feeds', feed_id, 'entries']:
                after = queries.get('after', None)
                before = queries.get('before', None)
                if entries := db.get_entries_in_range_by_feed_id(after, before, feed_id):
                    self.return_json([{'id': entry.id,
                                       'title': entry.title}
                                      for entry in entries])
                else:
                    return self.return_json_error(f'no matching entries in {feed_id} \
                                           (after={after}, before={before})')
            case ['', 'api', 'feeds', feed_id]:
                if feed := db.get_feed_by_id(feed_id):
                    return self.return_json({'id': feed.id})
                else:
                    return self.return_json_error(f'no such feed_id {feed_id}')
            case ['', 'api', 'entries', entry_id]:
                # potentially allow filtering output fields
                if entry := db.get_entry_by_id(entry_id):
                    return self.return_json({'id': entry.id})
                else:
                    return self.return_json_error(f'no such entry_id {entry_id}')
            case _:
                return self.return_json_error('endpoint not found')


def run(server_class=ThreadingHTTPServer, handler_class=SimpleAPIHandler,
        port=8870):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    print(f"Serving on http://localhost:{port}")
    httpd.serve_forever()


if __name__ == '__main__':
    run()
