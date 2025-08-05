#!/usr/bin/env python3

import db
import os
import sys
from tqdm import tqdm
import warnings
from utility import parse_abf

try:
    import mlx_whisper
    model = mlx_whisper.load_model("base.en")
except ModuleNotFoundError:
    import whisper
    model = whisper.load_model('base')


def transcribe(after, before, feeds):
    feed_list = db.get_feed_list_or_die(feeds)
    filtered_msg = "FP16 is not supported on CPU; using FP32 instead"
    warnings.filterwarnings("ignore", message=filtered_msg)

    os.makedirs('.cache', exist_ok=True)

    # save to a list so we can have an accurate progress bar later
    to_transcribe = []
    for feedref in feed_list.feeds:
        for entry in feedref.feed.entries_in_range(after, before):
            if entry.summarywork_type == 'audiosummarywork' and \
                    entry.summarywork.audio_path is not None and \
                    entry.summarywork.transcript is None:
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
