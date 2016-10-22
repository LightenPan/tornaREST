# coding:utf-8
import json
import uuid

from tornado.web import HTTPError

from handler.api import errors
from handler.api.base import DbHandler
from data.mysqldb import Gallery


class GalleryListHandler(DbHandler):
    def get(self):
        uid, params = self.parse_params()
        offset = params['offset'] if 'offset' in params else 0
        count = params['count'] if 'count' in params else 100

        self.info('GalleryListHandler get log params. uid: %s, params: %s', uid, str(params))

        gallery_list = []
        data = self.db.query(Gallery).all()[offset:count]
        for item in data:
            gallery_list.append(item.to_dict())
        self.write_json(gallery_list)


class GalleryHandler(DbHandler):
    def get(self):
        uid, params = self.parse_params()
        video_id = params['video_id'] if 'video_id' in params else ''

        self.info('GalleryHandler get log params. uid: %s, params: %s', uid, str(params))

        if len(video_id) == 0:
            raise HTTPError(**errors.status_20000)

        gallery = self.db.query(Gallery).filter(Gallery.video_id == video_id).one()
        self.info('GalleryHandler log data. data: %s', str(gallery.to_dict()))
        self.write_json(gallery.to_dict())

    def post(self):
        uid, params = self.parse_params()
        video_id = params['video_id'] if 'video_id' in params else ''

        self.info('GalleryHandler get log params. uid: %s, params: %s', uid, str(params))

        # 检查post数据是否合法
        if len(video_id) == 0:
            raise HTTPError(**errors.status_20000)

        # 插入或者更新数据
        rows = self.db.query(Gallery).filter(Gallery.video_id == video_id).one()
        if len(rows) == 0:
            new_gallery = Gallery.default_create(
                game_id=params['game_id'],
                source=params['source'],
                title=params['title'],
                ext_image_url=params['ext_image_url'],
                summary=params['summary'],
                author=params['author'],
                ext_author_image_url=params['ext_author_image_url'],
                time_span=params['time_span'],
                publication_date=params['publication_date'],
                video_url=params['video_url'],
                third_id=params['third_id'],
                insert_user=uid,
            )
            self.db.add(new_gallery)
        else:
            rows.update(params)
        self.db.commit()

        # 返回成功
        self.write_json()
