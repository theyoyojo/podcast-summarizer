#!/usr/bin/env python3

from transformers import pipeline
import argparse
import json
import tqdm
from utility import load_subdirectory

def do_summarize(file, chunk_max_size=1024):
    text=None
    with open(file, 'r') as f:
        text = f.read()
    chunks = [text[i:i+chunk_max_size] for i in range(0, len(text), chunk_max_size)]
    summary = []
    for chunk in chunks:
        results = summarizer(chunk, max_length=130, min_length=30, do_sample=False)
        summary.append(results[0]['summary_text'])
    return ' '.join(summary)


def summarize(subdirectory_name):
    directory = load_subdirectory(subirectory_name)
    
    #warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

    pbar = tqdm.tqdm(total=directory['count'], desc="Summarizing Text")
    pbar.update(0)
    for i in range(directory['count']):
        result = do_summarize(f'{subdirectory_name}/{i}.txt')
        with open(f'{subdirectory_name}/{i}.summary.txt', 'w') as f:
            print(result, file=f)
            pbar.update(1)

parser = argparse.ArgumentParser(prog='summarize')

parser.add_argument('-d',
                    '--directory',
                    type=str,
                    required=True,
                    help='select directory with text files and directory')


summarizer = pipeline('summarization', model='facebook/bart-large-cnn')

def main():
    args = parser.parse_args()
    summarize(args.directory)


if __name__ == '__main__':
    main()
