# -*- coding: utf-8 -*-
"""
Created on Sat Aug 28 09:37:55 2021

@author: ert
"""

import os

from database.news_operator import newsDatabaseOperator
from utils.datetime_tools import date_range_generator
from engine.brain import SCD
from config.static_vars import ROOT

"""
local latest news 8.24 14:55 ~120,000 data
label 0: negative, 1: positive
"""

his_operator = newsDatabaseOperator()
insula = SCD(is_deploy=False)
# make sure insula is using roberta model to ensure accuracy
source = "ycj"

date_start, date_end = "2021-01-01", "2021-08-23"
neg_txt_path = os.path.join(ROOT, "models", "negative.txt")
pos_txt_path = os.path.join(ROOT, "models", "positive.txt")
if os.path.exists(neg_txt_path) or os.path.exists(pos_txt_path):
    os.remove(neg_txt_path)
    os.remove(pos_txt_path)  # make sure positive.txt and negative.txt are intact

dates = date_range_generator(date_start, date_end)
neg_count, pos_count = 0, 0
for date in dates:
    print("generating training data for", date)
    news = his_operator._get_news(source, date)
    neg = open(os.path.join(ROOT, "models", "negative.txt"), "a", encoding="utf-8")
    pos = open(os.path.join(ROOT, "models", "positive.txt"), "a", encoding="utf-8")

    for _id, content, codes in news:
        if not codes:
            continue
        index = insula.get_news_sentiment(content)
        if abs(index) < 0.8:  # get rid of neutral contents
            continue

        if index < 0:
            neg.write("<|>".join([content, "0", "\n"]))
            neg_count += 1
        else:
            pos.write("<|>".join([content, "1", "\n"]))
            pos_count += 1

    neg.close()
    pos.close()

print("neg_count", neg_count, "pos_count", pos_count)
