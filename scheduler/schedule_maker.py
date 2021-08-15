# -*- coding: utf-8 -*-
"""
Created on Thu Aug 12 20:56:12 2021

@author: ert
"""

import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler

from database.news_operator import newsDatabaseOperator
from scraper.sina import sinaScrapper

from utils.datetime_tools import reverse_timestamper

his_operator = newsDatabaseOperator()
ss = sinaScrapper()

news_fields = list(his_operator.news_fields['daily_news'].keys())
scheduler = BackgroundScheduler()



def live_sina_news():
    source = 'sina'
    max_id = his_operator.get_latest_news_id(source=source)
    params = ss.get_params(_type=0)
    news = ss.get_news(params)
    
    df = pd.DataFrame(news['list'][::-1]) # reverse sequence for sina
    df = df[(df['fid'] > max_id)]
    
    if len(df) == 0:
        return
    
    df['year'] = df['timestamp'].apply(lambda row: reverse_timestamper(row)[:4])
    for year, _count in df['year'].value_counts().items():
        fetched = df[news_fields][(df['year'] == year)].to_numpy()
        his_operator.insert_news_data(fetched, year, source)

    '''
    ## TODO:
    # weights = some_func_apply_to_df(df)
    # his_operator.insert_weight_data()
    '''

scheduler.add_job(func=live_sina_news, trigger='cron', minute='*/5')

        





