import scrapy
from bs4 import BeautifulSoup
import re,json,time
from tutorial.items import ArtistCategoryItem,ArtistItem,AlbumItem,SongItem,CommentItem,SongCommentCountItem


class MusicSpider(scrapy.Spider):
    name = "music"
    base_url = 'http://music.163.com'
    start_urls = [
        "http://music.163.com/discover/artist",
    ]
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url,self.parse)

    def parse(self, response):
        if response.status != 200:
            req = response.request
            req.meta["change_proxy"] = True
            yield req
        soup = BeautifulSoup(response.body, 'html.parser')
        for item in soup.find_all(class_='cat-flag'):
            href = item['href']
            catname = item.string
            match = re.match('.*id=(\d{4})$', href)
            if match:
                catid = match.group(1)
                item = ArtistCategoryItem()
                item['id'] = catid
                item['name'] = catname
                yield item

                for initial in [0] + range(ord('A'), ord('Z') + 1):
                    next = self.base_url + '/discover/artist/cat?id=%s&initial=%d' % (catid, initial)
                    print next
                    yield scrapy.Request(next, self.parse_artist_category)

    def parse_artist_category(self,response):
        if response.status != 200:
            req = response.request
            req.meta["change_proxy"] = True
            yield req
        soup = BeautifulSoup(response.body, 'html.parser')
        for item in soup.find_all('a'):
            match = re.match('/artist\?id=(\d+)$', item['href'])
            if match:
                artist_id = match.group(1)
                artist_name = item['title'][:-3]
                category_id = re.match('.*/cat\?id=(\d+).*', response.url).group(1)
                item = ArtistItem()
                item['id'] = artist_id
                item['name'] = artist_name
                item['category_id'] = category_id
                yield item

                next = self.base_url + '/artist/album?id=%s&limit=200' % artist_id
                yield scrapy.Request(next, self.parse_artist)

    def parse_artist(self,response):
        if response.status != 200:
            req = response.request
            req.meta["change_proxy"] = True
            yield req
        soup = BeautifulSoup(response.body, 'html.parser')
        for item in soup.find_all(id='m-song-module'):
            album_li_list = item.find_all('li')
            for li in album_li_list:
                # print li
                match = re.match('.*id=(\d+)$', li.find('a')['href'])
                if match:
                    alb_id = match.group(1)
                    next = self.base_url + '/album?id=%s' % alb_id
                    yield scrapy.Request(next, self.parse_album)

    def parse_album(self,response):
        if response.status != 200:
            req = response.request
            req.meta["change_proxy"] = True
            yield req
        soup = BeautifulSoup(response.body, 'html.parser')
        for item in soup.find_all('a', href=re.compile('\/song\?id=\d+')):
            song_href = item['href']
            match = re.match('.*id=(\d+)$', song_href)
            if match:
                song_id = match.group(1)
                next = 'http://music.163.com/api/song/detail/?id=%s&ids=[%s]' % (song_id, song_id)
                yield scrapy.Request(next, self.parse_song)

    def parse_song(self,response):
        if response.status != 200:
            req = response.request
            req.meta["change_proxy"] = True
            yield req
        try:
            song = json.loads(response.body)
        except:
            print 'parse json error'
        else:
            song_json = song['songs'][0]
            album_json = song_json['album']
            artist_json = song_json['artists'][0]

            song_id = song_json['id']
            song_name = song_json['name']
            song_duration = song_json['duration']
            artist_id = artist_json['id']
            album_id = album_json['id']
            album_name = album_json['name']
            album_size = album_json['size']
            album_cover = album_json['picUrl']
            release_time = album_json['publishTime']
            release_comp = album_json['company']

            itemsong = SongItem()
            itemsong['id'] = song_id
            itemsong['name'] = song_name
            itemsong['duration'] = song_duration
            itemsong['album_id'] = album_id
            itemsong['artist_id'] = artist_id
            yield itemsong

            itemalbum = AlbumItem()
            itemalbum['id'] = album_id
            itemalbum['alb_name'] = album_name
            itemalbum['alb_cover'] = album_cover
            itemalbum['alb_size'] = album_size
            itemalbum['artist_id'] = artist_id
            itemalbum['release_time'] = release_time
            itemalbum['release_comp'] = release_comp
            try:
                timestamp = str(release_time)
                itemalbum['release_time'] = time.strftime('%Y-%m-%d',
                                                   time.localtime(float(timestamp[:10] + '.' + timestamp[-3:])))
            except:
                print 'timestamp error:%s' % release_time
                itemalbum['release_time'] = ''
            yield itemalbum

            comment_thread = song_json['commentThreadId']
            next = 'http://music.163.com/weapi/v1/resource/comments/' + comment_thread

            from ..utils import get_encSecKey,get_params
            params = get_params(1)
            encSecKey = get_encSecKey()
            yield scrapy.FormRequest(url=next,formdata={"params": params,"encSecKey": encSecKey},callback=self.parse_comment)

    def parse_comment(self,response):
        if response.status != 200:
            req = response.request
            req.meta["change_proxy"] = True
            yield req
        url = response.url
        song_id = url[url.rfind('_')+1:]
        json_comment = json.loads(response.body)
        total = json_comment.get('total', 0)

        song_comment_count = SongCommentCountItem()
        song_comment_count['total'] = total
        song_comment_count['song_id'] = song_id
        yield song_comment_count

        hot_comments = json_comment['hotComments']
        for item in hot_comments:
            comment = CommentItem()
            comment['song_id'] = song_id

            try:
                highpoints = re.compile(u'[\U00010000-\U0010ffff]')
            except re.error:
                highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')

            content = highpoints.sub(u'??', item['content'])
            comment['content'] = content[:300]
            comment['liked_count'] = int(item['likedCount'])
            timestamp = str(item['time'])
            comment['timestamp'] = time.strftime('%Y%m%d%H%M%S',
                                              time.localtime(float(timestamp[:10] + '.' + timestamp[-3:])))
            comment_user = item.get('user')
            if comment_user:
                comment['user_id'] = int(comment_user.get('userId', 0))
                comment['nickname'] = comment_user.get('nickname')
            yield comment

