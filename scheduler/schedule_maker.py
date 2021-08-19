# -*- coding: utf-8 -*-
"""
Created on Thu Aug 12 20:56:12 2021

@author: ert
"""

import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler

from engine.brain import SCD
from database.news_operator import newsDatabaseOperator
from database.redis_watcher import redisWatcher
from scraper.sina import sinaScrapper
from scraper.yuncaijing import yuncaijingScrapper
from utils.datetime_tools import reverse_timestamper, get_today_date

scheduler = BackgroundScheduler()
watcher = redisWatcher()
ss = sinaScrapper()
ys = yuncaijingScrapper()
his_operator = newsDatabaseOperator()
insula = SCD()

news_fields = list(his_operator.news_fields['daily_news'].keys())


def live_sina_news():
    source = 'sina'
    max_id = his_operator.get_latest_news_id(source=source)
    params = ss.get_params(_type=0)
    news = ss.get_news(params)
    filtered_news = ss.get_filtered_news(news['list'])

    df = pd.DataFrame(filtered_news[::-1])  # reverse sequence for sina
    df = df[(df['fid'] > max_id)]
    if len(df) == 0:
        return

    df['score'] = df['content'].apply(lambda row: insula.get_news_sentiment(row))
    weights_dict = dict()
    for idx, row in df.iterrows():
        codes = row['code'].split(',')
        for pseudo_code in codes:
            if pseudo_code.startswith('s') and len(pseudo_code) == 8:
                real_code = pseudo_code[:2] + '.' + pseudo_code[2:]
                weights_dict[real_code] = row['score']

    watcher.update_code_weight(weights_dict)  # {'code': 'score'}
    # his_operator.insert_weight_data() # this mission could be done during night

    df['year'] = df['timestamp'].apply(lambda row: reverse_timestamper(row)[:4])
    for year, _count in df['year'].value_counts().items():
        fetched = df[news_fields][(df['year'] == year)].to_numpy()
        his_operator.insert_news_data(fetched, year, source)


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


def sync_weight_data():
    pass

for f in [live_sina_news, live_yuncaijing_news]:
    scheduler.add_job(func=f, trigger='cron', hour='7-22', minute='*/5')
    scheduler.add_job(func=f, trigger='cron', hour='0-6,23', minute='*/30')
    
