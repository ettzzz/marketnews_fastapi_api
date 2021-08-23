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
        # self.warmup_days = warmup_days
        # self.source = source
        # self.start_date = get_delta_date(DAY_ZERO, self.warmup_days + 1)
        # self.warmup_dates = date_range_generator(
        #     start=DAY_ZERO,
        #     end=get_delta_date(DAY_ZERO, self.warmup_days)
        # )
        self.init_weight(code_list)

    def warmup_weight(self):
        print('warming up for {} days!'.format(self.warmup_days))
        for date in self.warmup_dates:
            print('warming_up', date)
            historical_news = his_operator._get_news(self.source, date)
            self.update_weight(historical_news)

    def init_weight(self, codes=None):
        if not codes:
            codes = all_codes_receiver()
        self.weights_dict = {k: 0 for k in codes}

    def read_weight(self, weights_dict):
        self.weights_dict = weights_dict

    def update_weight(self, fetched):
        for timestamp, content, codes_str in fetched:
            codes = codes_str.split(',')
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
    sim_env = simEnvironment()

    ##### warmup #####
    warmup_days = 10
    start_date = get_delta_date(DAY_ZERO, warmup_days + 1)
    warmup_dates = date_range_generator(
        start=DAY_ZERO,
        end=get_delta_date(DAY_ZERO, warmup_days)
    )
    print('warming up for {} days!'.format(warmup_days))
    for date in warmup_dates:
        print('warming_up', date)
        historical_news = his_operator._get_news(source, date)
        sim_env.update_weight(historical_news)
    ##### warmup done #####

    date_ranger = date_range_generator(start_date, '2020-12-31')  # or max date in ycj
    for date in date_ranger:
        print('generating', date)
        for i in range(len(DAILY_TICKS) - 1):
            start_time = DAILY_TICKS[i]
            end_time = DAILY_TICKS[i+1]
            start = timestamper(date + ' ' + start_time, '%Y-%m-%d %H:%M:%S')
            end = timestamper(date + ' ' + end_time, '%Y-%m-%d %H:%M:%S')
            news = his_operator._get_news(sim_env.source, date, start, end)
            sim_env.update_weight(news)
            if end_time[-1] == '0':
                his_operator.insert_weight_data(
                    sim_env.weights_dict,
                    date + ' ' + end_time
                )
        sim_env.decay_weight()
