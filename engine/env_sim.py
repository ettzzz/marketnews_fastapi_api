#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 20 16:40:16 2021

@author: eee
"""

'''
日期范围
初始化weights都是0 先用一个月/一星期的做启动吧 以后就得从2019-02-01开始了

每天先从sql读出来
分时段每个时段来一个计算一次weight_dict
储存一条
每天结束的时候decay一个


'''


from engine.brain import SCD
from config.static_vars import DAY_ZERO
from database.news_operator import newsDatabaseOperator
from utils.datetime_tools import get_delta_date, date_range_generator, timestamper
from utils.internet_tools import all_codes_receiver

insula = SCD()
his_operator = newsDatabaseOperator()


class simEnvironment():
    def __init__(self, code_list=None):
        self.init_weight(code_list)

    def init_weight(self, codes=None):
        if not codes:
            codes = all_codes_receiver()
        self.weights_dict = {k: 0 for k in codes}

    def read_weight(self, weights_dict):
        self.weights_dict = weights_dict

    def update_weight(self, fetched):
        for timestamp, content, codes_str in fetched:
            codes = codes_str.split(',')
            if len(codes) == 0:
                continue
            score = insula.get_news_sentiment(content)
            for pseudo_code in codes:
                if pseudo_code.startswith('6'):
                    real_code = 'sh.' + pseudo_code
                else:
                    real_code = 'sz.' + pseudo_code
                if real_code in self.weights_dict:
                    self.weights_dict[real_code] = score

    def decay_weight(self):
        self.weights_dict = {
            k: insula.weight_decay(v, 1) for k, v in self.weights_dict.items()
        }


if __name__ == "__main__":
    from config.static_vars import DAILY_TICKS
    
    source = 'ycj'
    all_codes = all_codes_receiver()
    sim_env = simEnvironment(code_list=all_codes)

    max_date = his_operator.get_latest_news_date(source=source)
    date_ranger = date_range_generator(DAY_ZERO, max_date)
    # TODO: how to get rid of weekends and holidays? dqn add an api for request_trading_days
    # pick up days were not trading, if date in these days, don't insert_weight_data
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
            else:
                sim_env.decay_weight()
