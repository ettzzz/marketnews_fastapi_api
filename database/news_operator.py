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
    def __init__(self, mongo_uri=MONGO_URI, db_name=DB_NAME):
        super().__init__(mongo_uri, db_name)
        self.chunk_size = 500
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

    def get_latest_news_id(self, source, conn=None):
        if conn is None:
            conn = self.on()
        table_name = source
        if not self.has_table(table_name):
            return self.init_news_id[source]
        else:
            col = conn[table_name]
            res = col.find_one(sort=[("_id", -1)])
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
        for i in range(len(fetched)//self.chunk_size):
            col.insert_many(fetched[i*self.chunk_size:(i+1)*self.chunk_size])  
            ## happily all fetched is formatted by scrapper class
            time.sleep(0.5)
        return
