#!/usr/bin/env python3

import argparse
from tqdm import tqdm
import db

from update import update
from download import download
from transcribe import transcribe
from chatgpt import chatgpt
from utility import date_type

def summarize(after, before, feeds):
    feed_list = db.get_feed_list(feeds)
    if not feed_list:
        print(f'fatal: no such feed list "{feeds}" found in database')
        exit(1)

    to_summarize = []
    for feedref in feed_list.feeds:
        for entry in feedref.feed.entries_in_range(after, before):
            if ((entry.summarywork_type == 'audiosummarywork' and (text := entry.summarywork.transcript)) \
                    or (entry.summarywork_type == 'articleummarywork' and (text := entry.summarywork.full_text))) \
                    and entry.summarywork.bullet_points is None:
                to_summarize.append((entry, text))

    if len(to_summarize) == 0:
        print("Nothing to summarize.")
        return

    pbar = tqdm(total=len(to_summarize), desc="Summarizing Text")
    pbar.update(0)
    for p in to_summarize:
        summary = chatgpt(f'Give me a comprehensive summary of the following document in bullet point format: {p[1]}')
        sw = p[0].summarywork
        sw.bullet_points = summary
        sw.save()
        pbar.update(1)

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

    print('Generating report...')
    report_query = f'Combine all subsequent information, which is a series of docuuments separated by a single line containing "=====" that each summarize the key points from important information sources, into a clear and informative report:\n\n {"\n=====\n".join(to_report)}'

    report_text = chatgpt(report_query)
    db.insert_report(after, before, feed_list.feeds, report_text, report_entries)


# example invocation: ./pipeline.py -a 2025-07-01 -b 2025-08-01 -f timber.json
def pipeline(after, before, feeds):
    update(feeds)
    download(after, before, feeds)
    transcribe(after, before, feeds)
    summarize(after, before, feeds)
    report(after, before, feeds)
    print(db.get_latest_report(after, before, feeds))


parser = argparse.ArgumentParser(prog='pipeline')

parser.add_argument('-a',
                    '--after',
                    type=date_type,
                    required=True,
                    help='select content published after this date')

parser.add_argument('-b',
                    '--before',
                    type=date_type,
                    required=True,
                    help='select content published before this date')

parser.add_argument('-f',
                    '--feeds',
                    type=str,
                    required=True,
                    help='select json tile with rss feed list')


def main():
    args = parser.parse_args()
    pipeline(args.after, args.before, args.feeds)

if __name__ == '__main__':
    main()
