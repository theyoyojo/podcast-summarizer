#!/bin/env python

import argparse
import tqdm
import warnings
import whisper
from utility import load_subdirectory

def transcribe(subdirectory_name):
    directory = load_subdirectory(subdirectory_name)

    warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

    pbar = tqdm.tqdm(total=directory['count'], desc="Transcribing Podcasts")
    pbar.update(0)
    for i in range(directory['count']):
        result = model.transcribe(f'{subdirectory_name}/{i}.mp3')
        with open(f'{subdirectory_name}/{i}.txt', 'w') as f:
            print(result['text'], file=f)
            pbar.update(1)

parser = argparse.ArgumentParser(prog='trancribe')

parser.add_argument('-d',
                    '--directory',
                    type=str,
                    required=True,
                    help='select directory with podcast files and directory')

model = whisper.load_model('base')

def main():
    args = parser.parse_args()
    transcribe(args.directory)

if __name__ == '__main__':
    main()
