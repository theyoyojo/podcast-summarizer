#!/usr/bin/env python3

from peewee import SqliteDatabase, Model, TextField, CharField, \
    IntegerField, ForeignKeyField, DateTimeField
import hashlib
from datetime import datetime
import time
from utility import download_file

DB = SqliteDatabase("sources.db")


class BaseModel(Model):
    class Meta:
        database = DB


class FeedList(BaseModel):
    source = CharField(max_length=255, null=False, unique=True)


# a summary of summaries
class Report(BaseModel):
    timestamp = DateTimeField()
    after = DateTimeField()
    before = DateTimeField()
    text = TextField(null=True)
    feedlist = ForeignKeyField(FeedList, backref='reports', null=True)

    @property
    def audiosummarywork(self):
        return (AudioSummaryWork
                .select()
                .join(Reportable, on=(Reportable.reportable_id == self.id))
                .join(Report)
                .where(
                    (Report.id == self.id)
                    & (Reportable.reportable_type == 'audiosummarywork')  # NOQA: W503
                ))

    @property
    def articlesummarywork(self):
        return (ArticleSummaryWork
                .select()
                .join(Reportable, on=(Reportable.reportable_id == self.id))
                .join(Report)
                .where(
                    (Report.id == self.id)
                    & (Reportable.reportable_type == 'articlesummarywork')  # NOQA: W503
                ))

    def __str__(self):
        return f'''{self.text}\n\n\
                *[Generated at {self.timestamp} \
                from {self.feedlist.source} \
                after {self.after} \
                before {self.before}]*
                '''.strip()


def insert_report(after, before, feedlist, text, entries):
    report, _ = Report.get_or_create(
        timestamp=datetime.now().isoformat(),
        defaults={
            'after': after,
            'before': before,
            'text': text,
            'feedlist': feedlist,
        }
    )

    for e in entries:
        Reportable.get_or_create(
            report=report,
            defaults={
                'reportable_id': e.summarywork_id,
                'reportable_type': e.summarywork_type,
            }
        )

    return report


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

    # after is inclusive but before is exclusive
    def entries_in_range(self, after, before):
        entries = (self.entries
                   .select()
                   .where(
                       (after <= Entry.published_parsed)
                       & (Entry.published_parsed < before))  # NOQA: W503
                   .execute())
        return entries


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


class AudioSummaryWork(BaseModel):
    # same ID as entry
    id = CharField(primary_key=True, max_length=64, null=False, unique=True)
    audio_path = CharField(max_length=2048, null=True)
    transcript = TextField(null=True)
    bullet_points = TextField(null=True)

    @property
    def entry(self):
        return Entry.select().where(
            (Entry.summarywork_id == self.id)
            & (Entry.summarywork_type == 'audiosummarywork')).first()  # NOQA: W503

    def download(self):
        path = f'.cache/{self.entry.id}.mp3'
        download_file(self.entry.enclosures[0].url, local_filename=path)
        self.audio_path = path
        self.save()

    @property
    def reports(self):
        return (Report.select().join(Reportable).where(
            (Report.reportables.reportable_id == self.id)
            & (Report.reportables.reportable_type == 'audiosummarywork')))  # NOQA: W503


class ArticleSummaryWork(BaseModel):
    # same ID as entry
    id = CharField(primary_key=True, max_length=64, null=False, unique=True)
    # might be in HTML
    full_text = TextField(null=True)
    bullet_points = TextField(null=True)

    @property
    def entry(self):
        return Entry.select().where(
            (Entry.summarywork_id == self.id)
            & (Entry.summarywork_type == 'articlesummarywork')).first()  # NOQA: W503

    def download(self):
        self.full_text = download_file(self.entry.enclosures[0].url,
                                       return_data=True)
        self.save()

    @property
    def reports(self):
        return (Report.select().join(Reportable).where(
            (Report.reportables.reportable_id == self.id)
            & (Report.reportables.reportable_type == 'articlesummarywork')))  # NOQA: W503


class Reportable(BaseModel):
    report = ForeignKeyField(Report, backref="reportables")
    reportable_id = CharField(max_length=64)
    reportable_type = CharField(max_length=32)


class Entry(BaseModel):
    # Related feed
    feed = ForeignKeyField(Feed, backref='entries', on_delete='CASCADE')

    # the unique summarywork for this entry, may be audio, text, etc
    summarywork_id = CharField(max_length=64)
    summarywork_type = CharField(max_length=32)

    @property
    def summarywork(self):
        match self.summarywork_type:
            case 'audiosummarywork':
                return AudioSummaryWork.get_by_id(self.summarywork_id)
            case 'articlesummarywork':
                return ArticleSummaryWork.get_by_id(self.summarywork_id)
            case _:
                return None

    def is_downloaded(self):
        match self.summarywork_type:
            case 'audiosummarywork':
                return self.summarywork.audio_path is not None
            case 'articlesummarywork':
                return self.summarywork.full_text is not None
            case _:
                return False

    def download(self):
        if not self.is_downloaded():
            self.summarywork.download()

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
    entry = ForeignKeyField(Entry,
                            backref='author_details', on_delete='CASCADE')

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
    entry = ForeignKeyField(Entry,
                            backref='media_contents', on_delete='CASCADE')

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
    return hashlib.sha256((guid + "BIAS").encode('utf-8')).hexdigest()


