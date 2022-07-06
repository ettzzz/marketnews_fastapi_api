#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 20:42:04 2022

@author: ert
"""

import time

from database.news_operator import newsDatabaseOperator
from scrapper.yuncaijing import yuncaijingScrapper
from utils.datetime_tools import (
    get_now,
    get_today_date,
    get_delta_date,
    date_range_generator,
)


def call_for_update():
    source = "ycj"
    _now = get_now(is_timestamp=False)
    today = get_today_date()

    if _now.hour == 0 and _now.minute <= 5:
        yesterday = get_delta_date(today, -1)
        dates = date_range_generator(yesterday, today)
    else:
        dates = date_range_generator(today, today)

    ys = yuncaijingScrapper()
    his_operator = newsDatabaseOperator()
    max_id = his_operator.get_latest_news_id(source=source)

    fetched = list()
    conn = his_operator.on()
    for date in dates:
        page = 1
        while True:
            ycj_params = ys.get_params(page, date)
            ycj_news = ys.get_news(ycj_params)  ## fid is descending
            if not ycj_news:
                break  ## page is too large, empty data
            if ycj_news[0]["fid"] <= max_id:
                break  ## the biggest fid is small/equal than max_id
            if ycj_news[-1]["fid"] <= max_id:
                for n in ycj_news:
                    if n["fid"] > max_id:
                        fetched.append(n)
                break  ##
            else:
                fetched += ycj_news
                page += 1
                time.sleep(0.5)

        his_operator.insert_news_data(fetched, source, conn)
        fetched.clear()

    his_operator.off()
    return
