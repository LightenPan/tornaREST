# coding:utf-8

import redis
import config

redisdb = redis.Redis(
    connection_pool=
    redis.ConnectionPool(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        db=0
    )
)

