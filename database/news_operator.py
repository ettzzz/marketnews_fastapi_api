#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 11 13:39:11 2021

@author: eee
"""

import os

from .base_operator import sqliteBaseOperator
from config.static_vars import NEWS_HISTORY_PATH

'''
1.按日期来，还是得存一下原语料数据的
2.如果有多个来源的话 应该放在同一个表里
3.来一个总表，分date，timestamp，weight，训练时候主要读取这个，
两个column，一个是code的顺序，一个是500个数


实时的情绪池：在redis里，5分钟新闻爬下来->先分析一波，更新到redis里
新闻存在今天的表里，交易时段内每隔30分钟总表就读取一个redis生成一条新纪录
'''

def sql_friendly_mapper(whatever, token='-'):
    return whatever.replace(token, '_')



class newsDatabaseOperator(sqliteBaseOperator):
    def __init__(self, sql_dbfile_path = NEWS_HISTORY_PATH):

        self.init_table_names = {
            'feature': 'news_weight',
        }
        self.news_fields = {
            'feature': {
                'date': ['DATE'],
                'time': ['TIME'],
                'weights': ['TEXT'],
                'sequence': ['TEXT']
            },
            'daily_news': {
                'fid': ['INTEGER'],
                'source': ['TEXT'],
                'content': ['TEXT'],
                'time': ['TIME'],
                'code': ['TEXT'],
                'industry': ['TEXT'],
                'info': ['TEXT'],
                'comment': ['TEXT'],
            },
            
        }

        if not os.path.exists(sql_dbfile_path):
            super().__init__(sql_dbfile_path)
            conn = self.on()
            for table in self.init_table_names:
                conn.execute(
                    self.create_table_sql_command(
                        self.init_table_names[table],
                        self.news_fields[table])
                )
            self.off(conn)
        else:
            super().__init__(sql_dbfile_path)

    def purge_tables_with_caution(self, table_names=[]):
        table_names = list(self.init_table_names.values()) if not table_names else table_names
        for t in table_names:
            self.delete_table(t)

    
    # @sqlite3_pipeline_wrapper
    def insert_news_data(self, fetched, date_str):
        table_name = sql_friendly_mapper(date_str, token='-')
        fields = list(self.news_fields['daily_news'].keys())
        
        conn = self.on()
        conn.execute(
            self.create_table_sql_command(
                table_name,
                self.stock_fields['daily_news'])
            )
        conn.executemany(
            self.insert_batch_sql_command(table_name, fields), fetched
            )
        self.off(conn)
        
        
    def insert_weight_data(self):
        pass
    
        
    def get_feature_weights(self, start_date, end_date):
        feature_weights = self.fetch_by_command(
            "SELECT * FROM {} WHERE date BETWEEN '{}' AND '{}';".format(
                self.init_table_names['feature'],
                start_date,
                end_date
                )
            )
        return feature_weights

