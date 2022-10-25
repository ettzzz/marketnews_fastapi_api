#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  6 19:36:05 2022

@author: ert
"""


from database.base_mongo import BaseMongoOperator

from config.static_vars import DAY_ZERO, MONGO_URI, DB_NAME
from utils.datetime_tools import reverse_timestamper, DATE_FORMAT


class newsDatabaseOperator(BaseMongoOperator):
    def __init__(self, mongo_uri=MONGO_URI, db_name=DB_NAME):
        super().__init__(mongo_uri, db_name)
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

    def get_latest_news_id(self, source, conn=None):
        if conn is None:
            conn = self.on()
        table_name = source
        if not self.has_table(table_name):
            return -1
        else:
            col = conn[table_name]
            res = col.find_one(sort=[("_id", -1)])
            if res is None:  ## when collection is empty:
                return -1
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
        col.insert_many(fetched)  ## happily all fetched is formatted by scrapper class
        return
