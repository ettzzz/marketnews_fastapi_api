# -*- coding: utf-8 -*-
"""
Created on Thu Aug 12 20:56:12 2021

@author: ert
"""
import time
import random

import pandas as pd
import numpy as np
from apscheduler.schedulers.background import BackgroundScheduler

from database.news_operator import newsDatabaseOperator
from database.redis_watcher import redisWatcher
from scraper.yuncaijing import yuncaijingScrapper
from utils.datetime_tools import (
    reverse_timestamper,
    get_today_date,
    get_now,
    date_range_generator,
    timestamper,
    get_delta_date
)
from config.static_vars import DAILY_TICKS
from engine.brain import SCD

scheduler = BackgroundScheduler()
watcher = redisWatcher()
ys = yuncaijingScrapper()
his_operator = newsDatabaseOperator()

insula = SCD()

news_fields = list(his_operator.news_fields['daily_news'].keys())
source = 'ycj'
ts_format = '%Y-%m-%d %H:%M:%S'
date_format = '%Y-%m-%d'

# def live_sina_news():
#     source = 'sina'
#     max_id = his_operator.get_latest_news_id(source=source)
#     params = ss.get_params(_type=0)
#     news = ss.get_news(params)
#     filtered_news = ss.get_filtered_news(news['list'])

#     df = pd.DataFrame(filtered_news[::-1])  # reverse sequence for sina
#     df = df[(df['fid'] > max_id)]
#     if len(df) == 0:
#         return

#     df['score'] = df['content'].apply(lambda row: insula.get_news_sentiment(row))
#     weights_dict = dict()
#     for idx, row in df.iterrows():
#         codes = row['code'].split(',')
#         for pseudo_code in codes:
#             if pseudo_code.startswith('s') and len(pseudo_code) == 8:
#                 real_code = pseudo_code[:2] + '.' + pseudo_code[2:]
#                 weights_dict[real_code] = row['score']

#     watcher.update_code_weight(weights_dict)  # {'code': 'score'}

#     df['year'] = df['timestamp'].apply(lambda row: reverse_timestamper(row)[:4])
#     for year, _count in df['year'].value_counts().items():
#         fetched = df[news_fields][(df['year'] == year)].to_numpy()
#         his_operator.insert_news_data(fetched, year, source)


def _split_code_score(df, weights_dict=None):
    # just for ycj
    if not weights_dict:
        weights_dict = dict()

    for idx, row in df.iterrows():
        codes = row['code']
        for pseudo_code in codes:
            if len(pseudo_code) < 6:
                continue  # not sure why there is a single stuff
            if pseudo_code.startswith('6'):
                real_code = 'sh.' + pseudo_code
            else:
                real_code = 'sz.' + pseudo_code
            weights_dict[real_code] = row['score']

    return weights_dict


def live_news():
    today = get_today_date()
    year = today[:4]

    max_id = his_operator.get_latest_news_id(source=source)
    params = ys.get_params(page=1, date=today)
    news = ys.get_news(params)
    filtered_news = ys.get_filtered_news(news)

    if len(filtered_news) == 0:
        return

    df = pd.DataFrame(filtered_news[::-1])
    df = df[(df['fid'] > max_id)]
    if len(df) == 0:
        return
    # update news raw data first, redis later
    fetched = df[news_fields].to_numpy()
    his_operator.insert_news_data(fetched, year, source)

    df = df.replace('', np.nan)
    df = df.dropna(subset=['code'])
    df['score'] = df['content'].apply(lambda row: insula.get_news_sentiment(row))

    weights_dict = watcher.get_code_weight()  # TODO: need to confirm whether we can use an empty dict
    weights_dict = _split_code_score(df, weights_dict)
    watcher.update_code_weight(weights_dict)


