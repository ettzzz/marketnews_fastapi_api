# -*- coding: utf-8 -*-
"""
Created on Thu Aug 12 20:56:12 2021

@author: ert
"""
import time
import random

import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler

from engine.brain import SCD
from database.news_operator import newsDatabaseOperator
from database.redis_watcher import redisWatcher
# from scraper.sina import sinaScrapper
from engine.env_sim import simEnvironment
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

scheduler = BackgroundScheduler()
watcher = redisWatcher()
# ss = sinaScrapper()
ys = yuncaijingScrapper()
his_operator = newsDatabaseOperator()
insula = SCD()

news_fields = list(his_operator.news_fields['daily_news'].keys())


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


def live_yuncaijing_news():
    source = 'ycj'
    max_id = his_operator.get_latest_news_id(source=source)
    today = get_today_date()
    params = ys.get_params(page=1, date=today)
    news = ys.get_news(params)
    filtered_news = ys.get_filtered_news(news)

    df = pd.DataFrame(filtered_news[::-1])
    df = df[(df['fid'] > max_id)]
    if len(df) == 0:
        return

    df['score'] = df['content'].apply(lambda row: insula.get_news_sentiment(row))
    weights_dict = dict()
    for idx, row in df.iterrows():
        codes = row['code']
        for pseudo_code in codes:
            if pseudo_code.startswith('6'):
                real_code = 'sh.' + pseudo_code
            else:
                real_code = 'sz.' + pseudo_code
            weights_dict[real_code] = row['score']

    watcher.update_code_weight(weights_dict)

    fetched = df[news_fields].to_numpy()
    year = today[:4]
    his_operator.insert_news_data(fetched, year, source)


def update_yuncaijing_news(is_history=True):
    source = 'ycj'
    max_id = his_operator.get_latest_news_id(source=source)
    max_date = his_operator.get_latest_news_date(source=source)
    today = get_today_date()
    if is_history:
        latest_date = get_delta_date(today, -1)  # yesterday
    else:
        latest_date = today
    dates = date_range_generator(max_date, latest_date)
    ''''''
    weights_dict = his_operator.get_latest_weight_dict()
    for date in dates:
        print('updating yuncaijing', date)
        year = date[:4]
        page = 1
        news = []
        while True:
            ycj_params = ys.get_params(page, date)
            ycj_news = ys.get_news(ycj_params)
            if not ycj_news:
                break
            news += ycj_news
            page += 1
            time.sleep(random.random() + random.randint(1, 2))

        news = list(set(news))  # just in case of redundancy when dealing with today's news
        df = pd.DataFrame(news[::-1])  # reverse sequence for yuncaijing
        df = df[(df['fid'] > max_id)]
        if len(df) == 0:
            continue

        fetched = df[news_fields].to_numpy()
        his_operator.insert_news_data(fetched, year, source)

        df['score'] = df['content'].apply(lambda row: insula.get_news_sentiment(row))

        for i in range(len(DAILY_TICKS) - 1):
            start_time = DAILY_TICKS[i]
            end_time = DAILY_TICKS[i+1]
            start = timestamper(date + ' ' + start_time, '%Y-%m-%d %H:%M:%S')
            end = timestamper(date + ' ' + end_time, '%Y-%m-%d %H:%M:%S')
            news = df[(df['timestamp'] >= start) & (df['timestamp'] < end)]
            for idx, row in news.iterrows():
                codes = row['code'].split(',')
                for pseudo_code in codes:
                    if pseudo_code.startswith('6'):
                        real_code = 'sh.' + pseudo_code
                    else:
                        real_code = 'sz.' + pseudo_code
                    if real_code in weights_dict:
                        weights_dict[real_code] = row['score']

            if end_time[-1] == '0':
                his_operator.insert_weight_data(
                    weights_dict,
                    date + ' ' + end_time
                )

        weights_dict = {
            k: insula.weight_decay(v, 1) for k, v in weights_dict.items()
        }

    # watcher.update_code_weight(weights_dict)


def update_news_weight():
    source = 'ycj'  # !! this is not optimized way to get max_date
    # max_date = his_operator.get_latest_news_date(source=source)

    sim_env = simEnvironment()
    # TODO: sim_env.read_weight = his_operator.get_latest_weight?
    yesterday = get_delta_date(get_today_date(), -1)
    date_ranger = date_range_generator(max_date, yesterday)

    for date in date_ranger:
        print('generating', date)
        for i in range(len(DAILY_TICKS) - 1):
            start_time = DAILY_TICKS[i]
            end_time = DAILY_TICKS[i+1]
            start = timestamper(date + ' ' + start_time, '%Y-%m-%d %H:%M:%S')
            end = timestamper(date + ' ' + end_time, '%Y-%m-%d %H:%M:%S')
            news = his_operator._get_news(source, date, start, end)
            sim_env.update_weight(news)
            if end_time[-1] == '0':
                his_operator.insert_weight_data(
                    sim_env.weights_dict,
                    date + ' ' + end_time
                )
        sim_env.decay_weight()


def sync_weight_data():
    date_time_str = reverse_timestamper(get_now())[:-2] + '00'
    weights_dict = watcher.get_code_weight()
    his_operator.insert_weight_data(weights_dict, date_time_str)


def decay_weight_data():
    weights_dict = watcher.get_code_weight()
    decayed_weights_dict = {
        k: insula.weight_decay(v, 1) for k, v in weights_dict.items()
    }
    watcher.update_code_weight(decayed_weights_dict)


'''
0:01
scrape news for yesterday and before + calculate news_weight + decay if necessary
4hours max

8:00
scrape news for today's dawn + calculate news_weight

9:00-15:00 scrape news every 5 minutes + calculate news_weight
'''


# scheduler.add_job(func=update_yuncaijing_news, trigger='date')  # whenever run code
scheduler.add_job(func=live_yuncaijing_news, trigger='cron', hour='9-15', minute='*/5')
# scheduler.add_job(func=live_yuncaijing_news, trigger='cron', hour='0-6,23', minute='*/30')

scheduler.add_job(func=sync_weight_data, trigger='cron', hour='10,13,14', minute='*/30')
scheduler.add_job(func=sync_weight_data, trigger='cron', hour='9,11', minute='30')
scheduler.add_job(func=sync_weight_data, trigger='cron', hour='15', minute='0')

# scheduler.add_job(func=decay_weight_data, tirgger='cron', hour=23, minute=55)
