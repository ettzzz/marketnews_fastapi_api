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


# from utils.internet_tools import * # to get all codes


from engine.brain import SCD
import pandas as pd
from config.static_vars import DAY_ZERO
from database.news_operator import newsDatabaseOperator
from utils.datetime_tools import get_delta_date, date_range_generator
insula = SCD()
his_operator = newsDatabaseOperator()


class simEnvironment():
    def __init__(self):
        self.warmup_days = 30
        self.start_date = get_delta_date(DAY_ZERO, self.warmup_days + 1)
        self.warmup_dates = date_range_generator(
            start=DAY_ZERO,
            end=get_delta_date(DAY_ZERO, self.warmup_days)
        )
        self.source = 'ycj'
        # self.weights_dict = {k: 0 for k in codes}

    def warmup_weight(self):
        for date in self.warmup_dates:
            historical_news = his_operator._get_news(self.source, date)
            self.update_weight(historical_news, codes)
        pass

    def update_weight(self, news, codes):
        for pseudo_code in codes:
            if pseudo_code.startswith('6'):
                real_code = 'sh.' + pseudo_code
            else:
                real_code = 'sz.' + pseudo_code
            self.weights_dict[real_code] = insula.get_news_sentiment(news)

        pass

    def decay_weight(self):
        self.weights_dict = {
            k: insula.weight_decay(v, 1) for k, v in self.weights_dict.items()
        }


if __name__ == "__main__":
    sim_env = simEnvironment()
    sim_env.warmup_weight()
    date_ranger = date_range_generator(sim_env.start_date, '2020-12-31')  # or max date in ycj
    for date in date_ranger:
        # 分时段
        news = his_operator._get_news(sim_env.source, date)
        codes = []
        sim_env.update_weight(news, codes)
        # his_operator.insert_weight_data

        sim_env.decay_weight()