def insert_feed(feed_data):
    # error if none of these values exist to be hashed
    feed_id = hash_guid(feed_data.get("id",
                                      feed_data.get("link",
                                                    feed_data["title"])))

    feed, _ = Feed.get_or_create(
        id=feed_id,
        defaults={
            'title': feed_data.get('title'),
            'link': feed_data.get('link'),
            'description': feed_data.get('description'),
            'language': feed_data.get('language'),
            'updated': feed_data.get('updated'),
            'updated_parsed': datetime.fromtimestamp(
                time.mktime(feed_data.get('updated_parsed'))),
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
    # error if none of these values exist to be hashed
    entry_id = hash_guid(entry_data.get("id",
                                        entry_data.get("link",
                                                       entry_data["title"])))

    entry, _ = Entry.get_or_create(
        id=entry_id,
        defaults={
            'feed': feed,
            'title': entry_data.get('title'),
            'link': entry_data.get('link'),
            'summary': entry_data.get('summary'),
            'published': entry_data.get('published'),
            'published_parsed': datetime.fromtimestamp(
                time.mktime(entry_data.get('published_parsed'))),
            'updated': entry_data.get('updated'),
            'updated_parsed': datetime.fromtimestamp(
                time.mktime(entry_data.get('updated_parsed'))),
            'author': entry_data.get('author'),
            'summarywork_id': 'INITIAL_ID',
            'summarywork_type': 'INITIAL_TYPE',
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
    got_one = False
    for enclosure in entry_data.get('enclosures', []):
        if not got_one and 'type' in enclosure:
            match enclosure.type:
                case t if t.startswith('audio/'):
                    entry.summarywork_type = 'audiosummarywork'
                    entry.summarywork_id = AudioSummaryWork.get_or_create(
                        id=entry.id,
                        defaults={
                            'audio_path': None,
                            'transcript': None,
                            'bullet_points': None,
                        }
                    )[0].id
                    entry.save()
                case t if t.startswith('text/'):
                    entry.summarywork_type = 'articlesummarywork'
                    entry.summarywork_id = ArticleSummaryWork.get_or_create(
                        id=entry.id,
                        defaults={
                            'full_text': None,
                            'bullet_points': None,
                        }
                    )[0].id
                    entry.save()
                case _:
                    entry.summarywork_type = 'INVALID_TYPE'
                    entry.summarywork_id = 'INVALID_ID'
            entry.save()
            got_one = True
        EntryEnclosure.get_or_create(
            entry=entry,
            url=enclosure.get('url'),
            length=(
                int(enclosure.get('length', 0))
                if enclosure.get('length')
                else None
            ),
            type=enclosure.get('type'),
        )

    return entry


def get_entry_by_id(entry_id):
    try:
        return Entry.get_by_id(entry_id)
    except Entry.DoesNotExist:
        return None


def insert_feed_list(feeds):
    feed_list, _ = FeedList.get_or_create(
        source=feeds
    )
    return feed_list


def get_feed_list_or_die(feeds):
    feed_list = FeedList.select().where(FeedList.source == feeds).first()
    if not feed_list:
        print(f'fatal: no such feed list "{feeds}" found in database')
        exit(1)
    return feed_list


def get_entries_in_range_by_source(after, before, source):
    feed_list = get_feed_list_or_die(source)

    result = []
    for feedlistfeed in feed_list.feeds:
        if (entries := feedlistfeed.feed.entries_in_range(after, before)):
            result += entries

    return result


def get_entries_in_range_by_feed_id(after, before, feed_id):
    if after is None:
        after = datetime.min
    if before is None:
        before = datetime.max
    result = []
    try:
        feed = Feed.get_by_id(feed_id)
        if (entries := feed.entries_in_range(after, before)):
            result += entries
    except Feed.DoesNotExist:
        pass
    return result


def get_last_updated_by_source(source):
    feed_list = get_feed_list_or_die(source)
    date = None

    for feedlistfeed in feed_list.feeds:
        if date is None or feedlistfeed.feed.updated_parsed < date:
            date = feedlistfeed.feed.updated_parsed

    return date.isoformat()


def get_source(source):
    feed_list = get_feed_list_or_die(source)
    return feed_list.source


def get_feeds_by_source(source):
    feed_list = get_feed_list_or_die(source)

    result = []
    for feedlistfeed in feed_list.feeds:
        result.append(feedlistfeed.feed)

    return result


def get_feed_by_id(feed_id):
    try:
        return Feed.get_by_id(feed_id)
    except Feed.DoesNotExist:
        return None


def get_latest_report(after, before, feeds):
    try:
        return (Report.select()
                .join(FeedList)
                .where(
                    (Report.after == after)
                    & (Report.before == before)  # NOQA: W503
                    & (FeedList.source == feeds))  # NOQA: W503
                .order_by(Report.timestamp.desc())
                .first())
    except Report.DoesNotExist:
        return None


def get_reports_by_source(source):
    try:
        return (Report.select()
                      .join(FeedList)
                      .where(FeedList.source == source)
                      .order_by(Report.timestamp.desc()))
    except Report.DoesNotExist:
        return []


def add_feed_list_feed(feed_list, feed):
    return FeedListFeed.get_or_create(feed_list=feed_list, feed=feed)


def feed_directory():
    return [f.source for f in FeedList.select()]


if __name__ == '__main__':
    DB.create_tables(BaseModel.__subclasses__())
