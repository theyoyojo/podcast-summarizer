#!/usr/bin/env python3

import db
import sys
from utility import parse_abf
from chatgpt import chatgpt

def report(after, before, feeds):
    feed_list = db.get_feed_list(feeds)
    if not feed_list:
        print(f'fatal: no such feed list "{feeds}" found in database')
        exit(1)

    to_report = []
    report_entries = []
    for feedref in feed_list.feeds:
        for entry in feedref.feed.entries_in_range(after, before):
            if summary := entry.summarywork.bullet_points:
                to_report.append(summary)
                report_entries.append(entry)

    print('Generating report...', file=sys.stderr)
    if len(to_report) > 0:
        report_query = f'Combine all subsequent information, which is a series of docuuments separated by a single line containing "=====" that each summarize the key points from important information sources, into a clear and informative report:\n\n {(chr(10) + "=====" + chr(10)).join(to_report)}'

        report_text = chatgpt(report_query)
    else:
        report_text = 'Nothing to report.'
    return db.insert_report(after, before, feed_list, report_text, report_entries)

if __name__ == '__main__':
    args = parse_abf('report')
    report(args.after, args.before, args.feeds)
