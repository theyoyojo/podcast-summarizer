#!/bin/env python

import time
import argparse
import feedparser
import requests
import pathlib
import os
import shutil
import json
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


def download_file(url, local_filename=None):
    """
    Downloads a file from a URL and saves it to the current directory.

    Args:
        url (str): The URL of the file to download.
        local_filename (str, optional): The name to save the file as.
                                         If None, the function will try to
                                         determine the filename from the URL.
                                         Defaults to None.
    """
    if local_filename is None:
        local_filename = url.split('/')[-1]

    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }


    try:
        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"File downloaded successfully as '{local_filename}'")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    except IOError as e:
        print(f"An error occurred while writing the file: {e}")

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


    filename = f'{args.after.date()}_{args.before.date()}'
    data = {
        'count': 0,
        'timestamp': datetime.now().isoformat(),
        'podcasts': []
    }

    print(f'Searching between {args.before} and {args.after}...')
    for feed in feeds:
        found=0
        print(f'Searching {feed.feed.get("title", "N/A")}...')
        for entry in feed.entries:
            if not hasattr(entry, "published_parsed"):
                continue
            publication_date = datetime.fromtimestamp(time.mktime(entry.published_parsed))

            if args.after <= publication_date <= args.before:
                data
                found += 1
                print(f'[Title] {entry.title}\n[Published On] {publication_date}\n[More Info] {entry.get("link", "N/A")}')
                for i, enclosure in enumerate(entry.get("enclosures", [])):
                    print(f'\t[DOWNLOAD] {enclosure.href}')
                download_link = entry.get('enclosures', [])[0] if entry.get('enclosures', []) else None
                data['podcasts'].append({
                    'title': entry.title,
                    'timestamp': publication_date.isoformat(),
                    'more_info': entry.get('link', None),
                    'download': download_link
                })
                data['count'] += 1


        if not found:
            print('\t<nothing found>')


    exec_wd = pathlib.Path.cwd()
    new_dir_path = pathlib.Path(filename)

    try:
        # if exists, wipe
        if new_dir_path.exists():
            shutil.rmtree(new_dir_path)
        new_dir_path.mkdir(exist_ok=False)

        os.chdir(new_dir_path)
        for i in range(data['count']):
            download_file(data['podcasts'][i]['download']['href'], local_filename=f'{i}.mp3')
        with open('info.json', 'w') as f:
            print(json.dumps(data), file=f)

    finally:
        os.chdir(exec_wd)


if __name__ == '__main__':
    main(parser.parse_args())
