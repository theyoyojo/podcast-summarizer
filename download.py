#!/bin/env python3

from utility import date_type, download_file
import argparse
import db
import os
from tqdm import tqdm


# after is inclusive but before is exclusive
def download(after, before, feeds):
    feed_list = db.get_feed_list(feeds)
    if not feed_list:
        print(f'fatal: no such feed list "{feeds}" found in database')
        exit(1)

    os.makedirs('.cache', exist_ok=True)

    # save to a list so we can have an accurate progress bar later
    to_download = []
    for feedref in feed_list.feeds:
        for entry in feedref.feed.entries_in_range(after, before):
            if not entry.is_downloaded():
                to_download.append(entry)

    if len(to_download) < 1:
        print("Nothing to download.")
        return

    pbar = tqdm(total=len(to_download), desc="Downloading Content")
    pbar.update(0)
    for e in to_download:
        e.download()
        pbar.update(1)


parser = argparse.ArgumentParser(prog='download')

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

if __name__ == "__main__":
    args = parser.parse_args()
    download(args.after, args.before, args.feeds)
