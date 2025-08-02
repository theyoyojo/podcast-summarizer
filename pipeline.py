#!/bin/env python

import argparse
import tqdm

from gather import gather
from transcribe import transcribe
from chatgpt import chatgpt
from utility import load_subdirectory, date_type

# example invocation: ./pipeline.py -a 2025-07-01 -b 2025-08-01
def pipeline(after, before):
    gather(after, before)
    subdirectory_name = f'{after.date()}_{before.date()}'
    transcribe(subdirectory_name)
    directory = load_subdirectory(subdirectory_name)
    pbar = tqdm.tqdm(total=directory['count'], desc="Asking ChatGPT")
    pbar.update(0)
    general_query = 'Give me a short report using the following input data:\n'
    for i in range(directory['count']):
        content=None
        with open(f'{subdirectory_name}/{i}.txt', 'r') as f:
            if (content := f.read()):
                summary = chatgpt(f'bullet points of {content}')
                with open(f'{subdirectory_name}/{i}.bullets.txt', 'w') as g:
                    print(summary, file=g)
                general_query += summary
                general_query += '\n'
        pbar.update(1)

    general_summary = chatgpt(general_query)
    with open(f'{subdirectory_name}/general.summary.txt', 'w') as f:
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


def main():
    args = parser.parse_args()
    pipeline(args.after, args.before)

if __name__ == '__main__':
    main()
