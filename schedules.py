#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 20:42:04 2022

@author: ert
"""

import time
import random

from database.news_operator import newsDatabaseOperator
from scrapper.yuncaijing import yuncaijingScrapper
from utils.datetime_tools import (
    get_now,
    get_today_date,
    get_delta_date,
    date_range_generator,
)


def call_for_update(from_date=None):
    source = "ycj"
    _now = get_now(is_timestamp=False)
    today = get_today_date()

    if from_date is not None:
        dates = date_range_generator(from_date, today)
    else:
        if _now.hour == 0 and _now.minute <= 5:
            yesterday = get_delta_date(today, -1)
            dates = date_range_generator(yesterday, today)
        else:
            dates = date_range_generator(today, today)

    ys = yuncaijingScrapper()
    his_operator = newsDatabaseOperator()
    conn = his_operator.on()
    max_id = his_operator.get_latest_news_id(source=source, conn=conn)

    fetched = list()
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
                for n in ycj_news:
                    if n["code"]:
                        fetched.append(n)
                page += 1
                time.sleep(1 + random.random())

        his_operator.insert_news_data(fetched, source, conn)
        fetched.clear()
        print(date, f"finished with pages {page}")

    his_operator.off()
    return
