#!/bin/env python

from dataclasses import dataclass

@dataclass
class Podcast:
    title: str
    description: str
    rss: str
    website: str

def main():
    with open('podcasts', 'r', encoding='utf-8') as p:
        entries = p.read().split("---")

    podcasts = []

    for e in entries:
        v = {'title':'', 'description':'','rss':'','website':''}
        lines = [l.strip() for l in e.strip().splitlines()]
        for l in lines:
            match l.split(':', 1):
                case ['Title', title]:
                    v['title'] = title
                case ['Description', description]:
                    v['description'] = description
                case ['RSS Feed', rss]:
                    v['rss'] = rss
                case ['Website', website]:
                    v['website'] = website
                case _:
                    raise Exception("Unexpected field")
        podcasts.append(Podcast(title=v['title'], description=v['description'], rss=v['rss'], website=v['website']))

    print(podcasts)


if __name__ == '__main__':
    main()
