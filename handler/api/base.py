# coding:utf-8
import uuid

from bson import ObjectId
import traceback
from tornado.web import RequestHandler, HTTPError, os
import config
from handler.api import errors
from util.token import token_manager
from qiniu import Auth, put_data
from util.crypt import md5_data

from util import jsonhelper

# 初始化日志
import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('main')


class BaseHandler(RequestHandler):
    def data_received(self, chunk):
        pass

    def __init__(self, application, request, **kwargs):
        # 赋值流水号，可以用来打印日志
        self.object_id = uuid.uuid4()

        RequestHandler.__init__(self, application, request, **kwargs)
        self.set_header('Content-Type', 'text/json')

        if self.settings['allow_remote_access']:
            self.access_control_allow()

    def access_control_allow(self):
        # 允许 JS 跨域调用
        self.set_header("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Depth, User-Agent, X-File-Size, "
                                                        "X-Requested-With, X-Requested-By, If-Modified-Since, "
                                                        "X-File-Name, Cache-Control, Token")
        self.set_header('Access-Control-Allow-Origin', '*')

    def get(self, *args, **kwargs):
        raise HTTPError(**errors.status_0)

    def post(self, *args, **kwargs):
        raise HTTPError(**errors.status_0)

    def put(self, *args, **kwargs):
        raise HTTPError(**errors.status_0)

    def delete(self, *args, **kwargs):
        raise HTTPError(**errors.status_0)

    def options(self, *args, **kwargs):
        if self.settings['allow_remote_access']:
            self.write("")

    def write_error(self, status_code, **kwargs):
        self._status_code = 200

        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            # in debug mode, try to send a traceback
            lines = []
            for line in traceback.format_exception(*kwargs["exc_info"]):
                lines.append(line)

            self.write_json(dict(traceback=''.join(lines)), status_code, self._reason)

        else:
            self.write_json(None, status_code, self._reason)

    def write_json(self, data, status_code=200, msg='success.'):
        self.finish(jsonhelper.dumps({
            'code': status_code,
            'msg': msg,
            'data': data
        }))

    def is_logined(self):
        # 自己的账号登录
        if 'Token' in self.request.headers:
            token = self.request.headers['Token']
            logined, uid = token_manager.validate_token(token)

            if not logined:
                raise HTTPError(**errors.status_2)

            # 已经登陆
            return uid
        else:
            # 调用vask库解用户信息
            uin = self.get_cookie('pt2gguin', '')
            skey = self.get_cookie('skey', '')
            # logined = self.__ptlogin.verify(uin, skey, self.request.headers['REMOTE_ADDR'])
            logined = True

            if not logined:
                raise HTTPError(**errors.status_2)

            # 已经登陆
            return uin

    def upload_file_from_request(self, name, key):
        if name in self.request.files:
            fileinfo = self.request.files[name][0]
            fname = fileinfo['filename']
            body = fileinfo['body']

            extn = os.path.splitext(fname)[1]
            cname = md5_data(body) + extn

            q = Auth(config.QINIU_AK, config.QINIU_SK)
            key += cname
            token = q.upload_token(config.QINIU_BUCKET_NAME)
            ret, info = put_data(token, key, body)

            if info.status_code == 200:
                return config.QINIU_HOST + key
            else:
                # 上传失败
                raise HTTPError(**errors.status_24)

        # 找不到上传文件
        raise HTTPError(**errors.status_25)

    def info(self, msg, *args, **kwargs):
        new_msg = '%s, objectid: %s' % (msg, self.object_id)
        logger.info(new_msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        new_msg = '[%s]%s' % (self.object_id, msg)
        logger.debug(new_msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        new_msg = '[%s]%s' % (self.object_id, msg)
        logger.warning(new_msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        new_msg = '[%s]%s' % (self.object_id, msg)
        logger.error(new_msg, *args, **kwargs)

    @staticmethod
    def vaildate_id(_id):
        if _id is None or not ObjectId.is_valid(_id):
            raise HTTPError(**errors.status_3)

    @staticmethod
    def check_none(resource):
        if resource is None:
            raise HTTPError(**errors.status_22)


class APINotFoundHandler(BaseHandler):
    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        raise HTTPError(**errors.status_1)

    def post(self, *args, **kwargs):
        raise HTTPError(**errors.status_1)

    def put(self, *args, **kwargs):
        raise HTTPError(**errors.status_1)

    def delete(self, *args, **kwargs):
        raise HTTPError(**errors.status_1)

    def options(self, *args, **kwargs):
        if self.settings['allow_remote_access']:
            self.write("")


class DbHandler(BaseHandler):
    @property
    def db(self):
        return self.application.db

    def parse_params(self):
        # 检查登录态
        uid = self.is_logined()

        # 解请求包
        try:
            query = jsonhelper.loads(self.get_argument('p', ''))
        except:
            raise HTTPError(**errors.status_26)

        return uid, query
