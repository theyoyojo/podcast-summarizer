#!/usr/bin/env python3

import db
import os
import sys
import argparse
from tqdm import tqdm
import warnings
from utility import date_type, parse_abf

try:
    import mlx_whisper
    model = mlx_whisper.load_model("base.en")
except:
    import whisper
    model = whisper.load_model('base')

def transcribe(after, before, feeds):
    feed_list = db.get_feed_list(feeds)
    if not feed_list:
        print(f'fatal: no such feed list "{feeds}" found in database')
        exit(1)
    warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

    os.makedirs('.cache', exist_ok=True)

    # save to a list so we can have an accurate progress bar later
    to_transcribe = []
    for feedref in feed_list.feeds:
        for entry in feedref.feed.entries_in_range(after, before):
            if entry.summarywork_type == 'audiosummarywork' and entry.summarywork.audio_path is not None and entry.summarywork.transcript is None:
                to_transcribe.append(entry)

    if len(to_transcribe) == 0:
        print("Nothing to transcribe.", file=sys.stderr)
        return

    pbar = tqdm(total=len(to_transcribe), desc="Transcribing Audio")
    pbar.update(0)
    for e in to_transcribe:
        result = model.transcribe(e.summarywork.audio_path)
        sw = e.summarywork
        sw.transcript = result['text']
        sw.save()
        pbar.update(1)

if __name__ == '__main__':
    args = parse_abf('transcribe')
    transcribe(args.after, args.before, args.feeds)
