# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from tutorial import settings
from tutorial.items import ArtistCategoryItem,ArtistItem,AlbumItem,SongItem,CommentItem
from scrapy.exceptions import DropItem

class MongoPipeline(object):
    def __init__(self,):
        self.mongo_uri = '127.0.0.1'
        self.mongo_db = 'music_spider'

    def open_spider(self, spider):
        import pymongo
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, ArtistCategoryItem):
            if self.db['artist_category'].find({'id':item['id']}).count() == 0:
                self.db['artist_category'].insert(dict(item))
                return item
            else:
                raise DropItem(u'重复')
        elif isinstance(item,ArtistItem):
            if self.db['artist'].find({'id':item['id']}).count() == 0:
                self.db['artist'].insert(dict(item))
                return item
            else:
                raise DropItem(u'重复')
        elif isinstance(item,AlbumItem):
            if self.db['album'].find({'id':item['id']}).count() == 0:
                self.db['album'].insert(dict(item))
                return item
            else:
                raise DropItem(u'重复')
        elif isinstance(item,SongItem):
            if self.db['song'].find({'id':item['id']}).count() == 0:
                self.db['song'].insert(dict(item))
                return item
            else:
                raise DropItem(u'重复')
        elif isinstance(item, CommentItem):
            self.db['comment'].insert(dict(item))
        else:
            song_id = int(item['song_id'])
            song_item = self.db.song.find_one({'id':song_id})
            self.db.song.update_one({
                '_id': song_item['_id']
            }, {
                '$set': {
                    'total': item['total']
                }
            }, upsert=False)