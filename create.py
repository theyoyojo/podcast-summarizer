#!/bin/env python

import time
import argparse
import feedparser
from datetime import datetime
from dataclasses import dataclass

@dataclass
class Podcast:
    title: str
    description: str
    rss: str
    website: str

parser = argparse.ArgumentParser(prog='create_summary')

def date_type(datestr):
    try:
        return datetime.strptime(datestr, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f'Bad date argument: {datestr} (Excepted YYYY-MM-DD)')


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

def main(args):
    with open('podcasts', 'r', encoding='utf-8') as p:
        entries = p.read().split("---")

    podcasts = []

    for e in entries:
        v = {'title':'', 'description':'','rss':'','website':''}
        lines = [l.strip() for l in e.strip().splitlines()]
        for l in lines:
            match l.split(':', 1):
                case ['Title', title]:
                    v['title'] = title.strip()
                case ['Description', description]:
                    v['description'] = description.strip()
                case ['RSS Feed', rss]:
                    v['rss'] = rss.strip()
                case ['Website', website]:
                    v['website'] = website.strip()
                case _:
                    raise Exception('Unexpected field')
        podcasts.append(Podcast(title=v['title'], description=v['description'], rss=v['rss'], website=v['website']))

    feeds = []
    for p in podcasts:
        feed = feedparser.parse(p.rss)
        if feed.bozo:
            print(f'FAIL: cannot parse {p.rss}: {feed.bozo_exception}')
        else:
            feeds.append(feed)


    print('Before', args.before)
    print('After', args.after)

    for feed in feeds:
        print(f'Search {feed.feed.get("title", "N/A")}')
        for entry in feed.entries:
            if not hasattr(entry, "published_parsed"):
                continue
            publication_date = datetime.fromtimestamp(time.mktime(entry.published_parsed))

            if args.after <= publication_date <= args.before:
                print(f'{entry.title} published {publication_date} at {entry.get("link", "N/A")}')
                for i, enclosure in enumerate(entry.get("enclosures", [])):
                    print(f'\t{i}: {enclosure.href}')

if __name__ == '__main__':
    main(parser.parse_args())
