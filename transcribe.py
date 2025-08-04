#!/bin/env python

import argparse
import tqdm
import warnings
import whisper
from utility import load_cache, cache_query, cache_write

def transcribe(feeds):
    cache = load_cache(f'.cache-{feeds}')

    warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

    pbar = tqdm.tqdm(total=cache['count'], desc="Transcribing Podcasts")
    pbar.update(0)
    for i in range(cache['count']):
        result = model.transcribe(f'{cache["dir"]}/{i}.mp3')
        if cache['podcasts'][i]['transcript'] is None:
            with open(f'{cache["dir"]}/{i}.txt', 'w') as f:
                print(result['text'], file=f)
        pbar.update(1)

parser = argparse.ArgumentParser(prog='trancribe')

parser.add_argument('-f',
                    '--feeds',
                    type=str,
                    required=True,
                    help='select json tile with rss feed list')

model = whisper.load_model('base')

def main():
    args = parser.parse_args()
    transcribe(args.feeds)

if __name__ == '__main__':
    main()
