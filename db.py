#!/bin/env python3

from peewee import SqliteDatabase, Model, TextField, CharField, IntegerField, ForeignKeyField, DateTimeField
import hashlib
from datetime import datetime
import time

DB = SqliteDatabase("sources.db")

class BaseModel(Model):
    class Meta:
        database = DB

class FeedList(BaseModel):
    source = CharField(max_length=255, null=False, unique=True)

# class Episode(BaseModel):
#     # sha256 output
#     id = CharField(primary_key=True, max_length=64)
#     title = TextField()
#     audio_href = TextField()
#     timestamp = TextField()
#     info_href = TextField()
#     audio_filename = TextField()
#     transcript_filename = TextField()
#     bullets_filename = TextField()
#     feed = ForeignKeyField(Feed, backref='episodes')


class Feed(BaseModel):
    # Feed unique ID
    id = CharField(primary_key=True, max_length=64, null=False, unique=True)

    # Title of the feed
    title = CharField(max_length=255, null=True)
    
    # URL to the website or feed source
    link = CharField(max_length=2048, null=True)
    
    # Description or subtitle of the feed
    description = TextField(null=True)
    
    # Language code (e.g., "en-US")
    language = CharField(max_length=10, null=True)
    
    # Last updated date/time as string
    updated = CharField(null=True)
    
    # Parsed version of `updated`
    updated_parsed = DateTimeField(null=True)
    
    # Feed author or publisher
    author = CharField(max_length=100, null=True)
    
    # Copyright or rights information
    rights = CharField(max_length=255, null=True)
    
    # Subtitle or tagline of the feed
    subtitle = CharField(max_length=255, null=True)


class FeedListFeed(BaseModel):
    feed = ForeignKeyField(Feed, backref='feed_list')
    feed_list = ForeignKeyField(FeedList, backref='feeds')


class FeedAuthorDetail(BaseModel):
    # Related feed
    feed = ForeignKeyField(Feed, backref='author_details', on_delete='CASCADE')

    # Author's name (up to 100 chars)
    name = CharField(max_length=100, null=True)

    # Author's email (up to 255 chars)
    email = CharField(max_length=255, null=True)


class FeedImage(BaseModel):
    # Related feed
    feed = ForeignKeyField(Feed, backref='images', on_delete='CASCADE')

    # Image URL (up to 2048 chars)
    url = CharField(max_length=2048, null=True)

    # Image title (up to 255 chars)
    title = CharField(max_length=255, null=True)

    # Image link (up to 2048 chars)
    link = CharField(max_length=2048, null=True)


class Entry(BaseModel):
    # Related feed
    feed = ForeignKeyField(Feed, backref='entries', on_delete='CASCADE')

    # Unique identifier of the entry (64 chars in sha256)
    id = CharField(primary_key=True, max_length=64)

    # Entry title (up to 255 chars)
    title = CharField(max_length=255, null=True)

    # URL to the full content or web page (up to 2048 chars)
    link = CharField(max_length=2048, null=True)

    # Short summary or description of the entry (long text)
    summary = TextField(null=True)

    # Published date as string (ISO 8601, ~30 chars)
    published = CharField(max_length=30, null=True)

    # Parsed published date
    published_parsed = DateTimeField(null=True)

    # Last updated date as string (ISO 8601, ~30 chars)
    updated = CharField(max_length=30, null=True)

    # Parsed updated date
    updated_parsed = DateTimeField(null=True)

    # Author of the entry (up to 100 chars)
    author = CharField(max_length=100, null=True)


class EntryAuthorDetail(BaseModel):
    # Related entry
    entry = ForeignKeyField(Entry, backref='author_details', on_delete='CASCADE')

    # Author's name (up to 100 chars)
    name = CharField(max_length=100, null=True)

    # Author's email (up to 255 chars)
    email = CharField(max_length=255, null=True)


class EntryTag(BaseModel):
    # Related entry
    entry = ForeignKeyField(Entry, backref='tags', on_delete='CASCADE')

    # Tag or category term (up to 100 chars)
    term = CharField(max_length=100, null=True)

    # Scheme or domain of the tag (up to 255 chars)
    scheme = CharField(max_length=255, null=True)

    # Human-readable label for the tag (up to 255 chars)
    label = CharField(max_length=255, null=True)


class EntryContent(BaseModel):
    # Related entry
    entry = ForeignKeyField(Entry, backref='content', on_delete='CASCADE')

    # Content type (e.g., "text/html") (up to 50 chars)
    type = CharField(max_length=50, null=True)

    # Language of the content (e.g., "en-US") (up to 10 chars)
    language = CharField(max_length=10, null=True)

    # The actual content string (long text)
    value = TextField(null=True)


