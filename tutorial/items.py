# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TutorialItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class ComicInfoItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    author = scrapy.Field()
    hits = scrapy.Field()
    category = scrapy.Field()
    state = scrapy.Field()
    cover = scrapy.Field()
    brief = scrapy.Field()

class ComicContentItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    provisionid = scrapy.Field()
    content = scrapy.Field()

class ArtistCategoryItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()

class ArtistItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    category_id = scrapy.Field()
    cover = scrapy.Field()

class AlbumItem(scrapy.Item):
    id = scrapy.Field()
    alb_name = scrapy.Field()
    alb_desc = scrapy.Field()
    alb_cover = scrapy.Field()
    alb_size = scrapy.Field()
    artist_id = scrapy.Field()
    release_time = scrapy.Field()
    release_comp = scrapy.Field()

class SongItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    duration = scrapy.Field()
    artist_id = scrapy.Field()
    album_id = scrapy.Field()
    comment_count = scrapy.Field()

class CommentItem(scrapy.Item):
    song_id = scrapy.Field()
    content = scrapy.Field()
    liked_count = scrapy.Field()
    timestamp = scrapy.Field()
    user_id = scrapy.Field()
    nickname = scrapy.Field()

class SongCommentCountItem():
    song_id = scrapy.Field()
    total = scrapy.Field()