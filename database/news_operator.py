#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 11 13:39:11 2021

@author: eee
"""

import os

from .base_operator import sqliteBaseOperator
from config.static_vars import NEWS_HISTORY_PATH, DAY_ZERO
from utils.datetime_tools import get_today_date, timestamper, reverse_timestamper


'''
3.来一个总表，分date，timestamp，weight，训练时候主要读取这个，
两个column，一个是code的顺序，一个是500个数
'''


class newsDatabaseOperator(sqliteBaseOperator):
    def __init__(self, sql_dbfile_path=NEWS_HISTORY_PATH):

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
                # 'timestamp': ['INTEGER'], # again a fucking mistake
                'timestamp': ['TEXT'],
                'tag': ['TEXT'],
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

    def insert_news_data(self, fetched, year_str, source):
        table_name = '{}_{}'.format(source, year_str)
        fields = list(self.news_fields['daily_news'].keys())

        conn = self.on()
        if not self.table_info(table_name):
            conn.execute(
                self.create_table_sql_command(
                    table_name,
                    self.news_fields['daily_news'])
            )

        conn.executemany(
            self.insert_batch_sql_command(table_name, fields), fetched
        )
        self.off(conn)

    def insert_weight_data(self, weights_dict, date_time_str):
        date, _time = date_time_str.split(' ')
        fields = list(self.news_fields['feature'].keys())
        non_zero_dict = {k: v for k, v in weights_dict.items() if v != 0}

        fetched = [[
            date,
            _time,
            str(list(non_zero_dict.values())),
            str(list(non_zero_dict.keys()))
        ]]
        conn = self.on()
        conn.executemany(
            self.insert_batch_sql_command(
                self.init_table_names['feature'], fields
            ),
            fetched
        )
        self.off(conn)

    def get_feature_weights(self, start_date, end_date):
        fields = list(self.news_fields['feature'].keys())
        fetched = self.fetch_by_command(
            "SELECT {} FROM '{}' WHERE date BETWEEN '{}' AND '{}';".format(
                ','.join(fields),
                self.init_table_names['feature'],
                start_date,
                end_date
            )
        )

        results = list()
        for f in fetched:
            temp = dict(zip(fields, f))
            temp['weights_dict'] = dict(zip(eval(temp['sequence']), eval(temp['weights'])))
            results.append(temp)
        return results

    def get_code_weights(self, code, start_date, end_date):
        fields = list(self.news_fields['feature'].keys())
        fetched = self.fetch_by_command(
            "SELECT {} FROM '{}' WHERE date BETWEEN '{}' AND '{}';".format(
                ','.join(fields),
                self.init_table_names['feature'],
                start_date,
                end_date
            )
        )
        results = dict()
        for f in fetched:
            temp = dict(zip(fields, f))
            weights_dict = dict(zip(eval(temp['sequence']), eval(temp['weights'])))
            timestamp = '{} {}'.format(temp['date'], temp['time'])
            if code in weights_dict:
                results[timestamp] = weights_dict[code]
            else:
                results[timestamp] = 0
        return results


    def _get_news(self, source, date, start_timestamp=None, end_timestamp=None):
        year = date[:4]
        table_name = '{}_{}'.format(source, year)
        if not start_timestamp:
            start_timestamp = timestamper(date + ' ' + '00:00:00', '%Y-%m-%d %H:%M:%S')
        if not end_timestamp:
            end_timestamp = timestamper(date + ' ' + '23:59:59', '%Y-%m-%d %H:%M:%S')

        target_cols = ['timestamp', 'content', 'code']
        news = self.fetch_by_command(
            # "SELECT {} FROM '{}' WHERE code != '' AND timestamp BETWEEN {} AND {};".format(
            "SELECT {} FROM '{}' WHERE timestamp BETWEEN '{}' AND '{}';".format(
                ','.join(target_cols),
                table_name,
                start_timestamp,
                end_timestamp
            )
        )
        return news

    def get_latest_news_id(self, source='ycj'):
        today = get_today_date()
        table_name = '{}_{}'.format(source, today[:4])  # source + year
        if not self.table_info(table_name):
            table_name = '{}_{}'.format(source, str(int(today[:4]) - 1))

        # TODO: fetch all table whose name contains source

        latest_news_id = self.fetch_by_command(
            "SELECT MAX(fid) FROM '{}' WHERE source = '{}';".format(
                table_name,
                source
            )
        )
        return latest_news_id[0][0]  # it should be an int

    def get_latest_news_date(self, source='ycj'):
        today = get_today_date()
        table_name = '{}_{}'.format(source, today[:4])  # source + year
        if not self.table_info(table_name):
            table_name = '{}_{}'.format(source, str(int(today[:4]) - 1))

        try:
            latest_news_date = self.fetch_by_command(
                "SELECT MAX(timestamp) FROM '{}' WHERE source = '{}';".format(
                    table_name,
                    source
                )
            )
            date, _time = reverse_timestamper(latest_news_date[0][0]).split(' ')
        except Exception as e:
            print(e)
            date = DAY_ZERO

        return date

    def get_latest_weight_dict(self):
        latest_weight_query = self.fetch_by_command(
            "SELECT * FROM '{}' WHERE uid=(SELECT MAX(uid) FROM '{}');".format(
                self.init_table_names['feature'],
                self.init_table_names['feature'],
            )
        )
        uid, date, _time, v, k = latest_weight_query[0]
        latest_weight_dict = dict(zip(eval(k), eval(v)))
        return latest_weight_dict
