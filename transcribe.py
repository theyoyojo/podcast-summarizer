#!/bin/env python

import argparse
import json
import tqdm
import warnings
import whisper

parser = argparse.ArgumentParser(prog='trancribe')

parser.add_argument('-d',
                    '--directory',
                    type=str,
                    required=True,
                    help='select directory with podcast files and directory')

model = whisper.load_model('base')

def main():
    args = parser.parse_args()
    directory = None

    try:
        file_path = f'{args.directory}/directory.json'
        with open(file_path, 'r') as f:
            directory = json.loads(f.read())
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{file_path}'. The file may be invalid.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

    pbar = tqdm.tqdm(total=directory['count'], desc="Podcast transcription")
    pbar.update(0)
    for i in range(directory['count']):
        result = model.transcribe(f'{args.directory}/{i}.mp3')
        with open(f'{args.directory}/{i}.txt', 'w') as f:
            print(result['text'], file=f)
            pbar.update(1)


if __name__ == '__main__':
    main()
