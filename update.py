#!/usr/bin/env python3

import argparse
import feedparser
import json
import datetime
import time
import db

from tqdm import tqdm

# feeds is a json file containing a list of {"title":<text>, "rss":<feed link>}
def update(feeds):
    try:
        with open(feeds, 'r', encoding='utf-8') as f:
            feeds_json = json.loads(f.read())
    except FileNotFoundError as e:
        print(f'fatal: cannot open "{feeds}": {e}')
        exit(1)

    feed_list = db.insert_feed_list(feeds)
    feeds = []
    pbar = tqdm(total=len(feeds_json), desc='Updating Feeds')
    pbar.update(0)
    for f in feeds_json:
        parsed = feedparser.parse(f['rss'])
        if parsed.bozo:
            print(f'failed to parse "{p["rss"]}": {feed.bozo_exception}')
        feed = db.insert_feed(parsed.feed)
        db.add_feed_list_feed(feed_list=feed_list, feed=feed)
        for entry in parsed.entries:
            db.insert_entry(feed, entry)
        pbar.update(1)

parser = argparse.ArgumentParser(prog='update')

parser.add_argument('-f',
                    '--feeds',
                    type=str,
                    required=True,
                    help='select json tile with rss feed list to update')


if __name__ == "__main__":
    args = parser.parse_args()
    update(args.feeds)
