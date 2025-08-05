#!/usr/bin/env python3

import db
import os
from tqdm import tqdm
from utility import parse_abf


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


if __name__ == "__main__":
    args = parse_abf('download')
    download(args.after, args.before, args.feeds)
