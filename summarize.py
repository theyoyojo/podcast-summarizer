#!/usr/bin/env python3

import db
import sys
from tqdm import tqdm
from utility import parse_abf
from chatgpt import chatgpt

def summarize(after, before, feeds):
    feed_list = db.get_feed_list(feeds)
    if not feed_list:
        print(f'fatal: no such feed list "{feeds}" found in database')
        exit(1)

    to_summarize = []
    for feedref in feed_list.feeds:
        for entry in feedref.feed.entries_in_range(after, before):
            if ((entry.summarywork_type == 'audiosummarywork' and (text := entry.summarywork.transcript)) \
                    or (entry.summarywork_type == 'articlesummarywork' and (text := entry.summarywork.full_text))) \
                    and entry.summarywork.bullet_points is None:
                to_summarize.append((entry, text))

    if len(to_summarize) == 0:
        print("Nothing to summarize.", file=sys.stderr)
        return

    pbar = tqdm(total=len(to_summarize), desc="Summarizing Text")
    pbar.update(0)
    for p in to_summarize:
        summary = chatgpt(f'Give me a comprehensive summary of the following document in bullet point format: {p[1]}')
        sw = p[0].summarywork
        sw.bullet_points = summary
        sw.save()
        pbar.update(1)

if __name__ == '__main__':
    args = parse_abf('summarize')
    summarize(args.after, args.before, args.feeds)
