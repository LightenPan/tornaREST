# coding:utf-8

import os
import config

# from motorengine import connect

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from url import urls

import tornado.web


class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            handlers=urls,
            template_path=os.path.join(os.path.dirname(__file__), "template"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=True,
            allow_remote_access=True
        )
        tornado.web.Application.__init__(self, **settings)

        # 连接mongodb数据库
        # connect(config.DB_NAME, host=config.DB_HOST, port=config.DB_PORT, io_loop=io_loop,
        #         username=config.DB_USER, password=config.DB_PWD)

        # 连接mysql数据库
        engine = create_engine('mysql://%s:%s@%s/%s?charset=utf8' %
                      (config.MYSQL_USER, config.MYSQL_PWD, config.MYSQL_HOST, config.MYSQL_NAME),
                      encoding='utf-8', echo=False, pool_size=100, pool_recycle=10)
        self.db = scoped_session(sessionmaker(bind=engine,
                                              autocommit=False, autoflush=True,
                                              expire_on_commit=False))


app = Application()
