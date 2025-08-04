#!/usr/bin/env python3

import argparse
import tqdm

from gather import gather
from transcribe import transcribe
from chatgpt import chatgpt
from utility import load_cache, date_type

# example invocation: ./pipeline.py -a 2025-07-01 -b 2025-08-01
def pipeline(after, before, feeds):
    gather(after, before, feeds)
    cache = load_cache(f'.cache-{feeds}')
    transcribe(feeds)
    pbar = tqdm.tqdm(total=cache['count'], desc="Asking ChatGPT")
    pbar.update(0)
    general_query = 'Give me a short report using the following input data:\n'
    for i in range(cache['count']):
        content=None
        with open(f'{cache["dir"]}/{i}.txt', 'r') as f:
            if (content := f.read()):
                summary = chatgpt(f'bullet points of {content}')
                with open(f'{cache["dir"]}/{i}.bullets.txt', 'w') as g:
                    print(summary, file=g)
                general_query += summary
                general_query += '\n'
        pbar.update(1)

    general_summary = chatgpt(general_query)
    with open(f'{cache["dir"]}/general.summary.txt', 'w') as f:
        print(general_summary, file=f)

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
