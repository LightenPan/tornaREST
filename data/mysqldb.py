# coding:utf-8
import datetime
import uuid

from datetime import date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, VARCHAR, ForeignKey, Float, DateTime
from sqlalchemy import inspect

from util.jsonhelper import dumps

Base = declarative_base()  # create Base leifrom sqlalchemy import inspect


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


class Gallery(Base):
    __tablename__ = 'tgp_video_gallery'
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer)  # 游戏
    source = Column(Integer, nullable=False)  # 来源
    crawl_url = Column(VARCHAR(255), nullable=True)  # 爬虫url

    title = Column(VARCHAR(80), nullable=False)  # 标题
    image_url = Column(VARCHAR(255), nullable=True)  # 标题图片
    ext_image_url = Column(VARCHAR(255), nullable=False)  # 外部导入的标题图片
    summary = Column(VARCHAR(255), nullable=True)  # 摘要
    author = Column(VARCHAR(30), nullable=True)  # 作者
    author_image_url = Column(VARCHAR(100), nullable=True)  # 作者头像图片
    ext_author_image_url = Column(VARCHAR(255), nullable=True)  # 外部导入的作者头像图片
    time_span = Column(Integer, nullable=True)  # 时长
    publish_state = Column(Integer, nullable=True)  # 是否发布，2发布，1未发布
    publication_date = Column(DateTime, nullable=False)  # 对外发表日期
    video_id = Column(VARCHAR(50), nullable=True)  # 视频id
    video_url = Column(VARCHAR(512), nullable=True)  # 视频播放地址
    third_id = Column(VARCHAR(50), nullable=True)  # 来源id
    auto_pub_date = Column(DateTime, nullable=True)  # 自动发布时间
    # channels = models.ManyToManyField(Channel, blank=True, through='GalleryChannelRefer')
    channels_desc = Column(VARCHAR(255), nullable=True)  # 所属频道描述
    # tags = models.ManyToManyField(Channel, blank=True, through='GalleryTagRefer')

    insert_date = Column(DateTime, nullable=True)  # 创建时间
    last_modify_date = Column(DateTime, nullable=True)  # 最后修改时间
    insert_user = Column(VARCHAR(30), nullable=False)  # 编辑
    status = Column(Integer, nullable=True)  # 内部状态

    backup1 = Column(VARCHAR(255), nullable=True)  # 爬虫流水号
    backup2 = Column(VARCHAR(255), nullable=True)  # 移动端播放地址
    backup3 = Column(VARCHAR(255), nullable=True)  # 备用字段3

    def to_dict(self):
        return dict([(k, getattr(self, k)) for k in self.__dict__.keys() if not k.startswith("_")])

    @staticmethod
    def default_create(game_id, source,
                       title, ext_image_url, summary,
                       author, ext_author_image_url,
                       time_span, publication_date,
                       video_url, third_id,
                       insert_user):
        now = datetime.datetime.now()
        return Gallery(
            game_id=game_id,
            source=source,
            title=title,
            ext_image_url=ext_image_url,
            summary=summary,
            author=author,
            ext_author_image_url=ext_author_image_url,
            time_span=time_span,
            publish_state=1,
            publication_date=publication_date,
            video_id=uuid.uuid4(),
            video_url=video_url,
            third_id=third_id,
            insert_date=now,
            last_modify_date=now,
            status=0,
            insert_user=insert_user
        )
