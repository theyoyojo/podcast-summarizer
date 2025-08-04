#!/bin/env python

import argparse
import feedparser
import json
import pathlib
import os
import requests
import shutil
import time
import tqdm

from dataclasses import dataclass
from datetime import datetime
from utility import date_type, load_cache, cache_add_range, cache_query, cache_write

@dataclass
class Podcast:
    title: str
    description: str
    rss: str
    website: str

parser = argparse.ArgumentParser(prog='create_summary')


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
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    except IOError as e:
        print(f"An error occurred while writing the file: {e}")

def gather(after, before, feeds):
    podcasts = {}
    with open(feeds, 'r', encoding='utf-8') as f:
        podcasts = json.loads(f.read())
        
    with open('podcasts', 'r', encoding='utf-8') as p:
        entries = p.read().split("---")

    feed_data = []
    pbar = tqdm.tqdm(total=len(podcasts), desc='Updating Feeds')
    pbar.update(0)
    for p in podcasts:
        feed = feedparser.parse(p['rss'])
        if feed.bozo:
            print(f'FAIL: cannot parse {p['rss']}: {feed.bozo_exception}')
        else:
            feed_data.append(feed)
        pbar.update(1)


    cache = load_cache(f'.cache-{feeds}')

    need_download = []
    for feed in feed_data:
        for entry in feed.entries:
            if not hasattr(entry, "published_parsed"):
                continue
            publication_date = datetime.fromtimestamp(time.mktime(entry.published_parsed))

            if cache_query(cache, publication_date, publication_date):
                continue
            if after <= publication_date <= before:
                download_link = entry.get('enclosures', [])[0] if entry.get('enclosures', []) else None
                cache['podcasts'].append({
                    'title': entry.title,
                    'timestamp': publication_date.isoformat(),
                    'more_info': entry.get('link', None),
                    'download': download_link,
                    'audio': None,
                    'transcript': None,
                    'bullets': None
                })
                need_download.append(cache['count'])
                cache['count'] += 1
    exec_wd = pathlib.Path.cwd()
    try:
        pbar = tqdm.tqdm(total=cache['count'],
                         desc="Downloading Podcasts")
        pbar.update(0)
        os.chdir(cache['dir'])
        for i in need_download:
            name = f'{i}.mp3'

            if cache['podcasts'][i]['audio'] is None:
                download_file(cache['podcasts'][i]['download']['href'],
                              local_filename=name)
                cache['podcasts'][i]['audio'] = name
            pbar.update(1)
        cache_write(cache, after, before)
    finally:
        os.chdir(exec_wd)


def main():
    args = parser.parse_args()
    gather(args.after, args.before, args.feeds)

if __name__ == '__main__':
    main()
