#!/usr/bin/env python3

from utility import parse_abf
from update import update
from download import download
from transcribe import transcribe
from summarize import summarize
from report import report


# example invocation: ./pipeline.py -a 2025-07-01 -b 2025-08-01 -f timber.json
def pipeline(after, before, feeds):
    update(feeds)
    download(after, before, feeds)
    transcribe(after, before, feeds)
    summarize(after, before, feeds)
    r = report(after, before, feeds)
    print(r)


if __name__ == '__main__':
    args = parse_abf('pipeline')
    pipeline(args.after, args.before, args.feeds)