def update_news(is_history=True):
    today = get_today_date()
    max_id = his_operator.get_latest_news_id(source=source)
    weights_dict = his_operator.get_latest_weight_dict()

    if is_history:
        max_date = his_operator.get_latest_news_date(source=source)
        latest_date = get_delta_date(today, -1)
    else:
        max_date = today
        latest_date = today

    dates = date_range_generator(max_date, latest_date)
    for date in dates:
        year = date[:4]  # could be another year, ha
        page = 1
        news = []
        while True:
            ycj_params = ys.get_params(page, date)
            ycj_news = ys.get_news(ycj_params)
            print('updating', date, page, 'is_history', is_history)
            time.sleep(random.random() + random.randint(1, 2))
            if is_history and not ycj_news:
                break  # if it's history and ycj_news is an empty list
            if not is_history and reverse_timestamper(ycj_news[-1]['timestamp'], date_format) < date:
                break  # it it's for today and last news is yesterday
            if ycj_news[0]['fid'] <= max_id:
                break  # we already have this batch
            news += ycj_news
            page += 1
        print('updating done.')

        if len(news) == 0:
            continue

        df = pd.DataFrame(news[::-1])  # from morning till evening
        df = df[(df['fid'] > max_id)]  # make sure all news are new
        df = df.drop_duplicates(subset=['fid'], keep='first')  # drop duplicates of today's news
        if len(df) == 0:
            continue

        fetched = df[news_fields].to_numpy()
        his_operator.insert_news_data(fetched, year, source)  # add raw news data first

        df = df.replace('', np.nan)
        df = df.dropna(subset=['code'])
        df['score'] = df['content'].apply(lambda row: insula.get_news_sentiment(row))

        for i in range(len(DAILY_TICKS) - 1):  # then update news_weight table
            start_time = DAILY_TICKS[i]
            end_time = DAILY_TICKS[i+1]
            start = str(timestamper(date + ' ' + start_time, ts_format))
            end = str(timestamper(date + ' ' + end_time, ts_format))
            period_news = df[(df['timestamp'] >= start) & (df['timestamp'] < end)]
            print(start_time, end_time, len(period_news))
            if len(period_news) == 0:
                continue  # just make sure each time interval is valid

            weights_dict = _split_code_score(period_news, weights_dict)
            if end_time[-1] == '0':  # 23:59:59 is not included
                his_operator.insert_weight_data(
                    weights_dict,
                    date + ' ' + end_time
                )
            else:  # when end_time is '23:59:59', decay when every day's end
                weights_dict = {k: insula.weight_decay(v, 1) for k, v in weights_dict.items()}

    watcher.update_code_weight(weights_dict)  # finally update weight to redis watcher


def sync_weight():
    date_time_str = reverse_timestamper(get_now())[:-2] + '00'
    weights_dict = watcher.get_code_weight()
    his_operator.insert_weight_data(weights_dict, date_time_str)


'''
0:03
scrape news for yesterday and before + calculate news_weight + decay if necessary
4hours max ≈ 90 days of news

8:50
scrape news for today's dawn + calculate news_weight

9:00-15:00 scrape news every 5 minutes + calculate news_weight
'''

scheduler.add_job(func=update_news, kwargs={'is_history': True}, trigger='cron',
                  hour=2, minute=1, day_of_week='mon-fri')  # for yesterday and before
# for today's dawn TODO not sure yet
scheduler.add_job(func=update_news, kwargs={'is_history': False}, trigger='cron',
                  hour=8, minute=50, day_of_week='mon-fri')
scheduler.add_job(func=live_news, trigger='cron',
                  hour='9-14', minute='*/5', day_of_week='mon-fri')
scheduler.add_job(func=live_news, trigger='cron',
                  hour=15, minute=0, day_of_week='mon-fri')
# AHAHAHAH watch out for news later than 15:00

scheduler.add_job(func=sync_weight, trigger='cron',
                  hour='10,13,14', minute='*/30', day_of_week='mon-fri')
scheduler.add_job(func=sync_weight, trigger='cron',
                  hour='9,11', minute='30', day_of_week='mon-fri')
scheduler.add_job(func=sync_weight, trigger='cron',
                  hour='15', minute='0', day_of_week='mon-fri')

scheduler.start()
