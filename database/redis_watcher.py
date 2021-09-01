#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  1 17:24:58 2018

@author: eriti
"""
# https://redis-py.readthedocs.io/en/latest/ # Official documentation

from functools import wraps

import redis

from config.static_vars import SENTI_REDIS_CONFIG


def pipeline_wrapper(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        conn = redis.StrictRedis(**SENTI_REDIS_CONFIG)
        pipe = conn.pipeline(transaction=True)
        results = func(self, *args, **kwargs)
        pipe.execute()
        return results
    return wrapper


class redisWatcher():
    def __init__(self, connection_config=SENTI_REDIS_CONFIG):
        self.conn = redis.StrictRedis(**connection_config)
        self.code_weight = 'code_sentiment'  # single code
        self.field_weight = 'field_sentiment'  # field

    def _non_zero_mapping(self, raw_dict):
        return {k: float(v) for k, v in raw_dict.items() if float(v) != 0}

    @pipeline_wrapper
    def flush_with_caution(self):
        self.conn.flushdb()

    @pipeline_wrapper
    def reset_all_weight(self):
        self.conn.delete(self.code_weight)
        # self.conn.delete(self.field_weight)

    @pipeline_wrapper
    def get_code_weight(self):
        redis_results = self.conn.hgetall(self.code_weight)
        results = self._non_zero_mapping(redis_results)
        return results

    # @pipeline_wrapper
    # def get_field_weight(self):
    #     results = self.conn.hgetall(self.field_weight)
    #     return results

    @pipeline_wrapper
    def update_code_weight(self, weights_dict):
        non_zeros = self._non_zero_mapping(weights_dict)
        self.reset_all_weight()  # it seems redis cannot overwrite an existing key
        self.conn.hset(self.code_weight, mapping=non_zeros)

    # @pipeline_wrapper
    # def update_field_weight(self, weights_dict):
    #     self.conn.hmset(self.field_weight, mapping=weights_dict)