class EntryMediaContent(BaseModel):
    # Related entry
    entry = ForeignKeyField(Entry, backref='media_contents', on_delete='CASCADE')

    # Media URL (up to 2048 chars)
    url = CharField(max_length=2048, null=True)

    # Media type (e.g., image/jpeg) (up to 100 chars)
    type = CharField(max_length=100, null=True)

    # Medium type (e.g., image, video) (up to 50 chars)
    medium = CharField(max_length=50, null=True)


class EntryEnclosure(BaseModel):
    # Related entry
    entry = ForeignKeyField(Entry, backref='enclosures', on_delete='CASCADE')

    # Enclosure URL (e.g., audio or file) (up to 2048 chars)
    url = CharField(max_length=2048, null=True)

    # Length in bytes
    length = IntegerField(null=True)

    # MIME type of the enclosure (up to 100 chars)
    type = CharField(max_length=100, null=True)


def hash_guid(guid):
    return hashlib.sha256(guid.encode('utf-8')).hexdigest()

def insert_feed(feed_data):
    # error if none of these values has be hashed
    feed_id = hash_guid(feed_data.get("id", feed_data.get("link", feed_data["title"])))

    feed, _ = Feed.get_or_create(
        id=feed_id,
        defaults={
            'title': feed_data.get('title'),
            'link': feed_data.get('link'),
            'description': feed_data.get('description'),
            'language': feed_data.get('language'),
            'updated': feed_data.get('updated'),
            'updated_parsed': datetime.fromtimestamp(time.mktime(feed_data.get('updated_parsed'))),
            'author': feed_data.get('author'),
            'rights': feed_data.get('rights'),
            'subtitle': feed_data.get('subtitle'),
        }
    )

    # Feed authors (if any)
    for author in feed_data.get('authors', []):
        FeedAuthorDetail.get_or_create(
            feed=feed,
            name=author.get('name'),
            email=author.get('email'),
        )

    # Feed image (if any)
    if 'image' in feed_data:
        FeedImage.get_or_create(
            feed=feed,
            url=feed_data['image'].get('href'),
            title=feed_data['image'].get('title'),
            link=feed_data['image'].get('link'),
        )

    return feed


def insert_entry(feed, entry_data):
    # error if none of these values has be hashed
    entry_id = hash_guid(entry_data.get("id", entry_data.get("link", entry_data["title"])))

    entry, _ = Entry.get_or_create(
        id=entry_id,
        defaults={
            'feed': feed,
            'title': entry_data.get('title'),
            'link': entry_data.get('link'),
            'summary': entry_data.get('summary'),
            'published': entry_data.get('published'),
            'published_parsed': datetime.fromtimestamp(time.mktime(entry_data.get('published_parsed'))),
            'updated': entry_data.get('updated'),
            'updated_parsed': datetime.fromtimestamp(time.mktime(entry_data.get('updated_parsed'))),
            'author': entry_data.get('author'),
        }
    )

    # Entry authors
    for author in entry_data.get('authors', []):
        EntryAuthorDetail.get_or_create(
            entry=entry,
            name=author.get('name'),
            email=author.get('email'),
        )

    # Entry tags
    for tag in entry_data.get('tags', []):
        EntryTag.get_or_create(
            entry=entry,
            term=tag.get('term'),
            scheme=tag.get('scheme'),
            label=tag.get('label'),
        )

    # Entry content
    for content in entry_data.get('content', []):
        EntryContent.get_or_create(
            entry=entry,
            type=content.get('type'),
            language=content.get('language'),
            value=content.get('value'),
        )

    # Media content
    for media in entry_data.get('media_content', []):
        EntryMediaContent.get_or_create(
            entry=entry,
            url=media.get('url'),
            type=media.get('type'),
            medium=media.get('medium'),
        )

    # Enclosures
    for enclosure in entry_data.get('enclosures', []):
        EntryEnclosure.get_or_create(
            entry=entry,
            url=enclosure.get('url'),
            length=int(enclosure.get('length', 0)) if enclosure.get('length') else None,
            type=enclosure.get('type'),
        )

    return entry


def insert_feed_list(feeds):
    feed_list, _ = FeedList.get_or_create(
        defaults={
            'source': feeds,
        }
    )
    return feed_list

def add_feed_list_feed(feed_list, feed):
    return FeedListFeed.get_or_create(feed_list=feed_list, feed=feed)
    

if __name__ == '__main__':
    DB.create_tables(BaseModel.__subclasses__())
