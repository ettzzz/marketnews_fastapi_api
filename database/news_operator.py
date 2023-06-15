#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  6 19:36:05 2022

@author: ert
"""

import time

from database.base_mongo import BaseMongoOperator

from config.static_vars import DAY_ZERO, MONGO_URI, DB_NAME
from utils.datetime_tools import reverse_timestamper, DATE_FORMAT


class newsDatabaseOperator(BaseMongoOperator):
    def __init__(self, mongo_uri=MONGO_URI, db_name=DB_NAME, safety_first=True):
        super().__init__(mongo_uri, db_name)
        self.safety_first = safety_first
        self.chunk_size = 400
        self.init_table_names = {
            "feature": "news_weight",
        }

        self.news_fields = {
            "feature": {
                "date": [],
                "time": [],
                "weights": [],
                "sequence": [],
            },
            "daily_news": {
                "fid": [int, 0],
                "source": [],
                "content": [],
                "timestamp": [int, 0],
                "tag": [],
                "code": [],
                "industry": [],
                "info": [],
                "comment": [],
            },
        }

        self.init_news_id = {"ycj": 12253007}  ## from 2019-01-01

    def chunk_yielder(self, data):
        chunk = list()
        for i, d in enumerate(data):
            if i % self.chunk_size == 0 and i > 0:
                yield chunk
                del chunk [:]
            chunk.append(d)
        yield chunk
        

    def _safe_insert(self, data, col, retry=0):
        if retry >= 3:
            return
        try:
            col.insert_many(data)
            time.sleep(1)
            return
        except:
            time.sleep(1)
            return self._safe_insert(data, col, retry+1)

    def get_latest_news_id(self, source, key="_id", conn=None):
        if conn is None:
            conn = self.on()
        table_name = source
        if not self.has_table(table_name):
            return self.init_news_id[source]
        else:
            col = conn[table_name]
            res = col.find_one(sort=[(key, -1)])
            if res is None:  ## when collection is empty:
                return self.init_news_id[source]
            else:
                return res["fid"]

    def get_latest_news_date(self, source, conn=None):
        if conn is None:
            conn = self.on()
        table_name = source
        if not self.has_table(table_name):
            date = DAY_ZERO
        else:
            col = conn[table_name]
            res = col.find_one(sort=[("_id", -1)])
            date = reverse_timestamper(res["timestamp"], _format=DATE_FORMAT)
        return date

    def insert_news_data(self, fetched, source, conn):
        if not fetched:
            return
        table_name = source
        col = conn[table_name]

        if self.safety_first == True:
            chunks = self.chunk_yielder(fetched)
            for data_chunk in chunks:
                self._safe_insert(data_chunk, col)
        else:
            col.insert_many(fetched)
        return
