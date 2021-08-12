#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  1 17:24:58 2018

@author: eriti
"""
# https://redis-py.readthedocs.io/en/latest/ # Official documentation

from functools import wraps

import redis

from config.static_vars import REDIS_CONFIG, INIT_POOL_CODES
from utils.common_tools import db_friendly_code


def pipeline_wrapper(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        conn = redis.StrictRedis(**REDIS_CONFIG)
        pipe = conn.pipeline(transaction=True)
        results = func(self, *args, **kwargs)
        pipe.execute()
        return results
    return wrapper


class redisWatcher():
    def __init__(self, connection_config=REDIS_CONFIG):
        self.conn = redis.StrictRedis(**connection_config)
        self.own = 'own'
        self.stop_loss = 'stop_loss'
        self.loss_day_limit = 5

    @pipeline_wrapper
    def flush_with_caution(self):
        self.conn.flushall()  # or flusahdb() but not tested yet

    @pipeline_wrapper
    def init_pool(self, pool=[]):
        if len(pool) == 0:
            pool = INIT_POOL_CODES
        self.conn.sadd(self.own, *pool)

    @pipeline_wrapper
    def get_pool(self):
        return self.conn.smembers(self.own)

    @pipeline_wrapper
    def update_pool(self, codes):
        pool = self.get_pool()
        codes_set = set(codes)
        to_add = codes_set - pool
        to_swipe = pool - codes_set

        self.conn.sadd(self.own, *to_add)
        self.conn.srem(self.own, *to_swipe)
        return list(to_add), list(to_swipe)

    @pipeline_wrapper
    def minus_pool(self, codes):
        self.conn.srem(self.own, *codes)

    @pipeline_wrapper
    def add_records(self, records):
        for code, record in records.items():
            self.conn.lpush(db_friendly_code(code), record)

    @pipeline_wrapper
    def get_bad_pool(self):
        bad_pool = dict()
        stop_loss = self.conn.hgetall(self.stop_loss)
        for code, count in stop_loss.items():
            if int(count) >= self.loss_day_limit - 1:
                bad_pool[code] = count
        return bad_pool

    @pipeline_wrapper
    def add_bad_pool(self, codes):
        bad_pool = self.get_bad_pool()
        # is there a way to avoid this for loop?
        for code in codes:
            if code in bad_pool and bad_pool[code] >= self.loss_day_limit:
                continue
            else:
                self.conn.hincrby(self.stop_loss, code, 1)
            # code now is a value in key-value pair
            # so it's not necessary to db_friendly_name(code)

    @pipeline_wrapper
    def minus_bad_pool(self, codes):
        bad_pool = self.get_bad_pool()
        for code in codes:
            if code in bad_pool and bad_pool[code] > 0:
                self.conn.hincrby(self.stop_loss, code, -1)
